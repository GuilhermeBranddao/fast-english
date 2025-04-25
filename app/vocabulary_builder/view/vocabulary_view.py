import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import os

from app.vocabulary_builder.model.vocabulary_model import VocabularyModel
# from app.vocabulary_builder.view.vocabulary_view import VocabularyView
from app.vocabulary_builder.controller.vocabulary_controller import VocabularyController
from app.game_color.main import ColorGame

class Pagina(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

    def centralizar_widget(self, widget, rely):
        widget.place(relx=0.5, rely=rely, anchor=tk.CENTER)

class PaginaInicial(Pagina):
    def __init__(self, parent, controller):
        Pagina.__init__(self, parent, controller)

        label = tk.Label(self, text="Esta é a Página Inicial")
        self.centralizar_widget(label, 0.2)
        botao1 = tk.Button(self, text="Jogo Vocabulario", command=lambda: controller.mostrar_frame(PageGame))
        self.centralizar_widget(botao1, 0.5)
        
        botao2 = tk.Button(self, text="Ir para a Página 2", command=lambda: controller.mostrar_frame(Pagina2))
        botao2.place(relx=0.7, rely=0.5, anchor=tk.CENTER) # Exemplo sem centralizar

        botao_game_color = tk.Button(self, text="Game Color", command=lambda: controller.mostrar_frame(ColorGameView))
        botao_game_color.place(relx=0.7, rely=0.6, anchor=tk.CENTER) # Exemplo sem centralizar

        

class ColorGameView(Pagina):
    def __init__(self, parent, controller):
        Pagina.__init__(self, parent, controller)
        self.game = ColorGame(self)
        self.game.pack(expand=True, fill='both')

class PaginaComBotaoVoltar(Pagina):
    def __init__(self, parent, controller, texto_label):
        Pagina.__init__(self, parent, controller)
        label = tk.Label(self, text=texto_label)
        self.centralizar_widget(label, 0.2)
        botao_voltar = tk.Button(self, text="Voltar para a Inicial", command=lambda: controller.mostrar_frame(PaginaInicial))
        self.centralizar_widget(botao_voltar, 0.8)

class Pagina2(PaginaComBotaoVoltar):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Esta é a Página 2")

class PageGame(Pagina):
    def __init__(self, parent, controller):
        Pagina.__init__(self, parent, controller)
        self.controller = controller

        label_title = tk.Label(self, text="Seleção do Tipo de Jogo", font=("Arial", 16))
        self.centralizar_widget(label_title, 0.1)

        label_category = tk.Label(self, text="Escolha uma categoria:", font=("Arial", 14))
        self.centralizar_widget(label_category, 0.2)

        self.category_combobox = ttk.Combobox(self, state="readonly")
        self.centralizar_widget(self.category_combobox, 0.3)
        self.category_combobox["values"] = self.controller.vocabulary_model.list_categories() # Acessa o model
        self.category_combobox.bind("<<ComboboxSelected>>", self.populate_subcategories)

        label_subcategory = tk.Label(self, text="Escolha uma subcategoria:", font=("Arial", 14))
        self.centralizar_widget(label_subcategory, 0.4)

        self.subcategory_combobox = ttk.Combobox(self, state="readonly")
        self.centralizar_widget(self.subcategory_combobox, 0.5)
        self.subcategory_combobox["state"] = "disabled"

        start_button = tk.Button(self, text="Iniciar Jogo", command=self.start_game, font=("Arial", 12), state="disabled")
        self.centralizar_widget(start_button, 0.7)
        self.start_button = start_button

    def populate_subcategories(self, event):
        category = self.category_combobox.get()
        subcategories = self.controller.vocabulary_model.list_subcategories(category) # Acessa o model
        self.subcategory_combobox["values"] = subcategories
        self.subcategory_combobox["state"] = "readonly" if subcategories else "disabled"
        self.subcategory_combobox.set("")
        self.start_button["state"] = "disabled"
        self.subcategory_combobox.bind("<<ComboboxSelected>>", self.enable_start_button)

    def enable_start_button(self, event):
        if self.subcategory_combobox.get():
            self.start_button["state"] = "normal"
        else:
            self.start_button["state"] = "disabled"

    def start_game(self):
        selected_category = self.category_combobox.get()
        selected_subcategory = self.subcategory_combobox.get()
        if selected_category and selected_subcategory:
            print(f"Jogo iniciado com categoria: {selected_category}, subcategoria: {selected_subcategory}")
            # Inicia o quiz usando o controlador
            self.controller.vocabulary_controller.start_quiz(selected_category, selected_subcategory)
            self.controller.mostrar_frame(GameVocabulary, game_category=selected_category, game_subcategory=selected_subcategory)
        else:
            messagebox.showinfo("Seleção Inválida", "Por favor, escolha uma categoria e subcategoria.")

class GameVocabulary(Pagina):
    def __init__(self, parent, controller):
        Pagina.__init__(self, parent, controller)
        self.controller = controller

        self.label_image = tk.Label(self)
        # self.label_image.pack() # Ou use self.centralizar_widget se essa função estiver definida
        self.centralizar_widget(self.label_image, 0.25)
        self.displayed_image_tk = None

        self.word_label = tk.Label(self, text="", font=("Arial", 18, "bold"))
        self.centralizar_widget(self.word_label, 0.4)
        self.answer_entry = ttk.Entry(self, font=("Arial", 14))
        self.centralizar_widget(self.answer_entry, 0.5)
        self.feedback_label = ttk.Label(self, text="", font=("Arial", 12))
        self.centralizar_widget(self.feedback_label, 0.6)
        botao_confirmar = tk.Button(self, text="Confirmar", command=self.check_answer)
        botao_confirmar.place(relx=0.65, rely=0.7, anchor=tk.CENTER)
        botao_voltar_inicial = tk.Button(self, text="Voltar para Seleção", command=lambda: self.controller.mostrar_frame(PageGame))
        botao_voltar_inicial.place(relx=0.35, rely=0.7, anchor=tk.CENTER)
        self.category = None
        self.subcategory = None

    def load_game_content(self, category, subcategory):
        self.category = category
        self.subcategory = subcategory
        label_info = tk.Label(self, text=f"Vocabulário - Categoria: {self.category}, Subcategoria: {self.subcategory}", font=("Arial", 14))
        self.centralizar_widget(label_info, 0.1)
        self.controller.vocabulary_controller.view = self # Define a view no controlador
        self.next_word()

    def display_word(self, word):
        self.word_label.config(text=word)
        self.answer_entry.delete(0, tk.END)
        self.feedback_label.config(text="")
    
    def display_image(self, path_image):
        try:
            imagem_pil = Image.open(path_image)
            imagem_tk = ImageTk.PhotoImage(imagem_pil)
            self.label_image.config(image=imagem_tk)
            self.displayed_image_tk = imagem_tk # Guarde a referência
        except FileNotFoundError:
            print(f"Erro: Arquivo de imagem não encontrado em {path_image}")
            self.label_image.config(text="Imagem não encontrada")
        except Exception as e:
            print(f"Erro ao carregar a imagem: {e}")
            self.label_image.config(text=f"Erro ao carregar a imagem: {e}")

    def display_feedback(self, message, color):
        self.feedback_label.config(text=message, foreground=color)

    def check_answer(self):
        user_answer = self.answer_entry.get()
        self.controller.vocabulary_controller.check_answer(user_answer)

    def next_word(self):
        self.controller.vocabulary_controller.next_word()

class ControladorDePaginas(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Aplicação com Múltiplas Páginas")
        self.geometry('600x400')

        self.vocabulary_model = VocabularyModel()
        self.vocabulary_controller = VocabularyController(self, self.vocabulary_model)

        container = tk.Frame(self)
        container.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.frames = {}
        for F in (PaginaInicial, PageGame, Pagina2, GameVocabulary, ColorGameView):
            frame = F(container, self)
            self.frames[F] = frame
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.mostrar_frame(PaginaInicial)

    def mostrar_frame(self, pagina_classe, **kwargs):
        frame = self.frames[pagina_classe]
        frame.tkraise()
        if pagina_classe == GameVocabulary and kwargs:
            frame.load_game_content(kwargs['game_category'], kwargs['game_subcategory'])


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