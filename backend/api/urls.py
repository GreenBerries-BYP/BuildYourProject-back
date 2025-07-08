from django.urls import path
from .views import RegisterView, LoginView, HomeView, ProjectView, ProjectCollaboratorsView, ProjectShareWithMeView



# As urls são o que o usuário vai acessar, sempre nesse padrão: 
# Url que o usuário vai ver, nome da url na view, apelido pra referenciar a url no front

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("home/", HomeView.as_view(), name='home'),
    path('projetos/', ProjectView.as_view(), name='projetos'),
    path('projetos/<int:project_id>/collaborators/', ProjectCollaboratorsView.as_view(), name='project-collaborators'),
    path('projetos/sharewithme/', ProjectShareWithMeView.as_view(), name='project-share-with-me'),

]
