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
    
    def close(self):
        self.conn.close()