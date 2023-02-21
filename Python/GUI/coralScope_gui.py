import tkinter as tk
import os
import time
from PIL import Image, ImageTk

root = tk.Tk()

# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen


root.title("coralScope")
# create a full screen window
root.geometry('%dx%d+%d+%d' % (ws, hs, 0, 0))
root.configure(bg='white')

# display logo
load = Image.open("coralscope_logo.png")
resize_image  = load.resize((100,100))
render = ImageTk.PhotoImage(resize_image)
img = tk.Label(image=render)
img.image = render
img.place(x=25, y=25)

# Status text
logo_label = tk.Label(root, text="CoralScope",font=("Arial", 25))
logo_label.place(x=150, y=25)

root.mainloop()