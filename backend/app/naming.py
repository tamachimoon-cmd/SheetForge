from __future__ import annotations

import re
import unicodedata


def normalize_identifier(value: str, fallback: str = "field") -> str:
    """Transforma rótulos humanos em identificadores seguros e estáveis."""
    normalized = unicodedata.normalize("NFKD", str(value))
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", normalized.strip()).strip("_").lower()

    if not normalized:
        normalized = fallback
    if normalized[0].isdigit():
        normalized = f"{fallback}_{normalized}"

    return normalized
