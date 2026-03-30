from __future__ import annotations

from pathlib import Path

from catalogo_acervo.domain.entities.catalog_item import CatalogItem
from catalogo_acervo.domain.entities.import_job import ImportJob
from catalogo_acervo.domain.contracts.parser_contract import ParserContract
from catalogo_acervo.domain.services.normalization import normalize_text
from catalogo_acervo.infrastructure.db.repositories.catalog_item_repository import CatalogItemRepository
from catalogo_acervo.infrastructure.db.repositories.import_repository import ImportRepository
from catalogo_acervo.infrastructure.logging.processing_logger import ProcessingLogger


class ImportSourceItemsUseCase:
    def __init__(
        self,
        parser: ParserContract,
        import_repository: ImportRepository,
        item_repository: CatalogItemRepository,
        logger: ProcessingLogger,
    ) -> None:
        self.parser = parser
        self.import_repository = import_repository
        self.item_repository = item_repository
        self.logger = logger

    def execute(self, source_id: int, file_path: Path) -> int:
        job_id = self.import_repository.create(
            ImportJob(source_id=source_id, status="running", raw_file_name=file_path.name)
        )

        records = self.parser.parse(file_path)
        inserted = 0
        errors = 0

        for record in records:
            try:
                item = CatalogItem(
                    source_id=source_id,
                    source_key=str(record.get("source_key") or record.get("id") or record.get("title")),
                    item_type=str(record.get("item_type") or "other"),
                    title_raw=str(record.get("title") or ""),
                    title_norm=normalize_text(record.get("title")),
                    author_raw=record.get("author"),
                    author_norm=normalize_text(record.get("author")),
                    series_raw=record.get("series"),
                    series_norm=normalize_text(record.get("series")),
                    publisher_raw=record.get("publisher"),
                    publisher_norm=normalize_text(record.get("publisher")),
                    year=int(record["year"]) if record.get("year") else None,
                    language=record.get("language"),
                    resource_type=record.get("resource_type"),
                    raw_record_json=record,
                    current_import_id=job_id,
                )
                self.item_repository.upsert(item)
                inserted += 1
            except Exception as exc:  # pragma: no cover - segurança de pipeline
                errors += 1
                self.logger.log(
                    message="Falha ao processar registro",
                    level="ERROR",
                    source_id=source_id,
                    import_id=job_id,
                    context={"error": str(exc), "record": record},
                )

        status = "completed_with_errors" if errors else "completed"
        self.import_repository.finish(job_id, status, len(records), inserted, errors)
        self.logger.log(
            message="Importação finalizada",
            source_id=source_id,
            import_id=job_id,
            context={"total_read": len(records), "inserted": inserted, "errors": errors},
        )
        return job_id
