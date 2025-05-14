import os
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import pandas as pd
from PIL import Image, ImageTk
import json
import pygame
# import random
from datetime import datetime
from deep_translator import GoogleTranslator
# from random import randint

from app.utils.data_loader import DataLoader
from app.utils.game_timer import GameTimer
from app.utils.save_data import save_game_data

import numpy as np
from numpy import random

# np.random.seed(42)

# Inicializa o mixer do pygame
pygame.mixer.init()

TITLE_FONT = ("Arial", 20)
LABEL_FONT = ("Arial", 14)
SMALL_FONT = ("Arial", 12)

# DATA_PATH = Path("extract_data_video/data/extracted_data/words/data_organize")
DATA_PATH = Path("database/vocabulary/words/data_organize")
SUBCATEGORY_NAME = "em_loja"

class HangmanGame(tk.Frame):
    MAX_ATTEMPTS = 6

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        # self.loader = DataLoader(base_path=DATA_PATH)
        # self.list_data_words:list[dict] = self.loader.get_all_words(subcategory_name=SUBCATEGORY_NAME)

        self.list_data_words:list[dict] = self.open_json('database/vocabulary/study_word_list.json')
        
        # random.shuffle(self.list_data_words)

        self.timer = GameTimer(self)

        self.clicks_on_guess = 0

        self.last_word = None

        self.id_game = self.gerar_hash_id()
        self.reset_game()
        self.setup_ui()

    def gerar_hash_id(self):
        agora = datetime.now().strftime("%Y%m%d%H%M%S%f")  # AnoMesDiaHoraMinSegMicroseg
        return hex(abs(hash(agora)))[2:]  # Converte para hexadecimal e remove '0x'

    def reset_game(self):
        if not self.list_data_words:
            messagebox.showinfo("Fim", "Não há mais palavras disponíveis.")
            self.parent.quit()
            return

        self.list_of_typed_letters = []
        self.dict_info_words = self.list_data_words.pop(random.randint(0, len(self.list_data_words)-1))

        self.word_answer = self.dict_info_words.get("text_eng", None)
        self.word_answer = self.word_answer.lower()
        
        self.word_question = self.dict_info_words.get("text_pt_br", None) 

        self.guessed_word = self.hide_text(self.word_answer) 
        self.remaining_attempts = self.MAX_ATTEMPTS
        self.guessed_letters = set()

        self.timer.reset_timer()
        self.timer.play()

    def hide_text(self, text: str) -> str:
        # return [" " if c == " " else "_" for c in text]
        return ['_' if c.isalpha() else c for c in text]

    def show_label_words(self):
        font=("Arial", 12)
        fg="black"
        self.palavras_restantes_label = tk.Label(self, text=f"Palavras restantes: {len(self.list_data_words)}", font=font, fg=fg)
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

        self.btn_editar = tk.Button(self, text="✏️ Editar")
        self.btn_editar.config(command=lambda: self.editar_json(dict_info_words=self.dict_info_words))
        self.btn_editar.place(relx=0.0, rely=0.5, anchor="w")

        self.btn_editar = tk.Button(self, text="🎲 Embaralhar")
        self.btn_editar.config(command=self.restart_game)
        self.btn_editar.place(relx=0.0, rely=0.56, anchor="w")

        self.update_ui()


    def update_ui(self):
        
        self.palavras_restantes_label.config(text=f"Palavras restantes: {len(self.list_data_words)}")

        self.word_label.config(text=" ".join(self.guessed_word))
        self.attempts_label.config(text=f"Tentativas restantes: {self.remaining_attempts}")
        self.guessed_label.config(text=f"Letras tentadas: {', '.join(sorted(self.guessed_letters))}")
        self.hint_label.config(text=f"Dica: {self.word_question}")


        image_figure = self.dict_info_words.get("image_figure", None)

        if image_figure:
            img_path = image_figure
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

        # Repedindo para garantir que todas as letras sejam adicionadas
        for letter in guess:
            self.list_of_typed_letters.append(letter.lower())
            

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
    
    def editar_json(self, dict_info_words):
        SMALL_FONT = ("Arial", 10)  # ou use a fonte que desejar
        path_base = Path(dict_info_words.get("path", ""))
        path_text_json = path_base / "text_v2.json"
        path_image = path_base / "image_text.jpg"

        if not path_text_json.exists():
            messagebox.showerror("Erro", f"Arquivo não encontrado: {path_text_json}")
            return

        try:
            with open(path_text_json, 'r', encoding="utf-8") as f:
                json_data = json.load(f)
        except Exception as e:
            messagebox.showerror("Erro ao abrir JSON", str(e))
            return

        # Cria nova janela
        editor_window = tk.Toplevel(self)
        editor_window.title("Editar texto")

        current_row = 0

        # Exibe imagem no topo (se existir)
        if path_image.exists():
            try:
                img = Image.open(path_image).resize((200, 200))
                photo = ImageTk.PhotoImage(img)

                img_label = tk.Label(editor_window, image=photo)
                img_label.image = photo  # evitar que o garbage collector apague
                img_label.grid(row=current_row, column=0, columnspan=2, pady=10)
                current_row += 1
            except Exception as e:
                messagebox.showwarning("Imagem", f"Erro ao carregar imagem: {e}")

        entries = {}

        for key, value in json_data.items():
            tk.Label(editor_window, text=key, font=SMALL_FONT).grid(row=current_row, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(editor_window, width=60)
            entry.insert(0, value)
            entry.grid(row=current_row, column=1, padx=10, pady=5, sticky="w")
            entries[key] = entry
            current_row += 1

        def salvar_alteracoes():
            for key in json_data:
                json_data[key] = entries[key].get()

            try:
                with open(path_text_json, 'w', encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso.")
                editor_window.destroy()
            except Exception as e:
                messagebox.showerror("Erro ao salvar JSON", str(e))

        salvar_btn = tk.Button(editor_window, text="Salvar", command=salvar_alteracoes, font=SMALL_FONT)
        salvar_btn.grid(row=current_row, column=0, columnspan=2, pady=10)

    def reveal_letters(self, letter):
        for idx, char in enumerate(self.word_answer):
            if char == letter:
                self.guessed_word[idx] = letter

    def exibir_fim_de_jogo(self):
        # Cria uma nova janela
        fim_window = tk.Toplevel(self)
        fim_window.title("Fim de jogo")
        fim_window.grab_set()  # modal
        fim_window.configure(bg="white")

        # Ícone de erro
        icon_label = tk.Label(fim_window, text="❌", font=("Arial", 40), bg="white", fg="red")
        icon_label.pack(pady=(15, 0))

        # Mensagem da palavra correta
        msg_label = tk.Label(
            fim_window,
            text=f"A palavra era: {self.word_answer}",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="black",
            wraplength=300,
            justify="center"
        )
        msg_label.pack(padx=20, pady=10)

        # Frame para os botões
        btn_frame = tk.Frame(fim_window, bg="white")
        btn_frame.pack(pady=(0, 15))

        # Botão Editar
        btn_editar = tk.Button(
            btn_frame,
            text="✏️ Editar",
            font=("Arial", 10),
            width=15,
            command=lambda: [fim_window.destroy(), self.editar_json(self.last_word)]
        )
        btn_editar.pack(side="left", padx=10)

        # Botão OK
        btn_ok = tk.Button(
            btn_frame,
            text="✅ OK",
            font=("Arial", 10),
            width=15,
            command=fim_window.destroy
            # command=lambda: [fim_window.destroy(), self.restart_game()]
        )
        btn_ok.pack(side="left", padx=10)

        # Centraliza a janela
        fim_window.update_idletasks()
        w = fim_window.winfo_width()
        h = fim_window.winfo_height()
        x = (fim_window.winfo_screenwidth() // 2) - (w // 2)
        y = (fim_window.winfo_screenheight() // 2) - (h // 2)
        fim_window.geometry(f"{w}x{h}+{x}+{y}")

    def exibir_vitoria(self):
        vitoria_window = tk.Toplevel(self)
        vitoria_window.title("Você venceu!")
        vitoria_window.grab_set()
        vitoria_window.configure(bg="white")

        # Ícone e mensagem
        icon_label = tk.Label(vitoria_window, text="🎉", font=("Arial", 40), bg="white", fg="green")
        icon_label.pack(pady=(15, 0))

        msg_label = tk.Label(
            vitoria_window,
            text=f"Você venceu!\nA palavra era: {self.word_answer}",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="black",
            wraplength=300,
            justify="center"
        )
        msg_label.pack(padx=20, pady=10)

        # Frame para os botões
        btn_frame = tk.Frame(vitoria_window, bg="white")
        btn_frame.pack(pady=(0, 15))

        # Botão Editar
        btn_editar = tk.Button(
            btn_frame,
            text="✏️ Editar",
            font=("Arial", 10),
            width=15,
            command=lambda: [vitoria_window.destroy(), self.editar_json(self.last_word)]
        )
        btn_editar.pack(side="left", padx=10)

        # Botão OK
        btn_ok = tk.Button(
            vitoria_window,
            text="OK",
            font=("Arial", 10),
            width=15,
            command=vitoria_window.destroy
            # command=lambda: [vitoria_window.destroy(), self.restart_game()]
        )
        btn_ok.pack(pady=(0, 15))

        # Centraliza
        vitoria_window.update_idletasks()
        w = vitoria_window.winfo_width()
        h = vitoria_window.winfo_height()
        x = (vitoria_window.winfo_screenwidth() // 2) - (w // 2)
        y = (vitoria_window.winfo_screenheight() // 2) - (h // 2)
        vitoria_window.geometry(f"{w}x{h}+{x}+{y}")

    def check_game_end(self) -> bool:
        if "_" not in self.guessed_word:
            self.save_score(True)
            # messagebox.showinfo("Você venceu!", f"A palavra era: {self.word_answer}")
            # self.restart_game()
            self.exibir_vitoria()
            self.restart_game()
            return True

        if self.remaining_attempts <= 0:
            self.save_score(False)

            # Coloca a palavra de volta na lista
            self.list_data_words.append(self.dict_info_words)
            
            # messagebox.showerror("Fim de jogo", f"A palavra era: {self.word_answer}")
            self.exibir_fim_de_jogo()
            self.restart_game()
            return True

        return False

    def restart_game(self):
        self.last_word = self.dict_info_words.copy()
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

        path_word = Path(self.dict_info_words.get("path", None))

        category = path_word.parts[-3]
        sub_category = path_word.parts[-2]
        # adjetivos/sobre_as_pessoas/unable

        # if not any([category == loader_category.name for loader_category in self.loader.get_categories()]):
        #     print("Categoria Não Existe")

        self.timer.reset_timer()
        self.clicks_on_guess = 0

        # assert total_attempts >= used_attempts, "Tentativas usadas não podem ser maiores que o total permitido."

        datetime_now = datetime.now().isoformat(timespec="seconds")
        

        game_data = {
            "id_game": self.id_game,
            "datetime": datetime_now,
            "word": self.word_answer,
            "category":category,
            "sub_category":sub_category,
            "hint": self.word_question,
            "won": won,
            "difficulty": difficulty,
            "total_attempts": self.MAX_ATTEMPTS,
            "used_attempts": attempts_used,
            "clicks_on_guess": clicks_on_guess,
            "correct_guessed_letters": correct_guessed_letters,
            "incorrect_guessed_letters": incorrect_guessed_letters,
            "list_of_typed_letters":self.list_of_typed_letters,
            # "correct_guesses": correct_guesses,
            # "incorrect_guesses": incorrect_guesses,
            "time_taken": time_taken,
            "game_name": "hangman",
        }

        save_game_data(game_data)
        # self.save_score()

    def translate_sentence(self, sentence, source_lang="en", target_lang="pt"):
        try:
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            return translator.translate(sentence)
        except Exception as e:
            print(f"Translation error: {e}")
            return "Translation unavailable"
    
    def open_json(self, filepath):
        try:
            with open(filepath, 'r', encoding="utf-8") as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            print(f"Error: File not found at {filepath}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {filepath}")
            return None

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
