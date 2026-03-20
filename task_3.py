import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
import sqlite3

URL = "https://www.cbr-xml-daily.ru/daily_json.js"
DB_NAME = "currency.db"


class CurrencyMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Монитор валют")
        self.root.geometry("600x500")

        self.currencies = {}
        self.init_db()
        self.load_currencies()
        self.create_widgets()

    def init_db(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS group_currencies (
                group_id INTEGER,
                currency_code TEXT,
                FOREIGN KEY (group_id) REFERENCES groups (id)
            )
        ''')
        conn.commit()
        conn.close()

    def load_currencies(self):
        try:
            response = requests.get(URL)
            data = response.json()
            self.currencies = data["Valute"]
        except:
            messagebox.showerror("Ошибка", "Не удалось загрузить курсы валют")

    def get_groups(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM groups")
        groups = cur.fetchall()
        conn.close()
        return groups

    def get_group_currencies(self, group_id):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT currency_code FROM group_currencies WHERE group_id = ?", (group_id,))
        currencies = [row[0] for row in cur.fetchall()]
        conn.close()
        return currencies

    def add_group(self, name):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO groups (name) VALUES (?)", (name,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def delete_group(self, name):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id FROM groups WHERE name = ?", (name,))
        group = cur.fetchone()
        if group:
            cur.execute("DELETE FROM group_currencies WHERE group_id = ?", (group[0],))
            cur.execute("DELETE FROM groups WHERE name = ?", (name,))
            conn.commit()
        conn.close()

    def add_currency_to_group(self, group_name, currency_code):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id FROM groups WHERE name = ?", (group_name,))
        group = cur.fetchone()
        if group:
            cur.execute("SELECT * FROM group_currencies WHERE group_id = ? AND currency_code = ?",
                        (group[0], currency_code))
            if not cur.fetchone():
                cur.execute("INSERT INTO group_currencies (group_id, currency_code) VALUES (?, ?)",
                            (group[0], currency_code))
                conn.commit()
                conn.close()
                return True
        conn.close()
        return False

    def remove_currency_from_group(self, group_name, currency_code):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id FROM groups WHERE name = ?", (group_name,))
        group = cur.fetchone()
        if group:
            cur.execute("DELETE FROM group_currencies WHERE group_id = ? AND currency_code = ?",
                        (group[0], currency_code))
            conn.commit()
        conn.close()

    def create_widgets(self):
        tab_control = ttk.Notebook(self.root)

        tab_all = ttk.Frame(tab_control)
        tab_control.add(tab_all, text="Все валюты")

        self.all_list = tk.Listbox(tab_all, width=70, height=20)
        self.all_list.pack(padx=10, pady=10)

        for code in self.currencies:
            c = self.currencies[code]
            self.all_list.insert(tk.END, f"{code}: {c['Nominal']} {c['Name']} = {c['Value']} руб.")

        tk.Button(tab_all, text="Найти валюту", command=self.find_currency).pack(pady=5)

        tab_groups = ttk.Frame(tab_control)
        tab_control.add(tab_groups, text="Группы")

        self.groups_list = tk.Listbox(tab_groups, width=70, height=15)
        self.groups_list.pack(padx=10, pady=10)
        self.groups_list.bind('<<ListboxSelect>>', self.show_group_currencies)

        btn_frame = tk.Frame(tab_groups)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Создать группу", command=self.create_group).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Добавить валюту", command=self.add_currency).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить валюту", command=self.remove_currency).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить группу", command=self.delete_group_ui).pack(side=tk.LEFT, padx=5)

        self.currency_list = tk.Listbox(tab_groups, width=70, height=8)
        self.currency_list.pack(padx=10, pady=10)

        tab_control.pack(expand=1, fill="both")

        self.update_groups_list()

    def find_currency(self):
        code = simpledialog.askstring("Поиск", "Введите код валюты (например USD):")
        if code:
            code = code.upper()
            if code in self.currencies:
                c = self.currencies[code]
                messagebox.showinfo("Валюта", f"{code}: {c['Nominal']} {c['Name']} = {c['Value']} руб.")
            else:
                messagebox.showerror("Ошибка", "Валюта не найдена")

    def create_group(self):
        name = simpledialog.askstring("Создать группу", "Введите название группы:")
        if name:
            if self.add_group(name):
                self.update_groups_list()
                messagebox.showinfo("Успех", f"Группа '{name}' создана")
            else:
                messagebox.showerror("Ошибка", "Такая группа уже есть")

    def delete_group_ui(self):
        selection = self.groups_list.curselection()
        if not selection:
            messagebox.showerror("Ошибка", "Выберите группу")
            return

        group = self.groups_list.get(selection[0])
        confirm = messagebox.askyesno("Подтверждение", f"Удалить группу '{group}'?")
        if confirm:
            self.delete_group(group)
            self.update_groups_list()
            self.currency_list.delete(0, tk.END)
            messagebox.showinfo("Успех", f"Группа '{group}' удалена")

    def add_currency(self):
        selection = self.groups_list.curselection()
        if not selection:
            messagebox.showerror("Ошибка", "Выберите группу")
            return

        group = self.groups_list.get(selection[0])

        code = simpledialog.askstring("Добавить валюту", "Введите код валюты (например USD):")
        if code:
            code = code.upper()
            if code in self.currencies:
                if self.add_currency_to_group(group, code):
                    self.show_group_currencies()
                    messagebox.showinfo("Успех", f"{code} добавлен в группу")
                else:
                    messagebox.showerror("Ошибка", "Такая валюта уже есть в группе")
            else:
                messagebox.showerror("Ошибка", "Валюта не найдена")

    def remove_currency(self):
        selection = self.groups_list.curselection()
        if not selection:
            messagebox.showerror("Ошибка", "Выберите группу")
            return

        group = self.groups_list.get(selection[0])

        curr_selection = self.currency_list.curselection()
        if not curr_selection:
            messagebox.showerror("Ошибка", "Выберите валюту из списка")
            return

        code = self.currency_list.get(curr_selection[0]).split(":")[0]

        self.remove_currency_from_group(group, code)
        self.show_group_currencies()
        messagebox.showinfo("Успех", f"{code} удален из группы")

    def update_groups_list(self):
        self.groups_list.delete(0, tk.END)
        groups = self.get_groups()
        for group in groups:
            self.groups_list.insert(tk.END, group[1])

    def show_group_currencies(self, event=None):
        self.currency_list.delete(0, tk.END)

        selection = self.groups_list.curselection()
        if selection:
            group_name = self.groups_list.get(selection[0])
            groups = self.get_groups()
            group_id = None
            for g in groups:
                if g[1] == group_name:
                    group_id = g[0]
                    break

            if group_id:
                currencies = self.get_group_currencies(group_id)
                for code in currencies:
                    if code in self.currencies:
                        c = self.currencies[code]
                        self.currency_list.insert(tk.END, f"{code}: {c['Value']} руб.")
                    else:
                        self.currency_list.insert(tk.END, f"{code}: нет данных")


root = tk.Tk()
app = CurrencyMonitor(root)
root.mainloop()