#!/usr/bin/env python3
"""
"""
import os
import sys
import time
from typing import Optional

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Import project modules
from problem.problem import Item, KnapsackProblem
from algorithms.ga import GeneticAlgorithm
from json_utils import (
    list_json_files,
    load_problem_from_json as load_problem_from_json_local,
    choose_file_interactive,
    choose_file_system,
    save_last_dir,
    load_last_dir,
)


def prompt_yes_no(message: str, default: str = 's') -> bool:
    response = input(f'{message} (s/n) [{default}]: ').strip().lower() or default
    return response.startswith('s')


def print_history_table(history: list[dict]) -> None:
    if not history:
        print("(sem histórico)")
        return

    headers = ["ger", "valor", "fitness", "média", "mut", "cross", "peso", "t(s)"]

    table: list[list[str]] = []
    prev_total = 0.0
    for rec in history:
        total = float(rec.get("elapsed", 0.0))
        gen_time = max(0.0, total - prev_total)
        prev_total = total

        row = [
            str(rec.get("gen", "-")),
            str(int(rec.get("best_value", 0))),
            f"{rec.get('best_fitness', 0):.2f}",
            f"{rec.get('avg_fitness', 0):.2f}",
            str(rec.get("mutations", 0)),
            str(rec.get("crossovers", 0)),
            str(rec.get("best_weight", "-")),
            f"{gen_time:.4f}",
        ]
        table.append(row)

    widths = [max(len(headers[i]), max(len(row[i]) for row in table)) for i in range(len(headers))]

    print(" | ".join(h.center(w) for h, w in zip(headers, widths)))
    print("-+-".join("-" * w for w in widths))

    for row in table:
        print(" | ".join(cell.rjust(w) for cell, w in zip(row, widths)))


def load_problem_from_json(path: str, provided_capacity: Optional[int] = None):
    items_data, capacity = load_problem_from_json_local(path)
    capacity = capacity or provided_capacity

    if capacity is None:
        if sys.stdin is not None and sys.stdin.isatty():
            while True:
                v = input("JSON não contém 'capacity'. Informe a capacidade (peso máximo) como inteiro: ").strip()
                if v == "":
                    print('Entrada vazia. Cancelando.')
                    sys.exit(1)
                try:
                    capacity = int(v)
                    if capacity <= 0:
                        print('A capacidade deve ser um inteiro positivo. Tente novamente.')
                        continue
                    break
                except ValueError:
                    print('Valor inválido. Digite um número inteiro positivo.')
        else:
            print(f"Erro: o arquivo {path} não contém 'capacity'. Passe --capacity na linha de comando ou adicione 'capacity' ao JSON.")
            sys.exit(1)

    items = [
        Item(
            name=it.get('name') if isinstance(it, dict) else None,
            weight=it['weight'],
            value=it['value']
        )
        for it in items_data
    ]
    return items, capacity


def prompt(prompt_text: str, default: Optional[str] = None) -> str:
    if default is None:
        return input(prompt_text)
    else:
        v = input(f"{prompt_text} [{default}]: ")
        return v.strip() or default


def _print_selected_items(best, items, capacity):
    try:
        selected_idx = [i for i, bit in enumerate(best) if int(bit)]
        if not selected_idx:
            print('\nNenhum item selecionado pelo indivíduo ótimo.')
            return

        selected_sorted = sorted(selected_idx, key=lambda i: items[i].value / items[i].weight if items[i].weight > 0 else float('inf'), reverse=True)

        print('\nItens selecionados (ordenados por valor/peso):')
        total_value = total_weight = 0
        for display_num, idx in enumerate(selected_sorted, start=1):
            item = items[idx]
            name = item.name or f'Item_{idx+1}'
            print(f'  {display_num}) {name} — peso={item.weight}, valor={item.value}')
            total_value += item.value
            total_weight += item.weight

        print(f'Total de itens selecionados: {len(selected_sorted)}')
        print(f'Peso total dos itens selecionados: {total_weight} / {capacity}')
        print(f'Valor total dos itens selecionados: {total_value}')
    except Exception:
        pass


