from flask import Flask, render_template, redirect, url_for, session, jsonify, request, Response
from jinja2 import FileSystemLoader
from werkzeug.security import check_password_hash, generate_password_hash
import json
import math
import os
import secrets
import tempfile
import uuid
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# NOTA: La clave secreta debe ser una cadena de bytes aleatoria en producción
# Para Canvas, usamos un valor placeholder.
app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("FLASK_COOKIE_SECURE", "0") == "1",
    MAX_CONTENT_LENGTH=1 * 1024 * 1024,
)
app.jinja_loader = FileSystemLoader(os.path.join(BASE_DIR, "templates"))
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
    {"id": 111, "nombre": "Vestido Negro", "seccion": "mujer", "subcategoria": "Vestidos",
     "precio": 28990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#1a1a1a", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Negro"],
     "color_fijo": True, "descripcion": "Vestido en color negro."},
    {"id": 109, "nombre": "Vestido Rojo", "seccion": "mujer", "subcategoria": "Vestidos",
     "precio": 28990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#a02040", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Rojo"],
     "color_fijo": True, "descripcion": "Vestido en color rojo."},
    {"id": 113, "nombre": "Vestido Azul", "seccion": "mujer", "subcategoria": "Vestidos",
     "precio": 28990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#202080", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Azul"],
     "color_fijo": True, "descripcion": "Vestido en color azul."},
    {"id": 115, "nombre": "Vestido Rosa", "seccion": "mujer", "subcategoria": "Vestidos",
     "precio": 28990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#c0a0a0", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Rosa"],
     "color_fijo": True, "descripcion": "Vestido en color rosa."},
    {"id": 112, "nombre": "Vestido Negro", "seccion": "mujer", "subcategoria": "Vestidos",
     "precio": 28990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#1a1a1a", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Negro"],
     "color_fijo": True, "descripcion": "Vestido en color negro."},
    {"id": 110, "nombre": "Vestido Rojo", "seccion": "mujer", "subcategoria": "Vestidos",
     "precio": 28990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#a02040", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Rojo"],
     "color_fijo": True, "descripcion": "Vestido en color rojo."},
    {"id": 114, "nombre": "Vestido Azul", "seccion": "mujer", "subcategoria": "Vestidos",
     "precio": 28990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#202080", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Azul"],
     "color_fijo": True, "descripcion": "Vestido en color azul."},
    {"id": 116, "nombre": "Vestido Rosa", "seccion": "mujer", "subcategoria": "Vestidos",
     "precio": 28990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#c0a0a0", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Rosa"],
     "color_fijo": True, "descripcion": "Vestido en color rosa."},

    {"id": 117, "nombre": "Top Negro", "seccion": "mujer", "subcategoria": "Tops",
     "precio": 9990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#1a1a1a", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Negro"],
     "color_fijo": True, "descripcion": "Top en color negro."},
    {"id": 119, "nombre": "Top Rojo", "seccion": "mujer", "subcategoria": "Tops",
     "precio": 9990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#a02040", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Rojo"],
     "color_fijo": True, "descripcion": "Top en color rojo."},
    {"id": 121, "nombre": "Top Blanco", "seccion": "mujer", "subcategoria": "Tops",
     "precio": 9990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#e8e4de", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Blanco"],
     "color_fijo": True, "descripcion": "Top en color blanco."},
    {"id": 123, "nombre": "Top Rosa", "seccion": "mujer", "subcategoria": "Tops",
     "precio": 9990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#c0a0a0", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Rosa"],
     "color_fijo": True, "descripcion": "Top en color rosa."},
    {"id": 118, "nombre": "Top Negro", "seccion": "mujer", "subcategoria": "Tops",
     "precio": 9990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#1a1a1a", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Negro"],
     "color_fijo": True, "descripcion": "Top en color negro."},
    {"id": 120, "nombre": "Top Rojo", "seccion": "mujer", "subcategoria": "Tops",
     "precio": 9990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#a02040", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Rojo"],
     "color_fijo": True, "descripcion": "Top en color rojo."},
    {"id": 122, "nombre": "Top Blanco", "seccion": "mujer", "subcategoria": "Tops",
     "precio": 9990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#e8e4de", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Blanco"],
     "color_fijo": True, "descripcion": "Top en color blanco."},
    {"id": 124, "nombre": "Top Rosa", "seccion": "mujer", "subcategoria": "Tops",
     "precio": 9990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#c0a0a0", "talles": ["XS", "S", "M", "L"], "colores_nombre": ["Rosa"],
     "color_fijo": True, "descripcion": "Top en color rosa."},

    {"id": 125, "nombre": "Jean Negro", "seccion": "mujer", "subcategoria": "Jeans",
     "precio": 25990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#1a1a1a", "talles": ["36", "38", "40", "42"], "colores_nombre": ["Negro"],
     "color_fijo": True, "descripcion": "Jean en color negro."},
    {"id": 127, "nombre": "Jean Azul", "seccion": "mujer", "subcategoria": "Jeans",
     "precio": 25990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#3f5b8c", "talles": ["36", "38", "40", "42"], "colores_nombre": ["Azul"],
     "color_fijo": True, "descripcion": "Jean en color azul."},
    {"id": 129, "nombre": "Jean Celeste", "seccion": "mujer", "subcategoria": "Jeans",
     "precio": 25990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#9db6d3", "talles": ["36", "38", "40", "42"], "colores_nombre": ["Celeste"],
     "color_fijo": True, "descripcion": "Jean en color celeste."},
    {"id": 131, "nombre": "Jean Gris", "seccion": "mujer", "subcategoria": "Jeans",
     "precio": 25990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#8a8d93", "talles": ["36", "38", "40", "42"], "colores_nombre": ["Gris"],
     "color_fijo": True, "descripcion": "Jean en color gris."},
    {"id": 126, "nombre": "Jean Negro", "seccion": "mujer", "subcategoria": "Jeans",
     "precio": 25990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#1a1a1a", "talles": ["36", "38", "40", "42"], "colores_nombre": ["Negro"],
     "color_fijo": True, "descripcion": "Jean en color negro."},
    {"id": 128, "nombre": "Jean Azul", "seccion": "mujer", "subcategoria": "Jeans",
     "precio": 25990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#3f5b8c", "talles": ["36", "38", "40", "42"], "colores_nombre": ["Azul"],
     "color_fijo": True, "descripcion": "Jean en color azul."},
    {"id": 130, "nombre": "Jean Celeste", "seccion": "mujer", "subcategoria": "Jeans",
     "precio": 25990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#9db6d3", "talles": ["36", "38", "40", "42"], "colores_nombre": ["Celeste"],
     "color_fijo": True, "descripcion": "Jean en color celeste."},
    {"id": 132, "nombre": "Jean Gris", "seccion": "mujer", "subcategoria": "Jeans",
     "precio": 25990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#8a8d93", "talles": ["36", "38", "40", "42"], "colores_nombre": ["Gris"],
     "color_fijo": True, "descripcion": "Jean en color gris."},

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
    {"id": 133, "nombre": "Conjunto Training Negro", "seccion": "deportivo", "subcategoria": "Conjuntos",
     "precio": 34990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#1a1a1a", "talles": ["S", "M", "L"], "colores_nombre": ["Negro"],
     "color_fijo": True, "descripcion": "Conjunto Training en color negro."},
    {"id": 135, "nombre": "Conjunto Training Gris", "seccion": "deportivo", "subcategoria": "Conjuntos",
     "precio": 34990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#8a8d93", "talles": ["S", "M", "L"], "colores_nombre": ["Gris"],
     "color_fijo": True, "descripcion": "Conjunto Training en color gris."},
    {"id": 137, "nombre": "Conjunto Training Azul", "seccion": "deportivo", "subcategoria": "Conjuntos",
     "precio": 34990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#3f5b8c", "talles": ["S", "M", "L"], "colores_nombre": ["Azul"],
     "color_fijo": True, "descripcion": "Conjunto Training en color azul."},
    {"id": 139, "nombre": "Conjunto Training Rosa", "seccion": "deportivo", "subcategoria": "Conjuntos",
     "precio": 34990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#c0a0a0", "talles": ["S", "M", "L"], "colores_nombre": ["Rosa"],
     "color_fijo": True, "descripcion": "Conjunto Training en color rosa."},
    {"id": 134, "nombre": "Conjunto Training Negro", "seccion": "deportivo", "subcategoria": "Conjuntos",
     "precio": 34990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#1a1a1a", "talles": ["S", "M", "L"], "colores_nombre": ["Negro"],
     "color_fijo": True, "descripcion": "Conjunto Training en color negro."},
    {"id": 136, "nombre": "Conjunto Training Gris", "seccion": "deportivo", "subcategoria": "Conjuntos",
     "precio": 34990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#8a8d93", "talles": ["S", "M", "L"], "colores_nombre": ["Gris"],
     "color_fijo": True, "descripcion": "Conjunto Training en color gris."},
    {"id": 138, "nombre": "Conjunto Training Azul", "seccion": "deportivo", "subcategoria": "Conjuntos",
     "precio": 34990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#3f5b8c", "talles": ["S", "M", "L"], "colores_nombre": ["Azul"],
     "color_fijo": True, "descripcion": "Conjunto Training en color azul."},
    {"id": 140, "nombre": "Conjunto Training Rosa", "seccion": "deportivo", "subcategoria": "Conjuntos",
     "precio": 34990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#c0a0a0", "talles": ["S", "M", "L"], "colores_nombre": ["Rosa"],
     "color_fijo": True, "descripcion": "Conjunto Training en color rosa."},
    {"id": 141, "nombre": "Short Running Negro", "seccion": "deportivo", "subcategoria": "Shorts",
     "precio": 14990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#1a1a1a", "talles": ["S", "M", "L"], "colores_nombre": ["Negro"],
     "color_fijo": True, "descripcion": "Short Running en color negro."},
    {"id": 143, "nombre": "Short Running Gris", "seccion": "deportivo", "subcategoria": "Shorts",
     "precio": 14990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#8a8d93", "talles": ["S", "M", "L"], "colores_nombre": ["Gris"],
     "color_fijo": True, "descripcion": "Short Running en color gris."},
    {"id": 145, "nombre": "Short Running Azul", "seccion": "deportivo", "subcategoria": "Shorts",
     "precio": 14990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#3f5b8c", "talles": ["S", "M", "L"], "colores_nombre": ["Azul"],
     "color_fijo": True, "descripcion": "Short Running en color azul."},
    {"id": 147, "nombre": "Short Running Rojo", "seccion": "deportivo", "subcategoria": "Shorts",
     "precio": 14990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#a02040", "talles": ["S", "M", "L"], "colores_nombre": ["Rojo"],
     "color_fijo": True, "descripcion": "Short Running en color rojo."},
    {"id": 142, "nombre": "Short Running Negro", "seccion": "deportivo", "subcategoria": "Shorts",
     "precio": 14990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#1a1a1a", "talles": ["S", "M", "L"], "colores_nombre": ["Negro"],
     "color_fijo": True, "descripcion": "Short Running en color negro."},
    {"id": 144, "nombre": "Short Running Gris", "seccion": "deportivo", "subcategoria": "Shorts",
     "precio": 14990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#8a8d93", "talles": ["S", "M", "L"], "colores_nombre": ["Gris"],
     "color_fijo": True, "descripcion": "Short Running en color gris."},
    {"id": 146, "nombre": "Short Running Azul", "seccion": "deportivo", "subcategoria": "Shorts",
     "precio": 14990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#3f5b8c", "talles": ["S", "M", "L"], "colores_nombre": ["Azul"],
     "color_fijo": True, "descripcion": "Short Running en color azul."},
    {"id": 148, "nombre": "Short Running Rojo", "seccion": "deportivo", "subcategoria": "Shorts",
     "precio": 14990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#a02040", "talles": ["S", "M", "L"], "colores_nombre": ["Rojo"],
     "color_fijo": True, "descripcion": "Short Running en color rojo."},
    {"id": 149, "nombre": "Zapatillas Blanco", "seccion": "deportivo", "subcategoria": "Calzado",
     "precio": 66990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#e8e4de", "talles": ["36", "37", "38", "39", "40"], "colores_nombre": ["Blanco"],
     "color_fijo": True, "descripcion": "Zapatillas en color blanco."},
    {"id": 151, "nombre": "Zapatillas Negro", "seccion": "deportivo", "subcategoria": "Calzado",
     "precio": 66990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#1a1a1a", "talles": ["36", "37", "38", "39", "40"], "colores_nombre": ["Negro"],
     "color_fijo": True, "descripcion": "Zapatillas en color negro."},
    {"id": 153, "nombre": "Zapatillas Gris", "seccion": "deportivo", "subcategoria": "Calzado",
     "precio": 66990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#8a8d93", "talles": ["36", "37", "38", "39", "40"], "colores_nombre": ["Gris"],
     "color_fijo": True, "descripcion": "Zapatillas en color gris."},
    {"id": 155, "nombre": "Zapatillas Rosa", "seccion": "deportivo", "subcategoria": "Calzado",
     "precio": 66990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#c0a0a0", "talles": ["36", "37", "38", "39", "40"], "colores_nombre": ["Rosa"],
     "color_fijo": True, "descripcion": "Zapatillas en color rosa."},
    {"id": 150, "nombre": "Zapatillas Blanco", "seccion": "deportivo", "subcategoria": "Calzado",
     "precio": 66990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#e8e4de", "talles": ["36", "37", "38", "39", "40"], "colores_nombre": ["Blanco"],
     "color_fijo": True, "descripcion": "Zapatillas en color blanco."},
    {"id": 152, "nombre": "Zapatillas Negro", "seccion": "deportivo", "subcategoria": "Calzado",
     "precio": 66990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#1a1a1a", "talles": ["36", "37", "38", "39", "40"], "colores_nombre": ["Negro"],
     "color_fijo": True, "descripcion": "Zapatillas en color negro."},
    {"id": 154, "nombre": "Zapatillas Gris", "seccion": "deportivo", "subcategoria": "Calzado",
     "precio": 66990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#8a8d93", "talles": ["36", "37", "38", "39", "40"], "colores_nombre": ["Gris"],
     "color_fijo": True, "descripcion": "Zapatillas en color gris."},
    {"id": 156, "nombre": "Zapatillas Rosa", "seccion": "deportivo", "subcategoria": "Calzado",
     "precio": 66990, "descuento": None, "precio_original": None, "es_novedad": False,
     "color_media": "#c0a0a0", "talles": ["36", "37", "38", "39", "40"], "colores_nombre": ["Rosa"],
     "color_fijo": True, "descripcion": "Zapatillas en color rosa."},
]

