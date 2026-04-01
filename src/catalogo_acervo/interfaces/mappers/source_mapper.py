from __future__ import annotations

from catalogo_acervo.domain.entities.source import Source
from catalogo_acervo.interfaces.dto.source_dto import SourceDTO


class SourceMapper:
    """Mapper entre Source (entidade) e SourceDTO."""

    @staticmethod
    def to_dto(entity: Source) -> SourceDTO:
        return SourceDTO(
            id=entity.id,
            name=entity.name,
            source_type=entity.source_type,
            parser_name=entity.parser_name,
            description=entity.description,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(dto: SourceDTO) -> Source:
        return Source(
            id=dto.id,
            name=dto.name,
            source_type=dto.source_type,
            parser_name=dto.parser_name,
            description=dto.description,
            is_active=dto.is_active,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )
