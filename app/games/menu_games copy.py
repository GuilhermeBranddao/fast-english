import tkinter as tk
from tkinter import messagebox
from app.games.vocabulary_game.main import VocabularyGame
from app.games.game_color.main import ColorGame
from app.games.hangman_game.main import HangmanGame
from app.games.text_challenge.main import TextChallengeApp



class WordBaseApp(tk.Frame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)

        self.current_type = "words"
        self.data = {
            "words": {
                "Casa": {
                    "Partes": ["porta", "janela", "telhado"],
                    "Cômodos": ["sala", "quarto", "cozinha"]
                },
                "Trabalho": {
                    "Profissões": ["engenheiro", "professor"]
                }
            },
            "phrases": {
                "Saudações": {
                    "Informal": ["Oi!", "E aí?"],
                    "Formal": ["Bom dia", "Como vai?"]
                }
            }
        }

        self.build_ui()

    def build_ui(self):
        # Limpa tudo
        for widget in self.winfo_children():
            widget.destroy()

        # Topo: Botões de tipo
        top_frame = tk.Frame(self)
        top_frame.pack(pady=10)

        words_btn = tk.Button(top_frame, text="Palavras", command=lambda: self.switch_type("words"))
        words_btn.pack(side="left", padx=5)

        phrases_btn = tk.Button(top_frame, text="Frases", command=lambda: self.switch_type("phrases"))
        phrases_btn.pack(side="left", padx=5)

        # Área de conteúdo
        self.content_frame = tk.Frame(self)
        self.content_frame.pack(fill="both", expand=True, pady=10)

        self.draw_categories()

    def switch_type(self, type_name):
        self.current_type = type_name
        self.draw_categories()

    def draw_categories(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        categories = self.data.get(self.current_type, {})

        for category, subcats in categories.items():
            cat_frame = tk.Frame(self.content_frame)
            cat_frame.pack(fill="x", padx=10, pady=5)

            is_expanded = tk.BooleanVar(value=False)

            def toggle(sub_frame=subcats, var=is_expanded, master=cat_frame, cat_name=category):
                if var.get():
                    for widget in master.winfo_children()[1:]:
                        widget.destroy()
                    var.set(False)
                else:
                    for sub, items in sub_frame.items():
                        sub_btn = tk.Button(
                            master,
                            text=f"   {sub}",
                            anchor="w",
                            command=lambda sub=sub, items=items: self.show_word_list(category=cat_name, subcategory=sub, words=items)
                        )
                        sub_btn.pack(fill="x")
                    var.set(True)

            btn = tk.Button(cat_frame, text=category, anchor="w", command=toggle)
            btn.pack(fill="x")

    def show_word_list(self, category, subcategory, words):
        # Limpa conteúdo

        
        for widget in self.winfo_children():
            widget.destroy()

        # Botão voltar
        back_btn = tk.Button(self, text="Voltar", command=self.build_ui)
        back_btn.pack(pady=10)


        # Título
        title = tk.Label(self, text=f"{self.current_type.title()} - {category} > {subcategory}", font=("Arial", 16))
        title.pack(pady=5)

        # Lista de palavras
        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, pady=10)

        for word in words:
            word_label = tk.Label(list_frame, text=word, anchor="w")
            word_label.pack(fill="x", padx=20, pady=2)



class BasePage(tk.Frame):
    """Classe base para todas as páginas com métodos comuns."""

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller

    def centralize_widget(self, widget, rely):
        """Centraliza um widget verticalmente."""
        widget.place(relx=0.5, rely=rely, anchor=tk.CENTER)

    def add_back_button(self, text="Voltar para a Inicial"):
        """Adiciona um botão para voltar à página inicial."""
        back_button = tk.Button(self, text=text, command=lambda: self.controller.show_frame("MainPage"))
        self.centralize_widget(back_button, 0.85)

    def add_stats_view(self):
        pass


