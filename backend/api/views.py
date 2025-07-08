from django.http import JsonResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomTokenObtainPairSerializer, ProjectSerializer
from api.models import Project, User, UserProject, ProjectRole
from api.serializers import UserSerializer
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Na view a gente faz o tratamento do que a url pede. Depende se for get, post, update.
# Sempre retorne em JSON pro front conseguir tratar bem
class RegisterView(CreateAPIView):
    queryset = User.objects.all()  # Pega todos os usuários do banco de dados
    serializer_class = UserSerializer  # Serializa os dados do usuário
    permission_classes = [AllowAny]  # Permite acesso a qualquer usuário, mesmo não autenticado


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class HomeView(APIView):
    permission_classes = [IsAuthenticated]
    print('chega no home view')

    def get(self, request):
        print("Usuário autenticado:", request.user)
        print("Email do usuário:", request.user.email)
        print("Username:", request.user.username)
        print("Dados completos do usuário:", UserSerializer(request.user).data)

        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projetos = Project.objects.filter(userproject__user=request.user)
        serializer = ProjectSerializer(projetos, many=True)
        return Response(serializer.data)

    def post(self, request):
        print("Dados recebidos no POST:", request.data)
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save()
            UserProject.objects.create(
                user=request.user,
                project=project,
                role=ProjectRole.LEADER  # ou ProjectRole.MEMBER se quiser padrão
            )

            collaborator_emails = request.data.get('collaborators', [])
            for email in collaborator_emails:
                try:
                    found_user = User.objects.get(email=email)
                    UserProject.objects.create(user=found_user, project=project, role=ProjectRole.MEMBER)
                except User.DoesNotExist:
                    print(f"Usuário com email: {email} não encontrado. Enviando convite")
                    subject = "Você foi convidado para colaborar em um projeto!"
                    message = f"Olá!\n\nVocê foi convidado para colaborar no projeto '{project.name}' na nossa plataforma. " \
                              f"Se você ainda não tem uma conta, por favor, registre-se usando este e-mail para ter acesso ao projeto." \
                              f"\n\nLink do projeto: https://buildyourproject-front.onrender.com/register"
                    from_email = settings.DEFAULT_FROM_EMAIL
                    recipient_list = [email]
                    
                    try:
                        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                        print(f"Convite enviado para: {email}")
                    except Exception as e:
                        print(f"Falha ao enviar convite para: {email}: {e}")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProjectCollaboratorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

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
