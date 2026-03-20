import sqlite3


def init_db():
    conn = sqlite3.connect('resource/drink_shop.db')
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS drinks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            strength REAL,
            price REAL,
            quantity INTEGER
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            quantity INTEGER
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS cocktails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            strength REAL,
            recipe TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            item TEXT,
            quantity INTEGER,
            total REAL
        )
    ''')

    conn.commit()
    conn.close()


def add_drink():
    print("\n--- Добавление напитка ---")
    name = input("Название: ")
    strength = float(input("Крепость (%): "))
    price = float(input("Цена: "))
    quantity = int(input("Количество: "))

    conn = sqlite3.connect('resource/drink_shop.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO drinks (name, strength, price, quantity) VALUES (?, ?, ?, ?)",
                (name, strength, price, quantity))
    conn.commit()
    conn.close()
    print("Напиток добавлен!")


def add_ingredient():
    print("\n--- Добавление ингредиента ---")
    name = input("Название: ")
    price = float(input("Цена: "))
    quantity = int(input("Количество: "))

    conn = sqlite3.connect('resource/drink_shop.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO ingredients (name, price, quantity) VALUES (?, ?, ?)",
                (name, price, quantity))
    conn.commit()
    conn.close()
    print("Ингредиент добавлен!")


def view_stock():
    conn = sqlite3.connect('resource/drink_shop.db')
    cur = conn.cursor()

    print("\n==================================================")
    print("АЛКОГОЛЬНЫЕ НАПИТКИ:")
    cur.execute("SELECT * FROM drinks")
    drinks = cur.fetchall()
    if drinks:
        for d in drinks:
            print(f"ID:{d[0]} | {d[1]} | {d[2]}% | {d[3]} руб | {d[4]} шт")
    else:
        print("Нет напитков")

    print("\nИНГРЕДИЕНТЫ:")
    cur.execute("SELECT * FROM ingredients")
    ingredients = cur.fetchall()
    if ingredients:
        for i in ingredients:
            print(f"ID:{i[0]} | {i[1]} | {i[2]} руб | {i[3]} шт")
    else:
        print("Нет ингредиентов")

    conn.close()
    print()


def add_cocktail():
    print("\n--- Добавление коктейля ---")
    name = input("Название: ")

    conn = sqlite3.connect('resource/drink_shop.db')
    cur = conn.cursor()

    print("\nДоступные напитки:")
    cur.execute("SELECT id, name, strength FROM drinks")
    drinks = cur.fetchall()
    for d in drinks:
        print(f"ID:{d[0]} | {d[1]} | {d[2]}%")

    print("\nДоступные ингредиенты:")
    cur.execute("SELECT id, name FROM ingredients")
    ingredients = cur.fetchall()
    for i in ingredients:
        print(f"ID:{i[0]} | {i[1]}")

    print("\nВведите рецепт в формате: id:количество,id:количество")
    print("Пример: 1:50,2:30")
    recipe = input("Рецепт: ")
    price = float(input("Цена коктейля: "))

    total_volume = 0
    total_alcohol = 0
    parts = recipe.split(',')
    for part in parts:
        if ':' in part:
            pid, amount = part.split(':')
            amount = float(amount)
            total_volume += amount
            cur.execute("SELECT strength FROM drinks WHERE id = ?", (pid,))
            res = cur.fetchone()
            if res:
                total_alcohol += amount * (res[0] / 100)

    if total_volume > 0:
        strength = (total_alcohol / total_volume) * 100
    else:
        strength = 0

    cur.execute("INSERT INTO cocktails (name, price, strength, recipe) VALUES (?, ?, ?, ?)",
                (name, price, strength, recipe))
    conn.commit()
    conn.close()

    print(f"Коктейль добавлен! Крепость: {strength:.1f}%")


def view_cocktails():
    conn = sqlite3.connect('resource/drink_shop.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM cocktails")
    cocktails = cur.fetchall()
    conn.close()

    if not cocktails:
        print("\nНет коктейлей\n")
        return

    print("\n==================================================")
    print("КОКТЕЙЛИ:")
    for c in cocktails:
        print(f"ID:{c[0]} | {c[1]} | Крепость:{c[3]:.1f}% | Цена:{c[2]} руб")
    print()


def check_stock_for_cocktail(recipe):
    conn = sqlite3.connect('resource/drink_shop.db')
    cur = conn.cursor()

    parts = recipe.split(',')
    for part in parts:
        if ':' in part:
            pid, amount = part.split(':')
            amount = float(amount)

            cur.execute("SELECT quantity FROM drinks WHERE id = ?", (pid,))
            res = cur.fetchone()
            if res:
                if res[0] < amount:
                    conn.close()
                    return False

            cur.execute("SELECT quantity FROM ingredients WHERE id = ?", (pid,))
            res = cur.fetchone()
            if res:
                if res[0] < amount:
                    conn.close()
                    return False

    conn.close()
    return True


def update_stock_for_cocktail(recipe):
    conn = sqlite3.connect('resource/drink_shop.db')
    cur = conn.cursor()

    parts = recipe.split(',')
    for part in parts:
        if ':' in part:
            pid, amount = part.split(':')
            amount = float(amount)

            cur.execute("UPDATE drinks SET quantity = quantity - ? WHERE id = ?", (amount, pid))
            if cur.rowcount == 0:
                cur.execute("UPDATE ingredients SET quantity = quantity - ? WHERE id = ?", (amount, pid))

    conn.commit()
    conn.close()


def sell_cocktail():
    view_cocktails()

    try:
        cid = int(input("\nВведите ID коктейля: "))

        conn = sqlite3.connect('resource/drink_shop.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM cocktails WHERE id = ?", (cid,))
        cocktail = cur.fetchone()

        if not cocktail:
            print("Коктейль не найден!")
            conn.close()
            return

        quantity = int(input("Количество: "))

        for i in range(quantity):
            if not check_stock_for_cocktail(cocktail[4]):
                print("Недостаточно ингредиентов!")
                conn.close()
                return

        for i in range(quantity):
            update_stock_for_cocktail(cocktail[4])

        total = cocktail[2] * quantity

        cur.execute("INSERT INTO sales (date, item, quantity, total) VALUES (?, ?, ?, ?)",
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), cocktail[1], quantity, total))
        conn.commit()
        conn.close()

        print(f"Продано {quantity} шт коктейля на сумму {total} руб")

    except:
        print("Ошибка!")


def sell_drink():
    conn = sqlite3.connect('resource/drink_shop.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM drinks")
    drinks = cur.fetchall()

    if not drinks:
        print("\nНет напитков\n")
        conn.close()
        return

    print("\n==================================================")
    print("НАПИТКИ:")
    for d in drinks:
        print(f"ID:{d[0]} | {d[1]} | {d[3]} руб | {d[4]} шт")

    try:
        did = int(input("\nВведите ID напитка: "))
        quantity = int(input("Количество: "))

        cur.execute("SELECT * FROM drinks WHERE id = ?", (did,))
        drink = cur.fetchone()

        if not drink:
            print("Напиток не найден!")
            conn.close()
            return

        if drink[4] < quantity:
            print(f"Недостаточно! Доступно: {drink[4]} шт")
            conn.close()
            return

        total = drink[3] * quantity

        cur.execute("UPDATE drinks SET quantity = quantity - ? WHERE id = ?", (quantity, did))
        cur.execute("INSERT INTO sales (date, item, quantity, total) VALUES (?, ?, ?, ?)",
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), drink[1], quantity, total))
        conn.commit()
        conn.close()

        print(f"Продано {quantity} шт на сумму {total} руб")

    except:
        print("Ошибка!")


def restock():
    print("\n--- Пополнение запасов ---")
    print("1. Пополнить напитки")
    print("2. Пополнить ингредиенты")

    choice = input("Выбор: ")

    if choice == '1':
        conn = sqlite3.connect('resource/drink_shop.db')
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM drinks")
        drinks = cur.fetchall()

        if not drinks:
            print("Нет напитков")
            conn.close()
            return

        for d in drinks:
            print(f"ID:{d[0]} | {d[1]}")

        try:
            did = int(input("ID напитка: "))
            quantity = int(input("Количество для добавления: "))
            cur.execute("UPDATE drinks SET quantity = quantity + ? WHERE id = ?", (quantity, did))
            conn.commit()
            print("Запасы пополнены!")
        except:
            print("Ошибка!")

        conn.close()

    elif choice == '2':
        conn = sqlite3.connect('resource/drink_shop.db')
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM ingredients")
        ingredients = cur.fetchall()

        if not ingredients:
            print("Нет ингредиентов")
            conn.close()
            return

        for i in ingredients:
            print(f"ID:{i[0]} | {i[1]}")

        try:
            iid = int(input("ID ингредиента: "))
            quantity = int(input("Количество для добавления: "))
            cur.execute("UPDATE ingredients SET quantity = quantity + ? WHERE id = ?", (quantity, iid))
            conn.commit()
            print("Запасы пополнены!")
        except:
            print("Ошибка!")

        conn.close()


def view_sales():
    conn = sqlite3.connect('resource/drink_shop.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales ORDER BY date DESC")
    sales = cur.fetchall()
    conn.close()

    if not sales:
        print("\nНет продаж\n")
        return

    print("\n==================================================")
    print("ПРОДАЖИ:")
    total_revenue = 0
    for s in sales:
        print(f"{s[1]} | {s[2]} | {s[3]} шт | {s[4]} руб")
        total_revenue += s[4]
    print("==================================================")
    print(f"ОБЩАЯ ВЫРУЧКА: {total_revenue} руб")
    print()


def main():
    init_db()

    while True:
        print("\n==================================================")
        print("I LOVE DRINK")
        print("==================================================")
        print("1. Добавить напиток")
        print("2. Добавить ингредиент")
        print("3. Просмотр склада")
        print("4. Добавить коктейль")
        print("5. Список коктейлей")
        print("6. Продать коктейль")
        print("7. Продать напиток")
        print("8. Пополнение запасов")
        print("9. Просмотр продаж")
        print("0. Выход")
        print("==================================================")

        choice = input("Выбор: ")

        if choice == '1':
            add_drink()
        elif choice == '2':
            add_ingredient()
        elif choice == '3':
            view_stock()
        elif choice == '4':
            add_cocktail()
        elif choice == '5':
            view_cocktails()
        elif choice == '6':
            sell_cocktail()
        elif choice == '7':
            sell_drink()
        elif choice == '8':
            restock()
        elif choice == '9':
            view_sales()
        elif choice == '0':
            print("До свидания!")
            break
        else:
            print("Неверный выбор!")


if __name__ == "__main__":
    main()