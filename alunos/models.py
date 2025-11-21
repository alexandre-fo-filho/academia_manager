# alunos/models.py

from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator 
from django.conf import settings
from datetime import date

# Validação para garantir que o nome contenha apenas letras e espaços
ALPHABETIC_VALIDATOR = RegexValidator(
    r'^[a-zA-ZáàâãéèêíìîóòôõúùûçÇÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛ\s]*$', 
    'Apenas letras são permitidas neste campo.'
)

# Opções de Sexo
SEXO_CHOICES = (
    ('M', 'Masculino'),
    ('F', 'Feminino'),
    ('O', 'Outro'),
)

# Opções de Modalidade
MODALIDADE_CHOICES = (
    ('MT', 'Muay Thai'),
    ('JJ', 'Jiu Jitsu'),
    ('MUSC', 'Musculação'),
    ('DANCA', 'Dança'),
)

def calcular_idade(data_nascimento):
    """Calcula a idade com base na data de nascimento."""
    today = date.today()
    return today.year - data_nascimento.year - ((today.month, today.day) < (data_nascimento.month, data_nascimento.day))

class Aluno(models.Model):
    # DADOS PESSOAIS
    # Nome: Obrigatório, apenas letras (usando o validador definido)
    nome = models.CharField(
        max_length=150, 
        validators=[ALPHABETIC_VALIDATOR],
        verbose_name="Nome Completo"
    )
    # RG: Apenas números será feito por um widget no formulário
    rg = models.CharField(max_length=12, unique=True)
    # CPF: Obrigatório, apenas números
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    # Sexo: Obrigatório, usando as opções definidas
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default='O')
    # Data de Nascimento: Obrigatório (null=False por padrão)
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    
    # CONTATO
    # WhatsApp: Obrigatório. Usaremos um campo CharField e o tipo de input no formulário
    whatsapp = models.CharField(max_length=15,  blank=True, null=True, verbose_name="Telefone/WhatsApp")
    # Email: Opcional, Django valida se é um e-mail válido se for preenchido
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)

    # ENDEREÇO (Todos obrigatórios)
    rua = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=50, blank=True, null=True)
    # Cidade e Estado: Pré-preenchido e obrigatório
    cidade = models.CharField(max_length=50, default='Jacobina')
    estado = models.CharField(max_length=2, default='BA')

    # FOTO (Novo campo)
    foto = models.ImageField(
        upload_to='alunos_fotos/', # Pasta onde as fotos serão salvas dentro da pasta MEDIA_ROOT
        null=True,                 # Permite que o campo seja nulo no banco de dados
        blank=True                 # Permite que o campo seja opcional no formulário
    )

    # MATRÍCULA
    # Modalidade: Obrigatório, aceita múltiplas opções (ManyToMany)
    # NOTA: Para ter pelo menos 1, faremos uma validação no formulário (próximo passo)
    modalidades = models.ManyToManyField('Modalidade') # Usaremos um modelo separado para Multi-Seleção
    data_matricula = models.DateField(default=timezone.now, verbose_name="Data de Cadastro")
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ['nome']

    @property
    def idade(self):
        """Propriedade para obter a idade do aluno."""
        return calcular_idade(self.data_nascimento)

    @property
    def status_display(self):
        """Retorna o status como texto para exibição."""
        return "Ativo" if self.ativo else "Inativo"
    
    def _limpar_whatsapp(self):
        whatsapp = self.whatsapp
        if whatsapp:
            whatsapp_limpo = ''.join(filter(str.isdigit, whatsapp))
            self.whatsapp = whatsapp_limpo

            # CRUCIAL: Normalizar para o padrão do WhatsApp (55 + DDD + Número)
            if whatsapp_limpo.startswith('55'):
                # Já tem DDI
                self.whatsapp = whatsapp_limpo
            elif len(whatsapp_limpo) >= 10 or len(whatsapp_limpo) == 11: 
                # Se tem 10 (DDD + 8 ou 9 dígitos) ou 11 (DDD + 9 dígitos)
                self.whatsapp = '55' + whatsapp_limpo
            else:
                # Se não for um número válido, salva limpo, mas sem DDI
                self.whatsapp = whatsapp_limpo

        else:
            self.whatsapp = None
    
    @property
    def whatsapp_formatado(self):
        """Formata o número (só dígitos) para exibição bonita."""
        numero_puro = self.whatsapp
        if not numero_puro:
            return "Não informado"
            
        # Tenta remover o DDI '55' se estiver presente, para formatar
        n = numero_puro
        if n.startswith('55'):
            n = n[2:]

        tamanho = len(n)

        if tamanho == 11: # Ex: 74991234567 (DDD + 9 dígitos)
            return f"({n[0:2]}) {n[2:3]} {n[3:7]}-{n[7:]}" 
        elif tamanho == 10: # Ex: 7491234567 (DDD + 8 dígitos)
            return f"({n[0:2]}) {n[2:6]}-{n[6:]}"
        elif tamanho == 9: # Ex: 991234567 (9 dígitos sem DDD)
            return f"{n[0]} {n[1:5]}-{n[5:]}"
        
        return "Inválido/Curto" # Retorna o número puro se a formatação falhar

    # Propriedade para criar o link direto para o WhatsApp
    # @property
    # def link_whatsapp(self):
    #    numero_puro = self.whatsapp
    #    if numero_puro and len(numero_puro) >= 12 and numero_puro.startswith('55'):
    #        return f"https://wa.me/{numero_puro}" 
    #    return None
      
    def save(self, *args, **kwargs):
        """Sobrescreve o save para garantir que o whatsapp seja limpo antes de ir para o banco."""
        self._limpar_whatsapp()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        """Define a URL padrão (dashboard) após salvar/editar."""
        from django.urls import reverse
        return reverse('alunos:dashboard')

