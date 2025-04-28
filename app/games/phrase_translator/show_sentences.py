import asyncio
import tkinter as tk
from tkinter import messagebox
from deep_translator import GoogleTranslator

# Exemplo de texto
text = """This is an example sentence to test the interface."""

# Função para traduzir sentenças
def translate_sentences(sentence, source_lang="en", target_lang="pt"):
    translator = GoogleTranslator(source=source_lang, target=target_lang)
    try:
        translation = translator.translate(sentence)
    except Exception as e:
        print(f"Erro ao traduzir a frase '{sentence}': {e}")
        translation = "Erro na tradução"
    return translation

# Função para exibir sentenças no Tkinter
def display_sentence(sentence, list_sentence, index, text_widget, text_translate_widget, result_list, save_button, skip_button):
    text_widget.delete(1.0, tk.END)
    text_translate_widget.delete(1.0, tk.END)
    text_widget.insert(tk.END, sentence)

    def save_sentence():
        result_list.append(sentence)
        next_sentence()

    def next_sentence():
        if index < len(list_sentence) - 1:
            display_sentence(list_sentence[index + 1], list_sentence, index + 1, text_widget, text_translate_widget, result_list, save_button, skip_button)
        else:
            messagebox.showinfo("Fim", "Não há mais sentenças para exibir.")
            window.quit()

    save_button.config(command=save_sentence)
    skip_button.config(command=next_sentence)

# Função para exibir tradução
def display_translate(sentence, text_translate_widget):
    text_translate_widget.delete(1.0, tk.END)
    translated_sentence = translate_sentences(sentence)
    text_translate_widget.insert(tk.END, translated_sentence)

# Função principal
def main(text):
    list_sentences = text.split("\n")
    result_list = []

    window = tk.Tk()
    window.title("Interface Responsiva")

    # Criação do frame principal
    main_frame = tk.Frame(window)
    main_frame.pack(fill="both", expand=True)

    # Configuração da área de texto original
    text_widget = tk.Text(main_frame, height=5)
    text_widget.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    # Configuração da área de texto traduzida
    text_translate_widget = tk.Text(main_frame, height=5)
    text_translate_widget.pack(side="right", fill="both", expand=True, padx=5, pady=5)

    # Botões
    button_frame = tk.Frame(window)
    button_frame.pack(fill="x", pady=5)

    save_button = tk.Button(button_frame, text="Salvar")
    save_button.pack(side="left", padx=5)

    skip_button = tk.Button(button_frame, text="Pular")
    skip_button.pack(side="left", padx=5)

    translate_button = tk.Button(button_frame, text="Traduzir")
    translate_button.pack(side="left", padx=5)

    def show_translation():
        sentence = text_widget.get(1.0, tk.END).strip()
        display_translate(sentence, text_translate_widget)

    translate_button.config(command=show_translation)

    display_sentence(list_sentences[0], list_sentences, 0, text_widget, text_translate_widget, result_list, save_button, skip_button)

    # Configura redimensionamento dos widgets
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)

    window.mainloop()
    return result_list

with open("app/database/txt/text.txt", 'r') as f:
    text = f.read()
# Chama a função principal e obtém as sentenças salvas
saved_sentences = main(text)

# Executa o programa
saved_sentences = main(text)
print("Sentenças salvas:", saved_sentences)


