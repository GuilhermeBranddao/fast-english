"""
Arquivo principal da aplicação do jogo de formação de frases.
"""

import tkinter as tk
from app.games.drag_the_word.game_logic import GameLogic
from app.games.drag_the_word.ui_manager import UIManager
from app.games.drag_the_word.word_manager import WordManager
from app.games.drag_the_word.collision_detector import CollisionDetector


class LanguageGameApp(tk.Frame):
    """
    Classe principal da aplicação do jogo de formação de frases.
    Coordena os diferentes componentes do jogo.
    """

    def __init__(self, root):
        self.root = root
        self._setup_window()
        
        # Inicializa os componentes principais
        self.ui_manager = UIManager(self.root)
        self.word_manager = WordManager()
        self.collision_detector = CollisionDetector()
        self.game_logic = GameLogic(
            ui_manager=self.ui_manager,
            word_manager=self.word_manager,
            collision_detector=self.collision_detector
        )
        
        # Conecta os callbacks da UI com a lógica do jogo
        self._connect_ui_callbacks()
        
        # Inicia o primeiro nível
        self.game_logic.load_level()

    def _setup_window(self):
        """Configura a janela principal da aplicação."""
        self.root.title("Monte a Frase Correta!")
        self.root.geometry("950x680")
        self.root.resizable(False, False)
        self.root.configure(bg="#ECEFF1")

    def _connect_ui_callbacks(self):
        """Conecta os callbacks da interface com a lógica do jogo."""
        self.ui_manager.set_check_callback(self.game_logic.check_phrase_action)
        self.ui_manager.set_edit_callback(self.game_logic.edit_button_action)


def main():
    """Função principal de execução da aplicação."""
    try:
        root = tk.Tk()
        app = LanguageGameApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Erro na execução: {e}")
        if 'root' in locals():
            root.destroy()


if __name__ == "__main__":
    main()