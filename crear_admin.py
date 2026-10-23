"""Crea (o cambia) el usuario administrador de NexTech.
Uso:  python crear_admin.py
"""
import getpass
from app import guardar_admin, hay_admin

nombre = input("Nombre del administrador [admin]: ").strip() or "admin"
while True:
    clave = getpass.getpass("Contraseña (mínimo 8 caracteres): ")
    if len(clave) >= 8 and clave == getpass.getpass("Repite la contraseña: "):
        break
    print("La contraseña es muy corta o no coincide. Intenta de nuevo.")
guardar_admin(nombre, clave)
print(f"Listo. Ahora ingresa en http://127.0.0.1:5000/admin/login con el usuario «{nombre}».")
