from flask import Flask, render_template, redirect, url_for, session, jsonify, request, Response
from werkzeug.security import check_password_hash, generate_password_hash
import json
import os
import uuid
from datetime import datetime, timedelta

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

# ============================================================
# SECTOR DUAL — indumentaria femenina y deportiva
# ============================================================
dual_name = "DUAL — Indumentaria"
DUAL_ENVIO_COSTO = 1990

dual_productos = [
    # ---- MUJER ----
    {"id": 101, "nombre": "Vestido Lino", "seccion": "mujer", "subcategoria": "Vestidos",
     "precio": 28990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#e6c7ba", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Beige", "Negro"],
     "descripcion": "Vestido de lino fresco y liviano, ideal para el día a día."},
    {"id": 102, "nombre": "Top Morley", "seccion": "mujer", "subcategoria": "Tops",
     "precio": 9990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#d9b8a8", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Blanco", "Terracota"],
     "descripcion": "Top básico de morley, suave al tacto y de uso versátil."},
    {"id": 103, "nombre": "Jean Wide Leg", "seccion": "mujer", "subcategoria": "Jeans",
     "precio": 25990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#7c8ba3", "talles": ["36", "38", "40", "42"], "colores_nombre": ["Azul"],
     "descripcion": "Jean tiro alto de pierna ancha, silueta relajada."},
    {"id": 104, "nombre": "Conjunto Rib", "seccion": "mujer", "subcategoria": "Conjuntos",
     "precio": 24990, "descuento": None, "precio_original": None, "es_novedad": True,
     "color_media": "#c9a6a1", "talles": ["S", "M", "L"], "colores_nombre": ["Rosa viejo", "Negro"],
     "descripcion": "Conjunto de top y calza en canalé, ideal para combinar."},
    {"id": 105, "nombre": "Blusa Oversize", "seccion": "mujer", "subcategoria": "Blusas",
     "precio": 18990, "descuento": 21, "precio_original": 23990, "es_novedad": False,
     "color_media": "#ded3c4", "talles": ["S", "M", "L"], "colores_nombre": ["Crudo"],
     "descripcion": "Blusa oversize de gasa liviana, corte relajado."},
    {"id": 106, "nombre": "Campera Liviana", "seccion": "mujer", "subcategoria": "Camperas",
     "precio": 34990, "descuento": None, "precio_original": None, "es_novedad": True,
     "color_media": "#b7a99c", "talles": ["S", "M", "L", "XL"], "colores_nombre": ["Camel"],
     "descripcion": "Campera liviana de entretiempo, con capucha desmontable."},
    {"id": 107, "nombre": "Falda Midi", "seccion": "mujer", "subcategoria": "Faldas",
     "precio": 16990, "descuento": 24, "precio_original": 22350, "es_novedad": False,
     "color_media": "#a9764f", "talles": ["XS", "S", "M"], "colores_nombre": ["Ladrillo"],
     "descripcion": "Falda midi tiro alto con abertura frontal."},
    {"id": 108, "nombre": "Crop Top", "seccion": "mujer", "subcategoria": "Tops",
     "precio": 8990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#e0a8a0", "talles": ["XS", "S", "M"], "colores_nombre": ["Rosa"],
     "descripcion": "Crop top básico de algodón, calce ajustado."},

    # ---- DEPORTIVO ----
    {"id": 201, "nombre": "Top Deportivo", "seccion": "deportivo", "subcategoria": "Tops",
     "precio": 10990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#2b3a55", "talles": ["S", "M", "L"], "colores_nombre": ["Negro", "Gris"],
     "descripcion": "Top deportivo con soporte medio, tela transpirable."},
    {"id": 202, "nombre": "Calza Premium", "seccion": "deportivo", "subcategoria": "Calzas",
     "precio": 21990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#232d3f", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Negro"],
     "descripcion": "Calza de compresión con cintura alta, tela secado rápido."},
    {"id": 203, "nombre": "Remera Dry Fit", "seccion": "deportivo", "subcategoria": "Remeras",
     "precio": 12990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#3d4a63", "talles": ["S", "M", "L", "XL"], "colores_nombre": ["Gris", "Azul"],
     "descripcion": "Remera técnica dry fit para entrenamiento."},
    {"id": 204, "nombre": "Short Run", "seccion": "deportivo", "subcategoria": "Shorts",
     "precio": 14990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#1c2540", "talles": ["S", "M", "L"], "colores_nombre": ["Negro"],
     "descripcion": "Short de running liviano con malla interior."},
    {"id": 205, "nombre": "Campera Run", "seccion": "deportivo", "subcategoria": "Camperas",
     "precio": 28990, "descuento": 20, "precio_original": 36240, "es_novedad": False,
     "color_media": "#34405c", "talles": ["S", "M", "L", "XL"], "colores_nombre": ["Gris"],
     "descripcion": "Campera cortavientos para entrenar al aire libre."},
    {"id": 206, "nombre": "Conjunto Training", "seccion": "deportivo", "subcategoria": "Conjuntos",
     "precio": 34990, "descuento": 26, "precio_original": 47280, "es_novedad": False,
     "color_media": "#465372", "talles": ["S", "M", "L"], "colores_nombre": ["Negro"],
     "descripcion": "Conjunto de top y calza para entrenamiento de alta intensidad."},
    {"id": 207, "nombre": "Zapatillas Air", "seccion": "deportivo", "subcategoria": "Calzado",
     "precio": 66990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#17203a", "talles": ["36", "37", "38", "39", "40"], "colores_nombre": ["Blanco/Negro"],
     "descripcion": "Zapatillas running con amortiguación reactiva."},
    {"id": 208, "nombre": "Mochila Sport", "seccion": "deportivo", "subcategoria": "Accesorios",
     "precio": 18990, "descuento": None, "precio_original": None, "es_novedad": True,
     "color_media": "#4a5670", "talles": ["Único"], "colores_nombre": ["Negro"],
     "descripcion": "Mochila deportiva con compartimento para calzado."},
]

