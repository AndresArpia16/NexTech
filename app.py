"""NexTech: tienda virtual de tecnología hecha con Python y Flask.

Este es el archivo principal. Está dividido en secciones:
  1. CONFIGURACIÓN
  2. DATOS DE DEMOSTRACIÓN  (aquí puedes editar categorías y productos de ejemplo)
  3. BASE DE DATOS          (SQLite: crea las tablas y hace las consultas)
  4. AYUDAS PARA LAS PLANTILLAS HTML
  5. PÁGINAS DE LA TIENDA   (inicio, productos, carrito...)
  6. PANEL DE ADMINISTRACIÓN (protegido con contraseña)
"""
import os
import secrets
import sqlite3
import uuid
from functools import wraps

from flask import (Flask, abort, flash, g, redirect, render_template, request, session, url_for)
from markupsafe import Markup
from werkzeug.security import check_password_hash, generate_password_hash

# =====================================================================
# 1. CONFIGURACIÓN
# =====================================================================
CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_BD = os.path.join(CARPETA, "nextech.db")            # archivo de la base de datos
CARPETA_IMAGENES = os.path.join(CARPETA, "static", "img", "productos")
EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "webp"}


def obtener_clave_secreta():
    """Clave para firmar las sesiones. Se crea sola la primera vez (o se toma de la variable SECRET_KEY)."""
    if os.environ.get("SECRET_KEY"):
        return os.environ["SECRET_KEY"]
    ruta = os.path.join(CARPETA, ".clave_secreta")
    if not os.path.exists(ruta):
        with open(ruta, "w") as archivo:
            archivo.write(secrets.token_hex(32))
    with open(ruta) as archivo:
        return archivo.read().strip()


