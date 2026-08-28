from __future__ import annotations

from typing import Any

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .analyzer import analyze_file
from .project_store import (
    EntityNotFoundError,
    InvalidPayloadError,
    ProjectNotFoundError,
    RowNotFoundError,
    create_project,
    create_row,
    delete_row,
    get_project,
    get_row,
    list_projects,
    list_rows,
    update_row,
)
from .schema_builder import build_app_schema
from .source_reader import read_source_rows

app = FastAPI(
    title="SheetForge API",
    version="0.2.0",
    description="Transforme planilhas em aplicações persistentes e manipuláveis.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _raise_store_error(exc: Exception) -> None:
    if isinstance(exc, ProjectNotFoundError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if isinstance(exc, EntityNotFoundError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if isinstance(exc, RowNotFoundError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if isinstance(exc, InvalidPayloadError):
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    raise exc


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "sheetforge-api", "version": "0.2.0"}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)) -> dict[str, Any]:
    filename = file.filename or "upload"
    if not filename.lower().endswith((".xlsx", ".csv")):
        raise HTTPException(status_code=415, detail="Use um arquivo .xlsx ou .csv.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="O arquivo está vazio.")

    try:
        analysis = analyze_file(content, filename)
        schema = build_app_schema(analysis)
    except ValueError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Não foi possível analisar o arquivo: {exc}") from exc

    return {"analysis": analysis, "app_schema": schema}


@app.post("/api/projects/import", status_code=201)
async def import_project(file: UploadFile = File(...)) -> dict[str, Any]:
    filename = file.filename or "upload"
    if not filename.lower().endswith((".xlsx", ".csv")):
        raise HTTPException(status_code=415, detail="Use um arquivo .xlsx ou .csv.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="O arquivo está vazio.")

    try:
        analysis = analyze_file(content, filename)
        schema = build_app_schema(analysis)
        rows_by_entity = read_source_rows(content, filename, schema)
        project = create_project(schema, rows_by_entity)
    except (InvalidPayloadError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Não foi possível importar o arquivo: {exc}") from exc

    return {"analysis": analysis, "project": project}


@app.get("/api/projects")
def projects() -> dict[str, Any]:
    items = list_projects()
    return {"items": items, "total": len(items)}


@app.get("/api/projects/{project_id}")
def project(project_id: str) -> dict[str, Any]:
    try:
        return get_project(project_id)
    except Exception as exc:
        _raise_store_error(exc)
        raise


@app.get("/api/projects/{project_id}/entities/{entity_name}/rows")
def entity_rows(
    project_id: str,
    entity_name: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: str | None = None,
) -> dict[str, Any]:
    try:
        return list_rows(project_id, entity_name, limit, offset, search)
    except Exception as exc:
        _raise_store_error(exc)
        raise


@app.get("/api/projects/{project_id}/entities/{entity_name}/rows/{row_id}")
def entity_row(project_id: str, entity_name: str, row_id: int) -> dict[str, Any]:
    try:
        return get_row(project_id, entity_name, row_id)
    except Exception as exc:
        _raise_store_error(exc)
        raise


@app.post("/api/projects/{project_id}/entities/{entity_name}/rows", status_code=201)
def add_entity_row(project_id: str, entity_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return create_row(project_id, entity_name, payload)
    except Exception as exc:
        _raise_store_error(exc)
        raise


@app.patch("/api/projects/{project_id}/entities/{entity_name}/rows/{row_id}")
def edit_entity_row(
    project_id: str,
    entity_name: str,
    row_id: int,
    payload: dict[str, Any],
) -> dict[str, Any]:
    try:
        return update_row(project_id, entity_name, row_id, payload)
    except Exception as exc:
        _raise_store_error(exc)
        raise


@app.delete("/api/projects/{project_id}/entities/{entity_name}/rows/{row_id}", status_code=204)
def remove_entity_row(project_id: str, entity_name: str, row_id: int) -> None:
    try:
        delete_row(project_id, entity_name, row_id)
    except Exception as exc:
        _raise_store_error(exc)
        raise
