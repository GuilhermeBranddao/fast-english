import os
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import pandas as pd
from PIL import Image, ImageTk
import json
import pygame
import random
from datetime import datetime
import time
from deep_translator import GoogleTranslator
from random import randint

# Inicializa o mixer do pygame
pygame.mixer.init()

TITLE_FONT = ("Arial", 20)
LABEL_FONT = ("Arial", 14)
SMALL_FONT = ("Arial", 12)

DATA_PATH = Path("extract_data_video/data_organize")

from datetime import datetime
from typing import List, Dict, Union

from datetime import datetime
import os 



import csv
import os
from typing import Dict, Union, List
def save_game_data(data: Dict[str, Union[str, int, float, List[str], bool]], 
                   file_path: str = "database/infos/game_data_{game_name}.csv") -> None:
    
    file_path = file_path.format(game_name=data.get("game_name", "error"))
    file_exists = os.path.isfile(file_path)

    # Convert listas para string
    for key, value in data.items():
        if isinstance(value, list):
            data[key] = ",".join(map(str, value))

    # Define os fieldnames dinamicamente
    if file_exists:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            # Adiciona novas chaves que estão em `data` mas não no CSV
            for key in data.keys():
                if key not in fieldnames:
                    fieldnames.append(key)
    else:
        fieldnames = list(data.keys())

    # Reescreve o CSV inteiro se foi necessário atualizar os cabeçalhos
    if file_exists:
        with open(file_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        # Atualiza todas as linhas antigas com as novas chaves (valores vazios)
        for row in rows:
            for key in fieldnames:
                if key not in row:
                    row[key] = ""

        # Adiciona a nova linha
        clean_data = {key: data.get(key, "") for key in fieldnames}
        rows.append(clean_data)

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    else:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(data)

def fill_dict(
    word: str = None,
    category: str = None,
    sub_category: str = None,
    hint: Union[str, int] = None,
    won: bool = None,
    difficulty: float = None,
    total_attempts: int = None,
    used_attempts: int = None,
    clicks_on_guess: int = None,
    correct_guessed_letters: List[str] = None,
    incorrect_guessed_letters: List[str] = None,
    correct_guesses: int = None,
    incorrect_guesses: int = None,
    time_taken: float = None,
    game_name: str = None,
) -> Dict[str, Union[str, int, float, List[str], bool]]:
    """
    Retorna um dicionário com os dados de desempenho de um jogador em uma partida.

    Parâmetros:
    - word: Palavra do jogo.
    - category: Categoria da palavra
    - sub_category: Sub-categoria da palavra
    - hint: Dica associada à palavra (string ou ID).
    - won: True se o jogador venceu, False se perdeu.
    - difficulty: Dificuldade da palavra (0.0 a 1.0).
    - total_attempts: Tentativas permitidas.
    - used_attempts: Tentativas usadas.
    - clicks_on_guess: quantidade de clikes no botão de adivinhar
    - correct_guessed_letters: Lista de letras tentadas corretamente.
    - incorrect_guessed_letters: Lista de letras tentadas incorretamente.
    - correct_guesses: Quantidade de acertos.
    - incorrect_guesses: Quantidade de erros.
    - time_taken: Tempo gasto (em segundos).
    - game_name: Nome do jogo.

    Retorno:
    - Um dicionário com os dados formatados.
    """

    assert total_attempts >= used_attempts, "Tentativas usadas não podem ser maiores que o total permitido."

    datetime_now = datetime.now().isoformat(timespec="seconds")

    game_data = {
        "datetime": datetime_now,
        "word": word,
        "category":category,
        "sub_category":sub_category,
        "hint": hint,
        "won": won,
        "difficulty": difficulty,
        "total_attempts": total_attempts,
        "used_attempts": used_attempts,
        "clicks_on_guess": clicks_on_guess,
        "correct_guessed_letters": correct_guessed_letters,
        "incorrect_guessed_letters": incorrect_guessed_letters,
        "correct_guesses": correct_guesses,
        "incorrect_guesses": incorrect_guesses,
        "time_taken": time_taken,
        "game_name": game_name,
    
    }

    save_game_data(game_data)



class DataLoader:
    def __init__(self, base_path=DATA_PATH):
        self.base_path = base_path

    def get_categories(self):
        return [self.base_path / path for path in os.listdir(self.base_path)]

    def get_subcategories(self, category_path):
        return [category_path / path for path in os.listdir(category_path)]

    def get_words(self, subcategory_path):
        return [subcategory_path / path for path in os.listdir(subcategory_path)]

    def get_all_words(self, subcategory_name=None):
        palavras = []
        for categoria in self.get_categories():
            for subcat in self.get_subcategories(categoria):
                if subcategory_name and subcat.name != subcategory_name:
                    continue
                palavras.extend(self.get_words(subcat))
        return palavras


class Palavra:
    def __init__(self, path):
        self.path = path
        self.arquivos = list(os.listdir(path))
        self.texto_info = self._carregar_texto()
        self.imagens = self._carregar_imagens()

        self.text_pt_br = self.texto_info.get("recorte_1.jpg", "")
        self.text_eng = self.texto_info.get("recorte_3.jpg", "")
        self.audio_path = path / "audio.wav"
        self.fonetica_path = path / "recorte_4.jpg"

    def _carregar_texto(self):
        try:
            with open(self.path / "text.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def _carregar_imagens(self):
        return sorted(
            [self.path / arq for arq in self.arquivos if arq.startswith("recorte_") and arq.endswith(".jpg") and "recorte_4" not in arq],
            key=lambda x: int(x.stem.split("_")[1])
        )

class GameTimer:
    def __init__(self, master, x=1.0, y=0.0, anchor="ne", font=("Arial", 12), fg="black"):
        self.master = master
        self.label = tk.Label(master, font=font, fg=fg)
        self.label.place(relx=x, rely=y, anchor=anchor)

        self.start_time = None
        self.elapsed_time = 0  
        self.accumulated_time = 0 # Acumula tempo antes de pausas
        self.running = False

        # Botões
        self.play_button = tk.Button(master, text="▶ Play", command=self.play)
        self.play_button.place(relx=x, rely=y + 0.05, anchor=anchor)

        self.stop_button = tk.Button(master, text="⏸ Stop", command=self.stop, state=tk.DISABLED)
        self.stop_button.place(relx=x, rely=y + 0.10, anchor=anchor)

        self.restart_button = tk.Button(master, text="🔄 Reset", command=self.reset_timer)
        self.restart_button.place(relx=x, rely=y + 0.15, anchor=anchor)

    def update_timer(self):
        if self.running:
            current_time = time.time()
            self.elapsed_time = current_time - self.start_time
            total_elapsed = int(self.accumulated_time + self.elapsed_time)

            mins, secs = divmod(total_elapsed, 60)
            time_str = f"Tempo: {mins:02d}:{secs:02d}"

            self.label.config(text=time_str)
            self.master.after(1000, self.update_timer)

    def play(self):
        if not self.running:
            self.running = True
            self.start_time = time.time()
            self.update_timer()
            self.play_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

    def stop(self):
        if self.running:
            self.running = False
            self.accumulated_time += time.time() - self.start_time
            self.play_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def reset_timer(self):
        self.running = False
        self.start_time = None
        self.accumulated_time = 0
        self.label.config(text="Tempo: 00:00")
        self.play_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)



class HangmanGame(tk.Frame):
    MAX_ATTEMPTS = 6

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.loader = DataLoader()
        self.palavras_paths = self.loader.get_all_words(subcategory_name="divisões")
        random.shuffle(self.palavras_paths)

        self.timer = GameTimer(self)

        self.clicks_on_guess = 0

        self.reset_game()
        self.setup_ui()

    def reset_game(self):
        if not self.palavras_paths:
            messagebox.showinfo("Fim", "Não há mais palavras disponíveis.")
            self.parent.quit()
            return

        
        self.path_word = self.palavras_paths.pop(randint(0, len(self.palavras_paths)-1))
        self.palavra = Palavra(self.path_word)


        self.word_answer = self.palavra.text_eng.lower()
        
        self.word_question = self.palavra.text_pt_br

        self.guessed_word = [" " if c == " " else "_" for c in self.word_answer]
        self.remaining_attempts = self.MAX_ATTEMPTS
        self.guessed_letters = set()

        
        self.timer.play()

        # self.start_time = time.time()


    def show_label_words(self):
        font=("Arial", 12)
        fg="black"
        self.palavras_restantes_label = tk.Label(self, text=f"Palavras restantes: {len(self.palavras_paths)}", font=font, fg=fg)
        self.palavras_restantes_label.place(relx=0, rely=0.0, anchor="nw")

    def setup_ui(self):

        self.show_label_words()

        self.word_label = tk.Label(self, text=" ".join(self.guessed_word), font=TITLE_FONT)
        self.word_label.pack(pady=10)

        self.attempts_label = tk.Label(self, text="", font=LABEL_FONT)
        self.attempts_label.pack()

        self.guessed_label = tk.Label(self, text="", font=SMALL_FONT)
        self.guessed_label.pack()

        self.image_label = tk.Label(self)
        self.image_label.pack(pady=10)

        self.hint_label = tk.Label(self, text="", font=LABEL_FONT)
        self.hint_label.pack()

        self.input_frame = tk.Frame(self)
        self.input_frame.pack(pady=10)

        tk.Label(self.input_frame, text="Letra:", font=SMALL_FONT).pack(side="left")
        self.letter_entry = tk.Entry(self.input_frame, width=5, font=LABEL_FONT)
        self.letter_entry.pack(side="left")

        self.guess_button = tk.Button(self.input_frame, text="Adivinhar", command=self.check_guess)
        self.guess_button.pack(side="left", padx=5)

        self.update_ui()

    def update_ui(self):
        
        self.palavras_restantes_label.config(text=f"Palavras restantes: {len(self.palavras_paths)}")

        self.word_label.config(text=" ".join(self.guessed_word))
        self.attempts_label.config(text=f"Tentativas restantes: {self.remaining_attempts}")
        self.guessed_label.config(text=f"Letras tentadas: {', '.join(sorted(self.guessed_letters))}")
        self.hint_label.config(text=f"Dica: {self.word_question}")

        # if not img_path.exists():
        #     print(f"[ERRO] Caminho da imagem não encontrado: {img_path}")

        # if not hasattr(self.image_label, 'current_image_path') or self.image_label.current_image_path != img_path:

        if self.palavra.imagens:
            img_path = self.palavra.imagens[0]
            img = Image.open(img_path).resize((200, 200))
            photo = ImageTk.PhotoImage(img)

            self.image_label.config(image=photo)
            self.image_label.image = photo  # <- MANTÉM REFERÊNCIA
        else:
            self.image_label.config(image='')
            self.image_label.image = None

    def check_guess(self):

        self.clicks_on_guess += 1

        guess = self.letter_entry.get().strip().lower()
        self.letter_entry.delete(0, tk.END)

        if not guess.isalpha():
            messagebox.showwarning("Letra inválida", "Digite apenas letras.")
            return

        for letter in guess:
            if letter in self.guessed_letters:
                continue

            self.guessed_letters.add(letter)

            if letter in self.word_answer:
                self.reveal_letters(letter)
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
            messagebox.showinfo("Você venceu!", f"A palavra era: {self.word_answer}")
            self.restart_game()
            return True

        if self.remaining_attempts <= 0:
            self.save_score(False)

            # Coloca a palavra de volta na lista
            self.palavras_paths.append(self.path_word)
            
            messagebox.showerror("Fim de jogo", f"A palavra era: {self.word_answer}")
            self.restart_game()
            return True

        return False

    def restart_game(self):
        self.reset_game()
        self.update_ui()

    def save_score(self, won: bool):
        attempts_used = self.MAX_ATTEMPTS - self.remaining_attempts
        difficulty = attempts_used / self.MAX_ATTEMPTS

        correct_guessed_letters=[letter for letter in self.guessed_word if letter.isalnum()]
        incorrect_guessed_letters = list(set(self.guessed_letters).difference(set(self.guessed_word)))

        # finaliza_tempo
        # end_time = time.time()
        time_taken = self.timer.elapsed_time

        clicks_on_guess = self.clicks_on_guess

        category = self.path_word.parts[2]
        sub_category = self.path_word.parts[3]

        if any([category == loader_category.name for loader_category in self.loader.get_categories()]):
            print("Categoria existe")

        self.timer.reset_timer()
        self.clicks_on_guess = 0

        fill_dict(
            word=self.word_answer,
            category=category,
            sub_category=sub_category,
            hint=self.word_question,
            won=won,
            difficulty=round(difficulty, 2),
            total_attempts=self.MAX_ATTEMPTS,
            used_attempts=attempts_used,
            clicks_on_guess=clicks_on_guess,
            correct_guessed_letters = correct_guessed_letters,
            incorrect_guessed_letters = incorrect_guessed_letters,
            # correct_guesses=2,
            # incorrect_guesses=2,
            time_taken=time_taken,
            game_name='hangman',
        )

    def translate_sentence(self, sentence, source_lang="en", target_lang="pt"):
        try:
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            return translator.translate(sentence)
        except Exception as e:
            print(f"Translation error: {e}")
            return "Translation unavailable"



if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.title("Jogo da Forca com Imagens")
        game = HangmanGame(root)
        game.pack(expand=True, fill="both")
        root.geometry("600x600")
        root.mainloop()
    except Exception as e:
        print(f"Error {e}")
    
    finally:
        root.destroy()
