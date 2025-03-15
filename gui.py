import tkinter as tk

def handle_button_press(win,func):
    # win.destroy()
    func()

def window(func):

    window = tk.Tk()
    window.geometry("400x400")
    window.title("OSLP")
    button = tk.Button(window,text="My simple app.", command=lambda: handle_button_press(window,func))
    button = tk.Button(window,text="Stop", command=lambda: handle_button_press(window,func))
    button.pack()
    # Start the event loop.
    window.mainloop()