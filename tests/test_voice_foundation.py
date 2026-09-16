from fastapi.testclient import TestClient

from backend.app import app
from backend.dialect_pipeline import preprocess
from backend.hardware import HardwareProfile, select_engine

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_egyptian_dialect_is_registered():
    response = client.get("/api/dialects")
    assert any(item["id"] == "ar-eg" for item in response.json())


def test_arabic_digits_are_preprocessed():
    result = preprocess("السعر ١٢٥ جنيه ؟", "ar", "ar-eg")
    assert result["text"] == "السعر 125 جنيه؟"


def test_hardware_routing_has_low_resource_path():
    assert select_engine(HardwareProfile(ram_mb=2048), True).backend == "cpu"
    assert select_engine(HardwareProfile(ram_mb=1024), True).backend == "remote"


def test_prepare_endpoint():
    response = client.post("/api/prepare", json={"text": "أهلاً يا صاحبي", "dialect": "ar-eg"})
    assert response.status_code == 200
    assert response.json()["dialect"]["locale"] == "ar-EG"
