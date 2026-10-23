from fastapi import APIRouter, HTTPException
from backend.schemas import ExplicacionObligacionInput, RecordatorioEstructurado
from backend.services.llm import generar_explicacion_didactica

router = APIRouter(prefix="/api/obligaciones", tags=["Obligaciones e IA"])

@router.post("/explicar", response_model=RecordatorioEstructurado)
def endpoint_explicar_obligacion(payload: ExplicacionObligacionInput):
    try:
        resultado, tokens_in, tokens_out = generar_explicacion_didactica(
            codigo_obligacion=payload.codigo_obligacion,
            tipo_regimen=payload.tipo_regimen.value,
            fecha_vencimiento=payload.fecha_vencimiento.isoformat(),
            noveno_digito=payload.noveno_digito
        )
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallo en servicio generativo: {str(e)}")

@router.post("/simular-error-429")
def endpoint_simular_error_429():
    try:
        generar_explicacion_didactica(
            codigo_obligacion="IVA_SEMESTRAL_1",
            tipo_regimen="RIMPE_EMPRENDEDOR",
            fecha_vencimiento="2026-07-24",
            noveno_digito=8,
            modo_simulacion_429=True
        )
        return {"status": "ok"}
    except Exception as e:
        return {
            "status": "error_controlado_429",
            "detalle": "Reintentos de Tenacity agotados exitosamente",
            "error": str(e)
        }
