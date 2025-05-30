from django.http import JsonResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomTokenObtainPairSerializer
from api.models import User
from api.serializers import UserSerializer

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