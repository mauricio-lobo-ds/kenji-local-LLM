from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class SQLResultStatus(StrEnum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    PARTIAL = "PARTIAL"


class SQLResult(BaseModel, frozen=True):
    status: SQLResultStatus
    sql: str = ""
    error_message: str = ""
    raw_llm_response: str = ""
    model_name: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @classmethod
    def success(
        cls,
        sql: str,
        raw_llm_response: str = "",
        model_name: str = "",
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> SQLResult:
        return cls(
            status=SQLResultStatus.SUCCESS,
            sql=sql,
            raw_llm_response=raw_llm_response,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    @classmethod
    def failure(
        cls,
        error_message: str,
        raw_llm_response: str = "",
        model_name: str = "",
    ) -> SQLResult:
        return cls(
            status=SQLResultStatus.ERROR,
            error_message=error_message,
            raw_llm_response=raw_llm_response,
            model_name=model_name,
        )

    def is_success(self) -> bool:
        return self.status == SQLResultStatus.SUCCESS
