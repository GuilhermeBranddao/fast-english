from pathlib import Path
import json
import os

class DataLoader:
    def __init__(self, base_path):
        self.base_path = Path(base_path)

    def get_categories(self, kind_return="list") -> list[Path]:
        if kind_return == "list":
            return [self.base_path / path for path in os.listdir(self.base_path)]
        elif kind_return == "dict":
            return {path: self.base_path / path for path in os.listdir(self.base_path)}

    def get_subcategories(self, category_path) -> list[Path]:
        return [category_path / path for path in os.listdir(category_path)]

    def get_word_paths(self, subcategory_path) -> list[Path]:
        return [subcategory_path / path for path in os.listdir(subcategory_path)]

    def get_all_words(self, subcategory_name=None) -> list[dict]:
        palavras = []
        for categoria in self.get_categories():
            for subcat in self.get_subcategories(categoria):
                if subcategory_name and subcat.name != subcategory_name:
                    continue
                for word_path in self.get_word_paths(subcat):
                    palavras.append(self._carregar_palavra(word_path))
        return palavras

    def _carregar_palavra(self, path) -> dict:
        files = list(os.listdir(path))
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