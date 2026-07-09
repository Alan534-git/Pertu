// Datos de los refrescos para el script
const refrescoData = {
    '1': 1.50, // Coca-Cola
    '2': 1.75, // Pepsi
    '3': 1.25, // Sprite
    '4': 1.60, // Fanta
    '5': 1.00, // 7Up
    '6': 0.75  // Manaos (nuevo)
};

// --- NUEVA RESTRICCIÓN DE CANTIDAD ---
const MAX_QUANTITY = 20;
// -----------------------------------

function generateItemKey() {
    if (window.crypto && typeof window.crypto.randomUUID === 'function') {
        return window.crypto.randomUUID();
    }

    if (window.crypto && typeof window.crypto.getRandomValues === 'function') {
        const bytes = new Uint8Array(16);
        window.crypto.getRandomValues(bytes);

        bytes[6] = (bytes[6] & 0x0f) | 0x40;
        bytes[8] = (bytes[8] & 0x3f) | 0x80;

        return Array.from(bytes, byte => byte.toString(16).padStart(2, '0')).join('');
    }

    return `item-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

/**
 * CAMBIO: Función para calcular el precio total.
 * Ahora usa la cantidad de milanesas y la cantidad de refrescos por separado.
 */
function updateTotalPrice(card) {
    const basePrice = parseFloat(card.querySelector('.precio-base span').dataset.basePrice);
    const selectedRefrescoBtn = card.querySelector('.btn-refresco.selected');
    const refrescoPrice = parseFloat(selectedRefrescoBtn.dataset.price);
    
    // Leer las dos cantidades
    const cantMilanesaInput = card.querySelector('.input-cantidad-milanesa');
    const cantRefrescoInput = card.querySelector('.input-cantidad-refresco');

    let cantMilanesa = parseInt(cantMilanesaInput.value);
    let cantRefresco = parseInt(cantRefrescoInput.value);

    // Validar y limitar la cantidad de milanesas
    if (isNaN(cantMilanesa) || cantMilanesa < 1) {
        cantMilanesa = 1;
        cantMilanesaInput.value = 1;
    } else if (cantMilanesa > MAX_QUANTITY) {
        cantMilanesa = MAX_QUANTITY;
        cantMilanesaInput.value = MAX_QUANTITY;
        showFloatingMessage(`Milanesas limitadas a ${MAX_QUANTITY} por ítem.`, 'warning');
    }

    // Validar y limitar la cantidad de refrescos
    if (isNaN(cantRefresco) || cantRefresco < 0) {
        cantRefresco = 0;
        cantRefrescoInput.value = 0;
    } else if (cantRefresco > MAX_QUANTITY) {
        cantRefresco = MAX_QUANTITY;
        cantRefrescoInput.value = MAX_QUANTITY;
        showFloatingMessage(`Refrescos limitados a ${MAX_QUANTITY} por ítem.`, 'warning');
    }

    // Si el refresco seleccionado es "Sin Refresco" (id 0), la cantidad de refresco debe ser 0
    const refrescoId = parseInt(selectedRefrescoBtn.dataset.refrescoId);
    if (refrescoId === 0) {
        cantRefresco = 0;
        cantRefrescoInput.value = 0;
    }

    // Calcular el subtotal
    const milanesaTotal = basePrice * cantMilanesa;
    const refrescoTotal = refrescoPrice * cantRefresco;
    const total = milanesaTotal + refrescoTotal;

    // Actualizar el botón de "Agregar al Carrito"
    const btnAgregar = card.querySelector('.btn-agregar');
    if (btnAgregar) {
        // Buscamos el span del precio, si existe
        const priceSpan = btnAgregar.querySelector('.total-price');
        if (priceSpan) {
            priceSpan.textContent = total.toFixed(2);
        }
        btnAgregar.dataset.cantidadMilanesa = cantMilanesa;
        btnAgregar.dataset.cantidadRefresco = cantRefresco;
    }
}

/**
 * Muestra un mensaje flotante de éxito/error/advertencia.
 */
function showFloatingMessage(message, type = 'success') {
    const dialog = document.getElementById('floating-message-dialog');
    if (!dialog) return;

    dialog.textContent = message;
    // Limpia clases anteriores
    dialog.classList.remove('show', 'success', 'error', 'warning');
    dialog.classList.add(type);

    // Muestra el diálogo
    requestAnimationFrame(() => {
        dialog.classList.add('show');
    });

    // Oculta el diálogo después de 3 segundos
    setTimeout(() => {
        dialog.classList.remove('show');
    }, 3000);
}

/**
 * Maneja la selección del tipo de refresco.
 */
function handleRefrescoSelection(card, selectedBtn) {
    // 1. Deseleccionar el botón anterior
    card.querySelectorAll('.btn-refresco').forEach(btn => {
        btn.classList.remove('selected');
    });

    // 2. Seleccionar el nuevo botón
    selectedBtn.classList.add('selected');

    // 3. Obtener los elementos de cantidad de refresco
    const inputRefresco = card.querySelector('.input-cantidad-refresco');
    const controlRefresco = card.querySelector('.cantidad-control-refresco');
    const refrescoId = parseInt(selectedBtn.dataset.refrescoId);

    // 4. Actualizar estado de cantidad de refresco
    if (refrescoId === 0) {
        // Si es "Sin Refresco" (ID 0), la cantidad debe ser 0 y se deshabilita el control
        inputRefresco.value = 0;
        controlRefresco.classList.add('disabled');
        inputRefresco.disabled = true;
    } else {
        // Si es un refresco real, habilitar y asegurar que la cantidad sea al menos 1
        inputRefresco.disabled = false;
        controlRefresco.classList.remove('disabled');
        if (parseInt(inputRefresco.value) === 0) {
            inputRefresco.value = 1; // Asume 1 por defecto al seleccionar un refresco
        }
    }

    // 5. Actualizar precio total
    updateTotalPrice(card);
}

/**
 * Función para manejar la acción de "Agregar al Carrito".
 */
async function handleAgregar(btnAgregar) {
    const card = btnAgregar.closest('.producto-card');
    const productId = btnAgregar.dataset.productId;
    const refrescoId = card.querySelector('.btn-refresco.selected').dataset.refrescoId;

    const cantMilanesa = parseInt(btnAgregar.dataset.cantidadMilanesa);
    const cantRefresco = parseInt(btnAgregar.dataset.cantidadRefresco);
    
    // Validar en el cliente (doble chequeo)
    if (cantMilanesa < 1 || cantMilanesa > MAX_QUANTITY) {
        showFloatingMessage(`La cantidad de Milanesas debe estar entre 1 y ${MAX_QUANTITY}.`, 'error');
        return;
    }
    if (refrescoId != 0 && (cantRefresco < 1 || cantRefresco > MAX_QUANTITY)) {
        showFloatingMessage(`La cantidad de Refrescos debe estar entre 1 y ${MAX_QUANTITY}.`, 'error');
        return;
    }

    // --- CORRECCIÓN AQUÍ ---
    // Guardamos el precio actual ANTES de cambiar el innerHTML del botón
    const priceSpan = btnAgregar.querySelector('.total-price');
    const currentPrice = priceSpan ? priceSpan.textContent : '0.00';
    
    // Deshabilitar el botón temporalmente
    const originalText = btnAgregar.innerHTML;
    btnAgregar.disabled = true;
    btnAgregar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Agregando...';

    const itemKey = generateItemKey(); // Generamos una clave única para la UI

    try {
        const response = await fetch('/api/agregar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: productId,
                refresco_id: refrescoId,
                cant_milanesa: cantMilanesa,
                cant_refresco: cantRefresco,
                item_key: itemKey // Enviamos la clave única para referencia (aunque el servidor generará la suya)
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Éxito:
            showFloatingMessage('✅ ¡Agregado al Carrito!', 'success');
            updateCartIcon(data.cart_count);

            // Transicionar el botón a "Cancelar"
            btnAgregar.classList.remove('btn-agregar');
            btnAgregar.classList.add('btn-cancelar');
            
            // --- USO DEL PRECIO GUARDADO ---
            // Usamos 'currentPrice' en lugar de intentar leer el DOM modificado
            btnAgregar.innerHTML = `❌ Cancelar Último Ítem ($${currentPrice})`;
            
            // Guardar la clave del ítem y el precio para restaurarlo si se cancela
            btnAgregar.dataset.itemKey = itemKey;
            btnAgregar.dataset.lastPrice = currentPrice;
            
            // Revertir a "Agregar" después de 5 segundos
            setTimeout(() => {
                // Solo si el botón sigue en modo "Cancelar"
                if (btnAgregar.classList.contains('btn-cancelar') && btnAgregar.dataset.itemKey === itemKey) {
                    btnAgregar.classList.remove('btn-cancelar');
                    btnAgregar.classList.add('btn-agregar');
                    btnAgregar.innerHTML = originalText;
                    delete btnAgregar.dataset.itemKey;
                    delete btnAgregar.dataset.lastPrice;
                }
                btnAgregar.disabled = false;
            }, 5000); 

        } else {
            // Error de validación o del servidor
            showFloatingMessage(`❌ Error: ${data.message || 'Error desconocido al agregar.'}`, 'error');
            btnAgregar.innerHTML = originalText;
        }

    } catch (error) {
        console.error('Error de red:', error);
        showFloatingMessage('🚨 Error de conexión al servidor.', 'error');
        btnAgregar.innerHTML = originalText; // Restaurar texto si hay error de red
    } finally {
        // Si no se revirtió a "Agregar" automáticamente, lo reactivamos.
        // Nota: Si fue éxito, queremos dejarlo activado pero con clase 'btn-cancelar'
        // Si fue error, ya se restauró arriba.
        if (btnAgregar.classList.contains('btn-agregar')) {
             btnAgregar.disabled = false;
        } else {
             btnAgregar.disabled = false; // Habilitar el botón de cancelar
        }
    }
}


/**
 * Función para manejar la acción de "Cancelar Último Ítem" (solo en la tienda).
 */
async function handleCancelar(btnCancel) {
    const itemKey = btnCancel.dataset.itemKey;
    const lastPrice = btnCancel.dataset.lastPrice || '0.00'; // Recuperamos el precio guardado

    if (!itemKey) {
        showFloatingMessage('Error: No hay ítem a cancelar.', 'error');
        return;
    }

    // Deshabilitar el botón temporalmente
    const originalText = btnCancel.innerHTML;
    btnCancel.disabled = true;
    btnCancel.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cancelando...';

    try {
        const response = await fetch('/api/eliminar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ item_key: itemKey })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Éxito:
            showFloatingMessage('🗑️ Ítem cancelado.', 'warning');
            updateCartIcon(data.cart_count);

            // Revertir el botón a "Agregar"
            btnCancel.classList.remove('btn-cancelar');
            btnCancel.classList.add('btn-agregar');
            
            // Reconstruimos el HTML del botón con el precio recuperado
            btnCancel.innerHTML = `➕ Agregar al carrito ($<span class="total-price">${lastPrice}</span>)`;
            
            delete btnCancel.dataset.itemKey;
            delete btnCancel.dataset.lastPrice;

        } else {
            // Error de validación o del servidor
            showFloatingMessage(`❌ Error al cancelar: ${data.message || 'Error desconocido.'}`, 'error');
            btnCancel.innerHTML = originalText;
        }

    } catch (error) {
        console.error('Error de red:', error);
        showFloatingMessage('🚨 Error de conexión al servidor.', 'error');
        btnCancel.innerHTML = originalText;
    } finally {
        btnCancel.disabled = false;
    }
}


/**
 * Actualiza el contador del carrito en la cabecera.
 */
function updateCartIcon(count) {
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = count;
        cartCountElement.classList.toggle('hidden', count === 0);
        cartCountElement.classList.toggle('flex', count > 0);
        // Compatibilidad con la versión anterior de clases en HTML template
        cartCountElement.style.display = count > 0 ? 'flex' : 'none'; 
    }
}


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
    // 2. LÓGICA DE SELECCIÓN DE REFRESCO Y CANTIDAD
    // ---------------------------------

    document.querySelectorAll('.producto-card').forEach(card => {
        
        // Listener para los botones de Refresco
        card.querySelectorAll('.btn-refresco').forEach(btn => {
            btn.addEventListener('click', () => {
                handleRefrescoSelection(card, btn);
            });
        });
        
        // Listener para los botones de AUMENTAR/DISMINUIR cantidad de MILANESA
        card.querySelector('.cantidad-control-milanesa').addEventListener('click', (event) => {
            const btn = event.target.closest('button');
            const input = card.querySelector('.input-cantidad-milanesa');
            
            if (btn && input) {
                let currentVal = parseInt(input.value);
                if (btn.classList.contains('btn-cant-aumentar')) {
                    if (currentVal < MAX_QUANTITY) {
                         input.value = currentVal + 1;
                    } else {
                        showFloatingMessage(`Límite de ${MAX_QUANTITY} Milanesas alcanzado.`, 'warning');
                    }
                } else if (btn.classList.contains('btn-cant-disminuir') && currentVal > 1) {
                    input.value = currentVal - 1;
                }
                updateTotalPrice(card);
            }
        });
        
        // Listener para la entrada directa de cantidad de MILANESA
        card.querySelector('.input-cantidad-milanesa').addEventListener('input', () => {
            updateTotalPrice(card);
        });
        
        // Listener para los botones de AUMENTAR/DISMINUIR cantidad de REFRESCO
        card.querySelector('.cantidad-control-refresco').addEventListener('click', (event) => {
            const btn = event.target.closest('button');
            const input = card.querySelector('.input-cantidad-refresco');
            const selectedRefrescoBtn = card.querySelector('.btn-refresco.selected');
            const refrescoId = parseInt(selectedRefrescoBtn.dataset.refrescoId);

            // Solo permitir modificación si NO es "Sin Refresco"
            if (btn && input && refrescoId !== 0) {
                let currentVal = parseInt(input.value);
                if (btn.classList.contains('btn-cant-aumentar')) {
                    if (currentVal < MAX_QUANTITY) {
                         input.value = currentVal + 1;
                    } else {
                        showFloatingMessage(`Límite de ${MAX_QUANTITY} Refrescos alcanzado.`, 'warning');
                    }
                } else if (btn.classList.contains('btn-cant-disminuir') && currentVal > 1) {
                    input.value = currentVal - 1;
                } else if (btn.classList.contains('btn-cant-disminuir') && currentVal === 1) {
                    // Al bajar de 1, volvemos a "Sin Refresco" y ponemos la cantidad a 0
                    const sinRefrescoBtn = card.querySelector('.btn-refresco[data-refresco-id="0"]');
                    if(sinRefrescoBtn) {
                        handleRefrescoSelection(card, sinRefrescoBtn);
                    }
                    return; // Ya se actualizó el precio en handleRefrescoSelection
                }
                updateTotalPrice(card);
            }
        });

        // Listener para la entrada directa de cantidad de REFRESCO
        card.querySelector('.input-cantidad-refresco').addEventListener('input', () => {
            const inputRefresco = card.querySelector('.input-cantidad-refresco');
            const selectedRefrescoBtn = card.querySelector('.btn-refresco.selected');
            const refrescoId = parseInt(selectedRefrescoBtn.dataset.refrescoId);

            // Si el valor cambia a 0, automáticamente seleccionar "Sin Refresco"
            if (parseInt(inputRefresco.value) === 0 && refrescoId !== 0) {
                 const sinRefrescoBtn = card.querySelector('.btn-refresco[data-refresco-id="0"]');
                 if(sinRefrescoBtn) {
                     handleRefrescoSelection(card, sinRefrescoBtn);
                 }
            } else {
                updateTotalPrice(card);
            }
        });
    });
    
    // ---------------------------------
    // 3. LÓGICA DE AGREGAR/CANCELAR
    // ---------------------------------
    // Usamos delegación de eventos para los botones de agregar/cancelar
    const productosContainer = document.querySelector('.productos-container');
    if (productosContainer) {
        productosContainer.addEventListener('click', (event) => {
            const btnAgregar = event.target.closest('.btn-agregar');
            if (btnAgregar) {
                event.preventDefault();
                handleAgregar(btnAgregar);
                return;
            }

            const btnCancel = event.target.closest('.btn-cancelar');
            if (btnCancel) {
                event.preventDefault();
                handleCancelar(btnCancel);
                return;
            }
        });
    }


    // ---------------------------------
    // 5. LÓGICA DE INICIALIZACIÓN
    // ---------------------------------
    document.querySelectorAll('.producto-card').forEach(card => {
        // Selecciona el botón "Sin Refresco" por defecto
        const sinRefrescoBtn = card.querySelector('.btn-refresco[data-refresco-id="0"]');
        if (sinRefrescoBtn) {
            sinRefrescoBtn.classList.add('selected');
        }
        
        // Ponemos la cantidad de refresco a 0 por defecto si "Sin Refresco" está seleccionado
        const inputRefresco = card.querySelector('.input-cantidad-refresco');
        if (sinRefrescoBtn && sinRefrescoBtn.classList.contains('selected') && inputRefresco) {
            inputRefresco.value = 0;
        }

        // Inicializar el precio y cantidad en el botón "Agregar al Carrito"
        updateTotalPrice(card);
    });
});