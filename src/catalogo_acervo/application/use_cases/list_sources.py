from __future__ import annotations

from catalogo_acervo.domain.entities.source import Source
from catalogo_acervo.infrastructure.db.repositories.source_repository import SourceRepository


class ListSourcesUseCase:
    def __init__(self, repository: SourceRepository) -> None:
        self.repository = repository

    def execute(self) -> list[Source]:
        return self.repository.list_all()
