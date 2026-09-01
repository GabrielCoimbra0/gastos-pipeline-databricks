# Pipeline de Gastos Pessoais, Arquitetura Medalhão (Bronze/Silver/Gold)

Pipeline de dados end-to-end construído no **Databricks Free Edition**, usando **PySpark** e **Delta Lake**, aplicado a um problema real: entender meus próprios gastos a partir do extrato do cartão.

O objetivo não foi só processar dados, foi praticar decisões de engenharia de dados que se aplicam em qualquer contexto de negócio: schema explícito, arquitetura em camadas, tratamento de dado sujo, e escolhas de modelagem justificadas.

> **Nota sobre os dados:** o CSV incluso (`data/exemplo_fake.csv`) é **fictício**, gerado com a mesma estrutura e os mesmos padrões do extrato real usado no desenvolvimento (formato de data, campos com IOF, valores em vírgula decimal). Nenhum dado financeiro real está neste repositório.

## Arquitetura

```
CSV (extrato) → Bronze → Silver → Gold
```

| Camada | O que acontece | Tabela |
|---|---|---|
| **Bronze** | Ingestão do CSV bruto, com schema explícito (`StructType`), sem nenhuma transformação | `gastos_prj.bronze.transacoes` |
| **Silver** | Limpeza de texto (aspas, ponto de milhar), conversão de tipos, classificação de negócio | `gastos_prj.silver.transacoes` |
| **Gold** | Agregações prontas para consumo/análise | `gastos_prj.gold.resumo_por_tipo` |

Organização no Unity Catalog: um catalog (`gastos_prj`) com um schema por camada (`bronze`, `silver`, `gold`), cada um contendo as tabelas Delta daquela etapa.

## Decisões de design

**Por que schema explícito em vez de `inferSchema`?**
O campo de valor vem como texto formatado (`"84,80"`, com vírgula decimal e aspas). Deixar o Spark inferir o tipo automaticamente arrisca interpretar a coluna errado. Definir o schema manualmente também evita que o Spark precise escanear o arquivo inteiro só para adivinhar tipos.

**Por que manter tudo como `String` na Bronze, mesmo sabendo que um campo é numérico?**
A regra da camada Bronze é fidelidade total ao dado original — nenhuma interpretação. A conversão de tipo é uma transformação, e transformação é responsabilidade da Silver.

**Por que classificar `tipo_transacao` em `compra`, `imposto` e `estorno_imposto`, em vez de simplesmente somar tudo?**
Compras internacionais no extrato geram uma cobrança de IOF separada — e, na maioria dos casos, um estorno posterior desse mesmo IOF. Em vez de descartar essas linhas ou somá-las cegamente ao gasto, optei por **preservar a granularidade**: cada tipo fica marcado, e a decisão de incluir ou excluir o IOF de uma métrica específica é feita na camada Gold, não na Silver. Isso evita perder informação de negócio (no caso, o insight de que quase 100% do IOF cobrado costuma ser devolvido).

## Desafios e aprendizados

**Bug: classificação de IOF falhando silenciosamente.**
Ao aplicar a regra `descricao.startswith("IOF de")`, transações claramente com "IOF de..." no texto continuavam caindo na categoria padrão (`compra`). Investigando com `repr()` em vez de `display()` (que formata e esconde caracteres), foi possível identificar que o campo `descricao` vinha com aspas duplas residuais do escaping do CSV (ex: `"IOF de ""Uber *Trip..."""`), então a string começava com `"` em vez de `I`, quebrando o `startswith`. Corrigido com `regexp_replace` para remover as aspas externas e desfazer o escaping (`""` → `"`) antes da classificação.

**Ordem importa em condições encadeadas (`when`/`otherwise`).**
O padrão "IOF de volta de..." (estorno) também começa com "IOF de", então precisou ser verificado *antes* da regra mais genérica — senão a condição genérica capturava o caso específico primeiro e o estorno nunca era alcançado.

**Formatação numérica brasileira.**
Valores acima de mil vêm com ponto como separador de milhar e vírgula como decimal (ex: `9.041,15`). A limpeza precisou remover o ponto de milhar *antes* de trocar a vírgula por ponto decimal — na ordem inversa, o resultado ficava malformado (dois pontos).

## Stack

- Databricks Free Edition (compute serverless)
- PySpark
- Delta Lake / Unity Catalog
- Arquitetura medalhão (Bronze/Silver/Gold)

## Estrutura do repositório

```
.
├── notebooks/
│   ├── 01_ingestao_bronze.py
│   ├── 02_transformacao_silver.py
│   └── 03_agregacao_gold.py
├── data/
│   └── exemplo_fake.csv
└── README.md
```
