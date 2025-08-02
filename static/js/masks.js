// =========================
// MASKS AND VALIDATION
// =========================

// Observer para campos adicionados dinamicamente
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.addedNodes.length > 0) {
            setTimeout(aplicarMascaraTelefone, 100);
        }
    });
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

// Máscara para campos de telefone específica
function setupPhoneMask(input) {
    if (!input) return;
    
    // Remove caracteres especiais
    input.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        
        // Limita a 11 dígitos
        if (value.length > 11) {
            value = value.slice(0, 11);
        }
        
        // Aplica formatação
        if (value.length > 0) {
            if (value.length <= 2) {
                value = `(${value}`;
            } else if (value.length <= 7) {
                value = `(${value.slice(0, 2)}) ${value.slice(2)}`;
            } else {
                value = `(${value.slice(0, 2)}) ${value.slice(2, 7)}-${value.slice(7)}`;
            }
        }
        
        e.target.value = value;
    });
    
    // Previne caracteres inválidos
    input.addEventListener('keypress', function(e) {
        const allowedKeys = ['Backspace', 'Delete', 'Tab', 'ArrowLeft', 'ArrowRight', 'Home', 'End'];
        
        if (allowedKeys.includes(e.key)) {
            return;
        }
        
        if (!/[0-9]/.test(e.key)) {
            e.preventDefault();
        }
    });
    
    // Placeholder dinâmico
    if (!input.placeholder) {
        input.placeholder = '(11) 99999-9999';
    }
}

// Validação de telefone
function validatePhone(phone) {
    const cleaned = phone.replace(/\D/g, '');
    return cleaned.length >= 10 && cleaned.length <= 11;
}

// Validação de email
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Aplicar validações em tempo real
function setupRealTimeValidation() {
    // Telefones
    document.querySelectorAll('input[type="tel"]').forEach(input => {
        input.addEventListener('blur', function() {
            const isValid = validatePhone(this.value);
            this.classList.toggle('is-invalid', !isValid && this.value.length > 0);
            this.classList.toggle('is-valid', isValid);
        });
    });
    
    // Emails
    document.querySelectorAll('input[type="email"]').forEach(input => {
        input.addEventListener('blur', function() {
            const isValid = validateEmail(this.value);
            this.classList.toggle('is-invalid', !isValid && this.value.length > 0);
            this.classList.toggle('is-valid', isValid);
        });
    });
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', setupRealTimeValidation);