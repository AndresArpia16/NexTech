# NexTech · Tienda virtual (Python + Flask + HTML + CSS)

Proyecto formativo SENA. No usa React, JSX, TypeScript ni Node.js: solo **Python**, **HTML**, **CSS** y un poco de **JavaScript básico**. Todos los productos son **datos de demostración**.

> Para publicarla en Internet lee `PUBLICAR.md`.

---

## 1. Qué cambió respecto a la versión React

| Antes (React) | Ahora (Flask) |
|---|---|
| Archivos `.jsx` y componentes | Archivos `.html` en `templates/` |
| `npm`, Vite, Node.js | Solo Python y `pip` |
| Productos en archivos `.js` | Productos de ejemplo en `app.py` y luego en SQLite |
| Carrito en el navegador | Carrito en la sesión del servidor, con precios leídos de la base de datos |
| Sin panel de administración | Panel protegido en `/admin` |

Se conservaron: diseño oscuro azul eléctrico, buscador, filtros, ordenamiento, categorías, ofertas, favoritos, detalle con productos relacionados, carrito y compra de demostración.

---

## 2. Estructura

```
NexTech/
├── app.py                 ← Lógica principal: rutas, productos de ejemplo, base de datos, panel admin
├── crear_admin.py         ← Crea tu usuario administrador
├── requirements.txt       ← Librerías necesarias (Flask)
├── templates/             ← Páginas HTML
│   ├── base.html          ← Menú y pie de página (se repite en todas las páginas)
│   ├── index.html         ← Página de inicio  ← aquí cambias los textos principales
│   ├── productos.html     ← Catálogo, ofertas y favoritos (con buscador y filtros)
│   ├── detalle_producto.html
│   ├── carrito.html  checkout.html  resumen.html
│   ├── info.html          ← Textos de Nosotros, Contacto, Privacidad, Términos
│   ├── admin.html  admin_login.html  admin_producto.html   ← Panel de administración
│   └── partials/_tarjeta.html  ← Diseño de la tarjeta de producto (una sola vez)
└── static/
    ├── css/style.css      ← Colores, tamaños, espacios, tarjetas, botones, celulares
    ├── js/script.js       ← JavaScript básico (menú móvil, confirmar eliminar, vista previa de foto)
    └── img/               ← default.svg (imagen cuando falta una foto)
        └── productos/     ← Fotos de los productos
```
`base.html` y `partials/` son archivos extra que se añadieron para no repetir el menú ni la tarjeta en cada página.

---

## 3. Ejecutar en Windows (en tu computador)

1. **Instalar Python**: entra a https://www.python.org/downloads/ → *Download Python 3.x* → abre el instalador y **marca la casilla «Add python.exe to PATH»** → *Install Now*. Comprueba en una terminal con `python --version`.
2. **Abrir la carpeta en Visual Studio Code**: descomprime `NexTech.zip` → abre VS Code → menú *Archivo > Abrir carpeta…* → elige la carpeta `NexTech`.
3. **Abrir la terminal**: menú *Terminal > Nuevo terminal* (o `Ctrl + ñ`). Debe mostrar la ruta de `NexTech`.
4. **Instalar las dependencias** (solo la primera vez):
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
   Si PowerShell bloquea `activate`, ejecuta una vez: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y repite.
5. **Crear el administrador** (solo la primera vez): `python crear_admin.py` y escribe usuario y contraseña (mínimo 8 caracteres).
6. **Ejecutar**: `python app.py`
7. **Ver la página**: abre en el navegador **http://127.0.0.1:5000**. El panel está en **http://127.0.0.1:5000/admin/login** (o el icono 👤).
8. **Detener el servidor**: en la terminal pulsa `Ctrl + C`.
9. **Ver tus cambios**: con `python app.py` el servidor se reinicia solo al guardar un archivo `.py`. Para HTML y CSS guarda el archivo (`Ctrl + S`) y recarga el navegador (`Ctrl + F5` para ignorar la caché).

Cada vez que vuelvas a trabajar: abre la carpeta, abre la terminal, ejecuta `venv\Scripts\activate` y luego `python app.py`.

