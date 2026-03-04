from app.domain.value_objects.business_rule import (
    BusinessRule,
    BusinessRuleSet,
    RulePriority,
)


def test_to_numbered_list_empty():
    rule_set = BusinessRuleSet()
    result = rule_set.to_numbered_list()
    assert "no business rules" in result.lower()


def test_to_numbered_list_single_rule():
    rule_set = BusinessRuleSet(rules=[BusinessRule(description="Only active customers")])
    result = rule_set.to_numbered_list()
    assert result.startswith("1.")
    assert "Only active customers" in result


def test_to_numbered_list_multiple_rules():
    rule_set = BusinessRuleSet(
        rules=[
            BusinessRule(description="Rule A", priority=RulePriority.HIGH),
            BusinessRule(description="Rule B", priority=RulePriority.LOW),
            BusinessRule(description="Rule C"),
        ]
    )
    lines = rule_set.to_numbered_list().splitlines()
    assert len(lines) == 3
    assert lines[0].startswith("1.")
    assert lines[1].startswith("2.")
    assert lines[2].startswith("3.")


def test_priority_tags_in_list():
    rule_set = BusinessRuleSet(
        rules=[
            BusinessRule(description="Important", priority=RulePriority.HIGH),
            BusinessRule(description="Optional", priority=RulePriority.LOW),
        ]
    )
    result = rule_set.to_numbered_list()
    assert "[HIGH]" in result
    assert "[LOW]" in result


def test_example_included():
    rule_set = BusinessRuleSet(
        rules=[BusinessRule(description="Filter by status", example="status = 'active'")]
    )
    result = rule_set.to_numbered_list()
    assert "status = 'active'" in result


def test_business_rule_frozen():
    import pytest

    rule = BusinessRule(description="immutable")
    with pytest.raises((TypeError, Exception)):
        rule.description = "changed"  # type: ignore[misc]
