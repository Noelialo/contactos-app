from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class Grupo(Base):
    __tablename__ = "grupos"

    codigo      = Column(String(36), primary_key=True, index=True)
    grupo       = Column(String(120), nullable=False)
    esta_activo = Column(Boolean, default=True)

    personas = relationship("Persona", back_populates="grupo")


class Persona(Base):
    __tablename__ = "personas"

    codigo        = Column(String(36), primary_key=True, index=True)
    nombres       = Column(String(150), nullable=False)
    apellidos     = Column(String(150), nullable=False)
    correo        = Column(String(200), nullable=False)
    nro_celular   = Column(String(30))
    direccion     = Column(String(250))
    observaciones = Column(Text)
    fotografia    = Column(String(500))     # URL pública de Supabase Storage
    esta_activo   = Column(Boolean, default=True)
    grupo_codigo  = Column(String(36), ForeignKey("grupos.codigo"), nullable=False)

    grupo = relationship("Grupo", back_populates="personas")
