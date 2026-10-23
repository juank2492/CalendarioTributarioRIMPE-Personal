from enum import Enum
from datetime import date
from typing import List
from pydantic import BaseModel, Field, EmailStr

class TipoRegimenEnum(str, Enum):
    RIMPE_NEGOCIO_POPULAR = "RIMPE_NEGOCIO_POPULAR"
    RIMPE_EMPRENDEDOR = "RIMPE_EMPRENDEDOR"

class PerfilContribuyenteInput(BaseModel):
    ruc: str = Field(..., pattern=r"^\d{13}$", description="RUC de 13 dígitos numéricos")
    razon_social: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    tipo_regimen: TipoRegimenEnum
    anio_fiscal: int = Field(default=2026, ge=2024, le=2030)
    tiene_actividades_excluidas: bool = False

class EventoCalendarioOutput(BaseModel):
    id: str
    codigo_obligacion: str
    titulo: str
    fecha_vencimiento: str
    fecha_nominal: str
    fue_trasladada: bool
    motivo_traslado: str
    categoria: str
    color_identificador: str

class CalendarioCalculadoOutput(BaseModel):
    ruc: str
    noveno_digito: int
    tipo_regimen: str
    anio_fiscal: int
    eventos: List[EventoCalendarioOutput]

class ExplicacionObligacionInput(BaseModel):
    codigo_obligacion: str = Field(..., min_length=3, max_length=50)
    tipo_regimen: TipoRegimenEnum
    fecha_vencimiento: date
    noveno_digito: int = Field(..., ge=0, le=9)

class RecordatorioEstructurado(BaseModel):
    asunto: str
    resumen_didactico: str
    formulario_sri: str
    comprobantes_validos: str
    advertencia_en_cero: str
    base_legal: str