class MainPage(BasePage):
    """Página inicial contendo o menu principal."""

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)

        # Título do menu principal
        title_label = tk.Label(self, text="Menu Principal", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        # Lista de botões e páginas correspondentes
        games = [
            ("Jogo de Vocabulário", VocabularyGame),
            ("Jogo Da Forca", HangmanGame),
            ("Game Color", ColorGame),
            ("Desafio de Texto", TextChallengeApp)
        ]

        # Criação dinâmica de botões
        for game_name, game_class in games:
            button = tk.Button(self, text=game_name, width=25, height=2,
                               command=lambda g=game_class: controller.show_game_frame(g))
            button.pack(pady=10)

        # Botão adicional
        other_button = tk.Button(self, text="Ir para a Página 2", width=25, height=2,
                                  command=lambda: controller.show_frame("PageTwo"))
        other_button.pack(pady=10)


class GamePage(BasePage):
    """Página genérica para carregar jogos dinamicamente."""

    def __init__(self, parent, controller, game_class, **kwargs):
        super().__init__(parent, controller, **kwargs)
        self.game_instance = None
        self.game_class = game_class

    def load_game(self):
        """Carrega e exibe o jogo apenas quando necessário."""
        if not self.game_instance:
            self.game_instance = self.game_class(self)
            self.game_instance.pack(expand=True, fill="both")
            self.add_back_button()

            # Estatisticas
            # # Divisão da interface em dois frames
            # self.game_frame = tk.Frame(self, bg="#ffffff")  # Área do jogo com fundo branco
            # self.stats_frame = tk.Frame(self, bg="#2c3e50", width=220, relief="raised", bd=2)  # Estatísticas com bordas

            # title_label = tk.Label(
            #     self.stats_frame, text="Estatísticas", font=("Helvetica", 16, "bold"),
            #     bg="#34495e", fg="#ecf0f1", pady=10
            # )
            # title_label.pack(pady=10, fill="x")


class PageTwo(BasePage):
    """Página adicional de exemplo."""

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        label = tk.Label(self, text="Esta é a Página 2", font=("Arial", 14))
        self.centralize_widget(label, 0.4)
        self.add_back_button()

class PageMenuApapter(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.title("Aplicação com Múltiplas Páginas")
        # self.geometry('700x500')

        # Container para armazenar frames
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Dicionário para páginas
        self.frames = {}
        self.games = {}

        # Registra a página inicial e a página adicional
        
        # self.register_frame("BaseApp", WordBaseApp)
        self.register_frame("MainPage", WordBaseApp)

        # self.register_frame("MainPage", MainPage)
        self.register_frame("PageTwo", PageTwo)

        # Exibe a página inicial
        self.show_frame("MainPage")

    def register_frame(self, name, page_class):
        """Registra um frame."""
        frame = page_class(self.container, self)
        self.frames[name] = frame
        frame.place(relwidth=1, relheight=1)

    def register_game_frame(self, game_class):
        """Registra dinamicamente páginas de jogos."""
        if game_class not in self.games:
            frame = GamePage(self.container, self, game_class)
            self.games[game_class] = frame
            frame.place(relwidth=1, relheight=1)

    def show_frame(self, name):
        """Exibe a página pelo nome."""
        frame = self.frames[name]
        frame.tkraise()

    def show_game_frame(self, game_class):
        """Exibe uma página de jogo dinamicamente."""
        if game_class not in self.games:
            self.register_game_frame(game_class)
        self.games[game_class].tkraise()
        self.games[game_class].load_game()



class PageController(tk.Tk):
    """Gerenciador principal para alternar entre páginas."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Aplicação com Múltiplas Páginas")
        self.geometry('700x500')

        # Container para armazenar frames
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Dicionário para páginas
        self.frames = {}
        self.games = {}

        # Registra a página inicial e a página adicional
        self.register_frame("MainPage", MainPage)
        self.register_frame("PageTwo", PageTwo)

        # Exibe a página inicial
        self.show_frame("MainPage")

    def register_frame(self, name, page_class):
        """Registra um frame."""
        frame = page_class(self.container, self)
        self.frames[name] = frame
        frame.place(relwidth=1, relheight=1)

    def register_game_frame(self, game_class):
        """Registra dinamicamente páginas de jogos."""
        if game_class not in self.games:
            frame = GamePage(self.container, self, game_class)
            self.games[game_class] = frame
            frame.place(relwidth=1, relheight=1)

    def show_frame(self, name):
        """Exibe a página pelo nome."""
        frame = self.frames[name]
        frame.tkraise()

    def show_game_frame(self, game_class):
        """Exibe uma página de jogo dinamicamente."""
        if game_class not in self.games:
            self.register_game_frame(game_class)
        self.games[game_class].tkraise()
        self.games[game_class].load_game()


# if __name__ == "__main__":
#     app = PageController()
#     app.mainloop()

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = PageApapter(root)
#     root.mainloop()