from django.urls import path
from .views import RegisterView, LoginView

# As urls são o que o usuário vai acessar, sempre nesse padrão: 
# Url que o usuário vai ver, nome da url na view, apelido pra referenciar a url no front

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
]
