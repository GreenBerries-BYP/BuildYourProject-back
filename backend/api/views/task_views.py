from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from ..models import Project, UserProject, ProjectPhase, Task, TaskAssignee, Phase, ProjectRole
from ..serializers import TaskSerializer

User = get_user_model()

class ProjectTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        if not UserProject.objects.filter(user=request.user, project_id=project_id).exists():
            return Response({"detail": "Você não tem acesso a este projeto."}, status=status.HTTP_403_FORBIDDEN)

        try:
            project = Project.objects.select_related().get(id=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        leader = UserProject.objects.filter(project=project, role=ProjectRole.LEADER).first()
        creator_name = leader.user.full_name if leader else None

        collaborators_qs = UserProject.objects.filter(project=project).select_related('user')
        collaborators = [up.user.full_name for up in collaborators_qs]

        tarefasProjeto = []
        project_phases = ProjectPhase.objects.filter(project=project).prefetch_related(
            'task_set',
            'task_set__taskassignee_set',
            'task_set__taskassignee_set__user'
        )
        
        for pp in project_phases:
            phase = pp.phase
            tasks = pp.task_set.all()

            total_tasks = tasks.count()
            completed_tasks = tasks.filter(is_completed=True).count()
            progresso = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

            subTarefas = []
            for task in tasks:
                assignees = task.taskassignee_set.select_related('user')
                responsaveis = [a.user.full_name for a in assignees]

                subTarefas.append({
                    "id": task.id,
                    "title": task.title,
                    "is_completed": task.is_completed,
                    "responsavel": ", ".join(responsaveis) if responsaveis else None,
                    "prazo": task.due_date.strftime("%d/%m/%Y") if task.due_date else None,
                    "status": "concluído" if task.is_completed else "pendente"
                })

            tarefasProjeto.append({
                "id": phase.id,
                "nomeTarefa": phase.name,
                "progresso": progresso,
                "subTarefas": subTarefas
            })

        projeto_data = {
            "name": project.name,
            "creator_name": creator_name,
            "collaborator_count": collaborators_qs.count(),
            "collaborators": collaborators,
            "tarefasProjeto": tarefasProjeto
        }

        return Response(projeto_data, status=status.HTTP_200_OK)

    def post(self, request, project_id):
        if not UserProject.objects.filter(user=request.user, project_id=project_id).exists():
            return Response({"detail": "Você não tem acesso a este projeto."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        try:
            phase = ProjectPhase.objects.get(id=data.get("phase_id"), project_id=project_id)
        except ProjectPhase.DoesNotExist:
            return Response({"detail": "Fase não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        task = Task.objects.create(
            title=data.get("title"),
            description=data.get("description", ""),
            is_completed=data.get("is_completed", False),
            due_date=data.get("due_date"),
            project_phase=phase
        )

        assignee_ids = data.get("assignee_ids", [])
        for uid in assignee_ids:
            try:
                user = User.objects.get(id=uid)
                TaskAssignee.objects.create(task=task, user=user)
            except User.DoesNotExist:
                continue

        return Response({"detail": "Tarefa criada com sucesso.", "task_id": task.id}, status=status.HTTP_201_CREATED)

    def patch(self, request, project_id, task_id):
        if not UserProject.objects.filter(user=request.user, project_id=project_id).exists():
            return Response({"detail": "Você não tem acesso a este projeto."}, status=status.HTTP_403_FORBIDDEN)

        try:
            task = Task.objects.get(id=task_id, project_phase__project_id=project_id)
        except Task.DoesNotExist:
            return Response({"detail": "Tarefa não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        is_completed = request.data.get("is_completed")
        if is_completed is None or not isinstance(is_completed, bool):
            return Response({"error": "O campo 'is_completed' deve ser booleano."}, status=status.HTTP_400_BAD_REQUEST)

        task.is_completed = is_completed
        task.save()
        return Response({"detail": "Status atualizado com sucesso."})

    def delete(self, request, project_id, task_id):
        if not UserProject.objects.filter(user=request.user, project_id=project_id).exists():
            return Response({"detail": "Você não tem acesso a este projeto."}, status=status.HTTP_403_FORBIDDEN)

        try:
            task = Task.objects.get(id=task_id, project_phase__project_id=project_id)
        except Task.DoesNotExist:
            return Response({"detail": "Tarefa não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        task.delete()
        return Response({"detail": "Tarefa excluída com sucesso."}, status=status.HTTP_204_NO_CONTENT)

class CreateTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        if not UserProject.objects.filter(user=request.user, project_id=project_id).exists():
            return Response({"detail": "Você não tem acesso a este projeto."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()

        phase_obj, _ = Phase.objects.get_or_create(name=data.get("nome"))
        project_phase = ProjectPhase.objects.create(project_id=project_id, phase=phase_obj)

        task = Task.objects.create(
            project_phase=project_phase,
            title=data.get("nome"),
            description=data.get("descricao", ""),
            is_completed=False,
            due_date=data.get("dataEntrega")
        )

        responsavel_id = data.get("responsavel")
        if responsavel_id:
            try:
                user = User.objects.get(id=responsavel_id)
                TaskAssignee.objects.create(task=task, user=user)
            except User.DoesNotExist:
                pass

        return Response({"detail": "Tarefa criada com sucesso.", "task_id": task.id}, status=status.HTTP_201_CREATED)

class TaskUpdateStatusView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def patch(self, request, *args, **kwargs):
        task = self.get_object()
        is_completed = request.data.get('is_completed')

        if is_completed is None:
            return Response({"error": "O campo 'is_completed' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(is_completed, bool):
            return Response({"error": "O campo 'is_completed' deve ser booleano."}, status=status.HTTP_400_BAD_REQUEST)
        
        task.is_completed = is_completed
        task.save()
        
        return Response({"detail": "Status atualizado com sucesso."})
    
class TaskAssignView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        try:
            task = Task.objects.select_related(
                'project_phase__project'
            ).get(id=task_id)
        except Task.DoesNotExist:
            return Response({"error": "Tarefa não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        # Verificar se o usuário tem acesso ao projeto da tarefa
        project = task.project_phase.project
        if not UserProject.objects.filter(user=request.user, project=project).exists():
            return Response({"detail": "Você não tem acesso a este projeto."}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "ID do usuário é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_to_assign = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Verificar se o usuário a ser atribuído é colaborador do projeto
        if not UserProject.objects.filter(user=user_to_assign, project=project).exists():
            return Response({"error": "Este usuário não é colaborador do projeto."}, status=status.HTTP_400_BAD_REQUEST)

        # Criar a atribuição da tarefa (permite múltiplos assignees se necessário)
        task_assignee, created = TaskAssignee.objects.get_or_create(
            task=task,
            user=user_to_assign
        )

        # Serializar os dados do usuário para retornar ao frontend
        user_data = {
            "id": user_to_assign.id,
            "full_name": user_to_assign.full_name,
            "email": user_to_assign.email,
            "name": user_to_assign.full_name  # Para compatibilidade com frontend
        }

        # Serializar a tarefa atualizada
        task_serializer = TaskSerializer(task)

        return Response({
            "detail": "Tarefa atribuída com sucesso." if created else "Tarefa já estava atribuída a este usuário.",
            "task_id": task.id,
            "assigned_user": user_data,
            "task": task_serializer.data
        }, status=status.HTTP_200_OK)