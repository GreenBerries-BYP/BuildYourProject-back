from django.db import models
from django.contrib.auth.models import AbstractUser

#Camada de models serve pra definir os dados que serão salvos na aplicação
#Os atributos de usuário que virarão tabela no banco de dados tem que ser descritos aqui
#Nesse caso, usuário vai herdar tudo de AbstractUser, que é um usuário padrão que o Django cria (login e senha)
class PapelSistema(models.TextChoices):
    ADMIN = 'admin', 'Admin'  
    USUARIO = 'usuario', 'Usuário'  #O primeiro valor é o que vai ser salvo no banco de dados, o segundo é o que vai aparecer para o django admin

class PapelProjeto(models.TextChoices):
    MEMBRO = 'membro', 'Membro'
    LIDER = 'lider', 'Líder'

class Usuario(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    nome_completo = models.CharField(max_length=255)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    papel = models.CharField(max_length=10, choices=PapelSistema.choices)

    def __str__(self):
        return self.nome_completo

class Projeto(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField()
    criador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='projetos_criados')
    tema = models.CharField(max_length=100)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_entrega = models.DateTimeField()

    def __str__(self):
        return self.nome

class UsuarioProjeto(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    papel = models.CharField(max_length=10, choices=PapelProjeto.choices)

    def __str__(self):
        return f"{self.usuario} - {self.projeto} ({self.papel})"

class Fase(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField()

    def __str__(self):
        return self.nome

class ProjetoFase(models.Model):
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE)
    ordem = models.IntegerField()

    class Meta:
        unique_together = ('projeto', 'fase')  

    def __str__(self):
        return f"{self.projeto} - {self.fase} (Ordem {self.ordem})"

class Tarefa(models.Model):
    projeto_fase = models.ForeignKey(ProjetoFase, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    concluida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_entrega = models.DateTimeField()

    def __str__(self):
        return self.titulo

class TarefaResponsavel(models.Model):
    tarefa = models.ForeignKey(Tarefa, on_delete=models.CASCADE)
    usuario_projeto = models.ForeignKey(UsuarioProjeto, on_delete=models.CASCADE)

class Chat(models.Model):
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    remetente = models.ForeignKey(UsuarioProjeto, on_delete=models.CASCADE)
    conteudo = models.TextField()
    data_mensagem = models.DateTimeField(auto_now_add=True)

class AnexoTarefa(models.Model):
    tarefa = models.ForeignKey(Tarefa, on_delete=models.CASCADE)
    arquivo = models.FileField(upload_to='anexos/')
    data_upload = models.DateTimeField(auto_now_add=True)

