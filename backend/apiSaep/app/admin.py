from django.contrib import admin
from .models import Produto, MovimentacaoEstoque

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade_estoque', 'estoque_min', 'preco')
    search_fields = ('nome',)

@admin.register(MovimentacaoEstoque)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'tipo', 'quantidade', 'usuario', 'data_movimentacao')
    list_filter = ('tipo', 'produto', 'usuario')
    ordering = ('-data_movimentacao',)
