import json
import os
import calendar
from datetime import date, timedelta
from typing import List, Dict, Any

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "sri_rules_2026.json")

def cargar_configuracion() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def es_dia_inhabil(fecha: date, feriados: list) -> bool:
    if fecha.weekday() >= 5:
        return True
    return [fecha.month, fecha.day] in feriados

def trasladar_al_siguiente_dia_habil(fecha: date, feriados: list) -> tuple[date, bool, str]:
    fue_trasladada = False
    motivo = "NINGUNO"
    
    while es_dia_inhabil(fecha, feriados):
        if not fue_trasladada:
            fue_trasladada = True
            motivo = "FIN_DE_SEMANA" if fecha.weekday() >= 5 else "FERIADO_NACIONAL"
        fecha += timedelta(days=1)
        
    return fecha, fue_trasladada, motivo

def calcular_vencimientos(ruc: str, tipo_regimen: str, anio: int = 2026) -> List[Dict[str, Any]]:
    if len(ruc) != 13 or not ruc.isdigit():
        raise ValueError("El RUC debe tener exactamente 13 dígitos numéricos.")

    config = cargar_configuracion()
    noveno_digito = ruc[8]
    dia_base = config["ninth_digit_deadlines"].get(noveno_digito)
    feriados = config.get("feriados_nacionales_ecuador", [])

    regimen_data = config["rimpe_types"].get(tipo_regimen)
    if not regimen_data:
        raise ValueError(f"Régimen '{tipo_regimen}' no soportado.")

    eventos = []
    for obl in regimen_data["obligations"]:
        mes = obl["month"]
        target_year = anio + 1 if (obl["code"] == "IVA_SEMESTRAL_2" and mes == 1) else anio
        
        max_dias = calendar.monthrange(target_year, mes)[1]
        dia_calculado = min(dia_base, max_dias)
        fecha_nominal = date(target_year, mes, dia_calculado)

        fecha_final, trasladada, motivo = trasladar_al_siguiente_dia_habil(fecha_nominal, feriados)

        eventos.append({
            "id": f"evt-{obl['code'].lower()}-{target_year}",
            "codigo_obligacion": obl["code"],
            "titulo": obl["name"],
            "fecha_vencimiento": fecha_final.isoformat(),
            "fecha_nominal": fecha_nominal.isoformat(),
            "fue_trasladada": trasladada,
            "motivo_traslado": motivo,
            "categoria": "RIMPE",
            "color_identificador": obl.get("color", "#2563eb")
        })

    return eventos
