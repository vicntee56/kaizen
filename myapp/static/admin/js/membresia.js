document.addEventListener('DOMContentLoaded', function() {
    // Función para sincronizar checkboxes
    function syncCheckboxes() {
        const pagado = document.getElementById('id_pagado');
        const noPagado = document.getElementById('id_no_pagado');
        
        if (pagado && noPagado) {
            // Sincronización inicial
            noPagado.checked = !pagado.checked;
            
            // Event listeners
            pagado.addEventListener('change', function() {
                noPagado.checked = !this.checked;
            });
            
            noPagado.addEventListener('change', function() {
                pagado.checked = !this.checked;
            });
        }
    }
    
    syncCheckboxes();
    
    // Para formsets dinámicos
    document.addEventListener('formset:added', function() {
        setTimeout(syncCheckboxes, 100);
    });
});