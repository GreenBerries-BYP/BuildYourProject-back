# Imports do Django
from django.conf import settings
from django.core.mail import send_mail
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model

# Imports do Django Rest Framework
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
import requests #precisa usar o pip install requests
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import random

# Imports do projeto
from .models import Project, User, UserProject, ProjectRole, Task, ProjectPhase, Phase, TaskAssignee
from .serializers import (
    UserSerializer,
    CustomTokenObtainPairSerializer,
    ProjectSerializer,
    ProjectWithCollaboratorsAndTasksSerializer,
    ProjectWithTasksSerializer,
    TaskSerializer,
    SharedProjectSerializer
)

# Lista de convites pendentes (email -> lista de IDs de projetos)
invited_users = {}

# Armazenamento temporário de códigos (para teste rápido, em produção use DB ou cache)
verification_codes = {}  # {email: code}

User = get_user_model()

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

User = get_user_model()

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get("access_token")
        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
            email = idinfo["email"]
            name = idinfo.get("name", "")

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email.split("@")[0],
                    "full_name": name,
                    "role": "user",
                },
            )

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "role": user.role,
                    },
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Token inválido", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
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
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            # DELETE: remove projeto
    def delete(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        if not project_id:
            return Response({"detail": "ID do projeto não informado."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Só o líder pode apagar
        user_project = UserProject.objects.filter(user=request.user, project=project, role=ProjectRole.LEADER).first()
        if not user_project:
            return Response({"detail": "Você não tem permissão para apagar este projeto."}, status=status.HTTP_403_FORBIDDEN)

        project.delete()
        return Response({"detail": "Projeto excluído com sucesso."}, status=status.HTTP_204_NO_CONTENT)


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

class ProjectTasksView(APIView):
    permission_classes = [IsAuthenticated]

    # READ: retorna projeto com colaboradores e tarefas no formato do front
    def get(self, request, project_id):
        # Verifica se o usuário pertence ao projeto
        if not UserProject.objects.filter(user=request.user, project_id=project_id).exists():
            return Response({"detail": "Você não tem acesso a este projeto."}, status=status.HTTP_403_FORBIDDEN)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # líder do projeto
        leader = UserProject.objects.filter(project=project, role=ProjectRole.LEADER).first()
        creator_name = leader.user.full_name if leader else None

        # colaboradores
        collaborators_qs = UserProject.objects.filter(project=project)
        collaborators = [up.user.full_name for up in collaborators_qs]

        # tarefas do projeto (phases)
        tarefasProjeto = []
        project_phases = ProjectPhase.objects.filter(project=project)
        for pp in project_phases:
            phase = pp.phase
            tasks = Task.objects.filter(project_phase=pp)

            # progresso da fase
            total_tasks = tasks.count()
            completed_tasks = tasks.filter(is_completed=True).count()
            progresso = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

            subTarefas = []
            for task in tasks:
                assignees = TaskAssignee.objects.filter(task=task)
                responsaveis = [a.user.full_name for a in assignees]

            subTarefas.append({
                "id": task.id,
                "title": task.title,  # o front espera title
                "is_completed": task.is_completed,  # o front espera is_completed
                "responsavel": ", ".join(responsaveis) if responsaveis else None,
                "prazo": task.due_date.strftime("%d/%m/%Y") if task.due_date else None,
                "status": "concluído" if task.is_completed else "pendente"
            })

            tarefasProjeto.append({
                "id": phase.id,
                "nomeTarefa": phase.name,
                "progresso": progresso,
                "subTarefas": subTarefas
            })

        # >>> AQUI adaptamos os nomes p/ bater com o React <<<
        projeto_data = {
            "name": project.name,  # antes era nomeProjeto
            "creator_name": creator_name,  # antes era admProjeto
            "collaborator_count": collaborators_qs.count(),  # antes era numIntegrantes
            "collaborators": collaborators,
            "tarefasProjeto": tarefasProjeto
        }

        return Response(projeto_data, status=status.HTTP_200_OK)


    # CREATE: cria nova tarefa a partir de uma fase
    def post(self, request, project_id):
        if not UserProject.objects.filter(user=request.user, project_id=project_id).exists():
            return Response({"detail": "Você não tem acesso a este projeto."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        # espera que o front envie 'phase_id' para saber onde criar a tarefa
        try:
            phase = ProjectPhase.objects.get(id=data.get("phase_id"), project_id=project_id)
        except ProjectPhase.DoesNotExist:
            return Response({"detail": "Fase não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        task = Task.objects.create(
            title=data.get("title"),
            description=data.get("description", ""),
            is_completed=data.get("is_completed", False),
            due_date=data.get("due_date"),
            project_phase=phase
        )

        # atribuir responsáveis se houver
        assignee_ids = data.get("assignee_ids", [])
        for uid in assignee_ids:
            user = User.objects.get(id=uid)
            TaskAssignee.objects.create(task=task, user=user)

        return Response({"detail": "Tarefa criada com sucesso.", "task_id": task.id}, status=status.HTTP_201_CREATED)

    # UPDATE: atualiza status da tarefa
    def patch(self, request, project_id, task_id):
        if not UserProject.objects.filter(user=request.user, project_id=project_id).exists():
            return Response({"detail": "Você não tem acesso a este projeto."}, status=status.HTTP_403_FORBIDDEN)

        try:
            task = Task.objects.get(id=task_id, project_phase__project_id=project_id)
        except Task.DoesNotExist:
            return Response({"detail": "Tarefa não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        is_completed = request.data.get("is_completed")
        if is_completed is None or not isinstance(is_completed, bool):
            return Response({"error": "O campo 'is_completed' deve ser booleano."}, status=status.HTTP_400_BAD_REQUEST)

        task.is_completed = is_completed
        task.save()
        return Response({"detail": "Status atualizado com sucesso."})

    # DELETE: remove tarefa
    def delete(self, request, project_id, task_id):
        if not UserProject.objects.filter(user=request.user, project_id=project_id).exists():
            return Response({"detail": "Você não tem acesso a este projeto."}, status=status.HTTP_403_FORBIDDEN)

        try:
            task = Task.objects.get(id=task_id, project_phase__project_id=project_id)
        except Task.DoesNotExist:
            return Response({"detail": "Tarefa não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        task.delete()
        return Response({"detail": "Tarefa excluída com sucesso."}, status=status.HTTP_204_NO_CONTENT)

# cria a tarefa do zero
class CreateTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        # Verifica se usuário pertence ao projeto
        if not UserProject.objects.filter(user=request.user, project_id=project_id).exists():
            return Response({"detail": "Você não tem acesso a este projeto."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()

        # Criar fase automática que é a própria tarefa
        phase_obj, _ = Phase.objects.get_or_create(name=data.get("nome"))
        project_phase = ProjectPhase.objects.create(project_id=project_id, phase=phase_obj)

        # Criar a tarefa
        task = Task.objects.create(
            project_phase=project_phase,
            title=data.get("nome"),
            description=data.get("descricao", ""),
            is_completed=False,
            due_date=data.get("dataEntrega")
        )

        # Atribuir responsável se houver
        responsavel_id = data.get("responsavel")
        if responsavel_id:
            try:
                user = User.objects.get(id=responsavel_id)
                TaskAssignee.objects.create(task=task, user=user)
            except User.DoesNotExist:
                pass

        return Response({"detail": "Tarefa criada com sucesso.", "task_id": task.id}, status=status.HTTP_201_CREATED)

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

class UserConfigurationView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retorna o usuário logado
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)  # PATCH
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Se vier senha, usar set_password
        if 'password' in serializer.validated_data:
            instance.set_password(serializer.validated_data.pop('password'))

        # Atualiza outros campos
        for attr, value in serializer.validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
        
# envio de código de verificação (func: "esqueci minha senha")
class SendResetCodeView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "O e-mail é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "E-mail não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Gerar código de 6 dígitos
        code = "".join([str(random.randint(0, 9)) for _ in range(6)])
        verification_codes[email] = code  # salva temporariamente

        subject = "Código de verificação"
        message = f"Olá {user.username},\n\nSeu código de verificação é: {code}\n\nNão compartilhe este código com ninguém."
        from_email = settings.DEFAULT_FROM_EMAIL

        try:
            send_mail(subject, message, from_email, [email], fail_silently=False)
            return Response({"message": "Código enviado com sucesso."}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Erro ao enviar e-mail:", e)
            return Response({"error": "Erro ao enviar e-mail."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# verificação de código
class VerifyResetCodeView(APIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response({"error": "E-mail e código são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)
        
        if verification_codes.get(email) == code:
            # Aqui você poderia permitir redefinir a senha
            return Response({"message": "Código verificado com sucesso."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Código inválido."}, status=status.HTTP_400_BAD_REQUEST)

        
class TermsView(TemplateView):
    template_name = "index.html" 

class PoliticsView(TemplateView): 
    template_name = "index.html"
