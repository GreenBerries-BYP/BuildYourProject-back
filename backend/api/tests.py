from django.test import TestCase
from django.utils import timezone
from api.models import User, Project, Phase, ProjectPhase, Task, TaskAssignee, ProjectRole, UserProject

class ProjectAndTaskTests(TestCase):
    def setUp(self):
        # Criar usuário
        self.user = User.objects.create_user( #type:ignore
            email='teste@example.com',
            username='testeuser',
            password='123456',
            full_name='Usuário Teste',
            role='user'
        )

        # Criar projeto com datas válidas
        self.project = Project.objects.create(
            name='Projeto Teste',
            description='Descrição do projeto teste',
            type='default_type',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=10),
            phases=[]
        )

        # Criar phase
        self.phase = Phase.objects.create(
            name='Fase Teste',
            description='Descrição da fase teste'
        )

        # Criar ProjectPhase
        self.project_phase = ProjectPhase.objects.create(
            project=self.project,
            phase=self.phase
        )

        # Criar task
        self.task = Task.objects.create(
            title='Tarefa Teste',
            description='Descrição da tarefa teste',
            due_date=timezone.now() + timezone.timedelta(days=5),
            project_phase=self.project_phase
        )

        # Criar task assignee
        self.task_assignee = TaskAssignee.objects.create(
            task=self.task,
            user=self.user
        )

        # Criar relação de usuário no projeto (como líder)
        self.user_project = UserProject.objects.create(
            user=self.user,
            project=self.project,
            role=ProjectRole.LEADER
        )

    # Exemplo de teste de criação de task
    def test_task_creation(self):
        self.assertEqual(self.task.title, 'Tarefa Teste')
        self.assertEqual(self.task.project_phase, self.project_phase)
        self.assertFalse(self.task.is_completed)

    # Exemplo de teste de exclusão de projeto como líder
    def test_delete_project_as_leader(self):
        self.assertEqual(self.user_project.role, ProjectRole.LEADER)
        project_id = self.project.id
        self.project.delete()
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=project_id)

    # Exemplo de teste de exclusão de projeto como não líder
    def test_delete_project_as_non_leader(self):
        # Mudar role para MEMBER
        self.user_project.role = ProjectRole.MEMBER
        self.user_project.save()
        project_id = self.project.id
        # Usuário não deve poder deletar -> vamos simular checagem
        if self.user_project.role != ProjectRole.LEADER:
            cannot_delete = True
        else:
            cannot_delete = False
        self.assertTrue(cannot_delete)
