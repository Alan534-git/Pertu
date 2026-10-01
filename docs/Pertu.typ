#set document(
  title: "Pertu — Documentación integral del sistema",
  author: "Equipo de desarrollo",
  date: datetime.today(),
)
#set page(
  paper: "a4",
  margin: (x: 2.2cm, y: 2cm),
  numbering: "1",
)
#set text(font: "Libertinus Serif", size: 10pt, lang: "es")
#set par(justify: true, leading: 0.72em)
#set heading(numbering: "1.1")

#show heading.where(level: 1): set text(size: 19pt, weight: "bold", fill: rgb("#173A68"))
#show heading.where(level: 2): set text(size: 14pt, weight: "bold", fill: rgb("#2F6FED"))
#show heading.where(level: 3): set text(size: 11pt, weight: "bold", fill: rgb("#334155"))

#let accent = rgb("#2F6FED")
#let navy = rgb("#173A68")
#let soft = rgb("#EEF3FA")
#let code-bg = rgb("#F4F6F8")

#let callout(title, body) = block(
  fill: soft,
  stroke: (left: 3pt + accent),
  inset: 10pt,
  radius: 4pt,
)[
  #text(weight: "bold", fill: navy)[#title] \
  #body
]

#let code(content) = block(
  fill: code-bg,
  inset: 9pt,
  radius: 4pt,
  width: 100%,
)[#text(font: "DejaVu Sans Mono", size: 8.5pt)[#content]]

#align(center)[
  #v(2cm)
  #text(size: 32pt, weight: "bold", fill: navy)[Pertu]

  #v(0.35cm)
  #text(size: 17pt, fill: accent)[Documentación integral del sistema]

  #v(1cm)
  #text(size: 11pt)[Plataforma web multi-sector para ventas, gestiones e inmobiliaria]

  #v(1.8cm)
  #rect(
    width: 7cm,
    height: 2.2cm,
    radius: 12pt,
    fill: navy,
  )[
    #align(center + horizon)[
      #text(size: 18pt, weight: "bold", fill: white)[Flask · Jinja · CSS · JavaScript]
    ]
  ]

  #v(1.5cm)
  #text(fill: gray)[Documento técnico y funcional]
  #linebreak()
  #text(fill: gray)[Actualizado: #datetime.today().display()]
]

#pagebreak()

#outline(title: "Contenido", indent: auto)
#pagebreak()

= Resumen ejecutivo

Pertu es una aplicación web monolítica desarrollada con Flask que integra distintos servicios bajo una única autenticación y una experiencia visual común. El sistema organiza sus funcionalidades en cuatro sectores principales:

- *Delivery*: catálogo de milanesas, bebidas, cantidades y carrito.
- *Gestoría*: recepción y seguimiento de trámites.
- *DUAL*: tienda de indumentaria femenina y deportiva.
- *InmoControl*: catálogo inmobiliario, favoritos, consultas, tasaciones, visitas y compras.

La aplicación utiliza plantillas Jinja para renderizar HTML en el servidor, CSS modular por dominio, JavaScript vanilla para interacciones y archivos JSON como persistencia del prototipo.

#callout("Objetivo de producto", [
  Pertu centraliza operaciones de sectores diferentes sin duplicar la autenticación, el contexto de usuario ni los mecanismos básicos de administración. La arquitectura actual es adecuada para una entrega académica o MVP y tiene puntos claros de evolución hacia servicios especializados.
])

= Arquitectura general

== Capas principales

