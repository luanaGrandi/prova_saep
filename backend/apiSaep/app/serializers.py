from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from .models import Produto, MovimentacaoEstoque

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['id', 'nome', 'descricao', 'quantidade_estoque', 'estoque_min', 'preco']
        read_only_fields = ['id']

    def validate_nome(self, value):
        if not value.strip():
            raise serializers.ValidationError("O nome do produto não pode ser vazio.")
        return value


class MovimentacaoSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = MovimentacaoEstoque
        fields = ['id', 'produto', 'usuario', 'tipo', 'quantidade', 'data_movimentacao']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except AuthenticationFailed:
            raise AuthenticationFailed(detail={'detail': 'Credenciais inválidas.'})