DUAL_IMAGENES = {
    101: "/static/img/dual/categorias/vestidos.jpg",
    102: "/static/img/dual/Nueva%20carpeta/top.jpg",
    103: "/static/img/dual/categorias/jeans.jpg",
    104: "/static/img/dual/Nueva%20carpeta/conjunto.jpg",
    105: "/static/img/dual/categorias/accesorios.jpg",
    106: "/static/img/dual/Nueva%20carpeta/campera.jpg",
    107: "/static/img/dual/categorias/deportivo.jpg",
    108: "/static/img/dual/Nueva%20carpeta/top.jpg",
    201: "/static/img/dual/Nueva%20carpeta/top.jpg",
    202: "/static/img/dual/productos/202.jpg",
    203: "/static/img/dual/productos/203.jpg",
    204: "/static/img/dual/productos/204.jpg",
    205: "/static/img/dual/productos/205.jpg",
    206: "/static/img/dual/productos/206.jpg",
    207: "/static/img/dual/productos/207.jpg",
    208: "/static/img/dual/Nueva%20carpeta/mochila.jpg",
}

# Imágenes propias de los productos: static/img/dual/productos/<id>.jpg (o png/webp)
# Si no existe el archivo, se usa el link de DUAL_IMAGENES como respaldo.
DUAL_PROD_IMG_DIR = os.path.join(BASE_DIR, "static", "img", "dual", "productos")


