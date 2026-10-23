"""Todas las consultas a la base de datos están aquí.
Si cambias de SQLite a MySQL/PostgreSQL, solo tendrás que modificar este archivo."""
import os
import sqlite3
from flask import g

RUTA_BD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "nextech.db")


def obtener_bd():
    """Abre la conexión una vez por petición."""
    if "bd" not in g:
        g.bd = sqlite3.connect(RUTA_BD)
        g.bd.row_factory = sqlite3.Row   # permite usar fila["nombre"]
    return g.bd


def cerrar_bd(error=None):
    bd = g.pop("bd", None)
    if bd is not None:
        bd.close()


# ---------- Categorías ----------
def listar_categorias():
    return obtener_bd().execute("SELECT * FROM categorias ORDER BY id").fetchall()


# ---------- Productos (consultas de la tienda) ----------
CONSULTA_BASE = """SELECT p.*, c.nombre AS categoria, c.slug AS categoria_slug
                   FROM productos p JOIN categorias c ON c.id = p.categoria_id"""

ORDENES = {"precio_asc": "p.precio ASC", "precio_desc": "p.precio DESC", "nombre": "p.nombre COLLATE NOCASE ASC"}


def buscar_productos(q="", categoria="", marca="", precio_max=0, solo_disponibles=False,
                     solo_destacados=False, solo_ofertas=False, orden="", incluir_ocultos=False):
    """Busca productos aplicando los filtros. Los valores siempre van como parámetros (?) para evitar inyección SQL."""
    condiciones, valores = [], []
    if not incluir_ocultos:
        condiciones.append("p.activo = 1")
    if q:
        condiciones.append("(p.nombre LIKE ? OR p.marca LIKE ? OR c.nombre LIKE ?)")
        valores += [f"%{q}%", f"%{q}%", f"%{q}%"]
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
    sql = CONSULTA_BASE + (" WHERE " + " AND ".join(condiciones) if condiciones else "")
    sql += " ORDER BY " + ORDENES.get(orden, "p.id ASC")
    return obtener_bd().execute(sql, valores).fetchall()


def obtener_producto(id_producto, incluir_ocultos=False):
    sql = CONSULTA_BASE + " WHERE p.id = ?" + ("" if incluir_ocultos else " AND p.activo = 1")
    return obtener_bd().execute(sql, (id_producto,)).fetchone()


def productos_relacionados(producto, limite=4):
    return obtener_bd().execute(
        CONSULTA_BASE + " WHERE p.categoria_id = ? AND p.id != ? AND p.activo = 1 LIMIT ?",
        (producto["categoria_id"], producto["id"], limite)).fetchall()


def listar_marcas():
    filas = obtener_bd().execute("SELECT DISTINCT marca FROM productos WHERE activo = 1 ORDER BY marca").fetchall()
    return [f["marca"] for f in filas]


# ---------- Productos (administración) ----------
CAMPOS = ("nombre", "marca", "categoria_id", "precio", "precio_anterior", "stock",
          "descripcion", "detalle", "especificaciones", "imagen", "destacado", "activo")


def crear_producto(datos):
    bd = obtener_bd()
    cursor = bd.execute(f"INSERT INTO productos ({', '.join(CAMPOS)}) VALUES ({', '.join('?' * len(CAMPOS))})",
                        [datos[c] for c in CAMPOS])
    bd.commit()
    return cursor.lastrowid


def actualizar_producto(id_producto, datos):
    bd = obtener_bd()
    asignaciones = ", ".join(f"{c} = ?" for c in CAMPOS)
    bd.execute(f"UPDATE productos SET {asignaciones} WHERE id = ?", [datos[c] for c in CAMPOS] + [id_producto])
    bd.commit()


def cambiar_estado(id_producto):
    """Oculta o muestra un producto en la tienda (sin borrarlo)."""
    bd = obtener_bd()
    bd.execute("UPDATE productos SET activo = 1 - activo WHERE id = ?", (id_producto,))
    bd.commit()


def eliminar_producto(id_producto):
    bd = obtener_bd()
    bd.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
    bd.commit()


# ---------- Usuarios ----------
def obtener_usuario(nombre):
    return obtener_bd().execute("SELECT * FROM usuarios WHERE nombre = ?", (nombre,)).fetchone()
