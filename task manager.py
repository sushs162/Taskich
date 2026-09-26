import tkinter as tk
from tkinter import messagebox, ttk


class TaskManagerApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Task Manager — Прототип (Windows)")
    self.root.geometry("600x450")
    self.root.minsize(500, 400)

    # Список для хранения задач в памяти (прототип CRUD)
    self.tasks = []

    # --- Верхняя панель ввода ---
    input_frame = ttk.LabelFrame(root, text=" Новая задача ", padding=10)
    input_frame.pack(fill="x", padx=10, pady=10)

    # Название задачи
    ttk.Label(input_frame, text="Название:").grid(
        row=0, column=0, sticky="w", padx=5, pady=5
    )
    self.title_entry = ttk.Entry(input_frame, width=25)
    self.title_entry.grid(row=0, column=1, padx=5, pady=5)

    # Приоритет
    ttk.Label(input_frame, text="Приоритет:").grid(
        row=0, column=2, sticky="w", padx=5, pady=5
    )
    self.priority_cb = ttk.Combobox(
        input_frame,
        values=["Low", "Medium", "High", "Critical"],
        width=10,
        state="readonly",
    )
    self.priority_cb.grid(row=0, column=3, padx=5, pady=5)
    self.priority_cb.current(1)

    # Дедлайн
    ttk.Label(input_frame, text="Дедлайн:").grid(
        row=1, column=0, sticky="w", padx=5, pady=5
    )
    self.deadline_entry = ttk.Entry(input_frame, width=25)
    self.deadline_entry.grid(row=1, column=1, padx=5, pady=5)
    self.deadline_entry.insert(0, "Завтра")

    # Кнопка добавления (Create)
    add_btn = ttk.Button(
        input_frame, text="Добавить задачу", command=self.add_task
    )
    add_btn.grid(row=1, column=2, columnspan=2, sticky="ew", padx=5, pady=5)

    # --- Центральная область (Список задач - Read) ---
    list_frame = ttk.LabelFrame(root, text=" Список задач ", padding=10)
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # Древовидная таблица для красивого отображения
    columns = ("Title", "Priority", "Deadline")
    self.tree = ttk.Treeview(
        list_frame, columns=columns, show="headings", selectmode="browse"
    )

    self.tree.heading("Title", text="Название")
    self.tree.heading("Priority", text="Приоритет")
    self.tree.heading("Deadline", text="Дедлайн")

    self.tree.column("Title", width=250, anchor="w")
    self.tree.column("Priority", width=100, anchor="center")
    self.tree.column("Deadline", width=120, anchor="center")

    scrollbar = ttk.Scrollbar(
        list_frame, orient="vertical", command=self.tree.yview
    )
    self.tree.configure(yscrollcommand=scrollbar.set)

    self.tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # --- Нижняя панель управления (Delete / Update элементы) ---
    btn_frame = ttk.Frame(root, padding=10)
    btn_frame.pack(fill="x", padx=10, pady=5)

    delete_btn = ttk.Button(
        btn_frame, text="Удалить выбранную задачу", command=self.delete_task
    )
    delete_btn.pack(side="right", padx=5)

  def add_task(self):
    title = self.title_entry.get().strip()
    priority = self.priority_cb.get()
    deadline = self.deadline_entry.get().strip()

    if not title:
      messagebox.showerror(
          "Ошибка", "Название задачи не может быть пустым!"
      )
      return

    # Добавление в локальную структуру данных
    task = {"title": title, "priority": priority, "deadline": deadline}
    self.tasks.append(task)

    # Отображение в UI
    self.tree.insert("", "end", values=(title, priority, deadline))

    # Очистка полей ввода
    self.title_entry.delete(0, tk.END)
    messagebox.info(
        "Успех", f"Задача '{title}' успешно создана!", icon="info"
    ) if hasattr(messagebox, "info") else messagebox.showinfo(
        "Успех", f"Задача '{title}' успешно создана!"
    )

  def delete_task(self):
    selected_item = self.tree.selection()
    if not selected_item:
      messagebox.showwarning(
          "Внимание", "Выберите задачу из списка для удаления!"
      )
      return

    # Получаем индекс выбранного элемента
    item_index = self.tree.index(selected_item[0])

    # Удаляем из визуального списка и из структуры данных
    self.tree.delete(selected_item)
    removed_task = self.tasks.pop(item_index)
    messagebox.showinfo("Успех", f"Задача '{removed_task['title']}' удалена.")


if __name__ == "__main__":
  root = tk.Tk()
  app = TaskManagerApp(root)
  root.mainloop()