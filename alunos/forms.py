from django import forms
from .models import Aluno, Modalidade, Pagamento
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator
import re

cpf_validator = RegexValidator(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', 'Formato de CPF inválido.')

class CustomAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Injeta classes CSS e atributos no campo Usuário
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Digite seu usuário',
            'required': True,
            'class': 'form-control'  # Classe para estilizar o input
        })
        
        # Injeta classes CSS e atributos no campo Senha
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Digite sua senha',
            'required': True,
            'class': 'form-control' # Classe para estilizar o input
        })

class AlunoForm(forms.ModelForm):
    # Sobrescrevemos o campo 'modalidades' para torná-lo obrigatório (min_value=1)
    modalidades = forms.ModelMultipleChoiceField(
        queryset=Modalidade.objects.all(),
        widget=forms.CheckboxSelectMultiple, # Exibe como checkboxes
        required=True,
        label="Selecione as Modalidades (Obrigatório)",
    )

    class Meta:
        model = Aluno
        # Lista todos os campos que queremos usar no formulário customizado
        fields = [
            'foto', 'nome', 'data_nascimento', 'sexo',
            'cpf', 'rg', 'whatsapp',
            'rua', 'numero', 'bairro', 'cidade', 'estado',
            'modalidades', 'ativo',
        ]
        
        # Define o tipo de input para campos de data e aplica o formato brasileiro
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'rg': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control phone-mask', 'placeholder': '(XX) 9XXXX-XXXX', 'maxlength': '15'}), # CLASSE CRÍTICA
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

    def clean_whatsapp(self):
        whatsapp = self.cleaned_data.get('whatsapp')
        if whatsapp:
            whatsapp_limpo = ''.join(filter(str.isdigit, whatsapp))
          
            if len(whatsapp_limpo) not in [10, 11]:
                raise forms.ValidationError("Por favor, insira um WhatsApp válido com DDD (10 ou 11 dígitos).")
            return whatsapp_limpo
        return whatsapp
    
    def clean_cpf(self):
        # GARANTE que o campo está em cleaned_data (se for obrigatório no Model)
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Limpa o CPF para retornar apenas números
            return cpf.replace('.', '').replace('-', '')
        return cpf # Retorna None ou string vazia se não for preenchido

    # Método de Validação Customizada (Clean)
    def clean(self):
        cleaned_data = super().clean()
        
        # Validação: Campos devem ter apenas números (e opcionalmente traços/pontos)
        numeric_fields = ['cpf', 'rg', 'whatsapp']
        
        for field_name in numeric_fields:
            value = cleaned_data.get(field_name)
            
            # Adiciona verificação para None/vazio para não quebrar a validação
            if value is not None and value != '':
                # Remove pontos, traços e parênteses para verificar se sobrou apenas dígitos
                cleaned_value = re.sub(r'[.\-() ]', '', value)
                
                if not cleaned_value.isdigit():
                    # self.add_error adiciona o erro ao campo específico
                    self.add_error(field_name, "O campo deve conter apenas números.")
                
                # Salva o valor limpo (apenas dígitos) em cleaned_data
                cleaned_data[field_name] = cleaned_value
                
        # Validação cruzada (ex: data_nascimento deve ser anterior a data_matricula, etc.)
        # Exemplo:
        # data_nascimento = cleaned_data.get('data_nascimento')
        # data_matricula = cleaned_data.get('data_matricula')

        # if data_nascimento and data_matricula and data_nascimento > data_matricula:
        #     raise ValidationError("A data de nascimento não pode ser posterior à data de matrícula.")

        return cleaned_data
    
    
    
# Formulário para Cadastro/Edição de Pagamentos
class PagamentoForm(forms.ModelForm):
    # O aluno será selecionado via ForeignKey
    aluno = forms.ModelChoiceField(
        queryset=Aluno.objects.filter(ativo=True).order_by('nome'),
        label='Aluno',
        empty_label="Selecione o Aluno",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Adicionando widgets de calendário para datas
    data_pagamento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Data do Pagamento'
    )
    data_vencimento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Data de Vencimento'
    )
    
    class Meta:
        model = Pagamento
        fields = [
            'aluno', 'valor', 'data_pagamento', 'data_vencimento', 
            'metodo_pagamento', 'pago', 'observacao'
        ]
        widgets = {
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_pagamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'metodo_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

# Formulário para Cadastro e Edição de Pagamentos
# Este formulário é necessário para o cadastro_pagamento_view
class CadastroPagamentoForm(forms.ModelForm):
    
    # Lista de métodos de pagamento (ajuste conforme o seu modelo Pagamento, se necessário)
    METODOS = [
        ('cartao', 'Cartão de Crédito/Débito'),
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('transferencia', 'Transferência'),
    ]

    metodo_pagamento = forms.ChoiceField(
        label='Método de Pagamento',
        choices=METODOS
    )
    
    class Meta:
        model = Pagamento
        fields = ['aluno', 'valor', 'data_pagamento', 'data_vencimento', 'metodo_pagamento', 'pago', 'observacao']
        widgets = {
            'data_pagamento': forms.DateInput(attrs={'type': 'date'}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date'}),
            'observacao': forms.Textarea(attrs={'rows': 3}),
        }

    # Você pode adicionar lógica de limpeza se necessário aqui
    pass


# NOVO: Formulário de Filtro de Histórico de Pagamentos
class FiltroHistoricoForm(forms.Form):
    data_inicio = forms.DateField(
        label='Data de Início',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        required=False
    )
    data_fim = forms.DateField(
        label='Data de Fim',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')

        if data_inicio and data_fim and data_inicio > data_fim:
            raise forms.ValidationError(
                "A Data de Início não pode ser posterior à Data de Fim."
            )
        return cleaned_data