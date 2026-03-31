"""
Supabase Storage — Helper para subir/eliminar fotografías.

Usa la REST API de Supabase Storage directamente (sin SDK).
Requiere las variables de entorno:
  SUPABASE_URL  →  https://xxxxx.supabase.co
  SUPABASE_KEY  →  anon / public key
"""

import os
import uuid
import httpx
from pathlib import Path

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
BUCKET = "fotos-contactos"

_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}


def _storage_url(path: str = "") -> str:
    return f"{SUPABASE_URL}/storage/v1/object/{path}"


async def upload_foto(file_bytes: bytes, original_filename: str) -> str:
    """
    Sube una foto a Supabase Storage y devuelve la URL pública.

    Args:
        file_bytes: contenido binario del archivo
        original_filename: nombre original (para extraer extensión)

    Returns:
        URL pública de la foto subida
    """
    ext = Path(original_filename).suffix.lower() or ".jpg"
    # Nombre único para evitar colisiones
    object_name = f"{uuid.uuid4().hex}{ext}"

    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    content_type = mime_map.get(ext, "image/jpeg")

    headers = {
        **_HEADERS,
        "Content-Type": content_type,
        "x-upsert": "true",
    }

    url = _storage_url(f"{BUCKET}/{object_name}")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, content=file_bytes, headers=headers)
        resp.raise_for_status()

    # URL pública
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{object_name}"
    return public_url


async def delete_foto(foto_url: str) -> None:
    """
    Elimina una foto de Supabase Storage dada su URL pública.
    No lanza error si la foto no existe.
    """
    if not foto_url or BUCKET not in foto_url:
        return

    # Extraer el nombre del objeto de la URL
    # URL: https://xxx.supabase.co/storage/v1/object/public/fotos-contactos/abc123.jpg
    try:
        object_name = foto_url.split(f"{BUCKET}/")[-1]
    except (IndexError, ValueError):
        return

    headers = {**_HEADERS, "Content-Type": "application/json"}
    url = _storage_url(f"{BUCKET}")

    async with httpx.AsyncClient(timeout=15) as client:
        # La API de delete usa un body con prefixes
        resp = await client.request(
            "DELETE",
            f"{SUPABASE_URL}/storage/v1/object/{BUCKET}",
            headers=headers,
            json={"prefixes": [object_name]},
        )
        # Ignorar errores silenciosamente (la foto puede no existir)
        if resp.status_code not in (200, 204, 404):
            pass  # log en producción


def is_configured() -> bool:
    """Verifica si las credenciales de Supabase están configuradas."""
    return bool(SUPABASE_URL and SUPABASE_KEY)
