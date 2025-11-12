# Monografia Técnica: Algoritmo Genético para o Problema da Mochila 0/1

## 1. Introdução
Este trabalho apresenta a implementação de um sistema compacto para resolver a variante clássica do Problema da Mochila 0/1 utilizando um Algoritmo Genético (AG). O objetivo é selecionar um subconjunto de itens, cada qual com peso e valor, de modo que a soma dos pesos não ultrapasse a capacidade máxima e o valor total seja maximizado. O sistema oferece execução interativa e modo de linha de comando, leitura de arquivos JSON como instâncias do problema, histórico por geração e critério de parada baseado em estagnação do melhor indivíduo.

## 2. Fundamentação Teórica

### 2.1 Problema da Mochila 0/1
Formalmente, dado um conjunto de n itens onde cada item i possui peso w_i e valor v_i, e uma capacidade máxima W, busca-se um vetor binário x ∈ {0,1}^n que maximize Σ v_i x_i sujeito a Σ w_i x_i ≤ W. A formulação é NP-difícil e serve como caso de estudo para heurísticas evolucionárias.

### 2.2 Algoritmos Genéticos
Algoritmos Genéticos (AGs) são meta-heurísticas inspiradas na evolução natural. Operam sobre:
- Representação: indivíduos como vetores binários (genes 0/1 indicando inclusão do item).
- População: conjunto de candidatos mantidos a cada geração.
- Fitness: função de avaliação da qualidade (aqui, valor total se factível; grande penalidade caso exceda a capacidade).
- Seleção: escolha de indivíduos para reprodução (torneio).
- Crossover: recombinação genética (um ponto).
- Mutação: perturbação aleatória (bit-flip com probabilidade por gene).
- Elitismo: preservação do melhor indivíduo entre gerações.
- Critério de Parada: máximo de gerações ou estabilidade (melhor valor não melhora por k gerações consecutivas).

### 2.3 Penalização versus Reparo
Abordagens comuns incluem penalizações suaves (reduzindo fitness proporcional à violação) ou reparo. Optou-se por:
- Fitness inviável = -1e9 (garantia de exclusão sistemática de soluções excedentes).
- Operador de reparo imediato: remove itens de pior razão valor/peso até tornar a solução factível. Isso reduz o espaço de busca efetivo e evita que indivíduos sobrecarregados contaminem a seleção.

### 2.4 Critério de Estagnação
Utiliza-se um critério adaptativo: se o melhor valor não muda por `stable_limit` gerações consecutivas, o AG é interrompido. Evita gasto computacional desnecessário após aparente convergência.

## 3. Arquitetura do Sistema

### 3.1 Organização de Módulos
- `problem/problem.py`: Define `Item` e `KnapsackProblem` com avaliação rígida.
- `algorithms/ga.py`: Implementa o AG completo (população, seleção, reprodução, mutação, reparo, histórico).
- `json_utils.py`: Entrada/saída de JSON, cache em memória, seleção interativa e integração com diálogo do sistema.
- `main.py`: Interface de execução (interativa e CLI), seleção de parâmetros automáticos, impressão de resultados e histórico.

### 3.2 Fluxo de Execução (Interativo)
1. Usuário inicia aplicação sem argumentos.
2. Sistema tenta abrir seletor nativo ou lista JSONs disponíveis.
3. Carrega instância (capacidade do JSON ou solicitada se ausente).
4. Usuário escolhe auto-parâmetros ou define manualmente.
5. AG executa com registro de histórico.
6. Pergunta se exibe histórico por geração.
7. Loop continua até usuário optar por encerrar.

### 3.3 Fluxo de Execução (Não Interativo)
1. Chamada com `--input arquivo.json`.
2. Uso opcional de `--auto` para parâmetros automáticos.
3. Flag `--show s` habilita histórico.
4. Execução e impressão direta dos resultados.

## 4. Detalhamento dos Componentes

### 4.1 Representação dos Dados
Cada indivíduo é uma lista de inteiros (0/1) com comprimento igual ao número de itens. O JSON tem o formato:

```json
{
  "capacity": 150,
  "items": [
    { "name": "Item_1", "weight": 12, "value": 45 },
    { "name": "Item_2", "weight": 7,  "value": 22 }
  ]
}
```

O campo `name` é opcional; se ausente, o sistema usa rótulos derivados (`Item_i`).

### 4.2 Avaliação
A função `evaluate(individual)` percorre apenas os bits ativos acumulando peso e valor. Caso o peso total ultrapasse a capacidade, retorna fitness extremamente negativo. Isto garante robustez e simplifica as pressões de seleção.

### 4.3 Seleção por Torneio
Para cada seleção, realiza-se um mini-concurso entre k indivíduos aleatórios (`tournament_size`), escolhendo o de maior fitness. É simples, eficiente e evita necessidade de ordenação completa.

### 4.4 Crossover e Mutação
- Crossover: ponto único (eficaz para mistura simples em problemas binários).
- Mutação: percorre genes e inverte bits com probabilidade `mutation_rate`. Contribui para manter diversidade populacional.

### 4.5 Reparo
Após criação de indivíduos (inicial e descendentes), aplica-se `_repair`: enquanto o peso for excedente, remove o item de menor razão valor/peso. A heurística prioriza preservação de itens “eficientes”.

### 4.6 Histórico
Se habilitado, por geração registra: `gen`, `best_fitness`, `avg_fitness`, `mutations`, `crossovers`, `best_value`, `best_weight`, `elapsed`.

### 4.7 Critério de Parada
Dois limites: geração máxima (`generations`) e estabilidade (`stable_limit`), interrompendo quando não há melhora de valor por k rodadas.

### 4.8 Seleção Automática de Parâmetros
Heurística:
- `pop_size ≈ 10 * n` limitado entre 20 e 200.
- `generations ≈ 50 * sqrt(n)` limitado entre 50 e 2000.
- `mutation_rate ≈ 1/n` limitado entre 0.01 e 0.1.

## 5. Decisões de Projeto
1. Penalidade rígida + reparo para inviáveis (capacidade nunca excedida na prática).
2. Reparo guloso reduz descarte e acelera convergência.
3. Histórico opt-in evita overhead quando não necessário.
4. JSON flexível: capacidade opcional com fallback via CLI/entrada.
5. Simplicidade: sem dependências externas.

## 6. Análise de Complexidade
- Avaliação por indivíduo: O(n) onde n é número de itens.
- Reparo: no pior caso O(n^2) (remoções sucessivas com busca do pior item no conjunto selecionado), mas prático.
- Uma geração: ~ O(pop_size * n).
- Total: ~ O(generations * pop_size * n) até parada por estabilidade.

## 7. Validação
Execuções com instância exemplo mostram: respeito à capacidade, parada por estabilidade em poucas dezenas de gerações, reparo garantindo factibilidade e histórico coerente.

## 8. Extensões Futuras
- Expor `--stable-limit` na CLI.
- Relatórios de diversidade.
- Crossovers alternativos (dois pontos, uniforme).
- Exportação de histórico para CSV.
- Mutação adaptativa ao longo das gerações.

## 9. Conclusão
O sistema entrega uma solução eficiente e clara para a Mochila 0/1 via AG, integrando reparo, penalização forte e critério adaptativo de parada. A arquitetura modular facilita manutenção e evolução.


