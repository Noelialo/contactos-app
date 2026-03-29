from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import uuid, os
from pathlib import Path
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db, engine
import models, schemas
import supabase_storage

# Crear tablas (si no existen)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestión de Contactos API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorio base del proyecto (donde está main.py)
BASE_DIR = Path(__file__).parent

# Servir frontend estático
FRONTEND_DIR = BASE_DIR / "frontend"

# Montar archivos estáticos del frontend (manifest.json, sw.js, etc.)
STATIC_DIR = FRONTEND_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── HELPERS ────────────────────────────────────────────────────────────────

MAX_FOTO_SIZE = 2 * 1024 * 1024  # 2 MB


def parse_bool(value: str) -> bool:
    """Parsea string del formulario a bool real."""
    return value.lower() in ("true", "1", "yes", "on")


# ── RUTAS FRONTEND ────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/manifest.json")
def manifest():
    return FileResponse(str(FRONTEND_DIR / "manifest.json"))


@app.get("/sw.js")
def service_worker():
    return FileResponse(str(FRONTEND_DIR / "sw.js"), media_type="application/javascript")


# ── HEALTH ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}


# ── GRUPOS ─────────────────────────────────────────────────────────────────

@app.get("/grupos", response_model=list[schemas.GrupoOut])
def listar_grupos(db: Session = Depends(get_db)):
    return db.query(models.Grupo).all()


@app.get("/grupos/{grupo_id}", response_model=schemas.GrupoOut)
def obtener_grupo(grupo_id: str, db: Session = Depends(get_db)):
    g = db.query(models.Grupo).filter(models.Grupo.codigo == grupo_id).first()
    if not g:
        raise HTTPException(404, "Grupo no encontrado")
    return g


@app.post("/grupos", response_model=schemas.GrupoOut, status_code=201)
def crear_grupo(grupo: schemas.GrupoCreate, db: Session = Depends(get_db)):
    db_grupo = models.Grupo(
        codigo=str(uuid.uuid4()),
        grupo=grupo.grupo,
        esta_activo=grupo.esta_activo
    )
    db.add(db_grupo)
    db.commit()
    db.refresh(db_grupo)
    return db_grupo


@app.put("/grupos/{grupo_id}", response_model=schemas.GrupoOut)
def actualizar_grupo(grupo_id: str, grupo: schemas.GrupoCreate, db: Session = Depends(get_db)):
    g = db.query(models.Grupo).filter(models.Grupo.codigo == grupo_id).first()
    if not g:
        raise HTTPException(404, "Grupo no encontrado")
    g.grupo = grupo.grupo
    g.esta_activo = grupo.esta_activo
    db.commit()
    db.refresh(g)
    return g


@app.delete("/grupos/{grupo_id}")
def eliminar_grupo(grupo_id: str, db: Session = Depends(get_db)):
    g = db.query(models.Grupo).filter(models.Grupo.codigo == grupo_id).first()
    if not g:
        raise HTTPException(404, "Grupo no encontrado")

    # Verificar si el grupo tiene personas asociadas
    count = db.query(models.Persona).filter(
        models.Persona.grupo_codigo == grupo_id
    ).count()
    if count > 0:
        raise HTTPException(
            400,
            f"No se puede eliminar: el grupo tiene {count} persona(s) asociada(s). "
            "Reasigne o elimine las personas primero."
        )

    db.delete(g)
    db.commit()
    return {"mensaje": "Grupo eliminado"}


# ── PERSONAS ───────────────────────────────────────────────────────────────

@app.get("/personas", response_model=list[schemas.PersonaOut])
def listar_personas(db: Session = Depends(get_db)):
    return db.query(models.Persona).all()


@app.get("/personas/{persona_id}", response_model=schemas.PersonaOut)
def obtener_persona(persona_id: str, db: Session = Depends(get_db)):
    p = db.query(models.Persona).filter(models.Persona.codigo == persona_id).first()
    if not p:
        raise HTTPException(404, "Persona no encontrada")
    return p


