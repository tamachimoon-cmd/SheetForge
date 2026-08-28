# Especificação de análise de planilhas

## Entrada suportada no MVP 0.1

- `.xlsx`
- `.csv`

## Etapas

1. Identificar workbook e abas.
2. Remover linhas vazias anteriores ao primeiro cabeçalho útil.
3. Considerar a primeira linha útil como cabeçalho no MVP.
4. Normalizar nomes para identificadores seguros.
5. Amostrar até 100 linhas para inferência.
6. Inferir tipos: string, integer, number, boolean e datetime.
7. Avaliar unicidade e padrão do nome para sugerir chave primária.
8. Contar fórmulas em XLSX sem executá-las.
9. Detectar relações simples quando um campo termina em `_id` e corresponde a outra entidade.
10. Entregar o resultado ao Schema Builder.

## Limitações deliberadas

O MVP não promete interpretar corretamente planilhas com múltiplas tabelas na mesma aba, cabeçalhos multinível, VBA, Power Query, Power Pivot ou fórmulas de negócio complexas. Esses recursos entram depois que a fundação estiver estável.
