from __future__ import annotations

import os
import time
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
    """OpenAI-compatible AI gateway with safe secrets and provider fallback."""

    def configured(self) -> list[str]:
        return [name for name, cfg in PROVIDERS.items() if os.getenv(cfg.api_key_env)]

    def status(self) -> list[dict[str, Any]]:
        return [
            {
                "provider": name,
                "configured": bool(os.getenv(cfg.api_key_env)),
                "model": os.getenv(cfg.model_env, cfg.default_model),
                "base_url": cfg.base_url,
            }
            for name, cfg in PROVIDERS.items()
        ]

    def models(self, provider: str) -> list[dict[str, Any]]:
        cfg = self._config(provider)
        api_key = self._api_key(cfg)
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{cfg.base_url}/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            response.raise_for_status()
            data = response.json()
        return data.get("data", [])

    def chat(
        self,
        provider: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        cfg = self._config(provider)
        return self._chat_with_config(cfg, messages, temperature)

    def auto_chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        preferred: str | None = None,
    ) -> dict[str, Any]:
        candidates = self.configured()
        if preferred and preferred in candidates:
            candidates.remove(preferred)
            candidates.insert(0, preferred)
        if not candidates:
            raise RuntimeError("No AI provider is configured")

        failures: list[str] = []
        for provider in candidates:
            try:
                result = self.chat(provider, messages, temperature)
                result.setdefault("_voice_gateway", {})
                result["_voice_gateway"].update({"provider": provider, "attempted": candidates})
                return result
            except (httpx.HTTPError, TimeoutError, RuntimeError, ValueError) as exc:
                failures.append(f"{provider}: {type(exc).__name__}")
        raise RuntimeError("All configured AI providers failed: " + "; ".join(failures))

    def _chat_with_config(
        self,
        cfg: ProviderConfig,
        messages: list[dict[str, str]],
        temperature: float,
    ) -> dict[str, Any]:
        api_key = self._api_key(cfg)
        model = os.getenv(cfg.model_env, cfg.default_model)
        payload = {"model": model, "messages": messages, "temperature": temperature}
        with httpx.Client(timeout=httpx.Timeout(90.0, connect=15.0)) as client:
            response = client.post(
                f"{cfg.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    def _api_key(cfg: ProviderConfig) -> str:
        value = os.getenv(cfg.api_key_env, "").strip()
        if not value:
            raise RuntimeError(f"Provider {cfg.name} is not configured")
        return value

    @staticmethod
    def _config(provider: str) -> ProviderConfig:
        try:
            return PROVIDERS[provider.lower()]
        except KeyError as exc:
            raise ValueError(f"Unknown AI provider: {provider}") from exc
