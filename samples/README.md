# Planilhas de teste

Use esta pasta para exemplos não sensíveis.

Um workbook simples para validar o MVP pode conter:

## Aba Clientes

| ID | Nome | CNPJ | Status |
|---|---|---|---|
| 1 | Empresa A | 00.000.000/0001-00 | Ativo |
| 2 | Empresa B | 11.111.111/0001-11 | Ativo |

## Aba Pedidos

| ID | clientes_id | Produto | Valor | Status |
|---|---|---|---:|---|
| 101 | 1 | Link IP | 1200 | Novo |
| 102 | 2 | SD-WAN | 2500 | Em análise |

O campo `clientes_id` deve produzir uma relação inicial com a entidade `clientes`.
