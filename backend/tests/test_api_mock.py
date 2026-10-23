import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@patch("backend.services.llm._invocar_gemini_api")
def test_caso_feliz_explicacion_mock(mock_api):
    payload = {
        "codigo_obligacion": "IVA_SEMESTRAL_1",
        "tipo_regimen": "RIMPE_EMPRENDEDOR",
        "fecha_vencimiento": "2026-07-24",
        "noveno_digito": 8
    }
    response = client.post("/api/obligaciones/explicar", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "asunto" in data
    assert "resumen_didactico" in data
    assert "base_legal" in data

def test_validacion_entrada_invalida_ruc_422():
    payload = {
        "ruc": "09234",
        "razon_social": "Test Invalido",
        "email": "test@test.com",
        "tipo_regimen": "RIMPE_EMPRENDEDOR",
        "anio_fiscal": 2026
    }
    response = client.post("/api/perfil/calcular-vencimientos", json=payload)
    assert response.status_code == 422

def test_simulador_error_429():
    response = client.post("/api/obligaciones/simular-error-429")
    assert response.status_code == 200
    assert response.json()["status"] == "error_controlado_429"
