from pydantic import BaseModel
from typing import Optional


class GrupoCreate(BaseModel):
    grupo: str
    esta_activo: bool = True


class GrupoOut(BaseModel):
    codigo: str
    grupo: str
    esta_activo: bool

    class Config:
        from_attributes = True


class PersonaOut(BaseModel):
    codigo: str
    nombres: str
    apellidos: str
    correo: str
    nro_celular: Optional[str]
    direccion: Optional[str]
    observaciones: Optional[str]
    fotografia: Optional[str]
    esta_activo: bool
    grupo_codigo: str
    grupo: Optional[GrupoOut]

    class Config:
        from_attributes = True
