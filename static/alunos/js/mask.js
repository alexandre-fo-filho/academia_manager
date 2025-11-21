// Função que aplica a máscara de telefone (XX) XXXXX-XXXX
function maskPhone(value) {
    if (!value) return ""
    // Remove tudo que não for dígito
    value = value.replace(/\D/g,'');
    
    // Se o valor tiver mais de 10 dígitos (o que implica um 9º dígito móvel), ajusta
    if (value.length > 10) {
        // (XX) 9XXXX-XXXX
        value = value.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3');
    } else {
        // (XX) XXXX-XXXX (Para telefones fixos ou se o 9º dígito ainda não foi digitado)
        value = value.replace(/^(\d{2})(\d{4})(\d{4})$/, '($1) $2-$3');
    }
    
    return value;
}

// Aplica a máscara a todos os campos com a classe 'phone-mask'
document.addEventListener('DOMContentLoaded', function() {
    const phoneInputs = document.querySelectorAll('.phone-mask');
    phoneInputs.forEach(input => {
        
        // Aplica a máscara ao carregar (para valores pré-existentes, ex: na edição)
        // O valor do input no HTML pode estar limpo (só dígitos), então aplica a máscara visual
        if (input.value) {
             input.value = maskPhone(input.value);
        }
        
        // Aplica a máscara ao digitar
        input.addEventListener('input', function(e) {
            e.target.value = maskPhone(e.target.value);
        });
    });
});