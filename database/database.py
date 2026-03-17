
def create_tables(self):
    # Таблица пользователей
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