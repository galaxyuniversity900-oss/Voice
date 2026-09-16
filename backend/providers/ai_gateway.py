from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    base_url: str
    api_key_env: str
    model_env: str
    default_model: str


PROVIDERS = {
    "nvidia": ProviderConfig(
        name="nvidia",
        base_url="https://integrate.api.nvidia.com/v1",
        api_key_env="NVIDIA_API_KEY",
        model_env="NVIDIA_MODEL",
        default_model="openai/gpt-oss-20b",
    ),
    "unikey": ProviderConfig(
        name="unikey",
        base_url="https://www.getunikey.ai/v1",
        api_key_env="UNIKEY_API_KEY",
        model_env="UNIKEY_MODEL",
        default_model="unikey-router",
    ),
}


class AIGateway:
    """OpenAI-compatible text-model gateway with environment-only secrets."""

    def configured(self) -> list[str]:
        return [name for name, cfg in PROVIDERS.items() if os.getenv(cfg.api_key_env)]

    def models(self, provider: str) -> list[dict[str, Any]]:
        cfg = self._config(provider)
        api_key = os.getenv(cfg.api_key_env)
        if not api_key:
            raise RuntimeError(f"Provider {provider} is not configured")
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{cfg.base_url}/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            response.raise_for_status()
            data = response.json()
        return data.get("data", [])

    def chat(self, provider: str, messages: list[dict[str, str]], temperature: float = 0.2) -> dict[str, Any]:
        cfg = self._config(provider)
        api_key = os.getenv(cfg.api_key_env)
        if not api_key:
            raise RuntimeError(f"Provider {provider} is not configured")
        model = os.getenv(cfg.model_env, cfg.default_model)
        payload = {"model": model, "messages": messages, "temperature": temperature}
        with httpx.Client(timeout=90.0) as client:
            response = client.post(
                f"{cfg.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    def _config(self, provider: str) -> ProviderConfig:
        try:
            return PROVIDERS[provider]
        except KeyError as exc:
            raise ValueError(f"Unknown AI provider: {provider}") from exc
