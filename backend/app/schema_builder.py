from __future__ import annotations

from typing import Any


def build_app_schema(analysis: dict[str, Any]) -> dict[str, Any]:
    entities = []
    pages = []

    for entity in analysis["entities"]:
        entities.append(
            {
                "name": entity["name"],
                "label": entity["source_name"],
                "primaryKey": entity.get("primary_key"),
                "storageKey": "__sf_rowid",
                "fields": [
                    {
                        "name": field["name"],
                        "label": field["source_name"],
                        "type": field["type"],
                        "nullable": field["nullable"],
                    }
                    for field in entity["fields"]
                ],
            }
        )
        pages.append(
            {
                "type": "crud",
                "name": entity["name"],
                "label": entity["source_name"],
                "entity": entity["name"],
                "features": ["list", "search", "filter", "create", "edit", "delete"],
            }
        )

    return {
        "schemaVersion": "0.2",
        "app": {
            "name": analysis["workbook"]["filename"].rsplit(".", 1)[0],
            "sourceType": analysis["workbook"]["type"],
            "runtime": {"database": "sqlite", "mode": "migrate"},
        },
        "entities": entities,
        "relationships": analysis.get("relationships", []),
        "pages": pages,
        "dashboard": {
            "enabled": True,
            "widgets": [
                {"type": "metric", "metric": "entity_count", "label": "Entidades"},
                {"type": "metric", "metric": "relationship_count", "label": "Relações"},
            ],
        },
    }
