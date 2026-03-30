from pathlib import Path

from catalogo_acervo.infrastructure.ingestion.parsers.mock_parser import MockParser


def test_mock_parser_reads_rows() -> None:
    parser = MockParser()
    rows = parser.parse(Path("data/samples/mock_source.csv"))
    assert len(rows) == 3
    assert rows[0]["source_key"] == "BK-001"
