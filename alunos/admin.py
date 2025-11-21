# alunos/admin.py

from django.contrib import admin
from .models import Aluno, Modalidade # Garanta que Aluno e Modalidade estão importados

# 1. Atualiza a classe de customização para o Admin
class AlunoAdmin(admin.ModelAdmin):
    # Campos que serão exibidos na lista de alunos (AGORA COM 'whatsapp' E NOVOS CAMPOS)
    list_display = (
        'nome', 
        'cpf', 
        'whatsapp', # <-- CORREÇÃO: Substituímos 'telefone' por 'whatsapp'
        'cidade',
        'data_matricula', 
        'ativo'
    )
    
    # Adiciona um filtro lateral
    list_filter = ('ativo', 'data_matricula', 'sexo') # Adicionando 'sexo' ao filtro
    
    # Adiciona uma caixa de busca
    search_fields = ('nome', 'cpf', 'whatsapp') # Adicionando 'whatsapp' à busca
    
    # Define a ordem padrão
    ordering = ('-data_matricula',)

# 2. Registra os modelos
admin.site.register(Aluno, AlunoAdmin)
admin.site.register(Modalidade)