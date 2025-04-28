import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import os

from app.vocabulary_game.model.vocabulary_model import VocabularyModel
# from app.vocabulary_game.view.vocabulary_view import VocabularyView
from app.vocabulary_game.controller.vocabulary_controller import VocabularyController
from app.game_color.main import ColorGame
from app.hangman_game.main import HangmanGame
from app.vocabulary_game.main import VocabularyGame
from app.text_challenge.main import TextChallengeApp

class Pagina(tk.Frame):
    def __init__(self, parent, controller, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.controller = controller

    def centralizar_widget(self, widget, rely):
        widget.place(relx=0.5, rely=rely, anchor=tk.CENTER)

class PaginaInicial(Pagina):
    def __init__(self, parent, controller, **kwargs):
        Pagina.__init__(self, parent, controller, **kwargs)


        label = tk.Label(self, text="Esta é a Página Inicial")
        label.grid(row=0, column=0, columnspan=2, padx=10, pady=10) # Ocupa duas colunas

        botao1 = tk.Button(self, text="Jogo Vocabulario", command=lambda: controller.mostrar_frame(VocabularyGameView))
        botao1.grid(row=1, column=0, padx=10, pady=5, sticky="ew") # sticky="ew" expande horizontalmente

        botao2 = tk.Button(self, text="Ir para a Página 2", command=lambda: controller.mostrar_frame(Pagina2))
        botao2.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        botao_game_color = tk.Button(self, text="Game Color", command=lambda: controller.mostrar_frame(ColorGameView))
        botao_game_color.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        botao_hangman_game = tk.Button(self, text="Jogo Da Forca", command=lambda: controller.mostrar_frame(HangmanGameView))
        botao_hangman_game.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        botao_text_challenge = tk.Button(self, text="Desafio Do Texto", command=lambda: controller.mostrar_frame(TextChallengeAppView))
        botao_text_challenge.grid(row=2, column=2, padx=10, pady=5, sticky="ew")


class HangmanGameView(Pagina):
    def __init__(self, parent, controller, **kwargs):
        Pagina.__init__(self, parent, controller, **kwargs)
        self.game = HangmanGame(self)
        self.game.pack(expand=True, fill='both')

        botao_voltar = tk.Button(self, text="Voltar para a Inicial", command=lambda: controller.mostrar_frame(PaginaInicial))
        self.centralizar_widget(botao_voltar, 0.8)

class ColorGameView(Pagina):
    def __init__(self, parent, controller, **kwargs):
        Pagina.__init__(self, parent, controller, **kwargs)
        self.game = ColorGame(self)
        self.game.pack(expand=True, fill='both')

        botao_voltar = tk.Button(self, text="Voltar para a Inicial", command=lambda: controller.mostrar_frame(PaginaInicial))
        self.centralizar_widget(botao_voltar, 0.8)

class PaginaComBotaoVoltar(Pagina):
    def __init__(self, parent, controller, texto_label, **kwargs):
        Pagina.__init__(self, parent, controller, **kwargs)
        label = tk.Label(self, text=texto_label)
        self.centralizar_widget(label, 0.2)
        botao_voltar = tk.Button(self, text="Voltar para a Inicial", command=lambda: controller.mostrar_frame(PaginaInicial))
        self.centralizar_widget(botao_voltar, 0.8)

class VocabularyGameView(Pagina):
    def __init__(self, parent, controller, **kwargs):
        Pagina.__init__(self, parent, controller, **kwargs)

        self.game = VocabularyGame(self)
        self.game.pack(expand=True, fill='both')

        botao_voltar = tk.Button(self, text="Voltar para a Inicial", command=lambda: controller.mostrar_frame(PaginaInicial))
        self.centralizar_widget(botao_voltar, 0.8)

class TextChallengeAppView(Pagina):
    def __init__(self, parent, controller, **kwargs):
        Pagina.__init__(self, parent, controller, **kwargs)

        self.game = TextChallengeApp(self)
        self.game.pack(expand=True, fill='both')

        botao_voltar = tk.Button(self, text="Voltar para a Inicial", command=lambda: controller.mostrar_frame(PaginaInicial))
        self.centralizar_widget(botao_voltar, 0.8)

class Pagina2(PaginaComBotaoVoltar):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Esta é a Página 2")



class ControladorDePaginas(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Aplicação com Múltiplas Páginas")
        self.geometry('600x600')

        container = tk.Frame(self)
        container.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.frames = {}


        
        for F in (PaginaInicial, Pagina2, VocabularyGameView, ColorGameView, HangmanGameView, TextChallengeAppView):
            # config = page_configurations.get(F, {})
            frame = F(container, self)
            self.frames[F] = frame
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.mostrar_frame(PaginaInicial)

    def mostrar_frame(self, pagina_classe, **kwargs):
        frame = self.frames[pagina_classe]
        frame.tkraise()
        if pagina_classe == VocabularyGameView and kwargs:
            frame.load_game_content(kwargs['game_category'], kwargs['game_subcategory'])


# app = ControladorDePaginas()
# app.mainloop()




# import tkinter as tk
# from tkinter import ttk

# class VocabularyView:
#     def __init__(self, root, controller):
#         self.root = root
#         self.root.title("Vocabulary Quiz")
#         self.controller = controller

#         self.category_frame = ttk.Frame(self.root, padding=10)
#         self.category_frame.pack(fill="both", expand=True)

#         ttk.Label(self.category_frame, text="Choose a category:", font=("Arial", 14)).pack(pady=5)
#         self.category_combobox = ttk.Combobox(self.category_frame, state="readonly")
#         self.category_combobox.pack(pady=5)
#         self.category_combobox.bind("<<ComboboxSelected>>", self.populate_subcategories)

#         ttk.Label(self.category_frame, text="Choose a subcategory:", font=("Arial", 14)).pack(pady=5)
#         self.subcategory_combobox = ttk.Combobox(self.category_frame, state="readonly")
#         self.subcategory_combobox.pack(pady=5)

#         self.start_button = ttk.Button(self.category_frame, text="Start Quiz", command=self.controller.start_quiz)
#         self.start_button.pack(pady=10)

#         self.quiz_frame = ttk.Frame(self.root, padding=10)

#         ttk.Label(self.quiz_frame, text="Translate the following word:", font=("Arial", 14)).pack(pady=10)
#         self.word_label = ttk.Label(self.quiz_frame, text="", font=("Arial", 18, "bold"))
#         self.word_label.pack(pady=10)

#         self.label1 = ttk.Label(self.quiz_frame, text="Label 1")
#         self.label1.pack(pady=13)

#         self.answer_entry = ttk.Entry(self.quiz_frame, font=("Arial", 14))
#         self.answer_entry.pack(pady=5)

#         self.check_button = ttk.Button(self.quiz_frame, text="Check Answer", command=self.controller.check_answer)
#         self.check_button.pack(pady=5)

#         self.feedback_label = ttk.Label(self.quiz_frame, text="", font=("Arial", 12))
#         self.feedback_label.pack(pady=5)

#         self.back_button = ttk.Button(self.quiz_frame, text="Back to Categories", command=self.controller.back_to_categories)
#         self.back_button.pack(pady=10)

#         self.populate_categories(self.controller.get_categories())

#     def populate_categories(self, categories):
#         self.category_combobox["values"] = categories

#     def populate_subcategories(self, event):
#         category = self.category_combobox.get()
#         subcategories = self.controller.get_subcategories(category)
#         self.subcategory_combobox["values"] = subcategories

#     def show_quiz_frame(self):
#         self.category_frame.pack_forget()
#         self.quiz_frame.pack(fill="both", expand=True)

#     def show_category_frame(self):
#         self.quiz_frame.pack_forget()
#         self.category_frame.pack(fill="both", expand=True)

#     def display_word(self, word):
#         self.word_label.config(text=word)
#         self.answer_entry.delete(0, tk.END)
#         self.feedback_label.config(text="")

#     def display_feedback(self, message, color):
#         self.feedback_label.config(text=message, foreground=color)