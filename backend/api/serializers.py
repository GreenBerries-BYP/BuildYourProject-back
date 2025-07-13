from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
import re 


from .models import (
    User, Project, UserProject, Phase, ProjectPhase,
    Task, TaskAssignee, Chat
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',  
            'username',
            'email',
            'password',
            'full_name',  
            'registration_date',
            'role'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'registration_date': {'read_only': True},
            'role': {'required': False, 'default': 'user'},  # valor padrão
        }

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("A senha deve ter no mínimo 8 caracteres.")
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra maiúscula.")
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra minúscula.")
        if not re.search(r"\d", value):
            raise serializers.ValidationError("A senha deve conter pelo menos um número.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError("A senha deve conter pelo menos um caractere especial.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  
        user.save()
        return user


    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.get('role', 'user')
        user = User(**validated_data)
        user.role = role
        user.set_password(password)
        user.save()
        return user

# # alterado pra alinhar com o front
# class ProjectSerializer(serializers.ModelSerializer):
#     # O model não tem 'creator', só created_at e due_date
#     class Meta:
#         model = Project
#         fields = [
#             'id',  
#             'name',  
#             'description',  
#             'type',
#             'created_at',  # antes creation_date
#             'due_date',    # antes delivery_date
#         ]

class ProjectSerializer(serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()
    collaborators_info = serializers.SerializerMethodField()  # só para exibir no GET
    collaborator_count = serializers.SerializerMethodField()

    startDate = serializers.DateTimeField(source='start_date')
    endDate = serializers.DateTimeField(source='end_date')

    phases = serializers.ListField(child=serializers.CharField(), write_only=True)
    collaborators = serializers.ListField(
        child=serializers.EmailField(), write_only=True, required=False
    )

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'description',
            'type',
            'startDate',
            'endDate',
            'creator_name',
            'phases',
            'collaborators',
            'collaborators_info',
            'collaborator_count',
        ]

    def get_creator_name(self, obj):
        leader_relation = UserProject.objects.filter(project=obj, role='leader').select_related('user').first()
        return leader_relation.user.full_name if leader_relation else None

    def get_collaborators_info(self, obj):
        user_projects = UserProject.objects.filter(project=obj).select_related('user')
        return [{'id': up.user.id, 'full_name': up.user.full_name, 'email': up.user.email} for up in user_projects]

    def get_collaborator_count(self, obj):
        return UserProject.objects.filter(project=obj).count()

    def validate_phases(self, value):
        if not value:
            raise serializers.ValidationError("O campo fases é obrigatório e não pode estar vazio.")
        if not isinstance(value, list):
            raise serializers.ValidationError("Fases deve ser uma lista de strings.")
        if not all(isinstance(item, str) for item in value):
            raise serializers.ValidationError("Todos os itens da lista de fases devem ser strings.")
        return value

    def create(self, validated_data):
        phases_data = validated_data.pop('phases', [])
        collaborators_data = validated_data.pop('collaborators', [])

        project = Project.objects.create(**validated_data)
        project.phases = phases_data
        project.save()

        # Criar fases, relacionar e criar tarefas
        for phase_name in phases_data:
            phase_obj, created = Phase.objects.get_or_create(name=phase_name)
            project_phase = ProjectPhase.objects.create(project=project, phase=phase_obj)
            Task.objects.create(
                project_phase=project_phase,
                title=phase_name,
                description=f"Fase inicial do projeto: {phase_name}",
                is_completed=False,
                due_date=project.end_date
            )

        # Note: Criação dos UserProject para colaboradores fica na view (como você fez)

        return project



class UserProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProject
        fields = [
            'id',  
            'user',  
            'project',  
            'role'  
        ]


class PhaseSerializer(serializers.ModelSerializer):
    class Meta:
        print('chega no phaseSerializer')
        model = Phase
        fields = [
            'id',  
            'name',  
            'description',  
            'parent_phase'  
        ]


class ProjectPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPhase
        fields = [
            'id',  
            'project',  
            'phase'
        ]

# alterado pra alinhar com o front
class TaskSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='title')
    prazo = serializers.DateTimeField(source='due_date')
    responsavel = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id',
            'nome',
            'responsavel',
            'prazo',
            'status',
        ]

    def get_responsavel(self, obj):
        assignee = TaskAssignee.objects.filter(task=obj).select_related('user').first()
        return assignee.user.full_name if assignee else None

    def get_status(self, obj):
        return 'concluído' if obj.is_completed else 'pendente'

class TaskAssigneeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssignee
        fields = [
            'id',  
            'task',  
            'user'  # model aponta para user, não user_project
        ]


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = [
            'id',  
            'project',  
            'user',  # antes sender
            'content',  
            'sent_at'  
        ]
        read_only_fields = ['sent_at']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['role'] = user.role
        return token

    def validate(self, attrs):
        attrs['username'] = attrs.get('email')
        return super().validate(attrs)
    
# serializers.py

class SimpleTaskSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    is_completed = serializers.BooleanField()  

    class Meta:
        model = Task
        fields = ['title', 'is_completed']


class ProjectWithTasksSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'tasks']

    def get_tasks(self, project):
        fase_ids = ProjectPhase.objects.filter(project=project).values_list('id', flat=True)
        tarefas = Task.objects.filter(project_phase__id__in=fase_ids).order_by('due_date')
        return SimpleTaskSerializer(tarefas, many=True).data

