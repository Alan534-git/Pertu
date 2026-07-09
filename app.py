from flask import Flask, render_template, redirect, url_for, session, jsonify, request
import os
import uuid # Necesario para generar item_key únicas

# NOTA: La clave secreta debe ser una cadena de bytes aleatoria en producción
# Para Canvas, usamos un valor placeholder.
app = Flask(__name__)
app.secret_key = "clave-secreta"  # Necesario para manejar sesiones

# --- NUEVA RESTRICCIÓN DE CANTIDAD ---
MAX_QUANTITY = 20
# -----------------------------------

# --- PRODUCTOS ACTUALIZADOS A MILANESAS ---
productos = [
    {"id": 1, "nombre": "Milanesa Napolitana", "precio": 25, "imagen": "milanesa_napolitana.webp"},
    {"id": 2, "nombre": "Milanesa a Caballo", "precio": 22, "imagen": "milanesa_caballo.webp"},
    {"id": 3, "nombre": "Milanesa Fugazzeta", "precio": 24, "imagen": "milanesa_fugazzeta.webp"},
    {"id": 4, "nombre": "Milanesa Cheddar y Bacon", "precio": 26, "imagen": "milanesa_cheddar.webp"}
]
# --- FIN DE CAMBIOS DE PRODUCTOS ---

# Precios de los refrescos
refresco_precios = {
    '0': 0.00,  # Sin Refresco
    '1': 1.50,  # Coca-Cola
    '2': 1.75,  # Pepsi
    '3': 1.25,  # Sprite
    '4': 1.60,  # Fanta
    '5': 1.00,  # 7Up
    '6': 0.75   # Manaos (nuevo)
}

# Diccionario para mapear IDs de refresco a nombres e imágenes
refresco_info = {
    '0': {'nombre': 'Sin Refresco', 'imagen': None},
    '1': {'nombre': 'Coca-Cola', 'imagen': 'coca_cola.webp'},
    '2': {'nombre': 'Pepsi', 'imagen': 'pepsi.webp'},
    '3': {'nombre': 'Sprite', 'imagen': 'sprite.webp'},
    '4': {'nombre': 'Fanta', 'imagen': 'fanta.webp'},
    '5': {'nombre': '7Up', 'imagen': '7up.webp'},
    '6': {'nombre': 'Manaos', 'imagen': 'manaos.webp'}
}

# ----------------------------------
# Funciones de utilidad
# ----------------------------------

def get_cart_count(carrito):
    """Calcula el número total de ítems distintos en el carrito."""
    return len(carrito)

def get_product_by_id(product_id):
    """Busca un producto por su ID."""
    try:
        pid = int(product_id)
        return next((p for p in productos if p['id'] == pid), None)
    except ValueError:
        return None

def calculate_item_price(milanesa_precio, cant_milanesa, refresco_id, cant_refresco):
    """Calcula el precio total de una línea de pedido."""
    
    # 1. Precio de la milanesa
    milanesa_total = milanesa_precio * cant_milanesa
    
    # 2. Precio del refresco (solo si se seleccionó uno)
    refresco_precio = refresco_precios.get(str(refresco_id), 0.00)
    
    # Si se seleccionó "Sin Refresco", la cantidad de refresco es 0 y el precio es 0.
    if refresco_id == 0:
        refresco_total = 0.00
    else:
        refresco_total = refresco_precio * cant_refresco
        
    return milanesa_total + refresco_total

# ----------------------------------
# Rutas
# ----------------------------------

@app.route("/")
def index():
    """Ruta de la página principal (tienda)."""
    cart_count = get_cart_count(session.get("carrito", []))
    return render_template("index.html", productos=productos, cart_count=cart_count)

@app.route("/carrito")
def carrito():
    """Ruta de la página del carrito de compras."""
    carrito_items = session.get("carrito", [])
    total = sum(item['precio_total'] for item in carrito_items) # Corregido: usa precio_total
    return render_template("carrito.html", carrito=carrito_items, total=total)

@app.route("/vaciar")
def vaciar():
    """Ruta para vaciar el carrito."""
    session["carrito"] = []
    session.modified = True
    return redirect(url_for("carrito"))

