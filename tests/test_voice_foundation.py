from fastapi.testclient import TestClient

from backend.app import app
from backend.dialect_pipeline import preprocess
from backend.hardware import HardwareProfile, select_engine
from backend.providers.ai_gateway import AIGateway

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


def test_egyptian_diacritics_are_preserved():
    result = preprocess("النَّهَارْدَه الْجَوّ حِلْو أَوِي", "ar", "ar-eg")
    assert "النَّهَارْدَه" in result["text"]
    assert "حِلْو" in result["text"]


def test_non_egyptian_normalization_removes_diacritics():
    result = preprocess("مَرْحَبًا", "ar", "ar-msa")
    assert result["text"] == "مرحبا"


def test_hardware_routing_has_low_resource_path():
    assert select_engine(HardwareProfile(ram_mb=2048), True).backend == "cpu"
    assert select_engine(HardwareProfile(ram_mb=1024), True).backend == "remote"


def test_prepare_endpoint():
    response = client.post("/api/prepare", json={"text": "أهلاً يا صاحبي", "dialect": "ar-eg"})
    assert response.status_code == 200
    assert response.json()["dialect"] == "ar-EG"


def test_ai_providers_endpoint_hides_secrets(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "secret")
    monkeypatch.setenv("UNIKEY_API_KEY", "secret")
    response = client.get("/api/ai/providers")
    assert response.status_code == 200
    assert response.json()["configured"] == ["nvidia", "unikey"]
    assert "secret" not in response.text


def test_ai_chat_requires_configured_provider(monkeypatch):
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    response = client.post(
        "/api/ai/chat",
        json={"provider": "nvidia", "messages": [{"role": "user", "content": "hello"}]},
    )
    assert response.status_code == 503


def test_unknown_ai_provider():
    response = client.post(
        "/api/ai/chat",
        json={"provider": "unknown", "messages": [{"role": "user", "content": "hello"}]},
    )
    assert response.status_code == 404


def test_ai_status_contains_no_secret(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "top-secret")
    status = AIGateway().status()
    assert status[0]["configured"] is True
    assert all("top-secret" not in str(item) for item in status)


def test_auto_chat_requires_provider(monkeypatch):
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("UNIKEY_API_KEY", raising=False)
    try:
        AIGateway().auto_chat([{"role": "user", "content": "hello"}])
    except RuntimeError as exc:
        assert "No AI provider" in str(exc)
    else:
        raise AssertionError("auto_chat should fail when no provider is configured")


def test_speed_is_restricted_to_supported_kemetone_value():
    response = client.post(
        "/api/prepare",
        json={"text": "مرحبا", "dialect": "ar-eg", "speed": 1.5},
    )
    assert response.status_code == 422
