from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api.views.authentication_views import (
    RegisterView, 
    LoginView,
    GoogleLoginView,
    SendResetCodeView,
    VerifyResetCodeView,
    ResetPasswordView,
)
from api.views.project_views import (
    ProjectView,
    ProjectCollaboratorsView,
    ProjectShareWithMeView,
    ProjectDeleteView,
    TaskAssignView,
)
from api.views.task_views import (
    ProjectTasksView,
    TaskUpdateStatusView,
    CreateTaskView,
)
from api.views.google_views import GoogleCalendarSyncView
from api.views.utility_views import (
    HomeView,
    UserConfigurationView, 
    TermsView, 
    PoliticsView,
)
from api.views.analise_inteligente_views import (
    AnalisarProjetoView,
    AplicarSugestaoView
)

urlpatterns = [
    # Rotas Estáticas
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("home/", HomeView.as_view(), name='home'),
    path('projetos/', ProjectView.as_view(), name='projetos'),
    path('use_terms/', TermsView.as_view(), name='use_terms'),
    path('politics/', PoliticsView.as_view(), name='politics'),
    path('projetos/sharewithme/', ProjectShareWithMeView.as_view(), name='project-share-with-me'),

    # Rotas dinâmicas
    path('projetos/<int:project_id>/collaborators/', ProjectCollaboratorsView.as_view(), name='project-collaborators'),
    path('projetos/<int:project_id>/tasks/', ProjectTasksView.as_view(), name='project-tasks'),
    path('tasks/<int:pk>/', TaskUpdateStatusView.as_view(), name='task-update-status'),
    path('user/', UserConfigurationView.as_view(), name='user-config'),
    path('projetos/<int:project_id>/tarefas-novas/', CreateTaskView.as_view(), name='create-task'),
    path('tasks/<int:task_id>/assign/', TaskAssignView.as_view(), name='task-assign'),
    path("auth/google/", GoogleLoginView.as_view(), name="google_login"),
    path("auth/send-reset-code/", SendResetCodeView.as_view(), name="send-reset-code"),
    path("auth/verify-reset-code/", VerifyResetCodeView.as_view(), name="verify-reset-code"),
    path("auth/reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    
    path('projetos/<int:project_id>/delete/', ProjectDeleteView.as_view(), name='project-delete'),

    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("google/calendar/sync/", GoogleCalendarSyncView.as_view(), name="google_calendar_sync"),

    # IMPLEMENTAÇÃO ML
    path('projetos/<int:project_id>/analisar/', AnalisarProjetoView.as_view(), name='analisar-projeto'),
    path('projetos/<int:project_id>/aplicar-sugestao/', AplicarSugestaoView.as_view(), name='aplicar-sugestao'),
]