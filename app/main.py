import tkinter as tk
from tkinter import ttk
from app.games.menu_games import PageMenuApapter
# Cores do tema
COR_FUNDO = "#f0f2f5"
COR_TOPO = "#4a7a8c"
COR_MENU = "#2c3e50"
COR_TEXTO = "#ffffff"

class Sidebar(tk.Frame):
    def __init__(self, parent, width_open=200, width_closed=50, bg_color="#f5f5f5", texts=[]):
        super().__init__(parent, bg=bg_color)
        self.width_open = width_open
        self.width_closed = width_closed
        self.is_open = True

        self.configure(width=self.width_open)
        self.pack_propagate(False)

        # Botão de alternar
        self.toggle_button = tk.Button(
            self,
            text="≡",
            command=self.toggle,
            bg="#dddddd",
            fg="#333333",
            bd=0,
            font=("Arial", 16),
            relief="flat",
            cursor="hand2"
        )
        self.toggle_button.pack(pady=10)

        # Área dos botões
        self.buttons_frame = tk.Frame(self, bg=bg_color)
        self.buttons_frame.pack(fill="both", expand=True)

        self.buttons = []


    def add_button(self, text, command):
        btn = tk.Button(
            self.buttons_frame,
            text=text,
            bg=COR_MENU,
            fg=COR_TEXTO,
            font=("Arial", 12),
            anchor="w",
            relief="flat",
            bd=0,
            padx=10,
            cursor="hand2",
            command=command
        )
        btn.pack(fill="x", pady=5)
        self.buttons.append(btn)

    def toggle(self):
        if self.is_open:
            self.configure(width=self.width_closed)
            for btn in self.buttons:
                btn.configure(text="")
        else:
            self.configure(width=self.width_open)
            texts = ["Início", "Jogos", "Relatórios", "Configurações"]
            for btn, text in zip(self.buttons, texts):
                btn.configure(text=text)

        self.is_open = not self.is_open


class FrameInicio(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COR_FUNDO)
        tk.Label(self, text="Bem-vindo ao sistema", font=("Helvetica", 14), bg=COR_FUNDO).pack(pady=30)

class FrameRelatorios(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COR_FUNDO)
        tk.Label(self, text="Relatórios disponíveis", font=("Helvetica", 14), bg=COR_FUNDO).pack(pady=30)


class FrameConfiguracoes(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COR_FUNDO)
        tk.Label(self, text="Configurações do Sistema", font=("Helvetica", 14), bg=COR_FUNDO).pack(pady=20)
        ttk.Entry(self).pack(pady=10)
        ttk.Button(self, text="Salvar").pack(pady=10)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema com Sidebar Recolhível")
        self.root.geometry("800x600")
        self.root.configure(bg=COR_FUNDO)

        self.frames = {}

        self.criar_topo()

        # Dicionário com os nomes e classes dos frames
        self.opcoes_frames = {
            "Início": FrameInicio,
            "Jogos": PageMenuApapter,
            "Relatórios": FrameRelatorios,
            "Configurações": FrameConfiguracoes
        }

        texts = self.opcoes_frames.keys()

        # Sidebar com toggle
        self.sidebar = Sidebar(root, 
                width_open=200, 
                width_closed=50, 
                bg_color=COR_MENU, 
                texts=texts)
        
        self.sidebar.pack(side="left", fill="y")

        self.sidebar.add_button("Início", lambda: self.mostrar_frame("Início"))
        self.sidebar.add_button("Jogos", lambda: self.mostrar_frame("Jogos"))
        self.sidebar.add_button("Relatórios", lambda: self.mostrar_frame("Relatórios"))
        self.sidebar.add_button("Configurações", lambda: self.mostrar_frame("Configurações"))

        # Conteúdo principal
        self.conteudo = tk.Frame(root, bg=COR_FUNDO)
        self.conteudo.pack(side="right", expand=True, fill="both")

        self.mostrar_frame("Início")

    def criar_topo(self):
        topo = tk.Frame(self.root, height=60, bg=COR_TOPO)
        topo.pack(side="top", fill="x")

        titulo = tk.Label(topo, text="Meu Sistema", bg=COR_TOPO, fg=COR_TEXTO,
                          font=("Helvetica", 18, "bold"))
        titulo.pack(pady=10)

    def mostrar_frame(self, nome):
        # Esconde todos os frames
        for frame in self.frames.values():
            frame.pack_forget()

        # Cria o frame se ainda não existir
        if nome not in self.frames:
            classe_frame = self.opcoes_frames[nome]
            self.frames[nome] = classe_frame(self.conteudo)

        # Exibe o frame desejado
        self.frames[nome].pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
