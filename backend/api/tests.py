from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import User, Project, UserProject, Phase, ProjectPhase, Task

class ProjectSharedWithMeTests(TestCase):
    def setUp(self):
        # Criar usuários
        self.user_owner = User.objects.create_user(
            username='owneruser',
            email='owner@example.com',
            password='password123'
        )
        self.user_member = User.objects.create_user(
            username='memberuser',
            email='member@example.com',
            password='password123'
        )
        self.user_outsider = User.objects.create_user(
            username='outsideruser',
            email='outsider@example.com',
            password='password123'
        )

        # Criar projeto
        self.project = Project.objects.create(
            name="Projeto Teste",
            description="Projeto de teste",
            type="tipo1",
            start_date="2025-01-01T00:00:00Z",
            end_date="2025-12-31T00:00:00Z"
        )

        # Relacionar usuários ao projeto
        UserProject.objects.create(user=self.user_owner, project=self.project, role='leader')
        UserProject.objects.create(user=self.user_member, project=self.project, role='member')

        # Criar fase
        self.phase = Phase.objects.create(name="Fase 1")
        self.project_phase = ProjectPhase.objects.create(project=self.project, phase=self.phase)

        # Criar tarefa
        self.task = Task.objects.create(
            project_phase=self.project_phase,
            title="Tarefa 1",
            description="Descrição da tarefa 1",
            is_completed=False,
            due_date="2025-12-31T00:00:00Z"
        )

        # Configurar cliente REST
        self.client = APIClient()

    def authenticate(self, user):
        """Autenticar cliente com JWT"""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_shared_projects_with_tasks_as_member(self):
        """Usuário membro vê o projeto compartilhado com suas tarefas"""
        self.authenticate(self.user_member)
        response = self.client.get('/api/projetos/sharewithme/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        projeto = response.data[0]
        self.assertEqual(projeto['id'], self.project.id)
        self.assertEqual(len(projeto['tarefasProjeto']), 1)
        self.assertEqual(projeto['tarefasProjeto'][0]['nomeTarefa'], "Tarefa 1")


    def test_shared_projects_with_tasks_as_outsider(self):
        """Usuário que não está no projeto não vê nada"""
        self.authenticate(self.user_outsider)
        response = self.client.get('/api/projetos/sharewithme/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_unauthenticated_user(self):
        """Usuário não autenticado recebe 401"""
        self.client.credentials()  # Remove autenticação
        response = self.client.get('/api/projetos/sharewithme/')
        self.assertEqual(response.status_code, 401)
