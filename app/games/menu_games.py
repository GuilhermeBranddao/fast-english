import tkinter as tk
from tkinter import ttk
from app.games.vocabulary_game.main import VocabularyGame
from app.games.game_color.main import ColorGame
from app.games.hangman_game.main import HangmanGame
from app.games.word_shuffle_game.main import WordShuffleGame 
from app.games.text_challenge.main import TextChallengeApp
from app.games.text_reader_app.main import TextReaderApp
from app.toolkit.utils.data_loader import DataLoader
import json
import os
from pathlib import Path
import numpy as np

from app.stats_words.analyzer import WordStatsAnalyzer, WordLearningAnalyzer

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
            ("Word Shuffle Game", WordShuffleGame),
            ("Text Reader App", TextReaderApp),
            ("Game Color", ColorGame),
            ("Desafio de Texto", TextChallengeApp),
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
        print("Iniciando PageMenuApapter")
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
        print(f"Exibindo frame: {name}")
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

class WordBaseApp(BasePage):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)

        self.data_path = os.path.join("database", "extract_data_video", "data", "extracted_data", "{kind}", "data_organize")
        self.save_path_study_word_list = os.path.join("database", "vocabulary", "study_word_list.json")
        self.current_type = "words"

        word_stats_analyzer = WordStatsAnalyzer(list_game_name=["game_data_hangman", "game_data_word_shuffle_game"])
        df = word_stats_analyzer.stats_grouped
        self.word_accuracy_map = dict(zip(df['word'].str.lower(), df['acuracia']))

        self.word_stats_analyzer = WordLearningAnalyzer(word_stats_analyzer.stats_grouped)

        self.data = self.build_data_structure()

        self.build_ui()

    def build_data_structure(self):
        data_structure = {}
        content_types = ["words", "phrases"]

        for content_type in content_types:
            loader = DataLoader(base_path=self.data_path.format(kind=content_type))
            content_data = {}

            for category in loader.get_categories():
                category_name = category.name
                category_data = {}

                for subcategory in loader.get_subcategories(category):
                    subcategory_name = subcategory.name

                    word_paths = [
                        Path(str(path).replace("\\", "/"))
                        for path in loader.get_word_paths(subcategory)
                    ]

                    category_data[subcategory_name] = word_paths

                content_data[category_name] = category_data

            data_structure[content_type] = content_data

        return data_structure

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
    
    def draw_progress_bar(self, parent, progress, height=10, background="#ddd", fill_color="#4caf50", padding=(0, 0)):
        """
        Cria uma barra de progresso dentro de um widget pai.

        Args:
            parent (tk.Widget): Widget onde a barra será inserida.
            progress (float): Progresso de 0 a 100.
            height (int): Altura da barra.
            background (str): Cor de fundo da barra.
            fill_color (str): Cor do preenchimento do progresso.
            padding (tuple): Padding vertical (topo, base).

        Returns:
            tk.Canvas: O canvas com a barra desenhada.
        """

        canvas = tk.Canvas(parent, height=height, bg=background, highlightthickness=0)
        canvas.pack(fill="x", pady=padding)

        # canvas.update_idletasks()  # Garante que canvas.winfo_width() funcione corretamente
        # width = canvas.winfo_reqwidth()
        # fill_width = width * (progress / 100)

        # canvas.create_rectangle(0, 0, fill_width, height, fill=fill_color, width=0)
        canvas.create_rectangle(0, 0, canvas.winfo_reqwidth() * progress / 100, 10, fill="#4caf50", width=0)
        
        return canvas

    def add_tooltip(self, widget, text):
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        label = tk.Label(tooltip, text=text, bg="lightyellow", relief="solid", borderwidth=1, font=("Helvetica", 9))
        label.pack()

        def enter(event):
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 20
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def leave(event):
            tooltip.withdraw()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def create_subcategory_box(self, parent, subcategory_name, word_list, category_name, all_maps):
        index = len(parent.winfo_children())
        sub_color = "#f9f9f9" if index % 2 == 0 else "#eeeeee"

        sub_frame = tk.Frame(parent, bg=sub_color, bd=1, relief="solid")
        sub_frame.pack(fill="x", pady=5)

        tk.Label(sub_frame, text=subcategory_name, font=("Helvetica", 12, "bold"),
                bg=sub_color, anchor="w").pack(anchor="w", padx=5, pady=(5, 0))

        # Progresso
        category_map = all_maps.get(category_name, {})
        sub_learned = category_map.get(subcategory_name, {}).get("learned", 0)
        sub_progress = (sub_learned / len(word_list)) * 100 if word_list else 0

        tk.Label(sub_frame, text=f"{sub_learned}/{len(word_list)} words", bg=sub_color,
                font=("Helvetica", 10), anchor="w").pack(anchor="w", padx=5)

        self.draw_progress_bar(parent=sub_frame, progress=sub_progress, padding=(0, 0))

        tk.Button(sub_frame, text="Study",
                command=lambda words=word_list: self.start_game(words)
                ).pack(pady=5, anchor="e", padx=5)

    def create_category_box(self, frame, category_name, subcats, category_color, all_maps, learned_per_category):
        # frame.pack(fill="x", padx=10, pady=5)

        # Frame principal da categoria
        frame_category = tk.Frame(frame, bg="white", bd=2, relief="groove")
        frame_category.pack(fill="x", padx=10, pady=10)

        # Quadrado branco com nome e info da categoria
        frame_header = tk.Frame(frame_category, bg=category_color, bd=5,)
        frame_header.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_header, text=category_name, font=("Helvetica", 14, "bold"), bg=category_color, anchor="w").pack(anchor="w")

        total_words = sum(len(words) for words in subcats.values())

        learned_words = learned_per_category.get(category_name, 0)  # Atualize com os dados reais futuramente

        label = tk.Label(frame_header, text=f"{learned_words}/{total_words} Words Learned", bg="white", font=("Helvetica", 10), anchor="w")#.pack(anchor="w")
        # label = tk.Label(frame_header, text=f"{learned_words}/{total_words} words learned")
        label.pack(anchor="w")
        self.add_tooltip(label, f"{total_words - learned_words} words remaining")

        # sub_progress = self.get_accuracy_for_words(word_list)
        # Barra de progresso da categoria
        progress = (learned_words / total_words) * 100 if total_words else 0

        self.draw_progress_bar(parent=frame_header, 
                                progress=progress, 
                                height=10, background="#ddd", fill_color="#4caf50", padding=(0, 0))

        # Subcategorias dentro da categoria (inicialmente ocultas)
        frame_subcategory = tk.Frame(frame_category, bg="white")


        def toggle_subcategories(frame=frame_subcategory, subcategory_dict=subcats, category_name=category_name):
            if frame.winfo_ismapped():
                frame.pack_forget()
            else:
                if not frame.winfo_children():
                    for subcategory_name, word_list in subcategory_dict.items():
                        self.create_subcategory_box(frame, subcategory_name, word_list, category_name, all_maps)
                frame.pack(fill="x", padx=10, pady=5)
                        
        # Botão de expandir/retrair subcategorias
        toggle_button = tk.Button(frame_header, text="Mostrar / Ocultar", cursor="hand2",
                                  command=toggle_subcategories)
        toggle_button.pack(anchor="e", pady=(5, 0))


    def setup_scrollable_category_area(self, parent_frame):
        canvas = tk.Canvas(parent_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.scroll_canvas = canvas
        self.scroll_frame = scroll_frame

    def draw_categories(self):
        # TODO: Colocar icones
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.setup_scrollable_category_area(parent_frame=self.content_frame)

        categories = self.data.get(self.current_type, {})

        category_colors = [
            "#FFC1C1", "#C1FFD7", "#C1D4FF", "#FFF5C1", "#E1C1FF", "#C1F0FF",
            "#A8D5BA",  # Verde menta
            "#F9E79F",  # Amarelo claro
            "#AED6F1",  # Azul bebê
            "#F5CBA7",  # Pêssego
            "#D7BDE2",  # Lavanda
            "#FADBD8",  # Rosa claro
            "#D5F5E3",  # Verde claro
            "#FDEBD0",  # Creme
            "#E8DAEF",  # Lilás
            "#F6DDCC",  # Bege
            "#D6EAF8",  # Azul claro
            "#FCF3CF",  # Amarelo pastel
            "#E5E8E8",  # Cinza claro
            "#FDEDEC",  # Rosa muito claro
            "#EBDEF0",  # Roxo claro
        ]

        all_maps, learned_per_category = self.word_stats_analyzer.generate_learning_maps(categories)
        
        for i, (category_name, subcats) in enumerate(categories.items()):

            category_color = category_colors[i % len(category_colors)]

            self.create_category_box(frame=self.scroll_frame,
                                    category_name=category_name,
                                    subcats=subcats,
                                    category_color=category_color,
                                    all_maps=all_maps,
                                    learned_per_category=learned_per_category)

    def start_game(self, words):

        loader = DataLoader(base_path=self.data_path.format(kind=self.current_type))

        ## Salvando lista de nomes
        study_word_list = [loader._carregar_palavra(path=Path(str(path).replace("\\", "/"))) for path in words]

        # Convert WindowsPath objects to strings in the study_word_list
        serializable_study_word_list = [
            {key: str(value) for key, value in word.items()}
            for word in study_word_list
        ]

        # Save the updated list to the JSON file
        with open(self.save_path_study_word_list, 'w', encoding="utf-8") as json_file:
            json.dump(serializable_study_word_list, json_file, ensure_ascii=False, indent=4)

        self.controller.show_frame("MainPage")

# Iniciar app
if __name__ == "__main__":
    try:
        root = tk.Tk()
        game = PageMenuApapter(root)
        game.pack(expand=True, fill="both")
        root.title("PageMenuApapter")
        root.geometry("840x520")
        root.mainloop()

    except Exception as e:
        print(f"Error {e}")
    finally:
        root.destroy()