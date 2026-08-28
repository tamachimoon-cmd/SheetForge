# SheetForge — Arquitetura Funcional

## Objetivo

O SheetForge deve funcionar como um **compilador de planilhas para aplicações**, e não como um simples conversor de Excel para telas. O sistema primeiro compreende a estrutura, o significado, as relações e as regras existentes no workbook. Depois transforma esse entendimento em um modelo intermediário, o **SheetForge App Schema**, que serve como fonte da verdade para gerar banco, API, interface, workflows e dashboards.

> O SheetForge não converte células em telas. Ele reconstrói o sistema que estava escondido dentro da planilha.

## Fluxo macro

```text
Excel / CSV / XLSM
        ↓
Workbook Inspector
        ↓
Structure Analyzer
        ↓
Semantic Engine
        ↓
Relationship Engine
        ↓
Rules Engine
        ↓
Workflow Engine
        ↓
UI Inference
        ↓
SheetForge App Schema
        ↓
Migration Engine
        ↓
App Generator
        ↓
Database + API + Frontend
        ↓
Aplicação funcional
```

## 1. Workbook Inspector

Responsável por ler o workbook completo e construir um inventário técnico da planilha.

Deve identificar:

- nome e quantidade de abas;
- abas visíveis, ocultas e muito ocultas;
- intervalo utilizado por aba;
- cabeçalhos;
- tabelas estruturadas;
- tipos de célula;
- fórmulas;
- validações de dados;
- listas suspensas;
- células protegidas;
- referências entre abas;
- hyperlinks;
- named ranges;
- tabelas dinâmicas;
- gráficos;
- formatação condicional;
- campos vazios;
- duplicidades;
- possíveis identificadores;
- macros em arquivos `.xlsm`;
- conexões e Power Query quando tecnicamente possível.

O resultado desta etapa deve ser determinístico e não depender de IA.

## 2. Classificação das abas

Cada aba deve receber um papel funcional provável:

- `DATA`
- `MASTER_DATA`
- `TRANSACTION`
- `LOOKUP`
- `CONFIG`
- `REPORT`
- `DASHBOARD`
- `WORKFLOW`
- `HISTORY`
- `UNKNOWN`

Exemplo:

```json
{
  "sheet": "Clientes",
  "role": "MASTER_DATA",
  "confidence": 0.96
}
```

Nem toda aba deve virar uma tela no aplicativo. Abas de parâmetros, apoio, configuração e cálculo podem virar estruturas internas do sistema.

## 3. Entity Detection

O sistema deve identificar quais abas representam objetos de negócio.

Exemplo:

```text
ABA: CLIENTES
ID_CLIENTE
NOME
CNPJ
REGIONAL
STATUS
```

Deve resultar em uma entidade semelhante a:

```json
{
  "entity": "Cliente",
  "source": "Clientes",
  "primaryKey": "ID_CLIENTE"
}
```

## 4. Inferência de tipos

O SheetForge deve inferir o tipo semântico, não apenas o tipo bruto da célula.

Tipos esperados:

- `string`
- `integer`
- `decimal`
- `currency`
- `boolean`
- `date`
- `datetime`
- `email`
- `phone`
- `cpf`
- `cnpj`
- `cep`
- `url`
- `enum`
- `relation`
- `percentage`
- `text`

Campos como CNPJ, telefone e CEP devem permanecer strings, mesmo quando o Excel os armazena como números.

## 5. Primary Key Detection

O sistema deve procurar colunas candidatas como:

- `ID`
- `CODIGO`
- `ID_CLIENTE`
- `COD_PEDIDO`
- `PROTOCOLO`
- `NUM_OS`

A confiança deve considerar:

- unicidade;
- preenchimento;
- repetição;
- padrão do nome;
- sequencialidade;
- tipo do dado.

Quando nenhuma chave confiável existir, o sistema pode gerar `sheetforge_id`.

## 6. Relationship Engine

Deve detectar relações entre entidades comparando nomes, valores e padrões.

Exemplo:

```text
Clientes.ID_CLIENTE
Pedidos.ID_CLIENTE
```

Deve resultar em:

```json
{
  "from": "Pedido.ID_CLIENTE",
  "to": "Cliente.ID_CLIENTE",
  "type": "many-to-one"
}
```

No app, a relação deve ser apresentada por significado, por exemplo um seletor de cliente, e não por um ID numérico cru.

## 7. Semantic Engine

A IA entra depois da análise estrutural, recebendo uma representação reduzida e estruturada do workbook.

Responsabilidades da camada semântica:

- interpretar nomes ambíguos;
- reconhecer entidades de negócio;
- sugerir nomes amigáveis;
- identificar possíveis workflows;
- interpretar o propósito de abas;
- sugerir UX;
- auxiliar na interpretação de regras complexas.

