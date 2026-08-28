from backend.app.project_store import (
    create_project,
    create_row,
    delete_row,
    list_rows,
    update_row,
)


def _schema() -> dict:
    return {
        "schemaVersion": "0.2",
        "app": {"name": "Teste", "sourceType": "csv"},
        "entities": [
            {
                "name": "clientes",
                "label": "Clientes",
                "primaryKey": "id",
                "storageKey": "__sf_rowid",
                "fields": [
                    {"name": "id", "label": "ID", "type": "integer", "nullable": False},
                    {"name": "nome", "label": "Nome", "type": "string", "nullable": False},
                ],
            }
        ],
        "relationships": [],
        "pages": [],
    }


def test_project_store_crud(tmp_path) -> None:
    project = create_project(
        _schema(),
        {"clientes": [{"id": 1, "nome": "Ana"}, {"id": 2, "nome": "Bruno"}]},
        tmp_path,
    )
    project_id = project["projectId"]

    listed = list_rows(project_id, "clientes", data_dir=tmp_path)
    assert listed["total"] == 2
    assert listed["items"][0]["nome"] == "Ana"

    created = create_row(project_id, "clientes", {"id": 3, "nome": "Carla"}, tmp_path)
    assert created["nome"] == "Carla"

    updated = update_row(project_id, "clientes", created["__sf_rowid"], {"nome": "Carla Souza"}, tmp_path)
    assert updated["nome"] == "Carla Souza"

    delete_row(project_id, "clientes", created["__sf_rowid"], tmp_path)
    assert list_rows(project_id, "clientes", data_dir=tmp_path)["total"] == 2
