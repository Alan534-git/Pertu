from flask import Flask, render_template, redirect, url_for, session, jsonify, request, Response
from werkzeug.security import check_password_hash, generate_password_hash
import json
import os
import uuid
from datetime import datetime

# NOTA: La clave secreta debe ser una cadena de bytes aleatoria en producción
# Para Canvas, usamos un valor placeholder.
app = Flask(__name__)
app.secret_key = "clave-secreta"  # Necesario para manejar sesiones

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
REQUESTS_FILE = os.path.join(DATA_DIR, "requests.json")

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

delivery_name = "Delivery"
gestoria_name = "Gestoría del automotor"

default_users = {
    "users": [
        {
            "username": "admin",
            "password_hash": generate_password_hash("admin123"),
            "role": "admin",
            "sector": "admin",
            "display_name": "Administrador"
        },
        {
            "username": "cliente_delivery",
            "password_hash": generate_password_hash("delivery123"),
            "role": "cliente",
            "sector": "delivery",
            "display_name": "Cliente Delivery"
        },
        {
            "username": "cliente_gestoria",
            "password_hash": generate_password_hash("gestoria123"),
            "role": "cliente",
            "sector": "gestoria",
            "display_name": "Cliente Gestoría"
        }
    ]
}

default_requests = {
    "delivery_orders": [],
    "gestoria_requests": []
}

gestoria_services = [
    {
        "id": 1,
        "titulo": "Transferencia de vehículo",
        "descripcion": "Carga de datos, control de documentación y seguimiento del trámite.",
        "precio": 180.0
    },
    {
        "id": 2,
        "titulo": "Alta / baja de dominio",
        "descripcion": "Gestión del dominio y validación de requisitos para circular.",
        "precio": 120.0
    },
    {
        "id": 3,
        "titulo": "Informe de dominio",
        "descripcion": "Consulta rápida de estado legal y antecedentes del automotor.",
        "precio": 60.0
    },
    {
        "id": 4,
        "titulo": "Seguimiento de trámite",
        "descripcion": "Estado en tiempo real del expediente y notificaciones básicas.",
        "precio": 40.0
    }
]


def load_json(path, default_value):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_value


def save_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)


def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        save_json(USERS_FILE, default_users)
    if not os.path.exists(REQUESTS_FILE):
        save_json(REQUESTS_FILE, default_requests)


def load_users():
    data = load_json(USERS_FILE, default_users)
    return data.get("users", [])


def load_requests():
    data = load_json(REQUESTS_FILE, default_requests)
    data.setdefault("delivery_orders", [])
    data.setdefault("gestoria_requests", [])
    return data


def save_requests(payload):
    save_json(REQUESTS_FILE, payload)


def get_current_user():
    return session.get("user")


def get_user_by_username(username):
    return next((user for user in load_users() if user["username"] == username), None)


def role_required(role):
    current_user = get_current_user()
    if not current_user or current_user.get("role") != role:
        return redirect(url_for("login"))
    return None


def redirect_for_user(user):
    if not user:
        return redirect(url_for("login"))

    if user.get("role") == "admin":
        return redirect(url_for("admin_dashboard"))

    if user.get("sector") == "gestoria":
        return redirect(url_for("gestoria"))

    return redirect(url_for("delivery"))


@app.context_processor
def inject_user_context():
    current_user = get_current_user()
    return {
        "current_user": current_user,
        "is_logged_in": current_user is not None,
        "is_admin": bool(current_user and current_user.get("role") == "admin"),
        "user_sector": current_user.get("sector") if current_user else None,
    }


ensure_data_files()

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
    """Ruta principal: redirige según sesión y rol."""
    current_user = get_current_user()
    if current_user:
        return redirect_for_user(current_user)
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Autenticación basada en usuarios cargados desde JSON."""
    if get_current_user():
        return redirect_for_user(get_current_user())

    error_message = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_user_by_username(username)

        if user and check_password_hash(user["password_hash"], password):
            session["user"] = {
                "username": user["username"],
                "display_name": user.get("display_name", user["username"]),
                "role": user["role"],
                "sector": user.get("sector", "delivery")
            }
            return redirect_for_user(session["user"])

        error_message = "Usuario o contraseña incorrectos."

    return render_template("login.html", error_message=error_message)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/delivery")
def delivery():
    """Sector Delivery reutilizando la tienda actual."""
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("login"))

    if current_user.get("role") != "admin" and current_user.get("sector") not in ("delivery", "admin"):
        return redirect_for_user(current_user)

    cart_count = get_cart_count(session.get("carrito", []))
    return render_template(
        "index.html",
        productos=productos,
        cart_count=cart_count,
        sector_title=delivery_name,
        section_description="Pedidos rápidos, seguimiento y confirmación de compra.",
        page_title="Delivery"
    )


@app.route("/gestoria")
def gestoria():
    """Sector Gestoría del automotor con servicios y registro en JSON."""
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("login"))

    if current_user.get("role") != "admin" and current_user.get("sector") not in ("gestoria", "admin"):
        return redirect_for_user(current_user)

    requests_data = load_requests()
    all_requests = requests_data.get("gestoria_requests", [])
    if current_user.get("role") != "admin":
        visible_requests = [item for item in all_requests if item.get("username") == current_user.get("username")]
    else:
        visible_requests = all_requests

    return render_template(
        "gestoria.html",
        sector_title=gestoria_name,
        services=gestoria_services,
        requests=visible_requests,
        page_title="Gestoría del automotor"
    )


@app.route("/admin")
def admin_dashboard():
    """Panel mínimo para revisar usuarios y solicitudes."""
    protected = role_required("admin")
    if protected:
        return protected

    users = load_users()
    requests_data = load_requests()
    return render_template(
        "admin.html",
        users=users,
        delivery_orders=requests_data.get("delivery_orders", []),
        gestoria_requests=requests_data.get("gestoria_requests", []),
        page_title="Panel admin"
    )


@app.route("/favicon.ico")
def favicon():
        """Sirve un favicon embebido para evitar el 404 del navegador."""
        favicon_svg = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>
    <rect width='64' height='64' rx='14' fill='#d6451e'/>
    <path d='M18 20h28c2 0 4 2 4 4v2c0 4-3 7-7 7h-4l7 11h-10l-6-10h-6v10H18V20zm10 14h10c3 0 5-2 5-5s-2-5-5-5H28v10z' fill='#ffffff'/>
</svg>"""
        return Response(favicon_svg, mimetype="image/svg+xml")

