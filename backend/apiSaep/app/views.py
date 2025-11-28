from rest_framework import generics, status, filters, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction

from .models import Produto, MovimentacaoEstoque
from .serializers import (
    ProdutoSerializer,
    MovimentacaoSerializer,
    MyTokenObtainPairSerializer,
)





class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = (AllowAny,)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh = request.data.get("refresh")
            RefreshToken(refresh).blacklist()
            return Response({"detail": "Logout realizado com sucesso."})
        except:
            return Response({"detail": "Token inválido."}, status=400)


# ===============================
# 📦 CRUD de Produtos
# ===============================

class ProdutoListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Produto.objects.all().order_by("nome")
    serializer_class = ProdutoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'descricao']
    ordering = ['nome']


class ProdutoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

    def delete(self, request, *args, **kwargs):
        produto = self.get_object()
        if produto.movimentacoes.exists():
            return Response(
                {"detail": "Não é possível excluir produto com movimentações."},
                status=400
            )
        return super().delete(request, *args, **kwargs)


# ===============================
# 📊 CRUD Movimentação de Estoque
# ===============================

class MovimentacaoListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MovimentacaoSerializer
    queryset = MovimentacaoEstoque.objects.all().order_by('-data_movimentacao')

    def perform_create(self, serializer):
        produto = serializer.validated_data['produto']
        tipo = serializer.validated_data['tipo']
        qtd = serializer.validated_data['quantidade']

        with transaction.atomic():
            produto = Produto.objects.select_for_update().get(pk=produto.pk)

            # Validação estoque
            if tipo == 'saida' and qtd > produto.quantidade_estoque:
                raise serializers.ValidationError("Quantidade maior que o estoque disponível.")

            # Aplica movimentação
            if tipo == 'entrada':
                produto.quantidade_estoque += qtd
            else:
                produto.quantidade_estoque -= qtd

            produto.save()
            serializer.save(usuario=self.request.user)


class MovimentacaoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MovimentacaoSerializer
    queryset = MovimentacaoEstoque.objects.all()

    def perform_update(self, serializer):
        movimentacao_antiga = self.get_object()
        nova = serializer.validated_data
        produto = movimentacao_antiga.produto

        with transaction.atomic():
            produto = Produto.objects.select_for_update().get(pk=produto.pk)

            # Reverte efeito anterior no estoque
            if movimentacao_antiga.tipo == 'entrada':
                produto.quantidade_estoque -= movimentacao_antiga.quantidade
            else:
                produto.quantidade_estoque += movimentacao_antiga.quantidade

            # Valida nova saída
            if nova['tipo'] == 'saida' and nova['quantidade'] > produto.quantidade_estoque:
                raise serializers.ValidationError("Quantidade maior que o estoque disponível.")

            # Aplica nova movimentação
            if nova['tipo'] == 'entrada':
                produto.quantidade_estoque += nova['quantidade']
            else:
                produto.quantidade_estoque -= nova['quantidade']

            produto.save()
            serializer.save(usuario=self.request.user)

    def perform_destroy(self, instance):
        produto = instance.produto

        with transaction.atomic():
            produto = Produto.objects.select_for_update().get(pk=produto.pk)

            # Reverte estoque
            if instance.tipo == 'entrada':
                produto.quantidade_estoque -= instance.quantidade
            else:
                produto.quantidade_estoque += instance.quantidade

            produto.save()
            instance.delete()
