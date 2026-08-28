from __future__ import annotations

import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


PROJECT_ID_RE = re.compile(r"^[a-f0-9]{12}$")


class ProjectNotFoundError(LookupError):
    pass


class EntityNotFoundError(LookupError):
    pass


class RowNotFoundError(LookupError):
    pass


class InvalidPayloadError(ValueError):
    pass


def _data_root(data_dir: str | Path | None = None) -> Path:
    if data_dir is not None:
        root = Path(data_dir)
    else:
        configured = os.getenv("SHEETFORGE_DATA_DIR")
        root = Path(configured) if configured else Path(__file__).resolve().parents[1] / "data"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _db_path(project_id: str, data_dir: str | Path | None = None) -> Path:
    if not PROJECT_ID_RE.fullmatch(project_id):
        raise ProjectNotFoundError("Projeto inválido.")
    path = _data_root(data_dir) / f"{project_id}.sqlite3"
    if not path.exists():
        raise ProjectNotFoundError("Projeto não encontrado.")
    return path


def _sqlite_type(field_type: str) -> str:
    return {
        "integer": "INTEGER",
        "number": "REAL",
        "boolean": "INTEGER",
    }.get(field_type, "TEXT")


def _open(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _set_meta(connection: sqlite3.Connection, key: str, value: Any) -> None:
    connection.execute(
        "INSERT OR REPLACE INTO __sheetforge_meta (key, value) VALUES (?, ?)",
        (key, json.dumps(value, ensure_ascii=False, default=str)),
    )


def _get_meta(connection: sqlite3.Connection, key: str) -> Any:
    row = connection.execute("SELECT value FROM __sheetforge_meta WHERE key = ?", (key,)).fetchone()
    if row is None:
        return None
    return json.loads(row["value"])


def _entity_definition(schema: dict[str, Any], entity_name: str) -> dict[str, Any]:
    entity = next((item for item in schema.get("entities", []) if item["name"] == entity_name), None)
    if entity is None:
        raise EntityNotFoundError(f"Entidade '{entity_name}' não encontrada.")
    return entity


def _validate_payload(entity: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    allowed = {field["name"] for field in entity["fields"]}
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise InvalidPayloadError(f"Campos desconhecidos: {', '.join(unknown)}")
    return {key: value for key, value in payload.items() if key in allowed}


def create_project(
    app_schema: dict[str, Any],
    rows_by_entity: dict[str, list[dict[str, Any]]],
    data_dir: str | Path | None = None,
) -> dict[str, Any]:
    project_id = uuid4().hex[:12]
    path = _data_root(data_dir) / f"{project_id}.sqlite3"
    created_at = datetime.now(timezone.utc).isoformat()
    summary: dict[str, dict[str, int]] = {}

    with _open(path) as connection:
        connection.execute(
            "CREATE TABLE __sheetforge_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )

        for entity in app_schema["entities"]:
            table_name = entity["name"]
            field_names = [field["name"] for field in entity["fields"]]
            if "__sf_rowid" in field_names:
                raise InvalidPayloadError("O nome de campo '__sf_rowid' é reservado pelo SheetForge.")

            columns = ["__sf_rowid INTEGER PRIMARY KEY AUTOINCREMENT"]
            columns.extend(
                f"{_quote(field['name'])} {_sqlite_type(field['type'])}"
                for field in entity["fields"]
            )
            connection.execute(f"CREATE TABLE {_quote(table_name)} ({', '.join(columns)})")

            records = rows_by_entity.get(table_name, [])
            if records and field_names:
                placeholders = ", ".join("?" for _ in field_names)
                quoted_fields = ", ".join(_quote(name) for name in field_names)
                values = [[record.get(name) for name in field_names] for record in records]
                connection.executemany(
                    f"INSERT INTO {_quote(table_name)} ({quoted_fields}) VALUES ({placeholders})",
                    values,
                )

            summary[table_name] = {"rowsImported": len(records)}

        _set_meta(connection, "project_id", project_id)
        _set_meta(connection, "created_at", created_at)
        _set_meta(connection, "schema", app_schema)
        _set_meta(connection, "import_summary", summary)

    return {
        "projectId": project_id,
        "createdAt": created_at,
        "database": path.name,
        "importSummary": summary,
        "schema": app_schema,
    }


def get_project(project_id: str, data_dir: str | Path | None = None) -> dict[str, Any]:
    path = _db_path(project_id, data_dir)
    with _open(path) as connection:
        return {
            "projectId": _get_meta(connection, "project_id"),
            "createdAt": _get_meta(connection, "created_at"),
            "database": path.name,
            "importSummary": _get_meta(connection, "import_summary") or {},
            "schema": _get_meta(connection, "schema"),
        }


def list_projects(data_dir: str | Path | None = None) -> list[dict[str, Any]]:
    projects = []
    for path in sorted(_data_root(data_dir).glob("*.sqlite3"), reverse=True):
        try:
            projects.append(get_project(path.stem, data_dir))
        except (sqlite3.DatabaseError, ProjectNotFoundError):
            continue
    return projects


def list_rows(
    project_id: str,
    entity_name: str,
    limit: int = 100,
    offset: int = 0,
    search: str | None = None,
    data_dir: str | Path | None = None,
) -> dict[str, Any]:
    path = _db_path(project_id, data_dir)
    limit = max(1, min(limit, 500))
    offset = max(0, offset)

    with _open(path) as connection:
        schema = _get_meta(connection, "schema")
        entity = _entity_definition(schema, entity_name)
        fields = [field["name"] for field in entity["fields"]]

        where = ""
        params: list[Any] = []
        if search and fields:
            clauses = [f"CAST({_quote(field)} AS TEXT) LIKE ?" for field in fields]
            where = " WHERE " + " OR ".join(clauses)
            params = [f"%{search}%"] * len(fields)

        total = connection.execute(
            f"SELECT COUNT(*) AS total FROM {_quote(entity_name)}{where}", params
        ).fetchone()["total"]
        rows = connection.execute(
            f"SELECT * FROM {_quote(entity_name)}{where} ORDER BY __sf_rowid LIMIT ? OFFSET ?",
            [*params, limit, offset],
        ).fetchall()

    return {
        "entity": entity_name,
        "items": [dict(row) for row in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def get_row(
    project_id: str,
    entity_name: str,
    row_id: int,
    data_dir: str | Path | None = None,
) -> dict[str, Any]:
    path = _db_path(project_id, data_dir)
    with _open(path) as connection:
        schema = _get_meta(connection, "schema")
        _entity_definition(schema, entity_name)
        row = connection.execute(
            f"SELECT * FROM {_quote(entity_name)} WHERE __sf_rowid = ?", (row_id,)
        ).fetchone()
        if row is None:
            raise RowNotFoundError("Registro não encontrado.")
        return dict(row)


def create_row(
    project_id: str,
    entity_name: str,
    payload: dict[str, Any],
    data_dir: str | Path | None = None,
) -> dict[str, Any]:
    path = _db_path(project_id, data_dir)
    with _open(path) as connection:
        schema = _get_meta(connection, "schema")
        entity = _entity_definition(schema, entity_name)
        clean = _validate_payload(entity, payload)

        if clean:
            names = list(clean)
            placeholders = ", ".join("?" for _ in names)
            cursor = connection.execute(
                f"INSERT INTO {_quote(entity_name)} ({', '.join(_quote(name) for name in names)}) VALUES ({placeholders})",
                [clean[name] for name in names],
            )
        else:
            cursor = connection.execute(f"INSERT INTO {_quote(entity_name)} DEFAULT VALUES")
        row_id = cursor.lastrowid

    return get_row(project_id, entity_name, int(row_id), data_dir)


def update_row(
    project_id: str,
    entity_name: str,
    row_id: int,
    payload: dict[str, Any],
    data_dir: str | Path | None = None,
) -> dict[str, Any]:
    path = _db_path(project_id, data_dir)
    with _open(path) as connection:
        schema = _get_meta(connection, "schema")
        entity = _entity_definition(schema, entity_name)
        clean = _validate_payload(entity, payload)

        exists = connection.execute(
            f"SELECT 1 FROM {_quote(entity_name)} WHERE __sf_rowid = ?", (row_id,)
        ).fetchone()
        if exists is None:
            raise RowNotFoundError("Registro não encontrado.")

        if clean:
            assignments = ", ".join(f"{_quote(name)} = ?" for name in clean)
            connection.execute(
                f"UPDATE {_quote(entity_name)} SET {assignments} WHERE __sf_rowid = ?",
                [*clean.values(), row_id],
            )

    return get_row(project_id, entity_name, row_id, data_dir)


def delete_row(
    project_id: str,
    entity_name: str,
    row_id: int,
    data_dir: str | Path | None = None,
) -> None:
    path = _db_path(project_id, data_dir)
    with _open(path) as connection:
        schema = _get_meta(connection, "schema")
        _entity_definition(schema, entity_name)
        cursor = connection.execute(
            f"DELETE FROM {_quote(entity_name)} WHERE __sf_rowid = ?", (row_id,)
        )
        if cursor.rowcount == 0:
            raise RowNotFoundError("Registro não encontrado.")