A IA não deve ser o parser primário do Excel.

## 8. Rules Engine

Fórmulas devem ser traduzidas em regras de negócio portáveis.

Fluxo recomendado:

```text
Excel Formula
      ↓
Formula Parser
      ↓
AST
      ↓
Business Rule
      ↓
JavaScript / Python / SQL
```

Exemplo conceitual:

```text
SE diasDesde(dataEntrada) > 10
ENTÃO status = ATRASADO
SENÃO status = NORMAL
```

Deve virar uma regra declarativa no schema em vez de código acoplado diretamente ao frontend.

Regras não suportadas devem ser explicitamente marcadas para revisão. O sistema nunca deve fingir que converteu uma regra que não compreendeu.

## 9. Enum Detection

Colunas com valores recorrentes ou validações devem poder virar `enum`.

Exemplo:

```json
{
  "field": "status",
  "type": "enum",
  "options": ["Novo", "Análise", "Aprovado", "Concluído"]
}
```

Na interface isso deve virar um componente apropriado, como Select, filtro ou badge.

## 10. Workflow Engine

Sequências de status podem representar processos.

Exemplo:

```text
Aberto → Análise → Viabilidade → Configuração → Concluído
```

Quando houver evidência suficiente, o SheetForge pode propor um workflow e gerar visualizações como:

- Kanban;
- fila operacional;
- pipeline;
- SLA por etapa;
- histórico de transições.

Inferências de workflow devem possuir nível de confiança e permitir revisão humana.

## 11. Historical Analysis

Quando a base possuir campos como data de abertura, data de conclusão, responsável e status, o sistema pode inferir métricas como:

- SLA;
- aging;
- backlog;
- entrantes;
- concluídos;
- produtividade;
- tempo médio;
- volume por responsável;
- volume por regional.

## 12. Graph and Dashboard Interpretation

Gráficos existentes podem ser convertidos em definições declarativas.

Exemplo:

```json
{
  "type": "bar",
  "title": "Pedidos por Regional",
  "dimension": "regional",
  "metric": "count"
}
```

O gerador web poderá recriar o conceito visual sem depender do gráfico original do Excel.

## 13. Conditional Formatting

Formatação condicional pode conter semântica útil, por exemplo:

- vermelho = atraso;
- amarelo = atenção;
- verde = concluído.

Quando a regra de formatação for objetiva, ela pode ser convertida para estilos de status no app. Cores aplicadas manualmente devem ser tratadas apenas como indício, nunca como regra de negócio confiável.

## 14. SheetForge App Schema

O App Schema é a fonte da verdade entre a análise e a aplicação gerada.

Estrutura conceitual:

```json
{
  "app": {
    "name": "Controle Comercial",
    "version": "1.0"
  },
  "entities": {},
  "relationships": [],
  "rules": [],
  "workflows": [],
  "pages": [],
  "dashboards": [],
  "permissions": []
}
```

O código gerado deve nascer do schema. Alterações feitas pelo assistente também devem modificar primeiro o schema e depois regenerar a aplicação.

Fluxo correto:

```text
Usuário
  ↓
IA / Editor
  ↓
SheetForge App Schema
  ↓
Generator
  ↓
Aplicação
```

Evitar edição arbitrária e direta do código React pelo agente sempre que a mudança puder ser representada no schema.

## 15. Migration Engine

Após compreender a estrutura, o SheetForge deve importar os dados para banco.

Fluxo:

```text
Excel
  ↓
Data Cleaner
  ↓
Validator
  ↓
Database
```

O relatório de importação deve mostrar:

- linhas lidas;
- linhas importadas;
- linhas rejeitadas;
- erros por linha;
- IDs duplicados;
- campos obrigatórios ausentes;
- inconsistências de tipo.

O sistema não deve descartar silenciosamente registros inválidos.

## 16. Database Layer

MVP:

- SQLite.

Evolução:

- PostgreSQL;
- SQL Server;
- MySQL;
- outros conectores posteriormente.

Cada entidade válida tende a virar uma tabela, preservando relações e restrições inferidas.

## 17. App Generator

O gerador deve transformar o App Schema em:

- banco de dados;
- migrations;
- API;
- rotas;
- CRUD;
- filtros;
- busca;
- ordenação;
- formulários;
- dashboards;
- workflows;
- permissões;
- exportação;
- histórico e auditoria quando aplicável.

## 18. UI Inference

O tipo do campo deve orientar o componente:

```text
date       → DatePicker
boolean    → Switch
enum       → Select
text       → TextArea
currency   → CurrencyInput
relation   → SearchSelect
email      → EmailInput
```