@app.post("/personas", response_model=schemas.PersonaOut, status_code=201)
async def crear_persona(
    nombres: str = Form(...),
    apellidos: str = Form(...),
    correo: str = Form(...),
    nro_celular: str = Form(""),
    direccion: str = Form(""),
    observaciones: Optional[str] = Form(None),
    esta_activo: str = Form("true"),
    grupo_codigo: str = Form(...),
    fotografia: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    grupo = db.query(models.Grupo).filter(models.Grupo.codigo == grupo_codigo).first()
    if not grupo:
        raise HTTPException(400, "Grupo no existe")

    # Procesar foto
    foto_url = None
    if fotografia and fotografia.filename:
        content = await fotografia.read()

        # Validar tamaño
        if len(content) > MAX_FOTO_SIZE:
            raise HTTPException(400, "La foto excede el tamaño máximo de 2 MB")

        # Subir a Supabase Storage
        if supabase_storage.is_configured():
            foto_url = await supabase_storage.upload_foto(content, fotografia.filename)
        else:
            # Fallback: base64 para desarrollo local sin Supabase
            import base64
            ext = Path(fotografia.filename).suffix.lower().lstrip(".")
            mime = f"image/{ext}" if ext in ("jpg", "jpeg", "png", "webp", "gif") else "image/jpeg"
            foto_url = f"data:{mime};base64,{base64.b64encode(content).decode()}"

    persona = models.Persona(
        codigo=str(uuid.uuid4()),
        nombres=nombres,
        apellidos=apellidos,
        correo=correo,
        nro_celular=nro_celular,
        direccion=direccion,
        observaciones=observaciones,
        esta_activo=parse_bool(esta_activo),
        grupo_codigo=grupo_codigo,
        fotografia=foto_url
    )
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona


@app.put("/personas/{persona_id}", response_model=schemas.PersonaOut)
async def actualizar_persona(
    persona_id: str,
    nombres: str = Form(...),
    apellidos: str = Form(...),
    correo: str = Form(...),
    nro_celular: str = Form(""),
    direccion: str = Form(""),
    observaciones: Optional[str] = Form(None),
    esta_activo: str = Form("true"),
    grupo_codigo: str = Form(...),
    fotografia: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    p = db.query(models.Persona).filter(models.Persona.codigo == persona_id).first()
    if not p:
        raise HTTPException(404, "Persona no encontrada")

    grupo = db.query(models.Grupo).filter(models.Grupo.codigo == grupo_codigo).first()
    if not grupo:
        raise HTTPException(400, "Grupo no existe")

    # Procesar nueva foto si se proporcionó
    if fotografia and fotografia.filename:
        content = await fotografia.read()

        if len(content) > MAX_FOTO_SIZE:
            raise HTTPException(400, "La foto excede el tamaño máximo de 2 MB")

        # Eliminar foto anterior de Supabase si existe
        if p.fotografia and supabase_storage.is_configured():
            await supabase_storage.delete_foto(p.fotografia)

        # Subir nueva foto
        if supabase_storage.is_configured():
            p.fotografia = await supabase_storage.upload_foto(content, fotografia.filename)
        else:
            import base64
            ext = Path(fotografia.filename).suffix.lower().lstrip(".")
            mime = f"image/{ext}" if ext in ("jpg", "jpeg", "png", "webp", "gif") else "image/jpeg"
            p.fotografia = f"data:{mime};base64,{base64.b64encode(content).decode()}"

    p.nombres = nombres
    p.apellidos = apellidos
    p.correo = correo
    p.nro_celular = nro_celular
    p.direccion = direccion
    p.observaciones = observaciones
    p.esta_activo = parse_bool(esta_activo)
    p.grupo_codigo = grupo_codigo
    db.commit()
    db.refresh(p)
    return p


@app.delete("/personas/{persona_id}")
async def eliminar_persona(persona_id: str, db: Session = Depends(get_db)):
    p = db.query(models.Persona).filter(models.Persona.codigo == persona_id).first()
    if not p:
        raise HTTPException(404, "Persona no encontrada")

    # Eliminar foto de Supabase si existe
    if p.fotografia and supabase_storage.is_configured():
        await supabase_storage.delete_foto(p.fotografia)

    db.delete(p)
    db.commit()
    return {"mensaje": "Persona eliminada"}