@app.route("/api/agregar", methods=["POST"])
def api_agregar():
    """
    Agrega un ítem al carrito y devuelve JSON.
    El cliente envía product_id, refresco_id, cant_milanesa, cant_refresco.
    """
    data = request.get_json()
    product_id = data.get('product_id')
    refresco_id_str = str(data.get('refresco_id', 0))
    refresco_id = int(refresco_id_str)
    
    # Intenta parsear las cantidades, usando 1 y 0 como fallback
    try:
        cant_milanesa = int(data.get('cant_milanesa', 1))
        cant_refresco = int(data.get('cant_refresco', 0))
    except ValueError:
        return jsonify({'success': False, 'message': 'Cantidad inválida'}), 400

    # 1. Validar rangos de cantidad
    if cant_milanesa <= 0 or cant_milanesa > MAX_QUANTITY:
        return jsonify({
            'success': False, 
            'message': f'La cantidad de Milanesas debe estar entre 1 y {MAX_QUANTITY}.'
        }), 400
    
    # La cantidad de refresco debe ser 0 si no hay refresco seleccionado, o entre 1 y MAX_QUANTITY si sí lo hay.
    if refresco_id != 0:
        if cant_refresco <= 0 or cant_refresco > MAX_QUANTITY:
             return jsonify({
                'success': False, 
                'message': f'La cantidad de Refrescos debe estar entre 1 y {MAX_QUANTITY}.'
            }), 400
    elif refresco_id == 0 and cant_refresco != 0:
         return jsonify({'success': False, 'message': 'No puede haber cantidad de refresco si selecciona "Sin Refresco".'}), 400


    producto = get_product_by_id(product_id)

    if not producto:
        return jsonify({'success': False, 'message': 'Producto no encontrado'}), 404

    # 2. Calcular precio y construir el ítem
    milanesa_precio = producto['precio']
    
    precio_total = calculate_item_price(milanesa_precio, cant_milanesa, refresco_id, cant_refresco)

    # Obtener info del refresco
    info_ref = refresco_info.get(refresco_id_str, {'nombre': 'Desconocido', 'imagen': None})
    refresco_nombre = info_ref['nombre']
    refresco_imagen = info_ref['imagen']

    # --- CORRECCIÓN CLAVE: Usar el ID del cliente si existe, para permitir la cancelación ---
    client_key = data.get('item_key')
    final_key = client_key if client_key else str(uuid.uuid4())

    item = {
        'item_key': final_key, # Usamos la clave que sincroniza UI y Backend
        'id': producto['id'],
        'nombre': producto['nombre'],
        'imagen': producto['imagen'], 
        
        # Cantidades
        'cantidad_milanesa': cant_milanesa, 
        'cantidad_refresco': cant_refresco,
        
        # Info Refresco
        'refresco_id': refresco_id,
        'refresco_nombre': refresco_nombre,
        'imagen_refresco': refresco_imagen,
        
        # Precios
        'precio_milanesa': milanesa_precio,
        'precio_refresco': refresco_precios.get(refresco_id_str, 0.00),
        'precio_total': precio_total
    }

    # 3. Agregar al carrito
    carrito = session.get("carrito", [])
    carrito.append(item)
    session["carrito"] = carrito
    session.modified = True
    
    cart_count = get_cart_count(carrito)

    return jsonify({'success': True, 'message': 'Ítem agregado', 'cart_count': cart_count})

@app.route("/api/checkout", methods=["POST"])
def api_checkout():
    """
    Simula el proceso de pago.
    """
    carrito = session.get("carrito", [])
    if not carrito:
        return jsonify({'success': False, 'message': 'El carrito está vacío.'}), 400

    # Simulación de validación de pago/datos
    data = request.get_json()
    
    # 1. Procesa la orden (simulado)
    # Aquí iría la lógica real de procesamiento de pago y guardado de orden.

    # 2. Limpia el carrito
    session["carrito"] = []
    session.modified = True

    return jsonify({'success': True, 'message': 'Pago procesado'})

@app.route("/eliminar/<item_key>")
def eliminar(item_key):
    """Elimina un ítem específico (por item_key) del carrito."""
    carrito = session.get("carrito", [])
    
    nuevo_carrito = [item for item in carrito if item["item_key"] != item_key]
    
    if len(nuevo_carrito) < len(carrito):
        session["carrito"] = nuevo_carrito
        session.modified = True
    
    return redirect(url_for("carrito"))

# --- NUEVA RUTA API PARA ELIMINAR (Usada por index.js para "Cancelar") ---
@app.route("/api/eliminar", methods=["POST"])
def api_eliminar():
    """
    Elimina un ítem específico (por item_key) del carrito y devuelve JSON.
    """
    data = request.get_json()
    item_key = data.get('item_key')
    
    if not item_key:
        return jsonify({'success': False, 'message': 'Falta item_key'}), 400

    carrito = session.get("carrito", [])
    nuevo_carrito = [item for item in carrito if item["item_key"] != item_key]
    
    if len(nuevo_carrito) < len(carrito):
        session["carrito"] = nuevo_carrito
        session.modified = True
        cart_count = get_cart_count(nuevo_carrito)
        return jsonify({'success': True, 'message': 'Ítem eliminado', 'cart_count': cart_count})
    else:
        cart_count = get_cart_count(carrito)
        return jsonify({'success': False, 'message': 'Ítem no encontrado', 'cart_count': cart_count}), 404

if __name__ == "__main__":
    app_id = os.environ.get('__app_id', 'default-app-id')
    app.run(debug=True, host='0.0.0.0', port=5000)