Entidades devem gerar páginas de listagem, criação, edição, detalhe, busca e filtros conforme o caso.

## 19. Dashboard Generator

O sistema pode sugerir indicadores a partir de campos como:

- status;
- data;
- valor;
- regional;
- responsável;
- categoria.

A geração deve ser baseada em evidência dos dados e não em gráficos aleatórios apenas para preencher tela.

## 20. Review Stage

Antes da geração definitiva, o SheetForge deve apresentar uma etapa de revisão.

Exemplo:

```text
Entidades: 7
Relacionamentos: 12
Regras: 31
Fluxos: 2
Dashboards: 3
```

Cada inferência deve poder receber uma confiança:

```text
Clientes       99%
Pedidos        98%
Produtos       97%
Parâmetros     88%
Pendências     84%
```

O usuário pode corrigir o modelo antes da geração.

## 21. Ambiguity Resolution

Nomes ambíguos devem ser explicitamente sinalizados.

Exemplo: `COD` pode significar código de cliente, produto, pedido ou chave interna.

O sistema deve pedir revisão ou permitir mapeamento manual quando a confiança estiver abaixo do limite configurado.

## 22. SheetForge Assistant

Após a geração, o usuário pode solicitar mudanças em linguagem natural.

Exemplos:

- criar uma tela apenas com pedidos atrasados;
- mover Regional antes de Responsável;
- adicionar filtro por carteira;
- criar um dashboard de SLA;
- transformar Pendências em Kanban.

O assistente deve alterar o App Schema e acionar a regeneração correspondente.

## 23. Modos de funcionamento

### IMPORT

```text
Excel → App
```

Cria uma aplicação a partir de uma planilha fornecida.

### SYNC

```text
Excel ⇄ App
```

Mantém a planilha como uma origem temporariamente sincronizada. Alterações estruturais devem passar por comparação de schema antes de serem aplicadas.

### MIGRATE

```text
Excel → Database → App
```

Move definitivamente o processo para banco e aplicação, tornando o Excel apenas uma origem histórica/importação.

## 24. Diff de versões

No modo Sync, o sistema deve comparar versões do workbook.

Exemplo:

```text
+ coluna PRIORIDADE
- coluna LEGADO
~ STATUS alterado
```

O usuário deve ver o impacto antes de aplicar uma migração estrutural.

## 25. Princípio arquitetural obrigatório

O núcleo deve funcionar sem IA.

Camadas determinísticas:

```text
Excel → estrutura → schema → aplicação
```

A IA deve melhorar:

- semântica;
- nomenclatura;
- inferências;
- UX;
- workflows;
- interpretação de regras complexas.

Isso permite operação local, offline ou em ambientes corporativos fechados.

## 26. Núcleos de código

A evolução do projeto deve convergir para cinco motores principais:

```text
workbook-engine/
semantic-engine/
schema-engine/
migration-engine/
app-generator/
```

Responsabilidades:

### `workbook-engine`
Leitura, parsing, estrutura, fórmulas, metadados e inspeção de Excel/CSV.

### `semantic-engine`
Interpretação semântica, confiança, classificação e resolução de ambiguidades.

### `schema-engine`
Construção, validação, versionamento e diff do SheetForge App Schema.

### `migration-engine`
Limpeza, validação, conversão e migração de dados para banco.

### `app-generator`
Geração de database layer, API, frontend, formulários, CRUD, workflows e dashboards.

## 27. Prioridades de implementação

### MVP 0.2

1. Persistência SQLite.
2. Importação real dos registros do workbook.
3. Relatório de validação de importação.
4. CRUD dinâmico baseado no App Schema.
5. Renderização automática de formulários por tipo.
6. Relacionamentos entre entidades no CRUD.

### MVP 0.3

1. Classificação de abas.
2. Enum Detection.
3. Editor visual do App Schema.
4. Confidence Score.
5. Ambiguity Resolution.
6. Dashboard básico inferido.

### MVP 0.4

1. Formula Parser.
2. AST de regras.
3. Rules Engine.
4. Workflow Detection.
5. Kanban/Pipeline generator.
6. Interpretação de formatação condicional.

### MVP 0.5

1. SheetForge Assistant.
2. Alterações em linguagem natural via schema.
3. Sync Mode.
4. Schema Diff.
5. PostgreSQL.
6. Exportação da aplicação gerada.

## Critério de sucesso

O SheetForge só deve considerar uma transformação concluída quando o usuário conseguir sair de uma planilha operacional e obter uma aplicação utilizável com dados importados, formulários, pesquisa, filtros, relações, regras e fluxo de trabalho suficientes para executar o processo sem depender do workbook original no modo MIGRATE.