#table(
  columns: (1.35fr, 2.4fr, 1.4fr),
  stroke: 0.5pt + luma(80%),
  inset: 6pt,
  fill: (_, row) => if row == 0 { navy } else if calc.odd(row) { rgb("#F8FAFC") } else { white },
  table.header(
    [#text(fill: white, weight: "bold")[Capa]],
    [#text(fill: white, weight: "bold")[Responsabilidad]],
    [#text(fill: white, weight: "bold")[Ubicación]],
  ),
  [Aplicación], [Configuración Flask, rutas, validaciones y reglas de negocio], [`app.py`],
  [Presentación], [Plantillas Jinja, layouts, formularios y navegación], [`templates/`],
  [Estilos], [Tokens visuales, responsive, componentes por sector], [`static/css/`],
  [Comportamiento], [Carrito, galerías, checkout, formularios y feedback], [`static/js/`],
  [Persistencia], [Usuarios y solicitudes serializados en JSON], [`data/`],
  [Recursos], [Imágenes de productos, propiedades, fuentes e iconos], [`static/img/`, `static/webfonts/`],
)

== Flujo de una petición

#enum(
  [El navegador solicita una ruta Flask.],
  [Flask identifica la vista y carga el usuario desde la sesión.],
  [La vista verifica rol o sector cuando corresponde.],
  [Se consultan productos, propiedades o solicitudes.],
  [Jinja renderiza una plantilla con el contexto necesario.],
  [El navegador aplica CSS y ejecuta JavaScript para interacciones progresivas.],
)

== Estructura del repositorio

#code(```
Pertu/
├── app.py                    # Aplicación Flask, datos de dominio y rutas
├── data/
│   ├── users.json            # Usuarios del sistema
│   └── requests.json         # Pedidos y solicitudes por sector
├── templates/                # Vistas Jinja y layouts compartidos
│   ├── dual_base.html
│   ├── inmo/inmo_base.html
│   └── legacy/               # Plantillas históricas no principales
├── static/
│   ├── css/                  # Estilos globales y por módulo
│   ├── js/                   # Comportamiento del cliente
│   ├── img/                  # Recursos visuales
│   └── webfonts/             # Font Awesome local
└── docs/
    └── Pertu.typ             # Esta documentación
```)

= Acceso, usuarios y sesiones

== Autenticación

La ruta `/login` valida las credenciales contra `data/users.json`. Las contraseñas se comparan usando las funciones de hashing de Werkzeug. Cuando el acceso es correcto se guarda un usuario reducido en la sesión y se redirige según el rol o sector.

Los destinos principales son:

#table(
  columns: (1.2fr, 1.4fr, 2fr),
  stroke: 0.5pt + luma(80%),
  inset: 6pt,
  table.header([Ruta], [Perfil], [Destino]),
  [`/admin`], [Administrador], [Panel de administración],
  [`/delivery`], [Delivery], [Catálogo y carrito],
  [`/gestoria`], [Gestoría], [Formulario de trámite],
  [`/dual`], [DUAL], [Tienda de indumentaria],
  [`/inmo`], [InmoControl], [Portal inmobiliario],
)

== Control de acceso

Las funciones `dual_require_sector`, `inmo_require_sector` y `role_required` centralizan la autorización. Un usuario sin sesión vuelve a `/login`; un usuario autenticado en otro sector es redirigido a su sector correspondiente.

== Configuración relevante

#code(```
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = configurable mediante FLASK_COOKIE_SECURE
MAX_CONTENT_LENGTH = 1 MB
FLASK_SECRET_KEY = variable de entorno recomendada
```)

#callout("Recomendación de producción", [
  Definir siempre `FLASK_SECRET_KEY`, activar `FLASK_COOKIE_SECURE=1` detrás de HTTPS y sustituir las credenciales de ejemplo. Las sesiones y los archivos JSON son apropiados para desarrollo, pero no para múltiples procesos concurrentes.
])

= Módulo Delivery

== Experiencia

La página principal presenta un catálogo de milanesas con imagen, precio, cantidad, selección de bebida y cálculo de subtotal. El carrito permite modificar cantidades, quitar productos, vaciar el pedido y confirmar el checkout.

== Rutas

#table(
  columns: (1.4fr, 2.8fr),
  stroke: 0.5pt + luma(80%),
  inset: 6pt,
  table.header([Ruta], [Función]),
  [`/delivery`], [Renderiza el catálogo],
  [`/carrito`], [Muestra el carrito y el total],
  [`/vaciar`], [Vacía el carrito],
  [`/api/agregar`], [Agrega o actualiza un producto],
  [`/api/eliminar`], [Elimina una línea del carrito],
  [`/api/checkout`], [Confirma la compra],
)

== Reglas de negocio

- La cantidad máxima global definida es `MAX_QUANTITY = 20`.
- El precio se calcula en el servidor mediante `calculate_item_price`.
- El carrito se almacena en sesión.
- Las solicitudes confirmadas se persisten en `delivery_orders`.

= Módulo Gestoría

La pantalla de gestoría ofrece una interfaz para iniciar trámites y registrar datos del solicitante. La API `/api/tramite` valida el contenido y agrega la solicitud a `gestoria_requests`. El panel administrativo permite consultar solicitudes y cambiar su estado desde `/api/admin/request-status`.

El flujo recomendado para el usuario es:

#enum(
  [Elegir el tipo de trámite.],
  [Completar datos personales y del vehículo o gestión.],
  [Enviar la solicitud.],
  [Recibir confirmación visual y número de seguimiento.],
)

= Módulo DUAL

== Alcance funcional

DUAL es una tienda de ropa con dos líneas editoriales:

- *Mujer*: vestidos, tops, jeans, conjuntos, blusas y camperas.
- *Deportivo*: prendas y accesorios para entrenamiento.

También cuenta con categorías de ofertas y novedades, variantes de talle y color, stock por combinación, checkout, comprobante y seguimiento de envío.

== Plantillas principales

#table(
  columns: (2fr, 3fr),
  stroke: 0.5pt + luma(80%),
  inset: 6pt,
  table.header([Plantilla], [Uso]),
  [`dual_base.html`], [Layout compartido, header, navegación y footer],
  [`dual_index.html`], [Inicio, categorías destacadas y productos nuevos],
  [`dual_categoria.html`], [Listado filtrable por categoría],
  [`dual_producto.html`], [Detalle, variantes y selección de compra],
  [`dual_checkout.html`], [Datos de envío y pago],
  [`dual_comprobante.html`], [Confirmación del pedido],
  [`dual_pedidos.html`], [Historial de pedidos],
  [`dual_seguimiento.html`], [Seguimiento del envío],
)

== API de compra

`POST /api/dual/pedido` verifica sesión, producto, cantidad, talle, color, stock, datos de envío y método de pago. Luego genera identificadores únicos, descuenta stock, guarda el pedido en `dual_orders` y devuelve la URL del comprobante.

Los métodos de pago aceptados son tarjeta, Mercado Pago, transferencia y efectivo. El pedido contiene transportista, código de seguimiento, estado, total, envío y fecha de creación.

= Módulo InmoControl

== Alcance funcional

InmoControl ofrece:

- Búsqueda de propiedades para comprar o alquilar.
- Listado, detalle, galería de imágenes y mapa.
- Favoritos vinculados a la sesión.
- Solicitud de contacto y visita.
- Tasación estimada por tipo y superficie.
- Registro de intención de compra.
- Emprendimientos, servicios, novedades y cuenta.

== Rutas de navegación

#table(
  columns: (1.8fr, 3fr),
  stroke: 0.5pt + luma(80%),
  inset: 6pt,
  table.header([Ruta], [Propósito]),
  [`/inmo` y `/inmo/home`], [Inicio y buscador inmobiliario],
  [`/inmo/listado/<operacion>`], [Resultados de comprar o alquilar],
  [`/inmo/propiedad/<id>`], [Detalle de una propiedad],
  [`/inmo/mapa`], [Exploración por zonas],
  [`/inmo/emprendimientos`], [Proyectos inmobiliarios],
  [`/inmo/tasacion`], [Solicitud de tasación],
  [`/inmo/servicios`], [Servicios de la empresa],
  [`/inmo/novedades`], [Noticias y contenidos],
  [`/inmo/contacto`], [Contacto general],
  [`/inmo/cuenta`], [Favoritos y actividad del usuario],
)

== APIs inmobiliarias

#table(
  columns: (2fr, 3fr),
  stroke: 0.5pt + luma(80%),
  inset: 6pt,
  table.header([Endpoint], [Operación]),
  [`/api/inmo/favorito`], [Añade o quita favoritos],
  [`/api/inmo/contacto`], [Registra una consulta],
  [`/api/inmo/visita`], [Agenda una visita],
  [`/api/inmo/tasacion`], [Calcula y guarda una tasación],
  [`/api/inmo/compra`], [Registra una intención de compra],
)

La tasación utiliza una tarifa base por tipo de propiedad y la superficie declarada. El resultado es una estimación orientativa y no reemplaza una valuación profesional.

= Sistema visual y UX

== Layouts compartidos

Los módulos con mayor complejidad utilizan layouts base:

- `dual_base.html` para DUAL.
- `inmo/inmo_base.html` para InmoControl.

Estos layouts concentran marca, navegación, sesión, footer y bloques de extensión. De esta forma las páginas internas comparten una estructura estable y pueden cambiar el contenido sin duplicar chrome.

== Design system transversal

`static/css/design-system.css` define:

- Foco visible para teclado.
- Radios y sombras base.
- Estados de controles deshabilitados.
- Compatibilidad con usuarios que prefieren reducir movimiento.

Los estilos específicos se mantienen en `dual.css`, `inmo.css`, `style.css`, `index.css` y `carrito.css` para evitar acoplar la identidad visual de un sector a otro.

== Responsive y accesibilidad

- DUAL e InmoControl incluyen menú móvil con botón real, `aria-expanded`, `aria-controls` y etiqueta accesible.
- Las grillas se adaptan a una columna en pantallas pequeñas.
- Los campos y botones mantienen áreas táctiles utilizables.
- Las galerías y acciones conservan estados visuales de foco y hover.
- El sistema respeta `prefers-reduced-motion`.

= Persistencia y modelo de datos

== Archivos

#table(
  columns: (1.7fr, 3fr),
  stroke: 0.5pt + luma(80%),
  inset: 6pt,
  table.header([Archivo], [Contenido]),
  [`data/users.json`], [Usuarios, roles, sectores y hashes de contraseña],
  [`data/requests.json`], [Pedidos delivery, pedidos DUAL, contactos, visitas, tasaciones y compras InmoControl],
)

== Escrituras seguras actuales

`save_json` escribe primero en un archivo temporal, fuerza el contenido a disco con `fsync` y después realiza `os.replace`. Este patrón reduce el riesgo de dejar un JSON truncado si el proceso se interrumpe durante una escritura.

== Limitaciones del almacenamiento actual

- No hay transacciones ni bloqueo distribuido.
- Dos procesos pueden sobrescribir cambios simultáneos.
- Las búsquedas y filtros son lineales en memoria.
- El stock no tiene una reserva transaccional.
- Los archivos crecen sin índices ni paginación.

= Seguridad

== Controles implementados

- Hashing de contraseñas con Werkzeug.
- Sesión protegida con `HttpOnly` y `SameSite=Lax`.
- Límite de tamaño de solicitud de 1 MB.
- Validación de IDs, cantidades, variantes, stock y métodos de pago.
- Control de acceso por rol y sector.
- Headers `X-Content-Type-Options`, `X-Frame-Options` y `Referrer-Policy`.
- Escritura atómica de archivos JSON.

== Pendientes antes de producción

#enum(
  [Agregar protección CSRF para formularios y endpoints mutables.],
  [Aplicar rate limiting y auditoría de intentos de login y APIs.],
  [Validar y normalizar emails, teléfonos y contenido textual con mayor profundidad.],
  [Mover secretos y credenciales fuera de archivos y datos de ejemplo.],
  [Usar una base de datos con transacciones y permisos por usuario.],
  [Agregar una política CSP compatible con las fuentes y assets reales.],
  [Servir todo el tráfico mediante HTTPS y activar cookies Secure.],
)

= Escalabilidad

== Evolución recomendada

La migración puede hacerse de forma incremental:

#table(
  columns: (0.8fr, 2fr, 2.5fr),
  stroke: 0.5pt + luma(80%),
  inset: 6pt,
  table.header([Etapa], [Cambio], [Beneficio]),
  [1], [Extraer configuración y secretos a un entorno gestionado], [Despliegues repetibles y seguros],
  [2], [Migrar JSON a PostgreSQL o MariaDB], [Transacciones, índices y concurrencia],
  [3], [Separar catálogos y pedidos en servicios de dominio], [Escalado independiente por carga],
  [4], [Incorporar Redis para sesiones y cache], [Menor latencia y menos lecturas],
  [5], [Procesar emails, comprobantes y tracking con una cola], [APIs más rápidas y resilientes],
  [6], [Agregar observabilidad], [Métricas, logs estructurados y trazas],
)

== Diseño objetivo

La separación recomendada no implica convertir todo en microservicios de inmediato. Primero conviene mantener un monolito modular con paquetes como `auth`, `delivery`, `gestoria`, `dual`, `inmo` y `admin`. Cuando el tráfico lo justifique, los módulos con mayor carga pueden extraerse manteniendo contratos HTTP estables.

= Operación y mantenimiento

== Ejecución local

#code(```
# Crear y activar un entorno virtual
python -m venv .venv
.venv\Scripts\activate

# Instalar dependencias del proyecto
pip install flask werkzeug

# Configurar una clave de sesión
$env:FLASK_SECRET_KEY = "clave-local-segura"

# Iniciar el servidor
python app.py
```)

== Verificaciones recomendadas

- Compilar sintaxis del backend con `python -m py_compile app.py`.
- Ejecutar pruebas de rutas con Flask en modo testing.
- Verificar respuestas `2xx`, `4xx` y redirecciones de cada sector.
- Probar checkout con stock válido, stock insuficiente y variantes inválidas.
- Probar el menú móvil con teclado y lector de pantalla.
- Ejecutar `typst compile docs/Pertu.typ docs/Pertu.pdf` para regenerar este documento.

= Referencia rápida de endpoints

#table(
  columns: (1.4fr, 0.9fr, 3fr),
  stroke: 0.5pt + luma(80%),
  inset: 5pt,
  table.header([Endpoint], [Método], [Descripción]),
  [`/login`], [GET/POST], [Autenticación],
  [`/logout`], [GET], [Cierre de sesión],
  [`/api/agregar`], [POST], [Carrito Delivery],
  [`/api/eliminar`], [POST], [Eliminación del carrito],
  [`/api/checkout`], [POST], [Checkout Delivery],
  [`/api/tramite`], [POST], [Alta de trámite],
  [`/api/admin/request-status`], [POST], [Cambio de estado administrativo],
  [`/api/dual/pedido`], [POST], [Compra DUAL],
  [`/api/inmo/favorito`], [POST], [Favoritos inmobiliarios],
  [`/api/inmo/contacto`], [POST], [Consulta inmobiliaria],
  [`/api/inmo/visita`], [POST], [Solicitud de visita],
  [`/api/inmo/tasacion`], [POST], [Tasación],
  [`/api/inmo/compra`], [POST], [Compra inmobiliaria],
)

= Conclusión

Pertu cuenta con una base funcional amplia, layouts sectoriales reutilizables y validaciones de negocio concentradas en Flask. La reciente capa de diseño común mejora la coherencia visual y la experiencia responsive sin eliminar la identidad de DUAL, Delivery, Gestoría o InmoControl.

Para evolucionar hacia un sistema extremadamente escalable, la prioridad técnica es reemplazar la persistencia JSON por una base transaccional, formalizar contratos de API, incorporar pruebas automatizadas y extraer los dominios solo cuando existan métricas que justifiquen la separación. Esta estrategia conserva velocidad de desarrollo y reduce el riesgo de una migración prematura a microservicios.
