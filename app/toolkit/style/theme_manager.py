class ThemeManager:
    def __init__(self, root, default_theme="dark"):
        self.root = root
        self.themes = {
            "light": {
                "bg": "#f9f9f9",
                "fg": "#222222",
                "btn_bg": "#e0e0e0",
                "btn_fg": "#000000",
                "accent": "#007acc",
                "emoji": "🌙",
                "label": "Modo Claro",
                "btn_label": "Ativar Modo Escuro"
            },
            "dark": {
                "bg": "#1e1e1e",
                "fg": "#ffffff",
                "btn_bg": "#2d2d2d",
                "btn_fg": "#ffffff",
                "accent": "#3794ff",
                "emoji": "☀️",
                "label": "Modo Escuro",
                "btn_label": "Ativar Modo Claro"
            }
        }
        self.current_theme = default_theme
        self.widget_registry = []  # Lista de tuplas (widget, tipo)
        self.apply_root_theme()
    
    def refresh(self):
        self.apply_root_theme()
        self.apply_all()

    def get_theme_data(self):
        return self.themes[self.current_theme]

    def apply_theme(self, widget):
        theme = self.get_theme_data()
        cls = widget.__class__.__name__

        if cls == "Label":
            widget.config(bg=theme["bg"], fg=theme["fg"])
        elif cls == "Button":
            widget.config(
                bg=theme["btn_bg"],
                fg=theme["btn_fg"],
                activebackground=theme["btn_bg"],
                activeforeground=theme["accent"]
            )
        elif cls == "Frame":
            widget.config(bg=theme["bg"])

    def apply_all(self):
        self._apply_recursive(self.root)

    def _apply_recursive(self, widget):
        self.apply_theme(widget)
        for child in widget.winfo_children():
            self._apply_recursive(child)

    def register(self, widget, widget_type):
        self.widget_registry.append((widget, widget_type))
        self.apply_theme(widget) 


    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_root_theme()
        self.apply_all()

    # def get_theme_data(self):
        # return self.themes[self.current_theme]

    def apply_root_theme(self):
        theme = self.get_theme_data()
        self.root.configure(bg=theme["bg"])

    # def apply_theme(self, widget, widget_type):
    #     theme = self.get_theme_data()
    #     if widget_type == "label":
    #         widget.config(bg=theme["bg"], fg=theme["fg"])
    #     elif widget_type == "button":
    #         widget.config(
    #             bg=theme["btn_bg"],
    #             fg=theme["btn_fg"],
    #             activebackground=theme["btn_bg"],
    #             activeforeground=theme["accent"]
    #         )
    #     else:
    #         pass  # outros tipos no futuro

    # def apply_all(self):
    #     for widget, widget_type in self.widget_registry:
    #         self.apply_theme(widget, widget_type)
