# 📒 Gestión de Contactos — Despliegue en Render

Aplicación Full Stack (FastAPI + PostgreSQL) desplegada en [Render.com](https://render.com).

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend + Frontend | FastAPI (Python 3.12) |
| Base de datos | PostgreSQL 16 (Render managed) |
| Hosting | Render Web Service |
| CI/CD | GitHub → Render (auto-deploy en push) |

## Estructura del Proyecto

```
contactos-render/
├── main.py           # API REST + sirve el frontend
├── models.py         # Tablas SQLAlchemy (UUID como PK)
├── schemas.py        # Validación Pydantic
├── database.py       # Conexión PostgreSQL via DATABASE_URL
├── requirements.txt  # Dependencias Python
├── render.yaml       # Blueprint de infraestructura Render
├── .gitignore
└── frontend/
    └── index.html    # SPA completa (HTML/CSS/JS)
```

> **Nota sobre fotografías:** Las fotos se almacenan como `base64` directamente
> en PostgreSQL, lo que garantiza persistencia aunque Render reinicie el servicio
> (el filesystem de Render es efímero en el plan gratuito).

---

## 🚀 Despliegue en Render — Paso a Paso

### Opción A: Blueprint automático (recomendado)

1. Sube el código a GitHub
2. En [render.com](https://render.com) → **New** → **Blueprint**
3. Conecta tu repo → Render lee `render.yaml` y crea todo automáticamente

### Opción B: Manual (paso a paso detallado)

#### 1. Preparar el repositorio en GitHub

```bash
git init
git add .
git commit -m "feat: initial commit - gestión de contactos"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/contactos-app.git
git push -u origin main
```

#### 2. Crear la base de datos PostgreSQL en Render

1. Ir a [dashboard.render.com](https://dashboard.render.com)
2. Click **New +** → **PostgreSQL**
3. Configurar:
   - **Name:** `contactos-db`
   - **Database:** `contactos_db`
   - **User:** `contactos_user`
   - **Region:** Oregon (US West) — el más cercano disponible en plan free
   - **Plan:** Free
4. Click **Create Database**
5. Guardar el **Internal Database URL** (lo necesitas en el paso siguiente)

#### 3. Crear el Web Service en Render

1. Click **New +** → **Web Service**
2. Conectar tu repositorio de GitHub
3. Configurar:
   - **Name:** `contactos-app`
   - **Region:** Oregon (US West) — **igual que la BD**
   - **Branch:** `main`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
4. En la sección **Environment Variables**, agregar:
   - Key: `DATABASE_URL`
   - Value: pegar el **Internal Database URL** copiado del paso anterior
5. Click **Create Web Service**

#### 4. Verificar el despliegue

Render tardará ~2-3 minutos en el primer build. Cuando diga **Live**:

- Frontend: `https://contactos-app.onrender.com`
- API Docs: `https://contactos-app.onrender.com/docs`

#### 5. Auto-deploy (CI/CD automático)

Cada `git push` a `main` dispara un nuevo deploy automáticamente:

```bash
# Flujo de trabajo en equipo
git checkout -b feature/nueva-funcionalidad
# ... hacer cambios ...
git add . && git commit -m "feat: descripción del cambio"
git push origin feature/nueva-funcionalidad
# Crear Pull Request en GitHub → merge a main → Render despliega
```

---

## Desarrollo Local

```bash
# Requiere Python 3.12+ y PostgreSQL local, o usar Docker solo para la BD:
docker run -d --name pg -e POSTGRES_DB=contactos_db \
  -e POSTGRES_USER=contactos_user \
  -e POSTGRES_PASSWORD=contactos_pass \
  -p 5432:5432 postgres:16-alpine

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
DATABASE_URL=postgresql://contactos_user:contactos_pass@localhost:5432/contactos_db \
  uvicorn main:app --reload

# Abrir http://localhost:8000
```

---

## API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/grupos` | Listar grupos |
| POST | `/grupos` | Crear grupo |
| PUT | `/grupos/{id}` | Actualizar grupo |
| DELETE | `/grupos/{id}` | Eliminar grupo |
| GET | `/personas` | Listar personas |
| POST | `/personas` | Crear persona (con foto) |
| GET | `/personas/{id}` | Obtener persona |
| PUT | `/personas/{id}` | Actualizar persona |
| DELETE | `/personas/{id}` | Eliminar persona |

---

## Equipo — LG3 Cloud Computing 2026
