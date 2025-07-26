"""
Detector de colisões para o jogo de formação de frases.
"""
import tkinter as tk

class CollisionDetector:
    """Gerencia a detecção de colisões entre palavras e áreas do jogo."""
    
    def __init__(self):
        self.assembly_area = None

    def set_assembly_area(self, assembly_area):
        """Define a área de montagem para verificação de colisões."""
        self.assembly_area = assembly_area

    def are_colliding(self, widget1, widget2):
        """
        Verifica se dois widgets estão colidindo usando suas coordenadas globais.
        """
        try:
            x1 = widget1.winfo_rootx()
            y1 = widget1.winfo_rooty()
            w1 = widget1.winfo_width()
            h1 = widget1.winfo_height()
            
            x2 = widget2.winfo_rootx()
            y2 = widget2.winfo_rooty()
            w2 = widget2.winfo_width()
            h2 = widget2.winfo_height()

            # Retorna True se houver sobreposição nos eixos X e Y
            return not (x1 + w1 < x2 or x1 > x2 + w2 or
                       y1 + h1 < y2 or y1 > y2 + h2)
        except tk.TclError:
            # Widget pode ter sido destruído
            return False

    def is_colliding_with_any_other_word(self, target_word, all_words):
        """Verifica se uma palavra específica está colidindo com qualquer outra palavra."""
        for word_data in all_words:
            other_word = word_data.get("word_box")
            if other_word != target_word and self.are_colliding(target_word, other_word):
                return True
        return False

    def check_all_collisions(self, all_words):
        """Verifica e atualiza as cores de todas as palavras baseadas em colisões."""
        for word_data in all_words:
            word_widget = word_data.get("word_box")
            if self.is_colliding_with_any_other_word(word_widget, all_words):
                word_widget.config(bg="red")
            else:
                word_widget.config(bg=word_widget.original_bg)

    def is_word_in_assembly_area(self, word_widget):
        """
        Verifica se uma palavra está significativamente dentro da área de montagem.
        Considera uma sobreposição de mais de 50% da área da palavra.
        """
        if not self.assembly_area:
            return False

        try:
            # Coordenadas da palavra no sistema de coordenadas do ROOT
            word_x1_root = word_widget.winfo_rootx()
            word_y1_root = word_widget.winfo_rooty()
            word_x2_root = word_x1_root + word_widget.winfo_width()
            word_y2_root = word_y1_root + word_widget.winfo_height()

            # Coordenadas da área de montagem no sistema de coordenadas do ROOT
            assembly_x1_root = self.assembly_area.winfo_rootx()
            assembly_y1_root = self.assembly_area.winfo_rooty()
            assembly_x2_root = assembly_x1_root + self.assembly_area.winfo_width()
            assembly_y2_root = assembly_y1_root + self.assembly_area.winfo_height()

            # Calcula a área de sobreposição
            overlap_x = max(0, min(word_x2_root, assembly_x2_root) - max(word_x1_root, assembly_x1_root))
            overlap_y = max(0, min(word_y2_root, assembly_y2_root) - max(word_y1_root, assembly_y1_root))
            
            word_area = word_widget.winfo_width() * word_widget.winfo_height()
            overlap_area = overlap_x * overlap_y

            # Considera a palavra "dentro" se mais de 50% de sua área estiver na área de montagem
            return word_area > 0 and (overlap_area / word_area) > 0.5
            
        except tk.TclError:
            # Widget pode ter sido destruído
            return False

    def get_words_in_order(self, words_in_area):
        """Ordena as palavras da esquerda para a direita baseado na posição X."""
        try:
            return sorted(words_in_area, key=lambda w: w.winfo_rootx())
        except tk.TclError:
            # Algum widget pode ter sido destruído
            return []