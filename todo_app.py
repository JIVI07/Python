import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List App")
        self.root.geometry("500x500")
        self.root.resizable(True, True)
        
        self.data_file = "todo_data.json"
        self.tasks = self.load_tasks()
        self.create_widgets()
        self.refresh_list()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        title_label = ttk.Label(main_frame, text="To-Do List", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Label(main_frame, text="New Task:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.task_entry = ttk.Entry(main_frame, width=40)
        self.task_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        self.task_entry.bind("<Return>", lambda e: self.add_task())
        
        add_btn = ttk.Button(main_frame, text="Add Task", command=self.add_task)
        add_btn.grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=(0, 5))
        
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.task_listbox = tk.Listbox(
            list_frame, 
            height=15, 
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            font=("Arial", 10)
        )
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.task_listbox.yview)
        
        self.task_listbox.bind("<Double-Button-1>", lambda e: self.mark_done())
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        mark_done_btn = ttk.Button(button_frame, text="Mark as Done", command=self.mark_done)
        mark_done_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        delete_btn = ttk.Button(button_frame, text="Delete Task", command=self.delete_task)
        delete_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_btn = ttk.Button(button_frame, text="Clear All", command=self.clear_tasks)
        clear_btn.pack(side=tk.LEFT)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def add_task(self):
        task_text = self.task_entry.get().strip()
        if task_text:
            task = {
                "text": task_text,
                "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "completed": False
            }
            self.tasks.append(task)
            self.save_tasks()
            self.refresh_list()
            self.task_entry.delete(0, tk.END)
            self.status_var.set(f"Task added: {task_text}")
        else:
            messagebox.showwarning("Warning", "Please enter a task.")
    
    def mark_done(self):
        selected = self.task_listbox.curselection()
        if selected:
            index = selected[0]
            self.tasks[index]["completed"] = not self.tasks[index]["completed"]
            self.save_tasks()
            self.refresh_list()
            status = "completed" if self.tasks[index]["completed"] else "marked as not done"
            self.status_var.set(f"Task {status}: {self.tasks[index]['text']}")
        else:
            messagebox.showwarning("Warning", "Please select a task to mark as done.")
    
    def delete_task(self):
        selected = self.task_listbox.curselection()
        if selected:
            index = selected[0]
            task_text = self.tasks[index]["text"]
            if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{task_text}'?"):
                del self.tasks[index]
                self.save_tasks()
                self.refresh_list()
                self.status_var.set(f"Task deleted: {task_text}")
        else:
            messagebox.showwarning("Warning", "Please select a task to delete.")
    
    def clear_tasks(self):
        if self.tasks:
            if messagebox.askyesno("Confirm", "Are you sure you want to clear all tasks?"):
                self.tasks = []
                self.save_tasks()
                self.refresh_list()
                self.status_var.set("All tasks cleared")
        else:
            messagebox.showinfo("Info", "No tasks to clear.")
    
    def refresh_list(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            prefix = "✓ " if task["completed"] else "☐ "
            task_text = f"{prefix}{task['text']} (Added: {task['created']})"
            self.task_listbox.insert(tk.END, task_text)
            
            if task["completed"]:
                self.task_listbox.itemconfig(tk.END, {'fg': 'gray'})
    
    def load_tasks(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def save_tasks(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except IOError:
            messagebox.showerror("Error", "Could not save tasks to file.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()