"""Integration tests — require a running Ollama instance with qwen2.5-coder:7b."""
from __future__ import annotations

import pytest

from app.adapters.outbound.llm.ollama_adapter import OllamaLLMAdapter
from app.adapters.outbound.llm.ollama_client import OllamaClient
from app.domain.entities.etl_request import ETLRequest
from app.domain.services.prompt_builder import PromptBuilderService
from app.domain.value_objects.business_rule import BusinessRule, BusinessRuleSet
from app.domain.value_objects.table_schema import TableSchema
from app.infrastructure.config.settings import Settings


@pytest.fixture(scope="module")
def settings():
    return Settings()


@pytest.fixture(scope="module")
def client(settings):
    return OllamaClient(settings)


@pytest.fixture(scope="module")
def adapter(client):
    return OllamaLLMAdapter(client=client, prompt_builder=PromptBuilderService())


def _ollama_available(client: OllamaClient) -> bool:
    return client.is_reachable()


def test_health_check(client):
    if not _ollama_available(client):
        pytest.skip("Ollama not running — skipping integration tests")
    assert client.is_reachable() is True


def test_generate_sql_contains_select(adapter, client):
    if not _ollama_available(client):
        pytest.skip("Ollama not running — skipping integration tests")

    request = ETLRequest(
        source_tables=[
            TableSchema(
                table_name="orders",
                ddl_raw=(
                    "CREATE TABLE orders ("
                    "  id INT PRIMARY KEY,"
                    "  customer_id INT,"
                    "  amount DECIMAL(10,2),"
                    "  status VARCHAR(20)"
                    ");"
                ),
            )
        ],
        target_table=TableSchema(
            table_name="orders_summary",
            ddl_raw=(
                "CREATE TABLE orders_summary ("
                "  customer_id INT,"
                "  total_amount DECIMAL(12,2),"
                "  order_count INT"
                ");"
            ),
        ),
        data_sample="id,customer_id,amount,status\n1,42,150.00,completed\n2,42,50.00,completed",
        business_rules=BusinessRuleSet(
            rules=[BusinessRule(description="Only include orders with status = 'completed'")]
        ),
        target_dialect="PostgreSQL",
    )

    result = adapter.generate_sql(request)
    assert result.is_success(), f"Expected success but got: {result.error_message}"
    assert "SELECT" in result.sql.upper(), f"SQL does not contain SELECT:\n{result.sql}"
    assert result.model_name != ""
