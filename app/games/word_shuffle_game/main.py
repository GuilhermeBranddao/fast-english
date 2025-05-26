import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import pygame
import os
import string
from datetime import datetime
from pathlib import Path
from app.toolkit.utils.save_data import save_game_data, del_game_task
from app.stats_words.analyzer import WordStatsAnalyzer
import json
from app.toolkit import word_utils

# Inicializa áudio
pygame.mixer.init()

def highlight_letters(user_input, shuffled_word, text_widget):
    text_widget.config(state='normal')
    text_widget.delete("1.0", tk.END)
    for letter in shuffled_word:
        if letter in user_input:
            text_widget.insert(tk.END, letter, "green")
        else:
            text_widget.insert(tk.END, letter)
    text_widget.tag_config("green", foreground="green")
    text_widget.config(state='disabled')



# App principal
class WordShuffleGame(tk.Frame):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        self.word_stats_analyzer = WordStatsAnalyzer(list_game_name=["game_data_hangman", "game_data_word_shuffle_game"])

        self.list_data_words = word_utils.open_json('database/vocabulary/study_word_list.json')

        random.shuffle(self.list_data_words)

        self.list_unknown_words = word_utils.filter_unknown_words(self.list_data_words, 
                                                            self.word_stats_analyzer, 
                                                            acc_min=60,
                                                            # filter_specific_word="i/l"
                                                            )
        self.entries:list[dict[str, str]] = []
        self.audio_path = ""

        # if self.load_check_pending_words():
            # return  # Espera o usuário resolver pendência

        # Frame principal
        self.frame = tk.Frame(self)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Frame para botões
        self.btn_frame = tk.Frame(self)
        self.btn_frame.pack(pady=10)

        self.next_btn = tk.Button(self.btn_frame, text="➡ Próxima", command=self.load_sentence, state='disabled')
        self.next_btn.pack(side="left", padx=5)

        self.play_audio_btn = tk.Button(self.btn_frame, text="🔊 Ouvir Áudio", command=self.play_audio)
        self.play_audio_btn.pack(side="left", padx=5)

        self.frame_stats()
        
        # Botão Editar
        btn_editar = tk.Button(
            self.btn_frame,
            text="✏️ Editar",
            font=("Arial", 10),
            width=10,
            command=lambda: self.editar_json(list_pending_words=self.dict_info_words)
        )
        btn_editar.pack(side="left", padx=5)

        self.id_game = word_utils.gerar_hash_id()

        self.clicks_on_guess = {}

        # Verifica se ainda há pendentes após editar
        if not self.load_check_pending_words():
            self.load_sentence()

    def frame_stats(self):
        # Frame para estatísticas
        self.stats_frame = tk.Frame(self)
        self.stats_frame.pack(pady=(10, 5))

        font_stats = ("Arial", 12, "bold")
        
        tk.Label(self.stats_frame, text="Palavras Faltantes:", font=font_stats, fg="#D9534F").grid(row=0, column=0, padx=5, sticky="e")
        self.label_skipped = tk.Label(self.stats_frame, text=f"{len(self.list_unknown_words)}", font=font_stats)
        self.label_skipped.grid(row=0, column=1, padx=5, sticky="w")

        tk.Label(self.stats_frame, text="Palavras Conhecidas:", font=font_stats, fg="#5CB85C").grid(row=0, column=2, padx=5, sticky="e")
        self.label_known = tk.Label(self.stats_frame, text=f"{len(self.list_data_words)}", font=font_stats)
        self.label_known.grid(row=0, column=3, padx=5, sticky="w")

    def update_stats(self):
        self.label_skipped.config(text=str(len(self.list_unknown_words)))
        self.label_known.config(text=str(len(self.list_data_words)))

    
    def editar_json(self, list_pending_words:dict|list[dict[str, str]]):
        if isinstance(list_pending_words, list):
            if not list_pending_words:
                return False  # Nenhuma pendente, pode continuar
            
        if isinstance(list_pending_words, dict):
            list_pending_words = [list_pending_words]

        list_pending_words = list_pending_words.copy()
        dict_info_words = list_pending_words.pop(random.randint(0, len(list_pending_words) - 1))

        SMALL_FONT = ("Arial", 10)  # ou use a fonte que desejar

        path = dict_info_words.get("path", "")
        
        path_base = Path(path.replace("\\", "/"))

        path_text_json = path_base / "text_v2.json"
        path_image = path_base / "image_text.jpg"


        if not path_text_json.exists():
            messagebox.showerror("Erro", f"Arquivo não encontrado: {path_text_json}")
            return

        try:
            with open(path_text_json, 'r', encoding="utf-8") as f:
                json_data = json.load(f)
        except Exception as e:
            print(f"ERROR: Erro ao abrir JSON: {e}")
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

        # Campos que podem ser editados manualmente
        campos_editaveis = ["pergunta_pt-br", "uso_da_linguagem", "tradução_en", "fonetica"]
        entries = {}

        for key in campos_editaveis:
            if key in json_data:
                tk.Label(editor_window, text=key, font=SMALL_FONT).grid(row=current_row, column=0, padx=10, pady=5, sticky="e")
                entry = tk.Entry(editor_window, width=60)
                entry.insert(0, json_data[key].capitalize())
                entry.grid(row=current_row, column=1, padx=10, pady=5, sticky="w")
                entries[key] = entry
                current_row += 1

        delete_var = tk.BooleanVar(value=False)
        delete_check = tk.Checkbutton(
            editor_window,
            text="Excluir tarefa do banco de dados",
            variable=delete_var,
            font=SMALL_FONT
        )
        delete_check.grid(row=current_row, column=0, columnspan=2, pady=(5, 0))
        current_row += 1


        # Label com contador de pendentes
        contador_label = tk.Label(editor_window, font=SMALL_FONT)
        contador_label.grid(row=current_row + 2, column=0, columnspan=2, pady=(5, 10))

        def atualizar_contador():
            total_pendentes = len(list_pending_words)
            contador_label.config(text=f"{total_pendentes} arquivo(s) pendente(s)")

        def salvar_alteracoes():
            for key in entries:
                json_data[key] = entries[key].get()

            # Atualiza status e timestamp automaticamente
            json_data["status"] = "revised"
            json_data["updated_at"] = datetime.now().isoformat()

            try:
                with open(path_text_json, 'w', encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=4)

                if delete_var.get():
                    from app.toolkit.utils.save_data import del_game_task
                    del_game_task(
                        id_game_task=self.id_game_task,
                        game_name="word_shuffle_game"
                    )

                atualizar_contador()

                # Se ainda houver pendências, recarrega o editor com a próxima
                if list_pending_words:
                    editor_window.destroy()
                    self.editar_json(list_pending_words)
                else:
                    messagebox.showinfo("Concluído", "Todas as pendências foram resolvidas.")
                    editor_window.destroy()
                    self.load_sentence()

            except Exception as e:
                messagebox.showerror("Erro ao salvar JSON", str(e))


        salvar_btn = tk.Button(editor_window, text="Salvar", command=salvar_alteracoes, font=SMALL_FONT)
        salvar_btn.grid(row=current_row, column=0, columnspan=2, pady=10)

        atualizar_contador()

    def load_check_pending_words(self):
        # Limpar frame anterior
        # self.frame_check_pending = tk.Frame(self)
        # self.frame_check_pending.pack(padx=20, pady=20, fill="both", expand=True)

        # for widget in self.frame_check_pending.winfo_children():
        #     widget.destroy()
        # self.entries.clear()

        # Verifica se há palavras pendentes
        list_pending_words = [d for d in self.list_unknown_words if "pending" in d.get("status", "")]

        if not list_pending_words:
            print("Não há palavras pendentes no desafio")
            return False  # Nenhuma pendente, pode continuar

        print(f"Há {len(list_pending_words)} palavras pendentes no desafio")
        # sentence = self.dict_info_words["text_eng"]
        # sentence_question = self.dict_info_words["text_pt_br"]
        # self.audio_path = self.dict_info_words["audio_path"]
        # image_path = self.dict_info_words["image_figure"]

        # tk.Label(self.frame_check_pending, text="Checando palavras pendentes", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=10)

        self.editar_json(list_pending_words=list_pending_words)
        return True


    def load_sentence(self, delete_last_task_in_database=False):
        
        self.update_stats()

        if delete_last_task_in_database:
            print(f"Deletar dados de tarefa no banco: {self.id_game_task}")
            del_game_task(id_game_task=self.id_game_task, game_name="word_shuffle_game")


        for widget in self.frame.winfo_children():
            widget.destroy()
        self.entries.clear()

        if not self.list_unknown_words:
            messagebox.showinfo("Fim", "Você completou todas as frases!")
            self.parent.quit()
            return

        self.dict_info_words = self.list_unknown_words.pop(random.randint(0, len(self.list_unknown_words) - 1))
        sentence = self.dict_info_words["text_eng"]
        sentence_question = self.dict_info_words["text_pt_br"]
        self.audio_path = self.dict_info_words["audio_path"].replace("\\", "/")
        image_path = self.dict_info_words["image_figure"]

        sentence = sentence.translate(str.maketrans('', '', ',.?!')).lower()
        
        # Título da questão
        tk.Label(self.frame, text=sentence_question, font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=10)

        # Cabeçalho alinhado com grid
        tk.Label(self.frame, text="Confirmar", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=3, pady=3)
        tk.Label(self.frame, text="Desistir", font=("Arial", 10, "bold")).grid(row=1, column=1, padx=3, pady=3)
        tk.Label(self.frame, text="Palavra", font=("Arial", 10, "bold")).grid(row=1, column=2, padx=3, pady=3)
        tk.Label(self.frame, text="Embaralhada", font=("Arial", 10, "bold")).grid(row=1, column=3, padx=3, pady=3)
        tk.Label(self.frame, text="Acuracia", font=("Arial", 10, "bold")).grid(row=1, column=4, padx=3, pady=3)

        self.quantity_play_audio = 0
        words = sentence.strip().split()

        self.inputs = []
        self.letter_labels_list = []  # Lista de listas (uma para cada palavra)
        for i, word in enumerate(words):
            word_stats = self.word_stats_analyzer.get_word_info(word, return_dict=True)
            
            shuffled = word_utils.shuffle_word(word)
            check = tk.Button(self.frame, text="✅", command=lambda idx=i: self.check_single_answer(idx))
            check.grid(row=i + 2, column=0, padx=1, pady=2)

            give_up = tk.Button(self.frame, text="❌", command=lambda idx=i: self.give_up_word(idx))
            give_up.grid(row=i + 2, column=1, padx=1, pady=2)
            
            self.input_var = tk.StringVar()
            self.input_var.trace_add("write", self.update_colors)
            entry = tk.Entry(self.frame, width=15, textvariable=self.input_var)#, font=("Arial", 18))
            entry.grid(row=i + 2, column=2, padx=3, pady=2)

            # label = tk.Label(self.frame, text=shuffled)
            # label.grid(row=i + 2, column=3, padx=3, pady=2, sticky="w")

            ##########
            letters_frame = tk.Frame(self.frame)
            letters_frame.grid(row=i + 2, column=3, padx=2)

            letter_labels = []
            for letter in shuffled:
                lbl = tk.Label(letters_frame, text=letter, font=("Arial", 10))
                lbl.pack(side="left", padx=1)
                letter_labels.append(lbl)


            self.letter_labels_list.append(letter_labels)
            self.inputs.append((self.input_var, word.lower()))
            ##########

            stats_acc = tk.Label(self.frame, text=word_stats.get("acuracia", "New Word!"))  # Exemplo
            stats_acc.grid(row=i + 2, column=4, padx=3, pady=2, sticky="w")
            clean_word = word.strip(string.punctuation).lower()
            self.entries.append({
                "word": word,
                "entry": entry,
                "clean_word": clean_word,
                # "label": label,
                "check": check,
                "give_up": give_up,
                "stats_acc": stats_acc,
            })

            self.clicks_on_guess[i] = 0

            if int(word_stats.get("acuracia", 0)) > 60:
                self.revela_palavra_conhecida(idx=i)

        # self.submit_btn.config(state='normal')
        self.next_btn.config(state='disabled')

        self.id_game_task = word_utils.gerar_hash_id()

        self.check_all_answers()

    def revela_palavra_conhecida(self, idx):
        dict_entries = self.entries[idx]

        dict_entries.get("check").config(state='disabled')
        dict_entries.get("give_up").config(state='disabled')
        dict_entries.get("entry").config(bg="lightgreen")
        dict_entries.get("entry").insert(0, dict_entries.get("clean_word"))


    def save_game(self, word, idx, won):

        datetime_now = datetime.now().isoformat(timespec="seconds")
        
        path_word = Path(self.dict_info_words.get("path", None))

        category = path_word.parts[-3]
        sub_category = path_word.parts[-2]
        word_folder = path_word.parts[-1]

        game_data = {
            "id_game": self.id_game,
            "id_game_task": self.id_game_task,
            "datetime": datetime_now,
            "word": word,
            "category":category,
            "sub_category":sub_category,
            "word_folder":word_folder,
            "won": won,
            "quantity_play_audio":self.quantity_play_audio,
            "clicks_on_guess": self.clicks_on_guess[idx],
            "game_name": "word_shuffle_game",
        }

        save_game_data(game_data)
        # print(game_data)
    
    def update_colors(self, *args):
        for idx, (input_var, _) in enumerate(self.inputs):
            typed = input_var.get()
            typed_letters = list(typed)

            letter_labels = self.letter_labels_list[idx]

            letter_labels = self.letter_labels_list[idx]
            # Resetar todas as letras para preto
            for lbl in letter_labels:
                lbl.config(fg="black", font=("Arial", 10))

            used = [False] * len(letter_labels)

            for letter in typed_letters:
                for i, lbl in enumerate(letter_labels):
                    if not used[i] and lbl.cget("text") == letter:
                        lbl.config(fg="green", font=("Arial", 12, "bold"))
                        used[i] = True
                        break

    
    def check_all_answers(self):
        all_correct = True
        for dict_entries in self.entries:
            user_input = dict_entries.get("entry").get().strip().lower()
            # print(user_input != correct_word)
            if user_input != dict_entries.get("clean_word"):
                all_correct = False

        if all_correct:
            pygame.mixer.music.stop()
            # messagebox.showinfo("Parabéns!", "Você acertou todas as palavras!")
            # self.submit_btn.config(state='disabled')
            self.next_btn.config(state='normal')
    
    def check_single_answer(self, idx):
        # entry, correct_word = self.entries[idx]
        self.clicks_on_guess[idx] += 1
        dict_entries = self.entries[idx]

        user_input = dict_entries.get("entry").get().strip().lower()
        if user_input == dict_entries.get("clean_word"):
            dict_entries.get("entry").config(bg="lightgreen")

            dict_entries.get("check").config(state='disabled')
            dict_entries.get("give_up").config(state='disabled')

            self.check_all_answers()

            self.save_game(word=dict_entries.get("word"), 
                           idx=idx, 
                           won=True)
        else:
            dict_entries.get("entry").config(bg="salmon")

    def give_up_word(self, idx):
        dict_entries = self.entries[idx]
        dict_entries.get("entry").delete(0, tk.END)
        dict_entries.get("entry").insert(0, dict_entries.get("clean_word"))
        dict_entries.get("entry").config(bg="yellow")


        dict_entries.get("check").config(state='disabled')
        dict_entries.get("give_up").config(state='disabled')

        self.check_all_answers()

        self.save_game(word=dict_entries.get("word"), 
                       idx=idx, 
                       won=False)


    def play_audio(self):
        if os.path.exists(self.audio_path):
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            pygame.mixer.music.load(self.audio_path)
            pygame.mixer.music.play()
            self.quantity_play_audio += 1
        else:
            messagebox.showerror("Erro", "Áudio não encontrado!")

# Iniciar app
if __name__ == "__main__":
    try:
        root = tk.Tk()
        game = WordShuffleGame(root)
        game.pack(expand=True, fill="both")
        root.title("Word Shuffle Game")
        root.geometry("840x520")
        root.mainloop()

    except Exception as e:
        print(f"Error {e}")
    finally:
        root.destroy()