app = Flask(__name__)
app.config.update(SECRET_KEY=obtener_clave_secreta(),
                  MAX_CONTENT_LENGTH=3 * 1024 * 1024,        # fotos de hasta 3 MB
                  SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

# =====================================================================
# 2. DATOS DE DEMOSTRACIÓN
# Se copian a la base de datos SOLO la primera vez que se ejecuta la página.
# Después, los productos se administran desde el panel (/admin).
# Para volver a cargar estos datos: detén el servidor y borra el archivo nextech.db
# =====================================================================
CATEGORIAS = [
    {"slug": "portatiles", "nombre": "Portátiles", "icono": "💻", "descripcion": "Equipos para trabajo, estudio y juegos"},
    {"slug": "monitores", "nombre": "Monitores", "icono": "🖥️", "descripcion": "Pantallas para todo uso"},
    {"slug": "teclados", "nombre": "Teclados", "icono": "⌨️", "descripcion": "Mecánicos e inalámbricos"},
    {"slug": "mouse", "nombre": "Mouse", "icono": "🖱️", "descripcion": "Precisión y ergonomía"},
    {"slug": "audifonos", "nombre": "Audífonos", "icono": "🎧", "descripcion": "Sonido para cada momento"},
    {"slug": "componentes", "nombre": "Componentes de PC", "icono": "🧩", "descripcion": "Piezas para armar o mejorar tu PC"},
    {"slug": "accesorios", "nombre": "Accesorios tecnológicos", "icono": "🔌", "descripcion": "Cables, bases, hubs y más"},
]

PRODUCTOS_DEMO = [
    {
        "nombre": "NovaBook 15 Pro",
        "marca": "Nexa",
        "categoria": "portatiles",          # debe ser un "slug" de CATEGORIAS
        "precio": 3299000,                       # pesos colombianos, solo números
        "precio_anterior": 3699000,               # None = sin oferta
        "stock": 8,                         # unidades en inventario
        "destacado": True,
        "descripcion": "Portátil ligero para productividad diaria.",
        "detalle": "Portátil de demostración con pantalla de 15,6 pulgadas pensado para trabajo y estudio.",
        "especificaciones": ["Procesador: 8 núcleos (demo)", "RAM: 16 GB", "Almacenamiento: 512 GB SSD", "Pantalla: 15,6″ Full HD"],
        "imagen": "",                         # nombre del archivo en static/img/productos/ (vacío = imagen predeterminada)
    },
    {
        "nombre": "Titan G17 Gamer",
        "marca": "Kryon",
        "categoria": "portatiles",          # debe ser un "slug" de CATEGORIAS
        "precio": 5890000,                       # pesos colombianos, solo números
        "precio_anterior": None,               # None = sin oferta
        "stock": 3,                         # unidades en inventario
        "destacado": True,
        "descripcion": "Potencia para juegos y diseño.",
        "detalle": "Portátil de demostración orientado a juegos y edición.",
        "especificaciones": ["Procesador: 12 núcleos (demo)", "RAM: 32 GB", "Almacenamiento: 1 TB SSD", "Pantalla: 17″ 144 Hz"],
        "imagen": "",                         # nombre del archivo en static/img/productos/ (vacío = imagen predeterminada)
    },
    {
        "nombre": "VisionView 27 QHD",
        "marca": "Aurum",
        "categoria": "monitores",          # debe ser un "slug" de CATEGORIAS
        "precio": 1190000,                       # pesos colombianos, solo números
        "precio_anterior": 1390000,               # None = sin oferta
        "stock": 12,                         # unidades en inventario
        "destacado": True,
        "descripcion": "Monitor QHD de 27 pulgadas.",
        "detalle": "Monitor de demostración con panel IPS y marcos delgados.",
        "especificaciones": ["Tamaño: 27″", "Resolución: 2560×1440", "Panel: IPS", "Refresco: 75 Hz"],
        "imagen": "",                         # nombre del archivo en static/img/productos/ (vacío = imagen predeterminada)
    },
    {
        "nombre": "CurveMax 32",
        "marca": "Voltix",
        "categoria": "monitores",          # debe ser un "slug" de CATEGORIAS
        "precio": 1650000,                       # pesos colombianos, solo números
        "precio_anterior": None,               # None = sin oferta
        "stock": 0,                         # unidades en inventario
        "destacado": False,
        "descripcion": "Monitor curvo inmersivo.",
        "detalle": "Monitor curvo de demostración para entretenimiento.",
        "especificaciones": ["Tamaño: 32″", "Resolución: Full HD", "Panel: VA curvo", "Refresco: 165 Hz"],
        "imagen": "",                         # nombre del archivo en static/img/productos/ (vacío = imagen predeterminada)
    },
    {
        "nombre": "KeyForge Mecánico TKL",
        "marca": "Kryon",
        "categoria": "teclados",          # debe ser un "slug" de CATEGORIAS
        "precio": 289000,                       # pesos colombianos, solo números
        "precio_anterior": 349000,               # None = sin oferta
        "stock": 25,                         # unidades en inventario
        "destacado": True,
        "descripcion": "Teclado mecánico compacto con luz RGB.",
        "detalle": "Teclado mecánico de demostración sin teclado numérico.",
        "especificaciones": ["Switches: Rojos (demo)", "Conexión: USB", "Distribución: TKL", "Luz: RGB"],
        "imagen": "",                         # nombre del archivo en static/img/productos/ (vacío = imagen predeterminada)
    },
    {
        "nombre": "AirType Slim",
        "marca": "Nexa",
        "categoria": "teclados",          # debe ser un "slug" de CATEGORIAS
        "precio": 179000,                       # pesos colombianos, solo números
        "precio_anterior": None,               # None = sin oferta
        "stock": 14,                         # unidades en inventario
        "destacado": False,
        "descripcion": "Teclado inalámbrico silencioso.",
        "detalle": "Teclado inalámbrico de demostración para oficina.",
        "especificaciones": ["Conexión: Bluetooth", "Batería: Recargable", "Distribución: Completo", "Ruido: Bajo"],
        "imagen": "",                         # nombre del archivo en static/img/productos/ (vacío = imagen predeterminada)
    },
    {
        "nombre": "Precision X Wireless",
        "marca": "Aurum",
        "categoria": "mouse",          # debe ser un "slug" de CATEGORIAS
        "precio": 159000,                       # pesos colombianos, solo números
        "precio_anterior": 199000,               # None = sin oferta
        "stock": 30,                         # unidades en inventario
        "destacado": True,
        "descripcion": "Mouse ergonómico inalámbrico.",
        "detalle": "Mouse de demostración con sensor óptico de alta precisión.",
        "especificaciones": ["Sensor: Óptico 16000 DPI", "Conexión: 2,4 GHz / BT", "Botones: 6", "Peso: 85 g"],
        "imagen": "",                         # nombre del archivo en static/img/productos/ (vacío = imagen predeterminada)
    },
    {
        "nombre": "Pulse Pro Gaming",
        "marca": "Voltix",
        "categoria": "mouse",          # debe ser un "slug" de CATEGORIAS
        "precio": 99000,                       # pesos colombianos, solo números
        "precio_anterior": None,               # None = sin oferta
        "stock": 40,                         # unidades en inventario
        "destacado": False,
        "descripcion": "Mouse con cable para juegos.",
        "detalle": "Mouse con cable de demostración, ligero y ajustable.",
        "especificaciones": ["Sensor: Óptico 8000 DPI", "Conexión: USB", "Botones: 7", "Peso: 72 g"],
        "imagen": "",                         # nombre del archivo en static/img/productos/ (vacío = imagen predeterminada)
    },
    {
        "nombre": "SoundWave ANC",
        "marca": "Aurum",
        "categoria": "audifonos",          # debe ser un "slug" de CATEGORIAS
        "precio": 459000,                       # pesos colombianos, solo números
        "precio_anterior": 549000,               # None = sin oferta
        "stock": 9,                         # unidades en inventario
        "destacado": True,
        "descripcion": "Audífonos con cancelación de ruido.",
        "detalle": "Audífonos inalámbricos de demostración con modo ambiente.",
        "especificaciones": ["Tipo: Over-ear", "Conexión: Bluetooth", "Autonomía: 30 h (demo)", "Micrófono: Sí"],
        "imagen": "",                         # nombre del archivo en static/img/productos/ (vacío = imagen predeterminada)
    },
    {
        "nombre": "BassCore Gamer",
        "marca": "Kryon",
        "categoria": "audifonos",          # debe ser un "slug" de CATEGORIAS
        "precio": 219000,                       # pesos colombianos, solo números
        "precio_anterior": None,               # None = sin oferta
        "stock": 18,                         # unidades en inventario
        "destacado": False,
        "descripcion": "Audífonos con micrófono para jugar.",
        "detalle": "Diadema de demostración con almohadillas acolchadas.",
        "especificaciones": ["Tipo: Over-ear", "Conexión: USB / 3,5 mm", "Sonido: Estéreo", "Micrófono: Retráctil"],
        "imagen": "",                         # nombre del archivo en static/img/productos/ (vacío = imagen predeterminada)
    },
    {
        "nombre": "SSD Rapid 1TB NVMe",
        "marca": "Nexa",
        "categoria": "componentes",          # debe ser un "slug" de CATEGORIAS
        "precio": 329000,                       # pesos colombianos, solo números
        "precio_anterior": 389000,               # None = sin oferta
        "stock": 22,                         # unidades en inventario
        "destacado": True,
        "descripcion": "Almacenamiento NVMe veloz.",
        "detalle": "Unidad de estado sólido de demostración M.2.",
        "especificaciones": ["Capacidad: 1 TB", "Interfaz: NVMe M.2", "Lectura: Hasta 3500 MB/s (demo)", "Formato: 2280"],
        "imagen": "",                         # nombre del archivo en static/img/productos/ (vacío = imagen predeterminada)
    },
    {
        "nombre": "Hub USB-C 7 en 1",
        "marca": "Voltix",
        "categoria": "accesorios",          # debe ser un "slug" de CATEGORIAS
        "precio": 139000,                       # pesos colombianos, solo números
        "precio_anterior": None,               # None = sin oferta
        "stock": 35,                         # unidades en inventario
        "destacado": False,
        "descripcion": "Amplía los puertos de tu portátil.",
        "detalle": "Hub de demostración con HDMI, USB y lector de tarjetas.",
        "especificaciones": ["Puertos: 7", "Video: HDMI", "Carga: USB-C PD", "Material: Aluminio"],
        "imagen": "",                         # nombre del archivo en static/img/productos/ (vacío = imagen predeterminada)
    },
]

# =====================================================================
# 3. BASE DE DATOS (SQLite)
# Si algún día migras a MySQL o PostgreSQL, solo cambiarías esta sección.
# =====================================================================
ESTRUCTURA_SQL = """
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,          -- nombre corto para la URL, ej: "portatiles"
    nombre TEXT NOT NULL,
    descripcion TEXT DEFAULT '',
    icono TEXT DEFAULT '📦'
);
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    marca TEXT NOT NULL,
    categoria_id INTEGER NOT NULL REFERENCES categorias(id),
    precio INTEGER NOT NULL,            -- pesos colombianos (COP)
    precio_anterior INTEGER,            -- si tiene valor, el producto está en oferta
    stock INTEGER NOT NULL DEFAULT 0,
    descripcion TEXT DEFAULT '',        -- descripción corta (tarjeta)
    detalle TEXT DEFAULT '',            -- descripción completa
    especificaciones TEXT DEFAULT '',   -- una por línea:  Nombre: valor
    imagen TEXT DEFAULT '',             -- archivo dentro de static/img/productos/
    destacado INTEGER NOT NULL DEFAULT 0,
    activo INTEGER NOT NULL DEFAULT 1   -- 0 = oculto en la tienda
);
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    clave_hash TEXT NOT NULL,           -- la contraseña NUNCA se guarda en texto plano
    es_admin INTEGER NOT NULL DEFAULT 0
);
"""


def obtener_bd():
    """Abre la conexión a la base de datos (una por petición)."""
    if "bd" not in g:
        g.bd = sqlite3.connect(RUTA_BD)
        g.bd.row_factory = sqlite3.Row            # permite escribir fila["nombre"]
    return g.bd


@app.teardown_appcontext
def cerrar_bd(error=None):
    bd = g.pop("bd", None)
    if bd is not None:
        bd.close()


def crear_base_de_datos():
    """Crea las tablas y carga los datos de demostración si la base está vacía."""
    bd = sqlite3.connect(RUTA_BD)
    bd.executescript(ESTRUCTURA_SQL)
    if bd.execute("SELECT COUNT(*) FROM categorias").fetchone()[0] == 0:
        for c in CATEGORIAS:
            bd.execute("INSERT INTO categorias (slug, nombre, descripcion, icono) VALUES (?,?,?,?)",
                       (c["slug"], c["nombre"], c["descripcion"], c["icono"]))
        for p in PRODUCTOS_DEMO:
            categoria_id = bd.execute("SELECT id FROM categorias WHERE slug = ?", (p["categoria"],)).fetchone()[0]
            bd.execute("""INSERT INTO productos (nombre, marca, categoria_id, precio, precio_anterior, stock,
                          descripcion, detalle, especificaciones, imagen, destacado)
                          VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                       (p["nombre"], p["marca"], categoria_id, p["precio"], p["precio_anterior"], p["stock"],
                        p["descripcion"], p["detalle"], "\n".join(p["especificaciones"]), p["imagen"],
                        int(p["destacado"])))
    bd.commit()
    bd.close()


def guardar_admin(nombre, clave):
    """Crea el administrador (la contraseña se guarda cifrada). Lo usa crear_admin.py."""
    bd = sqlite3.connect(RUTA_BD)
    bd.execute("INSERT OR REPLACE INTO usuarios (nombre, clave_hash, es_admin) VALUES (?,?,1)",
               (nombre, generate_password_hash(clave)))
    bd.commit()
    bd.close()


def hay_admin():
    bd = sqlite3.connect(RUTA_BD)
    existe = bd.execute("SELECT COUNT(*) FROM usuarios WHERE es_admin = 1").fetchone()[0] > 0
    bd.close()
    return existe


# ---------- Consultas de categorías y productos ----------
def listar_categorias():
    return obtener_bd().execute("SELECT * FROM categorias ORDER BY id").fetchall()


CONSULTA_PRODUCTOS = """SELECT p.*, c.nombre AS categoria, c.slug AS categoria_slug
                        FROM productos p JOIN categorias c ON c.id = p.categoria_id"""
ORDENES = {"precio_asc": "p.precio ASC", "precio_desc": "p.precio DESC", "nombre": "p.nombre COLLATE NOCASE ASC"}


def buscar_productos(q="", categoria="", marca="", precio_max=0, solo_disponibles=False,
                     solo_destacados=False, solo_ofertas=False, orden="", incluir_ocultos=False):
    """Busca productos aplicando los filtros. Los valores van como parámetros (?) para evitar inyección SQL."""
    condiciones, valores = [], []
    if not incluir_ocultos:
        condiciones.append("p.activo = 1")
    if q:
        condiciones.append("(p.nombre LIKE ? OR p.marca LIKE ? OR c.nombre LIKE ?)")
        valores += [f"%{q}%"] * 3
    if categoria:
        condiciones.append("c.slug = ?"); valores.append(categoria)
    if marca:
        condiciones.append("p.marca = ?"); valores.append(marca)
    if precio_max:
        condiciones.append("p.precio <= ?"); valores.append(precio_max)
    if solo_disponibles:
        condiciones.append("p.stock > 0")
    if solo_destacados:
        condiciones.append("p.destacado = 1")
    if solo_ofertas:
        condiciones.append("p.precio_anterior IS NOT NULL AND p.precio_anterior > p.precio")
    sql = CONSULTA_PRODUCTOS + (" WHERE " + " AND ".join(condiciones) if condiciones else "")
    sql += " ORDER BY " + ORDENES.get(orden, "p.id ASC")
    return obtener_bd().execute(sql, valores).fetchall()


def obtener_producto(id_producto, incluir_ocultos=False):
    sql = CONSULTA_PRODUCTOS + " WHERE p.id = ?" + ("" if incluir_ocultos else " AND p.activo = 1")
    return obtener_bd().execute(sql, (id_producto,)).fetchone()


def listar_marcas():
    filas = obtener_bd().execute("SELECT DISTINCT marca FROM productos WHERE activo = 1 ORDER BY marca").fetchall()
    return [fila["marca"] for fila in filas]


CAMPOS = ("nombre", "marca", "categoria_id", "precio", "precio_anterior", "stock",
          "descripcion", "detalle", "especificaciones", "imagen", "destacado", "activo")


def guardar_producto(datos, id_producto=None):
    """Crea un producto nuevo (id_producto=None) o actualiza uno existente."""
    bd = obtener_bd()
    valores = [datos[campo] for campo in CAMPOS]
    if id_producto:
        bd.execute(f"UPDATE productos SET {', '.join(c + ' = ?' for c in CAMPOS)} WHERE id = ?", valores + [id_producto])
    else:
        bd.execute(f"INSERT INTO productos ({', '.join(CAMPOS)}) VALUES ({', '.join('?' * len(CAMPOS))})", valores)
    bd.commit()


# =====================================================================
# 4. AYUDAS PARA LAS PLANTILLAS HTML
# =====================================================================
@app.before_request
def verificar_csrf():
    """Protección: todo formulario POST debe traer el código secreto de la sesión."""
    if request.method == "POST":
        if not session.get("csrf") or request.form.get("csrf") != session["csrf"]:
            abort(400)


def csrf_campo():
    """Campo oculto que va dentro de cada <form method="post">."""
    session.setdefault("csrf", secrets.token_hex(16))
    return Markup(f'<input type="hidden" name="csrf" value="{session["csrf"]}">')


@app.template_filter("cop")
def formato_cop(valor):
    """3299000 -> $3.299.000"""
    return "$" + f"{int(valor):,}".replace(",", ".")


@app.template_filter("descuento")
def calcular_descuento(p):
    if p["precio_anterior"] and p["precio_anterior"] > p["precio"]:
        return round((1 - p["precio"] / p["precio_anterior"]) * 100)
    return 0


@app.template_filter("especificaciones")
def separar_especificaciones(texto):
    """'RAM: 16 GB' (una por línea) -> [('RAM', '16 GB'), ...]"""
    filas = []
    for linea in (texto or "").splitlines():
        if ":" in linea:
            nombre, valor = linea.split(":", 1)
            filas.append((nombre.strip(), valor.strip()))
    return filas


def url_imagen(p):
    """Foto del producto; si el archivo no existe, usa static/img/default.svg"""
    nombre = os.path.basename(p["imagen"] or "")
    if nombre and os.path.isfile(os.path.join(CARPETA_IMAGENES, nombre)):
        return url_for("static", filename="img/productos/" + nombre)
    return url_for("static", filename="img/default.svg")


app.jinja_env.globals.update(csrf_campo=csrf_campo, url_imagen=url_imagen)


@app.context_processor
def datos_para_todas_las_paginas():
    """Variables disponibles en TODAS las plantillas (menú, contadores, pie de página)."""
    return {"categorias": listar_categorias(), "favoritos": session.get("favoritos", []),
            "cantidad_carrito": sum(session.get("carrito", {}).values()),
            "es_admin": bool(session.get("admin"))}


# =====================================================================
# 5. PÁGINAS DE LA TIENDA
# =====================================================================
@app.route("/")
def inicio():
    return render_template("index.html", destacados=buscar_productos(solo_destacados=True)[:6],
                           ofertas=buscar_productos(solo_ofertas=True)[:3])


def mostrar_productos(titulo, solo_ofertas=False):
    """Catálogo y ofertas usan la misma lógica: leen los filtros de la URL y consultan la base de datos."""
    f = request.args
    productos = buscar_productos(
        q=f.get("q", "").strip(), categoria=f.get("cat", ""), marca=f.get("marca", ""),
        precio_max=int(f["max"]) if f.get("max", "").isdigit() else 0,
        solo_disponibles=bool(f.get("disponibles")), solo_destacados=bool(f.get("destacados")),
        solo_ofertas=solo_ofertas or bool(f.get("ofertas")), orden=f.get("orden", ""))
    return render_template("productos.html", productos=productos, filtros=f, marcas=listar_marcas(),
                           solo_ofertas=solo_ofertas, titulo_pagina=titulo, mostrar_filtros=True,
                           precios=[200000, 500000, 1000000, 2000000, 4000000])


@app.route("/productos")
def productos():
    return mostrar_productos("Catálogo de productos")


@app.route("/ofertas")
def ofertas():
    return mostrar_productos("Productos en oferta", solo_ofertas=True)


@app.route("/producto/<int:id>")
def detalle_producto(id):
    producto = obtener_producto(id)
    if not producto:
        abort(404)
    relacionados = obtener_bd().execute(
        CONSULTA_PRODUCTOS + " WHERE p.categoria_id = ? AND p.id != ? AND p.activo = 1 LIMIT 4",
        (producto["categoria_id"], id)).fetchall()
    return render_template("detalle_producto.html", p=producto, relacionados=relacionados)


# ---------- Favoritos (se guardan en la sesión del navegador) ----------
@app.route("/favorito/<int:id>", methods=["POST"])
def alternar_favorito(id):
    lista = session.get("favoritos", [])
    lista.remove(id) if id in lista else lista.append(id)
    session["favoritos"] = lista
    return redirect(request.referrer or url_for("productos"))


@app.route("/favoritos")
def favoritos():
    lista = [p for p in (obtener_producto(i) for i in session.get("favoritos", [])) if p]
    return render_template("productos.html", productos=lista, filtros={}, titulo_pagina="Mis favoritos",
                           mostrar_filtros=False, solo_ofertas=False)


# ---------- Carrito (guardado en la sesión: {id_producto: cantidad}) ----------
def leer_carrito():
    """Devuelve (artículos, total). Los precios SIEMPRE se leen de la base de datos, nunca del navegador."""
    articulos, total = [], 0
    for id_texto, cantidad in session.get("carrito", {}).items():
        producto = obtener_producto(int(id_texto))
        if producto and producto["stock"] > 0:
            cantidad = min(cantidad, producto["stock"])
            subtotal = producto["precio"] * cantidad
            articulos.append({"p": producto, "cantidad": cantidad, "subtotal": subtotal})
            total += subtotal
    return articulos, total


@app.route("/carrito")
def carrito():
    articulos, total = leer_carrito()
    return render_template("carrito.html", articulos=articulos, total=total)


@app.route("/carrito/agregar/<int:id>", methods=["POST"])
def carrito_agregar(id):
    producto = obtener_producto(id)
    if not producto or producto["stock"] < 1:
        flash("Este producto no está disponible.", "error")
        return redirect(request.referrer or url_for("productos"))
    texto = request.form.get("cantidad", "1")
    cantidad = int(texto) if texto.isdigit() and int(texto) > 0 else 1
    contenido = session.get("carrito", {})
    contenido[str(id)] = min(contenido.get(str(id), 0) + cantidad, producto["stock"])
    session["carrito"] = contenido
    flash(f"{producto['nombre']} agregado al carrito.", "ok")
    return redirect(request.referrer or url_for("productos"))


@app.route("/carrito/cambiar/<int:id>", methods=["POST"])
def carrito_cambiar(id):
    """Botones del carrito: más (+1), menos (-1) o quitar."""
    contenido = session.get("carrito", {})
    accion = request.form.get("accion")
    if str(id) in contenido:
        if accion == "mas":
            producto = obtener_producto(id)
            contenido[str(id)] = min(contenido[str(id)] + 1, producto["stock"] if producto else 1)
        elif accion == "menos":
            contenido[str(id)] -= 1
        if accion == "quitar" or contenido[str(id)] <= 0:
            del contenido[str(id)]
    session["carrito"] = contenido
    return redirect(url_for("carrito"))


@app.route("/carrito/vaciar", methods=["POST"])
def carrito_vaciar():
    session["carrito"] = {}
    return redirect(url_for("carrito"))


# ---------- Finalizar compra (DEMOSTRACIÓN: no cobra ni guarda pedidos) ----------
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    articulos, total = leer_carrito()
    if not articulos:
        return redirect(url_for("carrito"))
    if request.method == "POST":
        nombre, correo = request.form.get("nombre", "").strip(), request.form.get("correo", "").strip()
        if len(nombre) < 3 or "@" not in correo or "." not in correo.split("@")[-1]:
            flash("Escribe tu nombre (mínimo 3 letras) y un correo válido.", "error")
        else:
            session["carrito"] = {}
            return render_template("resumen.html", nombre=nombre, correo=correo, articulos=articulos, total=total)
    return render_template("checkout.html", articulos=articulos, total=total)


# ---------- Páginas de texto (los textos están en templates/info.html) ----------
@app.route("/<pagina>")
def info(pagina):
    if pagina not in ("nosotros", "contacto", "privacidad", "terminos", "cuenta"):
        abort(404)
    return render_template("info.html", pagina=pagina)


@app.errorhandler(404)
def no_encontrada(error):
    return render_template("info.html", pagina="404"), 404


@app.errorhandler(400)
def peticion_invalida(error):
    flash("La sesión expiró o el formulario no es válido. Intenta de nuevo.", "error")
    return redirect(request.referrer or url_for("inicio"))


# =====================================================================
# 6. PANEL DE ADMINISTRACIÓN (solo con sesión de administrador)
# =====================================================================
def login_requerido(funcion):
    """Si no hay sesión de administrador, manda al formulario de ingreso."""
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return funcion(*args, **kwargs)
    return envoltura


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        fila = obtener_bd().execute("SELECT * FROM usuarios WHERE nombre = ?", (request.form.get("usuario", "").strip(),)).fetchone()
        # Mismo mensaje si falla el usuario o la clave (no se dan pistas).
        if fila and fila["es_admin"] and check_password_hash(fila["clave_hash"], request.form.get("clave", "")):
            session.clear()
            session["admin"] = fila["nombre"]
            return redirect(url_for("admin"))
        flash("Usuario o contraseña incorrectos.", "error")
    return render_template("admin_login.html")


@app.route("/admin/salir", methods=["POST"])
def admin_salir():
    session.clear()
    return redirect(url_for("inicio"))


@app.route("/admin/")
@login_requerido
def admin():
    return render_template("admin.html", productos=buscar_productos(incluir_ocultos=True))


def leer_formulario(producto):
    """Lee y valida el formulario del producto. Devuelve (datos, errores)."""
    f, errores = request.form, []
    datos = {"nombre": f.get("nombre", "").strip(), "marca": f.get("marca", "").strip(),
             "descripcion": f.get("descripcion", "").strip(), "detalle": f.get("detalle", "").strip(),
             "especificaciones": f.get("especificaciones", "").strip(),
             "destacado": 1 if f.get("destacado") else 0, "activo": 1 if f.get("activo") else 0,
             "imagen": producto["imagen"] if producto else ""}
    if not datos["nombre"] or not datos["marca"]:
        errores.append("El nombre y la marca son obligatorios.")

    def numero(campo, etiqueta, obligatorio=True):
        texto = f.get(campo, "").strip()
        if not texto and not obligatorio:
            return None
        if not texto.isdigit():
            errores.append(f"{etiqueta} debe ser un número entero sin puntos ni signos.")
            return 0
        return int(texto)

    datos["precio"] = numero("precio", "El precio")
    datos["stock"] = numero("stock", "El inventario")
    datos["precio_anterior"] = numero("precio_anterior", "El precio anterior", obligatorio=False)
    categoria = f.get("categoria_id", "")
    if categoria not in [str(c["id"]) for c in listar_categorias()]:
        errores.append("Elige una categoría válida.")
    datos["categoria_id"] = int(categoria) if categoria.isdigit() else 0
    return datos, errores


def guardar_imagen(archivo):
    """Guarda la foto subida con un nombre único. Devuelve el nombre, o None si no se subió nada."""
    if not archivo or not archivo.filename:
        return None
    extension = archivo.filename.rsplit(".", 1)[-1].lower()
    if extension not in EXTENSIONES_PERMITIDAS:
        raise ValueError("La imagen debe ser PNG, JPG o WEBP.")
    nombre = f"{uuid.uuid4().hex}.{extension}"
    archivo.save(os.path.join(CARPETA_IMAGENES, nombre))
    return nombre


def borrar_imagen(nombre):
    ruta = os.path.join(CARPETA_IMAGENES, os.path.basename(nombre or ""))
    if nombre and os.path.isfile(ruta):
        os.remove(ruta)


@app.route("/admin/nuevo", methods=["GET", "POST"])
@app.route("/admin/editar/<int:id>", methods=["GET", "POST"])
@login_requerido
def admin_producto(id=None):
    """Formulario para crear (sin id) o editar (con id) un producto."""
    producto = obtener_producto(id, incluir_ocultos=True) if id else None
    if id and not producto:
        abort(404)
    if request.method == "POST":
        datos, errores = leer_formulario(producto)
        try:
            nueva_imagen = guardar_imagen(request.files.get("imagen"))
        except ValueError as error:
            errores.append(str(error)); nueva_imagen = None
        if errores:
            for error in errores:
                flash(error, "error")
            datos["id"] = id
            return render_template("admin_producto.html", p=datos, categorias=listar_categorias())
        if nueva_imagen:
            if producto:
                borrar_imagen(producto["imagen"])        # reemplaza la foto anterior
            datos["imagen"] = nueva_imagen
        guardar_producto(datos, id)
        flash("Producto guardado correctamente.", "ok")
        return redirect(url_for("admin"))
    return render_template("admin_producto.html", p=producto or {"activo": 1, "stock": 0, "destacado": 0},
                           categorias=listar_categorias())


@app.route("/admin/estado/<int:id>", methods=["POST"])
@login_requerido
def admin_estado(id):
    """Oculta o muestra un producto en la tienda (sin borrarlo)."""
    bd = obtener_bd()
    bd.execute("UPDATE productos SET activo = 1 - activo WHERE id = ?", (id,))
    bd.commit()
    return redirect(url_for("admin"))


@app.route("/admin/eliminar/<int:id>", methods=["POST"])
@login_requerido
def admin_eliminar(id):
    producto = obtener_producto(id, incluir_ocultos=True)
    if producto:
        borrar_imagen(producto["imagen"])
        bd = obtener_bd()
        bd.execute("DELETE FROM productos WHERE id = ?", (id,))
        bd.commit()
        flash("Producto eliminado.", "ok")
    return redirect(url_for("admin"))


# =====================================================================
# ARRANQUE
# =====================================================================
crear_base_de_datos()
# En un hosting sin terminal puedes crear el administrador con las variables de entorno
# ADMIN_USUARIO y ADMIN_CLAVE (ver PUBLICAR.md). En tu computador usa:  python crear_admin.py
if not hay_admin() and os.environ.get("ADMIN_CLAVE"):
    guardar_admin(os.environ.get("ADMIN_USUARIO", "admin"), os.environ["ADMIN_CLAVE"])

if __name__ == "__main__":
    # debug=True reinicia el servidor al guardar cambios. NUNCA lo dejes activo en un servidor público.
    app.run(debug=True)
