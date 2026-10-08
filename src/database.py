import sqlite3


class DataBase:
    def __init__(self, file: str):
        self.cursor, self.conn = self.database_file(file)

    def add_user(self, username, password):
        # if not self.find_name(username):
        #     print("Usersname already in the database")
        #     return

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)

        try:
            sql = "INSERT INTO users (username, password) VALUES (?, ?)"
            self.cursor.execute(sql, (username, password))

            self.conn.commit()
            print(f"User '{username}' added successfully!")

        except sqlite3.IntegrityError:
            # print(f"The username '{username}' already exists.")
            found_user = self.get_user(username)
            return bool(found_user)

    def delete_user(self, username):
        # if not self.find_name(username):
        #     print(
        #         f"Username {username} has not been found\nSkipping deleting user from the database."
        #     )
        try:
            query = "DELETE FROM users WHERE username = ?"

            self.cursor.execute(query, (username,))

            self.conn.commit()
            if self.cursor.rowcount > 0:
                print(f"Success: User '{username}' has been deleted.")
            else:
                print(f"Notice: No user found with the username '{username}'.")

        except sqlite3.Error as error:
            print("Failed to delete data from SQLite table:", error)

    def database_file(self, file: str):
        conn = sqlite3.connect(file, check_same_thread=False)
        cursor = conn.cursor()

        return cursor, conn

    def close_connection(self):
        self.cursor.close()
        self.conn.close()

    def get_user(self, username):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)
        cursor = self.conn.execute(
            """
            SELECT id, username, password
            FROM users
            WHERE username = ?
            """,
            (username,),
        )

        return cursor.fetchone()

    def find_name(self, name):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)

        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM users WHERE username = ?)", (name,)
        )

        exists = self.cursor.fetchone()[0]

        return bool(exists)
