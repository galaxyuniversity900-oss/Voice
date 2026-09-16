# Voice

Hardware-adaptive voice cloning and Arabic speech platform.

## First engineering targets

1. **Do not require a powerful device.** A routing layer selects full local, quantized, CPU, or remote execution based on available resources.
2. **Arabic dialects are first-class.** Language (`ar`) is separate from dialect (`ar-eg`, `ar-sa`, etc.). Egyptian Arabic (`ar-EG`) is included from the foundation layer.

## Current foundation

- FastAPI service with health endpoint.
- Dialect registry with Egyptian + Gulf/Arabic regional profiles.
- Conservative Arabic text normalization that does not rewrite dialect wording.
- Hardware-aware engine selection API.
- Extension points for real TTS backends, quantized models, remote workers, pronunciation lexicons, and voice adapters.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn backend.app:app --reload
```

API: `GET /health`, `GET /api/dialects`, `GET /api/engine/route`, `POST /api/prepare`.

> Model weights and third-party engines must be integrated according to their own licenses. Voice cloning should only be used with permission from the speaker.
