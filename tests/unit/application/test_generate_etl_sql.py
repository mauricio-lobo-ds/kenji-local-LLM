import pytest
from unittest.mock import MagicMock

from app.application.dto.etl_request_dto import ETLRequestDTO, TableSchemaDTO
from app.application.use_cases.generate_etl_sql import GenerateETLSQLUseCase
from app.domain.entities.sql_result import SQLResult, SQLResultStatus
from app.domain.services.prompt_builder import PromptBuilderService


def _make_dto(**kwargs) -> ETLRequestDTO:
    defaults = dict(
        source_tables_raw=[
            TableSchemaDTO(table_name="orders", ddl_or_description="CREATE TABLE orders (id INT);")
        ],
        target_table_raw=TableSchemaDTO(
            table_name="orders_summary",
            ddl_or_description="CREATE TABLE orders_summary (total INT);",
        ),
        business_rules_text="Only completed orders\nExclude test accounts",
        target_dialect="PostgreSQL",
    )
    defaults.update(kwargs)
    return ETLRequestDTO(**defaults)


def _make_use_case(llm_result: SQLResult) -> GenerateETLSQLUseCase:
    mock_port = MagicMock()
    mock_port.generate_sql.return_value = llm_result
    builder = PromptBuilderService()
    return GenerateETLSQLUseCase(llm_port=mock_port, prompt_builder=builder)


def test_execute_returns_success_result():
    expected = SQLResult.success(sql="SELECT 1;", model_name="test-model")
    use_case = _make_use_case(expected)
    result = use_case.execute(_make_dto())
    assert result.is_success()
    assert result.sql == "SELECT 1;"


def test_execute_never_raises_on_llm_exception():
    mock_port = MagicMock()
    mock_port.generate_sql.side_effect = RuntimeError("connection refused")
    builder = PromptBuilderService()
    use_case = GenerateETLSQLUseCase(llm_port=mock_port, prompt_builder=builder)
    result = use_case.execute(_make_dto())
    assert result.status == SQLResultStatus.ERROR
    assert "connection refused" in result.error_message


def test_execute_never_raises_on_dto_mapping_error():
    """Even if the DTO produces an unexpected error, use case must not raise."""
    mock_port = MagicMock()
    mock_port.generate_sql.side_effect = Exception("unexpected")
    builder = PromptBuilderService()
    use_case = GenerateETLSQLUseCase(llm_port=mock_port, prompt_builder=builder)
    result = use_case.execute(_make_dto())
    assert result.status == SQLResultStatus.ERROR


def test_business_rules_parsed_from_text():
    """Multi-line rules_text should be split into individual BusinessRule objects."""
    captured_requests = []

    def capture_request(request):
        captured_requests.append(request)
        return SQLResult.success(sql="SELECT 1;")

    mock_port = MagicMock()
    mock_port.generate_sql.side_effect = capture_request
    builder = PromptBuilderService()
    use_case = GenerateETLSQLUseCase(llm_port=mock_port, prompt_builder=builder)

    use_case.execute(_make_dto(business_rules_text="Rule one\nRule two\nRule three"))
    assert len(captured_requests) == 1
    rules = captured_requests[0].business_rules.rules
    assert len(rules) == 3
    assert rules[0].description == "Rule one"
    assert rules[2].description == "Rule three"


def test_empty_business_rules_text_produces_empty_rule_set():
    captured_requests = []

    def capture(request):
        captured_requests.append(request)
        return SQLResult.success(sql="SELECT 1;")

    mock_port = MagicMock()
    mock_port.generate_sql.side_effect = capture
    builder = PromptBuilderService()
    use_case = GenerateETLSQLUseCase(llm_port=mock_port, prompt_builder=builder)

    use_case.execute(_make_dto(business_rules_text=""))
    assert captured_requests[0].business_rules.rules == []


def test_dialect_forwarded_to_entity():
    captured = []

    def capture(request):
        captured.append(request)
        return SQLResult.success(sql="SELECT 1;")

    mock_port = MagicMock()
    mock_port.generate_sql.side_effect = capture
    builder = PromptBuilderService()
    use_case = GenerateETLSQLUseCase(llm_port=mock_port, prompt_builder=builder)

    use_case.execute(_make_dto(target_dialect="Snowflake"))
    assert captured[0].target_dialect == "Snowflake"
