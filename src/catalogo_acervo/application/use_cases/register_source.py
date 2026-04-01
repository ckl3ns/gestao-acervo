from __future__ import annotations

from catalogo_acervo.domain.entities.source import Source
from catalogo_acervo.infrastructure.db.repositories.source_repository import SourceRepository
from catalogo_acervo.infrastructure.ingestion.parser_registry import ParserRegistry


class RegisterSourceUseCase:
    def __init__(
        self,
        repository: SourceRepository,
        parser_registry: ParserRegistry | None = None,
    ) -> None:
        self.repository = repository
        self.parser_registry = parser_registry

    def execute(self, name: str, source_type: str, parser_name: str, description: str | None = None) -> int:
        if self.parser_registry is not None:
            self.parser_registry.get(parser_name)
        source = Source(name=name, source_type=source_type, parser_name=parser_name, description=description)
        return self.repository.add(source)
