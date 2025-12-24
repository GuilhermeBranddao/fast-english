import json
import os
from collections import defaultdict
from pathlib import Path
# def get_add_words():

class DataLoader:
    def __init__(self, group:str=None, base_path=os.path.join("database", "data")) -> None:
        self.base_path = base_path
        self.group = group

    def load_index(self):
        with open(os.path.join(self.base_path, "index.json"), "r", encoding="utf-8") as f:
            # loaded_word_index = {entry["base"]: entry for entry in json.load(f)}
            loaded_word_index = json.load(f)
        
        return loaded_word_index
    
    def get_list_groups(self):
        return [folder for folder in os.listdir(self.base_path) if "." not in folder]
    
    def get_categories(self, group=None) -> set:
        # TODO: Pra melhorar o desempenho é possivel guardar os dados do index em cache
        index = self.load_index()
        
        if group:
            return set([i["category"] for i in index if i["type"] == group])
        else:
            return set([i["category"] for i in index if i["type"] == self.group])

    def get_count_subcategory_per_category(self, group) -> dict:
        index = self.load_index()

        if group:
            return {i["category"]:len(i["subcategory"]) for i in index if i["type"] == group}
        else:
            return {i["category"]:len(i["subcategory"]) for i in index if i["type"] == self.group}
    
    def map_categories_to_subcategories(self, group=None) -> dict:
        index = self.load_index()
        dict_subcategory_path_word = defaultdict(set)

        if group:
            for i in index:
                if i["type"] == group:
                    dict_subcategory_path_word[i["category"]].add(i["subcategory"])
        else:
            for i in index:
                if i["type"] == self.group:
                    dict_subcategory_path_word[i["category"]].add(i["subcategory"])
        return dict(dict_subcategory_path_word)
    
    def map_subcategories_to_word_path(self, group=None):
        """
        Obtem hashMap contendo a subcategoria e sua lista de palavras
        """
        index = self.load_index()

        dict_subcategory_path_word = defaultdict(set)
        
        if group:
            for i in index:
                if i["type"] == group:
                    dict_subcategory_path_word[i["subcategory"]].add(i["path"])
        else:
            for i in index:
                if i["type"] == self.group:
                    dict_subcategory_path_word[i["subcategory"]].add(i["path"])


        return dict(dict_subcategory_path_word)

    def _load_text(self, path: Path) -> dict:
        try:
            with open(path / "text_v2.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
            
    def load_words(self, path: Path) -> dict:
        if not (path / "text_v2.json").exists():
            raise FileNotFoundError(f"File text_v2.json not found in {path}.")

        files = os.listdir(path)
        text_info = self._load_text(path)

        return {
            "path": path,
            "files": files,
            "text_pt_br": text_info.get("pergunta_pt-br", ""),
            "text_eng": text_info.get("tradução_en", ""),
            "status": text_info.get("status", ""),
            "audio_path": path / "audio.wav",
            "image_figure": path / "image_figure.jpg",
        }

        # return {i["subcategory"]:i["path"] for i in index if i["type"] == self.group}

    # def get_list_words_per_path(self, path_word):
    #     """
    #     Obtendo lista de palavras pelo caminho
    #     """

    # def get_subcategories():
    # def get_word_paths():