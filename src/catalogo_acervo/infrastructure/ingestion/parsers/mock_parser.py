from __future__ import annotations

import csv
from pathlib import Path

from catalogo_acervo.infrastructure.ingestion.base_parser import BaseParser


class MockParser(BaseParser):
    parser_name = "mock_csv"

    def parse(self, file_path: Path) -> list[dict]:
        rows: list[dict] = []
        with file_path.open("r", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                rows.append(row)
        return rows
