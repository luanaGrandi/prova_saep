# core/urls.py
from django.urls import path
from .views import (
    MyTokenObtainPairView, LogoutView,
    ProdutoListCreateView, ProdutoRetrieveUpdateDestroyView,
    MovimentacaoListCreateView,  MovimentacaoRetrieveUpdateDestroyView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Auth JWT
    path('auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),

    # Produtos
    path('produtos/', ProdutoListCreateView.as_view(), name='produtos_list_create'),
    path('produtos/<int:pk>/', ProdutoRetrieveUpdateDestroyView.as_view(), name='produto_detail'),

    # Movimentações
    path('movimentacoes/', MovimentacaoListCreateView.as_view()),
    path('movimentacoes/<int:pk>/', MovimentacaoRetrieveUpdateDestroyView.as_view()),
]
