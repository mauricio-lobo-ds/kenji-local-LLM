from app.domain.entities.etl_request import ETLRequest
from app.domain.services.prompt_builder import PromptBuilderService
from app.domain.value_objects.business_rule import BusinessRule, BusinessRuleSet
from app.domain.value_objects.table_schema import TableSchema


def _make_request(**kwargs) -> ETLRequest:
    defaults = dict(
        source_tables=[TableSchema(table_name="src", ddl_raw="CREATE TABLE src (id INT);")],
        target_table=TableSchema(table_name="tgt", ddl_raw="CREATE TABLE tgt (id INT);"),
        target_dialect="PostgreSQL",
    )
    defaults.update(kwargs)
    return ETLRequest(**defaults)


def test_system_prompt_contains_dialect():
    builder = PromptBuilderService()
    request = _make_request(target_dialect="BigQuery")
    pair = builder.build(request)
    assert "BigQuery" in pair.system_prompt


def test_user_prompt_contains_source_ddl():
    builder = PromptBuilderService()
    request = _make_request()
    pair = builder.build(request)
    assert "CREATE TABLE src" in pair.user_prompt


def test_user_prompt_contains_target_ddl():
    builder = PromptBuilderService()
    request = _make_request()
    pair = builder.build(request)
    assert "CREATE TABLE tgt" in pair.user_prompt


def test_user_prompt_contains_business_rules():
    builder = PromptBuilderService()
    rules = BusinessRuleSet(rules=[BusinessRule(description="Only active users")])
    request = _make_request(business_rules=rules)
    pair = builder.build(request)
    assert "Only active users" in pair.user_prompt


def test_user_prompt_contains_data_sample():
    builder = PromptBuilderService()
    request = _make_request(data_sample="id,name\n1,Alice")
    pair = builder.build(request)
    assert "1,Alice" in pair.user_prompt


def test_additional_context_section_present_when_set():
    builder = PromptBuilderService()
    request = _make_request(additional_context="Partition by month")
    pair = builder.build(request)
    assert "Additional Context" in pair.user_prompt
    assert "Partition by month" in pair.user_prompt


def test_additional_context_section_absent_when_empty():
    builder = PromptBuilderService()
    request = _make_request(additional_context="")
    pair = builder.build(request)
    assert "Additional Context" not in pair.user_prompt


def test_prompt_pair_is_frozen():
    import pytest

    builder = PromptBuilderService()
    request = _make_request()
    pair = builder.build(request)
    with pytest.raises((TypeError, AttributeError)):
        pair.system_prompt = "hacked"  # type: ignore[misc]
