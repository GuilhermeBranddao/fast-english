import os
import random
import json
from tkinter import messagebox
from pathlib import Path
from app.utils.toolkit import read_json, normalize_text

class VocabularyModel:
    def __init__(self, data_folder:Path="database/vocabulary_json", image_folder:Path="database/images/time_expressions"):
        self.data_folder = data_folder
        self.image_folder = image_folder
        self.current_category = None
        self.current_subcategory = None
        self.words = {}
        self.current_word = None
        self.current_answer = None

    def list_categories(self) -> list:
        """Lists all categories available in the data folder."""
        return [
            category for category in os.listdir(self.data_folder)
            if os.path.isdir(os.path.join(self.data_folder, category))
        ]

    def list_subcategories(self, category: str) -> list:
        """Lists subcategories within a specific category."""
        category_path = os.path.join(self.data_folder, category)
        if os.path.isdir(category_path):
            return [
                subcategory[:-5] for subcategory in os.listdir(category_path)
                if subcategory.endswith(".json")
            ]
        return []

    def load_vocabulary(self, category: str, subcategory: str) -> bool:
        """Loads vocabulary from a specific category and subcategory."""
        file_path = os.path.join(self.data_folder, category, f"{subcategory}.json")
        self.words = read_json(file_path)
        return bool(self.words)

    def get_next_word(self) -> tuple:
        """Selects the next word randomly from the vocabulary."""
        if self.words:
            self.current_word, self.current_answer = random.choice(list(self.words.items()))
            return self.current_word, self.current_answer
        return None, None

    def get_image_path(self, image_name: str) -> str:
        """Gets the full path for an image file."""
        return os.path.join(self.image_folder, f"{image_name.lower()}.png")
    
    def check_answer(self, user_answer: str) -> bool:
        """Checks if the user's answer is correct."""
        normalized_user_answer = normalize_text(user_answer)
        normalized_correct_answer = normalize_text(self.current_answer)

        if self.current_word and normalized_user_answer == normalized_correct_answer:
            self.words.pop(self.current_word)
            return True
        return False

    