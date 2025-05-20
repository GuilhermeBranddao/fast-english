import tkinter as tk
from pathlib import Path
from app.utils.data_loader import DataLoader
import re
from tkinter import simpledialog
import json
from tqdm import tqdm

class TextReaderApp(tk.Frame):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.known_words = self.prep_data_match_word()

        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side="right", fill="y")

        self.text_widget = tk.Text(self, wrap="word", font=("Arial", 14), yscrollcommand=scrollbar.set)
        self.text_widget.pack(expand=True, fill="both")

        scrollbar.config(command=self.text_widget.yview)

        self.send_button = tk.Button(self, text="Enviar", command=self._process_text)
        self.send_button.pack(pady=(0, 5))

        self.send_button = tk.Button(self, text="Criar banco de dados com palavras", command=self._save_data_words)
        self.send_button.pack(pady=(0, 5))

        self.btn_listar_conhecidas = tk.Button(self, text="Listar Palavras Conhecidas no Texto", command=self._listar_palavras_conhecidas)
        self.btn_listar_conhecidas.pack(pady=(0, 5))


        self.btn_remover_conhecidas = tk.Button(self, text="Remover Palavras Conhecidas do Texto", command=self._remover_palavras_conhecidas_do_texto)
        self.btn_remover_conhecidas.pack(pady=(0, 5))

        self.btn_remover_desconhecidas = tk.Button(self, text="Remover Palavras Desconhecidas do Texto", command=self._remover_palavras_desconhecidas_do_texto)
        self.btn_remover_desconhecidas.pack(pady=(0, 5))

        self.btn_palavras_unicas = tk.Button(self, text="Manter Apenas Palavras Únicas", command=self._manter_palavras_unicas)
        self.btn_palavras_unicas.pack(pady=(0, 5))


        # Coluna do stats_label
        # self.stats_label = tk.Label(self, justify="left", font=("Arial", 12), anchor="nw")
        # self.stats_label.grid(row=0, column=1, padx=10, sticky="nw")  # Alinha no topo à esquerda

        self.stats_label = tk.Label(self, justify="left", font=("Arial", 12), anchor="nw")
        self.stats_label.pack(side="left", padx=10, anchor="n")

        self.list_data_words_in_text = []
        self._configure_tags()

    def prep_data_match_word(self):
        """
        Função otimizada que prepara os dados para a busca de palavras.
        """
        data_loader_words = DataLoader(base_path="database/extract_data_video/data/extracted_data/words/data_organize")
        data_loader_phrases = DataLoader(base_path="database/extract_data_video/data/extracted_data/phrases/data_organize")

        # Junta as listas diretamente
        lista_total = data_loader_words.get_all_words() + data_loader_phrases.get_all_words()

        # Cria os pares (palavra, caminho) com list comprehension
        set_data_words = [
            {"word": word, "path": Path(info["path"])}
            for info in tqdm(lista_total, desc="Processando palavras")
            for word in Path(info["path"]).stem.replace("_", " ").lower().split()
        ]

        return set_data_words

    def find_match_word(self, word, set_deta_words):
        """
        Função que procura por palavras que possuem a tag "tag" no nome.
        """
        word = word.lower()
        
        list_match_word = []
        for data_word in set_deta_words:
            word_name = data_word.get("word", "")

            if word == word_name:
                list_match_word.append(data_word)
        
        return list_match_word
        

    def _save_data_words(self):
        file_name = simpledialog.askstring("Salvar palavras", "Digite o nome do arquivo (sem extensão):")
        
        if not file_name:
            return  # Usuário cancelou

        MAX_POR_PALAVRA = 2
        contador_por_palavra = {}
        save_words = []

        for dict_match_word in self.list_data_words_in_text:
            palavra = dict_match_word["word"].lower()
            caminho = str(dict_match_word["path"])

            if contador_por_palavra.get(palavra, 0) < MAX_POR_PALAVRA:
                save_words.append(caminho)
                contador_por_palavra[palavra] = contador_por_palavra.get(palavra, 0) + 1

        save_path = Path("database/vocabulary/save_words") / f"{file_name}.json"
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, 'w', encoding="utf-8") as json_file:
            json.dump(save_words, json_file, ensure_ascii=False, indent=4)

        print(f"Palavras salvas em: {save_path}")

    def _listar_palavras_conhecidas(self):
        # Cria janela popup
        popup = tk.Toplevel(self)
        popup.title("Palavras Conhecidas no Texto")

        listbox = tk.Listbox(popup, selectmode=tk.SINGLE, width=50, height=20)
        listbox.pack(padx=10, pady=10)

        # Usar set para evitar repetições
        self.palavras_conhecidas_unicas = sorted(set(
            data['word'] for data in self.list_data_words_in_text
        ))

        for word in self.palavras_conhecidas_unicas:
            listbox.insert(tk.END, word)

        btn_remover = tk.Button(popup, text="Remover Palavra Selecionada", command=lambda: self._remover_palavra_base(listbox))
        btn_remover.pack(pady=(0, 10))

    def _remover_palavra_base(self, listbox):
        selection = listbox.curselection()
        if not selection:
            return

        index = selection[0]
        palavra = self.palavras_conhecidas_unicas[index]

        # Remove todas as ocorrências dessa palavra na base
        self.known_words = [w for w in self.known_words if w["word"] != palavra]

        # Atualiza a listbox
        listbox.delete(index)

        print(f"Palavra removida da base: {palavra}")

    def _manter_palavras_unicas(self):
        text = self.text_widget.get("1.0", tk.END)
        seen = set()
        result = []

        for match in re.finditer(r"[a-zA-Z]+", text):
            word = match.group()
            key = word.lower()

            if key not in seen:
                seen.add(key)
                result.append(word)

        texto_resultante = " ".join(result)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", texto_resultante)

    def _remover_palavras_conhecidas_do_texto(self):
        texto = self.text_widget.get("1.0", tk.END)
        palavras_para_remover = []

        for match in re.finditer(r"[a-zA-Z]+", texto):
            palavra = match.group()
            if self.find_match_word(palavra, self.known_words):
                palavras_para_remover.append(palavra)

        for palavra in set(palavras_para_remover):
            # Remove apenas a palavra completa
            texto = re.sub(rf'\b{re.escape(palavra)}\b', '', texto)

        # Limpa espaços extras e finaliza
        texto = re.sub(r'\s+', ' ', texto).strip()

        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", texto)
        self._process_text()


    def _remover_palavras_desconhecidas_do_texto(self):
        texto = self.text_widget.get("1.0", tk.END)
        palavras_para_remover = []

        for match in re.finditer(r"[a-zA-Z]+", texto):
            palavra = match.group()
            if not self.find_match_word(palavra, self.known_words):
                palavras_para_remover.append(palavra)

        for palavra in set(palavras_para_remover):
            # Remove somente a palavra isolada (com limites de palavra)
            texto = re.sub(rf'\b{re.escape(palavra)}\b', '', texto)

        # Remove espaços duplos e linhas em branco
        texto = re.sub(r'\s+', ' ', texto).strip()

        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", texto)
        self._process_text()

    def _configure_tags(self):
        self.text_widget.tag_config("green", foreground="green")
        self.text_widget.tag_config("gray", foreground="gray")

    def _process_text(self):
        self._clear_tags()
        text = self.text_widget.get("1.0", tk.END)
        self.total_words = self.known_words_count = 0
        self.list_data_words_in_text = []

        for match in re.finditer(r"[a-zA-Z]+", text):
            word = match.group()
            start, end = match.start(), match.end()
            self.total_words += 1

            match_data = self.find_match_word(word, self.known_words)
            if match_data:
                self.known_words_count += 1
                self.list_data_words_in_text.extend(match_data)
                tag = "green"
            else:
                tag = "gray"

            self.text_widget.tag_add(tag, f"1.0+{start}c", f"1.0+{end}c")

        self._show_statistics()

    def _clear_tags(self):
        self.text_widget.tag_remove("green", "1.0", tk.END)
        self.text_widget.tag_remove("gray", "1.0", tk.END)

    def _show_statistics(self):
        total = self.total_words
        known = self.known_words_count
        unknown = total - known
        percent = (known / total * 100) if total else 0

        stats_text = (
            f"Total de palavras: {total}\n"
            f"Conhecidas: {known}\n"
            f"Desconhecidas: {unknown}\n"
            f"Compreensão: {percent:.1f}%"
        )
        self.stats_label.config(text=stats_text)


if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.title("Leitura de Texto")
        app = TextReaderApp(root)
        app.pack(expand=True, fill="both")

        # # Texto inicial (opcional)
        # example_text = """How many-teste pieces you retrieve from your RAG system affects the result."""
        # app.text_widget.insert("1.0", example_text)
        root.mainloop()
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        root.destroy()

