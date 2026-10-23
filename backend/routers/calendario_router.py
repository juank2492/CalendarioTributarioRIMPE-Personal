from fastapi import APIRouter, HTTPException
from backend.schemas import PerfilContribuyenteInput, CalendarioCalculadoOutput
from backend.services.calculator import calcular_vencimientos

router = APIRouter(prefix="/api/perfil", tags=["Perfil y Calendario"])

@router.post("/calcular-vencimientos", response_model=CalendarioCalculadoOutput)
def endpoint_calcular_vencimientos(perfil: PerfilContribuyenteInput):
    try:
        eventos = calcular_vencimientos(
            ruc=perfil.ruc,
            tipo_regimen=perfil.tipo_regimen.value,
            anio=perfil.anio_fiscal
        )
        return {
            "ruc": perfil.ruc,
            "noveno_digito": int(perfil.ruc[8]),
            "tipo_regimen": perfil.tipo_regimen.value,
            "anio_fiscal": perfil.anio_fiscal,
            "eventos": eventos
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
