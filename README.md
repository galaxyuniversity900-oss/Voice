# Voice

Hardware-adaptive, Arabic-first voice platform with a mobile web client and pluggable TTS execution layer.

## Goals

- **Low-resource first:** route work across local GPU, quantized, CPU, and remote execution paths.
- **Arabic dialects as first-class data:** language and dialect are separate; `ar-EG` (Egyptian Arabic) is included alongside regional profiles.
- **Production-safe integration:** the core never pretends that a dialect registry is a speech model. Real audio generation requires a configured, licensed TTS runtime/model.
- **Mobile-ready:** the frontend is a lightweight responsive client suitable for Android browsers and thin-wrapper apps.

## Architecture

```text
Client (mobile/web)
        |
        v
FastAPI API -> Arabic preprocessing -> hardware router -> engine registry
                                                   |-> local
                                                   |-> GGUF/quantized
                                                   |-> CPU
                                                   `-> remote worker
```

The engine contract (`backend/engines/base.py`) keeps model/runtime integrations replaceable. The default deployment intentionally reports a clear `tts_engine_not_configured` response instead of generating fake audio.

## API

- `GET /health`
- `GET /api/dialects`
- `POST /api/prepare`
- `GET /api/system/capabilities`
- `GET /api/engine/route`
- `POST /api/synthesize`

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn backend.app:app --reload
```

Open `/` for the mobile-first Arabic client.

## Tests

```bash
pytest -q
```

GitHub Actions runs the test suite on pushes and pull requests.

## Egyptian Arabic

`ar-EG` currently provides locale identity plus conservative preprocessing. High-quality Egyptian pronunciation, prosody, speaker adaptation, and code-switching require an actual compatible model/adapter or provider; those components are intentionally isolated behind the engine contract rather than being simulated by string replacement.

## Voice cloning and model licensing

Use voice cloning only with the speaker's permission and follow the license/terms of every model, runtime, and provider used in deployment.
