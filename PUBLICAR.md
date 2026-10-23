# Cómo publicar NexTech en Internet

## 1. Computador vs. Internet: la diferencia

| | En tu computador (`python app.py`) | Publicada en Internet |
|---|---|---|
| Dirección | `http://127.0.0.1:5000` | Una dirección pública, ej. `https://tuusuario.pythonanywhere.com` |
| ¿Quién la ve? | Solo tú, en ese computador | Cualquier persona con el enlace |
| ¿Qué debe estar encendido? | Tu computador y la terminal | Un servidor del proveedor (tú no tienes que dejar nada abierto) |
| Servidor | El de pruebas de Flask (`debug=True`) | Un servidor de producción gestionado por el proveedor |
| Datos | `nextech.db` y fotos en tu disco | `nextech.db` y fotos en el disco del proveedor (¡copias de seguridad aparte!) |

Importante: lo que cambies en tu computador **no** aparece en Internet hasta que subas los archivos de nuevo. Y los productos que edites desde el panel en Internet **no** aparecen en tu computador: son bases de datos distintas.

## 2. Comparación de opciones (datos revisados en octubre de 2026; verifica siempre en la página oficial)

| Servicio | Plan gratuito | Ventajas para NexTech | Limitaciones |
|---|---|---|---|
| **PythonAnywhere** | Sí (cuenta *Beginner*) | Hecho para Python/Flask; sin tarjeta; disco persistente, así que SQLite y las fotos subidas se conservan; dirección `usuario.pythonanywhere.com` | 512 MB de almacenamiento, CPU limitada, la app gratuita tiene fecha de vencimiento y hay que renovarla, sin dominio propio, sin acceso SSH, soporte solo de comunidad |
| **Render** | Sí (servicio web *Free*) | Se despliega desde GitHub | El servicio se «duerme» tras 15 min sin visitas (primera carga lenta) y su disco es **efímero**: se pierden `nextech.db` y las fotos al reiniciar o redesplegar. Para guardar datos necesita un plan de pago con disco o una base de datos externa |
| **Fly.io, Railway** | Sin plan gratuito permanente (créditos o planes desde unos pocos dólares al mes) | Más flexibles, buen rendimiento | Requieren tarjeta y más conocimientos (Docker / línea de comandos) |

**Recomendación para el SENA: PythonAnywhere (plan gratuito)**, porque conserva tu base de datos y tus fotos. Con Render gratis la tienda perdería los productos que edites.

## 3. Publicar en PythonAnywhere paso a paso

1. **Crear la cuenta**: entra a https://www.pythonanywhere.com → *Start running Python online* → elige la cuenta gratuita **Beginner**. Tu usuario será parte de la dirección (ej. `ana` → `ana.pythonanywhere.com`).
2. **Subir los archivos**: en tu computador comprime la carpeta `NexTech` en un `.zip` (sin las carpetas `venv` ni el archivo `nextech.db`). En PythonAnywhere abre la pestaña **Files** → *Upload a file* y sube el zip a tu carpeta personal.
3. **Descomprimir**: pestaña **Consoles** → *Bash*. Escribe:
   ```
   unzip NexTech.zip
   ```
   (Si el zip tiene otro nombre, usa ese.) Comprueba con `ls NexTech`.
4. **Dependencias**: Flask ya viene instalado en PythonAnywhere. Si pide algo más: `pip install --user -r NexTech/requirements.txt` (puede mostrar un aviso con `gunicorn`; no se necesita allí).
5. **Crear el administrador** (en la misma consola Bash):
   ```
   cd NexTech
   python crear_admin.py
   ```
   Escribe usuario y una contraseña **fuerte y distinta** a la que usas en tu computador. Esto también crea `nextech.db` con los productos de ejemplo.
6. **Crear la aplicación web**: pestaña **Web** → *Add a new web app* → *Next* → **Manual configuration** → elige la versión de Python más reciente disponible → *Next*.
7. **Indicar dónde está tu código**: en la pestaña Web, sección *Code*, escribe en *Source code*: `/home/TU_USUARIO/NexTech`.
8. **Configurar el inicio de la app**: en la sección *Code* abre el enlace **WSGI configuration file**, borra su contenido y escribe (cambia `TU_USUARIO`):
   ```python
   import sys
   ruta = "/home/TU_USUARIO/NexTech"
   if ruta not in sys.path:
       sys.path.insert(0, ruta)

   from app import app as application
   ```
   Guarda (*Save*).
9. **Archivos estáticos** (CSS, JS, imágenes): en la sección *Static files* añade: URL `/static/` → Directory `/home/TU_USUARIO/NexTech/static`.
10. **Iniciar**: arriba en la pestaña Web pulsa el botón verde **Reload**. Abre `https://TU_USUARIO.pythonanywhere.com`. Esa es la **dirección pública** que puedes compartir.
11. **Si algo falla**: en la pestaña Web abre *Error log* y lee las últimas líneas.

### Actualizar la página después
- Cambios de **productos, fotos, precios o inventario**: hazlos directamente en `https://TU_USUARIO.pythonanywhere.com/admin/login`.
- Cambios de **código, HTML o CSS**: sube de nuevo los archivos modificados (pestaña *Files*, carpeta `NexTech`, sin tocar `nextech.db` ni `static/img/productos/`) y pulsa **Reload**.

### Mantenerla disponible
- La aplicación se mantiene encendida sola (no tienes que dejar nada abierto), pero en el plan gratuito **tiene fecha de vencimiento**: entra periódicamente a la pestaña **Web** y pulsa el botón de extender la fecha. Si la dejas vencer, la página se apaga. Revisa en esa pestaña cuál es el plazo actual.
- **Copias de seguridad**: descarga de vez en cuando `NexTech/nextech.db` y la carpeta `static/img/productos/` desde la pestaña Files.
- Si necesitas dominio propio, más CPU o más espacio, hay que pasar a un plan de pago (el plan *Developer* costaba 10 USD/mes al revisar).

## 4. Antes de mostrarla al público

- Usa una contraseña de administrador larga y única.
- No subas `.clave_secreta` ni `nextech.db` de tu computador (son privados).
- Es un proyecto de demostración: **no recibas pagos reales** ni datos de tarjetas. El checkout solo genera un resumen.
- La página en Internet usa HTTPS automáticamente en la dirección `pythonanywhere.com`.