def dual_imagen_producto(pid):
    for ext in ("jpg", "jpeg", "png", "webp", "avif"):
        ruta = os.path.join(DUAL_PROD_IMG_DIR, f"{pid}.{ext}")
        if os.path.isfile(ruta):
            return f"/static/img/dual/productos/{pid}.{ext}?v={int(os.path.getmtime(ruta))}"
    return DUAL_IMAGENES.get(pid)


for producto in dual_productos:
    producto["imagen"] = dual_imagen_producto(producto["id"])

# Stock de demostración por color y talle. Cero significa "sin stock".
DUAL_STOCK_AGOTADO = {
    101: [("Beige", "L")],
    102: [("Terracota", "XS"), ("Blanco", "L")],
    103: [("Azul", "42")],
    104: [("Rosa viejo", "S")],
    105: [("Crudo", "S")],
    106: [("Camel", "XL")],
    107: [("Ladrillo", "XS")],
    108: [("Rosa", "L")],
    201: [("Gris", "S")],
    202: [("Negro", "XS")],
    203: [("Azul", "XL")],
    204: [("Negro", "S")],
    205: [("Gris", "XL")],
    206: [("Negro", "L")],
    207: [("Blanco/Negro", "40")],
    208: [],
}

for producto in dual_productos:
    agotados = set(DUAL_STOCK_AGOTADO.get(producto["id"], []))
    producto["stock"] = {
        color: {
            talle: 0 if (color, talle) in agotados else 5
            for talle in producto["talles"]
        }
        for color in producto["colores_nombre"]
    }

