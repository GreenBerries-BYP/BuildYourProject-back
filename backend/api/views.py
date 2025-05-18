from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
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

