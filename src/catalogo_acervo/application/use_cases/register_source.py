from __future__ import annotations

from catalogo_acervo.domain.entities.source import Source
from catalogo_acervo.infrastructure.db.repositories.source_repository import SourceRepository


class RegisterSourceUseCase:
    def __init__(self, repository: SourceRepository) -> None:
        self.repository = repository

    def execute(self, name: str, source_type: str, parser_name: str, description: str | None = None) -> int:
        source = Source(name=name, source_type=source_type, parser_name=parser_name, description=description)
        return self.repository.add(source)
