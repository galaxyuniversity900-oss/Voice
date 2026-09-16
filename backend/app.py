from fastapi import FastAPI
from pydantic import BaseModel, Field
from .dialects import ARABIC_DIALECTS, get_dialect
from .normalizer import prepare_text
from .hardware import HardwareProfile, select_engine

app = FastAPI(title="Voice API", version="0.1.0")

class SynthesisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    language: str = "ar"
    dialect: str = "ar-eg"
    remote_available: bool = True

@app.get("/health")
def health():
    return {"status": "ok", "service": "voice"}

@app.get("/api/dialects")
def dialects():
    return [p.__dict__ for p in ARABIC_DIALECTS.values()]

@app.post("/api/prepare")
def prepare(req: SynthesisRequest):
    profile = get_dialect(req.dialect)
    text = prepare_text(req.text, req.dialect)
    return {"language": req.language, "dialect": profile.__dict__, "text": text}

@app.get("/api/engine/route")
def route(gpu_vram_mb: int = 0, ram_mb: int = 4096, cpu_threads: int = 4, remote_available: bool = True):
    target = select_engine(HardwareProfile(gpu_vram_mb, ram_mb, cpu_threads), remote_available)
    return {"backend": target.backend, "reason": target.reason}
