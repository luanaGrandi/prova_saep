from django.db import models
from django.contrib.auth.models import User

class Produto(models.Model):
    nome = models.CharField(max_length=200, unique=True, blank=False)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_estoque = models.IntegerField(default=0)
    estoque_min = models.IntegerField(default=0)

    def __str__(self):
        return self.nome

    # Método para verificar se o estoque do produto é suficiente
    def estoque_suficiente(self, quantidade):
        return self.quantidade_estoque >= quantidade


class MovimentacaoEstoque(models.Model):
    TIPO_CHOICES = (
        ("entrada", "Entrada"),
        ("saida", "Saída"),
    )

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='movimentacoes')  # Alterado de id_produto para produto
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    quantidade = models.PositiveIntegerField()
    data_movimentacao = models.DateTimeField(auto_now_add=True)  # Alterado para DateTimeField

    def __str__(self):
        return f'{self.tipo} - {self.quantidade} de {self.produto.nome}'

   
