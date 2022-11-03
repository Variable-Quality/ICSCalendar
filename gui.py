from tkinter import *
from tkinter import ttk

root = Tk()
root.title("Test Calendar Interface")
root.iconphoto(False, PhotoImage(file="bin/robot face.png"))
root.minsize(150,150)

frm = ttk.Frame(root, padding=10)
ttk.Label(frm, text="Burger king foot lettuce").grid(column=0, row=0)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=1)
frm.pack()
root.mainloop()

