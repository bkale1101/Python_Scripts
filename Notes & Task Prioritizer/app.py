import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title('Material You To-Do List')
        self.geometry('600x550')
        self.configure(bg='#F3F4F6')  # Light background color
        self.resizable(False, False)

        self.tasks = []

        # Title
        self.title_label = tk.Label(self, text="To-Do List", font=('Roboto', 24, 'bold'), bg='#F3F4F6', fg='#333')
        self.title_label.pack(pady=20)

        # Input Frame
        self.input_frame = tk.Frame(self, bg='#F3F4F6')
        self.input_frame.pack(pady=5)

        self.task_input = tk.Entry(self.input_frame, width=22, font=('Roboto', 14), bd=0, relief='flat', bg='#E0E0E0', fg='#333')
        self.task_input.pack(side='left', padx=5, pady=5)

        # Priority Dropdown
        self.priority_var = tk.StringVar(value='Normal')
        self.priority_dropdown = ttk.Combobox(self.input_frame, textvariable=self.priority_var,
                                               values=["Low", "Normal", "High"], width=10, state='readonly')
        self.priority_dropdown.pack(side='left', padx=5, pady=5)

        self.btn_add_task = tk.Button(self.input_frame, text="Add Task", command=self.add_task, 
                                       bg='#6200EE', fg='white', font=('Roboto', 12), borderwidth=0, relief='flat', padx=10, pady=5)
        self.btn_add_task.pack(side='right', padx=5, pady=5)

        # Listbox Frame with Scrollbar
        self.list_frame = tk.Frame(self)
        self.list_frame.pack(pady=10)

        self.lb_tasks = tk.Listbox(self.list_frame, width=50, height=12, font=('Roboto', 12), 
                                    bg='#FFFFFF', fg='#333', selectbackground='#D1E7DD', borderwidth=0)
        self.lb_tasks.pack(side='left')

        self.scrollbar = tk.Scrollbar(self.list_frame)
        self.scrollbar.pack(side='right', fill='y')

        self.lb_tasks.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.lb_tasks.yview)

        # Button Frame
        self.button_frame = tk.Frame(self, bg='#F3F4F6')
        self.button_frame.pack(pady=10)

        # Task Buttons
        self.btn_delete = tk.Button(self.button_frame, text="Delete", command=self.delete_task, 
                                     bg='#FF5252', fg='white', font=('Roboto', 12), borderwidth=0, relief='flat', width=12)
        self.btn_delete.pack(side='left', padx=5, pady=5)

        self.btn_delete_all = tk.Button(self.button_frame, text="Delete All", command=self.delete_all_tasks, 
                                         bg='#FF5252', fg='white', font=('Roboto', 12), borderwidth=0, relief='flat', width=12)
        self.btn_delete_all.pack(side='left', padx=5, pady=5)

        # Save Buttons
        self.btn_save = tk.Button(self.button_frame, text="Save Task", command=self.save_selected_task, 
                                   bg='#03A9F4', fg='white', font=('Roboto', 12), borderwidth=0, relief='flat', width=12)
        self.btn_save.pack(side='left', padx=5, pady=5)

        self.btn_save_all = tk.Button(self.button_frame, text="Save All Tasks", command=self.save_all_tasks, 
                                       bg='#03A9F4', fg='white', font=('Roboto', 12), borderwidth=0, relief='flat', width=12)
        self.btn_save_all.pack(side='left', padx=5, pady=5)

        # Task Count Label
        self.task_count_label = tk.Label(self, text="", bg='#F3F4F6', font=('Roboto', 12))
        self.task_count_label.pack(pady=5)

        self.update_task_count()

    def add_task(self):
        """Add a new task to the list."""
        task_text = self.task_input.get().strip()
        task_priority = self.priority_var.get()

        if task_text:
            time_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.tasks.append({'task': task_text, 'time_added': time_added, 'priority': task_priority})
            self.update_listbox()
            self.task_input.delete(0, 'end')
            self.update_task_count()
        else:
            messagebox.showwarning("Input Error", "Please enter a task.")

    def delete_task(self):
        """Delete the selected task."""
        selected_task_index = self.lb_tasks.curselection()
        if selected_task_index:
            del self.tasks[selected_task_index[0]]
            self.update_listbox()
            self.update_task_count()
        else:
            messagebox.showwarning("Selection Error", "Please select a task to delete.")

    def delete_all_tasks(self):
        """Clear all tasks from the list."""
        self.tasks = []
        self.update_listbox()
        self.update_task_count()

    def save_selected_task(self):
        """Save the selected task to a file."""
        selected_task_index = self.lb_tasks.curselection()
        if selected_task_index:
            task = self.tasks[selected_task_index[0]]
            with open("./saved_task.txt", "w") as f:
                f.write(f"Task: {task['task']}\nPriority: {task['priority']}\nAdded: {task['time_added']}\n")
            messagebox.showinfo("Save Task", "Selected task saved to 'saved_task.txt'")
        else:
            messagebox.showwarning("Selection Error", "Please select a task to save.")

    def save_all_tasks(self):
        """Save all tasks to a file."""
        if self.tasks:
            with open("all_tasks.txt", "w") as f:
                for task in self.tasks:
                    f.write(f"Task: {task['task']}\nPriority: {task['priority']}\nAdded: {task['time_added']}\n\n")
            messagebox.showinfo("Save All Tasks", "All tasks saved to 'all_tasks.txt'")
        else:
            messagebox.showwarning("No Tasks", "No tasks available to save.")

    def update_listbox(self):
        """Update the task list display."""
        self.lb_tasks.delete(0, "end")
        for task in self.tasks:
            task_display = f"{task['task']} | Priority: {task['priority']} | Added: {task['time_added']}"
            self.lb_tasks.insert("end", task_display)

    def update_task_count(self):
        """Update the task count label."""
        task_count = len(self.tasks)
        self.task_count_label.config(text=f"Number of tasks: {task_count}")


if __name__ == '__main__':
    app = TodoApp()
    app.mainloop()
