from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import random
import threading

from ..models import Project, UserProject, ProjectRole
from ..serializers import UserSerializer, CustomTokenObtainPairSerializer
from django.core.cache import cache

User = get_user_model()

def get_verification_code(email):
    return cache.get(f"reset_code_{email}")

def set_verification_code(email, code, timeout=600):  # 10 minutos
    cache.set(f"reset_code_{email}", code, timeout)

def delete_verification_code(email):
    cache.delete(f"reset_code_{email}")

def send_mail_async(subject, message, from_email, recipient_list):
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    except Exception as e:
        print("Erro ao enviar e-mail:", e)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        
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

class SendResetCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

        code = str(random.randint(100000, 999999))
        set_verification_code(email, code)

        print(f"Código de reset para {email}: {code}")

        subject = "Código de Recuperação de Senha - BuildYourProject"
        message = f"""
        Olá!

        Você solicitou a redefinição de sua senha no BuildYourProject.

        Seu código de verificação é: {code}

        Este código expira em 10 minutos.

        Se você não solicitou esta redefinição, ignore este email.

        Atenciosamente,
        Equipe BuildYourProject
        """
        
        from_email = settings.DEFAULT_FROM_EMAIL
        
        try:
            # Envia o email de forma assíncrona
            threading.Thread(
                target=send_mail_async,
                args=(subject, message, from_email, [email])
            ).start()
            
            print(f" Email de reset enviado para: {email}")
            
        except Exception as e:
            print(f" Erro ao enviar email: {e}")
            return Response(
                {'error': 'Erro ao enviar email'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({'message': 'Código enviado com sucesso'}, status=status.HTTP_200_OK)

class VerifyResetCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
            return Response(
                {'error': 'Email e código são obrigatórios'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verifica se o código existe e é válido no cache
        stored_code = get_verification_code(email)
        if not stored_code:
            return Response(
                {'error': 'Código expirado ou não encontrado. Solicite um novo código.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if stored_code != code:
            return Response(
                {'error': 'Código inválido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Código válido - retorna sucesso
        return Response({
            'message': 'Código válido',
            'verified': True
        }, status=status.HTTP_200_OK)
    
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')
        
        if not all([email, code, new_password]):
            return Response({'error': 'Todos os campos são obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)

        stored_code = get_verification_code(email)
        if not stored_code or stored_code != code:
            return Response( 
                {'error': 'Código inválido ou expirado'}, 
                status=status.HTTP_400_BAD_REQUEST
            )  
        
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            delete_verification_code(email)
            
            return Response({'message': 'Senha redefinida com sucesso'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
