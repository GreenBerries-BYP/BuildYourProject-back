from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# Usei jsonfield pra lidar com o campo template que tem itens aninhados, então não dava pra usar text 
class SystemRole(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    USER = 'user', 'User'

class ProjectRole(models.TextChoices):
    MEMBER = 'member', 'Member'
    LEADER = 'leader', 'Leader'

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField(max_length=128)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=SystemRole.choices)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    registration_date = models.DateTimeField(auto_now_add=True)  # <-- campo criado

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.full_name

# alterado para alinhar com o front
class Project(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    type = models.TextField(default='default_type')
    start_date = models.DateTimeField() # removi a definição automática pelo sistema
    end_date = models.DateTimeField()
    phases = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

class UserProject(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_participations')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='user_relations')
    role = models.CharField(max_length=10, choices=ProjectRole.choices)

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f"{self.user.full_name} - {self.project.name} ({self.role})"

class Phase(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    parent_phase = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class ProjectPhase(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='phases_relations')
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.project.name} - {self.phase.name}"

class Task(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(db_index=True)
    project_phase = models.ForeignKey(ProjectPhase, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title

class TaskAssignee(models.Model):
    id = models.BigAutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignees')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')

    def __str__(self):
        return f"{self.task.title} - {self.user.full_name}"

class Chat(models.Model):
    id = models.BigAutoField(primary_key=True)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.full_name}: {self.content[:30]}..."