import tkinter as tk
import random

class DraggableWord(tk.Label):
    """
    Representa uma palavra arrastável na interface do jogo.
    Gerencia seu próprio estado de arrasto e interação visual.
    """
    def __init__(self, master, text, parent_app, is_correct_word=False, **kwargs):
        # Usando ttk.Label para melhor integração com temas
        super().__init__(master, text=text, bd=1, relief="raised",
                         padx=10, pady=5, font=("Segoe UI", 12, "bold"), cursor="hand2", **kwargs)
        
        self.word_text = text
        self.parent_app = parent_app  # Referência à instância da classe principal
        self.is_correct_word = is_correct_word # Flag para diferenciar palavras da frase de distratores
        
        # Cores de fundo diferenciadas para palavras corretas e distratores
        self.original_bg = "#E8F5E9" if is_correct_word else "#CFD8DC" # Verde claro para corretas, cinza azulado para distratores
        self.config(bg=self.original_bg, fg="#263238") # Cor do texto escura para contraste

        self._drag_start_x = 0
        self._drag_start_y = 0

        self.bind("<Button-1>", self._on_drag_start)
        self.bind("<B1-Motion>", self._on_drag_motion)
        self.bind("<ButtonRelease-1>", self._on_drag_release)

    def _on_drag_start(self, event):
        """Inicia o processo de arrasto, elevando a palavra e mudando seu visual."""
        self.lift()  # Traz a palavra para a frente
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self.config(relief="solid", bd=2) # Efeito visual de "levantado"

    def _on_drag_motion(self, event):
        """Move a palavra com o mouse, limitando o movimento à janela principal."""
        # Calcula a nova posição global da palavra
        x_root = self.winfo_rootx() + event.x - self._drag_start_x
        y_root = self.winfo_rooty() + event.y - self._drag_start_y

        # Converte a nova posição global para coordenadas relativas ao master atual
        # Isso permite que a palavra seja arrastada para fora do frame original
        x_new = x_root - self.master.winfo_rootx()
        y_new = y_root - self.master.winfo_rooty()

        # Garante que a palavra não saia completamente da janela principal (root)
        root_width = self.parent_app.root.winfo_width()
        root_height = self.parent_app.root.winfo_height()
        
        x_new_limited = max(0, min(x_new, root_width - self.winfo_width() - self.master.winfo_x()))
        y_new_limited = max(0, min(y_new, root_height - self.winfo_height() - self.master.winfo_y()))
        
        self.place(x=x_new_limited, y=y_new_limited)
        
        # Notifica o aplicativo pai para verificar colisões e destacar áreas
        self.parent_app.check_all_collisions()
        # self.parent_app.highlight_assembly_area_on_hover(self)

    def _on_drag_release(self, event):
        """Finaliza o arrasto, reseta o visual e faz verificações finais."""
        self.config(relief="raised", bd=1) # Volta ao relevo normal
        self.parent_app.check_all_collisions() # Verifica colisão final
        # self.parent_app.highlight_assembly_area_on_hover(self, reset=True) # Reseta o destaque da área de montagem
        
        # Se não houver colisão com outras palavras, reseta a cor para a original
        if not self.parent_app._is_colliding_with_any_other_word(self):
            self.config(bg=self.original_bg)
