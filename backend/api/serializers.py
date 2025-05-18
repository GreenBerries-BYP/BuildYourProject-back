from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import (
    User, Project, UserProject, Phase, ProjectPhase,
    Task, TaskAssignee, ChatMessage, TaskAttachment
)

# Serializer pega os dados do model (vindo do banco de dados) e cria um JSON para enviar pro front
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'full_name', 'registration_date', 'role']
        # Os extra kwargs são usados para configurar comportamentos específicos dentro dos campos
        # write_only - Só é enviado no json, mas não será mostrado no retorno
        # read_only - Só será exibido no retorno, não será enviado
        # required - Campo obrigatório no json
        # default - Terá um valor padrão se nada for enviado no json
        # allow blank - Pode ter um valor em branco
        # allow null - Pode ter um valor nulo
        extra_kwargs = {
            "password": {"write_only": True},  # Por segurança, não exibir no retorno da API
            "registration_date": {"read_only": True},
            "role": {"required": False, "default": "user"},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        role = validated_data.get("role", "user")
        
        user = User(**validated_data)
        user.role = role # Define o papel do usuário, se não for enviado, será "user"
        user.set_password(password)
        user.save()
        return user

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'creator', 'theme', 'creation_date', 'delivery_date']
        read_only_fields = ['creation_date', 'creator']


class UserProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProject
        fields = ['id', 'user', 'project', 'role']


class PhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phase
        fields = ['id', 'name', 'description']


class ProjectPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPhase
        fields = ['id', 'project', 'phase', 'order']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'project_phase', 'title', 'description', 'is_completed', 'creation_date', 'delivery_date']
        read_only_fields = ['creation_date']


class TaskAssigneeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssignee
        fields = ['id', 'task', 'user_project']


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'project', 'sender', 'content', 'sent_at']
        read_only_fields = ['sent_at']


class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = ['id', 'task', 'file', 'uploaded_at']
        read_only_fields = ['uploaded_at']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD  # Define o campo de username como email

    @classmethod #Classmethod é um decorator que transforma a função em um método de classe, é usado para acessar atributos e métodos da classe sem precisar instanciar um objeto
    def get_token(cls, user): #cls é a classe, user é o usuário que está logado
        token = super().get_token(user) #Gera o token padrão
        token['username'] = user.username
        token['role'] = user.role
        #Adiciona o campo username e role no token, pode add mais
        return token

    def validate(self, attrs): #attrs é o dicionário que contém os dados enviados pelo usuário
        attrs['username'] = attrs.get("email") #Coloca o email no lugar do username
        #Django usa o username para autenticar o usuário, então precisamos colocar o email no lugar do username
        # Isso é necessário porque o Django não tem um campo de email por padrão
        return super().validate(attrs)