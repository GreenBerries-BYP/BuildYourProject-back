from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.cache import cache

from ..models import Project, UserProject, ProjectRole, Phase, ProjectPhase, Task, User
from ..serializers import ProjectSerializer, ProjectWithTasksSerializer, SharedProjectSerializer, UserSerializer

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
        projetos = Project.objects.filter(userproject__user=request.user).distinct()
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

                    # ENVIO DE EMAIL - USANDO MÉTODO SÍNCRONO QUE FUNCIONA
                    subject = "Você foi convidado para colaborar em um projeto!"
                    message = (
                        f"Olá!\n\nVocê foi convidado para colaborar no projeto '{project.name}'.\n"
                        "Se você ainda não tem uma conta, por favor, registre-se usando este e-mail para ter acesso.\n\n"
                        "Acesse a plataforma: https://buildyourproject-front.onrender.com/register"
                    )
                    from_email = settings.DEFAULT_FROM_EMAIL
                    
                    try:
                        send_mail(subject, message, from_email, [email], fail_silently=False)
                        print(f"✅ E-mail enviado com sucesso para {email}")
                    except Exception as e:
                        print(f"❌ Erro ao enviar e-mail para {email}: {e}")

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

            if not UserProject.objects.filter(user=request.user, project=project, role=ProjectRole.LEADER).exists():
                return Response(
                    {"detail": "Você não tem permissão para apagar este projeto."}, 
                    status=status.HTTP_403_FORBIDDEN
                )

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
