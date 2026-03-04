from __future__ import annotations

import logging
import re

from app.adapters.outbound.llm.ollama_client import OllamaClient, OllamaMessage
from app.application.ports.llm_port import LLMPort
from app.domain.entities.etl_request import ETLRequest
from app.domain.entities.sql_result import SQLResult
from app.domain.services.prompt_builder import PromptBuilderService

logger = logging.getLogger(__name__)


class OllamaLLMAdapter(LLMPort):
    def __init__(self, client: OllamaClient, prompt_builder: PromptBuilderService) -> None:
        self._client = client
        self._prompt_builder = prompt_builder

    def generate_sql(self, request: ETLRequest) -> SQLResult:
        prompt_pair = self._prompt_builder.build(request)
        messages = [
            OllamaMessage(role="system", content=prompt_pair.system_prompt),
            OllamaMessage(role="user", content=prompt_pair.user_prompt),
        ]
        ollama_response = self._client.chat(messages)
        sql = self._extract_sql(ollama_response.content)
        return SQLResult.success(
            sql=sql,
            raw_llm_response=ollama_response.content,
            model_name=ollama_response.model,
            prompt_tokens=ollama_response.prompt_tokens,
            completion_tokens=ollama_response.completion_tokens,
        )

    def health_check(self) -> bool:
        return self._client.is_reachable()

    def _extract_sql(self, raw: str) -> str:
        # Strip accidental markdown code fences (```sql ... ``` or ``` ... ```)
        pattern = r"```(?:sql)?\s*\n?(.*?)```"
        match = re.search(pattern, raw, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return raw.strip()
