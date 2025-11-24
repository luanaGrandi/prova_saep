from rest_framework_simplejwt.serializers import TokenObtainPairSerializer  # <-- Corrigido aqui
from rest_framework import serializers
from .models import Produto, MovimentacaoEstoque
from rest_framework.exceptions import AuthenticationFailed

# Serializer para leitura do produto
class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['id', 'nome', 'descricao', 'quantidade_estoque', 'estoque_min']
        read_only_fields = ['id', 'quantidade_estoque']

    # Validações para o nome do produto
    def validate_nome(self, value):
        if not value.strip():  # remove espaços em branco
            raise serializers.ValidationError("O nome do produto não pode ser vazio.")
        return value

    # Valida o estoque mínimo (não pode ser negativo)
    def validate_estoque_min(self, value):
        if value < 0:
            raise serializers.ValidationError("O estoque mínimo não pode ser negativo.")
        return value

# Serializer para criação do produto
class ProdutoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['id', 'nome', 'descricao', 'quantidade_estoque', 'estoque_min', 'preco']
        read_only_fields = ['id', 'nome']  # Nome é único, não podemos alterar

    # Validações para o nome do produto
    def validate_nome(self, value):
        if not value.strip():  # remove espaços em branco
            raise serializers.ValidationError("O nome do produto não pode ser vazio.")
        return value

    # Validação da quantidade em estoque
    def validate_quantidade_estoque(self, value):
        if value < 0:
            raise serializers.ValidationError("A quantidade de estoque não pode ser negativa.")
        return value

    # Validação do preço do produto (deve ser maior que zero)
    def validate_preco(self, value):
        if value <= 0:
            raise serializers.ValidationError("O preço do produto deve ser maior que zero.")
        return value

# Serializer para movimentações de estoque (entrada/saída)
class MovimentacaoSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    produto = serializers.PrimaryKeyRelatedField(queryset=Produto.objects.all())
    
    # Campos adicionais para o alerta
    alerta_estoque = serializers.SerializerMethodField()
    mensagem_alerta = serializers.SerializerMethodField()

    class Meta:
        model = MovimentacaoEstoque
        fields = ['id', 'produto', 'usuario', 'tipo', 'quantidade', 'data_movimentacao', 'alerta_estoque', 'mensagem_alerta']

    def get_alerta_estoque(self, obj):
        # Verifica se o estoque do produto está abaixo do mínimo após a movimentação
        produto = obj.produto
        if produto.quantidade_estoque < produto.estoque_min:
            return True
        return False

    def get_mensagem_alerta(self, obj):
        # Gera a mensagem de alerta se o estoque estiver abaixo do mínimo
        produto = obj.produto
        if produto.quantidade_estoque < produto.estoque_min:
            return f"Alerta: estoque do produto '{produto.nome}' está abaixo do mínimo configurado."
        return None


# Custom JWT serializer para mensagens de erro claras
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Adicionar claims adicionais, como o nome de usuário
        token['username'] = user.username
        return token

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except AuthenticationFailed as e:
            # Mensagem de erro mais clara para falha na autenticação
            raise AuthenticationFailed(detail={'detail': 'Credenciais inválidas. Verifique usuário/senha.'})
        return data
