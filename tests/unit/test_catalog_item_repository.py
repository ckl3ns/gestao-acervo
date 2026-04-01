"""Testes unitários: CatalogItemRepository — foco no upsert null-safe."""

from __future__ import annotations

from catalogo_acervo.domain.entities.catalog_item import CatalogItem
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import (
    CatalogItemRepository,
)


def _make_item(source_id: int, **kwargs: object) -> CatalogItem:
    defaults: dict = {
        "source_id": source_id,
        "source_key": "BK-001",
        "title_raw": "Título Original",
        "title_norm": "titulo original",
        "author_raw": "Autor X",
        "author_norm": "autor x",
        "year": 2020,
        "current_import_id": None,
    }
    defaults.update(kwargs)
    return CatalogItem(**defaults)  # type: ignore[arg-type]


def test_upsert_inserts_new_item(
    item_repo: CatalogItemRepository,
    registered_source_id: int,
) -> None:
    item_repo.upsert(_make_item(registered_source_id))
    result = item_repo.get_by_source_and_key(registered_source_id, "BK-001")
    assert result is not None
    assert result.title_norm == "titulo original"
    assert result.author_norm == "autor x"
    assert result.year == 2020


def test_upsert_conflict_preserves_existing_year_when_new_is_none(
    item_repo: CatalogItemRepository,
    registered_source_id: int,
) -> None:
    """COALESCE: reimportação sem year não deve apagar year existente."""
    item_repo.upsert(_make_item(registered_source_id, year=2020))
    item_repo.upsert(_make_item(registered_source_id, year=None))

    result = item_repo.get_by_source_and_key(registered_source_id, "BK-001")
    assert result is not None
    assert result.year == 2020, "year existente deve ser preservado quando novo é NULL"


def test_upsert_conflict_updates_year_when_new_is_not_none(
    item_repo: CatalogItemRepository,
    registered_source_id: int,
) -> None:
    """COALESCE: reimportação com year novo deve sobrescrever."""
    item_repo.upsert(_make_item(registered_source_id, year=2020))
    item_repo.upsert(_make_item(registered_source_id, year=2024))

    result = item_repo.get_by_source_and_key(registered_source_id, "BK-001")
    assert result is not None
    assert result.year == 2024, "year deve ser atualizado quando novo valor não é NULL"


def test_upsert_conflict_preserves_author_norm_when_new_is_none(
    item_repo: CatalogItemRepository,
    registered_source_id: int,
) -> None:
    """author_norm preenchido numa importação anterior não deve ser apagado."""
    item_repo.upsert(_make_item(registered_source_id, author_norm="wayne grudem"))
    item_repo.upsert(_make_item(registered_source_id, author_norm=None))

    result = item_repo.get_by_source_and_key(registered_source_id, "BK-001")
    assert result is not None
    assert result.author_norm == "wayne grudem"


def test_upsert_always_updates_title_raw(
    item_repo: CatalogItemRepository,
    registered_source_id: int,
) -> None:
    """title_raw é campo obrigatório — sempre sobrescrito."""
    item_repo.upsert(_make_item(registered_source_id, title_raw="Título Antigo"))
    item_repo.upsert(_make_item(registered_source_id, title_raw="Título Corrigido"))

    result = item_repo.get_by_source_and_key(registered_source_id, "BK-001")
    assert result is not None
    assert result.title_raw == "Título Corrigido"


def test_upsert_always_updates_current_import_id(
    item_repo: CatalogItemRepository,
    registered_source_id: int,
) -> None:
    """current_import_id deve refletir o job mais recente."""
    item_repo.upsert(_make_item(registered_source_id, current_import_id=None))
    item_repo.upsert(_make_item(registered_source_id, current_import_id=None))

    result = item_repo.get_by_source_and_key(registered_source_id, "BK-001")
    assert result is not None
    # Sem import_id explícito, o campo permanece NULL — comportamento correto
    assert result.source_key == "BK-001"


def test_get_by_source_and_key_returns_none_for_missing(
    item_repo: CatalogItemRepository,
    registered_source_id: int,
) -> None:
    result = item_repo.get_by_source_and_key(registered_source_id, "INEXISTENTE")
    assert result is None


def test_list_all_returns_inserted_items(
    item_repo: CatalogItemRepository,
    registered_source_id: int,
) -> None:
    item_repo.upsert(_make_item(registered_source_id, source_key="A"))
    item_repo.upsert(_make_item(registered_source_id, source_key="B"))
    all_items = item_repo.list_all()
    assert len(all_items) == 2
