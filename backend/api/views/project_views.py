from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.cache import cache
import threading  # ⚠️ ADICIONAR ESTE IMPORT

from ..models import Project, UserProject, ProjectRole, Phase, ProjectPhase, Task, User
from ..serializers import ProjectSerializer, ProjectWithTasksSerializer, SharedProjectSerializer, UserSerializer, TaskAssignee

# Imports do Django
from django.conf import settings
from django.core.mail import send_mail
from django.core.cache import cache
from django.shortcuts import get_object_or_404

# Imports do Django Rest Framework
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

# Imports do projeto
from ..models import Project, User, UserProject, ProjectRole, Task, ProjectPhase, Phase
from ..serializers import (
    UserSerializer,
    CustomTokenObtainPairSerializer,
    ProjectSerializer,
    ProjectWithCollaboratorsAndTasksSerializer,
    ProjectWithTasksSerializer,
    TaskSerializer,
    SharedProjectSerializer
)

# Lista de convites pendentes (email -> lista de IDs de projetos) - mantido para compatibilidade
invited_users = {}

import threading
import time

def enviar_email_async(subject, message, from_email, recipient_list):
    """Função com timeout para não travar"""
    def _enviar():
        try:
            print(f"🎯 INICIANDO ENVIO PARA: {recipient_list}")
            
            # ⚠️ TIMEOUT - se demorar mais de 10 segundos, para
            start_time = time.time()
            
            from django.core.mail import send_mail
            
            result = send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False
            )
            
            elapsed = time.time() - start_time
            print(f"📊 EMAIL PROCESSADO em {elapsed:.2f}s - Resultado: {result}")
            
            if result == 1:
                print(f"✅✅✅ SUCESSO!")
            else:
                print(f"❌❌❌ FALHA")
                
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"💥💥💥 ERRO após {elapsed:.2f}s: {str(e)}")
            import traceback
            print(f"📋 ERRO: {traceback.format_exc()}")
    
    thread = threading.Thread(target=_enviar)
    thread.daemon = True  # ⚠️ Thread morre se main morrer
    thread.start()
    
    # ⚠️ Timeout opcional - mata a thread após 30s
    def _timeout_killer():
        time.sleep(30)
        if thread.is_alive():
            print(f"⏰⏰⏰ TIMEOUT - Thread de email foi interrompida")
    
    timeout_thread = threading.Thread(target=_timeout_killer)
    timeout_thread.daemon = True
    timeout_thread.start()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        # Verifica convites na MEMÓRIA (sistema antigo)
        projetos_convidados_memoria = invited_users.get(user.email, [])
        for project_id in projetos_convidados_memoria:
            try:
                project = Project.objects.get(id=project_id)
                UserProject.objects.get_or_create(
                    user=user,
                    project=project,
                    role=ProjectRole.MEMBER
                )
            except Project.DoesNotExist:
                continue

        # Remove o email do dicionário após tratar
        if user.email in invited_users:
            del invited_users[user.email]

        # Verifica convites no CACHE (sistema novo)
        cache_key = f"project_invite_{user.email}"
        projetos_convidados_cache = cache.get(cache_key, [])
        
        for project_id in projetos_convidados_cache:
            try:
                project = Project.objects.get(id=project_id)
                UserProject.objects.get_or_create(
                    user=user,
                    project=project,
                    role=ProjectRole.MEMBER
                )
            except Project.DoesNotExist:
                continue

        # Remove do cache após tratar
        cache.delete(cache_key)

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Filtra apenas projetos onde o usuário é líder
        projetos = Project.objects.filter(
            userproject__user=request.user, 
            userproject__role=ProjectRole.LEADER
        ).distinct()
        serializer = ProjectWithTasksSerializer(projetos, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save()
            
            # Cria o líder do projeto
            UserProject.objects.create(
                user=request.user,
                project=project,
                role=ProjectRole.LEADER
            )

            collaborator_emails = request.data.get('collaborators', [])
            
            # Busca usuários existentes de forma otimizada
            users_existentes = User.objects.filter(email__in=collaborator_emails)
            users_existentes_map = {user.email: user for user in users_existentes}
            
            for email in collaborator_emails:
                if email in users_existentes_map:
                    # Usuário existe, adiciona ao projeto
                    UserProject.objects.create(
                        user=users_existentes_map[email],
                        project=project,
                        role=ProjectRole.MEMBER
                    )
                else:
                    # SALVA CONVITE NO CACHE (sistema novo)
                    cache_key = f"project_invite_{email}"
                    existing_invites = cache.get(cache_key, [])
                    existing_invites.append(project.id)
                    cache.set(cache_key, existing_invites, 60*60*24*7)  # 7 dias

                    # SALVA CONVITE NA MEMÓRIA (sistema antigo - para compatibilidade)
                    if email not in invited_users:
                        invited_users[email] = []
                    invited_users[email].append(project.id)

                    # CORREÇÃO: USAR A FUNÇÃO ASYNC
                    subject = "Você foi convidado para colaborar em um projeto!"
                    message = (f"Olá!\n\nVocê foi convidado para colaborar no projeto '{project.name}'.\n"
                              f"Se você ainda não tem uma conta, por favor, registre-se usando este e-mail para ter acesso.\n\n"
                              f"Acesse a plataforma: https://buildyourproject-front.onrender.com/")
                    from_email = settings.DEFAULT_FROM_EMAIL
                    
                    # CHAMADA CORRIGIDA - sem try/except
                    enviar_email_async(subject, message, from_email, [email])

            # Criar tarefas a partir das fases
            fases = project.phases or []
            for fase_nome in fases:
                phase_obj, _ = Phase.objects.get_or_create(name=fase_nome)
                project_phase = ProjectPhase.objects.create(project=project, phase=phase_obj)
                Task.objects.create(
                    project_phase=project_phase,
                    title=fase_nome,
                    description=f"Fase inicial do projeto: {fase_nome}",
                    is_completed=False,
                    due_date=project.end_date
                )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, project_id):
        try:
            project = get_object_or_404(Project, id=project_id)
            project.delete()
            
            return Response(
                {"detail": "Projeto excluído com sucesso."}, 
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {"detail": f"Erro ao excluir projeto: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class ProjectCollaboratorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(pk=project_id)
            if not UserProject.objects.filter(user=request.user, project=project).exists():
                return Response({"error": "Você não tem permissão para acessar este recurso."}, status=status.HTTP_403_FORBIDDEN)
        except Project.DoesNotExist:
            return Response({"error": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        user_projects = UserProject.objects.filter(project=project).select_related('user')
        users = [up.user for up in user_projects]
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProjectShareWithMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projetos = Project.objects.filter(
            userproject__user=request.user,
            userproject__role=ProjectRole.MEMBER
        ).distinct()
        serializer = SharedProjectSerializer(projetos, many=True)
        return Response(serializer.data)
    
# atribuição de tarefas
class TaskAssignView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        try:
            task = get_object_or_404(Task, id=task_id)
            user_id = request.data.get('user_id')
            
            if not user_id:
                return Response(
                    {"error": "user_id é obrigatório"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verifica se o usuário tem permissão para atribuir tarefas neste projeto
            project_phase = task.project_phase
            project = project_phase.project
            
            if not UserProject.objects.filter(user=request.user, project=project).exists():
                return Response(
                    {"error": "Você não tem permissão para atribuir tarefas neste projeto"}, 
                    status=status.HTTP_403_FORBIDDEN
                )

            # Verifica se o usuário a ser atribuído é membro do projeto
            user_to_assign = get_object_or_404(User, id=user_id)
            if not UserProject.objects.filter(user=user_to_assign, project=project).exists():
                return Response(
                    {"error": "O usuário não é membro deste projeto"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Cria ou atualiza a atribuição
            task_assignee, created = TaskAssignee.objects.get_or_create(
                task=task,
                defaults={'user': user_to_assign}
            )
            
            if not created:
                task_assignee.user = user_to_assign
                task_assignee.save()

            # Serializa a resposta
            user_data = UserSerializer(user_to_assign).data

            return Response({
                "message": "Tarefa atribuída com sucesso",
                "assigned_user": user_data,
                "task": {
                    "id": task.id,
                    "title": task.title
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Erro ao atribuir tarefa: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )