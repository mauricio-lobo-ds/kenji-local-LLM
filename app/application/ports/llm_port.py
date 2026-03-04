from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.etl_request import ETLRequest
from app.domain.entities.sql_result import SQLResult


class LLMPort(ABC):
    @abstractmethod
    def generate_sql(self, request: ETLRequest) -> SQLResult:
        """Generate ETL SQL from the given request."""

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if the LLM backend is reachable."""
