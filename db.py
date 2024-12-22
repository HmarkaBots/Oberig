import sqlite3

class BotDB:
    def __init__(self, db_file: str):
        """Ініціалізуємо підключення до бази даних"""
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """Створюємо таблицю, якщо вона не існує"""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               user_id INTEGER UNIQUE,
                               user_name TEXT NOT NULL,
                               user_phone TEXT NOT NULL,
                               j_date DATETIME DEFAULT (DATETIME('now'))
                               )''')
        self.conn.commit()

    def user_exists(self, user_id: int) -> bool:
        """Перевіряємо наявність користувача у базі"""
        result = self.cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
        return result.fetchone() is not None

    def add_user(self, user_id: int, user_name: str, user_phone: str):
        """Додаємо користувача до бази даних"""
        if not self.user_exists(user_id):
            self.cursor.execute("INSERT INTO users (user_id, user_name, user_phone, region) VALUES (?, ?, ?, ?)",
                                (user_id, user_name, user_phone, "Не вказано"))
            self.conn.commit()
        else:
            raise ValueError("Користувач вже існує в базі")

    def update_region(self, user_id, region):
        self.cursor.execute(
            "UPDATE users SET region = ? WHERE user_id = ?",
            (region, user_id)
        )
        self.conn.commit()

    def update_role(self, user_id, role):
        self.cursor.execute(
            "UPDATE users SET role = ? WHERE user_id = ?",
            (role, user_id)
        )
        self.conn.commit()

    def update_amount(self, user_id, amount):
     self.cursor.execute("UPDATE users SET amount = ? WHERE user_id = ?", (amount, user_id))
     self.conn.commit()

    def get_angels(self):
        """Отримує список користувачів з роллю 'Янгол'."""
        self.cursor.execute(
            """
            SELECT user_name, region, photo_path, jar_l 
            FROM users 
            WHERE role = 'Янгол'
            """
        )
        angels = [
            {
                "name": row[0],
                "region": row[1],
                "photo": row[2],
                "jar_link": row[3]
            }
            for row in self.cursor.fetchall()
        ]
        return angels

    def save_angel_details(self, user_id, region, amount, instagram, wish, photo_path, jar_l):
        """
        Зберігає деталі Янгола в базу даних, включаючи посилання на банку.
        """
        self.cursor.execute("""
            UPDATE users
            SET region = ?, amount = ?, instagram = ?, wish = ?, photo_path = ?, jar_l = ?
            WHERE user_id = ?
        """, (region, amount, instagram, wish, photo_path, jar_l, user_id))
        self.conn.commit()

    def save_guardian_details(self, user_id, chosen_angel, amount, instagram, wish, photo_path, jar_link):
        self.cursor.execute(
            """
            UPDATE users
            SET chosen_angel = ?, amount = ?, instagram = ?, wish = ?, photo_path = ?, jar_l = ?
            WHERE user_id = ?
            """,
            (chosen_angel, amount, instagram, wish, photo_path, jar_link, user_id)
        )
        self.conn.commit()

    # Додати метод для оновлення jar_l
    def update_jar_link(self, user_id: int, jar_link: str):
        self.cursor.execute("UPDATE users SET jar_l = ? WHERE user_id = ?", (jar_link, user_id))
        self.conn.commit()

    def close(self):
        """Закриваємо з'єднання з базою даних"""
        self.conn.close()
