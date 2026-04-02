# Formato de exportação CSV do Logos

Este documento registra a estrutura observada em exportações reais do Logos 7 e Logos 10.
Ele existe para evitar duas coisas ruins:
1. parser baseado em memória informal;
2. manutenção futura feita por adivinhação.

## Objetivo operacional

O parser `logos_csv` deve aceitar ambos os formatos observados e produzir registros canônicos compatíveis com o pipeline atual de importação.

## Arquivos observados

- `Biblioteca-Logos-10(20260401).csv`
- `Biblioteca-Logos-7(20260401).csv`

## Colunas comuns confirmadas

As colunas abaixo aparecem nos dois formatos analisados e são suficientes para a primeira camada do parser:

| Coluna CSV | Uso no parser | Observação |
|---|---|---|
| `Resource ID` | `source_key` | identidade primária do item dentro do Logos |
| `Title` | `title` | título preferencial |
| `Logos Title` | fallback de `title` | usado se `Title` vier vazio |
| `Resource Type` | `resource_type` + derivação de `item_type` | valor semântico nativo do Logos |
| `Authors` | `author` | texto livre; autores múltiplos vêm em um único campo |
| `Series` | `series` | pode vir vazio |
| `Languages` | `language` preferencial | idioma do recurso |
| `Metadata Language` | fallback de `language` | idioma dos metadados |
| `Publication Date` | candidato para `year` | pode conter ano simples ou faixa |
| `Electronic Publication Date` | fallback para `year` | usado quando `Publication Date` não ajuda |
| `File Name` | `path_or_location` | não é caminho absoluto; é apenas nome lógico do arquivo |

## Diferença estrutural relevante

### Logos 10

O formato observado no Logos 10 inclui a coluna:

- `Publishers`

Mapeamento atual:
- `Publishers` -> `publisher`

### Logos 7

O formato observado no Logos 7 **não** inclui `Publishers`.

Consequência:
- `publisher` deve ser aceito como `None` sem falha de validação.

## Colunas observadas no Logos 10

- `Resource ID`
- `Metadata Version`
- `Metadata Language`
- `Title`
- `Logos Title`
- `Abbreviated Title`
- `Logos Abbreviated Title`
- `Resource Type`
- `Edition`
- `Authors`
- `My Tags`
- `Community Tags`
- `My Rating`
- `Community Rating`
- `Publishers`
- `Publication Date`
- `Electronic Publication Date`
- `Series`
- `Subjects`
- `Languages`
- `File Name`
- `File Version`
- `Last Updated`
- `License`

## Colunas observadas no Logos 7

- `Resource ID`
- `Metadata Version`
- `Metadata Language`
- `Title`
- `Logos Title`
- `Abbreviated Title`
- `Logos Abbreviated Title`
- `Resource Type`
- `Edition`
- `Authors`
- `My Tags`
- `Community Tags`
- `My Rating`
- `Community Rating`
- `Publication Date`
- `Electronic Publication Date`
- `Series`
- `Subjects`
- `Languages`
- `File Name`
- `File Version`
- `Last Updated`
- `License`

## Decisões de mapeamento da primeira camada

| Campo canônico | Origem | Regra |
|---|---|---|
| `source_key` | `Resource ID` | obrigatório |
| `title` | `Title` | fallback para `Logos Title` |
| `author` | `Authors` | sem split nesta primeira camada |
| `series` | `Series` | opcional |
| `publisher` | `Publishers` | opcional; ausente no Logos 7 |
| `year` | `Publication Date`, `Electronic Publication Date` | extrair primeiro ano válido |
| `language` | `Languages`, `Metadata Language` | preferir idioma do recurso |
| `resource_type` | `Resource Type` | preservar valor original |
| `item_type` | derivado de `Resource Type` | taxonomia interna reduzida |
| `path_or_location` | `File Name` | manter nome lógico exportado |

## Mapeamento inicial de `Resource Type` para `item_type`

| `Resource Type` | `item_type` |
|---|---|
| `Monografia` | `book` |
| `Comentário` | `commentary` |
| `Comentário bíblico` | `commentary` |
| `Bíblia` | `bible` |
| `Léxico` | `lexicon` |
| `Enciclopédia` | `dictionary` |
| `Revista` | `journal` |
| `Diário` | `journal` |
| `Sermões` | `sermon` |
| `Estudo Bíblico` | `study_guide` |
| `Devocional agendado` | `devotional` |
| qualquer outro valor | `other` |

## Fragilidades já conhecidas

1. `Authors` ainda é texto bruto. Não há normalização de múltiplos autores nesta camada.
2. `Publication Date` pode carregar faixa de anos. O parser atual extrai apenas o primeiro ano válido.
3. `File Name` não prova localização física do recurso. Serve como pista, não como caminho resolvido.
4. `Resource Type` do Logos é mais rico que a taxonomia interna atual; parte da semântica ainda é comprimida em `other`.
5. Este documento descreve apenas o que foi observado nos dois arquivos reais analisados, não todos os formatos possíveis que o Logos pode exportar.

## Critério para evoluir este parser

Só vale sofisticar o parser quando aparecer uma necessidade real, por exemplo:
- dividir autores com confiabilidade aceitável;
- capturar editora de outro campo em exports antigos;
- suportar nova variante estrutural do CSV;
- enriquecer `item_type` com taxonomia mais precisa.

Até lá, a regra correta é: parser simples, previsível e documentado.
