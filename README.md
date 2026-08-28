# SheetForge

> From spreadsheet to software.

SheetForge transforma planilhas Excel e CSV em aplicações web. A proposta não é apenas renderizar células em uma tela: o projeto interpreta a estrutura do arquivo, infere entidades, campos, relações e regras básicas, gera um schema intermediário e usa esse modelo como base para construir aplicações.

## Fluxo

```text
Excel / CSV
    ↓
Workbook Analyzer
    ↓
SheetForge App Schema
    ↓
Rules + Relationships
    ↓
App Generator
    ↓
Frontend + API + Database
```

## MVP 0.1

- Upload de `.xlsx` e `.csv`
- Leitura de múltiplas abas
- Inferência de tipos de dados
- Identificação de possíveis chaves primárias
- Detecção inicial de relações entre abas
- Contagem de fórmulas como metadados
- Geração do SheetForge App Schema
- API FastAPI
- Interface React/Vite para upload e inspeção
- Arquitetura preparada para SQLite/PostgreSQL e CRUD dinâmico

## Estrutura

```text
SheetForge/
├── backend/            # API e motor de análise
├── frontend/           # Interface React
├── app-schema/         # Exemplo do modelo intermediário
├── docs/               # Visão, arquitetura e roadmap
├── samples/            # Orientações para planilhas de teste
└── tests/              # Testes do backend
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

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Por padrão o frontend usa `http://localhost:8000`.

## Endpoint principal

`POST /api/analyze`

Recebe um arquivo Excel ou CSV e devolve informações do workbook, entidades detectadas, campos e tipos inferidos, possíveis chaves primárias, relações e o schema intermediário.

## Princípio arquitetural

O SheetForge não gera uma aplicação diretamente do Excel. Primeiro produz um **SheetForge App Schema**. Esse contrato intermediário desacopla a origem dos dados da aplicação gerada e abre caminho para Google Sheets, Access, SQL e outras fontes no futuro.

O núcleo deve continuar funcional sem depender de IA. IA entra como camada de melhoria semântica, resolução de ambiguidades, interpretação de workflows e UX. O caminho determinístico continua sendo `Excel → estrutura → schema → aplicação`.

## Status

**MVP 0.1 — fundação funcional.**

Próximo marco: **MVP 0.2**, com persistência SQLite, importação real dos registros, relatório de validação, CRUD dinâmico, formulários automáticos e relacionamentos entre entidades.

## Licença

A definir antes da primeira release pública estável.
