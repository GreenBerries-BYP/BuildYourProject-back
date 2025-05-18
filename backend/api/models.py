from django.db import models
from django.contrib.auth.models import AbstractUser

# Camada de models serve pra definir os dados que serão salvos na aplicação
# Os atributos de usuário que virarão tabela no banco de dados têm que ser descritos aqui
# Nesse caso, o usuário vai herdar tudo de AbstractUser, que é um usuário padrão que o Django cria (login e senha)
class SystemRole(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    USER = 'user', 'Usuário'  # O primeiro valor é o que será salvo no banco de dados, o segundo é o que aparece no admin

class ProjectRole(models.TextChoices):
    MEMBER = 'member', 'Membro'
    LEADER = 'leader', 'Líder'

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    registration_date = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=10, choices=SystemRole.choices)
    USERNAME_FIELD = 'email'       
    REQUIRED_FIELDS = ['username'] 

    def __str__(self):
        return self.full_name

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    theme = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField()

    def __str__(self):
        return self.name

class UserProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_projects') 
    # O related_name é o nome que vai aparecer no admin, e o on_delete é o que acontece quando o usuário é deletado
    # Se não especificar o related_name, o Django vai criar um nome padrão, que é o nome do model em minúsculo + _set
    # Exemplo: userproject_set
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='user_projects')
    role = models.CharField(max_length=10, choices=ProjectRole.choices)

    def __str__(self):
        return f"{self.user} - {self.project} ({self.role})"

class Phase(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

class ProjectPhase(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE)
    order = models.IntegerField()

    class Meta:
        constraints = [
        models.UniqueConstraint(fields=['project', 'phase'], name='unique_project_phase')
    ] # UniqueConstraint é melhor que unique_together, pois é mais flexível e pode ser alterado depois

    def __str__(self):
        return f"{self.project} - {self.phase} (Ordem {self.order})"

class Task(models.Model):
    project_phase = models.ForeignKey(ProjectPhase, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_completed = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField()

    def __str__(self):
        return self.title

class TaskAssignee(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user_project = models.ForeignKey(UserProject, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.task} - {self.user_project.user} ({self.user_project.role})"
# O __str__ é o que vai aparecer no admin quando você clicar no objeto

class ChatMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    sender = models.ForeignKey(UserProject, on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
