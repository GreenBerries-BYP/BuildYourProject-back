from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.cache import cache
import threading 

from ..models import Project, UserProject, ProjectRole, Phase, ProjectPhase, Task, User
from ..serializers import ProjectSerializer, ProjectWithTasksSerializer, SharedProjectSerializer, UserSerializer, TaskAssignee

# Imports do Django
from django.conf import settings
from django.core.mail import send_mail
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from datetime import timedelta
from django.utils import timezone

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
import requests
import threading

def enviar_email_async(subject, message, from_email, recipient_list):
    """Usa API direta do Resend - 100% funcionando"""
    def _enviar():
        try:
            print(f"🎯 API RESEND PARA: {recipient_list}")
            print(f"📧 ASSUNTO: {subject}")
            
            api_key = "re_FKTWQnZM_8f99hCKt5mug8TtEWtQzbrTh"  # Sua API Key
            url = "https://api.resend.com/emails"
            
            payload = {
                "from": "noreply@byp-buildyourproject.com.br",  # Email verificado do Resend
                "to": recipient_list,
                "subject": subject,  
                "text": message     
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            print(f"📊 RESPOSTA RESEND: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅✅✅ EMAIL ENVIADO COM SUCESSO!")
                print(f"📧 ID: {response.json().get('id')}")
            else:
                print(f"❌❌❌ ERRO RESEND: {response.text}")
                
        except Exception as e:
            print(f"💥 ERRO API: {str(e)}")
    
    thread = threading.Thread(target=_enviar)
    thread.daemon = True
    thread.start()

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
            if fases and project.start_date and project.end_date:
                self.calcular_e_criar_tarefas_com_datas(project, fases)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
                    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def calcular_e_criar_tarefas_com_datas(self, project, fases):
        """Calcula datas automaticamente para tarefas e subtarefas"""
        start_date = project.start_date
        end_date = project.end_date - timedelta(days=1)  # 1 dia de antecedência
        
        total_duration = (end_date - start_date).days
        phases_count = len(fases)
        
        if phases_count == 0:
            return
        
        # Duração por fase (em dias)
        days_per_phase = total_duration / phases_count
        
        for index, fase_nome in enumerate(fases):
            # Calcular datas para esta fase
            phase_start = start_date + timedelta(days=index * days_per_phase)
            phase_end = start_date + timedelta(days=(index + 1) * days_per_phase)
            
            # Criar fase e tarefa principal
            phase_obj, _ = Phase.objects.get_or_create(name=fase_nome)
            project_phase = ProjectPhase.objects.create(project=project, phase=phase_obj)
            
            # Criar tarefa principal com datas calculadas
            main_task = Task.objects.create(
                project_phase=project_phase,
                title=fase_nome,
                description=f"Fase: {fase_nome}",
                is_completed=False,
                created_at=phase_start,  # ✅ Data de início calculada
                due_date=phase_end,      # ✅ Data de fim calculada
                complexidade=3.0  # Valor padrão
            )
            
            # ✅ CRIAR SUBTAREFAS AUTOMATICAMENTE COM DATAS
            self.criar_subtarefas_automaticas(main_task, phase_start, phase_end, fase_nome)

    def criar_subtarefas_automaticas(self, main_task, phase_start, phase_end, fase_nome):
        """Cria subtarefas com datas distribuídas dentro da tarefa principal"""
        subtarefas_base = [
            f"Planejar {fase_nome}",
            f"Executar {fase_nome}", 
            f"Revisar {fase_nome}",
            f"Finalizar {fase_nome}"
        ]
        
        total_duration = (phase_end - phase_start).days
        subtasks_count = len(subtarefas_base)
        
        if subtasks_count == 0:
            return
        
        days_per_subtask = total_duration / subtasks_count
        
        for sub_index, subtarefa_nome in enumerate(subtarefas_base):
            sub_start = phase_start + timedelta(days=sub_index * days_per_subtask)
            sub_end = phase_start + timedelta(days=(sub_index + 1) * days_per_subtask)
            
            Task.objects.create(
                project_phase=main_task.project_phase,
                title=subtarefa_nome,
                description=f"Subtarefa: {subtarefa_nome}",
                is_completed=False,
                created_at=sub_start,  # ✅ Data de início calculada
                due_date=sub_end,      # ✅ Data de fim calculada  
                parent_task=main_task,  # ✅ Link com tarefa principal
                complexidade=2.0  # Valor padrão para subtarefas
            )

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

            print(f"DEBUG TaskAssignView - task_id: {task_id}")
            print(f"DEBUG - Dados recebidos: {request.data}")
            
            task = get_object_or_404(Task, id=task_id)
            user_id = request.data.get('user_id')
            
            if not user_id:
                return Response(
                    {"error": "user_id e obrigatorio"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verifica permissoes
            project_phase = task.project_phase
            project = project_phase.project
            
            if not UserProject.objects.filter(user=request.user, project=project).exists():
                return Response(
                    {"error": "Voce nao tem permissao para atribuir tarefas neste projeto"}, 
                    status=status.HTTP_403_FORBIDDEN
                )

            # Verifica se o usuario a ser atribuido e membro do projeto
            user_to_assign = get_object_or_404(User, id=user_id)
            if not UserProject.objects.filter(user=user_to_assign, project=project).exists():
                return Response(
                    {"error": "O usuario nao e membro deste projeto"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # CORRETO: Criar ou atualizar TaskAssignee
            task_assignee, created = TaskAssignee.objects.get_or_create(
                task=task,
                defaults={'user': user_to_assign}
            )
            
            if not created:
                task_assignee.user = user_to_assign
                task_assignee.save()

            print(f"Tarefa atribuida com sucesso - Criado: {created}")

            # Serializa a resposta
            user_data = UserSerializer(user_to_assign).data

            return Response({
                "message": "Tarefa atribuida com sucesso",
                "assigned_user": user_data,
                "task": {
                    "id": task.id,
                    "title": task.title
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Erro: {str(e)}")
            return Response(
                {"error": f"Erro ao atribuir tarefa: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )