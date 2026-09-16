from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .dialect_pipeline import preprocess
from .dialects import ARABIC_DIALECTS
from .engines.base import SynthesisOptions
from .engines.defaults import build_registry
from .engines.router import route_engine
from .hardware import select_engine
from .hardware_probe import detect_hardware
from .frontend import FRONTEND_DIR

app = FastAPI(title="Voice API", version="0.4.0")
registry = build_registry()


class SynthesisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    language: str = "ar"
    dialect: str = "ar-eg"
    voice: str | None = None
    speed: float = Field(default=1.0, ge=0.5, le=2.0)


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
        "registered_engines": registry.names(),
        "available_engines": registry.available(),
    }


@app.get("/api/engine/route")
def route():
    hw = detect_hardware()
    routed = route_engine(registry, hw, remote_available=True)
    return {"backend": routed.target, "engine": routed.engine.name}


@app.post("/api/synthesize")
def synthesize(req: SynthesisRequest):
    try:
        prepared = preprocess(req.text, req.language, req.dialect)
        hw = detect_hardware()
        routed = route_engine(registry, hw, remote_available=True)
        if not routed.engine.available():
            raise HTTPException(
                status_code=503,
                detail={
                    "code": "tts_runtime_missing",
                    "message": "Install the TTS extra: pip install -e '.[tts]'",
                    "recommended_backend": routed.target,
                },
            )

        result = routed.engine.synthesize(
            prepared["text"],
            SynthesisOptions(
                language=req.language,
                dialect=req.dialect,
                voice=req.voice,
                speed=req.speed,
            ),
        )
        return FileResponse(
            result.audio_path,
            media_type="audio/wav",
            filename="voice.wav",
            headers={
                "X-Voice-Engine": result.backend,
                "X-Voice-Sample-Rate": str(result.sample_rate),
            },
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "tts_runtime_error",
                "message": str(exc),
            },
        ) from exc


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(FRONTEND_DIR / "index.html")