# Modelo separado para Modalidades
class Modalidade(models.Model):
    # Remova 'choices=MODALIDADE_CHOICES' daqui. 
    # Usaremos apenas um CharField para o nome.
    nome = models.CharField(max_length=50, unique=True) 
    
    def __str__(self):
        # A representação será apenas o nome
        return self.nome 
        # NOTA: O 'get_nome_display()' da versão anterior não funcionará mais aqui,
        # mas não será necessário, pois preencheremos o nome completo.

# Define as opções para o método de pagamento
METODO_PAGAMENTO_CHOICES = [
    ('PIX', 'PIX'),
    ('CARTAO', 'Cartão de Crédito/Débito'),
    ('DINHEIRO', 'Dinheiro'),
    ('TRANSFERENCIA', 'Transferência Bancária'),
]

# Define as opções para o status do aluno (se necessário)
STATUS_ALUNO_CHOICES = [
    ('ATIVO', 'Ativo'),
    ('INATIVO', 'Inativo'),
    ('SUSPENSO', 'Suspenso'),
]

class Pagamento(models.Model):
    # Relacionamento: Um pagamento pertence a um Aluno
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='pagamentos')
    
    # Detalhes do Pagamento
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = models.DateField(default=date.today)
    data_vencimento = models.DateField()
    metodo_pagamento = models.CharField(max_length=20, choices=METODO_PAGAMENTO_CHOICES)
    
    # Status (Ex: Pago, Estornado, Pendente)
    pago = models.BooleanField(default=False)
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pagamento de R${self.valor} para {self.aluno.nome}"

    @property
    def status_vencimento(self):
        """Verifica se o pagamento está vencido ou próximo do vencimento."""
        hoje = date.today()
        if self.pago:
            return 'PAGO'
        elif self.data_vencimento < hoje:
            return 'VENCIDO'
        elif (self.data_vencimento - hoje).days <= 5: # Vence em 5 dias ou menos
            return 'VENCE EM BREVE'
        else:
            return 'Pendente'

    class Meta:
        ordering = ['-data_vencimento']
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"

    @property
    def esta_vencido(self):
        # A fatura está vencida se a data de vencimento for anterior a hoje.
        # Não importa se está paga ou não, apenas se a data limite passou.
        return self.data_vencimento < date.today()
    
    @property
    def dias_vencido(self):
        """Calcula a diferença em dias se estiver vencido."""
        if self.esta_vencido:
            # timedelta resulta na diferença de dias
            return (date.today() - self.data_vencimento).days
        return 0 # Se não estiver vencido, retorna 0

    def __str__(self):
        return f"Pagamento de R${self.valor} por {self.aluno.nome}"