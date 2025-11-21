from django.urls import path
from . import views

# Definimos o nome do app para referências futuras
app_name = 'alunos' 

urlpatterns = [
    # Dashboard (Página principal após o login)
    path('dashboard/', views.dashboard, name='dashboard'),
             
    # Acessa a view 'lista_alunos' quando o usuário visita a URL raiz do app ('/')
    path('lista', views.lista_alunos, name='lista_alunos'),

    # NOVA URL: Mapeia o nome 'cadastro_aluno' para a view que criamos
    path('cadastro/', views.cadastro_aluno, name='cadastro_aluno'),

    # NOVO: Página Principal de Gerenciamento de Alunos
    path('gerenciar/', views.aluno_manager, name='aluno_manager'),

    # URLs de Edição do Aluno
    path('editar/<int:pk>/', views.cadastro_aluno, name='editar_aluno'),

    # URLs de Exclusão (a ser implementada)
    path('excluir/<int:pk>/', views.excluir_aluno, name='excluir_aluno'),

    # ==========================================================
    # ROTAS PARA PAGAMENTOS
    # ==========================================================
    path('pagamentos/gerenciar/', views.pagamentos_manager_view, name='pagamentos_manager'),

    path('pagamentos/cadastro/', views.cadastro_pagamento_view, name='cadastro_pagamento'),

    path('pagamentos/editar/<int:pk>/', views.cadastro_pagamento_view, name='editar_pagamento'),
    
    # CORREÇÃO: Apontamos para a view correta: historico_pagamentos_view
    path('pagamentos/historico/', views.historico_pagamentos_view, name='historico_pagamentos'), 
    
    # Mantemos o vencimentos apontando para o manager por enquanto
    path('pagamentos/vencimentos/', views.vencimentos_pagamentos_view, name='vencimentos_pagamentos'),

    # NOVO: URL para Excluir Pagamentos
    path('pagamentos/excluir/<int:pk>/', views.excluir_pagamento_view, name='excluir_pagamento'),
]