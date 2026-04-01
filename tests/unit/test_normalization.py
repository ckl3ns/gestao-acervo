from catalogo_acervo.domain.services.normalization import normalize_text


def test_normalize_text_lower_trim_spaces_and_remove_diacritics() -> None:
    assert normalize_text("  Teologia   Bíblica ") == "teologia biblica"
