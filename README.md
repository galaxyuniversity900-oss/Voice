# Voice

Hardware-adaptive, Arabic-first voice platform with a mobile-first web client, Egyptian Arabic TTS, and a secure multi-provider AI gateway.

## Architecture

```text
Mobile/Web Client
       |
       v
FastAPI API
   |        |
   |        +--> AI Gateway --> NVIDIA / UniKey
   |
Arabic preprocessing
       |
Hardware router
       |
KemeTone TTS --> local model cache --> 24 kHz WAV
```

## Egyptian Arabic TTS

The default runtime is **KemeTone** (`Rabe3/kemetone`): an 82M-parameter, 24 kHz Egyptian/Cairene Arabic model with an Apache-2.0 license. Model assets are downloaded online on first use or by the bootstrap scripts and cached locally; weights are never committed to Git.

KemeTone is a single-speaker Cairene model. It is not a general voice-cloning or multi-speaker engine. Egyptian Arabic (`ar-EG`) diacritics are preserved because they improve pronunciation. The current runtime intentionally exposes `speed=1.0` only because KemeTone's integration does not implement time-stretching.

### Install

Core API and tests:

```bash
pip install -e '.[dev]'
```

Real Egyptian TTS + model prefetch:

```bash
bash scripts/bootstrap_tts.sh
```

Windows PowerShell:

```powershell
./scripts/bootstrap_tts.ps1
```

Manual setup:

```bash
pip install -e '.[tts]'
sudo apt-get update
sudo apt-get install -y espeak-ng
python scripts/download_models.py
```

Start:

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

Open `/` for the Arabic mobile client.

## AI providers

The gateway supports OpenAI-compatible providers:

- NVIDIA: `https://integrate.api.nvidia.com/v1`
- UniKey: `https://www.getunikey.ai/v1`

Configure keys only through environment variables or your deployment secret manager. **Never put API keys in the frontend, APK, Git repository, logs, or screenshots.**

Copy `.env.example` to your deployment environment and set:

```env
NVIDIA_API_KEY=
NVIDIA_MODEL=openai/gpt-oss-20b
UNIKEY_API_KEY=
UNIKEY_MODEL=unikey-router
```

The API supports explicit provider selection and automatic fallback:

```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H 'content-type: application/json' \
  -d '{"provider":"auto","messages":[{"role":"user","content":"اكتب تحية مصرية قصيرة"}]}'
```

Automatic routing tries configured providers in order, optionally honoring `preferred_provider`, and only falls back after a provider request fails. Provider credentials are never returned by status endpoints.

## API

- `GET /health`
- `GET /api/dialects`
- `POST /api/prepare`
- `GET /api/system/capabilities`
- `GET /api/engine/route`
- `GET /api/ai/providers`
- `GET /api/ai/health`
- `GET /api/ai/{provider}/models`
- `POST /api/ai/chat` — explicit provider or `provider=auto`
- `POST /api/synthesize` — generated 24 kHz WAV

## Hardware routing

The runtime detects RAM/CPU and, when PyTorch CUDA is available, GPU VRAM. The router can select a local GPU path, CPU path, or a future remote worker based on available resources. No remote inference is falsely advertised as implemented.

## Environment

- `VOICE_KEMETONE_MODEL` — default `Rabe3/kemetone`
- `VOICE_MODEL_CACHE` — default `~/.cache/voice/models`
- `VOICE_OUTPUT_DIR` — default `./outputs`
- `NVIDIA_API_KEY`, `NVIDIA_MODEL`
- `UNIKEY_API_KEY`, `UNIKEY_MODEL`

## Tests

```bash
pytest -q
```

GitHub Actions runs the core suite without downloading model weights.

## Responsible use

Use synthetic speech and voice cloning only with appropriate permission and in compliance with the applicable license and law. Do not use the service to impersonate a person without authorization. Disclose synthetic speech when listeners could otherwise mistake it for human speech.
