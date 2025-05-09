from typing import Dict, Union, List
import csv
import os


def save_game_data(data: Dict[str, Union[str, int, float, List[str], bool]], 
                   file_path: str = "database/infos/game_data_{game_name}.csv") -> None:
    
    file_path = file_path.format(game_name=data.get("game_name", "error"))
    file_exists = os.path.isfile(file_path)

    # Convert listas para string
    for key, value in data.items():
        if isinstance(value, list):
            data[key] = ",".join(map(str, value))

    # Define os fieldnames dinamicamente
    if file_exists:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            # Adiciona novas chaves que estão em `data` mas não no CSV
            for key in data.keys():
                if key not in fieldnames:
                    fieldnames.append(key)
    else:
        fieldnames = list(data.keys())

    # Reescreve o CSV inteiro se foi necessário atualizar os cabeçalhos
    if file_exists:
        with open(file_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        # Atualiza todas as linhas antigas com as novas chaves (valores vazios)
        for row in rows:
            for key in fieldnames:
                if key not in row:
                    row[key] = ""

        # Adiciona a nova linha
        clean_data = {key: data.get(key, "") for key in fieldnames}
        rows.append(clean_data)

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    else:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(data)