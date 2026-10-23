import pytest
from datetime import date
from backend.services.calculator import calcular_vencimientos, trasladar_al_siguiente_dia_habil

MAPEO_DIGITOS = {
    "1": 10, "2": 12, "3": 14, "4": 16, "5": 18,
    "6": 20, "7": 22, "8": 24, "9": 26, "0": 28
}

@pytest.mark.parametrize("digito,dia_esperado", MAPEO_DIGITOS.items())
def test_noveno_digito_mapeo_nominal(digito, dia_esperado):
    # RUC de 13 dígitos exactos con el noveno dígito dinámico en posición ruc[8]
    ruc = f"17923456{digito}0001"
    eventos = calcular_vencimientos(ruc=ruc, tipo_regimen="RIMPE_EMPRENDEDOR", anio=2026)
    assert len(eventos) == 3
    for ev in eventos:
        nom_day = int(ev["fecha_nominal"].split("-")[2])
        assert nom_day == dia_esperado

def test_traslado_fin_de_semana():
    sabado = date(2026, 6, 20)
    fecha_fin, trasladada, motivo = trasladar_al_siguiente_dia_habil(sabado, [])
    assert trasladada is True
    assert fecha_fin == date(2026, 6, 22)
    assert motivo == "FIN_DE_SEMANA"

def test_negocio_popular_solo_renta_mayo():
    eventos = calcular_vencimientos(ruc="1792345680001", tipo_regimen="RIMPE_NEGOCIO_POPULAR", anio=2026)
    assert len(eventos) == 1
    assert eventos[0]["codigo_obligacion"] == "RENTA_RIMPE_NP"
    assert "-05-" in eventos[0]["fecha_vencimiento"]
