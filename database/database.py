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

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS examinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                examination_date TEXT NOT NULL,
                veterinarian TEXT NOT NULL,
                diagnosis TEXT,
                treatment TEXT,
                notes TEXT,
                is_scheduled INTEGER DEFAULT 0,
                FOREIGN KEY (animal_id) REFERENCES animals (id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()


        # Таблица прививок
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vaccinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                vaccination_date TEXT NOT NULL,
                vaccine_name TEXT NOT NULL,
                veterinarian TEXT NOT NULL,
                next_due_date TEXT,
                is_scheduled INTEGER DEFAULT 0,
                FOREIGN KEY (animal_id) REFERENCES animals (id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS diets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                diet_name TEXT NOT NULL,
                food_type TEXT NOT NULL,
                quantity TEXT NOT NULL,
                schedule TEXT,
                start_date TEXT NOT NULL,
                end_date TEXT,
                FOREIGN KEY (animal_id) REFERENCES animals (id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    def add_examination(self, animal_id, examination_date, veterinarian, diagnosis, treatment, notes=None, is_scheduled=0):
        self.cursor.execute('''
            INSERT INTO examinations (animal_id, examination_date, veterinarian, diagnosis, treatment, notes, is_scheduled)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (animal_id, examination_date, veterinarian, diagnosis, treatment, notes, is_scheduled))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_animal_examinations(self, animal_id):
        self.cursor.execute('SELECT * FROM examinations WHERE animal_id = ? ORDER BY examination_date DESC', (animal_id,))
        return self.cursor.fetchall()

    def add_vaccination(self, animal_id, vaccination_date, vaccine_name, veterinarian, next_due_date=None, is_scheduled=0):
        self.cursor.execute('''
            INSERT INTO vaccinations (animal_id, vaccination_date, vaccine_name, veterinarian, next_due_date, is_scheduled)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (animal_id, vaccination_date, vaccine_name, veterinarian, next_due_date, is_scheduled))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_animal_vaccinations(self, animal_id):
        self.cursor.execute('SELECT * FROM vaccinations WHERE animal_id = ? ORDER BY vaccination_date DESC', (animal_id,))
        return self.cursor.fetchall()

    def complete_examination(self, exam_id):
        self.cursor.execute('UPDATE examinations SET is_scheduled = 0 WHERE id = ?', (exam_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def complete_vaccination(self, vacc_id):
        self.cursor.execute('UPDATE vaccinations SET is_scheduled = 0 WHERE id = ?', (vacc_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

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

    def add_diet(self, animal_id, diet_name, food_type, quantity, schedule, start_date, end_date=None):
        self.cursor.execute('''
            INSERT INTO diets (animal_id, diet_name, food_type, quantity, schedule, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (animal_id, diet_name, food_type, quantity, schedule, start_date, end_date))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_animal_diets(self, animal_id):
        self.cursor.execute('SELECT * FROM diets WHERE animal_id = ? ORDER BY start_date DESC', (animal_id,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
