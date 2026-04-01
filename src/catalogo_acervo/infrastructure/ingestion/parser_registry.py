from __future__ import annotations

from catalogo_acervo.domain.contracts.parser_contract import ParserContract


class ParserRegistry:
    def __init__(self, parsers: list[ParserContract] | None = None) -> None:
        self._parsers: dict[str, ParserContract] = {}
        for parser in parsers or []:
            self.register(parser)

    def register(self, parser: ParserContract) -> None:
        self._parsers[parser.parser_name] = parser

    def get(self, parser_name: str) -> ParserContract:
        parser = self._parsers.get(parser_name)
        if parser is None:
            available = ", ".join(sorted(self._parsers)) or "<none>"
            raise ValueError(f"Parser '{parser_name}' não registrado. Disponíveis: {available}")
        return parser