@app.route("/carrito")
def carrito():
    """Ruta de la página del carrito de compras."""
    if not get_current_user():
        return redirect(url_for("login"))

    carrito_items = session.get("carrito", [])
    total = sum(item['precio_total'] for item in carrito_items) # Corregido: usa precio_total
    return render_template("carrito.html", carrito=carrito_items, total=total, page_title="Carrito Delivery")

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
    if not get_current_user():
        return jsonify({'success': False, 'message': 'Debe iniciar sesión.'}), 401

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
    current_user = get_current_user()
    if not current_user:
        return jsonify({'success': False, 'message': 'Debe iniciar sesión.'}), 401

    carrito = session.get("carrito", [])
    if not carrito:
        return jsonify({'success': False, 'message': 'El carrito está vacío.'}), 400

    # Simulación de validación de pago/datos
    data = request.get_json()
    
    # 1. Procesa la orden y la guarda en JSON.
    requests_data = load_requests()
    requests_data["delivery_orders"].append({
        "id": str(uuid.uuid4()),
        "username": current_user.get("username"),
        "display_name": current_user.get("display_name", current_user.get("username")),
        "items": carrito,
        "total": sum(item['precio_total'] for item in carrito),
        "status": "pendiente",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "payment": data or {}
    })
    save_requests(requests_data)

    # 2. Limpia el carrito
    session["carrito"] = []
    session.modified = True

    return jsonify({'success': True, 'message': 'Pago procesado'})


@app.route("/api/tramite", methods=["POST"])
def api_tramite():
    """Registra una solicitud de Gestoría en JSON."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'success': False, 'message': 'Debe iniciar sesión.'}), 401

    data = request.get_json() or {}
    nombre = (data.get("nombre") or "").strip()
    dni = (data.get("dni") or "").strip()
    servicio_id = data.get("servicio_id")
    detalle = (data.get("detalle") or "").strip()

    if not nombre or not dni or not servicio_id:
        return jsonify({'success': False, 'message': 'Complete nombre, DNI y servicio.'}), 400

    servicio = next((item for item in gestoria_services if str(item["id"]) == str(servicio_id)), None)
    if not servicio:
        return jsonify({'success': False, 'message': 'Servicio no encontrado.'}), 404

    requests_data = load_requests()
    new_request = {
        "id": str(uuid.uuid4()),
        "username": current_user.get("username"),
        "display_name": current_user.get("display_name", current_user.get("username")),
        "nombre": nombre,
        "dni": dni,
        "servicio_id": servicio["id"],
        "servicio": servicio["titulo"],
        "detalle": detalle,
        "status": "pendiente",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    requests_data["gestoria_requests"].append(new_request)
    save_requests(requests_data)

    return jsonify({'success': True, 'message': 'Trámite registrado', 'request': new_request})


@app.route("/api/admin/request-status", methods=["POST"])
def api_admin_request_status():
    """Permite al admin actualizar el estado de una solicitud."""
    protected = role_required("admin")
    if protected:
        return jsonify({'success': False, 'message': 'Acceso denegado.'}), 403

    data = request.get_json() or {}
    collection = data.get("collection")
    request_id = data.get("request_id")
    status = (data.get("status") or "").strip().lower()

    if collection not in ("delivery_orders", "gestoria_requests"):
        return jsonify({'success': False, 'message': 'Colección inválida.'}), 400
    if not request_id or not status:
        return jsonify({'success': False, 'message': 'Faltan datos.'}), 400

    requests_data = load_requests()
    updated = False
    for item in requests_data.get(collection, []):
        if item.get("id") == request_id:
            item["status"] = status
            item["updated_at"] = datetime.utcnow().isoformat() + "Z"
            updated = True
            break

    if not updated:
        return jsonify({'success': False, 'message': 'Solicitud no encontrada.'}), 404

    save_requests(requests_data)
    return jsonify({'success': True, 'message': 'Estado actualizado.'})

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