DUAL_CATEGORIA_CONFIG = {
    "mujer": {
        "titulo": "Indumentaria Femenina", "eyebrow": "INDUMENTARIA",
        "copy": "Descubrí las últimas tendencias en ropa y accesorios.",
        "subcategorias": ["Vestidos", "Tops", "Jeans", "Conjuntos", "Faldas", "Blusas", "Accesorios"],
    },
    "deportivo": {
        "titulo": "Ropa Deportiva", "eyebrow": "ROPA",
        "copy": "Tecnología, confort y diseño para tu mejor rendimiento.",
        "subcategorias": ["Calzas", "Tops", "Shorts", "Buzos", "Camperas", "Conjuntos", "Calzado", "Accesorios"],
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

# Cada categoría destacada:
#   slug          -> nombre del archivo de imagen (static/img/dual/categorias/<slug>.jpg|png|webp)
#   seccion       -> sección a la que pertenece (mujer / deportivo)
#   subcategorias -> qué productos muestra al hacer click
DUAL_CATEGORIAS_DESTACADAS = [
    {"slug": "vestidos", "imagen": "vestidos.jpg", "nombre": "Vestidos", "seccion": "mujer",
        "subcategorias": ["Vestidos"], "product_ids": [111, 109, 113, 115, 112, 110, 114, 116],
     "copy": "Vestidos para todos los días y para las ocasiones especiales."},
    {"slug": "tops", "imagen": "top.jpg", "nombre": "Tops", "seccion": "mujer",
     "subcategorias": ["Tops"], "product_ids": [117, 119, 121, 123, 118, 120, 122, 124],
     "copy": "Tops básicos y versátiles para combinar con todo."},
    {"slug": "jeans", "imagen": "jeans.jpg", "nombre": "Jeans", "seccion": "mujer",
     "subcategorias": ["Jeans"], "product_ids": [125, 127, 129, 131, 126, 128, 130, 132],
     "copy": "Jeans en cortes y calces para cada estilo."},
    {"slug": "training", "imagen": "training.jpf.jpg", "nombre": "Training", "seccion": "deportivo",
     "subcategorias": ["Conjuntos", "Tops", "Calzas"], "product_ids": [133, 135, 137, 139, 134, 136, 138, 140],
     "copy": "Todo lo que necesitás para entrenar con comodidad."},
    {"slug": "running", "imagen": "runing.jpg", "nombre": "Running", "seccion": "deportivo",
     "subcategorias": ["Shorts", "Camperas"], "product_ids": [141, 143, 145, 147, 142, 144, 146, 148],
     "copy": "Prendas livianas y técnicas para salir a correr."},
    {"slug": "calzado", "imagen": "calzado.jpg", "nombre": "Calzado", "seccion": "deportivo",
     "subcategorias": ["Calzado"], "product_ids": [149, 151, 153, 155, 150, 152, 154, 156],
     "copy": "Zapatillas con amortiguación para cada entrenamiento."},
]

# Carpetas donde pueden estar las imágenes de los círculos.
DUAL_CAT_IMG_DIRS = (
    os.path.join(BASE_DIR, "static", "img", "dual", "categorias"),
    os.path.join(BASE_DIR, "static", "img", "dual", "Nueva carpeta"),
)
DUAL_CAT_IMG_EXTS = ("jpg", "jpeg", "png", "webp", "avif")


def dual_imagen_categoria(slug, archivo=None):
    """Devuelve la URL de la imagen de categoría si existe, o None."""
    archivos = [archivo] if archivo else []
    archivos.extend(f"{slug}.{ext}" for ext in DUAL_CAT_IMG_EXTS)
    for directorio in DUAL_CAT_IMG_DIRS:
        try:
            existentes = {nombre.lower(): nombre for nombre in os.listdir(directorio)}
        except OSError:
            continue
        for candidato in archivos:
            nombre_archivo = existentes.get(candidato.lower())
            if nombre_archivo:
                ruta = os.path.join(directorio, nombre_archivo)
                archivo_static = os.path.relpath(ruta, os.path.join(BASE_DIR, "static")).replace(os.sep, "/")
                # ?v=<fecha> hace que el navegador recargue la imagen si la reemplazás
                return url_for("static", filename=archivo_static,
                               v=int(os.path.getmtime(ruta)))
    return None


def dual_categorias_destacadas():
    """Lista lista para el template: con imagen (si existe) y link a su contenido."""
    return [
        dict(
            c,
            imagen=dual_imagen_categoria(c["slug"], c.get("imagen")),
            url=url_for("dual_categoria", categoria=c["seccion"],
                        coleccion=c["slug"], _anchor="catalogo"),
        )
        for c in DUAL_CATEGORIAS_DESTACADAS
    ]

DUAL_TALLES = ["XS", "S", "M", "L", "XL"]
DUAL_COLORES_HEX = ["#1a1a1a", "#c9a6a1", "#7c8ba3", "#e6c7ba", "#3d4a63"]
DUAL_COLOR_HEX_BY_NAME = {
    "Negro": "#1a1a1a", "Blanco": "#f5f5f2", "Beige": "#e6c7ba",
    "Terracota": "#b86f58", "Rojo": "#a02040", "Azul": "#202080", "Rosa": "#c0a0a0",
    "Rosa viejo": "#c9a6a1",
    "Crudo": "#ded3c4", "Camel": "#b7a99c", "Ladrillo": "#a9764f",
    "Rosa": "#e0a8a0", "Gris": "#8b9099", "Blanco/Negro": "#d8d8d4",
}

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
        },
        {
            "username": "cliente_inmo",
            "password_hash": generate_password_hash("inmo123"),
            "role": "cliente",
            "sector": "inmo",
            "display_name": "Juan Pérez"
        }
    ]
}

