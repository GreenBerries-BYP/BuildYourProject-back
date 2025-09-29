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
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.shortcuts import get_object_or_404 
import random
from django.http import JsonResponse

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache

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

# Import ML apenas quando necessário (evitar carga desnecessária)
try:
    from .ml.predictor import PredictorAtraso
    from .ml.sugestoes import GeradorSugestoes
    ML_DISPONIVEL = True
except ImportError:
    ML_DISPONIVEL = False

# Armazenamento temporário de códigos (para teste rápido, em produção use DB ou cache)
verification_codes = {}  # {email: code}

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        # Import local para evitar circular
        from .models import Project, UserProject, ProjectRole
        
        # Usar cache em vez de variável global
        cache_key = f"project_invite_{user.email}"
        projetos_convidados = cache.get(cache_key, [])

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

        # Remove do cache após tratar
        cache.delete(cache_key)

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class GoogleLoginView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        token = request.data.get("access_token")
        if not token:
            return Response({"error": "Token não fornecido"}, status=400)
        
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                settings.GOOGLE_OAUTH2_CLIENT_ID
            )
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

            user.google_access_token = token
            user.save()

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "google_token": token,
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
        
class GoogleCalendarSyncView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        token = user.google_access_token
        if not token:
            return Response({"error": "Usuário não conectado ao Google"}, status=400)

        try:
            creds = Credentials(token)
            service = build('calendar', 'v3', credentials=creds)

            # Pega próximos 10 eventos
            events_result = service.events().list(
                calendarId='primary', 
                maxResults=10, 
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            
            # Fechar serviço
            service.close()
            
            return Response(events)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def post(self, request):
        user = request.user
        access_token = getattr(user, "google_access_token", None)
        if not access_token:
            return Response({"error": "Usuário não tem Google conectado."}, status=400)

        # Exemplo: criar um evento no Calendar
        event = {
            "summary": "Nova tarefa do projeto",
            "description": "Descrição da tarefa",
            "start": {
                "dateTime": "2025-09-17T10:00:00-03:00",
                "timeZone": "America/Sao_Paulo",
            },
            "end": {
                "dateTime": "2025-09-17T11:00:00-03:00",
                "timeZone": "America/Sao_Paulo",
            },
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers=headers,
                json=event,
            )

            if response.status_code == 200 or response.status_code == 201:
                return Response({"message": "Evento criado com sucesso!", "event": response.json()})
            else:
                return Response({"error": "Falha ao criar evento", "details": response.json()}, status=response.status_code)
        except Exception as e:
            return Response({"error": f"Erro na requisição: {str(e)}"}, status=500)
        
class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Query otimizada
        projetos = Project.objects.filter(
            userproject__user=request.user
        ).distinct().select_related()
        
        serializer = ProjectWithTasksSerializer(projetos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save()
            
            # Criar líder do projeto
            UserProject.objects.create(
                user=request.user,
                project=project,
                role=ProjectRole.LEADER
            )

            collaborator_emails = request.data.get('collaborators', [])
            
            # Processar colaboradores de forma eficiente
            users_existentes = User.objects.filter(email__in=collaborator_emails)
            users_existentes_map = {user.email: user for user in users_existentes}
            
            for email in collaborator_emails:
                if email in users_existentes_map:
                    # Usuário existe - criar relação
                    UserProject.objects.create(
                        user=users_existentes_map[email],
                        project=project,
                        role=ProjectRole.MEMBER
                    )
                else:
                    # Usar cache em vez de variável global
                    cache_key = f"project_invite_{email}"
                    existing_invites = cache.get(cache_key, [])
                    existing_invites.append(project.id)
                    cache.set(cache_key, existing_invites, 60*60*24*7)  # 7 dias

                    subject = "Você foi convidado para colaborar em um projeto!"
                    message = (f"Olá!\n\nVocê foi convidado para colaborar no projeto '{project.name}'.\n"
                               f"Se você ainda não tem uma conta, por favor, registre-se usando este e-mail para ter acesso.\n\n"
                               f"Acesse a plataforma: https://buildyourproject-front.onrender.com/") 
                    from_email = settings.DEFAULT_FROM_EMAIL
                    
                    try:
                        send_mail(subject, message, from_email, [email], fail_silently=False)
                    except Exception as e:
                        print("Erro ao enviar e-mail:", e)
                        pass

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
        return Response(serializer.errors, status=400)

class ProjectDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def options(self, request, *args, **kwargs):
        response = JsonResponse({"message": "OK"})
        response["Access-Control-Allow-Origin"] = "https://buildyourproject-front.onrender.com"
        response["Access-Control-Allow-Methods"] = "DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "authorization, content-type"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    def delete(self, request, project_id):
        try:
            project = get_object_or_404(Project, id=project_id)

            # Só o líder pode deletar
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

class ProjectTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        # Verifica se o usuário pertence ao projeto
        if not UserProject.objects.filter(user=request.user, project_id=project_id).exists():
            return Response({"detail": "Você não tem acesso a este projeto."}, status=status.HTTP_403_FORBIDDEN)

        try:
            project = Project.objects.select_related().get(id=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # líder do projeto
        leader = UserProject.objects.filter(project=project, role=ProjectRole.LEADER).first()
        creator_name = leader.user.full_name if leader else None

        # colaboradores
        collaborators_qs = UserProject.objects.filter(project=project).select_related('user')
        collaborators = [up.user.full_name for up in collaborators_qs]

        # tarefas do projeto (phases) - query otimizada
        tarefasProjeto = []
        project_phases = ProjectPhase.objects.filter(project=project).prefetch_related(
            'task_set',
            'task_set__taskassignee_set',
            'task_set__taskassignee_set__user'
        )
        
        for pp in project_phases:
            phase = pp.phase
            tasks = pp.task_set.all()

            # progresso da fase
            total_tasks = tasks.count()
            completed_tasks = tasks.filter(is_completed=True).count()
            progresso = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

            subTarefas = []
            for task in tasks:
                assignees = task.taskassignee_set.select_related('user')
                responsaveis = [a.user.full_name for a in assignees]

                subTarefas.append({
                    "id": task.id,
                    "title": task.title,
                    "is_completed": task.is_completed,
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

        projeto_data = {
            "name": project.name,
            "creator_name": creator_name,
            "collaborator_count": collaborators_qs.count(),
            "collaborators": collaborators,
            "tarefasProjeto": tarefasProjeto
        }

        return Response(projeto_data, status=status.HTTP_200_OK)

    def post(self, request, project_id):
        if not UserProject.objects.filter(user=request.user, project_id=project_id).exists():
            return Response({"detail": "Você não tem acesso a este projeto."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
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
            try:
                user = User.objects.get(id=uid)
                TaskAssignee.objects.create(task=task, user=user)
            except User.DoesNotExist:
                continue

        return Response({"detail": "Tarefa criada com sucesso.", "task_id": task.id}, status=status.HTTP_201_CREATED)

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

    def delete(self, request, project_id, task_id):
        if not UserProject.objects.filter(user=request.user, project_id=project_id).exists():
            return Response({"detail": "Você não tem acesso a este projeto."}, status=status.HTTP_403_FORBIDDEN)

        try:
            task = Task.objects.get(id=task_id, project_phase__project_id=project_id)
        except Task.DoesNotExist:
            return Response({"detail": "Tarefa não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        task.delete()
        return Response({"detail": "Tarefa excluída com sucesso."}, status=status.HTTP_204_NO_CONTENT)

class CreateTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
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
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        if 'password' in serializer.validated_data:
            instance.set_password(serializer.validated_data.pop('password'))

        for attr, value in serializer.validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
 
class SendResetCodeView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            email = request.data.get("email")
            if not email:
                return Response({"error": "O e-mail é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"message": "Se o e-mail existir, um código será enviado."}, status=status.HTTP_200_OK)

            # Gerar código de 6 dígitos
            code = "".join([str(random.randint(0, 9)) for _ in range(6)])
            
            # Salvar no cache por 15 minutos (900 segundos)
            cache_key = f"reset_code_{email}"
            cache.set(cache_key, code, 900)

            subject = "Código de verificação - BuildYourProject"
            message = f"""
Olá {user.full_name or user.username},

Seu código de verificação para redefinição de senha é: {code}

Este código expira em 15 minutos.

Se você não solicitou este código, por favor ignore este e-mail.

Atenciosamente,
Equipe BuildYourProject
"""
            from_email = settings.DEFAULT_FROM_EMAIL

            try:
                send_mail(subject, message.strip(), from_email, [email], fail_silently=False)
                print(f"✅ Email de reset enviado para: {email}")
                return Response({"message": "Código enviado com sucesso."}, status=status.HTTP_200_OK)
                
            except Exception as e:
                print("❌ Erro ao enviar e-mail:", e)
                if settings.DEBUG:
                    return Response({
                        "message": "Erro ao enviar email. Código gerado (apenas em desenvolvimento):",
                        "code": code
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "error": "Erro ao enviar e-mail. Tente novamente."
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            print("❌ Erro crítico em SendResetCodeView:", e)
            return Response({"error": "Erro interno do servidor."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyResetCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response({"error": "E-mail e código são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar código do cache
        cache_key = f"reset_code_{email}"
        stored_code = cache.get(cache_key)
        
        if stored_code and stored_code == code:
            # Código válido, criar sessão de verificação
            session_token = f"verified_{random.randint(1000, 9999)}"
            cache.set(f"reset_verified_{email}", session_token, 600)  # 10 minutos
            
            # Remover código usado
            cache.delete(cache_key)
            
            return Response({
                "message": "Código verificado com sucesso.",
                "session_token": session_token
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Código inválido ou expirado."}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        session_token = request.data.get("session_token")
        new_password = request.data.get("new_password")
        
        if not all([email, session_token, new_password]):
            return Response({"error": "Todos os campos são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar sessão
        stored_token = cache.get(f"reset_verified_{email}")
        if not stored_token or stored_token != session_token:
            return Response({"error": "Sessão expirada ou inválida. Por favor, inicie o processo novamente."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)

            if len(new_password) < 8:
                return Response({"error": "A senha deve ter no mínimo 8 caracteres."}, status=400)

            user.set_password(new_password)
            user.save()
            
            # Limpar sessão
            cache.delete(f"reset_verified_{email}")

            # Email de confirmação
            subject = "Senha alterada com sucesso - BuildYourProject"
            message = f"""
                Olá {user.full_name or user.username},

                Sua senha foi alterada com sucesso.

                Se você não realizou esta alteração, entre em contato conosco imediatamente.

                Atenciosamente,
                Equipe BuildYourProject
                """
            from_email = settings.DEFAULT_FROM_EMAIL

            try:
                send_mail(subject, message.strip(), from_email, [email], fail_silently=False)
            except Exception as e:
                print("Erro ao enviar email de confirmação:", e)
            
            return Response({"message": "Senha redefinida com sucesso."}, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

class TermsView(TemplateView):
    template_name = "index.html" 

class PoliticsView(TemplateView): 
    template_name = "index.html"

# IMPLEMENTAÇÃO ML:
class AnaliseProjetoView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, project_id):
        """
        Analisa o projeto e gera sugestões
        URL: POST /api/projetos/{id}/analisar
        """
        if not ML_DISPONIVEL:
            return Response({
                'sucesso': False,
                'error': 'Módulo de ML não disponível'
            }, status=503)
            
        from .models import AnaliseProjeto
        
        projeto = get_object_or_404(Project, id=project_id)
        
        # Verificar permissão
        if not UserProject.objects.filter(user=request.user, project=projeto).exists():
            return Response({"error": "Você não tem acesso a este projeto"}, status=403)
        
        try:
            # 1. Calcular probabilidade de atraso
            predictor = PredictorAtraso()
            probabilidade = predictor.prever_probabilidade_atraso(projeto)
            
            # 2. Gerar sugestões
            sugestoes = GeradorSugestoes.gerar_sugestoes(projeto)
            
            # 3. Salvar análise no histórico
            analise = AnaliseProjeto.objects.create(
                projeto=projeto,
                probabilidade_atraso=probabilidade,
                sugestoes_geradas=sugestoes
            )
            
            # 4. Atualizar projeto com alerta
            projeto.probabilidade_atraso = probabilidade
            projeto.alerta_atraso = probabilidade > 70  # Alerta se >70%
            projeto.data_ultima_analise = timezone.now()
            projeto.save()
            
            return Response({
                'sucesso': True,
                'probabilidade_atraso': probabilidade,
                'alerta_atraso': projeto.alerta_atraso,
                'sugestoes': sugestoes,
                'data_analise': analise.data_analise,
                'mensagem': 'Análise concluída com sucesso'
            })
            
        except Exception as e:
            return Response({
                'sucesso': False,
                'error': f'Erro na análise: {str(e)}'
            }, status=500)

class AplicarSugestaoView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, project_id):
        """
        Aplica uma sugestão específica no projeto
        URL: POST /api/projetos/{id}/aplicar-sugestao
        """
        from .models import AnaliseProjeto
        
        projeto = get_object_or_404(Project, id=project_id)
        sugestao_id = request.data.get('sugestao_id')
        acao = request.data.get('acao')
        
        # Verificar permissão (apenas líder pode aplicar sugestões)
        user_project = UserProject.objects.filter(
            user=request.user, 
            project=projeto
        ).first()
        
        if not user_project or user_project.role != ProjectRole.LEADER:
            return Response({"error": "Apenas o líder do projeto pode aplicar sugestões"}, status=403)
        
        try:
            # Executar a ação específica
            if acao == 'reordenar_tarefas_complexas':
                resultado = self._reordenar_tarefas_complexas(projeto)
            elif acao == 'redistribuir_carga':
                resultado = self._redistribuir_carga(projeto)
            elif acao == 'ajustar_prazos':
                resultado = self._ajustar_prazos(projeto)
            else:
                return Response({"error": "Ação não reconhecida"}, status=400)
            
            # Registrar no histórico
            analise = AnaliseProjeto.objects.filter(projeto=projeto).last()
            if analise:
                analise.acoes_aplicadas.append({
                    'sugestao_id': sugestao_id,
                    'acao': acao,
                    'data_aplicacao': timezone.now().isoformat(),
                    'resultado': resultado,
                    'aplicado_por': request.user.email
                })
                analise.save()
            
            return Response({
                'sucesso': True,
                'acao_aplicada': acao,
                'resultado': resultado,
                'mensagem': 'Sugestão aplicada com sucesso'
            })
            
        except Exception as e:
            return Response({
                'sucesso': False,
                'error': f'Erro ao aplicar sugestão: {str(e)}'
            }, status=500)
    
    def _reordenar_tarefas_complexas(self, projeto):
        """Move tarefas complexas para o início do cronograma"""
        tarefas = Task.objects.filter(
            project_phase__project=projeto,
            is_completed=False
        ).order_by('-complexidade', 'due_date')
        
        # Reagendar prazos baseado na nova ordem
        data_base = timezone.now() + timedelta(days=1)
        tarefas_atualizadas = 0
        
        for i, tarefa in enumerate(tarefas):
            novo_prazo = data_base + timedelta(days=i * 2)
            if tarefa.due_date != novo_prazo:
                tarefa.due_date = novo_prazo
                tarefa.save()
                tarefas_atualizadas += 1
        
        return f"Reordenadas {tarefas_atualizadas} tarefas por complexidade"
    
    def _redistribuir_carga(self, projeto):
        """Distribui tarefas de forma equilibrada"""
        usuarios = list(UserProject.objects.filter(project=projeto))
        if not usuarios:
            return "Nenhum usuário no projeto para redistribuir"
            
        tarefas_nao_atribuidas = Task.objects.filter(
            project_phase__project=projeto,
            is_completed=False,
            taskassignee__isnull=True
        )
        
        tarefas_distribuidas = 0
        
        for i, tarefa in enumerate(tarefas_nao_atribuidas):
            usuario = usuarios[i % len(usuarios)].user
            TaskAssignee.objects.create(task=tarefa, user=usuario)
            tarefas_distribuidas += 1
        
        return f"Distribuídas {tarefas_distribuidas} tarefas entre {len(usuarios)} membros"
    
    def _ajustar_prazos(self, projeto):
        """Estende prazos de tarefas críticas"""
        tarefas_criticas = Task.objects.filter(
            project_phase__project=projeto,
            is_completed=False,
            due_date__lt=timezone.now() + timedelta(days=3)
        )
        
        tarefas_ajustadas = 0
        
        for tarefa in tarefas_criticas:
            novo_prazo = tarefa.due_date + timedelta(days=7)
            if novo_prazo > projeto.end_date:
                novo_prazo = projeto.end_date
                
            tarefa.due_date = novo_prazo
            tarefa.save()
            tarefas_ajustadas += 1
        
        return f"Ajustados prazos de {tarefas_ajustadas} tarefas críticas"
