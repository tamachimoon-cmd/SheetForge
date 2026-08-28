from app.schema_builder import build_app_schema


def test_build_app_schema_creates_crud_page():
    analysis = {
        "workbook": {"filename": "clientes.xlsx", "type": "xlsx"},
        "entities": [
            {
                "name": "clientes",
                "source_name": "Clientes",
                "primary_key": "id",
                "fields": [
                    {"name": "id", "source_name": "ID", "type": "integer", "nullable": False},
                    {"name": "nome", "source_name": "Nome", "type": "string", "nullable": False},
                ],
            }
        ],
        "relationships": [],
    }

    schema = build_app_schema(analysis)

    assert schema["schemaVersion"] == "0.2"
    assert schema["entities"][0]["primaryKey"] == "id"
    assert schema["entities"][0]["storageKey"] == "__sf_rowid"
    assert schema["app"]["runtime"] == {"database": "sqlite", "mode": "migrate"}
    assert schema["pages"][0]["type"] == "crud"
