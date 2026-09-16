$ErrorActionPreference = 'Stop'

python -m pip install -e '.[tts]'
python scripts/download_models.py
Write-Host 'TTS runtime and KemeTone model assets are ready.'
Write-Host 'Install espeak-ng separately if the phonemizer reports it is missing.'
