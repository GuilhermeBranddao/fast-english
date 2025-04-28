import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import random
import json
from deep_translator import GoogleTranslator

TITLE_FONT = ("Arial", 20)
LABEL_FONT = ("Arial", 14)
SMALL_FONT = ("Arial", 12)

class HangmanGame(tk.Frame):
    MAX_ATTEMPTS = 6
    WORD_FILE = "database/vocabulary_json/describing_things/adjectives.json"

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        self.words = self.load_words()
        self.reset_game_vars()
        self.setup_ui()

    def load_words(self):
        try:
            with open(self.WORD_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return list(data.values())
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Failed to load words: {e}")
            self.parent.destroy()

    def reset_game_vars(self):
        self.word = random.choice(self.words).upper()
        self.word_translate = self.translate_sentence(self.word)
        # self.guessed_word = ["_"] * len(self.word)
        self.guessed_word = [" " if char == " " else "_" for char in self.word]

        self.remaining_attempts = self.MAX_ATTEMPTS
        self.guessed_letters = set()

    def setup_ui(self):
        self.word_label = tk.Label(self, text=" ".join(self.guessed_word), font=TITLE_FONT)
        self.word_label.pack(pady=20)

        self.attempts_label = tk.Label(self, text=f"Remaining Attempts: {self.remaining_attempts}", font=LABEL_FONT)
        self.attempts_label.pack(pady=10)

        self.input_frame = tk.Frame(self)
        self.input_frame.pack(pady=10)

        tk.Label(self.input_frame, text="Enter a letter:", font=SMALL_FONT).pack(side="left", padx=5)
        self.letter_entry = tk.Entry(self.input_frame, width=5, font=LABEL_FONT)
        self.letter_entry.pack(side="left", padx=5)

        self.guess_button = tk.Button(self.input_frame, text="Guess", command=self.check_guess)
        self.guess_button.pack(side="left", padx=5)

        self.guessed_label = tk.Label(self, text="Guessed Letters: ", font=SMALL_FONT)
        self.guessed_label.pack(pady=10)

        self.word_translate_label = tk.Label(self, text=f"Hint: {self.word_translate.capitalize()}", font=SMALL_FONT)
        self.word_translate_label.pack(pady=10)

    def check_guess(self):
        input_text = self.letter_entry.get().strip().upper()
        self.letter_entry.delete(0, tk.END)

        if not input_text.isalpha():
            messagebox.showwarning("Invalid Input", "Please enter valid letters only!")
            return

        for letter in input_text:
            if letter in self.guessed_letters:
                messagebox.showinfo("Repeated Letter", f"You already guessed '{letter}'!")
                continue

            self.guessed_letters.add(letter)
            self.update_ui()

            if letter in self.word:
                self.reveal_letter(letter)
            else:
                self.remaining_attempts -= 1

            if self.check_game_end():
                return

        self.update_ui()

    def reveal_letter(self, letter):
        for idx, char in enumerate(self.word):
            if char == letter:
                self.guessed_word[idx] = letter
        self.word_label.config(text=" ".join(self.guessed_word))

    def update_ui(self):
        self.guessed_label.config(text=f"Guessed Letters: {', '.join(sorted(self.guessed_letters))}")
        self.attempts_label.config(text=f"Remaining Attempts: {self.remaining_attempts}")
        self.word_translate_label.config(text=f"Hint: {self.word_translate.capitalize()}")

    def check_game_end(self):
        if "_" not in self.guessed_word:
            messagebox.showinfo("You Win!", f"Congratulations! The word was: {self.word}")
            # print(self.word, self.words )
            self.words.remove(self.word.lower())
            self.restart_game()
            return True
        elif self.remaining_attempts <= 0:
            messagebox.showerror("Game Over", f"You lost! The word was: {self.word}")
            self.restart_game()
            return True
        return False

    def restart_game(self):
        self.reset_game_vars()
        self.update_ui()

        self.guessed_word = [" " if char == " " else "_" for char in self.word]
        self.word_label.config(text=" ".join(self.guessed_word))

    def translate_sentence(self, sentence, source_lang="en", target_lang="pt"):
        try:
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            return translator.translate(sentence)
        except Exception as e:
            print(f"Translation error: {e}")
            return "Translation unavailable"

# Executar o jogo
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hangman Game")
    game = HangmanGame(root)
    game.pack(expand=True, fill='both')
    root.geometry("500x450")
    root.mainloop()
