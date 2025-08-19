from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Project, UserProject, ProjectPhase, Task

class UserConfigTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_config_url = reverse('user-config')
        self.project_url = reverse('projetos')
        self.project_share_url = reverse('project-share-with-me')

        # Usuário inicial para login
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Abcd1234!",
            "full_name": "Test User"
        }

    def test_user_lifecycle(self):
        # 1. Registrar usuário
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=self.user_data['email'])

        # 2. Login
        login_data = {"email": self.user_data['email'], "password": self.user_data['password']}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        # 3. Atualizar dados do usuário
        update_data = {"full_name": "Updated User", "password": "Xyz12345!"}
        response = self.client.patch(self.user_config_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.full_name, "Updated User")


class ProjectCRUDTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='creator', email='creator@example.com',
            password='Abcd1234!', full_name='Project Creator'
        )
        self.client.force_authenticate(user=self.user)

        self.project_data = {
            "name": "Test Project",
            "description": "Project description",
            "type": "Software",
            "startDate": "2025-08-18T10:00:00Z",
            "endDate": "2025-08-25T10:00:00Z",
            "phases": ["Phase 1", "Phase 2"],
            "collaborators": ["collab1@example.com"]
        }

    def test_project_crud(self):
        # 1. Criar projeto
        response = self.client.post(reverse('projetos'), self.project_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(name="Test Project")

        # Checa se líder foi criado
        self.assertTrue(UserProject.objects.filter(user=self.user, project=project, role='leader').exists())

        # 2. Listar projetos do usuário
        response = self.client.get(reverse('projetos'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # 3. Buscar colaboradores
        url_collab = reverse('project-collaborators', args=[project.id])
        response = self.client.get(url_collab)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(up['email'] == 'creator@example.com' for up in response.data))

        # 4. Criar tarefa em uma fase
        phase = ProjectPhase.objects.filter(project=project).first()
        task_data = {
            "title": "New Task",
            "description": "Task description",
            "is_completed": False,
            "due_date": "2025-08-24T10:00:00Z",
            "phase_id": phase.id,
            "assignee_ids": [self.user.id]
        }
        url_tasks = reverse('project-tasks', args=[project.id])
        response = self.client.post(url_tasks, task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task_id = response.data['task_id']

        # 5. Atualizar status da tarefa
        url_task_update = reverse('task-update-status', args=[task_id])
        response = self.client.patch(url_task_update, {"is_completed": True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = Task.objects.get(id=task_id)
        self.assertTrue(task.is_completed)

        # 6. Projetos compartilhados (share with me) - deve estar vazio
        response = self.client.get(reverse('project-share-with-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
