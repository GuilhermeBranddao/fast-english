"""
Gerenciador da interface do usuário para o jogo de formação de frases.
"""

import tkinter as tk
from tkinter import ttk


class UIManager:
    """Gerencia todos os elementos da interface do usuário."""
    
    def __init__(self, root):
        self.root = root
        self._setup_styles()
        self._create_widgets()
        
        # Callbacks que serão definidos pela classe principal
        self.check_callback = None
        self.edit_callback = None

    def _setup_styles(self):
        """Configura estilos para widgets ttk para uma aparência moderna."""
        style = ttk.Style()
        style.theme_use('clam')

        # Estilos gerais
        style.configure('TFrame', background='#FFFFFF', borderwidth=0, relief="flat")
        style.configure('TLabel', background='#ECEFF1', font=("Segoe UI", 12), foreground="#333333")
        style.configure('Header.TLabel', font=("Segoe UI", 20, "bold"), foreground="#2C3E50", background="#ECEFF1")
        style.configure('SubHeader.TLabel', font=("Segoe UI", 14, "bold"), foreground="#444444", background="#ECEFF1")
        
        style.configure('Primary.TButton', font=("Segoe UI", 13, "bold"), padding=10, 
                        background="#3F51B5", foreground="white", relief="flat")
        style.map('Primary.TButton', background=[('active', '#303F9F')])
        
        style.configure('Secondary.TButton', font=("Segoe UI", 12), padding=10, 
                        background="#78909C", foreground="white", relief="flat")
        style.map('Secondary.TButton', background=[('active', '#607D8B')])

    def _create_widgets(self):
        """Cria e posiciona todos os widgets da interface do jogo."""
        # Título principal
        ttk.Label(self.root, text="Monte a Frase em Inglês!", style='Header.TLabel').place(relx=0.5, y=30, anchor="center")

        # Labels informativos
        self.portugues_label = ttk.Label(self.root, text="", font=("Segoe UI", 16, "italic"), 
                                       foreground="#555555", background="#ECEFF1")
        self.portugues_label.place(x=50, y=70)

        self.attempts_label = ttk.Label(self.root, text="Tentativas: 0", font=("Segoe UI", 12), 
                                      foreground="#607D8B", background="#ECEFF1")
        self.attempts_label.place(x=780, y=70)

        # Área de palavras disponíveis
        ttk.Label(self.root, text="Palavras disponíveis:", style='SubHeader.TLabel').place(x=50, y=120)
        self.words_pool_frame = ttk.Frame(self.root, width=850, height=400, relief="ridge", borderwidth=1)
        self.words_pool_frame.place(x=50, y=150)
        self.root.update_idletasks()

        self._create_assembly_area()
        self._create_buttons()

        # Label de resultado
        self.result_label = ttk.Label(self.root, text="", font=("Segoe UI", 18, "bold"), background="#ECEFF1")
        self.result_label.place(relx=0.5, y=540, anchor="center")

    def _create_assembly_area(self):
        """Cria a área de montagem da frase."""
        self.assembly_hint_label = ttk.Label(
            self.words_pool_frame, 
            text="Monte a frase aqui ↓",
            font=("Segoe UI", 12, "italic"),
            background="#FAFAFA",
            foreground="#777", 
            relief="ridge", 
            border=1,
            justify="center"
        )
        self.assembly_hint_label.place(x=50, y=230, width=700, height=100)

    def _create_buttons(self):
        """Cria os botões de ação."""
        self.check_button = ttk.Button(
            self.root, 
            text="Verificar Frase", 
            command=self._on_check_button_click,
            style='Primary.TButton'
        )
        self.check_button.place(x=300, y=580, width=150, height=50)

        self.edit_button = ttk.Button(
            self.root,
            text="✏️ Editar",
            command=self._on_edit_button_click,
            width=10
        )
        self.edit_button.place(x=500, y=580, width=120, height=50)

    def _on_check_button_click(self):
        """Callback para o botão de verificar."""
        if self.check_callback:
            self.check_callback()

    def _on_edit_button_click(self):
        """Callback para o botão de editar."""
        if self.edit_callback:
            self.edit_callback()

    def set_check_callback(self, callback):
        """Define o callback para o botão de verificar."""
        self.check_callback = callback

    def set_edit_callback(self, callback):
        """Define o callback para o botão de editar."""
        self.edit_callback = callback

    def update_portuguese_text(self, text):
        """Atualiza o texto em português."""
        self.portugues_label.config(text=f'Traduza: "{text}"')

    def update_attempts(self, attempts):
        """Atualiza o contador de tentativas."""
        self.attempts_label.config(text=f"Tentativas: {attempts}")

    def update_result(self, text, color):
        """Atualiza o resultado da verificação."""
        self.result_label.config(text=text, foreground=color)

    def clear_result(self):
        """Limpa o texto de resultado."""
        self.result_label.config(text="")

    def enable_check_button(self):
        """Habilita o botão de verificar."""
        self.check_button.config(state="normal")

    def disable_check_button(self):
        """Desabilita o botão de verificar."""
        self.check_button.config(state="disabled")

    def get_words_pool_frame(self):
        """Retorna o frame onde as palavras são posicionadas."""
        return self.words_pool_frame

    def get_assembly_area(self):
        """Retorna a área de montagem."""
        return self.assembly_hint_label