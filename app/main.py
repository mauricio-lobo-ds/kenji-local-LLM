from __future__ import annotations

from app.adapters.outbound.llm.ollama_adapter import OllamaLLMAdapter
from app.adapters.outbound.llm.ollama_client import OllamaClient
from app.application.use_cases.generate_etl_sql import GenerateETLSQLUseCase
from app.domain.services.prompt_builder import PromptBuilderService
from app.infrastructure.config.settings import Settings
from app.infrastructure.logging.logger import configure_logging


def create_use_case() -> GenerateETLSQLUseCase:
    settings = Settings()
    configure_logging(settings)

    prompt_builder = PromptBuilderService()
    client = OllamaClient(settings)
    adapter = OllamaLLMAdapter(client=client, prompt_builder=prompt_builder)
    return GenerateETLSQLUseCase(llm_port=adapter, prompt_builder=prompt_builder)
