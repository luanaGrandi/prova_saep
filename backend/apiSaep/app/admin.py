from django.contrib import admin

# Register your models here.
from .models import Produto, MovimentacaoEstoque

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade_estoque', 'estoque_min')
admin.site.register(MovimentacaoEstoque)