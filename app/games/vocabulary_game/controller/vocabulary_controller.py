import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
# from app.vocabulary_builder.view.vocabulary_view import PageGame

class VocabularyController:
    def __init__(self, root, model):
        self.model = model
        self.view = None
        self.root = root

    def get_categories(self):
        return self.model.list_categories()

    def get_subcategories(self, category):
        return self.model.list_subcategories(category)

    def start_quiz(self, category, subcategory):
        if not category or not subcategory:
            messagebox.showwarning("Selection Error", "Please select both a category and a subcategory!")
            return

        if self.model.load_vocabulary(category, subcategory):
            self.next_word()
            return True
        return False

    def next_word(self):
        if self.root:
            word, answer = self.model.get_next_word()
            path_image = self.model.get_image_path(answer)
            if word:
                self.root.display_word(word)
            if path_image:
                self.root.display_image(path_image)
            else:
                messagebox.showinfo("Quiz End", "You have answered all the words in this subcategory!")
                # self.view.controller.mostrar_frame(PageGame)

    def check_answer(self, user_answer):
        # self.root.feedback_label.config(text="message", foreground="red")
        # if self.model.check_answer(user_answer):
        #     # self.root.after(2000, self.next_word)

        #     # return {"mensage","Correct!", "color":"green"}
        #     return ("Correct!", "green")
        # else:
        #     correct_answer = self.model.current_answer
        #     # self.view.display_feedback(f"{correct_answer}", "red")
        #     print(f"❌: {user_answer}, ✅: {correct_answer}")
        #     # self.root.after(2000, self.next_word)
        #     return (f"{correct_answer}", "red")

        #     # return {"mensage",correct_answer, "color":"red"}

        if self.root:
            if self.model.check_answer(user_answer):
                self.root.display_feedback("Correct!", "green")
            else:
                correct_answer = self.model.current_answer
                self.root.display_feedback(f"{correct_answer}", "red")
                print(f"❌: {user_answer}, ✅: {correct_answer}")
            self.root.after(2000, self.next_word)

    def back_to_categories(self):
        self.model.words = {} # Reset words when going back
        # self.view.controller.mostrar_frame(PageGame)

# import tkinter as tk
# from tkinter import ttk, messagebox
# import random
# import json
# import os
# from app.vocabulary_builder.model.vocabulary_model import VocabularyModel
# from app.vocabulary_builder.view.vocabulary_view import VocabularyView



# class VocabularyController:
#     def __init__(self, root):
#         self.model = VocabularyModel()
#         self.view = VocabularyView(root, self)

#     def get_categories(self):
#         return self.model.list_categories()

#     def get_subcategories(self, category):
#         return self.model.list_subcategories(category)

#     def start_quiz(self):
#         category = self.view.category_combobox.get()
#         subcategory = self.view.subcategory_combobox.get()

#         if not category or not subcategory:
#             messagebox.showwarning("Selection Error", "Please select both a category and a subcategory!")
#             return

#         if self.model.load_vocabulary(category, subcategory):
#             self.view.show_quiz_frame()
#             self.next_word()

#     def next_word(self):
#         word, answer = self.model.get_next_word()
#         if word:
#             self.view.display_word(word)
#         else:
#             messagebox.showinfo("Quiz End", "You have answered all the words in this subcategory!")
#             self.view.show_category_frame()

#     def check_answer(self):
#         user_answer = self.view.answer_entry.get()
#         if self.model.check_answer(user_answer):
#             self.view.display_feedback("Correct!", "green")
#         else:
#             correct_answer = self.model.current_answer
#             self.view.display_feedback(f"{correct_answer}", "red")
#             print(f"❌: {user_answer}, ✅: {correct_answer}")
#         self.view.root.after(2000, self.next_word)

#     def back_to_categories(self):
#         self.model.words = {} # Reset words when going back
#         self.view.show_category_frame()

# # --- (Simulando seus arquivos) ---
# def listar_funcionalidades(data_folder="data"):
#     return [d for d in os.listdir(data_folder) if os.path.isdir(os.path.join(data_folder, d))]

# def exibir_vocabulario(categoria, data_folder="data"):
#     category_path = os.path.join(data_folder, categoria)
#     if os.path.exists(category_path) and os.path.isdir(category_path):
#         return [f[:-5] for f in os.listdir(category_path) if f.endswith(".json")]
#     return []

# def carregar_vocabulario(categoria, arquivo, data_folder="data"):
#     filepath = os.path.join(data_folder, categoria, f"{arquivo}.json")
#     try:
#         with open(filepath, 'r', encoding='utf-8') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         messagebox.showerror("Error", f"Vocabulary file not found: {filepath}")
#         return {}
#     except json.JSONDecodeError:
#         messagebox.showerror("Error", f"Error decoding JSON in: {filepath}")
#         return {}