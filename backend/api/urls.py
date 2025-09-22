from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, 
    LoginView, 
    HomeView, 
    ProjectView, 
    ProjectCollaboratorsView, 
    ProjectShareWithMeView, 
    ProjectTasksView, 
    TaskUpdateStatusView,
    UserConfigurationView, 
    TermsView, 
    PoliticsView, 
    GoogleLoginView,
    CreateTaskView,
    SendResetCodeView,
    VerifyResetCodeView,
    ProjectDeleteView, 
    GoogleCalendarSyncView,
    AnaliseProjetoView,
    AplicarSugestaoView
)

# As urls são o que o usuário vai acessar, sempre nesse padrão: 
# Url que o usuário vai ver, nome da url na view, apelido pra referenciar a url no front

urlpatterns = [
    # Rotas Estáticas
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("home/", HomeView.as_view(), name='home'),
    path('projetos/', ProjectView.as_view(), name='projetos'),
    path('use_terms/', TermsView.as_view(), name='use_terms'),
    path('politics/', PoliticsView.as_view(), name='politics'),
    path('projetos/sharewithme/', ProjectShareWithMeView.as_view(), name='project-share-with-me'),

    # Rotas dinamicas
    path('projetos/<int:project_id>/collaborators/', ProjectCollaboratorsView.as_view(), name='project-collaborators'),
    path('projects/<int:project_id>/tasks/', ProjectTasksView.as_view(), name='project-tasks'),
    path('tasks/<int:pk>/', TaskUpdateStatusView.as_view(), name='task-update-status'),
    path('user/', UserConfigurationView.as_view(), name='user-config'),
    path('projetos/<int:project_id>/tarefas-novas/', CreateTaskView.as_view(), name='create-task'),
 
    path("auth/google/", GoogleLoginView.as_view(), name="google_login"),
    path("auth/send-reset-code/", SendResetCodeView.as_view(), name="send-reset-code"),
    path("auth/verify-reset-code/", VerifyResetCodeView.as_view(), name="verify-reset-code"),

    path('projetos/<int:project_id>/', ProjectView.as_view(), name='delete-project'), # delete project
  
    path('projetos/<int:project_id>/delete/', ProjectDeleteView.as_view(), name='project-delete'),  # DELETE

    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/google/", GoogleLoginView.as_view(), name="google_login"),
    path("google/calendar/sync/", GoogleCalendarSyncView.as_view(), name="google_calendar_sync"),

    # IMPLEMENTAÇÃO ML
    path('projetos/<int:project_id>/analisar/', AnaliseProjetoView.as_view(), name='analisar-projeto'),
    path('projetos/<int:project_id>/aplicar-sugestao/', AplicarSugestaoView.as_view(), name='aplicar-sugestao'),

]
