from __future__ import annotations

import logging

from app.application.dto.etl_request_dto import ETLRequestDTO, TableSchemaDTO
from app.application.ports.llm_port import LLMPort
from app.domain.entities.etl_request import ETLRequest
from app.domain.entities.sql_result import SQLResult
from app.domain.services.prompt_builder import PromptBuilderService
from app.domain.value_objects.business_rule import BusinessRule, BusinessRuleSet
from app.domain.value_objects.table_schema import TableSchema

logger = logging.getLogger(__name__)


class GenerateETLSQLUseCase:
    def __init__(self, llm_port: LLMPort, prompt_builder: PromptBuilderService) -> None:
        self._llm_port = llm_port
        self._prompt_builder = prompt_builder

    def execute(self, dto: ETLRequestDTO) -> SQLResult:
        try:
            request = self._map_dto_to_entity(dto)
            logger.info(
                "Executing ETL SQL generation request_id=%s dialect=%s",
                request.request_id,
                request.target_dialect,
            )
            result = self._llm_port.generate_sql(request)
            logger.info(
                "Generation complete request_id=%s status=%s",
                request.request_id,
                result.status,
            )
            return result
        except Exception as exc:
            logger.exception("Unhandled error during ETL SQL generation: %s", exc)
            return SQLResult.failure(error_message=str(exc))

    def _map_dto_to_entity(self, dto: ETLRequestDTO) -> ETLRequest:
        source_tables = [self._parse_table_schema(t) for t in dto.source_tables_raw]
        target_table = self._parse_table_schema(dto.target_table_raw)
        business_rules = self._parse_business_rules(dto.business_rules_text)

        return ETLRequest(
            source_tables=source_tables,
            target_table=target_table,
            data_sample=dto.data_sample,
            business_rules=business_rules,
            target_dialect=dto.target_dialect,
            additional_context=dto.additional_context,
        )

    def _parse_table_schema(self, dto_table: TableSchemaDTO) -> TableSchema:
        return TableSchema(
            table_name=dto_table.table_name,
            ddl_raw=dto_table.ddl_or_description,
            columns=[],
        )

    def _parse_business_rules(self, rules_text: str) -> BusinessRuleSet:
        if not rules_text or not rules_text.strip():
            return BusinessRuleSet()
        rules = []
        for line in rules_text.splitlines():
            line = line.strip()
            if line:
                rules.append(BusinessRule(description=line))
        return BusinessRuleSet(rules=rules)
