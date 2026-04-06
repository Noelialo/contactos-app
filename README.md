# 📒 Gestión de Contactos

**Aplicación Full Stack** para gestión de un directorio de contactos con fotografías, desarrollada con **FastAPI + PostgreSQL + Supabase**, desplegada en **Render.com**.

> 🌐 **Demo en vivo:** [contactos-app-c3h3.onrender.com](https://contactos-app-c3h3.onrender.com)

---

## 📸 Screenshots

| Vista Personas (Galería) | Vista Grupos | Detalle de Contacto |
|:---:|:---:|:---:|
| Grid responsivo con tarjetas | Tabla con estado y contador | Modal con foto ampliada y UUID |

---

## ✨ Funcionalidades

- ✅ **CRUD completo** de Personas y Grupos
- ✅ **UUID v4** como identificador interno de cada registro
- ✅ **Fotografías** almacenadas en Supabase Storage (bucket público)
- ✅ **Relación 1:N** — Un grupo tiene muchas personas
- ✅ **Vista Galería** — Tarjetas con foto, nombre, grupo y datos
- ✅ **Vista Lista** — Tabla ordenada con acciones
- ✅ **Detalle** — Modal completo con todos los datos y UUID visible
- ✅ **Búsqueda en tiempo real** por nombre, apellido y correo
- ✅ **Estadísticas** — Total contactos, activos y grupos
- ✅ **Responsive** — Funciona en desktop, tablet y celular
- ✅ **PWA** — Instalable como app nativa en dispositivos móviles
- ✅ **Protección de integridad** — No permite eliminar grupos con personas

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Versión | Rol |
|------|-----------|---------|-----|
| Backend | FastAPI | 0.111 | API REST + sirve HTML |
| Runtime | Python | 3.12 | Lenguaje principal |
| ORM | SQLAlchemy | 2.0 | Mapeo objeto-relacional |
| Validación | Pydantic | 2.7 | Esquemas de validación |
| Base de Datos | PostgreSQL (Supabase) | 15 | Datos de contactos y grupos |
| Almacenamiento | Supabase Storage | — | Fotografías |
| Servidor | Uvicorn | 0.29 | ASGI server producción |
| Hosting | Render.com | free | Plataforma PaaS |
| HTTP Client | httpx | 0.27 | Comunicación con Supabase |

---

## 📁 Estructura del Proyecto

```
contactos-app/
├── .env.example          # Template de variables de entorno
├── .gitignore            # Archivos excluidos
├── .python-version       # Pin Python 3.12.3
├── database.py           # Conexión SQLAlchemy + dotenv
├── main.py               # API REST + rutas frontend
├── models.py             # Modelos ORM (Grupo, Persona)
├── schemas.py            # Esquemas Pydantic
├── render.yaml           # Blueprint Render
├── requirements.txt      # Dependencias Python
├── supabase_storage.py   # Helper Supabase Storage API
└── frontend/
    ├── index.html        # SPA completa
    ├── manifest.json     # Manifest PWA
    ├── sw.js             # Service Worker
    ├── icon-192.png      # Icono PWA 192×192
    └── icon-512.png      # Icono PWA 512×512
```

---

## 🚀 Despliegue Rápido

### Variables de Entorno Requeridas

```env
DATABASE_URL=postgresql://user:pass@host:6543/postgres
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_anon_key
```

### Local

```bash
# 1. Clonar
git clone https://github.com/Noelialo/contactos-app.git
cd contactos-app

# 2. Entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Dependencias
pip install -r requirements.txt

# 4. Variables de entorno
cp .env.example .env   # Editar con tus credenciales

# 5. Ejecutar
uvicorn main:app --reload --port 8000
```

### Render.com

1. Conectar repo GitHub → **New Web Service**
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Agregar variables de entorno (DATABASE_URL, SUPABASE_URL, SUPABASE_KEY)
5. Deploy 🚀

---

## 📊 Modelo de Datos

```
┌─────────────────┐        ┌──────────────────────┐
│     GRUPOS      │        │      PERSONAS        │
├─────────────────┤        ├──────────────────────┤
│ codigo (PK/UUID)│───1:N─▶│ codigo (PK/UUID)     │
│ grupo           │        │ nombres              │
│ esta_activo     │        │ apellidos            │
└─────────────────┘        │ correo               │
                           │ nro_celular          │
                           │ direccion            │
                           │ observaciones        │
                           │ fotografia (URL)     │
                           │ esta_activo          │
                           │ grupo_codigo (FK)    │
                           └──────────────────────┘
```

---

## 📝 Licencia

Proyecto académico — LG3 Cloud Computing · UNIVALLE · 2026
