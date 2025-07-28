# Imports do Django
from django.conf import settings
from django.core.mail import send_mail

# Imports do Django Rest Framework
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.responses import success_response, error_response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView


# Imports do projeto
from .models import Project, User, UserProject, ProjectRole, Task, ProjectPhase, Phase
from .serializers import (
    UserSerializer,
    CustomTokenObtainPairSerializer,
    ProjectSerializer,
    ProjectWithCollaboratorsAndTasksSerializer,
    ProjectWithTasksSerializer,
    TaskSerializer
)

# Lista de convites pendentes (email -> lista de IDs de projetos)
invited_users = {}

# Na view a gente faz o tratamento do que a url pede. Depende se for get, post, update.
# Sempre retorne em JSON pro front conseguir tratar bem
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()  # Pega todos os usuários do banco de dados
    serializer_class = UserSerializer  # Serializa os dados do usuário
    permission_classes = [AllowAny]  # Permite acesso a qualquer usuário, mesmo não autenticado

    def perform_create(self, serializer):
        user = serializer.save()

        # Importa o dicionário de convites
        from .views import invited_users
        from .models import Project, UserProject, ProjectRole

        # Verifica se o email do novo usuário está na lista de convites pendentes
        projetos_convidados = invited_users.get(user.email, [])

        for project_id in projetos_convidados:
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

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return success_response("Usuário autenticado com sucesso", serializer.data)
    
class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projetos = Project.objects.filter(userproject__user=request.user).distinct()
        serializer = ProjectWithTasksSerializer(projetos, many=True)
        return success_response("Projetos listados com sucesso", serializer.data)

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
            for email in collaborator_emails:
                try:
                    found_user = User.objects.get(email=email)
                    UserProject.objects.create(user=found_user, project=project, role=ProjectRole.MEMBER)
                except User.DoesNotExist:
                    # Salva convite na memória
                    if email not in invited_users:
                        invited_users[email] = []
                    invited_users[email].append(project.id)

                    subject = "Você foi convidado para colaborar em um projeto!"
                    message = (f"Olá!\n\nVocê foi convidado para colaborar no projeto '{project.name}'.\n"
                               f"Se você ainda não tem uma conta, por favor, registre-se usando este e-mail para ter acesso.\n\n"
                               f"Acesse a plataforma: https://buildyourproject-front.onrender.com/")
                    from_email = settings.DEFAULT_FROM_EMAIL
                    
                    try:
                        send_mail(subject, message, from_email, [email], fail_silently=False)
                    except Exception as e:
                        print("Erro ao enviar e-mail:", e)
                        # Em um projeto real, é ideal usar o sistema de logging do Django
                        # em vez de print() para registrar falhas.
                        pass

            # Criar tarefas a partir das fases (se quiser reforçar aqui)
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
            
            return success_response("Projeto criado com sucesso!", serializer.data, status.HTTP_201_CREATED)
        
        return error_response("Erro ao criar projeto", serializer.errors)

class ProjectCollaboratorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(pk=project_id)
            if not UserProject.objects.filter(user=request.user, project=project).exists():
                return error_response("Você não tem permissão para acessar este recurso.", status_code=status.HTTP_403_FORBIDDEN)
        except Project.DoesNotExist:
            return error_response("Projeto não encontrado.", status_code=status.HTTP_404_NOT_FOUND)

        user_projects = UserProject.objects.filter(project=project).select_related('user')
        users = [up.user for up in user_projects]
        serializer = UserSerializer(users, many=True)
        return success_response("Colaboradores listados com sucesso", serializer.data)
    
class ProjectShareWithMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projetos = Project.objects.filter(
            userproject__user=request.user,
            userproject__role=ProjectRole.MEMBER
        ).distinct()
        serializer = ProjectSerializer(projetos, many=True)
        return success_response("Projetos compartilhados listados com sucesso", serializer.data)

class ProjectTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        if not UserProject.objects.filter(user=request.user, project_id=project_id).exists():
            return error_response("Você não tem acesso a este projeto.", status_code=status.HTTP_403_FORBIDDEN)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return error_response("Projeto não encontrado.", status_code=status.HTTP_404_NOT_FOUND)

        serializer = ProjectWithCollaboratorsAndTasksSerializer(project)
        return success_response("Projeto com colaboradores e tarefas carregado", serializer.data)

class TaskUpdateStatusView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def patch(self, request, *args, **kwargs):
        task = self.get_object()
        is_completed = request.data.get('is_completed')

        if is_completed is None:
            return error_response("Erro de validação", {"is_completed": "O campo 'is_completed' é obrigatório."})
        
        if not isinstance(is_completed, bool):
             return error_response("Erro de validação", {"is_completed": "O campo 'is_completed' deve ser um valor booleano (true/false)."})

        task.is_completed = is_completed
        task.save()
        serializer = self.get_serializer(task)
        return success_response("Status da tarefa atualizado", serializer.data)
