
import os
import json
from typing import List, Optional, Tuple

_cache: dict[str, Tuple[List[dict], Optional[int]]] = {}
_LAST_DIR_FILENAME = '.last_json_dir'


def list_json_files(root: str) -> List[str]:
    try:
        return sorted([f for f in os.listdir(root) if f.endswith('.json')])
    except Exception:
        return []


def load_problem_from_json(path: str) -> Tuple[List[dict], Optional[int]]:
    """Carrega e retorna (items, capacity_or_None). Usa cache em memória se disponível."""
    abs_path = os.path.abspath(path)
    if abs_path in _cache:
        return _cache[abs_path]

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    capacity = None
    if 'capacity' in data and data['capacity'] is not None:
        try:
            capacity = int(data['capacity'])
        except Exception:
            raise ValueError("Campo 'capacity' inválido. Deve ser um inteiro.")

    try:
        items = [
            {
                'name': it.get('name') if isinstance(it, dict) else None,
                'weight': int(it['weight']),
                'value': int(it['value'])
            }
            for it in data['items']
        ]
    except Exception:
        raise ValueError('Formato JSON inválido. Esperado: {"capacity": int (opcional), "items": [{"weight":int, "value":int}, ...]}')

    _cache[abs_path] = (items, capacity)
    return items, capacity


def get_cached(path: str) -> Optional[Tuple[List[dict], int]]:
    return _cache.get(os.path.abspath(path))


def save_last_dir(root: str, path: str) -> None:
    try:
        with open(os.path.join(root, _LAST_DIR_FILENAME), 'w', encoding='utf-8') as f:
            f.write(path)
    except Exception:
        pass


def load_last_dir(root: str) -> Optional[str]:
    p = os.path.join(root, _LAST_DIR_FILENAME)
    try:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                v = f.read().strip()
                if v:
                    return v
    except Exception:
        pass
    return None


def choose_directory_system(root: str) -> str:
    """Tenta abrir seletor nativo de diretório (tkinter). Se falhar, pede texto."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        tk.Tk().withdraw()
        sel = filedialog.askdirectory(initialdir=root)
        if sel:
            save_last_dir(root, sel)
            return sel
    except Exception:
        pass

    v = input(f"Digite caminho da pasta contendo JSONs [{root}]: ").strip()
    chosen = v or root
    save_last_dir(root, chosen)
    return chosen


def choose_file_system(initial_dir: str) -> str:
    """Abre seletor nativo de arquivo (.json). Retorna caminho ou '' se cancelado."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        tk.Tk().withdraw()
        sel = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[('JSON files', '*.json')])
        if sel:
            save_last_dir(initial_dir, os.path.dirname(sel))
            return sel
    except Exception:
        pass

    v = input(f"Digite caminho do arquivo JSON [{initial_dir}]: ").strip()
    return v or ''


def read_raw_json(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def choose_file_interactive(json_list: List[str], root: str) -> str:
    """Escolha interativa por texto (mantém compatibilidade anterior)."""
    def prompt(msg: str, default: str = '') -> str:
        return input(f"{msg} [{default}] : ").strip() or default

    last = load_last_dir(root)
    if last and (input(f"Usar pasta salva de JSONs? [{last}] (s/n): ").strip().lower() or 's').startswith('s'):
        try:
            json_list = sorted([f for f in os.listdir(last) if f.endswith('.json')])
            root = last
        except Exception:
            pass

    if not json_list:
        choose_dir = input('Nenhum JSON encontrado aqui. Abrir seletor de pasta do sistema? (s/n) [s]: ').strip().lower() or 's'
        if choose_dir.startswith('s'):
            chosen_dir = choose_directory_system(root)
            try:
                json_list = sorted([f for f in os.listdir(chosen_dir) if f.endswith('.json')])
                root = chosen_dir
            except Exception:
                pass
        if not json_list:
            return prompt('Digite o caminho do arquivo JSON', '')

    print('\nArquivos JSON encontrados:')
    for i, name in enumerate(json_list, start=1):
        print(f'  {i}) {name}')
    print('  0) digitar caminho manualmente')

    while True:
        choice = prompt('Escolha (número, parte do nome, ENTER=1)', '1').strip()
        if choice == '':
            choice = '1'

        if choice.isdigit():
            idx = int(choice)
            if idx == 0:
                return prompt('Digite o caminho do arquivo JSON', '')
            if 1 <= idx <= len(json_list):
                return os.path.join(root, json_list[idx - 1])
            print('Índice fora do intervalo, tente novamente.')
            continue

        if os.path.exists(choice):
            return choice

        matches = [name for name in json_list if choice.lower() in name.lower()]
        if len(matches) == 1:
            return os.path.join(root, matches[0])
        if len(matches) > 1:
            print('\nForam encontradas várias correspondências:')
            for i, name in enumerate(matches, start=1):
                print(f'  {i}) {name}')
            sub = prompt('Escolha o número da correspondência (ou ENTER para cancelar)', '')
            if sub.isdigit():
                si = int(sub)
                if 1 <= si <= len(matches):
                    return os.path.join(root, matches[si - 1])
            print('Entrada inválida, tente novamente.')
            continue

        print('Nenhum arquivo correspondente encontrado, tente novamente.')
