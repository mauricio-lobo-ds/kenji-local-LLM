from __future__ import annotations

import logging
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)


@dataclass
class OllamaMessage:
    role: str
    content: str


@dataclass
class OllamaResponse:
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    raw_json: dict = field(default_factory=dict)


class OllamaClient:
    def __init__(self, settings) -> None:
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model
        self._temperature = settings.llm_temperature
        self._max_tokens = settings.llm_max_tokens
        self._client = httpx.Client(timeout=120.0)

    def chat(self, messages: list[OllamaMessage]) -> OllamaResponse:
        url = f"{self._base_url}/v1/chat/completions"
        payload = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "stream": False,
        }
        logger.debug("POST %s model=%s", url, self._model)
        response = self._client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        choice = data["choices"][0]
        content = choice["message"]["content"]
        usage = data.get("usage", {})

        return OllamaResponse(
            content=content,
            model=data.get("model", self._model),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            raw_json=data,
        )

    def is_reachable(self) -> bool:
        try:
            url = f"{self._base_url}/v1/models"
            response = self._client.get(url, timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False
