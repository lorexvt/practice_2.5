import sqlite3


class Student:

    def __init__(self, first_name, last_name, patronymic, group, grades):
        self.first_name = first_name
        self.last_name = last_name
        self.patronymic = patronymic
        self.group = group
        self.grades = grades  # список из 4 оценок

    def average_grade(self):
        return sum(self.grades) / len(self.grades)

    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}"


def init_db():
    conn = sqlite3.connect('resource/students.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            patronymic TEXT,
            group_name TEXT,
            grades TEXT
        )
    ''')
    conn.commit()
    conn.close()


def add_student():
    print("\n--- Добавление студента ---")
    first_name = input("Имя: ")
    last_name = input("Фамилия: ")
    patronymic = input("Отчество: ")
    group = input("Группа: ")

    print("Введите 4 оценки (1-5):")
    grades = []
    for i in range(4):
        while True:
            try:
                grade = int(input(f"Оценка {i + 1}: "))
                if 1 <= grade <= 5:
                    grades.append(grade)
                    break
                else:
                    print("Оценка от 1 до 5!")
            except:
                print("Введите число!")

    student = Student(first_name, last_name, patronymic, group, grades)
    grades_str = ','.join(map(str, student.grades))

    conn = sqlite3.connect('resource/students.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO students (first_name, last_name, patronymic, group_name, grades)
        VALUES (?, ?, ?, ?, ?)
    ''', (student.first_name, student.last_name, student.patronymic, student.group, grades_str))
    conn.commit()
    conn.close()

    print("Студент добавлен!")


def view_all_students():
    conn = sqlite3.connect('resource/students.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    conn.close()

    if not students:
        print("\nНет студентов\n")
        return

    print("\n" + "=" * 60)
    for student in students:
        grades = list(map(int, student[5].split(',')))
        avg = sum(grades) / len(grades)
        print(f"ID: {student[0]} | {student[2]} {student[1]} {student[3]} | Группа: {student[4]} | Ср.балл: {avg:.2f}")
    print("=" * 60 + f"\nВсего: {len(students)}\n")


def view_one_student():
    try:
        student_id = int(input("Введите ID студента: "))

        conn = sqlite3.connect('resource/students.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        student = cursor.fetchone()
        conn.close()

        if student:
            grades = list(map(int, student[5].split(',')))
            avg = sum(grades) / len(grades)
            print("\n" + "=" * 50)
            print(f"ID: {student[0]}")
            print(f"ФИО: {student[2]} {student[1]} {student[3]}")
            print(f"Группа: {student[4]}")
            print(f"Оценки: {', '.join(map(str, grades))}")
            print(f"Средний балл: {avg:.2f}")
            print("=" * 50 + "\n")
        else:
            print("Студент не найден!\n")
    except:
        print("Ошибка!\n")


def edit_student():
    try:
        student_id = int(input("Введите ID студента: "))

        conn = sqlite3.connect('resource/students.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        student = cursor.fetchone()

        if not student:
            print("Студент не найден!\n")
            conn.close()
            return

        print("\nТекущие данные:")
        print(f"Имя: {student[1]}, Фамилия: {student[2]}, Отчество: {student[3]}, Группа: {student[4]}")

        print("\nВведите новые данные (оставьте пустым, чтобы не менять):")
        first_name = input(f"Имя ({student[1]}): ") or student[1]
        last_name = input(f"Фамилия ({student[2]}): ") or student[2]
        patronymic = input(f"Отчество ({student[3]}): ") or student[3]
        group = input(f"Группа ({student[4]}): ") or student[4]

        change_grades = input("Изменить оценки? (y/n): ")
        if change_grades.lower() == 'y':
            print("Введите 4 оценки (1-5):")
            grades = []
            for i in range(4):
                while True:
                    try:
                        grade = int(input(f"Оценка {i + 1}: "))
                        if 1 <= grade <= 5:
                            grades.append(grade)
                            break
                        else:
                            print("Оценка от 1 до 5!")
                    except:
                        print("Введите число!")
            grades_str = ','.join(map(str, grades))
        else:
            grades_str = student[5]

        cursor.execute('''
            UPDATE students 
            SET first_name=?, last_name=?, patronymic=?, group_name=?, grades=?
            WHERE id=?
        ''', (first_name, last_name, patronymic, group, grades_str, student_id))
        conn.commit()
        conn.close()

        print("Данные обновлены!\n")
    except:
        print("Ошибка!\n")


def delete_student():
    try:
        student_id = int(input("Введите ID студента: "))

        conn = sqlite3.connect('resource/students.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        student = cursor.fetchone()

        if not student:
            print("Студент не найден!\n")
            conn.close()
            return

        confirm = input(f"Удалить {student[2]} {student[1]}? (y/n): ")
        if confirm.lower() == 'y':
            cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
            conn.commit()
            print("Студент удален!\n")
        else:
            print("Отменено!\n")

        conn.close()
    except:
        print("Ошибка!\n")


def group_average():
    group = input("Введите название группы: ")

    conn = sqlite3.connect('resource/students.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE group_name = ?', (group,))
    students = cursor.fetchall()
    conn.close()

    if not students:
        print("Группа не найдена!\n")
        return

    print(f"\n--- Группа {group} ---")
    total_avg = 0
    for student in students:
        grades = list(map(int, student[5].split(',')))
        avg = sum(grades) / len(grades)
        total_avg += avg
        print(f"{student[2]} {student[1]} {student[3]}: {avg:.2f}")

    print(f"\nСредний балл группы: {total_avg / len(students):.2f}\n")


def main():
    init_db()

    while True:
        print("\n" + "=" * 40)
        print("1. Добавить студента")
        print("2. Все студенты")
        print("3. Просмотр студента")
        print("4. Редактировать")
        print("5. Удалить")
        print("6. Средний балл группы")
        print("0. Выход")
        print("=" * 40)

        choice = input("Выбор: ")

        if choice == '1':
            add_student()
        elif choice == '2':
            view_all_students()
        elif choice == '3':
            view_one_student()
        elif choice == '4':
            edit_student()
        elif choice == '5':
            delete_student()
        elif choice == '6':
            group_average()
        elif choice == '0':
            print("До свидания!")
            break
        else:
            print("Неверный выбор!\n")


if __name__ == "__main__":
    main()