default_requests = {
    "delivery_orders": [],
    "gestoria_requests": [],
    "dual_orders": [],
    "inmo_contacts": [],
    "inmo_tasaciones": [],
    "inmo_visitas": [],
    "inmo_compras": []
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

inmo_propiedades = [
    {
        "id": 1,
        "nombre": "Departamento en Palermo",
        "operacion": "venta",
        "precio": 420000,
        "ubicacion": "Palermo",
        "zona": "Palermo",
        "tipo": "Departamento",
        "dormitorios": 2,
        "banos": 2,
        "superficie": 72,
        "cocheras": 1,
        "descripcion": "Excelente departamento con luz natural y amenities modernos.",
        "caracteristicas": ["Balcony", "Terraza", "Luz natural", "Cocina equipada"],
        "color_media": "linear-gradient(135deg, #dfe8ff, #b4c8ff)",
        "imagen": "img.departamento1.jpg",
        "imagenes": [
            "img.departamento1.jpg",
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1200&q=80"
        ]
    },
    {
        "id": 2,
        "nombre": "Casa en Belgrano",
        "operacion": "venta",
        "precio": 680000,
        "ubicacion": "Belgrano",
        "zona": "Belgrano",
        "tipo": "Casa",
        "dormitorios": 4,
        "banos": 3,
        "superficie": 180,
        "cocheras": 2,
        "descripcion": "Casa familiar con jardín, excelente estado y mucha luminosidad.",
        "caracteristicas": ["Jardín", "Patio", "Cochera doble", "Living comedor"],
        "color_media": "linear-gradient(135deg, #e8ddcc, #d8c7b0)",
        "imagen": "img.casa2.jpg",
        "imagenes": [
            "img.casa2.jpg",
            "https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80"
        ]
    },
    {
        "id": 3,
        "nombre": "PH en Villa Crespo",
        "operacion": "alquiler",
        "precio": 1650,
        "ubicacion": "Villa Crespo",
        "zona": "Villa Crespo",
        "tipo": "PH",
        "dormitorios": 3,
        "banos": 2,
        "superficie": 95,
        "cocheras": 1,
        "descripcion": "PH muy luminoso con vista tranquila, ideal para vivir en una zona muy conectada.",
        "caracteristicas": ["Vista", "Luz natural", "Lavarropas", "Balcón"],
        "color_media": "linear-gradient(135deg, #d9f0d6, #b6d7b4)",
        "imagen": "img.departamento3.jpg",
        "imagenes": [
            "img.departamento3.jpg",
            "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=1200&q=80"
        ]
    },
    {
        "id": 4,
        "nombre": "Local comercial en Recoleta",
        "operacion": "alquiler",
        "precio": 2300,
        "ubicacion": "Recoleta",
        "zona": "Recoleta",
        "tipo": "Local",
        "dormitorios": 0,
        "banos": 1,
        "superficie": 58,
        "cocheras": 0,
        "descripcion": "Local comercial con alta visibilidad y excelente ubicación comercial.",
        "caracteristicas": ["Frente comercial", "Excelente tránsito", "Patio interno"],
        "color_media": "linear-gradient(135deg, #f8e2d8, #edd0c2)",
        "imagen": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=900&q=80",
        "imagenes": [
            "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1460317442991-0ec209397118?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1448630360428-65456885c650?auto=format&fit=crop&w=1200&q=80"
        ]
    },
    {
        "id": 5,
        "nombre": "Departamento en Caballito",
        "operacion": "venta",
        "precio": 310000,
        "ubicacion": "Caballito",
        "zona": "Caballito",
        "tipo": "Departamento",
        "dormitorios": 2,
        "banos": 1,
        "superficie": 64,
        "cocheras": 1,
        "descripcion": "Ideal para inversión o primera vivienda, muy bien conectado y con amenities.",
        "caracteristicas": ["Piso alto", "Laundry", "Esquina", "Muy luminoso"],
        "color_media": "linear-gradient(135deg, #dfe9e2, #c5d6cf)",
        "imagen": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=900&q=80",
        "imagenes": [
            "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1200&q=80"
        ]
    },
    {
        "id": 6,
        "nombre": "Terreno en Lanús",
        "operacion": "venta",
        "precio": 190000,
        "ubicacion": "Lanús",
        "zona": "Lanús",
        "tipo": "Terreno",
        "dormitorios": 0,
        "banos": 0,
        "superficie": 320,
        "cocheras": 0,
        "descripcion": "Terreno amplio en zona residencial con buen potencial de desarrollo.",
        "caracteristicas": ["Lote amplio", "Zona residencial", "Fácil acceso"],
        "color_media": "linear-gradient(135deg, #ccdfd9, #b3cdc2)",
        "imagen": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=900&q=80",
        "imagenes": [
            "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1479839672679-a46483c0e7c8?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1460317442991-0ec209397118?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1448630360428-65456885c650?auto=format&fit=crop&w=1200&q=80"
        ]
    },
]

inmo_zonas = [
    {"nombre": "Palermo", "precio_prom": 850000},
    {"nombre": "Belgrano", "precio_prom": 940000},
    {"nombre": "Villa Crespo", "precio_prom": 610000},
    {"nombre": "Recoleta", "precio_prom": 780000},
    {"nombre": "Caballito", "precio_prom": 490000},
    {"nombre": "Lanús", "precio_prom": 320000},
]

inmo_emprendimientos_data = [
    {
        "nombre": "Asteras Residencial", 
        "ubicacion": "Palermo", 
        "desde": 210000, 
        "color_media": "linear-gradient(135deg, #1d3357, #6d8bb0)",
        "imagen": "img4.jpg"
    },
    {
        "nombre": "Torre Sol", 
        "ubicacion": "Belgrano", 
        "desde": 260000, 
        "color_media": "linear-gradient(135deg, #8d6e63, #d4b7a3)",
        "imagen": "img.casa2.jpg"
    },
    {
        "nombre": "Marea Norte", 
        "ubicacion": "Dock Sud", 
        "desde": 185000, 
        "color_media": "linear-gradient(135deg, #2d6a4f, #9cc5a1)",
        "imagen": "img.departamento3.jpg"
    },
]

inmo_servicios = [
    {"titulo": "Venta y alquiler", "descripcion": "Asesoramiento completo para comprar, vender o alquilar con seguridad.", "icono": "fa-house"},
    {"titulo": "Tasación online", "descripcion": "Estimaciones rápidas con criterios de mercado actualizados.", "icono": "fa-chart-line"},
    {"titulo": "Gestión integral", "descripcion": "Seguimiento de documentación, trámites y coordinación de visitas.", "icono": "fa-file-contract"},
    {"titulo": "Inversión", "descripcion": "Análisis de rentabilidad y oportunidades de capitalización.", "icono": "fa-sack-dollar"},
]

inmo_novedades = [
    {"titulo": "Cómo elegir la zona ideal según presupuesto", "resumen": "Guía rápida para decidir entre barrios y precios.", "color_media": "linear-gradient(135deg, #d8e7ff, #b7c8f6)"},
    {"titulo": "Oportunidades en alquiler para familias", "resumen": "Las mejores opciones en zonas con escuelas y transporte.", "color_media": "linear-gradient(135deg, #d5f0df, #bfe5c7)"},
    {"titulo": "Tendencias del mercado inmobiliario 2026", "resumen": "Qué está creciendo y dónde conviene invertir ahora.", "color_media": "linear-gradient(135deg, #f9e7d1, #efd0a3)"},
]


def load_json(path, default_value):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return default_value


def save_json(path, payload):
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=directory,
            prefix=".tmp-",
            suffix=".json",
            delete=False,
        ) as file:
            temporary_path = file.name
            json.dump(payload, file, indent=2, ensure_ascii=False)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.unlink(temporary_path)


def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        save_json(USERS_FILE, default_users)
    else:
        users_payload = load_json(USERS_FILE, default_users)
        users = users_payload.get("users", [])
        existing = {user.get("username") for user in users if user.get("username")}
        added = False
        for user in default_users.get("users", []):
            username = user.get("username")
            if username and username not in existing:
                users.append(user)
                existing.add(username)
                added = True
        if added:
            users_payload["users"] = users
            save_json(USERS_FILE, users_payload)
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
    data.setdefault("inmo_contacts", [])
    data.setdefault("inmo_tasaciones", [])
    data.setdefault("inmo_visitas", [])
    data.setdefault("inmo_compras", [])
    return data


def save_requests(payload):
    save_json(REQUESTS_FILE, payload)


def get_current_user():
    user = session.get("user")
    if not isinstance(user, dict):
        session.pop("user", None)
        return None
    if not user.get("username"):
        session.pop("user", None)
        return None
    return user


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

    sector = (user.get("sector") or "").strip()
    if sector == "gestoria":
        return redirect(url_for("gestoria"))
    if sector == "dual":
        return redirect(url_for("dual_home"))
    if sector == "delivery":
        return redirect(url_for("delivery"))
    if sector == "inmo":
        return redirect(url_for("inmo_home"))

    session.pop("user", None)
    return redirect(url_for("login"))


@app.context_processor
def inject_user_context():
    current_user = get_current_user()
    return {
        "current_user": current_user,
        "is_logged_in": current_user is not None,
        "is_admin": bool(current_user and current_user.get("role") == "admin"),
        "user_sector": current_user.get("sector") if current_user else None,
    }


@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return response


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


def inmo_require_sector(current_user):
    """Verifica acceso al sector InmoControl."""
    if not current_user:
        return redirect(url_for("login"))
    if current_user.get("role") != "admin" and current_user.get("sector") not in ("inmo", "admin"):
        return redirect_for_user(current_user)
    return None


