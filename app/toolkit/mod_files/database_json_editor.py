import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageTk
import json
import random
from app.toolkit.utils.save_data import del_game_task


FONT_SMALL = ("Arial", 10)

class DatabaseJsonEditor:

    def __init__(self, master, task_list: list[dict], task_id:str, on_all_done_callback=None):
        self.master = master
        self.task_list = task_list.copy()
        self.task_id = task_id
        self.on_all_done_callback = on_all_done_callback
        self.entries = {}
        self.delete_task_var = tk.BooleanVar(value=False)
        self.create_editor_window()

    def load_json_data(self, json_path: Path):
        try:
            with open(json_path, 'r', encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            messagebox.showerror("JSON Load Error", str(e))
            return None

    def save_json_data(self, json_path: Path, data: dict):
        try:
            with open(json_path, 'w', encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("JSON Save Error", str(e))

    def create_editor_window(self):
        if not self.task_list:
            return

        if isinstance(self.task_list, list):
            current_task = self.task_list.pop(random.randint(0, len(self.task_list) - 1))
        else: 
            current_task = self.task_list
            
        base_path = Path(current_task["path"].replace("\\", "/"))
        json_path = base_path / "text_v2.json"
        image_path = base_path / "image_text.jpg"

        if not json_path.exists():
            messagebox.showerror("Missing File", f"JSON not found: {json_path}")
            return

        json_data = self.load_json_data(json_path)
        if json_data is None:
            return

        self.editor_window = tk.Toplevel(self.master)
        self.editor_window.title("Edit Word Task")

        current_row = 0
        if image_path.exists():
            try:
                image = Image.open(image_path).resize((200, 200))
                photo = ImageTk.PhotoImage(image)
                image_label = tk.Label(self.editor_window, image=photo)
                image_label.image = photo
                image_label.grid(row=current_row, column=0, columnspan=2, pady=10)
                current_row += 1
            except Exception as e:
                messagebox.showwarning("Image Error", f"Could not load image: {e}")

        self.populate_editable_fields(json_data, current_row)
        self.add_delete_checkbox(current_row + len(self.entries))
        self.add_counter_label(current_row + len(self.entries) + 2)
        self.add_save_button(json_data, json_path, current_row + len(self.entries) + 3)
        self.update_pending_counter()

    def populate_editable_fields(self, json_data: dict, start_row: int):
        editable_keys = ["pergunta_pt-br", "uso_da_linguagem", "tradução_en", "fonetica"]

        for idx, key in enumerate(editable_keys):
            if key in json_data:
                label = tk.Label(self.editor_window, text=key.replace("_", " ").title(), font=FONT_SMALL)
                label.grid(row=start_row + idx, column=0, padx=10, pady=5, sticky="e")

                entry = tk.Entry(self.editor_window, width=60)
                entry.insert(0, json_data[key].capitalize())
                entry.grid(row=start_row + idx, column=1, padx=10, pady=5, sticky="w")

                self.entries[key] = entry

    def add_delete_checkbox(self, row: int):
        delete_checkbox = tk.Checkbutton(
            self.editor_window,
            text="Remove task from database",
            variable=self.delete_task_var,
            font=FONT_SMALL
        )
        delete_checkbox.grid(row=row, column=0, columnspan=2, pady=(5, 0))

    def add_counter_label(self, row: int):
        self.counter_label = tk.Label(self.editor_window, font=FONT_SMALL)
        self.counter_label.grid(row=row, column=0, columnspan=2, pady=(5, 10))

    def update_pending_counter(self):
        remaining = len(self.task_list)
        self.counter_label.config(text=f"{remaining} task(s) remaining")

    def add_save_button(self, json_data: dict, json_path: Path, row: int):
        save_btn = tk.Button(
            self.editor_window,
            text="Save",
            command=lambda: self.save_changes(json_data, json_path),
            font=FONT_SMALL
        )
        save_btn.grid(row=row, column=0, columnspan=2, pady=10)

    def save_changes(self, json_data: dict, json_path: Path):
        for key, entry in self.entries.items():
            json_data[key] = entry.get()

        json_data["status"] = "revised"
        json_data["updated_at"] = datetime.now().isoformat()

        self.save_json_data(json_path, json_data)

        if self.delete_task_var.get():
            del_game_task(id_game_task=self.task_id, game_name="word_shuffle_game")

        if self.task_list:
            self.editor_window.destroy()
            DatabaseJsonEditor(self.master, self.task_list, self.task_id)
        else:
            messagebox.showinfo("Done", "All tasks have been processed.")
            self.editor_window.destroy()
            # if self.on_all_done_callback:
                # self.on_all_done_callback()