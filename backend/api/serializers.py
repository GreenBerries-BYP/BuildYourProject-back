from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
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
            'registration_date',  # campo correto do model
            'role'  
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'registration_date': {'read_only': True},
            'role': {'required': False, 'default': 'user'},  # padronizando para 'user'
        }

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

    class Meta:
        model = Project
        fields = [
            'id',  
            'name',  
            'description',  
            'type',
            'created_at',
            'due_date',
            'creator_name',  # campo adicionado
        ]

    def get_creator_name(self, obj):
        leader_relation = UserProject.objects.filter(project=obj, role='leader').select_related('user').first()
        return leader_relation.user.full_name if leader_relation else None

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
            'phase',  
            'order',
        ]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id',  
            'project_phase',  
            'title',  
            'description',  
            'is_completed',  
            'created_at',  # antes creation_date
            'due_date'     # antes delivery_date
        ]
        read_only_fields = ['created_at']


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