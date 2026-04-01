from __future__ import annotations

from catalogo_acervo.domain.entities.catalog_item import CatalogItem
from catalogo_acervo.interfaces.dto.catalog_item_dto import CatalogItemDTO


class CatalogItemMapper:
    """Mapper entre CatalogItem (entidade) e CatalogItemDTO."""

    @staticmethod
    def to_dto(entity: CatalogItem) -> CatalogItemDTO:
        return CatalogItemDTO(
            id=entity.id,
            source_id=entity.source_id,
            source_key=entity.source_key,
            item_type=entity.item_type,
            title_raw=entity.title_raw,
            title_norm=entity.title_norm,
            subtitle_raw=entity.subtitle_raw,
            author_raw=entity.author_raw,
            author_norm=entity.author_norm,
            series_raw=entity.series_raw,
            publisher_raw=entity.publisher_raw,
            year=entity.year,
            language=entity.language,
            path_or_location=entity.path_or_location,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(dto: CatalogItemDTO) -> CatalogItem:
        return CatalogItem(
            id=dto.id,
            source_id=dto.source_id,
            source_key=dto.source_key,
            item_type=dto.item_type,
            title_raw=dto.title_raw,
            title_norm=dto.title_norm,
            subtitle_raw=dto.subtitle_raw,
            author_raw=dto.author_raw,
            author_norm=dto.author_norm,
            series_raw=dto.series_raw,
            publisher_raw=dto.publisher_raw,
            year=dto.year,
            language=dto.language,
            path_or_location=dto.path_or_location,
            is_active=dto.is_active,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )
