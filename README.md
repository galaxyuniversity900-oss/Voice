# Voice

Hardware-adaptive, Arabic-first voice platform with a mobile web client and a real Egyptian Arabic TTS runtime.

## Runtime

The default Egyptian runtime is **KemeTone** (`Rabe3/kemetone`): an 82M-parameter, 24 kHz Egyptian/Cairene Arabic model with an Apache-2.0 license. Its published model card states that it runs on CPU or CUDA GPU and that the model weights are about 327 MB. The runtime downloads the model from Hugging Face on first synthesis and caches it locally; weights are never committed to this repository.

KemeTone is intentionally used as one concrete production engine behind the replaceable `VoiceEngine` contract. It is a single female voice and is optimized for Cairene Egyptian Arabic. Diacritics are preserved for `ar-EG` because the model card notes that they materially improve vowel pronunciation.

## Architecture

```text
Mobile/Web Client
       |
       v
FastAPI API
       |
Arabic preprocessing (preserve ar-EG diacritics)
       |
Hardware router
       |
KemeTone engine -> first-run online model download -> local cache -> WAV
```

The model itself is online-downloadable and lazy-loaded: installing the application does not place 327 MB of weights in Git. The first `/api/synthesize` request downloads and caches the required model assets.

## Install

Core API only:

```bash
pip install -e '.[dev]'
```

Real Egyptian TTS:

```bash
pip install -e '.[tts]'
```

KemeTone's published requirements use `kokoro`, PyTorch, soundfile and NumPy. Its phonemiser also requires the system `espeak-ng` library. On Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y espeak-ng
```

Then:

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

Open `/` for the mobile-first Arabic client.

## First synthesis

Use Egyptian Arabic (`ar-eg`). The first generation downloads the KemeTone model assets from Hugging Face. Subsequent generations use the local cache.

```bash
curl -X POST http://localhost:8000/api/synthesize \
  -H 'content-type: application/json' \
  -d '{"text":"النَّهَارْدَه الْجَوّ حِلْو أَوِي","dialect":"ar-eg","language":"ar","speed":1.0}' \
  --output voice.wav
```

Environment variables:

- `VOICE_KEMETONE_MODEL` — model repository, default `Rabe3/kemetone`.
- `VOICE_MODEL_CACHE` — local Hugging Face cache root, default `~/.cache/voice/models`.
- `VOICE_OUTPUT_DIR` — generated WAV directory, default `./outputs`.

## API

- `GET /health`
- `GET /api/dialects`
- `POST /api/prepare`
- `GET /api/system/capabilities`
- `GET /api/engine/route`
- `POST /api/synthesize` → WAV audio

## Hardware routing

The router prefers a local GPU on capable machines and falls back to the lightweight KemeTone CPU path for lower-resource systems. Extremely constrained machines remain eligible for a future remote-worker path rather than pretending that local inference is safe.

## Egyptian Arabic limitations

KemeTone is Cairo/Egyptian focused, single-speaker, conversational-neutral, and does not provide multi-speaker cloning. It also expects Egyptian Arabic rather than generic MSA. Long text should be split at sentence boundaries.

## Tests

```bash
pytest -q
```

GitHub Actions runs the core test suite on pushes and pull requests. TTS model downloads are intentionally not performed in CI.

## Responsible use

Use synthetic speech and voice cloning only with appropriate permission and in compliance with the model license and applicable law. KemeTone's model card specifically asks users not to impersonate the modeled person and to disclose synthetic speech where listeners could otherwise mistake it for human audio.
