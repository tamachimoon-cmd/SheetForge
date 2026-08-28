from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .analyzer import analyze_file
from .schema_builder import build_app_schema

app = FastAPI(
    title="SheetForge API",
    version="0.1.0",
    description="Transforme planilhas em um schema de aplicação.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "sheetforge-api"}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)) -> dict:
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
