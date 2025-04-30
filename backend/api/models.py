from django.db import models
from django.contrib.auth.models import AbstractUser

#Camada de models serve pra definir os dados que serão salvos na aplicação
#Os atributos de usuário que virarão tabela no banco de dados tem que ser descritos aqui
#Nesse caso, usuário vai herdar tudo de AbstractUser, que é um usuário padrão que o Django cria (login e senha)
class User(AbstractUser):
    """Model de usuário """
    
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('professor', 'Professor'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.role})"
