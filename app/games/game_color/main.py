import tkinter
import random

class ColorGame(tkinter.Frame):
    def __init__(self, parent=None, **kwargs):
        tkinter.Frame.__init__(self, parent, **kwargs)
        self.parent = parent
        self.colours = ['Red', 'Blue', 'Green', 'Pink', 'Black',
                        'Yellow', 'Orange', 'White', 'Purple', 'Brown']
        self.score = 0
        self.timeleft = 30
        self.running = False  # Flag to indicate if the game is running

        self.instructions = tkinter.Label(self, text="Type in the colour of the words, and not the word text!",
                                         font=('Helvetica', 12))
        self.instructions.pack()

        self.scoreLabel = tkinter.Label(self, text="Press enter to start",
                                        font=('Helvetica', 12))
        self.scoreLabel.pack()

        self.timeLabel = tkinter.Label(self, text="Time left: " + str(self.timeleft),
                                      font=('Helvetica', 12))
        self.timeLabel.pack()

        self.label = tkinter.Label(self, font=('Helvetica', 60))
        self.label.pack()

        self.entry = tkinter.Entry(self)
        self.entry.pack()
        self.entry.focus_set()
        self.entry.bind('<Return>', self.startGame)

        self.nextColour() # Initial call to set up the first color

    def startGame(self, event):
        if not self.running:
            self.running = True
            self.score = 0
            self.timeleft = 30
            self.scoreLabel.config(text="Score: " + str(self.score))
            self.timeLabel.config(text="Time left: " + str(self.timeleft))
            self.countdown()
        self.nextColour()

    def nextColour(self):
        if self.running and self.timeleft > 0:
            self.entry.focus_set()
            if self.entry.get().lower() == self.colours[1].lower():
                self.score += 1
                self.scoreLabel.config(text="Score: " + str(self.score))
            self.entry.delete(0, tkinter.END)
            random.shuffle(self.colours)
            self.label.config(fg=str(self.colours[1]), text=str(self.colours[0]))

    def countdown(self):
        if self.running and self.timeleft > 0:
            self.timeleft -= 1
            self.timeLabel.config(text="Time left: " + str(self.timeleft))
            self.after(1000, self.countdown)
        elif self.running:
            self.running = False
            self.scoreLabel.config(text="Game Over! Final Score: " + str(self.score))

# if __name__ == '__main__':
#     root = tkinter.Tk()
#     root.title("COLORGAME")
#     game = ColorGame(root)
#     game.pack(expand=True, fill='both')
#     root.geometry("375x200")
#     root.mainloop()