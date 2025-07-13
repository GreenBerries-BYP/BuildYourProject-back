# Imports do Django
from django.conf import settings
from django.core.mail import send_mail

# Imports do Django Rest Framework
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
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


# Na view a gente faz o tratamento do que a url pede. Depende se for get, post, update.
# Sempre retorne em JSON pro front conseguir tratar bem
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()  # Pega todos os usuários do banco de dados
    serializer_class = UserSerializer  # Serializa os dados do usuário
    permission_classes = [AllowAny]  # Permite acesso a qualquer usuário, mesmo não autenticado

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
            for email in collaborator_emails:
                try:
                    found_user = User.objects.get(email=email)
                    UserProject.objects.create(user=found_user, project=project, role=ProjectRole.MEMBER)
                except User.DoesNotExist:
                    subject = "Você foi convidado para colaborar em um projeto!"
                    message = (f"Olá!\n\nVocê foi convidado para colaborar no projeto '{project.name}'.\n"
                               f"Se você ainda não tem uma conta, por favor, registre-se usando este e-mail para ter acesso.\n\n"
                               f"Acesse a plataforma: https://buildyourproject-front.onrender.com/register")
                    from_email = settings.DEFAULT_FROM_EMAIL
                    
                    try:
                        send_mail(subject, message, from_email, [email], fail_silently=False)
                    except Exception as e:
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
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        serializer = ProjectSerializer(projetos, many=True)
        return Response(serializer.data)

class ProjectTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        if not UserProject.objects.filter(user=request.user, project_id=project_id).exists():
            return Response({"detail": "Você não tem acesso a este projeto."}, status=status.HTTP_403_FORBIDDEN)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectWithCollaboratorsAndTasksSerializer(project)
        return Response(serializer.data)

class TaskUpdateStatusView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def patch(self, request, *args, **kwargs):
        task = self.get_object()
        is_completed = request.data.get('is_completed')

        if is_completed is None:
            return Response({"error": "O campo 'is_completed' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(is_completed, bool):
             return Response({"error": "O campo 'is_completed' deve ser um valor booleano (true/false)."}, status=status.HTTP_400_BAD_REQUEST)

        task.is_completed = is_completed
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)