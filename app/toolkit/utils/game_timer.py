
import tkinter as tk
import time

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
