from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class ParserContract(Protocol):
    parser_name: str

    def parse(self, file_path: Path) -> list[dict[str, Any]]:
        """Retorna registros brutos de uma fonte."""