def run_ga(items, capacity, pop_size, generations, mutation_rate, record_history: bool, print_history: bool, max_time: Optional[float]):
    problem = KnapsackProblem(items, capacity, penalty_factor=10.0)
    ga = GeneticAlgorithm(problem, pop_size=pop_size, generations=generations, mutation_rate=mutation_rate)
    
    print(f"Tempo máximo: {max_time or 'sem limite'} {'segundos' if max_time else ''}")
    
    stable_limit = 15
    print(f"Critério: parar quando o mesmo melhor for encontrado {stable_limit} vezes consecutivas")
    
    start = time.perf_counter()
    best, total_value, total_weight = ga.evolve(record_history=record_history, max_time=max_time, show_progress=False, stable_limit=stable_limit)
    
    elapsed = time.perf_counter() - start

    print('\n(GA) Melhor indivíduo binário:', best)
    print(f'Valor total: {total_value}')
    print(f'Peso total: {total_weight} / {capacity}')
    print(f'Tempo de execução: {elapsed:.4f} s')

    _print_selected_items(best, items, capacity)

    if print_history and ga.history:
        print('\nHistórico por geração (gen, best_fitness, avg_fitness, mutations, crossovers, best_weight, elapsed_s):')
        print_history_table(ga.history)

    # Return GA object so caller can inspect history if desired
    return best, total_value, total_weight, ga


def choose_parameters(items, capacity):
    n = max(1, len(items))
    pop = int(min(200, max(20, 10 * n)))
    generations = int(min(2000, max(50, int(50 * (n ** 0.5)))))
    mutation = float(min(0.1, max(0.01, 1.0 / n)))
    return pop, generations, mutation


def interactive():
    print(     'Knapsack GA - interactive ')
    print('---------------------------------------')

    while True:
        last = load_last_dir(ROOT) or ROOT
        use_system = prompt_yes_no('Abrir seletor de arquivo do sistema para escolher JSON?', True)
        if use_system:
            path = choose_file_system(last)
            if not path:
                jsons = list_json_files(ROOT)
                path = choose_file_interactive(jsons, ROOT)
        else:
            jsons = list_json_files(ROOT)
            path = choose_file_interactive(jsons, ROOT)

        if not path or not os.path.exists(path):
            print('Arquivo não encontrado:', path)
            if prompt_yes_no('Deseja tentar novamente?', True):
                continue
            else:
                break

        save_last_dir(ROOT, os.path.dirname(path))

        items, capacity = load_problem_from_json(path)
        if prompt_yes_no('Selecionar parâmetros automaticamente?', True):
            pop_size, generations, mutation_rate = choose_parameters(items, capacity)
            print(f"Parâmetros selecionados automaticamente: pop_size={pop_size}, generations={generations}, mutation_rate={mutation_rate:.3f}")
        else:
            pop_size = int(prompt('Tamanho da população', '80'))
            generations = int(prompt('Gerações', '150'))
            mutation_rate = float(prompt('Taxa de mutação (ex.: 0.02)', '0.05'))

        max_time = 5.0
        print('\nExecutando... (Ctrl+C para parar)')
        best, total_value, total_weight, ga = run_ga(items, capacity, pop_size, generations, mutation_rate, record_history=True, print_history=False, max_time=max_time)

        if prompt_yes_no('Mostrar histórico por geração?', False) and ga.history:
            print('\nHistórico por geração (gen, best_fitness, avg_fitness, mutations, crossovers, best_weight, elapsed_s):')
            print_history_table(ga.history)

        if not prompt_yes_no('Deseja continuar com outro arquivo?', True):
            print('Saindo. Até mais.')
            break


def non_interactive(argv: list[str]):
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True, help='Arquivo JSON com a definição do problema')
    p.add_argument('--auto', action='store_true', help='seleciona parâmetros do AG automaticamente com base no tamanho do problema')
    p.add_argument('--show', choices=['s', 'n'], default='n', help='mostrar histórico por geração (s/n)')
    p.add_argument('--pop-size', type=int, default=80, help='tamanho da população')
    p.add_argument('--generations', type=int, default=150, help='número de gerações')
    p.add_argument('--mutation-rate', type=float, default=0.02, help='taxa de mutação por gene')
    p.add_argument('--max-time', type=float, default=5.0, help='tempo máximo de execução em segundos (padrão: 5)')
    p.add_argument('--capacity', type=int, default=None, help='capacidade (peso máximo) a usar se o JSON não contiver "capacity"')
    args = p.parse_args(argv)

    if not os.path.exists(args.input):
        print('Input file not found:', args.input)
        return

    items, capacity = load_problem_from_json(args.input, provided_capacity=args.capacity)
    show = args.show == 's'
    if args.auto:
        pop_size, generations, mutation_rate = choose_parameters(items, capacity)
        print(f"Auto-selected parameters: pop_size={pop_size}, generations={generations}, mutation_rate={mutation_rate:.3f}")
    else:
        pop_size, generations, mutation_rate = args.pop_size, args.generations, args.mutation_rate

    # In non-interactive mode: record and print history only if --show is 's'
    run_ga(items, capacity, pop_size, generations, mutation_rate, record_history=show, print_history=show, max_time=args.max_time)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        non_interactive(sys.argv[1:])
    else:
        try:
            interactive()
        except KeyboardInterrupt:
            print('\nInterrupted. Bye.')
