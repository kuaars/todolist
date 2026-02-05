import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import sqlite3

root = Tk()
root.title("Простой список задач")
root.geometry("700x700")

connection = sqlite3.connect('todolist.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS todolist (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE
)
''')
connection.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES todolist(user_id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE
)
''')
connection.commit()

current_user_id = None

def adduser():
    global current_user_id

    verificate = Toplevel(root)
    verificate.geometry("400x200")
    verificate.title("Проверка")

    label = Label(verificate, text='Введите логин')
    label.pack(pady=10)

    username_entry = Entry(verificate, width=30, font=("Arial", 12))
    username_entry.pack(pady=5)

    def user():
        global current_user_id
        username = username_entry.get().strip()

        if username:
            cursor.execute("SELECT user_id FROM todolist WHERE username = ?", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                current_user_id = existing_user[0]
                verificate.destroy()
                messagebox.showinfo('Успех', f'Добро пожаловать, {username}!')
                load_tasks()
            else:
                cursor.execute('INSERT INTO todolist (username) VALUES (?)', (username,))
                connection.commit()

                cursor.execute("SELECT user_id FROM todolist WHERE username = ?", (username,))
                new_user = cursor.fetchone()

                if new_user:
                    current_user_id = new_user[0]
                    verificate.destroy()
                    messagebox.showinfo('Успех', f'Пользователь {username} создан!')
                else:
                    messagebox.showerror('Ошибка', 'Не удалось создать пользователя')
        else:
            messagebox.showinfo('Info', 'Please enter your username')

    add = ttk.Button(verificate, text='Проверить', command=user)
    add.pack(pady=5)

def load_tasks():
    global current_user_id
    if current_user_id is not None:
        listbox.delete(0, END)
        cursor.execute("SELECT title, date FROM tasks WHERE user_id = ?", (current_user_id,))
        tasks = cursor.fetchall()
        for task in tasks:
            listbox.insert(END, f"{task[0]} - {task[1]}")

def add_task():
    global current_user_id

    if current_user_id is None:
        messagebox.showwarning('Ошибка', 'Сначала войдите в систему!')
        return

    task = entrytask.get().strip()
    date = entrydate.get().strip()

    if task and date:
        cursor.execute('''
                       INSERT INTO tasks (user_id, title, date)
                       VALUES (?, ?, ?)
                       ''', (current_user_id, task, date))
        connection.commit()

        listbox.insert(END, f"{task} - {date}")

        entrytask.delete(0, END)
        entrydate.delete(0, END)

        messagebox.showinfo('Успех', 'Задача добавлена!')
    else:
        messagebox.showwarning('Ошибка', 'Заполните все поля!')

frame = Frame(root)
frame.pack(pady=20)

Label(frame, text="Задача:", font=("Arial", 12)).grid(row=0, column=0, padx=5)
entrytask = Entry(frame, width=30, font=("Arial", 12))
entrytask.grid(row=0, column=1, padx=5)

Label(frame, text="Дата:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5)
entrydate = Entry(frame, width=30, font=("Arial", 12))
entrydate.grid(row=1, column=1, padx=5, pady=5)

add = ttk.Button(frame, text='Добавить', command=add_task)
add.grid(row=2, column=0, columnspan=2, pady=10)

listbox = Listbox(
    root,
    width=60,
    height=30,
    font=("Arial", 12),
    selectmode=SINGLE
)
listbox.pack(pady=20)

adduser()
root.mainloop()
connection.close()