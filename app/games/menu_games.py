import tkinter as tk
from app.games.vocabulary_game.main import VocabularyGame
from app.games.game_color.main import ColorGame
from app.games.hangman_game.main import HangmanGame
from app.games.text_challenge.main import TextChallengeApp
from app.utils.data_loader import DataLoader
import json
import os
from pathlib import Path


class BasePage(tk.Frame):
    """Classe base para todas as páginas com métodos comuns."""
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        self.controller = controller

    def centralize_widget(self, widget, rely):
        """Centraliza um widget verticalmente."""
        widget.place(relx=0.5, rely=rely, anchor=tk.CENTER)

    def add_back_button(self, text="Voltar para a Inicial"):
        """Adiciona um botão para voltar à página inicial."""
        back_button = tk.Button(self, text=text, command=lambda: self.controller.show_frame("WordBaseApp"))
        self.centralize_widget(back_button, 0.85)

    def add_stats_view(self):
        pass


class WordBaseApp(BasePage):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)

        self.data_path = os.path.join("database", "extract_data_video", "data", "extracted_data", "{kind}", "data_organize")
        self.save_path_study_word_list = os.path.join("database", "vocabulary", "study_word_list.json")
        self.current_type = "words"

        self.data = self.create_estructure()

        self.build_ui()

    def create_estructure(self):
        estrutura = {}
        list_kinds = ["words", "phrases"]
        for kind in list_kinds:
            self.loader = DataLoader(base_path=self.data_path.format(kind=kind))
            estrutura[kind] = {}
            for categoria in self.loader.get_categories():
                estrutura[kind][categoria.name] = {}
                for subcat in self.loader.get_subcategories(categoria):
                    estrutura[kind][categoria.name][subcat.name] = []
                    for word_path in self.loader.get_word_paths(subcat):
                        estrutura[kind][categoria.name][subcat.name].append(word_path)
        return estrutura

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

        database_words_btn = tk.Button(top_frame, text="Database", command=lambda: self.switch_type("database"))
        database_words_btn.pack(side="left", padx=5)

        # Área de conteúdo
        self.content_frame = tk.Frame(self)
        self.content_frame.pack(fill="both", expand=True, pady=10)

        self.draw_categories()

    def switch_type(self, type_name):
        self.current_type = type_name

        if type_name == "database":
            # Caminho da pasta com os arquivos
            folder = Path(os.path.join("database", "vocabulary", "save_words"))
            if not folder.exists():
                folder.mkdir(parents=True)

            # Lista arquivos .json
            self.database_files = list(folder.glob("*.json"))
            
            # Chama função que desenha os botões dos arquivos
            self.draw_database_files()
            return

        self.draw_categories()
    
    def draw_database_files(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if not self.database_files:
            label = tk.Label(self.content_frame, text="Nenhum banco de dados encontrado.")
            label.pack(pady=10)
            return

        label = tk.Label(self.content_frame, text="Escolha um banco de dados:")
        label.pack(pady=10)

        for file_path in self.database_files:
            data = self.load_database_file(file_path)
            btn = tk.Button(
                self.content_frame,
                text=file_path.stem,  # Nome do arquivo sem extensão
                anchor="w",
                # command=lambda path=file_path: self.load_database_file(path)
                command=lambda items=data: self.start_game(words=items)
            )
            btn.pack(fill="x", padx=10, pady=2)

    def load_database_file(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Aqui você pode usar os dados como quiser. Exemplo:
        self.loaded_words = data
        return data
        # print(f"Arquivo {path.name} carregado com sucesso!")
        # ou: self.start_game(category="database", subcategory=path.stem, words=data)

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
                            command=lambda items=items: self.start_game(words=items)
                            # command=lambda: self.controller.show_frame("MainPage")
                        )
                        sub_btn.pack(fill="x")
                    var.set(True)

            btn = tk.Button(cat_frame, text=category, anchor="w", command=toggle)
            btn.pack(fill="x")

    def start_game(self, words):
        # Limpa conteúdo
        # for widget in self.content_frame.winfo_children():
        #     widget.destroy()

        # Botão voltar
        # back_btn = tk.Button(self, text="Voltar", command=self.build_ui)
        # back_btn.pack(pady=10)

        ## Salvando lista de nomes
        study_word_list = [self.loader._carregar_palavra(path=Path(path.replace("\\", "/"))) for path in words]

        # Convert WindowsPath objects to strings in the study_word_list
        serializable_study_word_list = [
            {key: str(value) for key, value in word.items()}
            for word in study_word_list
        ]

        # Save the updated list to the JSON file
        with open(self.save_path_study_word_list, 'w', encoding="utf-8") as json_file:
            json.dump(serializable_study_word_list, json_file, ensure_ascii=False, indent=4)


        self.controller.show_frame("MainPage")


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
        self.register_frame("WordBaseApp", WordBaseApp)

        self.register_frame("MainPage", MainPage)
        self.register_frame("PageTwo", PageTwo)

        # Exibe a página inicial
        self.show_frame("WordBaseApp")

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
    
    def reset_game(self):
        """Reinicia o jogo atual."""
        if self.game_instance:
            self.game_instance.reset_game()

    def show_game_frame(self, game_class):
        """Exibe uma página de jogo dinamicamente, resetando sempre."""
        if game_class not in self.games:
            self.register_game_frame(game_class)
        else:
            # Destroi o frame anterior e recria do zero
            self.games[game_class].destroy()
            frame = GamePage(self.container, self, game_class)
            self.games[game_class] = frame
            frame.place(relwidth=1, relheight=1)
        
        self.games[game_class].tkraise()
        self.games[game_class].load_game()

