from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import *

class ProjectViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='teste@example.com', 
            username='testeuser', 
            password='Senha@1234', 
            full_name='Teste User',
            role='user'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.project_list_url = reverse('projetos')

    def test_get_projects_empty(self):
        response = self.client.get(self.project_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "Projetos listados com sucesso")
        self.assertEqual(response.data['data'], [])

    def test_post_create_project_success(self):
        payload = {
            "name": "Projeto Teste",
            "description": "Descrição do projeto",
            "type": "default_type",
            "startDate": "2025-08-01T10:00:00Z",
            "endDate": "2025-08-10T10:00:00Z",
            "phases": ["Fase 1", "Fase 2"],
            "collaborators": []
        }
        response = self.client.post(self.project_list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "Projeto criado com sucesso!")
        self.assertIn('name', response.data['data'])
        self.assertEqual(response.data['data']['name'], "Projeto Teste")

    def test_post_create_project_fail(self):
        # Enviar payload vazio deve falhar
        payload = {}
        response = self.client.post(self.project_list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], "Erro ao criar projeto")
        self.assertIn('name', response.data['errors'])
        self.assertIn('description', response.data['errors'])
        self.assertIn('startDate', response.data['errors'])
        self.assertIn('endDate', response.data['errors'])
        self.assertIn('phases', response.data['errors'])

class TaskUpdateStatusTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='teste2@example.com',
            username='user2',
            password='Senha@1234',
            full_name='User Dois',
            role='user'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Criar projeto e tarefa para o teste
        self.project = Project.objects.create(
            name="Projeto Tarefa",
            description="Projeto para teste tarefa",
            type="default_type",
            start_date="2025-08-01T10:00:00Z",
            end_date="2025-08-10T10:00:00Z",
            phases=[]
        )
        UserProject.objects.create(user=self.user, project=self.project, role=ProjectRole.LEADER)
        
        phase = Phase.objects.create(name="Fase Teste", description="Fase de teste")
        project_phase = ProjectPhase.objects.create(project=self.project, phase=phase)
        self.task = Task.objects.create(
            title="Tarefa Teste",
            description="Descrição da tarefa",
            due_date="2025-08-10T10:00:00Z",
            project_phase=project_phase,
            is_completed=False
        )
        self.task_update_url = reverse('task-update-status', args=[self.task.id])

    def test_patch_update_status_success(self):
        response = self.client.patch(self.task_update_url, {'is_completed': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "Status da tarefa atualizado")
        self.assertTrue(response.data['data']['status'] == 'concluído')

    def test_patch_update_status_missing_field(self):
        response = self.client.patch(self.task_update_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], "Erro de validação")
        self.assertIn('is_completed', response.data['errors'])

    def test_patch_update_status_invalid_field(self):
        response = self.client.patch(self.task_update_url, {'is_completed': 'not_bool'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], "Erro de validação")
        self.assertIn('is_completed', response.data['errors'])
