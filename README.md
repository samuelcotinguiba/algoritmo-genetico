# Algoritmo Genético para o Problema da Mochila 0/1

Este repositório contém uma implementação simples e eficiente de um Algoritmo Genético (AG) para resolver o Problema da Mochila 0/1 com entrada via JSON, interface em português, modo interativo e linha de comando, histórico por geração e critério de parada por estabilidade.

## Recursos

- Entrada a partir de arquivos JSON (com cache em memória)
- Interface interativa (com seletor nativo de arquivos quando disponível)
- Modo não interativo/CLI com parâmetros
- Critério de parada por estabilidade (melhor valor repetido por N gerações)
- Operador de reparo (garante que a capacidade nunca é excedida)
- Histórico por geração (valor, fitness, média, mutações, crossovers, peso, tempo)
- Suporte a nomes de itens (opcional) e diretório anterior persistido
- Zero dependências externas obrigatórias (usa apenas a stdlib; tkinter é opcional)

## Formato do JSON

```json
{
  "capacity": 150,               // opcional (pode ser informado via CLI ou solicitado interativamente)
  "items": [
    { "name": "Item_1", "weight": 12, "value": 45 },
    { "name": "Item_2", "weight": 7,  "value": 22 }
  ]
}
```

O campo `name` é opcional e serve apenas para exibição. Se ausente, será usado um rótulo padrão.

## Como executar

- Interativo (recomendado):
  - Rode `python3 main.py` e escolha o arquivo JSON pelo seletor. O algoritmo será executado automaticamente.
  - Após a execução, você pode optar por exibir o histórico por geração.

- Linha de comando (não interativo):
  - `python3 main.py --input test_instance.json --auto --show s --capacity 150`
    - `--auto` seleciona parâmetros automaticamente
    - `--show s` ativa a exibição do histórico
    - `--capacity` sobrescreve ou define a capacidade quando o JSON não possui o campo

### Parâmetros principais (CLI)

- `--input`: caminho do JSON (obrigatório no modo CLI)
- `--auto`: escolhe parâmetros do AG automaticamente
- `--show {s|n}`: exibe histórico por geração
- `--pop-size`, `--generations`, `--mutation-rate`: configuram o AG manualmente
- `--max-time`: tempo máximo de execução em segundos (padrão: 5)
- `--capacity`: capacidade a ser usada se o JSON não tiver `capacity`

## Estrutura do projeto

```
algorithms/ga.py        # Implementação do AG
problem/problem.py      # Definição do problema da mochila e avaliação
json_utils.py           # Leitura de JSON, cache, seletores e utilitários
main.py                 # Lançador interativo/CLI e impressão de resultados
README.md               # Este arquivo
```

## Notas

- O operador de reparo remove itens pela pior razão valor/peso até que o peso caiba na capacidade. Soluções inviáveis recebem fitness muito negativo para nunca serem selecionadas.
- O critério de estabilidade interrompe quando o melhor valor permanece o mesmo por 15 gerações consecutivas (padrão no `main.py`).

## Licença

Defina aqui a licença desejada (por exemplo, MIT, Apache-2.0, etc.).
