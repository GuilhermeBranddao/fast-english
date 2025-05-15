from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import json

class DataLoader:
    def __init__(self, base_path=None):
        self.base_path = Path(base_path)

    def get_all_words(self, subcategory_name=None) -> list[dict]:
        word_paths = []

        for categoria in os.scandir(self.base_path):
            if not categoria.is_dir():
                continue
            for subcat in os.scandir(categoria.path):
                if not subcat.is_dir():
                    continue
                if subcategory_name and Path(subcat).name != subcategory_name:
                    continue
                for word_dir in os.scandir(subcat.path):
                    if word_dir.is_dir():
                        word_paths.append(Path(word_dir.path))

        # Carrega os dados em paralelo
        with ThreadPoolExecutor() as executor:
            palavras = list(executor.map(self._carregar_palavra_safe, word_paths))

        # Remove os que falharam (retornaram None)
        return [p for p in palavras if p]

    def get_categories(self, kind_return="list") -> list[Path]:
        if kind_return == "list":
            return [self.base_path / path for path in os.listdir(self.base_path)]
        elif kind_return == "dict":
            return {path: self.base_path / path for path in os.listdir(self.base_path)}
        
    def get_subcategories(self, category_path) -> list[Path]:
        return [category_path / path for path in os.listdir(category_path)]
    
    def get_word_paths(self, subcategory_path) -> list[Path]:
        return [subcategory_path / path for path in os.listdir(subcategory_path)]

    def _carregar_palavra_safe(self, path: Path) -> dict | None:
        try:
            return self._carregar_palavra(path)
        except Exception:
            return None

    def _carregar_palavra(self, path: Path) -> dict:
        if not (path / "text_v2.json").exists():
            raise FileNotFoundError(f"File text_v2.json not found in {path}.")

        files = os.listdir(path)
        text_info = self._carregar_texto(path)

        return {
            "path": path,
            "files": files,
            "text_pt_br": text_info.get("pergunta_pt-br", ""),
            "text_eng": text_info.get("tradução_en", ""),
            "audio_path": path / "audio.wav",
            "image_figure": path / "image_figure.jpg",
        }

    def _carregar_texto(self, path) -> dict:
        try:
            with open(path / "text_v2.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}