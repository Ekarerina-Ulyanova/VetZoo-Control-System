import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="vetzoo.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS animals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                species TEXT NOT NULL,
                arrival_date TEXT NOT NULL,
                birth_date TEXT,
                gender TEXT,
                enclosure TEXT,
                health_status TEXT DEFAULT 'здоров',
                notes TEXT
            )
        ''')
        self.conn.commit()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                role TEXT NOT NULL CHECK(role IN ('admin', 'vet', 'keeper')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_animal(self, name, species, arrival_date, birth_date=None, gender=None, enclosure=None, notes=None):
        self.cursor.execute('''
            INSERT INTO animals (name, species, arrival_date, birth_date, gender, enclosure, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, species, arrival_date, birth_date, gender, enclosure, notes))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_animals(self):
        self.cursor.execute('SELECT * FROM animals ORDER BY name')
        return self.cursor.fetchall()
    
    def get_animal(self, animal_id):
        self.cursor.execute('SELECT * FROM animals WHERE id = ?', (animal_id,))
        return self.cursor.fetchone()
    
    def update_animal_status(self, animal_id, status):
        self.cursor.execute('UPDATE animals SET health_status = ? WHERE id = ?', (status, animal_id))
        self.conn.commit()

    def create_user(self, username, password_hash, role, full_name=None):
        try:
            self.cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, role)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, full_name, role))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def get_user_by_username(self, username):
        self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return self.cursor.fetchone()
    
    def get_user(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()
    
    def get_all_users(self):
        self.cursor.execute('SELECT id, username, full_name, role, created_at FROM users ORDER BY id')
        return self.cursor.fetchall()
    
    def delete_user(self, user_id):
        self.cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0    
    
    def close(self):
        self.conn.close()
