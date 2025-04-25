from tkinter import messagebox
import random
import json
import os

class VocabularyModel:
    def __init__(self, data_folder="database/vocabulary_json", data_folder_imagens="database/images/time_expressions"):
        self.data_folder = data_folder 
        self.data_folder_imagens = data_folder_imagens
        self.current_category = None
        self.current_subcategory = None
        self.words = {}
        self.current_word = None
        self.current_answer = None

    def list_categories(self):
        categories = [d for d in os.listdir(self.data_folder) if os.path.isdir(os.path.join(self.data_folder, d))]
        return categories

    def list_subcategories(self, category):
        category_path = os.path.join(self.data_folder, category)
        if os.path.exists(category_path) and os.path.isdir(category_path):
            subcategories = [f[:-5] for f in os.listdir(category_path) if f.endswith(".json")]
            return subcategories
        return []

    def load_vocabulary(self, category, subcategory):
        filepath = os.path.join(self.data_folder, category, f"{subcategory}.json")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.words = json.load(f)
            return True
        except FileNotFoundError:
            messagebox.showerror("Error", f"Vocabulary file not found: {filepath}")
            return False
        except json.JSONDecodeError:
            messagebox.showerror("Error", f"Error decoding JSON in: {filepath}")
            return False

    def get_next_word(self):
        if not self.words:
            return None, None
        self.current_word = random.choice(list(self.words.keys()))
        self.current_answer = self.words[self.current_word]
        return self.current_word, self.current_answer
    
    def get_path_image(self, image_name:str):
        image_name = image_name.lower()
        return os.path.join(self.data_folder_imagens, f"{image_name}.png") 

    def check_answer(self, user_answer):
        if self.current_word and user_answer.strip().lower() == self.current_answer.lower():
            self.words.pop(self.current_word)
            return True
        return False



# from tkinter import messagebox
# import random
# import json
# import os

# class VocabularyModel:
#     def __init__(self, data_folder="data"):
#         self.data_folder = data_folder
#         self.current_category = None
#         self.current_subcategory = None
#         self.words = {}
#         self.current_word = None
#         self.current_answer = None

#     def list_categories(self):
#         categories = [d for d in os.listdir(self.data_folder) if os.path.isdir(os.path.join(self.data_folder, d))]
#         return categories

#     def list_subcategories(self, category):
#         category_path = os.path.join(self.data_folder, category)
#         if os.path.exists(category_path) and os.path.isdir(category_path):
#             subcategories = [f[:-5] for f in os.listdir(category_path) if f.endswith(".json")]
#             return subcategories
#         return []

#     def load_vocabulary(self, category, subcategory):
#         filepath = os.path.join(self.data_folder, category, f"{subcategory}.json")
#         try:
#             with open(filepath, 'r', encoding='utf-8') as f:
#                 self.words = json.load(f)
#             return True
#         except FileNotFoundError:
#             messagebox.showerror("Error", f"Vocabulary file not found: {filepath}")
#             return False
#         except json.JSONDecodeError:
#             messagebox.showerror("Error", f"Error decoding JSON in: {filepath}")
#             return False

#     def get_next_word(self):
#         if not self.words:
#             return None, None
#         self.current_word = random.choice(list(self.words.keys()))
#         self.current_answer = self.words[self.current_word]
#         return self.current_word, self.current_answer

#     def check_answer(self, user_answer):
#         if self.current_word and user_answer.strip().lower() == self.current_answer.lower():
#             self.words.pop(self.current_word)
#             return True
#         return False