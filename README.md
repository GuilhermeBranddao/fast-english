# Instalando

poetry env use python
poetry env activate


poetry self add poetry-plugin-export
poetry export -f requirements.txt --output requirements.txt


python -m spacy download en_core_web_sm


```python
import os
from pathlib import Path

# Função para detectar a raiz do projeto com base na presença de ".venv"
def find_project_root(max_depth=10):
    current = Path.cwd()
    for i in range(max_depth):
        if any((current / name).exists() for name in [".venv", "pyproject.toml", ".git"]):
            print(f"📁 Raiz do projeto encontrada: {current}")
            os.chdir(current)
            return current
        print(f"{i} - Subindo para: {current.parent}")
        current = current.parent
    raise RuntimeError("❌ Raiz do projeto não encontrada.")

# Executa a busca
project_root = find_project_root()

# Ativa autoreload para desenvolvimento dinâmico
%load_ext autoreload
%autoreload 2
```