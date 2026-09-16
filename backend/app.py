from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .dialect_pipeline import preprocess
from .dialects import ARABIC_DIALECTS
from .hardware import HardwareProfile, select_engine
from .hardware_probe import detect_hardware
from .frontend import FRONTEND_DIR

app = FastAPI(title="Voice API", version="0.2.0")


class SynthesisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    language: str = "ar"
    dialect: str = "ar-eg"


@app.get("/health")
def health():
    return {"status": "ok", "service": "voice", "version": app.version}


@app.get("/api/dialects")
def dialects():
    return [p.__dict__ for p in ARABIC_DIALECTS.values()]


@app.post("/api/prepare")
def prepare(req: SynthesisRequest):
    try:
        return preprocess(req.text, req.language, req.dialect)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/system/capabilities")
def capabilities():
    hw = detect_hardware()
    target = select_engine(hw, remote_available=True)
    return {
        "hardware": hw.__dict__,
        "recommended_backend": target.backend,
        "reason": target.reason,
    }


@app.get("/api/engine/route")
def route(gpu_vram_mb: int = 0, ram_mb: int = 4096, cpu_threads: int = 4, remote_available: bool = True):
    target = select_engine(HardwareProfile(gpu_vram_mb, ram_mb, cpu_threads), remote_available)
    return {"backend": target.backend, "reason": target.reason}


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(FRONTEND_DIR / "index.html")
