// Los datos y funciones de refresco deben estar disponibles para ambos archivos JS
// Aunque no se usan aquí, se mantienen para consistencia si se compartiera lógica.
const refrescoData = {
    '1': 1.50, // Coca-Cola
    '2': 1.75, // Pepsi
    '3': 1.25, // Sprite
    '4': 1.60, // Fanta
    '5': 1.00, // 7Up
    '6': 0.75  // Manaos
};

document.addEventListener('DOMContentLoaded', function() {
    // ---------------------------------
    // 1. LÓGICA DE MODO CLARO/OSCURO
    // ---------------------------------
    const themeToggle = document.getElementById('theme-toggle');
    
    // Obtiene el tema almacenado o usa el del sistema por defecto
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme) {
        document.body.classList.toggle('dark-mode', storedTheme === 'dark');
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.body.classList.add('dark-mode');
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            const isDarkMode = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        });
    }

    // ---------------------------------
    // 2. LÓGICA DEL MODAL DE PAGO (CORREGIDA)
    // ---------------------------------
    // Se mueven todas las referencias a elementos dentro del DOMContentLoaded
    const modal = document.getElementById('modal-pago');
    const btnPagar = document.getElementById('btn-iniciar-pago');
    const btnCerrar = modal ? modal.querySelector('.btn-cerrar-modal') : null;
    const paymentForm = document.getElementById('payment-form');
    const formPago = document.getElementById('form-pago');
    const btnSubmitPago = document.getElementById('btn-submit-pago');
    const successMessage = document.getElementById('success-message'); // Mantenemos esta referencia si se quiere usar en el modal
    const errorMessage = document.getElementById('error-message');
    
    // NUEVA REFERENCIA: Diálogo flotante verde
    const floatingSuccessDialog = document.getElementById('floating-success-dialog');


    // 2.1 Abrir Modal
    if (btnPagar && modal) {
        btnPagar.addEventListener('click', () => {
            modal.style.display = 'block';

            // Resetear mensajes y formulario al abrir
            if (successMessage) successMessage.style.display = 'none';
            if (errorMessage) errorMessage.style.display = 'none';
            if (paymentForm) paymentForm.style.display = 'block';
            if (btnSubmitPago) btnSubmitPago.disabled = false;
        });
    }

    // 2.2 Cerrar Modal
    if (btnCerrar && modal) {
        btnCerrar.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

    // Cerrar al hacer click fuera del modal
    if (modal) {
        window.addEventListener('click', (event) => {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        });
    }

    // 2.3 Procesar Pago Asíncrono
    if (formPago && btnSubmitPago && paymentForm && errorMessage) {
        formPago.addEventListener('submit', function(event) {
            event.preventDefault();

            // Deshabilitar botón y cambiar texto para feedback
            btnSubmitPago.disabled = true;
            btnSubmitPago.textContent = 'Procesando...';
            
            // Ocultar mensajes de error/éxito anteriores
            errorMessage.style.display = 'none';
            
            // Simulación de validación simple (podría ser más robusta)
            const cardNumber = document.getElementById('card-number').value;
            if (cardNumber.length < 16) {
                // Validación fallida
                btnSubmitPago.disabled = false;
                errorMessage.textContent = '❌ Número de tarjeta incompleto. Intente de nuevo.';
                errorMessage.style.display = 'block';
                // Usamos el total del DOM para restaurar el texto
                const totalText = document.querySelector('.carrito-total span').textContent;
                btnSubmitPago.textContent = `Pagar ${totalText}`;
                return;
            }


            // CORRECCIÓN: Usar la ruta '/api/checkout' que es la que existe en app.py
            fetch('/api/checkout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({}) // Enviamos un JSON vacío para evitar error 400 por malformación
            })
            .then(response => {
                // Verificar si la respuesta fue un 4xx o 5xx
                if (!response.ok) {
                    throw new Error('Respuesta del servidor no fue OK');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // 1. Cierra el modal inmediatamente
                    if (modal) modal.style.display = 'none'; 
                    
                    // 2. MUESTRA EL DIÁLOGO FLOTANTE VERDE
                    if (floatingSuccessDialog) {
                        floatingSuccessDialog.classList.add('show');
                    }
                    
                    // 3. Redirige al inicio después de 2.5 segundos
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 2500);
                } else {
                    // Si la API devuelve success: false (ej: carrito vacío)
                    throw new Error(data.message || 'Error desconocido');
                }
            })
            .catch(error => {
                // Muestra mensaje de error en caso de fallo del fetch o de la API
                console.error('Error en el pago:', error);
                
                // Muestra el mensaje de error para el usuario DENTRO DEL MODAL
                errorMessage.textContent = `❌ ${error.message || 'Error de conexión.'}`;
                errorMessage.style.display = 'block';
                
                btnSubmitPago.disabled = false; // Reactiva el botón
                // Restaura el texto del botón al total original
                const totalText = document.querySelector('.carrito-total span').textContent;
                btnSubmitPago.textContent = `Pagar ${totalText}`;
            });
        });
    } else {
        // En caso de que falte algún elemento crucial (solo para debug)
        // console.warn("Uno o más elementos del formulario de pago no se encontraron.");
    }
});