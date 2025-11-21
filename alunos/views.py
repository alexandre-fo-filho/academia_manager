from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from django.utils import timezone
from .forms import AlunoForm, PagamentoForm, CadastroPagamentoForm, FiltroHistoricoForm
from .models import Aluno, Pagamento
import logging

logger = logging.getLogger(__name__)

# ==========================================================
# 1. VIEWS DE NAVEGAÇÃO
# ==========================================================
@login_required # Garante que só usuários logados acessem a dashboard
def dashboard(request):
    """Página principal de boas-vindas e navegação."""
    context = {
        'titulo': 'Bem-vindo(a) à Academia Manager',
        'usuario': request.user.username, # Obtém o nome do usuário logado
    }
    return render(request, 'alunos/dashboard.html', context)

# ==========================================================
# 2. VIEW DE CADASTRO / EDIÇÃO DE ALUNO (Corrigida)
# ==========================================================
@login_required
def aluno_manager(request):
    return render(request, 'alunos/aluno_manager.html', {'titulo': 'Gerenciar Alunos'})

@login_required
def lista_alunos(request):
    alunos = Aluno.objects.filter(ativo=True).order_by('nome')
    
    search_query = request.GET.get('q', '')
    if search_query:
        # Busca por nome ou CPF
        alunos = alunos.filter(
            Q(nome__icontains=search_query) |
            Q(cpf__icontains=search_query)
        )

    context = {
        'alunos': alunos,
        'search_query': search_query,
        'active_page': 'alunos',
        'titulo': 'Lista de Alunos'
    }

    return render(request, 'alunos/lista_alunos.html', context)

@login_required
def cadastro_aluno(request, pk=None):
    aluno = None
    titulo = 'Cadastrar Novo Aluno'
    if pk:
        aluno = get_object_or_404(Aluno, pk=pk)
        titulo = f"Editar Aluno: {aluno.nome}"

    if request.method == 'POST':
        form = AlunoForm(request.POST, request.FILES, instance=aluno)
        
        if form.is_valid():
            try:
                aluno_salvo = form.save()
                
                if pk:
                    messages.success(request, f"Aluno {aluno_salvo.nome} atualizado com sucesso!")
                else:
                    messages.success(request, f"Aluno {aluno_salvo.nome} matriculado com sucesso!")
                    
                return redirect('alunos:aluno_manager')
           
            except IntegrityError:
                # Tratamento de erro de banco (ex: CPF/RG duplicado)
                messages.error(request, "Erro: O CPF ou RG fornecido já está cadastrado no sistema.")
            except Exception as e:
                # Tratamento de erro genérico
                logger.error(f"Erro inesperado ao salvar aluno: {e}")
                messages.error(request, "Ocorreu um erro inesperado ao salvar o aluno.")

        else:
            # DEBUG CRÍTICO: Registra no console o que está falhando na validação
            logger.error(f"Formulário de Aluno Inválido. Erros: {form.errors}")
            
            # Mensagem de erro que aponta para os campos
            messages.error(request, "Erro no cadastro. Verifique os campos destacados em vermelho e preencha todos os obrigatórios.")

    else:
        # Se for um GET, cria um formulário vazio
        form = AlunoForm(instance=aluno)
        
    context = {
        'titulo': titulo,
        'form': form,
        'aluno': aluno
    }
    return render(request, 'alunos/cadastro_aluno.html', context)

def excluir_aluno(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)

    if request.method == 'POST':
        try:
            nome_aluno = aluno.nome # Salva o nome para a mensagem de feedback
            aluno.delete()
            
            # Adiciona uma mensagem de sucesso para exibir no dashboard
            messages.success(request, f'Aluno "{nome_aluno}" excluído com sucesso.')
            
            # Redireciona para a lista principal (dashboard)
            return redirect('alunos:dashboard')
        
        except Exception as e:
            # Em caso de erro (ex: problema de permissão)
            messages.error(request, f'Erro ao excluir o aluno: {e}')
            return redirect('alunos:dashboard')

    return render(request, 'alunos/confirmar_exclusao.html', {'aluno': aluno})

# ==========================================================
# 3. NOVAS VIEWS DE PAGAMENTOS
# ==========================================================

@login_required
def pagamentos_manager_view(request):
    """Página principal de gerenciamento de pagamentos (Menu de 4 botões)."""
    return render(request, 'alunos/pagamentos_manager.html', {'titulo': 'Gerenciar Pagamentos'})


