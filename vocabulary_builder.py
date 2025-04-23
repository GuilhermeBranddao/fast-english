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
        "Numbers 0-100": {str(number):engine.number_to_words(int(number)) for number in range(101)},
        "Ordinal Numbers 0-100": [f"{i}th" if i > 0 else "0th" for i in range(101)],
    },
    "Time Expressions": {
        "Days of the Week": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "Months of the Year": [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ],
        "The Calendar": ["day", "week", "month", "year", "decade", "century"]
    },
    "Seasons and Frequency": {
        "Seasons": ["Spring", "Summer", "Autumn", "Winter"],
        "Frequency": ["always", "often", "sometimes", "rarely", "never"]
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
        breakpoint()
        self.current_word = random.choice(words)
        self.word_label.config(text=self.current_word)
        self.answer_entry.delete(0, tk.END)
        self.feedback_label.config(text="")

    def check_answer(self):
        user_answer = self.answer_entry.get().strip()
        if user_answer.lower() == self.current_word.lower():
            self.feedback_label.config(text="Correct!", foreground="green")
        else:
            self.feedback_label.config(text=f"Wrong! Correct answer: {self.current_word}", foreground="red")
        self.root.after(2000, self.next_word)

    def back_to_categories(self):
        self.quiz_frame.pack_forget()
        self.category_frame.pack(fill="both", expand=True)

# Inicialização da aplicação
if __name__ == "__main__":
    root = tk.Tk()
    quiz_app = VocabularyQuiz(root)
    root.mainloop()
