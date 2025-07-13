from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
import re

from .models import (
    User, Project, UserProject, Phase, ProjectPhase,
    Task, TaskAssignee, Chat, ProjectRole
)
from . import tasks

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'full_name',
            'registration_date', 'role'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'registration_date': {'read_only': True},
            'role': {'required': False},
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

class ProjectSerializer(serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()
    collaborators_info = serializers.SerializerMethodField()
    collaborator_count = serializers.SerializerMethodField()
    startDate = serializers.DateTimeField(source='start_date', write_only=True)
    endDate = serializers.DateTimeField(source='end_date', write_only=True)
    phases = serializers.JSONField(write_only=True)
    collaborators = serializers.ListField(
        child=serializers.EmailField(), write_only=True, required=False
    )

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'type',
            'startDate', 'endDate', 'phases', 'collaborators',
            'creator_name', 'collaborators_info', 'collaborator_count'
        ]

    def get_collaborator_data(self, obj):
        if hasattr(obj, '_prefetched_objects_cache') and 'user_relations' in obj._prefetched_objects_cache:
            return obj.user_relations.all()
        return obj.user_relations.select_related('user').all()

    def get_creator_name(self, obj):
        for relation in self.get_collaborator_data(obj):
            if relation.role == ProjectRole.LEADER:
                return relation.user.full_name
        return None

    def get_collaborators_info(self, obj):
        return [
            {'id': rel.user.id, 'full_name': rel.user.full_name, 'email': rel.user.email}
            for rel in self.get_collaborator_data(obj)
        ]

    def get_collaborator_count(self, obj):
        return len(self.get_collaborator_data(obj))

    def create(self, validated_data):
        collaborators_emails = validated_data.pop('collaborators', [])
        request_user = self.context['request'].user
        
        project = Project.objects.create(**validated_data)

        UserProject.objects.create(user=request_user, project=project, role=ProjectRole.LEADER)

        for email in collaborators_emails:
            if email == request_user.email:
                continue
            try:
                found_user = User.objects.get(email=email)
                UserProject.objects.create(user=found_user, project=project, role=ProjectRole.MEMBER)
            except User.DoesNotExist:
                tasks.send_project_invitation_email.delay(
                    recipient_email=email,
                    project_name=project.name
                )

        for phase_name in project.phases:
            phase_obj, _ = Phase.objects.get_or_create(name=phase_name)
            project_phase = ProjectPhase.objects.create(project=project, phase=phase_obj)
            Task.objects.create(
                project_phase=project_phase, title=phase_name,
                description=f"Fase inicial do projeto: {phase_name}",
                due_date=project.end_date
            )
        return project

class TaskSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='title')
    prazo = serializers.DateTimeField(source='due_date')
    responsavel = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'nome', 'responsavel', 'prazo', 'status']

    def get_responsavel(self, obj):
        assignee = obj.assignees.select_related('user').first()
        return assignee.user.full_name if assignee else None

    def get_status(self, obj):
        return 'concluído' if obj.is_completed else 'pendente'

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['full_name'] = self.user.full_name
        data['id'] = self.user.id
        return data

class SimpleTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'is_completed', 'due_date']

class ProjectWithTasksSerializer(ProjectSerializer):
    tasks = serializers.SerializerMethodField()

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['tasks']

    def get_tasks(self, obj):
        all_tasks = []
        if hasattr(obj, '_prefetched_objects_cache') and 'phases_relations' in obj._prefetched_objects_cache:
            for phase_relation in obj.phases_relations.all():
                all_tasks.extend(phase_relation.tasks.all())
        return SimpleTaskSerializer(all_tasks, many=True).data

class TaskFullInfoSerializer(serializers.ModelSerializer):
    responsaveis = serializers.StringRelatedField(many=True, source='assignees')
    fase = serializers.CharField(source='project_phase.phase.name', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'is_completed',
            'created_at', 'due_date', 'fase', 'responsaveis',
        ]

class ProjectWithCollaboratorsAndTasksSerializer(ProjectWithTasksSerializer):
    pass