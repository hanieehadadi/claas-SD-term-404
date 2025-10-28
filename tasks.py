import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from plyer import notification
from datetime import datetime

# -----------------------------
# تنظیمات اولیه دیتابیس
# -----------------------------
conn = sqlite3.connect("tasks.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    due_date TEXT,
    done INTEGER DEFAULT 0
)
""")
conn.commit()

# -----------------------------
# توابع اصلی
# -----------------------------
def refresh(filter_type="all"):
    """به‌روزرسانی جدول بر اساس فیلتر انتخاب‌شده"""
    for row in tree.get_children():
        tree.delete(row)

    if filter_type == "done":
        cur.execute("SELECT * FROM tasks WHERE done=1 ORDER BY due_date")
    elif filter_type == "pending":
        cur.execute("SELECT * FROM tasks WHERE done=0 ORDER BY due_date")
    else:
        cur.execute("SELECT * FROM tasks ORDER BY due_date")

    for row in cur.fetchall():
        color = "#5cb85c" if row[3] else "#f0ad4e"
        tree.insert("", tk.END, values=row, tags=("colored",))
        tree.tag_configure("colored", background=color)

def add_task():
    title = entry_title.get().strip()
    due_date = entry_date.get().strip()

    if not title:
        messagebox.showwarning("خطا", "عنوان نمی‌تواند خالی باش،عنوان باید تکمیل شود!")
        return

    cur.execute("INSERT INTO tasks (title, due_date) VALUES (?, ?)", (title, due_date))
    conn.commit()
    entry_title.delete(0, tk.END)
    entry_date.delete(0, tk.END)
    refresh(filter_var.get())

def delete_task():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("اخطار", "هیچ وظیفه‌ای انتخاب نشده است.")
        return

    for sel in selected:
        task_id = tree.item(sel)["values"][0]
        cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    refresh(filter_var.get())

def complete_task():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("اخطار", "ابتدا یک وظیفه انتخاب کنید.")
        return
    for sel in selected:
        task_id = tree.item(sel)["values"][0]
        cur.execute("UPDATE tasks SET done=1 WHERE id=?", (task_id,))
    conn.commit()
    refresh(filter_var.get())

def edit_task():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("اخطار", "هیچ وظیفه‌ای انتخاب نشده است.")
        return
    item = tree.item(selected[0])["values"]
    new_title = entry_title.get().strip()
    new_date = entry_date.get().strip()
    if not new_title:
        messagebox.showwarning("خطا", "عنوان جدید نمی‌تواند خالی باشد.")
        return
    cur.execute("UPDATE tasks SET title=?, due_date=? WHERE id=?", (new_title, new_date, item[0]))
    conn.commit()
    entry_title.delete(0, tk.END)
    entry_date.delete(0, tk.END)
    refresh(filter_var.get())

def notify_today_tasks():
    today = datetime.today().strftime("%Y-%m-%d")
    cur.execute("SELECT title FROM tasks WHERE due_date=? AND done=0", (today,))
    tasks = [t[0] for t in cur.fetchall()]
    if tasks:
        notification.notify(
            title="یادآوری وظایف امروز 🕒",
            message="\n".join(tasks),
            timeout=10
        )

# -----------------------------
# رابط کاربری Tkinter
# -----------------------------
root = tk.Tk()
root.title("🧠 مدیریت وظایف حرفه‌ای")
root.geometry("700x550")
root.config(bg="#222")

style = ttk.Style()
style.configure("Treeview", font=("Vazirmatn", 11), rowheight=28)
style.configure("Treeview.Heading", font=("Vazirmatn", 12, "bold"))
style.map("Treeview", background=[("selected", "#337ab7")])

# بخش ورودی
frame_top = tk.Frame(root, bg="#333", pady=10)
frame_top.pack(fill=tk.X)

tk.Label(frame_top, text="عنوان وظیفه:", fg="white", bg="#333", font=("Vazirmatn", 12)).pack(side=tk.LEFT, padx=5)
entry_title = tk.Entry(frame_top, width=30, font=("Vazirmatn", 12))
entry_title.pack(side=tk.LEFT, padx=5)

tk.Label(frame_top, text="تاریخ (YYYY-MM-DD):", fg="white", bg="#333", font=("Vazirmatn", 12)).pack(side=tk.LEFT, padx=5)
entry_date = tk.Entry(frame_top, width=15, font=("Vazirmatn", 12))
entry_date.pack(side=tk.LEFT, padx=5)

# دکمه‌ها
frame_buttons = tk.Frame(root, bg="#222")
frame_buttons.pack(pady=10)

btn_add = tk.Button(frame_buttons, text="➕ افزودن", bg="#5cb85c", fg="white", font=("Vazirmatn", 12), command=add_task)
btn_add.grid(row=0, column=0, padx=5)

btn_edit = tk.Button(frame_buttons, text="✏️ ویرایش", bg="#0275d8", fg="white", font=("Vazirmatn", 12), command=edit_task)
btn_edit.grid(row=0, column=1, padx=5)

btn_done = tk.Button(frame_buttons, text="✅ انجام شد", bg="#f0ad4e", fg="white", font=("Vazirmatn", 12), command=complete_task)
btn_done.grid(row=0, column=2, padx=5)

btn_delete = tk.Button(frame_buttons, text="🗑️ حذف", bg="#d9534f", fg="white", font=("Vazirmatn", 12), command=delete_task)
btn_delete.grid(row=0, column=3, padx=5)

# جدول وظایف
columns = ("id", "title", "due_date", "done")
tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="extended")
tree.heading("id", text="ردیف")
tree.heading("title", text="عنوان")
tree.heading("due_date", text="تاریخ انجام")
tree.heading("done", text="وضعیت")

tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# فیلتر
frame_filter = tk.Frame(root, bg="#222")
frame_filter.pack(pady=10)

filter_var = tk.StringVar(value="all")
tk.Radiobutton(frame_filter, text="همه", variable=filter_var, value="all", bg="#222", fg="white", font=("Vazirmatn", 11), command=lambda: refresh("all")).pack(side=tk.LEFT, padx=10)
tk.Radiobutton(frame_filter, text="انجام‌نشده", variable=filter_var, value="pending", bg="#222", fg="white", font=("Vazirmatn", 11), command=lambda: refresh("pending")).pack(side=tk.LEFT, padx=10)
tk.Radiobutton(frame_filter, text="انجام‌شده", variable=filter_var, value="done", bg="#222", fg="white", font=("Vazirmatn", 11), command=lambda: refresh("done")).pack(side=tk.LEFT, padx=10)

# فراخوانی
refresh()
notify_today_tasks()

root.mainloop()
