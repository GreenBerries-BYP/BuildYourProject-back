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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