---

## 4. Dónde cambiar cada cosa

| Quiero cambiar… | Archivo | Cómo |
|---|---|---|
| Títulos, subtítulos, textos de botones, secciones de inicio | `templates/index.html` | Edita el texto entre las etiquetas HTML |
| Menú y pie de página | `templates/base.html` | |
| Textos de Nosotros, Contacto, etc. | `templates/info.html` | Diccionario `textos` al inicio |
| Colores | `static/css/style.css` | Variables al inicio (`:root`): `--ac` es el azul eléctrico, `--bg` el fondo |
| Tamaño de letra, márgenes | `static/css/style.css` | `body`, `h1`, `h2`, `.wrap`, `section` |
| Tamaño de tarjetas y cuadrícula | `static/css/style.css` | `.grid` (`minmax(250px,1fr)` = ancho mínimo de la tarjeta) y `.pic` (alto de la foto) |
| Botones | `static/css/style.css` | `.btn` y `.btn.p` |
| Celulares | `static/css/style.css` | Reglas `@media (max-width:...)` |
| Diseño de la tarjeta de producto | `templates/partials/_tarjeta.html` | Cambia todas las tarjetas a la vez |
| Categorías de ejemplo | `app.py` | Lista `CATEGORIAS` |
| Rutas y funciones | `app.py` | Secciones 5 y 6 |

---

## 5. Productos, imágenes e inventario

### Desde el navegador (recomendado)
Ingresa a `/admin/login`. En el panel puedes:
- **+ Nuevo producto**: nombre, marca, categoría, precio (solo números, ej. `2599000`), inventario, descripciones, características (una por línea: `RAM: 16 GB`) y foto.
- **Editar**: cambiar cualquier dato, **reemplazar la imagen** (la anterior se borra) y actualizar el inventario.
- **Oferta**: llena *Precio anterior* con un valor mayor al precio; el descuento se calcula solo.
- **Ocultar / Mostrar**: quita o devuelve un producto a la tienda sin borrarlo. **Eliminar** lo borra para siempre.

Solo el administrador con contraseña puede hacerlo; los visitantes no pueden modificar nada.

### Cómo funcionan los productos de ejemplo de `app.py` y la migración a SQLite
- La lista `PRODUCTOS_DEMO` de `app.py` es el punto de partida. **La primera vez** que ejecutas la página, `crear_base_de_datos()` la copia al archivo `nextech.db` (SQLite). Esa es la migración: ya no es necesario editar Python para cambiar productos.
- Después, **la fuente de verdad es `nextech.db`**: editar `PRODUCTOS_DEMO` ya no cambia la tienda. Si quieres recargar los ejemplos desde cero: detén el servidor, borra `nextech.db` y ejecútalo de nuevo (volverás a crear el administrador con `python crear_admin.py`).
- Si prefieres poner una foto a mano: copia el archivo a `static/img/productos/` (ej. `portatil1.jpg`) y escribe ese nombre en el campo `"imagen"` del producto en `PRODUCTOS_DEMO` (antes de crear la base) o súbela desde el panel.
- Si una imagen no existe se muestra `static/img/default.svg`. Las fotos se ajustan con `object-fit: contain` para que no se deformen.

### Migrar luego a MySQL o PostgreSQL
Todas las consultas están en la sección 3 de `app.py`. Cambia la conexión (`obtener_bd`) por la librería del otro motor (por ejemplo `pymysql` o `psycopg`) y ajusta los marcadores `?` por `%s`. Las tablas están descritas en `ESTRUCTURA_SQL`.

---

## 6. Seguridad incluida

Contraseña con hash (nunca en texto plano), panel protegido con sesión, protección CSRF en todos los formularios, consultas SQL con parámetros, subida de fotos limitada a PNG/JPG/WEBP de máx. 3 MB con nombre aleatorio, y precios del carrito siempre leídos de la base de datos.

## 7. Ideas para seguir

Cuentas de clientes, guardar pedidos en una tabla `pedidos`, pasarela de pago autorizada, límite de intentos de ingreso y administración de categorías desde el panel.
