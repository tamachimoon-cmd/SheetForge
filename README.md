# SheetForge

> From spreadsheet to software.

SheetForge transforma planilhas Excel e CSV em aplicações web. A proposta não é apenas renderizar células em uma tela: o projeto interpreta a estrutura do arquivo, infere entidades, campos e relações, produz um schema intermediário e usa esse modelo para criar persistência, API e interface utilizável.

## Fluxo

```text
Excel / CSV
    ↓
Workbook Analyzer
    ↓
SheetForge App Schema
    ↓
Data Importer
    ↓
SQLite Project Runtime
    ↓
Dynamic CRUD API
    ↓
React Workspace
```

## MVP 0.2

Implementado atualmente:

- Upload de `.xlsx` e `.csv`
- Leitura de múltiplas abas
- Normalização segura de nomes de abas e colunas
- Inferência de tipos de dados
- Identificação de possíveis chaves primárias
- Detecção inicial de relações entre abas
- Contagem de fórmulas como metadados
- Geração do SheetForge App Schema `0.2`
- Criação de um `project_id` para cada importação
- Banco SQLite isolado por projeto
- Importação real dos registros da planilha
- Chave interna `__sf_rowid`, independente da qualidade dos IDs existentes no Excel
- API CRUD dinâmica por entidade
- Busca textual nos registros
- Workspace React com módulos gerados a partir das abas
- Tabela de registros por entidade
- Criação, edição e exclusão de registros
- Formulários gerados a partir do schema
- CI com testes Python e build do frontend em cada commit na `main`

## Estrutura

```text
SheetForge/
├── backend/
│   └── app/
│       ├── analyzer.py        # Inspeção estrutural
│       ├── naming.py          # Identificadores seguros
│       ├── schema_builder.py  # SheetForge App Schema
│       ├── source_reader.py   # Leitura dos registros de origem
│       ├── project_store.py   # Runtime SQLite e CRUD
│       └── main.py            # API FastAPI
├── frontend/
│   └── src/
│       ├── api.js
│       ├── components/
│       └── App.jsx
├── app-schema/
├── docs/
├── samples/
├── tests/
└── .github/workflows/ci.yml
```

## Documentação

- [`docs/functional-architecture.md`](docs/functional-architecture.md) — especificação detalhada de como o SheetForge deve analisar o conteúdo do Excel e transformá-lo em uma aplicação utilizável.
- [`docs/architecture.md`](docs/architecture.md) — arquitetura técnica inicial.
- [`docs/vision.md`](docs/vision.md) — visão de produto.
- [`docs/roadmap.md`](docs/roadmap.md) — evolução planejada.

A arquitetura funcional define os motores de Workbook Inspection, análise semântica, relacionamentos, regras, workflows, migração, geração de interface e os modos `IMPORT`, `SYNC` e `MIGRATE`.

## Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Swagger: `http://localhost:8000/docs`

### Endpoints principais

```text
POST   /api/analyze
POST   /api/projects/import
GET    /api/projects
GET    /api/projects/{project_id}
GET    /api/projects/{project_id}/entities/{entity}/rows
GET    /api/projects/{project_id}/entities/{entity}/rows/{row_id}
POST   /api/projects/{project_id}/entities/{entity}/rows
PATCH  /api/projects/{project_id}/entities/{entity}/rows/{row_id}
DELETE /api/projects/{project_id}/entities/{entity}/rows/{row_id}
```

Os bancos são criados em `backend/data` por padrão. O diretório pode ser alterado usando `SHEETFORGE_DATA_DIR`.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Por padrão o frontend usa `http://localhost:8000`. Use `VITE_API_URL` para apontar para outro backend.

## Princípio arquitetural

O SheetForge não gera uma aplicação diretamente do Excel. Primeiro produz um **SheetForge App Schema**. Esse contrato intermediário desacopla a origem dos dados da aplicação gerada e abre caminho para Google Sheets, Access, SQL e outras fontes no futuro.

O núcleo deve continuar funcional sem depender de IA. IA entra como camada de melhoria semântica, resolução de ambiguidades, interpretação de workflows e UX. O caminho determinístico continua sendo:

```text
Excel → estrutura → schema → dados → runtime → aplicação
```

## Status

**MVP 0.2 — persistência e CRUD funcional implementados.**

Próximo marco: **MVP 0.3 — inteligência estrutural**, com classificação do papel das abas, tipos semânticos como CNPJ/moeda/e-mail, relacionamentos mais robustos, enums, tradução de fórmulas para regras e detecção inicial de workflows.

## Licença

A definir antes da primeira release pública estável.
