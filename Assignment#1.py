from tkinter import *
window = Tk()
window.geometry("400x300")
window.title("Hello World")

Canvas = Canvas(window, width=400, height=300)
Canvas.pack()

Canvas.create_rectangle(50, 50, 350, 250, fill="lightblue")
Canvas.create_oval(100, 50, 300, 250, fill="yellow")
Canvas.create_line(150, 150, 250, 150, fill="black", width=2)
Canvas.create_line(200, 100, 200, 200, fill="black", width=2)
Canvas.create_text(200, 265, text="Salim, Addymen", font=("Arial", 12, "bold"), fill="black")
Canvas.create_text(200, 285, text="BSIT-3PM", font=("Arial", 12, "bold"), fill="black") 



window.mainloop()
