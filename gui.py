import tkinter as tk
import queue

class gui:
    def __init__(self,root):
        # button = tk.Button(self.root,text="My simple app.", command=lambda: self.handle_button_press(self.root,func))
        self.root = root
        self.queue = queue.Queue()
        self.root.after(100, self.process_queue)
        # button.pack()

    def process_queue(self):
        """Process all pending GUI updates in the main thread"""
        while not self.queue.empty():
            try:
                task = self.queue.get_nowait()
                task()
            except queue.Empty:
                pass
        self.root.after(100, self.process_queue)
    
    def add_task(self, task):
        """Add a GUI update task to the queue"""
        self.queue.put(task)

    def add_func(self,func):
        new_button = tk.Button(self.root,text="new_button", command=func)
        new_button.pack()

    def handle_button_press(self,win,func):
        # win.destroy()
        func()
