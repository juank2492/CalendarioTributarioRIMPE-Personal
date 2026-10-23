import os
import json
import logging
from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
from backend.schemas import RecordatorioEstructurado

logger = logging.getLogger(__name__)

class RateLimitException(Exception):
    pass

def cargar_prompt_sistema() -> str:
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "system_v3.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "Eres un asistente tributario oficial del SRI. Genera salidas JSON estrictas."

FALLBACK_ESTATICO = {
    "IVA_SEMESTRAL_1": RecordatorioEstructurado(
        asunto="Recordatorio SRI: Declaración Semestral IVA (Semestre 1)",
        resumen_didactico="Corresponde a la liquidación de transacciones gravadas de enero a junio. Debe declararse en julio según el noveno dígito del RUC.",
        formulario_sri="Formulario 104",
        comprobantes_validos="Facturación electrónica con tarifa vigente de IVA.",
        advertencia_en_cero="Si no hubo ventas ni compras, declarar en cero obligatoriamente.",
        base_legal="Art. 158 Reglamento LORTI; Resolución NAC-DGERCGC23-00000034"
    ),
    "RENTA_RIMPE_NP": RecordatorioEstructurado(
        asunto="Recordatorio SRI: Impuesto a la Renta Negocio Popular",
        resumen_didactico="Pago consolidado único de $60 anuales exigible en mayo para negocios con ingresos brutos de hasta $20,000.",
        formulario_sri="Formulario 106 (Pago Cuota Única)",
        comprobantes_validos="Notas de venta vigentes.",
        advertencia_en_cero="No exime de presentación si los ingresos fueron cero.",
        base_legal="Art. 97.6 Ley de Régimen Tributario Interno"
    )
}

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    retry=retry_if_exception_type(RateLimitException),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def _invocar_gemini_api(cliente: genai.Client, model_name: str, sys_instruction: str, user_content: str):
    try:
        response = cliente.models.generate_content(
            model=model_name,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruction,
                temperature=0.2,
                max_output_tokens=600,
                response_mime_type="application/json",
                response_schema=RecordatorioEstructurado
            )
        )
        return response
    except APIError as e:
        if getattr(e, "code", None) == 429 or "RESOURCE_EXHAUSTED" in str(e):
            raise RateLimitException("Cuota de API temporalmente excedida")
        raise e

def generar_explicacion_didactica(
    codigo_obligacion: str,
    tipo_regimen: str,
    fecha_vencimiento: str,
    noveno_digito: int,
    modo_simulacion_429: bool = False
) -> tuple[RecordatorioEstructurado, int, int]:
    if modo_simulacion_429:
        logger.warning("[SIMULACIÓN] Disparando RateLimitException intencional")
        raise RateLimitException("Simulación forzada de error HTTP 429")

    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    if not api_key:
        logger.warning("GEMINI_API_KEY no configurada. Activando fallback local.")
        fb = FALLBACK_ESTATICO.get(codigo_obligacion, FALLBACK_ESTATICO["IVA_SEMESTRAL_1"])
        return fb, 0, 0

    cliente = genai.Client(api_key=api_key)
    sys_prompt = cargar_prompt_sistema()
    user_payload = json.dumps({
        "codigo_obligacion": codigo_obligacion,
        "tipo_regimen": tipo_regimen,
        "fecha_vencimiento": fecha_vencimiento,
        "noveno_digito": noveno_digito
    })

    try:
        resp = _invocar_gemini_api(cliente, model_name, sys_prompt, user_payload)
        tokens_in = resp.usage_metadata.prompt_token_count if resp.usage_metadata else 0
        tokens_out = resp.usage_metadata.candidates_token_count if resp.usage_metadata else 0
        resultado_obj = RecordatorioEstructurado.model_validate_json(resp.text)
        return resultado_obj, tokens_in, tokens_out
    except RateLimitException:
        logger.error("Rate limit reintentado 3 veces. Retornando fallback estático.")
        fb = FALLBACK_ESTATICO.get(codigo_obligacion, FALLBACK_ESTATICO["IVA_SEMESTRAL_1"])
        return fb, 0, 0
