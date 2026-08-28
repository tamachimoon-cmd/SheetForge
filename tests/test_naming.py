from backend.app.naming import normalize_identifier


def test_normalize_identifier_removes_accents_and_symbols() -> None:
    assert normalize_identifier("Nº OS / Técnico") == "no_os_tecnico"


def test_normalize_identifier_prefixes_numeric_names() -> None:
    assert normalize_identifier("2026 Total") == "field_2026_total"
