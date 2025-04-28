import tkinter as tk
from tkinter import ttk
from app.model.vocabulary_model import VocabularyModel
from app.games.vocabulary_game.controller.vocabulary_controller import VocabularyController
from app.utils.score import ScoreManager

from PIL import Image, ImageTk

# TODO: Evite prints de Debugs, use logging
# TODO: Padronizar nomes dos widgets (deixar todos em ingles)

class VocabularyGame(tk.Frame):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.model = VocabularyModel()
        self.controller = VocabularyController(root=self, model=self.model)

        self.create_main_screen()
        self.create_game_screen()

        self.show_main_screen()

    def create_main_screen(self):
        self.screen_main = tk.Frame(self)

        self.label_selection_title = tk.Label(self.screen_main, text="Seleção do Tipo de Jogo", font=("Arial", 16))
        self.centralizar_widget(self.label_selection_title, 0.1)

        self.label_category = tk.Label(self.screen_main, text="Escolha uma categoria:", font=("Arial", 14))
        self.centralizar_widget(self.label_category, 0.2)

        self.category_combobox = ttk.Combobox(self.screen_main, state="readonly")
        self.centralizar_widget(self.category_combobox, 0.3)
        self.category_combobox["values"] = self.controller.get_categories()
        self.category_combobox.bind("<<ComboboxSelected>>", self.populate_subcategories)

        self.label_subcategory = tk.Label(self.screen_main, text="Escolha uma subcategoria:", font=("Arial", 14))
        self.centralizar_widget(self.label_subcategory, 0.4)

        self.subcategory_combobox = ttk.Combobox(self.screen_main, state="readonly")
        self.centralizar_widget(self.subcategory_combobox, 0.5)
        self.subcategory_combobox["state"] = "disabled"
        self.subcategory_combobox.bind("<<ComboboxSelected>>", self.enable_start_button)

        self.start_button = tk.Button(self.screen_main, text="Iniciar Jogo", command=self.start_game, font=("Arial", 12), state="disabled")
        self.centralizar_widget(self.start_button, 0.7)

    def create_game_screen(self):
        self.screen_game = tk.Frame(self)

        self.label_game_info = tk.Label(self.screen_game, text="Game Info", font=("Arial", 14))
        self.centralizar_widget(self.label_game_info, 0.1)

        self.label_image = tk.Label(self.screen_game)
        self.centralizar_widget(self.label_image, 0.2)
        self.displayed_image_tk = None

        self.word_label = tk.Label(self.screen_game, text="Word label", font=("Arial", 18, "bold"))
        self.centralizar_widget(self.word_label, 0.3)

        self.answer_entry = ttk.Entry(self.screen_game, font=("Arial", 14))
        self.centralizar_widget(self.answer_entry, 0.4)

        self.feedback_label = ttk.Label(self.screen_game, text="Feedback", font=("Arial", 12))
        self.centralizar_widget(self.feedback_label, 0.5)

        self.botao_confirmar = tk.Button(self.screen_game, text="Confirmar", command=self.check_answer)
        self.botao_confirmar.place(relx=0.65, rely=0.7, anchor=tk.CENTER)

        self.botao_voltar_inicial = tk.Button(self.screen_game, text="Voltar para Seleção", command=self.show_main_screen)
        self.botao_voltar_inicial.place(relx=0.35, rely=0.7, anchor=tk.CENTER)

    def start_game(self) -> None:
        self.screen_main.pack_forget()
        self.screen_game.pack(fill="both", expand=True)


        category = self.category_combobox.get()
        subcategory = self.subcategory_combobox.get()
        self.controller.start_quiz(category=category, subcategory=subcategory)

    def show_main_screen(self):
        self.screen_game.pack_forget()
        self.screen_main.pack(fill="both", expand=True)


    def centralizar_widget(self, widget, rely, relx=0.5):
        widget.place(relx=relx, rely=rely, anchor=tk.CENTER)

    def populate_subcategories(self, event):
        category = self.category_combobox.get()
        print(f"[DEBUG] Categoria selecionada: {category}")

        subcategories = self.controller.get_subcategories(category)
        print(f"[DEBUG] Subcategorias retornadas: {subcategories}")

        if subcategories:
            self.subcategory_combobox["state"] = "readonly"
            self.subcategory_combobox["values"] = subcategories
            self.subcategory_combobox.set("")  # Limpa o campo
            self.subcategory_combobox.config(state="readonly")  # Depois coloca de volta para "readonly"
            self.start_button["state"] = "disabled"
            self.subcategory_combobox.bind("<<ComboboxSelected>>", self.enable_start_button)
        else:
            self.subcategory_combobox["state"] = "disabled"
            self.subcategory_combobox["values"] = []
            self.subcategory_combobox.set("")
            self.start_button["state"] = "disabled"

    def enable_start_button(self, event):
        print("Dados: ", self.subcategory_combobox.get())
        if self.subcategory_combobox.get():
            self.start_button["state"] = "normal"
        else:
            self.start_button["state"] = "disabled"
    
    def load_game_content(self, category, subcategory):
        self.label_game_info.config(text=f"Vocabulário - Categoria: {category}, Subcategoria: {subcategory}")
        self.controller.view = self
        self.next_word()

    def display_word(self, word):
        self.word_label.config(text=word)
        self.answer_entry.delete(0, tk.END)
        self.feedback_label.config(text="")

    def display_image(self, path_image):
        try:
            imagem_pil = Image.open(path_image)
            imagem_pil.thumbnail((200, 200))
            imagem_tk = ImageTk.PhotoImage(imagem_pil)
            self.label_image.config(image=imagem_tk)
            self.displayed_image_tk = imagem_tk
        except FileNotFoundError:
            print(f"Erro: Arquivo de imagem não encontrado em {path_image}")
            self.label_image.config(text="Imagem não encontrada")
        except Exception as e:
            print(f"Erro ao carregar a imagem: {e}")
            self.label_image.config(text=f"Erro ao carregar a imagem: {e}")

    def display_feedback(self, message, color):
        self.feedback_label.config(text=message, foreground=color)

    def check_answer(self):
        # self.controller.check_user_answer(self.answer_entry.get()) # TODO: musar o nome do metodo: check_user_answer
        self.controller.check_answer(self.answer_entry.get())

    def next_word(self):
        self.controller.next_word()

# # Inicializa o jogo
# if __name__ == "__main__":
#     root = tk.Tk()
#     root.title("Vocabulary Game")
#     game = VocabularyGame(root)
#     game.pack(expand=True, fill='both')
#     root.geometry("375x350")
#     root.mainloop()
