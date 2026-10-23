"""Panel de administración (protegido con inicio de sesión)."""
import os
import uuid
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort, current_app
from werkzeug.security import check_password_hash
import base_datos as bd

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "webp"}


def carpeta_imagenes():
    return os.path.join(current_app.static_folder, "img", "productos")


def login_requerido(funcion):
    """Si no hay sesión de administrador, manda al formulario de ingreso."""
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin.login"))
        return funcion(*args, **kwargs)
    return envoltura


# ---------- Ingreso y salida ----------
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = bd.obtener_usuario(request.form.get("usuario", "").strip())
        clave = request.form.get("clave", "")
        # Mismo mensaje si falla el usuario o la clave (no se da pistas).
        if usuario and usuario["es_admin"] and check_password_hash(usuario["clave_hash"], clave):
            session.clear()
            session["admin"] = usuario["nombre"]
            return redirect(url_for("admin.lista"))
        flash("Usuario o contraseña incorrectos.", "error")
    return render_template("admin/login.html")


@admin_bp.route("/salir", methods=["POST"])
def salir():
    session.clear()
    return redirect(url_for("inicio"))


# ---------- Lista de productos ----------
@admin_bp.route("/")
@login_requerido
def lista():
    productos = bd.buscar_productos(incluir_ocultos=True)
    return render_template("admin/lista.html", productos=productos)


# ---------- Crear y editar ----------
def leer_formulario(producto=None):
    """Lee y valida los campos del formulario. Devuelve (datos, errores)."""
    f, errores = request.form, []
    datos = {
        "nombre": f.get("nombre", "").strip(),
        "marca": f.get("marca", "").strip(),
        "descripcion": f.get("descripcion", "").strip(),
        "detalle": f.get("detalle", "").strip(),
        "especificaciones": f.get("especificaciones", "").strip(),
        "destacado": 1 if f.get("destacado") else 0,
        "activo": 1 if f.get("activo") else 0,
        "imagen": producto["imagen"] if producto else "",
    }
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
    if categoria not in [str(c["id"]) for c in bd.listar_categorias()]:
        errores.append("Elige una categoría válida.")
    datos["categoria_id"] = int(categoria) if categoria.isdigit() else 0
    return datos, errores


def guardar_imagen(archivo):
    """Guarda la imagen subida con un nombre único. Devuelve el nombre o None."""
    if not archivo or not archivo.filename:
        return None
    extension = archivo.filename.rsplit(".", 1)[-1].lower()
    if extension not in EXTENSIONES_PERMITIDAS:
        raise ValueError("La imagen debe ser PNG, JPG o WEBP.")
    nombre = f"{uuid.uuid4().hex}.{extension}"
    archivo.save(os.path.join(carpeta_imagenes(), nombre))
    return nombre


def borrar_imagen(nombre):
    if nombre:
        ruta = os.path.join(carpeta_imagenes(), os.path.basename(nombre))
        if os.path.isfile(ruta):
            os.remove(ruta)


@admin_bp.route("/nuevo", methods=["GET", "POST"])
@admin_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@login_requerido
def formulario(id=None):
    producto = bd.obtener_producto(id, incluir_ocultos=True) if id else None
    if id and not producto:
        abort(404)
    if request.method == "POST":
        datos, errores = leer_formulario(producto)
        try:
            nueva = guardar_imagen(request.files.get("imagen"))
        except ValueError as e:
            errores.append(str(e)); nueva = None
        if errores:
            for e in errores:
                flash(e, "error")
            datos["id"] = id
            return render_template("admin/formulario.html", p=datos, categorias=bd.listar_categorias())
        if nueva:
            if producto:
                borrar_imagen(producto["imagen"])   # reemplaza la foto anterior
            datos["imagen"] = nueva
        if producto:
            bd.actualizar_producto(id, datos)
        else:
            bd.crear_producto(datos)
        flash("Producto guardado correctamente.", "ok")
        return redirect(url_for("admin.lista"))
    valores = producto or {"activo": 1, "stock": 0, "destacado": 0}
    return render_template("admin/formulario.html", p=valores, categorias=bd.listar_categorias())


# ---------- Ocultar y eliminar ----------
@admin_bp.route("/estado/<int:id>", methods=["POST"])
@login_requerido
def estado(id):
    bd.cambiar_estado(id)
    return redirect(url_for("admin.lista"))


@admin_bp.route("/eliminar/<int:id>", methods=["POST"])
@login_requerido
def eliminar(id):
    producto = bd.obtener_producto(id, incluir_ocultos=True)
    if producto:
        borrar_imagen(producto["imagen"])
        bd.eliminar_producto(id)
        flash("Producto eliminado.", "ok")
    return redirect(url_for("admin.lista"))