DUAL_CATEGORIA_CONFIG = {
    "mujer": {
        "titulo": "Indumentaria Femenina", "eyebrow": "INDUMENTARIA",
        "copy": "Descubrí las últimas tendencias en ropa y accesorios.",
        "subcategorias": ["Vestidos", "Tops", "Jeans", "Conjuntos", "Faldas", "Blusas", "Accesorios"],
    },
    "deportivo": {
        "titulo": "Ropa Deportiva", "eyebrow": "ROPA",
        "copy": "Tecnología, confort y diseño para tu mejor rendimiento.",
        "subcategorias": ["Calzas", "Tops", "Shorts", "Buzos", "Camperas", "Conjuntos", "Accesorios"],
    },
    "ofertas": {
        "titulo": "Ofertas", "eyebrow": "OFERTAS",
        "copy": "Hasta 50% OFF en productos seleccionados.",
        "subcategorias": ["Mujer", "Deportivo", "Calzado", "Accesorios"],
    },
    "novedades": {
        "titulo": "Novedades", "eyebrow": "NOVEDADES",
        "copy": "Lo último que llegó a DUAL.",
        "subcategorias": ["Mujer", "Deportivo", "Calzado", "Accesorios"],
    },
}

DUAL_CATEGORIAS_DESTACADAS = [
    {"nombre": "Vestidos", "seccion": "mujer"},
    {"nombre": "Tops", "seccion": "mujer"},
    {"nombre": "Jeans", "seccion": "mujer"},
    {"nombre": "Training", "seccion": "deportivo"},
    {"nombre": "Running", "seccion": "deportivo"},
    {"nombre": "Calzado", "seccion": "deportivo"},
]

DUAL_TALLES = ["XS", "S", "M", "L", "XL"]
DUAL_COLORES_HEX = ["#1a1a1a", "#c9a6a1", "#7c8ba3", "#e6c7ba", "#3d4a63"]

DUAL_TRACKING_STEPS = [
    "Pedido confirmado",
    "En preparación",
    "En camino",
    "En destino",
    "Entregado",
]

DUAL_ESTADO_LABELS = {
    "pendiente": "Pendiente",
    "en_camino": "En camino",
    "entregado": "Entregado",
    "cancelado": "Cancelado",
}

DUAL_ESTADO_CLASES = {
    "pendiente": "pendiente",
    "en_camino": "en-camino",
    "entregado": "entregado",
    "cancelado": "cancelado",
}

DUAL_ESTADO_A_PASO = {
    "pendiente": 0,
    "en_camino": 2,
    "entregado": 4,
    "cancelado": 1,
}