@login_required
def cadastro_pagamento_view(request, pk=None):
    """
    View unificada para Cadastrar (pk=None) e Editar (pk=ID) um Pagamento.
    """
    pagamento = None
    titulo = 'Registrar Novo Pagamento'

    if pk:
        pagamento = get_object_or_404(Pagamento, pk=pk)
        titulo = f"Editar Pagamento de: {pagamento.aluno.nome}"

    if request.method == 'POST':
        form = PagamentoForm(request.POST, instance=pagamento)

        if form.is_valid():
            pagamento_salvo = form.save()
            
            if pk:
                messages.success(request, f"Pagamento de {pagamento_salvo.aluno.nome} atualizado com sucesso!")
            else:
                messages.success(request, f"Pagamento de {pagamento_salvo.aluno.nome} registrado com sucesso!")
            
            # TODO: Redirecionar para uma lista de pagamentos futuros
            return redirect('alunos:pagamentos_manager')
        else:
            messages.error(request, "Erro no registro. Verifique os campos.")
    else:
        # Se for um GET
        form = PagamentoForm(instance=pagamento)

    context = {
        'titulo': titulo,
        'form': form,
        'pagamento': pagamento,
        # Usaremos este booleano no template para mudar o título e botão
        'is_editing': pk is not None
    }
    return render(request, 'alunos/cadastro_pagamento.html', context)

@login_required
def historico_pagamentos_view(request):
    """
    Exibe o histórico de pagamentos e permite filtrar por período.
    """
    form = FiltroHistoricoForm(request.GET)
    pagamentos = Pagamento.objects.all().order_by('-data_pagamento', '-data_vencimento')
    data_inicio = None
    data_fim = None
    total_recebido = 0

    if form.is_valid():
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')

        if data_inicio:
            # Filtra pagamentos onde a data de pagamento é MAIOR ou IGUAL à data de início
            pagamentos = pagamentos.filter(data_pagamento__gte=data_inicio)
        
        if data_fim:
            # Filtra pagamentos onde a data de pagamento é MENOR ou IGUAL à data de fim
            pagamentos = pagamentos.filter(data_pagamento__lte=data_fim)
        
        # O cálculo do total deve ser feito APÓS o filtro
        total_recebido = pagamentos.aggregate(Sum('valor'))['valor__sum'] or 0

    context = {
        'titulo': 'Histórico de Pagamentos por Período',
        'form': form,
        'pagamentos': pagamentos,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'total_recebido': total_recebido,
    }
    return render(request, 'alunos/historico_pagamentos.html', context)

@login_required
def vencimentos_pagamentos_view(request):
    """
    Exibe a lista de todos os pagamentos vencidos (data_vencimento < hoje E pago=False).
    """
    hoje = date.today()
    
    # Filtra pagamentos onde:
    # 1. data_vencimento é menor que HOJE
    # 2. pago é False (ou seja, ainda não foi liquidado)
    pagamentos_vencidos = Pagamento.objects.filter(
        data_vencimento__lte=hoje, # '__lt' significa "less than" (menor que)
        pago=False
    ).select_related('aluno').order_by('data_vencimento') # Ordena pelo mais antigo

    # Calcula o total que está em aberto (soma dos valores dos pagamentos vencidos)
    total_aberto = pagamentos_vencidos.aggregate(Sum('valor'))['valor__sum'] or 0

    context = {
        'titulo': 'Pagamentos Vencidos',
        'pagamentos_vencidos': pagamentos_vencidos,
        'total_aberto': total_aberto,
        'hoje': hoje,
    }
    return render(request, 'alunos/vencimentos_pagamentos.html', context)

@login_required
def excluir_pagamento_view(request, pk):
    """
    Exclui um registro de Pagamento específico (PK).
    """
    # Tenta pegar o objeto Pagamento ou retorna erro 404
    pagamento = get_object_or_404(Pagamento, pk=pk)
    
    # A exclusão deve ser sempre feita via POST para segurança
    if request.method == 'POST':
        aluno_nome = pagamento.aluno.nome # Salva o nome antes de excluir
        
        pagamento.delete()
        
        messages.success(request, f'Pagamento do aluno {aluno_nome} excluído com sucesso.')
        
        # Redireciona de volta para o histórico de pagamentos
        return redirect('alunos:historico_pagamentos')
        
    # Se for GET, redireciona de volta com uma mensagem de erro (ou apenas redireciona)
    messages.error(request, 'Ação de exclusão inválida.')
    return redirect('alunos:historico_pagamentos')