from rest_framework import serializers
from .models import User

#Serializer pega os dados do model (Vindo do bdd) e cria um json para enviar pro front
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "role","name", "date_joined"]
        # Os extra kwargs são usados para configurar comportamentos específicos dentro dos campos
        # write only - Só é enviado no json, mas não será mostrado no retorno
        # read only - Só será exibido no retorno, não será enviado
        # required - Campo obrigatório no json
        # default - Terá um valor padrão se nada for enviado no json
        # allow blank - Pode ter um valor em branco
        # allow null - Pode ter um valor nulo
        
        extra_kwargs = {
            "password": {"write_only": True}, #Por segurança, não exibir no retorno da api (Já colocar no Viana)
            "date_joined": {"read_only": True},
        }

    def create(self, validated_data):
        role = validated_data.pop('role', None)
        name = validated_data.pop('name', None)
        user = User.objects.create_user(**validated_data)
        if role:
            user.role = role
        if name:
            user.name = name
        user.save()
        return user