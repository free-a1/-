# database.py
import sqlite3
from hashlib import sha256

class UserManager:
    def __init__(self):
        self.conn = sqlite3.connect('users.db')
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT 0
            )
        ''')
        self.conn.commit()

    def register_user(self, username, password, is_admin=False):
        password_hash = sha256(password.encode()).hexdigest()
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password_hash, is_admin)
                VALUES (?, ?, ?)
            ''', (username, password_hash, int(is_admin)))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # 用户名已存在

    def authenticate(self, username, password):
        password_hash = sha256(password.encode()).hexdigest()
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, is_admin FROM users 
            WHERE username=? AND password_hash=?
        ''', (username, password_hash))
        return cursor.fetchone()  # 返回 (user_id, is_admin)

    def log_audit(self, user_id, action, detail=""):
        """记录用户操作"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                action TEXT,
                detail TEXT
            )
        ''')
        cursor.execute('''
            INSERT INTO audit_log (user_id, action, detail)
            VALUES (?, ?, ?)
        ''', (user_id, action, detail))
        self.conn.commit()

# 全局用户管理实例
user_manager = UserManager()