import pytest

from catalogo_acervo.infrastructure.ingestion.parser_registry import ParserRegistry
from catalogo_acervo.infrastructure.ingestion.parsers.mock_parser import MockParser


def test_parser_registry_returns_registered_parser() -> None:
    registry = ParserRegistry([MockParser()])
    parser = registry.get("mock_csv")
    assert parser.parser_name == "mock_csv"


def test_parser_registry_raises_for_unknown_parser() -> None:
    registry = ParserRegistry([MockParser()])
    with pytest.raises(ValueError):
        registry.get("logos_csv")
