import tkinter as tk
from tkinter import messagebox
import random
import nltk
from nltk.corpus import words

# Garante que o corpus 'words' esteja disponível
try:
    WORD_LIST = words.words()
except LookupError:
    nltk.download('words')
    WORD_LIST = words.words()

# Frases do desafio
PHRASES = [
    "listen to the radio",
    "feed the cat",
    "have a break",
    "catch the bus",
    "cook dinner"
]

class TextChallengeApp(tk.Frame):
    def __init__(self, parent=None, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.parent = parent

        self.configure(bg="#f0f0f0")

        random.shuffle(PHRASES)  # Embaralha frases a cada execução

        self.phrase_labels = []
        self.create_widgets()
        self.bind_events()

    def create_widgets(self):
        title = tk.Label(
            self,
            text="Use todas as frases abaixo no seu texto (exatamente como estão):",
            font=("Arial", 14, "bold"),
            bg="#f0f0f0"
        )
        title.pack(pady=15)

        for phrase in PHRASES:
            label = tk.Label(self, text=phrase, font=("Arial", 12), fg="gray", bg="#f0f0f0")
            label.pack()
            self.phrase_labels.append(label)

        self.text_box = tk.Text(self, height=12, width=70, font=("Arial", 12))
        self.text_box.pack(pady=20)

    def bind_events(self):
        self.text_box.bind("<space>", self.on_space_press)
        self.text_box.bind("<KeyRelease-Return>", self.on_space_press)  # também ao apertar Enter

    def on_space_press(self, event=None):
        self.update_phrase_colors()
        self.highlight_misspelled_words()

    def update_phrase_colors(self):
        user_text = self.text_box.get("1.0", tk.END).lower()
        for label, phrase in zip(self.phrase_labels, PHRASES):
            label.config(fg="green" if phrase in user_text else "gray")

    def highlight_misspelled_words(self):
        self.text_box.tag_remove("misspelled", "1.0", tk.END)
        words_in_text = self.text_box.get("1.0", tk.END).lower().split()

        misspelled_words = {word for word in words_in_text if not self.is_correct_spelling(word)}

        for word in misspelled_words:
            start_idx = "1.0"
            while True:
                start_idx = self.text_box.search(word, start_idx, nocase=True, stopindex=tk.END)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(word)}c"
                self.text_box.tag_add("misspelled", start_idx, end_idx)
                start_idx = end_idx

        self.text_box.tag_config("misspelled", foreground="red")

    @staticmethod
    def is_correct_spelling(word):
        return word.isalpha() and word.lower() in WORD_LIST

# # # Inicializa o jogo
# if __name__ == "__main__":
#     root = tk.Tk()
#     root.title("Desafio de Texto")
#     game = TextChallengeApp(root)
#     game.pack(expand=True, fill='both')
#     root.geometry("700x600")
#     root.mainloop()