DUAL_MESES_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
                  "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DUAL_DIAS_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
# ============================================================


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
        },
        {
            "username": "cliente_dual",
            "password_hash": generate_password_hash("dual123"),
            "role": "cliente",
            "sector": "dual",
            "display_name": "Cliente DUAL"
        }
    ]
}

default_requests = {
    "delivery_orders": [],
    "gestoria_requests": [],
    "dual_orders": []
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
    else:
        current_users = load_json(USERS_FILE, {"users": []}).get("users", [])
        existing_usernames = {user.get("username") for user in current_users if isinstance(user, dict)}
        missing_users = []
        for user in default_users.get("users", []):
            if user.get("username") not in existing_usernames:
                missing_users.append(user)
        if missing_users:
            current_users.extend(missing_users)
            save_json(USERS_FILE, {"users": current_users})

    if not os.path.exists(REQUESTS_FILE):
        save_json(REQUESTS_FILE, default_requests)


def load_users():
    data = load_json(USERS_FILE, default_users)
    return data.get("users", [])


def load_requests():
    data = load_json(REQUESTS_FILE, default_requests)
    data.setdefault("delivery_orders", [])
    data.setdefault("gestoria_requests", [])
    data.setdefault("dual_orders", [])
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

    if user.get("sector") == "dual":
        return redirect(url_for("dual_home"))

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


def get_dual_product_by_id(product_id):
    """Busca un producto DUAL por su ID."""
    try:
        pid = int(product_id)
    except (TypeError, ValueError):
        return None
    return next((p for p in dual_productos if p["id"] == pid), None)


def dual_fecha_corta(iso_str):
    """Convierte una fecha ISO a formato dd/mm/aaaa."""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", ""))
        return dt.strftime("%d/%m/%Y")
    except (ValueError, AttributeError):
        return ""


def dual_fecha_larga(dt):
    """Formatea una fecha en español, sin depender del locale del sistema."""
    return f"{DUAL_DIAS_ES[dt.weekday()]} {dt.day} de {DUAL_MESES_ES[dt.month - 1]}"


def dual_build_tracking(pedido):
    """Arma las fechas estimadas de cada paso del seguimiento de envío."""
    creado = datetime.fromisoformat(pedido["created_at"].replace("Z", ""))
    incrementos = [0, 1, 2, 3, 4]
    pasos = []
    for nombre, dias in zip(DUAL_TRACKING_STEPS, incrementos):
        fecha_dt = creado + timedelta(days=dias)
        pasos.append({"nombre": nombre, "fecha": fecha_dt.strftime("%d/%m")})
    return pasos


def dual_require_sector(current_user):
    """Verifica acceso al sector DUAL; devuelve una respuesta de redirect o None si está OK."""
    if not current_user:
        return redirect(url_for("login"))
    if current_user.get("role") != "admin" and current_user.get("sector") not in ("dual", "admin"):
        return redirect_for_user(current_user)
    return None

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


@app.route("/dual")
def dual_home():
    """Home de DUAL: hero Mujer/Deportivo + categorías destacadas + novedades."""
    current_user = get_current_user()
    blocked = dual_require_sector(current_user)
    if blocked:
        return blocked

    destacados = [p for p in dual_productos if p.get("es_novedad")][:4]
    return render_template(
        "dual_index.html",
        categorias_destacadas=DUAL_CATEGORIAS_DESTACADAS,
        destacados=destacados,
        active_nav="inicio",
        dual_cart_count=0,
        page_title="DUAL",
    )


@app.route("/dual/<categoria>")
def dual_categoria(categoria):
    """Secciones Mujer, Deportivo, Ofertas y Novedades."""
    current_user = get_current_user()
    blocked = dual_require_sector(current_user)
    if blocked:
        return blocked

    categoria = categoria.lower()
    config = DUAL_CATEGORIA_CONFIG.get(categoria)
    if not config:
        return redirect(url_for("dual_home"))

    if categoria == "mujer":
        productos_filtrados = [p for p in dual_productos if p["seccion"] == "mujer"]
    elif categoria == "deportivo":
        productos_filtrados = [p for p in dual_productos if p["seccion"] == "deportivo"]
    elif categoria == "ofertas":
        productos_filtrados = [p for p in dual_productos if p.get("descuento")]
    else:  # novedades
        productos_filtrados = [p for p in dual_productos if p.get("es_novedad")]

    return render_template(
        "dual_categoria.html",
        categoria=categoria,
        titulo=config["titulo"],
        eyebrow=config["eyebrow"],
        copy=config["copy"],
        subcategorias=config["subcategorias"],
        talles=DUAL_TALLES,
        colores=DUAL_COLORES_HEX,
        productos=productos_filtrados,
        active_nav=categoria,
        dual_cart_count=0,
        page_title=config["titulo"],
    )


@app.route("/dual/producto/<int:product_id>")
def dual_producto(product_id):
    """Detalle de producto: selección de talle, color y cantidad."""
    current_user = get_current_user()
    blocked = dual_require_sector(current_user)
    if blocked:
        return blocked

    producto = get_dual_product_by_id(product_id)
    if not producto:
        return redirect(url_for("dual_home"))

    return render_template(
        "dual_producto.html",
        producto=producto,
        active_nav=producto["seccion"],
        dual_cart_count=0,
        page_title=producto["nombre"],
    )


@app.route("/dual/comprar/<int:product_id>")
def dual_comprar(product_id):
    """
    Se abre SOLO al presionar 'Comprar' en un producto.
    Muestra el wizard: Formulario de envío -> Métodos de pago -> Comprobante.
    """
    current_user = get_current_user()
    blocked = dual_require_sector(current_user)
    if blocked:
        return blocked

    producto = get_dual_product_by_id(product_id)
    if not producto:
        return redirect(url_for("dual_home"))

    talla = request.args.get("talla") or producto["talles"][0]
    color = request.args.get("color") or producto["colores_nombre"][0]
    try:
        cantidad = int(request.args.get("cantidad", 1))
    except ValueError:
        cantidad = 1
    cantidad = max(1, min(10, cantidad))

    subtotal = producto["precio"] * cantidad
    envio_costo = DUAL_ENVIO_COSTO
    total = subtotal + envio_costo

    item = {
        "product_id": producto["id"],
        "nombre": producto["nombre"],
        "color_media": producto["color_media"],
        "talla": talla,
        "color": color,
        "cantidad": cantidad,
        "precio_unitario": producto["precio"],
        "subtotal": subtotal,
    }

    order_payload = {"item": item, "envio_costo": envio_costo, "total": total}

    return render_template(
        "dual_checkout.html",
        item=item,
        envio_costo=envio_costo,
        total=total,
        order_payload_json=json.dumps(order_payload, ensure_ascii=False),
        active_nav=producto["seccion"],
        dual_cart_count=0,
        page_title="Finalizar compra",
    )


@app.route("/dual/pedidos")
def dual_pedidos():
    """Mis pedidos, con tabs por estado (Todos / En camino / Entregados / Cancelados)."""
    current_user = get_current_user()
    blocked = dual_require_sector(current_user)
    if blocked:
        return blocked

    filtro = request.args.get("estado", "todos")
    requests_data = load_requests()
    todos_los_pedidos = requests_data.get("dual_orders", [])

    if current_user.get("role") != "admin":
        pedidos_usuario = [o for o in todos_los_pedidos if o.get("username") == current_user.get("username")]
    else:
        pedidos_usuario = todos_los_pedidos

    if filtro != "todos":
        pedidos_usuario = [o for o in pedidos_usuario if o.get("estado") == filtro]

    pedidos_usuario = sorted(pedidos_usuario, key=lambda o: o.get("created_at", ""), reverse=True)

    pedidos_view = []
    for o in pedidos_usuario:
        estado = o.get("estado", "pendiente")
        pedidos_view.append({
            "id": o["id"],
            "numero": o["numero"],
            "total": o["total"],
            "item": o["item"],
            "fecha_corta": dual_fecha_corta(o["created_at"]),
            "estado_clase": DUAL_ESTADO_CLASES.get(estado, "pendiente"),
            "estado_label": DUAL_ESTADO_LABELS.get(estado, "Pendiente"),
        })

    return render_template(
        "dual_pedidos.html",
        pedidos=pedidos_view,
        filtro=filtro,
        active_nav="",
        dual_cart_count=0,
        page_title="Mis pedidos",
    )


@app.route("/dual/pedido/<order_id>")
def dual_pedido_detalle(order_id):
    """Seguimiento de envío de un pedido puntual."""
    current_user = get_current_user()
    blocked = dual_require_sector(current_user)
    if blocked:
        return blocked

    requests_data = load_requests()
    pedido_raw = next((o for o in requests_data.get("dual_orders", []) if o["id"] == order_id), None)
    if not pedido_raw:
        return redirect(url_for("dual_pedidos"))
    if current_user.get("role") != "admin" and pedido_raw.get("username") != current_user.get("username"):
        return redirect(url_for("dual_pedidos"))

    pasos = dual_build_tracking(pedido_raw)
    creado = datetime.fromisoformat(pedido_raw["created_at"].replace("Z", ""))
    fecha_estimada_dt = creado + timedelta(days=4)

    envio = pedido_raw.get("envio", {})
    direccion = ", ".join(filter(None, [
        f"{envio.get('calle', '')} {envio.get('numero', '')}".strip(),
        envio.get("localidad", ""),
    ]))

    pedido_view = {
        "numero": pedido_raw["numero"],
        "paso_actual": pedido_raw.get("paso_actual", 1),
        "transportista": pedido_raw.get("transportista", "Andreani"),
        "codigo_seguimiento": pedido_raw.get("codigo_seguimiento", ""),
        "fecha_estimada": dual_fecha_larga(fecha_estimada_dt),
        "horario_desde": "10:00",
        "horario_hasta": "18:00",
        "direccion": direccion or "Sin dirección registrada",
    }

    return render_template(
        "dual_seguimiento.html",
        pedido=pedido_view,
        pasos=pasos,
        active_nav="",
        dual_cart_count=0,
        page_title="Seguimiento de envío",
    )


@app.route("/api/dual/pedido", methods=["POST"])
def api_dual_pedido():
    """Confirma la compra: guarda el pedido y devuelve datos del comprobante."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({"success": False, "message": "Debe iniciar sesión."}), 401

    data = request.get_json() or {}
    item = data.get("item")
    envio_costo = data.get("envio_costo", DUAL_ENVIO_COSTO)
    total = data.get("total")
    envio = data.get("envio") or {}
    metodo_pago = data.get("metodo_pago", "tarjeta")

    if not item or not total:
        return jsonify({"success": False, "message": "Datos de compra incompletos."}), 400
    if not envio.get("nombre") or not envio.get("email") or not envio.get("calle"):
        return jsonify({"success": False, "message": "Completá los datos de envío."}), 400

    order_id = str(uuid.uuid4())
    numero = "DUAL-" + order_id[:6].upper()
    created_at = datetime.utcnow().isoformat() + "Z"
    codigo_seguimiento = "ARD" + order_id[:9].upper()

    pedido = {
        "id": order_id,
        "numero": numero,
        "username": current_user.get("username"),
        "display_name": current_user.get("display_name", current_user.get("username")),
        "item": item,
        "envio_costo": envio_costo,
        "total": total,
        "envio": envio,
        "metodo_pago": metodo_pago,
        "estado": "en_camino",
        "paso_actual": 1,
        "transportista": "Andreani",
        "codigo_seguimiento": codigo_seguimiento,
        "created_at": created_at,
    }

    requests_data = load_requests()
    requests_data["dual_orders"].append(pedido)
    save_requests(requests_data)

    total_formateado = "$" + "{:,.0f}".format(total).replace(",", ".")

    return jsonify({
        "success": True,
        "message": "Pago procesado",
        "order": {"id": order_id, "numero": numero, "total_formateado": total_formateado},
    })


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
        dual_orders=requests_data.get("dual_orders", []),
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

    if collection not in ("delivery_orders", "gestoria_requests", "dual_orders"):
        return jsonify({'success': False, 'message': 'Colección inválida.'}), 400
    if not request_id or not status:
        return jsonify({'success': False, 'message': 'Faltan datos.'}), 400

    requests_data = load_requests()
    updated = False
    for item in requests_data.get(collection, []):
        if item.get("id") == request_id:
            if collection == "dual_orders":
                item["estado"] = status
                if status in DUAL_ESTADO_A_PASO:
                    item["paso_actual"] = DUAL_ESTADO_A_PASO[status]
            else:
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