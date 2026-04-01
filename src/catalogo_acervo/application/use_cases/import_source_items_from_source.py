from __future__ import annotations

import hashlib
import json as _json
from pathlib import Path
from typing import Any, Protocol

from catalogo_acervo.domain.entities.alias import Alias
from catalogo_acervo.domain.entities.catalog_item import CatalogItem
from catalogo_acervo.domain.entities.import_job import ImportJob
from catalogo_acervo.domain.entities.source import Source
from catalogo_acervo.domain.services.aliasing import apply_aliases
from catalogo_acervo.domain.services.normalization import normalize_text
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import (
    CatalogItemRepository,
)
from catalogo_acervo.infrastructure.db.repositories.import_repository import ImportRepository
from catalogo_acervo.infrastructure.ingestion.parser_registry import ParserRegistry
from catalogo_acervo.infrastructure.logging.processing_logger import ProcessingLogger

from .suggest_matches import SuggestMatchesUseCase

# Campos candidatos para compor source_key, em ordem de preferência.
_SOURCE_KEY_CANDIDATES = ("source_key", "id")


def _extract_source_key(record: dict[str, Any], source_id: int, index: int) -> str:
    """Extrai source_key do registro com fallback explícito e rastreável.

    Política:
    1. Campo 'source_key' no registro (preferido).
    2. Campo 'id' no registro.
    3. Fallback determinístico baseado em hash SHA-256 do conteúdo do registro -
       nunca usa posição da linha para evitar corrupção de identidade entre reimportações.

    O parâmetro `index` é mantido na assinatura para compatibilidade, mas não é usado no fallback.
    O parâmetro `source_id` também é mantido por compatibilidade com chamadas existentes.
    """
    del source_id, index

    for field in _SOURCE_KEY_CANDIDATES:
        value = record.get(field)
        if value is not None and str(value).strip():
            return str(value).strip()

    content = _json.dumps(record, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(content.encode()).hexdigest()[:16]
    return f"hash:{digest}"


class SourceLookup(Protocol):
    def get_by_id(self, source_id: int) -> Source | None: ...


class AliasLookup(Protocol):
    def list_active(self) -> list[Alias]: ...


class ImportSourceItemsFromSourceUseCase:
    def __init__(
        self,
        *,
        source_lookup: SourceLookup,
        alias_lookup: AliasLookup,
        parser_registry: ParserRegistry,
        import_repository: ImportRepository,
        item_repository: CatalogItemRepository,
        logger: ProcessingLogger,
        suggest_matches_use_case: SuggestMatchesUseCase | None = None,
    ) -> None:
        self.source_lookup = source_lookup
        self.alias_lookup = alias_lookup
        self.parser_registry = parser_registry
        self.import_repository = import_repository
        self.item_repository = item_repository
        self.logger = logger
        self.suggest_matches_use_case = suggest_matches_use_case

    def execute(self, source_id: int, file_path: Path) -> int:
        source = self.source_lookup.get_by_id(source_id)
        if source is None:
            raise ValueError(f"Fonte {source_id} não encontrada")

        parser = self.parser_registry.get(source.parser_name)
        aliases = self.alias_lookup.list_active()

        job_id = self.import_repository.create(
            ImportJob(source_id=source_id, status="running", raw_file_name=file_path.name)
        )

        try:
            records = parser.parse(file_path)
        except Exception as exc:
            self.logger.log(
                message="Falha no parser - importação abortada",
                level="ERROR",
                source_id=source_id,
                import_id=job_id,
                context={"parser_name": source.parser_name, "file_path": str(file_path), "error": str(exc)},
            )
            self.import_repository.finish(job_id, "failed", 0, 0, 0, 0, 1)
            raise

        inserted = updated = skipped = errors = 0
        affected_ids: list[int] = []
        seen_keys: set[str] = set()

        for index, record in enumerate(records):
            try:
                source_key = _extract_source_key(record, source_id, index)

                if source_key.startswith("hash:"):
                    self.logger.log(
                        message="Fallback source_key gerado por hash",
                        level="INFO",
                        source_id=source_id,
                        import_id=job_id,
                        context={"hash": source_key, "index": index},
                    )

                if source_key.startswith("hash:") and source_key in seen_keys:
                    self.logger.log(
                        message="Colisão de hash detectada no fallback de source_key",
                        level="ERROR",
                        source_id=source_id,
                        import_id=job_id,
                        context={"hash": source_key, "index": index},
                    )
                    errors += 1
                    continue

                seen_keys.add(source_key)
                title_raw = str(record.get("title") or "").strip()
                if not title_raw:
                    raise ValueError(f"Registro sem título (source_key={source_key!r})")

                item = CatalogItem(
                    source_id=source_id,
                    source_key=source_key,
                    item_type=str(record.get("item_type") or "other"),
                    title_raw=title_raw,
                    title_norm=apply_aliases(
                        record.get("title"),
                        alias_kind="title",
                        aliases=aliases,
                        source_scope=source.parser_name,
                    ),
                    author_raw=record.get("author") or None,
                    author_norm=apply_aliases(
                        record.get("author"),
                        alias_kind="author",
                        aliases=aliases,
                        source_scope=source.parser_name,
                    ),
                    series_raw=record.get("series") or None,
                    series_norm=apply_aliases(
                        record.get("series"),
                        alias_kind="series",
                        aliases=aliases,
                        source_scope=source.parser_name,
                    ),
                    publisher_raw=record.get("publisher") or None,
                    publisher_norm=apply_aliases(
                        record.get("publisher"),
                        alias_kind="publisher",
                        aliases=aliases,
                        source_scope=source.parser_name,
                    ),
                    year=int(record["year"]) if record.get("year") else None,
                    language=normalize_text(record.get("language")),
                    resource_type=normalize_text(record.get("resource_type")),
                    raw_record_json=record,
                    current_import_id=job_id,
                )
                item_id, operation = self.item_repository.upsert(item)
                if operation == "inserted":
                    inserted += 1
                    affected_ids.append(item_id)
                elif operation == "updated":
                    updated += 1
                    affected_ids.append(item_id)
                else:
                    skipped += 1
            except Exception as exc:
                errors += 1
                self.logger.log(
                    message="Falha ao processar registro com fonte resolvida",
                    level="ERROR",
                    source_id=source_id,
                    import_id=job_id,
                    context={
                        "error": str(exc),
                        "record": record,
                        "parser_name": source.parser_name,
                    },
                )

        status = "completed_with_errors" if errors else "completed"
        self.import_repository.finish(job_id, status, len(records), inserted, updated, skipped, errors)
        self.logger.log(
            message="Importação finalizada com parser resolvido por fonte",
            source_id=source_id,
            import_id=job_id,
            context={
                "parser_name": source.parser_name,
                "total_read": len(records),
                "inserted": inserted,
                "updated": updated,
                "skipped": skipped,
                "errors": errors,
            },
        )
        if self.suggest_matches_use_case is not None and affected_ids:
            self.suggest_matches_use_case.execute(affected_item_ids=affected_ids)

        return job_id
