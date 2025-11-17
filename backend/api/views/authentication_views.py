from django.conf import settings
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
import requests
import os

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

def send_mail_async(subject, html_content, from_email, recipient_list):
    """Usa API direta do Resend para enviar email HTML"""
    def _enviar():
        try:
            print(f"API RESEND - RECUPERAÇÃO SENHA PARA: {recipient_list}")

            api_key = os.environ.get('RESEND_API_KEY')
            url = os.environ.get('RESEND_API_URL') 
            
            payload = {
                "from": from_email,
                "to": recipient_list,
                "subject": subject,
                "html": html_content
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            print(f" RESPOSTA RECUPERAÇÃO: {response.status_code}")
            
            if response.status_code == 200:
                print(f" EMAIL DE RECUPERAÇÃO ENVIADO!")
            else:
                print(f" ERRO RECUPERAÇÃO: {response.text}")
                
        except Exception as e:
            print(f"ERRO API RECUPERAÇÃO: {str(e)}")
    
    thread = threading.Thread(target=_enviar)
    thread.daemon = True
    thread.start()

def create_reset_email_html(code):
    """Cria o template HTML personalizado para o email de reset"""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(166deg, #8474a1 0%, #86b6a3 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .logo-container {{
            margin-bottom: 15px;
        }}
        .logo {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 40px 30px;
            color: #383560;
            line-height: 1.6;
        }}
        .code {{
            background: #c1d5cd;
            border: 2px dashed #58917a;
            border-radius: 10px;
            padding: 25px;
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            color: #045a5c;
            margin: 25px 0;
            letter-spacing: 5px;
        }}
        .footer {{
            background: #c8c1d4;
            padding: 25px;
            text-align: center;
            color: #383560;
            font-size: 14px;
        }}
        .footer-image {{
            display: block;
            margin: 15px auto;
            max-width: 200px;
            height: auto;
        }}
        .info-text {{
            color: #54969a;
            font-size: 14px;
            margin-top: 10px;
        }}
        .brand-text {{
            font-size: 20px;
            font-weight: bold;
            color: #5b4584;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo-container">
                <div class="logo">BuildYourProject</div>
            </div>
            <div style="font-size: 18px;">Redefinição de Senha</div>
        </div>
        
        <div class="content">
            <h2 style="color: #5b4584; margin-top: 0;">Olá!</h2>
            <p>Você solicitou a redefinição de sua senha no <strong style="color: #8474a1;">BuildYourProject</strong>.</p>
            
            <p>Seu código de verificação é:</p>
            <div class="code">{code}</div>
            
            <p class="info-text"><strong>⚠️ Este código expira em 10 minutos.</strong></p>
            
            <p>Se você não solicitou esta redefinição, ignore este email.</p>
        </div>
        
        <div class="footer">
            <p>Atenciosamente,<br>
            <strong>Equipe BuildYourProject</strong></p>
        
            <img src="https://github.com/GreenBerries-BYP/BuildYourProject-front/blob/main/BYP_logo_slogan.png?raw=true" alt="BuildYourProject" class="footer-image"> 
            
            <p style="margin-top: 15px; font-size: 12px; color: #5b4584;">
                © 2025 BuildYourProject. Todos os direitos reservados.
            </p>
        </div>
    </div>
</body>
</html>
"""

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
        
        # HTML PERSONALIZADO
        html_message = create_reset_email_html(code)
        
        from_email = settings.DEFAULT_FROM_EMAIL

        # Debug: Verificar configurações de email
        print(f" Configurações de Email:")
        print(f"   FROM_EMAIL: {from_email}")
        print(f"   EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Não configurado')}")
        print(f"   EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Não configurado')}")
        
        try:
            threading.Thread(
                target=send_mail_async,
                args=(subject, html_message, from_email, [email])
            ).start()
            
            print(f"Email de reset enviado para: {email}")
            
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
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
