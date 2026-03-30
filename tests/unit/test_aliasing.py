from catalogo_acervo.domain.entities.alias import Alias
from catalogo_acervo.domain.services.aliasing import apply_aliases


def test_apply_aliases_returns_canonical_text() -> None:
    aliases = [
        Alias(alias_kind="author", alias_text="wj grudem", canonical_text="wayne grudem", source_scope="mock_csv")
    ]

    normalized = apply_aliases(
        "wj grudem",
        alias_kind="author",
        aliases=aliases,
        source_scope="mock_csv",
    )

    assert normalized == "wayne grudem"


def test_apply_aliases_respects_source_scope() -> None:
    aliases = [
        Alias(alias_kind="author", alias_text="wj grudem", canonical_text="wayne grudem", source_scope="logos_csv")
    ]

    normalized = apply_aliases(
        "wj grudem",
        alias_kind="author",
        aliases=aliases,
        source_scope="mock_csv",
    )

    assert normalized == "wj grudem"
