from __future__ import annotations

from pathlib import Path
from typing import Any

from catalogo_acervo.domain.contracts.parser_contract import ParserContract


class BaseParser(ParserContract):
    parser_name = "base"

    def parse(self, file_path: Path) -> list[dict[str, Any]]:
        raise NotImplementedError
