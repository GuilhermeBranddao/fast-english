from app.stats_words.analyzer import WordStatsAnalyzer
from app.toolkit import word_utils as utils
from app.games.drag_the_word.draggable_word import DraggableWord
import random
from tkinter import ttk, messagebox
from app.toolkit.mod_files.database_json_editor import DatabaseJsonEditor
import tkinter as tk

class DragWordGame(tk.Frame):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        """
        Classe principal da aplicação do jogo de formação de frases.
        Gerencia o estado do jogo, níveis, UI e lógica.
        """

        # self.parent = parent

    # def __init__(self, root):
        self.root = parent
        # self.root.title("Monte a Frase Correta!")
        # self.root.geometry("950x680") # Aumenta um pouco mais a janela
        # self.root.resizable(False, False) # Impede o redimensionamento para manter o layout
        # self.root.configure(bg="#ECEFF1") # Fundo cinza claro para a janela principal

        self.current_level = 0
        self.attempts = 0
        self.current_phrase_data = {}
        self.list_draggable_words = [] # Lista para manter referências a todas as palavras arrastáveis

        self.PHRASES = self.filter_words()

        self._setup_styles() # Configura estilos globais para ttk
        self._create_widgets() # Cria todos os elementos da interface
        self._load_level() # Carrega o primeiro nível do jogo

    def _setup_styles(self):
        """Configura estilos para widgets ttk para uma aparência moderna."""
        style = ttk.Style()
        style.theme_use('clam') # Um tema limpo e moderno

        # Estilos gerais para TFrame, TLabel e TButton
        style.configure('TFrame', background='#FFFFFF', borderwidth=0, relief="flat")
        style.configure('TLabel', background='#ECEFF1', font=("Segoe UI", 12), foreground="#333333")
        style.configure('Header.TLabel', font=("Segoe UI", 20, "bold"), foreground="#2C3E50", background="#ECEFF1")
        style.configure('SubHeader.TLabel', font=("Segoe UI", 14, "bold"), foreground="#444444", background="#ECEFF1")
        
        style.configure('Primary.TButton', font=("Segoe UI", 13, "bold"), padding=10, 
                        background="#3F51B5", foreground="white", relief="flat") # Azul primário
        style.map('Primary.TButton', background=[('active', '#303F9F')])
        
        style.configure('Secondary.TButton', font=("Segoe UI", 12), padding=10, 
                        background="#78909C", foreground="white", relief="flat") # Cinza secundário
        style.map('Secondary.TButton', background=[('active', '#607D8B')])

    def _create_widgets(self):
        """Cria e posiciona todos os widgets da interface do jogo."""
        
        # Título principal da aplicação
        ttk.Label(self.root, text="Monte a Frase em Inglês!", style='Header.TLabel').place(relx=0.5, y=30, anchor="center")


        # Rótulo da frase em português a ser traduzida
        self.portugues_label = ttk.Label(self.root, text="", font=("Segoe UI", 16, "italic"), foreground="#555555", background="#ECEFF1")
        self.portugues_label.place(x=50, y=70)

        # Rótulo de tentativas do usuário
        self.attempts_label = ttk.Label(self.root, text="Tentativas: 0", font=("Segoe UI", 12), foreground="#607D8B", background="#ECEFF1")
        self.attempts_label.place(x=780, y=70)

        # --- Área de Palavras Disponíveis (Pool) ---
        ttk.Label(self.root, text="Palavras disponíveis:", style='SubHeader.TLabel').place(x=50, y=120)
        self.words_pool_frame = ttk.Frame(self.root, width=850, height=400, relief="ridge", borderwidth=1)
        self.words_pool_frame.place(x=50, y=150)
        self.root.update_idletasks() # Garante que as dimensões do frame estejam prontas

        self.assembly_area_ui()

        # --- Botões de Ação ---
        self.check_button = ttk.Button(self.root, text="Verificar Frase", command=self._check_phrase_action, style='Primary.TButton')
        self.check_button.place(x=300, y=580, width=150, height=50)

        # self.reset_button = ttk.Button(self.root, text="Resetar", command=self._reset_level, style='Secondary.TButton')
        # self.reset_button.place(x=500, y=580, width=120, height=50)

        self.edit_button = ttk.Button(
            self.root,
            text="✏️ Editar",
            width=10,
        )
        self.edit_button.place(x=500, y=580, width=120, height=50)
        
        # --- Label de Resultado ---
        self.result_label = ttk.Label(self.root, text="", font=("Segoe UI", 18, "bold"), background="#ECEFF1")
        self.result_label.place(relx=0.5, y=540, anchor="center")

    def assembly_area_ui(self):
        # Rótulo de dica dentro da área de montagem
        self.assembly_hint_label = ttk.Label(self.words_pool_frame, text="Monte a frase aqui ↓",
                                       font=("Segoe UI", 12, "italic"),
                                       background="#FAFAFA",
                                       foreground="#777", 
                                       relief="ridge", 
                                       border=1,
                                       justify="center",
                                       )
        self.assembly_hint_label.place(x=50, y=230, width=700, height=100)
        # self.assembly_hint_label.pack(expand=True, fill="both") # Centraliza o hint no frame

    def filter_words(self, all_words=list[dict[str, str]]) -> list[dict[str, str]]:
        """
        Filtrar frases que tem mais de 3 palavras
        """
        all_words = utils.open_json('database/vocabulary/study_word_list.json')
        random.shuffle(all_words)
        filtered_words = []
        for word in all_words:
            if len(word['text_eng'].split()) > 3:
                word['text_eng'] = word['text_eng'].lower()
                filtered_words.append(word)
        return filtered_words

    def _load_level(self):
        """Carrega os dados da frase para o nível atual e inicializa o jogo."""
        if self.current_level >= len(self.PHRASES):
            messagebox.showinfo("Fim do Jogo", "Parabéns! Você completou todas as fases!")
            self.root.destroy()
            return

        self.dict_info_words = self.PHRASES[self.current_level]
        sentence = self.dict_info_words.get("text_eng", "")
        sentence = sentence.translate(str.maketrans('', '', ',.?!')).lower().split()
        self.correct_word_order = sentence
        self.distractors = []# ["apple", "my", "go", "run", "dog"]
        
        self.portugues_label.config(text=f"Traduza: \"{self.dict_info_words.get("text_pt_br", "")}\"")
        self.attempts = 0
        self.attempts_label.config(text=f"Tentativas: {self.attempts}")
        self.result_label.config(text="")
        self.check_button.config(state="normal") # Garante que o botão esteja habilitado para o novo nível
        
        self.id_game_task = utils.gerar_hash_id()
        self.edit_button.config(command=lambda: DatabaseJsonEditor(master=self.root, task_id=self.id_game_task, 
                                                                   task_list=self.dict_info_words))


        self._clear_words() # Remove palavras do nível anterior
        self._place_initial_words() # Posiciona as palavras do novo nível



    def _clear_words(self):
        """Destrói todas as palavras arrastáveis da tela."""
        for index, dict_draggable_words in enumerate(self.list_draggable_words):
            dict_draggable_words.get("word_box").destroy()
        
        self.list_draggable_words.clear()


    def _place_initial_words(self):
        """Posiciona as palavras arrastáveis inicialmente de forma organizada no pool."""
        all_words_for_level = self.correct_word_order + self.distractors
        random.shuffle(all_words_for_level)

        words_per_row = 7 # Quantas palavras por linha no pool
        x_offset = 20
        y_offset = 20
        word_spacing_x = 120 # Espaçamento horizontal entre palavras
        word_spacing_y = 60 # Espaçamento vertical entre linhas de palavras

        for i, word_text in enumerate(all_words_for_level):
            row = i // words_per_row
            col = i % words_per_row
            
            x = x_offset + col * word_spacing_x
            y = y_offset + row * word_spacing_y
            
            # Verifica se a palavra é da frase correta para passar a flag
            is_correct = word_text in self.correct_word_order
            
            word_box = DraggableWord(self.words_pool_frame, word_text, self)#, is_correct_word=is_correct)
            word_box.place(x=x, y=y)
            
            # Muda a cor de word_box para verde
            # word_box.config(bg= "#25BA33") # Verde para palavras corretas, cinza azulado para distratores
            
            self.list_draggable_words.append({"index":i, f"word_text": word_text, "is_correct": is_correct, "word_box":word_box})
            # print("Add: ", word_text, "is_correct:", is_correct)

    def _is_colliding_with_any_other_word(self, target_word):
        """Verifica se uma palavra específica está colidindo com qualquer outra palavra arrastável."""
        # Itera sobre todas as palavras arrastáveis gerenciadas pelo aplicativo

        for index, dict_draggable_words in enumerate(self.list_draggable_words):
            other_word = dict_draggable_words.get("word_box")
            if other_word != target_word and self._are_colliding(target_word, other_word):
                return True

        return False

    def check_all_collisions(self):
        """Verifica e atualiza as cores de todas as palavras baseadas em colisões."""
        for index, dict_draggable_words in enumerate(self.list_draggable_words):
            word_widget = dict_draggable_words.get("word_box")
            if self._is_colliding_with_any_other_word(word_widget):
                word_widget.config(bg="red")
            else:
                word_widget.config(bg=word_widget.original_bg)

    def _are_colliding(self, widget1, widget2):
        """
        Verifica se dois widgets estão colidindo usando suas coordenadas globais no root.
        Mais robusto, pois não depende do master dos widgets.
        """
        x1, y1, w1, h1 = widget1.winfo_rootx(), widget1.winfo_rooty(), widget1.winfo_width(), widget1.winfo_height()
        x2, y2, w2, h2 = widget2.winfo_rootx(), widget2.winfo_rooty(), widget2.winfo_width(), widget2.winfo_height()

        # Retorna True se houver sobreposição nos eixos X e Y
        return not (x1 + w1 < x2 or x1 > x2 + w2 or
                    y1 + h1 < y2 or y1 > y2 + h2)

    def _is_word_in_assembly_area(self, word_widget):
        """
        Verifica se uma palavra está significativamente dentro da área de montagem,
        considerando uma sobreposição de mais de 50% da área da palavra.
        """
        # Coordenadas da palavra no sistema de coordenadas do ROOT
        word_x1_root = word_widget.winfo_rootx()
        word_y1_root = word_widget.winfo_rooty()
        word_x2_root = word_x1_root + word_widget.winfo_width()
        word_y2_root = word_y1_root + word_widget.winfo_height()

        # Coordenadas da área de montagem no sistema de coordenadas do ROOT
        assembly_x1_root = self.assembly_hint_label.winfo_rootx()
        assembly_y1_root = self.assembly_hint_label.winfo_rooty()
        assembly_x2_root = assembly_x1_root + self.assembly_hint_label.winfo_width()
        assembly_y2_root = assembly_y1_root + self.assembly_hint_label.winfo_height()

        # Calcula a área de sobreposição
        overlap_x = max(0, min(word_x2_root, assembly_x2_root) - max(word_x1_root, assembly_x1_root))
        overlap_y = max(0, min(word_y2_root, assembly_y2_root) - max(word_y1_root, assembly_y1_root))
        
        word_area = word_widget.winfo_width() * word_widget.winfo_height()
        overlap_area = overlap_x * overlap_y

        # Considera a palavra "dentro" se mais de 50% de sua área estiver na área de montagem
        return word_area > 0 and (overlap_area / word_area) > 0.5

    def _check_phrase_action(self):
        """Ação executada ao clicar no botão 'Verificar Frase'."""
        self.attempts += 1
        self.attempts_label.config(text=f"Tentativas: {self.attempts}")

        # Coleta apenas as palavras que estão na área de montagem
        assembled_words = []
        for index, dict_draggable_words in enumerate(self.list_draggable_words):
            word_widget = dict_draggable_words.get("word_box")
            if self._is_word_in_assembly_area(word_widget):
                assembled_words.append(word_widget)

        # Ordena as palavras pela posição X (da esquerda para a direita)
        assembled_words.sort(key=lambda w: w.winfo_rootx())
        current_phrase = [word.word_text for word in assembled_words]

        if current_phrase == self.correct_word_order:
            self.result_label.config(text="✅ Correto! Parabéns!", foreground="#28A745") # Verde de sucesso
            self.check_button.config(state="disabled") # Desabilita o botão para evitar cliques repetidos
            messagebox.showinfo("Parabéns!", "Você montou a frase corretamente!")
            self.root.after(1500, self._next_level) # Espera um pouco e carrega o próximo nível
        else:
            self.result_label.config(text="❌ Incorreto! Tente novamente.", foreground="#DC3545") # Vermelho de erro

        
        self.verify_match_word(frase_esperada=self.correct_word_order, 
                               frase_montada=assembled_words)
    
        print(f"Nível: {self.current_level + 1} | Tentativas: {self.attempts}")
        print("Frase esperada:", self.correct_word_order)
        print("Frase montada:", current_phrase)
        print("-" * 40)


    def verify_match_word(self, frase_esperada, frase_montada):
        """
        Verifica se a frase montada corresponde à frase esperada.
        Se corresponder, retorna True e exibe uma mensagem de sucesso.
        Se não corresponder, retorna False e exibe uma mensagem de erro.
        """
        for index, word in enumerate(frase_esperada):
            if len(frase_montada)-1 >= index:
                if frase_montada[index].word_text == frase_esperada[index]:
                    frase_montada[index].config(bg="#25BA33")
                    continue

                elif frase_montada[index].word_text in frase_esperada:
                    frase_montada[index].config(bg="#f5c71a")
                    continue

            # print("Incorreto. Tente novamente.")
            # frase_montada.append(frase_esperada[index]) # Simula a adição de uma palavra correta
            frase_montada[index].config(bg="#BF1D12") # f5c71a BF1D12



    def _reset_level(self):
        """Reseta o nível atual, embaralhando e recolocando as palavras."""
        confirm = messagebox.askyesno("Resetar Nível", "Tem certeza que deseja resetar este nível?")
        if confirm:
            self.attempts = 0
            self.attempts_label.config(text=f"Tentativas: {self.attempts}")
            self.result_label.config(text="")
            self.check_button.config(state="normal") # Habilita o botão
            self._clear_words() # Remove as palavras existentes
            self._place_initial_words() # Posiciona novas palavras embaralhadas

    def _next_level(self):
        """Avança para o próximo nível do jogo."""
        self.current_level += 1
        self._load_level() # Carrega os dados do próximo nível

# Bloco principal de execução do aplicativo
if __name__ == "__main__":
    root = tk.Tk()
    app = DragWordGame(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        root = tk.Tk()
        game = DragWordGame(root)
        game.pack(expand=True, fill="both")
        root.title("Word Shuffle Game")
        root.geometry("840x520")
        root.mainloop()

    except Exception as e:
        print(f"Error {e}")
        root.destroy()
