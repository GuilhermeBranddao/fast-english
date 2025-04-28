import os
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import random
from deep_translator import GoogleTranslator
from app.utils.toolkit import read_json

TITLE_FONT = ("Arial", 20)
LABEL_FONT = ("Arial", 14)
SMALL_FONT = ("Arial", 12)

class HangmanGame(tk.Frame):
    MAX_ATTEMPTS = 6
    WORD_FILE = "database/vocabulary_json/describing_things/adjectives.json"
    INFO_GAMES = "database/infos/game.csv"

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        self.dict_words = self.load_words()
        self.word_answer = None
        self.word_question = None
        self.reset_game()
        self.setup_ui()

    def load_words(self) -> dict:
        return read_json(self.WORD_FILE)

    def reset_game(self):
        if not self.dict_words:
            messagebox.showinfo("Info", "No more words available.")
            self.parent.quit()
            return

        self.word_question = random.choice(list(self.dict_words.keys()))
        self.word_answer = self.dict_words.pop(self.word_question).lower()

        self.guessed_word = [" " if c == " " else "_" for c in self.word_answer]
        self.remaining_attempts = self.MAX_ATTEMPTS
        self.guessed_letters = set()

    def setup_ui(self):
        self.word_label = tk.Label(self, text=" ".join(self.guessed_word), font=TITLE_FONT)
        self.word_label.pack(pady=20)

        self.attempts_label = tk.Label(self, text="", font=LABEL_FONT)
        self.attempts_label.pack(pady=10)

        self.input_frame = tk.Frame(self)
        self.input_frame.pack(pady=10)

        tk.Label(self.input_frame, text="Enter a letter:", font=SMALL_FONT).pack(side="left", padx=5)
        self.letter_entry = tk.Entry(self.input_frame, width=5, font=LABEL_FONT)
        self.letter_entry.pack(side="left", padx=5)

        self.guess_button = tk.Button(self.input_frame, text="Guess", command=self.check_guess)
        self.guess_button.pack(side="left", padx=5)

        self.guessed_label = tk.Label(self, text="", font=SMALL_FONT)
        self.guessed_label.pack(pady=10)

        self.hint_label = tk.Label(self, text="", font=SMALL_FONT)
        self.hint_label.pack(pady=10)

        self.update_ui()

    def update_ui(self):
        self.word_label.config(text=" ".join(self.guessed_word))
        self.attempts_label.config(text=f"Remaining Attempts: {self.remaining_attempts}")
        self.guessed_label.config(text=f"Guessed Letters: {', '.join(sorted(self.guessed_letters))}")
        self.hint_label.config(text=f"Hint: {self.word_question.capitalize()}")

    def check_guess(self):
        guess = self.letter_entry.get().strip().upper()
        self.letter_entry.delete(0, tk.END)

        if not guess.isalpha():
            messagebox.showwarning("Invalid Input", "Please enter only letters.")
            return

        for letter in guess:
            if letter in self.guessed_letters:
                messagebox.showinfo("Repeated Letter", f"You already guessed '{letter}'.")
                continue

            self.guessed_letters.add(letter)
            if letter.lower() in self.word_answer:
                self.reveal_letters(letter.lower())
            else:
                self.remaining_attempts -= 1

            if self.check_game_end():
                return

        self.update_ui()

    def reveal_letters(self, letter):
        for idx, char in enumerate(self.word_answer):
            if char == letter:
                self.guessed_word[idx] = letter

    def check_game_end(self) -> bool:
        if "_" not in self.guessed_word:
            self.save_score(True)
            messagebox.showinfo("You Win!", f"Congratulations! The word was: {self.word_answer}")
            self.restart_game()
            return True

        if self.remaining_attempts <= 0:
            self.save_score(False)
            messagebox.showerror("Game Over", f"You lost! The word was: {self.word_answer}")
            self.restart_game()
            return True

        return False

    def restart_game(self):
        self.reset_game()
        self.update_ui()
  
    def save_score(self, won: bool):
        attempts_used = self.MAX_ATTEMPTS - self.remaining_attempts
        difficulty = attempts_used / self.MAX_ATTEMPTS

        # Monta o dicionário de informações do jogo
        game_data = {
            "word": self.word_answer,
            "won": won,
            "difficulty": round(difficulty, 2),
            "game": "hangman_game"
        }

        # Verifica se o arquivo existe
        if os.path.exists(self.INFO_GAMES):
            df_info_games = pd.read_csv(self.INFO_GAMES)
        else:
            df_info_games = pd.DataFrame(columns=["word", "won", "difficulty", "game"])

        # Adiciona a nova linha
        df_info_games = pd.concat([df_info_games, pd.DataFrame([game_data])], ignore_index=True)

        # Salva de volta no CSV
        df_info_games.to_csv(self.INFO_GAMES, index=False)

        print(game_data)

    def translate_text(self, text, source_lang="en", target_lang="pt"):
        try:
            return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        except Exception as e:
            print(f"Translation error: {e}")
            return "Translation unavailable"

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hangman Game")
    game = HangmanGame(root)
    game.pack(expand=True, fill="both")
    root.geometry("500x450")
    root.mainloop()
