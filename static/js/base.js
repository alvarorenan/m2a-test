// =========================
// BASE JAVASCRIPT
// =========================

document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(function(alert) {
            new bootstrap.Alert(alert).close();
        });
    }, 5000);
    
    // Aplicar máscara de telefone
    aplicarMascaraTelefone();
    
    // Hot reload para desenvolvimento
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        setupHotReload();
    }
    
    // Setup de tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Setup de popovers do Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Função para aplicar máscara de telefone
function aplicarMascaraTelefone() {
    const phoneInputs = document.querySelectorAll('input[name*="telefone"], input[id*="telefone"], input[type="tel"]');
    console.log('🔍 Campos de telefone encontrados:', phoneInputs.length);
    
    phoneInputs.forEach(function(input, index) {
        console.log(`📱 Aplicando máscara no campo ${index + 1}:`, input);
        
        // Remove máscara anterior se existir
        if (input.inputmask) {
            input.inputmask.remove();
        }
        
        // Restringir apenas números e caracteres da máscara
        input.addEventListener('input', function(e) {
            // Remove tudo que não for número
            let valor = e.target.value.replace(/\D/g, '');
            
            // Aplicar formatação manual
            if (valor.length > 0) {
                if (valor.length <= 2) {
                    valor = `(${valor}`;
                } else if (valor.length <= 7) {
                    valor = `(${valor.slice(0, 2)}) ${valor.slice(2)}`;
                } else {
                    valor = `(${valor.slice(0, 2)}) ${valor.slice(2, 7)}-${valor.slice(7, 11)}`;
                }
            }
            
            e.target.value = valor;
        });
        
        // Também bloquear caracteres não-numéricos no keypress
        input.addEventListener('keypress', function(e) {
            // Permitir apenas números, backspace, delete, tab
            const allowedKeys = ['Backspace', 'Delete', 'Tab', 'ArrowLeft', 'ArrowRight'];
            if (allowedKeys.includes(e.key)) return;
            
            if (!/[0-9]/.test(e.key)) {
                e.preventDefault();
            }
        });
        
        // Aplicar InputMask como fallback se disponível
        if (typeof Inputmask !== 'undefined') {
            const inputMask = new Inputmask({
                mask: '(99) 99999-9999',
                placeholder: '(11) 99999-9999',
                showMaskOnHover: false,
                showMaskOnFocus: true,
                clearMaskOnLostFocus: false,
                removeMaskOnSubmit: false
            });
            inputMask.mask(input);
        }
    });
}

// Setup de hot reload
function setupHotReload() {
    // Ctrl+S para reload manual
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            console.log('🔥 Ctrl+S detectado! Recarregando...');
            location.reload();
        }
    });
    
    console.log('🔥 Hot Reload ativo! Ctrl+S para reload manual');
}

// Utility functions
window.Utils = {
    // Formatar moeda
    formatCurrency: function(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    },
    
    // Formatar data
    formatDate: function(date) {
        return new Intl.DateTimeFormat('pt-BR').format(new Date(date));
    },
    
    // Formatar data e hora
    formatDateTime: function(datetime) {
        return new Intl.DateTimeFormat('pt-BR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(datetime));
    },
    
    // Mostrar toast notification
    showToast: function(message, type = 'info') {
        // Implementação simples de toast
        const toastContainer = document.getElementById('toast-container') || createToastContainer();
        const toast = createToast(message, type);
        toastContainer.appendChild(toast);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
};

// Criar container de toasts se não existir
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
    document.body.appendChild(container);
    return container;
}

// Criar toast individual
function createToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show`;
    toast.style.cssText = 'min-width: 250px; margin-bottom: 10px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    return toast;
}