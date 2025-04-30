from django.urls import path
from .views import hello_world

#As urls são o que o usuário vai acessar, sempre nesse padrão: 
#Url que o usuário vai ver, nome da url na view, apelido pra referenciar a url no front

urlpatterns = [
    path('hello/', hello_world),
    
    # Rotas de Autenticação
    path("auth/register/", views.UserCreateView.as_view(), name="register"),
]
