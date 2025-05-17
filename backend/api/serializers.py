from rest_framework import serializers
from .models import (
    Usuario, Projeto, UsuarioProjeto, Fase, ProjetoFase,
    Tarefa, TarefaResponsavel, Chat, AnexoTarefa
)

# Serializer pega os dados do model (vindo do banco de dados) e cria um JSON para enviar pro front
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password', 'nome_completo', 'data_cadastro', 'papel']
        # Os extra kwargs são usados para configurar comportamentos específicos dentro dos campos
        # write only - Só é enviado no json, mas não será mostrado no retorno
        # read only - Só será exibido no retorno, não será enviado
        # required - Campo obrigatório no json
        # default - Terá um valor padrão se nada for enviado no json
        # allow blank - Pode ter um valor em branco
        # allow null - Pode ter um valor nulo
        
        extra_kwargs = {
            "password": {"write_only": True}, #Por segurança, não exibir no retorno da api (Já colocar no Viana)
            "data_cadastro": {"read_only": True},
        }

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)
    
    class ProjetoSerializer(serializers.ModelSerializer):
        class Meta:
            model = Projeto
            fields = ['id', 'nome', 'descricao', 'criador', 'tema', 'data_criacao', 'data_entrega']
            read_only_fields = ['data_criacao', 'criador'] #Não usei extra kwargs porque dá pra fazer direto
    
    class UsuarioProjetoSerializer(serializers.ModelSerializer):
        class Meta:
            model = UsuarioProjeto
            fields = ['id', 'usuario', 'projeto', 'papel']
    
    class FaseSerializer(serializers.ModelSerializer):
        class Meta:
            model = Fase
            fields = ['id', 'nome', 'descricao']
    
    class ProjetoFaseSerializer(serializers.ModelSerializer):
        class Meta:
            model = ProjetoFase
            fields = ['id', 'projeto', 'fase', 'ordem']

    class TarefaSerializer(serializers.ModelSerializer):
        class Meta:
            model = Tarefa
            fields = ['id', 'projeto_fase', 'titulo', 'descricao', 'concluida', 'data_criacao', 'data_entrega']
            read_only_fields = ['data_criacao']
    
    class TarefaResponsavelSerializer(serializers.ModelSerializer):
        class Meta:
            model = TarefaResponsavel
            fields = ['id', 'tarefa', 'usuario_projeto']

    class ChatSerializer(serializers.ModelSerializer):
        class Meta:
            model = Chat
            fields = ['id', 'projeto', 'remetente', 'conteudo', 'data_mensagem']
            read_only_fields = ['data_mensagem']

    class AnexoTarefaSerializer(serializers.ModelSerializer):
        class Meta:
            model = AnexoTarefa
            fields = ['id', 'tarefa', 'arquivo', 'data_upload']
            read_only_fields = ['data_upload']