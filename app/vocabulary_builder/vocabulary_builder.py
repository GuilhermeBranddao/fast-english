import tkinter as tk
from tkinter import ttk, messagebox
import random
import inflect

engine = inflect.engine()
# Dados de vocabulário
#word = engine.number_to_words(int(number))
# engine.number_to_words(int(number))

VOCABULARY = {
    "Numbers": {
        "Numbers 0-100": {str(number): engine.number_to_words(number) for number in range(101)},
        #"Large Numbers 100-1000": {str(number): engine.number_to_words(random.randint(100, 1000)) for _ in range(101)},
        #"Large Numbers 1000-1000000": {str(number): engine.number_to_words(random.randint(1000, 1000000)) for _ in range(101)},
        "Ordinal Numbers 0-100": {f"{number}th": engine.ordinal(engine.number_to_words(number)) if number > 0 else "0th" for number in range(101)},
    },
    "Time Expressions": {
        "Dias da Semana": {
            "Segunda-feira": "Monday",
            "Terça-feira": "Tuesday",
            "Quarta-feira": "Wednesday",
            "Quinta-feira": "Thursday",
            "Sexta-feira": "Friday",
            "Sábado": "Saturday",
            "Domingo": "Sunday",
        },
        "Meses do Ano": {
            "Janeiro": "January",
            "Fevereiro": "February",
            "Março": "March",
            "Abril": "April",
            "Maio": "May",
            "Junho": "June",
            "Julho": "July",
            "Agosto": "August",
            "Setembro": "September",
            "Outubro": "October",
            "Novembro": "November",
            "Dezembro": "December"
        },
        "O Calendário": {
            "dia": "day",
            "semana": "week",
            "mês": "month",
            "ano": "year",
            "década": "decade",
            "século": "century"
        }
    },
    "Seasons and Frequency": {
        "Estações": {
            "Primavera": "Spring",
            "Verão": "Summer",
            "Outono": "Autumn",
            "Inverno": "Winter"
        },
        "Frequência": {
            "sempre": "always",
            "frequentemente": "often",
            "às vezes": "sometimes",
            "raramente": "rarely",
            "nunca": "never"
        }
    }
}

# Lógica para gerenciar o quiz
class VocabularyQuiz:
    def __init__(self, root):
        self.root = root
        self.root.title("Vocabulary Quiz")
        self.current_category = None
        self.current_subcategory = None
        self.current_word = None
        self.current_answer = None

        self.setup_ui()

    def setup_ui(self):
        # Frame de seleção de categoria
        self.category_frame = ttk.Frame(self.root, padding=10)
        self.category_frame.pack(fill="both", expand=True)

        ttk.Label(self.category_frame, text="Choose a category:", font=("Arial", 14)).pack(pady=5)
        self.category_combobox = ttk.Combobox(self.category_frame, state="readonly", values=list(VOCABULARY.keys()))
        self.category_combobox.pack(pady=5)
        self.category_combobox.bind("<<ComboboxSelected>>", self.populate_subcategories)

        ttk.Label(self.category_frame, text="Choose a subcategory:", font=("Arial", 14)).pack(pady=5)
        self.subcategory_combobox = ttk.Combobox(self.category_frame, state="readonly")
        self.subcategory_combobox.pack(pady=5)

        self.start_button = ttk.Button(self.category_frame, text="Start Quiz", command=self.start_quiz)
        self.start_button.pack(pady=10)

        # Frame do quiz
        self.quiz_frame = ttk.Frame(self.root, padding=10)

        ttk.Label(self.quiz_frame, text="Translate the following word:", font=("Arial", 14)).pack(pady=10)
        self.word_label = ttk.Label(self.quiz_frame, text="", font=("Arial", 18, "bold"))
        self.word_label.pack(pady=10)

        self.answer_entry = ttk.Entry(self.quiz_frame, font=("Arial", 14))
        self.answer_entry.pack(pady=5)

        self.check_button = ttk.Button(self.quiz_frame, text="Check Answer", command=self.check_answer)
        self.check_button.pack(pady=5)

        self.feedback_label = ttk.Label(self.quiz_frame, text="", font=("Arial", 12))
        self.feedback_label.pack(pady=5)

        self.back_button = ttk.Button(self.quiz_frame, text="Back to Categories", command=self.back_to_categories)
        self.back_button.pack(pady=10)

    def populate_subcategories(self, event):
        category = self.category_combobox.get()
        subcategories = list(VOCABULARY[category].keys())
        self.subcategory_combobox["values"] = subcategories

    def start_quiz(self):
        self.current_category = self.category_combobox.get()
        self.current_subcategory = self.subcategory_combobox.get()

        if not self.current_category or not self.current_subcategory:
            messagebox.showwarning("Selection Error", "Please select both a category and a subcategory!")
            return

        self.category_frame.pack_forget()
        self.quiz_frame.pack(fill="both", expand=True)
        self.next_word()

    def next_word(self):
        words = VOCABULARY[self.current_category][self.current_subcategory]
        self.current_word = random.choice([i for i in words])
        self.current_answer = words[self.current_word]

        self.word_label.config(text=self.current_word)
        self.answer_entry.delete(0, tk.END)
        self.feedback_label.config(text="")

    def check_answer(self):
        user_answer = self.answer_entry.get().strip()
        if user_answer.lower() == self.current_answer.lower():
            self.feedback_label.config(text="Correct!", foreground="green")
        else:
            self.feedback_label.config(text=f"{self.current_answer}", foreground="red")
            print(f"❌: {user_answer}, ✅: {self.current_answer}")
        self.root.after(2000, self.next_word)

    def back_to_categories(self):
        self.quiz_frame.pack_forget()
        self.category_frame.pack(fill="both", expand=True)

# Inicialização da aplicação
if __name__ == "__main__":
    root = tk.Tk()
    quiz_app = VocabularyQuiz(root)
    root.mainloop()
