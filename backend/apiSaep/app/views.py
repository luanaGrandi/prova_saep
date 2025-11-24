from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Produto, MovimentacaoEstoque
from .serializers import ProdutoSerializer, ProdutoCreateSerializer, MovimentacaoSerializer, MyTokenObtainPairSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import transaction
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

# Login (JWT) com mensagens claras
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = (AllowAny,)

# Logout via blacklist do refresh token
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout realizado com sucesso."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": "Token inválido ou já expirado."}, status=status.HTTP_400_BAD_REQUEST)

# CRUD Produto - Listar e Criar
class ProdutoListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'descricao']
    ordering_fields = ['nome']
    ordering = ['nome']  # por padrão ordena por nome (alfabética)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProdutoCreateSerializer
        return ProdutoSerializer

    def get_queryset(self):
        return Produto.objects.all().order_by('nome')

# Validar se produto já existe no banco (serializador)
class ProdutoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = '__all__'

    def validate_nome(self, value):
        # Garantir que o nome não seja vazio
        if not value.strip():
            raise serializers.ValidationError("O nome do produto não pode ser vazio.")
        return value

    def create(self, validated_data):
        # Evitar duplicidade ao criar
        if Produto.objects.filter(nome=validated_data['nome']).exists():
            raise serializers.ValidationError({"detail": f"Produto com nome '{validated_data['nome']}' já existe."})
        return super().create(validated_data)

# View para detalhes, atualização e exclusão de produtos
class ProdutoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Produto.objects.all()
    serializer_class = ProdutoCreateSerializer  # permite atualizar quantidade se necessário

    def delete(self, request, *args, **kwargs):
        # Impedir exclusão de produto se houver movimentações registradas
        produto = self.get_object()
        if produto.movimentacoes.exists():
            return Response({"detail": "Não é possível excluir produto com movimentações registradas."},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().delete(request, *args, **kwargs)

# Listar movimentações e criar nova movimentação (entrada/saída)
class MovimentacaoListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = MovimentacaoEstoque.objects.select_related('produto', 'usuario').all().order_by('-data_movimentacao')
    serializer_class = MovimentacaoSerializer

    def perform_create(self, serializer):
        user = self.request.user
        produto = serializer.validated_data['produto']
        tipo = serializer.validated_data['tipo_movimentacao']
        quantidade = serializer.validated_data['quantidade']

        # Operações atômicas para garantir a consistência
        with transaction.atomic():
            produto = Produto.objects.select_for_update().get(pk=produto.pk)

            if tipo == 'saida':
                if quantidade > produto.quantidade_estoque:
                    raise serializers.ValidationError({"detail": "Quantidade de saída maior que o estoque disponível."})
                produto.quantidade_estoque -= quantidade
            else:  # tipo == 'entrada'
                produto.quantidade_estoque += quantidade

            produto.save()

            # Cria a movimentação com o usuário logado
            serializer.save(usuario=user)

    def create(self, request, *args, **kwargs):
        # Sobrescreve para capturar alertas de estoque mínimo e retornar mensagens claras
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_create(serializer)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)

        # Verificar estoque mínimo após a movimentação
        mov = serializer.instance
        produto = mov.produto

        alert = False
        alert_message = None
        if produto.quantidade_estoque < produto.estoque_min:
            alert = True
            alert_message = f"Alerta: estoque do produto '{produto.nome}' está abaixo do mínimo configurado."

        response_data = {
            "movimentacao": MovimentacaoSerializer(mov).data,
            "alerta_estoque": alert,
            "mensagem_alerta": alert_message
        }
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
