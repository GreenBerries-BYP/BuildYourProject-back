from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Project, UserProject, ProjectRole

class ShareWithMeViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Cria dois usuários
        self.user_leader = User.objects.create_user(
            email='lider@email.com',
            username='lider',
            password='senha123',
            full_name='Líder Teste',
            role='user'
        )

        self.user_member = User.objects.create_user(
            email='membro@email.com',
            username='membro',
            password='senha123',
            full_name='Membro Teste',
            role='user'
        )

        # Cria um projeto
        self.project = Project.objects.create(
            name='Projeto Teste',
            description='Descrição do projeto',
            type='tipo',
            start_date='2025-07-01T00:00:00Z',
            end_date='2025-12-01T00:00:00Z',
            phases=[]
        )

        # Liga o líder ao projeto
        UserProject.objects.create(user=self.user_leader, project=self.project, role=ProjectRole.LEADER)
        # Liga o membro ao projeto
        UserProject.objects.create(user=self.user_member, project=self.project, role=ProjectRole.MEMBER)

    def test_projects_shared_with_user(self):
        # Autentica o membro
        self.client.force_authenticate(user=self.user_member)

        # Faz a requisição para a view
        response = self.client.get('/api/projetos/sharewithme/')

        # Verifica se o projeto foi retornado
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Projeto Teste')
