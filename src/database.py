import sqlite3
import sys
import platform
import os


class DataBase:
    def __init__(self, file: str):
        self.cursor, self.conn = self.database_file(file)

    def add_user(self, username, password):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
                    CHECK (role IN ('user', 'staff', 'admin')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)

        try:
            print("ADDING USERNAME")
            sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
            self.cursor.execute(sql, (username, password))

            self.conn.commit()
            print(f"User '{username}' added successfully!")

        except sqlite3.IntegrityError as e:
            print("ERROR: ", e)

    def delete_user(self, username):
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
        if platform.system() in ("Linux", "Darwin"):
            folder_path = f"/home/{os.getlogin()}/.config/secure_chat/"
        elif platform.system() == "Windows":
            folder_path = f"C:\\Users\\{os.getlogin()}\\AppData\\Local"

        else:
            print("Unsupported OS detected\nExiting.")
            sys.exit()
            return
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        abs_path = os.path.join(folder_path + file)

        conn = sqlite3.connect(abs_path, check_same_thread=False)
        cursor = conn.cursor()

        return cursor, conn

    def close_connection(self):
        self.cursor.close()
        self.conn.close()

    def update_user(self, role: str, username: str):
        if self.find_name(username):
            if role.lower() in ("admin", "staff", "user"):
                query = """
                    UPDATE users
                    SET role = ?
                    WHERE username = ?;
                """
                self.cursor.execute(query, (role, username))

                self.conn.commit()

            else:
                print(
                    "Wrong paramater passed!\nPlease try again with the correct paramater."
                )
        else:
            print("Username not found in the database.")

    def get_user(self, username):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
                    CHECK (role IN ('user', 'staff', 'admin')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor = self.cursor.execute(
            """
            SELECT id, username, password_hash, role
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
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
                    CHECK (role IN ('user', 'staff', 'admin')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)

        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM users WHERE username = ?)", (name,)
        )

        exists = self.cursor.fetchone()[0]

        return bool(exists)