def inmo_get_favoritos():
    favoritos = session.get("inmo_favoritos", [])
    if not isinstance(favoritos, list):
        session["inmo_favoritos"] = []
        return []
    return favoritos


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
    destacados += [p for p in dual_productos if not p.get("es_novedad") and p["id"] != 101][:1]
    return render_template(
        "dual_index.html",
        categorias_destacadas=dual_categorias_destacadas(),
        destacados=destacados,
        color_hex=DUAL_COLOR_HEX_BY_NAME,
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

    # Si viene de un círculo de "Categorías destacadas" (?coleccion=vestidos)
    slug_coleccion = (request.args.get("coleccion") or "").lower()
    coleccion = next(
        (c for c in DUAL_CATEGORIAS_DESTACADAS
         if c["slug"] == slug_coleccion and c["seccion"] == categoria),
        None,
    )

    if categoria == "mujer":
        productos_filtrados = [p for p in dual_productos if p["seccion"] == "mujer"]
    elif categoria == "deportivo":
        productos_filtrados = [p for p in dual_productos if p["seccion"] == "deportivo"]
    elif categoria == "ofertas":
        productos_filtrados = [p for p in dual_productos if p.get("descuento")]
    else:  # novedades
        productos_filtrados = [p for p in dual_productos if p.get("es_novedad")]
    subcategorias_seleccionadas = request.args.getlist("subcategoria")
    talles_seleccionados = request.args.getlist("talle")
    colores_seleccionados = request.args.getlist("color")
    precio_maximo = request.args.get("precio_max", type=int)

    # La colección preselecciona sus subcategorías (y se ven tildadas en el filtro)
    if coleccion and not subcategorias_seleccionadas:
        subcategorias_seleccionadas = list(coleccion["subcategorias"])

    if subcategorias_seleccionadas:
        productos_filtrados = [
            p for p in productos_filtrados if p["subcategoria"] in subcategorias_seleccionadas
        ]
    if coleccion and coleccion.get("product_ids"):
        productos_filtrados = [
            p for p in productos_filtrados if p["id"] in coleccion["product_ids"]
        ]
    if talles_seleccionados:
        productos_filtrados = [
            p for p in productos_filtrados if any(t in p["talles"] for t in talles_seleccionados)
        ]
    if colores_seleccionados:
        productos_filtrados = [
            p for p in productos_filtrados if any(c in p["colores_nombre"] for c in colores_seleccionados)
        ]
    if precio_maximo is not None:
        productos_filtrados = [p for p in productos_filtrados if p["precio"] <= precio_maximo]

    colores_disponibles = sorted({
        color for producto in productos_filtrados for color in producto["colores_nombre"]
    })

    return render_template(
        "dual_categoria.html",
        categoria=categoria,
        titulo=coleccion["nombre"] if coleccion else config["titulo"],
        eyebrow=config["titulo"] if coleccion else config["eyebrow"],
        copy=coleccion["copy"] if coleccion else config["copy"],
        coleccion=coleccion,
        seccion_titulo=config["titulo"],
        subcategorias=config["subcategorias"],
        talles=DUAL_TALLES,
        colores=colores_disponibles,
        color_hex=DUAL_COLOR_HEX_BY_NAME,
        productos=productos_filtrados,
        filtros={
            "subcategoria": subcategorias_seleccionadas,
            "talle": talles_seleccionados,
            "color": colores_seleccionados,
            "precio_max": precio_maximo or 100000,
        },
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
        color_hex=DUAL_COLOR_HEX_BY_NAME,
        stock_json=json.dumps(producto["stock"], ensure_ascii=False),
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
        "imagen": producto.get("imagen"),
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


@app.route("/dual/pedido/<order_id>/comprobante")
def dual_pedido_comprobante(order_id):
    """Muestra el comprobante persistido de un pedido confirmado."""
    current_user = get_current_user()
    blocked = dual_require_sector(current_user)
    if blocked:
        return blocked

    requests_data = load_requests()
    pedido = next((o for o in requests_data.get("dual_orders", []) if o["id"] == order_id), None)
    if not pedido:
        return redirect(url_for("dual_pedidos"))
    if current_user.get("role") != "admin" and pedido.get("username") != current_user.get("username"):
        return redirect(url_for("dual_pedidos"))

    return render_template(
        "dual_comprobante.html",
        pedido=pedido,
        active_nav="",
        dual_cart_count=0,
        page_title="Comprobante de compra",
    )


@app.route("/api/dual/pedido", methods=["POST"])
def api_dual_pedido():
    """Confirma la compra: guarda el pedido y devuelve datos del comprobante."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({"success": False, "message": "Debe iniciar sesión."}), 401

    data = request.get_json() or {}
    item_data = data.get("item") or {}
    envio = data.get("envio") or {}
    metodo_pago = data.get("metodo_pago", "tarjeta")

    producto = get_dual_product_by_id(item_data.get("product_id"))
    if not producto:
        return jsonify({"success": False, "message": "Datos de compra incompletos."}), 400
    try:
        cantidad = int(item_data.get("cantidad", 1))
    except (TypeError, ValueError):
        cantidad = 0
    if cantidad < 1 or cantidad > 10:
        return jsonify({"success": False, "message": "La cantidad seleccionada no es válida."}), 400
    talla = item_data.get("talla")
    color = item_data.get("color")
    if talla not in producto["talles"] or color not in producto["colores_nombre"]:
        return jsonify({"success": False, "message": "La variante seleccionada no es válida."}), 400
    stock_disponible = producto.get("stock", {}).get(color, {}).get(talla, 0)
    if cantidad > stock_disponible:
        return jsonify({"success": False, "message": "El talle y color seleccionados no tienen stock suficiente."}), 400
    if not envio.get("nombre") or not envio.get("email") or not envio.get("calle"):
        return jsonify({"success": False, "message": "Completá los datos de envío."}), 400
    if metodo_pago not in {"tarjeta", "mercadopago", "transferencia", "efectivo"}:
        return jsonify({"success": False, "message": "El método de pago no es válido."}), 400

    item = {
        "product_id": producto["id"],
        "nombre": producto["nombre"],
        "color_media": producto["color_media"],
        "imagen": producto.get("imagen"),
        "talla": talla,
        "color": color,
        "cantidad": cantidad,
        "precio_unitario": producto["precio"],
        "subtotal": producto["precio"] * cantidad,
    }
    envio_costo = DUAL_ENVIO_COSTO
    total = item["subtotal"] + envio_costo

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

    producto["stock"][color][talla] -= cantidad

    total_formateado = "$" + "{:,.0f}".format(total).replace(",", ".")

    return jsonify({
        "success": True,
        "message": "Pago procesado",
        "order": {
            "id": order_id,
            "numero": numero,
            "total_formateado": total_formateado,
            "receipt_url": url_for("dual_pedido_comprobante", order_id=order_id),
        },
    })


@app.route("/inmo")
@app.route("/inmo/home")
def inmo_home():
    current_user = get_current_user()
    blocked = inmo_require_sector(current_user)
    if blocked:
        return blocked

    return render_template(
        "inmo/inmo.index",
        propiedades=inmo_propiedades[:4],
        zonas=inmo_zonas,
        emprendimientos=inmo_emprendimientos_data,
        servicios=inmo_servicios,
        novedades=inmo_novedades,
        active_nav="inicio",
        inmo_favoritos=inmo_get_favoritos(),
        page_title="InmoControl",
    )


@app.route("/inmo/registro", methods=["GET", "POST"])
def inmo_registro():
    current_user = get_current_user()
    if current_user:
        return redirect_for_user(current_user)

    error_message = None
    if request.method == "POST":
        display_name = (request.form.get("display_name") or "").strip()
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if not display_name or not username or not password:
            error_message = "Completá todos los campos."
        else:
            users = load_users()
            if any(u.get("username") == username for u in users):
                error_message = "Ese usuario ya existe."
            else:
                users.append({
                    "username": username,
                    "password_hash": generate_password_hash(password),
                    "role": "cliente",
                    "sector": "inmo",
                    "display_name": display_name,
                })
                save_json(USERS_FILE, {"users": users})
                session["user"] = {
                    "username": username,
                    "display_name": display_name,
                    "role": "cliente",
                    "sector": "inmo",
                }
                return redirect(url_for("inmo_home"))

    return render_template("inmo/inmo_resgistro.html", error_message=error_message)


@app.route("/inmo/listado/<operacion>")
def inmo_listado(operacion):
    current_user = get_current_user()
    blocked = inmo_require_sector(current_user)
    if blocked:
        return blocked

    operacion = operacion.lower()
    if operacion not in {"comprar", "alquilar"}:
        return redirect(url_for("inmo_home"))

    propiedades = [p for p in inmo_propiedades if p.get("operacion") == ("venta" if operacion == "comprar" else "alquiler")]
    filtro_ubicacion = request.args.get("ubicacion")
    filtro_tipo = request.args.get("tipo")
    if filtro_ubicacion:
        propiedades = [p for p in propiedades if p.get("ubicacion") == filtro_ubicacion]
    if filtro_tipo:
        propiedades = [p for p in propiedades if p.get("tipo") == filtro_tipo]

    return render_template(
        "inmo/inmo_listado.html",
        titulo="Comprar propiedades" if operacion == "comprar" else "Alquilar propiedades",
        operacion=operacion,
        propiedades=propiedades,
        zonas=inmo_zonas,
        tipos=sorted({p.get("tipo") for p in inmo_propiedades if p.get("tipo")}),
        ambientes=["1", "2", "3", "4", "5+"],
        filtro_ubicacion=filtro_ubicacion,
        filtro_tipo=filtro_tipo,
        active_nav=operacion,
        inmo_favoritos=inmo_get_favoritos(),
        page_title="InmoControl",
    )


@app.route("/inmo/propiedad/<int:property_id>")
def inmo_propiedad(property_id):
    current_user = get_current_user()
    blocked = inmo_require_sector(current_user)
    if blocked:
        return blocked

    propiedad = next((p for p in inmo_propiedades if p["id"] == property_id), None)
    if not propiedad:
        return redirect(url_for("inmo_home"))

    return render_template(
        "inmo/inmo_propiedad.html",
        propiedad=propiedad,
        inmo_favoritos=inmo_get_favoritos(),
        active_nav="comprar",
        page_title=propiedad["nombre"],
    )


@app.route("/inmo/comprar/<int:property_id>")
def inmo_comprar(property_id):
    current_user = get_current_user()
    blocked = inmo_require_sector(current_user)
    if blocked:
        return blocked

    propiedad = next((p for p in inmo_propiedades if p["id"] == property_id), None)
    if not propiedad:
        return redirect(url_for("inmo_home"))

    return render_template(
        "inmo/inmo_compra.html",
        propiedad=propiedad,
        inmo_favoritos=inmo_get_favoritos(),
        active_nav="comprar",
        page_title=f"Comprar — {propiedad['nombre']}",
    )


@app.route("/inmo/emprendimientos")
def inmo_emprendimientos():
    current_user = get_current_user()
    blocked = inmo_require_sector(current_user)
    if blocked:
        return blocked
    return render_template("inmo/inmo_emprendimiento.html", emprendimientos=inmo_emprendimientos_data, inmo_favoritos=inmo_get_favoritos(), active_nav="emprendimientos", page_title="Emprendimientos")


@app.route("/inmo/mapa")
def inmo_mapa():
    current_user = get_current_user()
    blocked = inmo_require_sector(current_user)
    if blocked:
        return blocked
    return render_template("inmo/inmo_mapa.html", zonas=inmo_zonas, inmo_favoritos=inmo_get_favoritos(), active_nav="comprar", page_title="Mapa inmobiliario")


@app.route("/inmo/cuenta")
def inmo_cuenta():
    current_user = get_current_user()
    blocked = inmo_require_sector(current_user)
    if blocked:
        return blocked

    requests_data = load_requests()
    favoritos = [p for p in inmo_propiedades if p["id"] in inmo_get_favoritos()]
    username = current_user.get("username")
    consultas = [item for item in requests_data.get("inmo_contacts", []) if item.get("username") == username]
    tasaciones = [item for item in requests_data.get("inmo_tasaciones", []) if item.get("username") == username]
    visitas = [item for item in requests_data.get("inmo_visitas", []) if item.get("username") == username]
    compras = [item for item in requests_data.get("inmo_compras", []) if item.get("username") == username]
    return render_template(
        "inmo/inmo_cuenta.html",
        propiedades_guardadas=favoritos,
        consultas=consultas,
        tasaciones=tasaciones,
        visitas=visitas,
        compras=compras,
        inmo_favoritos=inmo_get_favoritos(),
    )


@app.route("/inmo/tasacion")
def inmo_tasacion():
    current_user = get_current_user()
    blocked = inmo_require_sector(current_user)
    if blocked:
        return blocked
    return render_template("inmo/inmo_tasacion.html", inmo_favoritos=inmo_get_favoritos(), active_nav="tasacion", page_title="Tasación")


@app.route("/inmo/servicios")
def inmo_servicios_view():
    current_user = get_current_user()
    blocked = inmo_require_sector(current_user)
    if blocked:
        return blocked
    return render_template("inmo/inmo_servicios.html", servicios=inmo_servicios, inmo_favoritos=inmo_get_favoritos(), active_nav="servicios", page_title="Servicios")


@app.route("/inmo/novedades")
def inmo_novedades_view():
    current_user = get_current_user()
    blocked = inmo_require_sector(current_user)
    if blocked:
        return blocked
    return render_template("inmo/inmo_novedades.html", novedades=inmo_novedades, inmo_favoritos=inmo_get_favoritos(), active_nav="novedades", page_title="Novedades")


@app.route("/inmo/contacto")
def inmo_contacto():
    current_user = get_current_user()
    blocked = inmo_require_sector(current_user)
    if blocked:
        return blocked
    return render_template("inmo/inmo_contacto.html", inmo_favoritos=inmo_get_favoritos(), page_title="Contacto")


@app.route("/api/inmo/favorito", methods=["POST"])
def api_inmo_favorito():
    current_user = get_current_user()
    if not current_user:
        return jsonify({"success": False, "message": "Debe iniciar sesión."}), 401

    data = request.get_json(silent=True) or {}
    try:
        property_id = int(data.get("property_id"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Falta la propiedad."}), 400
    if not any(property_item["id"] == property_id for property_item in inmo_propiedades):
        return jsonify({"success": False, "message": "Propiedad no encontrada."}), 404

    favoritos = inmo_get_favoritos()
    if property_id in favoritos:
        favoritos = [pid for pid in favoritos if pid != property_id]
        guardado = False
    else:
        favoritos.append(property_id)
        guardado = True

    session["inmo_favoritos"] = favoritos
    return jsonify({"success": True, "guardado": guardado, "favoritos": favoritos})


@app.route("/api/inmo/contacto", methods=["POST"])
def api_inmo_contacto():
    current_user = get_current_user()
    if not current_user:
        return jsonify({"success": False, "message": "Debe iniciar sesión."}), 401

    data = request.get_json(silent=True) or {}
    property_id = data.get("property_id")
    if property_id not in (None, ""):
        try:
            property_id = int(property_id)
        except (TypeError, ValueError):
            return jsonify({"success": False, "message": "Propiedad no válida."}), 400
        if not any(property_item["id"] == property_id for property_item in inmo_propiedades):
            return jsonify({"success": False, "message": "Propiedad no encontrada."}), 404
    payload = {
        "id": str(uuid.uuid4()),
        "username": current_user.get("username"),
        "nombre": (data.get("nombre") or "").strip(),
        "email": (data.get("email") or "").strip(),
        "telefono": (data.get("telefono") or "").strip(),
        "mensaje": (data.get("mensaje") or data.get("consulta") or "").strip(),
        "property_id": property_id,
        "status": "nuevo",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    if not payload["nombre"] or not payload["email"]:
        return jsonify({"success": False, "message": "Completá nombre y email."}), 400

    requests_data = load_requests()
    requests_data["inmo_contacts"].append(payload)
    save_requests(requests_data)
    return jsonify({"success": True, "message": "Consulta enviada con éxito."})


@app.route("/api/inmo/visita", methods=["POST"])
def api_inmo_visita():
    current_user = get_current_user()
    if not current_user:
        return jsonify({"success": False, "message": "Debe iniciar sesión."}), 401

    data = request.get_json(silent=True) or {}
    try:
        property_id = int(data.get("property_id"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Falta la propiedad."}), 400
    if not any(property_item["id"] == property_id for property_item in inmo_propiedades):
        return jsonify({"success": False, "message": "Propiedad no encontrada."}), 404

    requests_data = load_requests()
    requests_data["inmo_visitas"].append({
        "id": str(uuid.uuid4()),
        "username": current_user.get("username"),
        "property_id": property_id,
        "status": "programada",
        "created_at": datetime.utcnow().isoformat() + "Z",
    })
    save_requests(requests_data)
    return jsonify({"success": True, "message": "Visita agendada."})


@app.route("/api/inmo/tasacion", methods=["POST"])
def api_inmo_tasacion():
    current_user = get_current_user()
    if not current_user:
        return jsonify({"success": False, "message": "Debe iniciar sesión."}), 401

    data = request.get_json(silent=True) or {}
    tipo = (data.get("tipo") or "Departamento").strip()
    try:
        superficie = float(data.get("superficie") or 0)
    except (TypeError, ValueError):
        superficie = 0
    direccion = (data.get("direccion") or "").strip()
    if not direccion or not math.isfinite(superficie) or superficie <= 0 or superficie > 100000:
        return jsonify({"success": False, "message": "Necesitamos dirección y superficie."}), 400

    base = {"Departamento": 1850, "Casa": 2200, "PH": 2000, "Oficina": 1700, "Terreno": 1200, "Local": 1600}.get(tipo, 1800)
    valor = round(base * superficie * (1.05 if tipo in {"Casa", "PH"} else 1.0), 2)

    requests_data = load_requests()
    tasacion = {
        "id": str(uuid.uuid4()),
        "username": current_user.get("username"),
        "direccion": direccion,
        "tipo": tipo,
        "valor_estimado": valor,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    requests_data["inmo_tasaciones"].append(tasacion)
    save_requests(requests_data)
    return jsonify({"success": True, "valor": valor, "valor_formateado": f"USD {valor:,.0f}".replace(",", ".")})


@app.route("/api/inmo/compra", methods=["POST"])
def api_inmo_compra():
    """Registra la compra de una propiedad y genera el comprobante."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({"success": False, "message": "Debe iniciar sesión."}), 401

    data = request.get_json(silent=True) or {}
    try:
        property_id = int(data.get("property_id"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Propiedad no encontrada."}), 400
    propiedad = next((p for p in inmo_propiedades if p["id"] == property_id), None)
    if not propiedad:
        return jsonify({"success": False, "message": "Propiedad no encontrada."}), 404

    nombre = (data.get("nombre") or "").strip()
    email = (data.get("email") or "").strip()
    telefono = (data.get("telefono") or "").strip()
    dni = (data.get("dni") or "").strip()
    forma_pago = (data.get("forma_pago") or "Contado").strip()

    if not nombre or not email or not dni:
        return jsonify({"success": False, "message": "Completá nombre, DNI y email."}), 400
    if forma_pago not in {"Contado", "Crédito hipotecario", "Financiación propia"}:
        return jsonify({"success": False, "message": "Forma de pago no válida."}), 400

    requests_data = load_requests()
    numero = f"INM-{1000 + len(requests_data['inmo_compras']) + 1}"
    compra = {
        "id": str(uuid.uuid4()),
        "numero": numero,
        "username": current_user.get("username"),
        "property_id": propiedad["id"],
        "propiedad_nombre": propiedad["nombre"],
        "propiedad_ubicacion": propiedad["ubicacion"],
        "precio": propiedad["precio"],
        "comprador": {"nombre": nombre, "email": email, "telefono": telefono, "dni": dni},
        "forma_pago": forma_pago,
        "status": "confirmada",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    requests_data["inmo_compras"].append(compra)
    save_requests(requests_data)

    return jsonify({
        "success": True,
        "message": "Compra confirmada.",
        "compra": compra,
        "precio_formateado": f"USD {propiedad['precio']:,.0f}".replace(",", "."),
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

    data = request.get_json(silent=True) or {}
    product_id = data.get('product_id')
    refresco_id_str = str(data.get('refresco_id', 0))
    if refresco_id_str not in refresco_precios:
        return jsonify({'success': False, 'message': 'Refresco no válido'}), 400
    refresco_id = int(refresco_id_str)
    
    # Intenta parsear las cantidades, usando 1 y 0 como fallback
    try:
        cant_milanesa = int(data.get('cant_milanesa', 1))
        cant_refresco = int(data.get('cant_refresco', 0))
    except (TypeError, ValueError):
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
    data = request.get_json(silent=True) or {}
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
    app.run(debug=False, host='0.0.0.0', port=5000)