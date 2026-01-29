import sqlite3
import hashlib
import os
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    """SQLite database manager for user authentication."""
    
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with users table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                language TEXT DEFAULT 'English'
            )
        """)
        
        # Create learning history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                sentence TEXT,
                correction TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, email, password):
        """Register a new user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            hashed_password = self.hash_password(password)
            
            cursor.execute("""
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
            """, (username, email, hashed_password))
            
            conn.commit()
            conn.close()
            
            return True, "✅ Registration successful! Please login."
        
        except sqlite3.IntegrityError:
            return False, "❌ Username or email already exists!"
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
    
    def authenticate_user(self, username, password):
        """Authenticate user with username and password."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            hashed_password = self.hash_password(password)
            
            cursor.execute("""
                SELECT id, username, email FROM users
                WHERE username = ? AND password = ? AND is_active = 1
            """, (username, hashed_password))
            
            user = cursor.fetchone()
            
            if user:
                # Update last login
                cursor.execute("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (user[0],))
                conn.commit()
                conn.close()
                
                return True, user  # (id, username, email)
            else:
                conn.close()
                return False, None
        
        except Exception as e:
            return False, None
    
    def save_learning_history(self, user_id, sentence, correction):
        """Save user's learning history."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO learning_history (user_id, sentence, correction)
                VALUES (?, ?, ?)
            """, (user_id, sentence, correction))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            return False
    
    def get_user_history(self, user_id, limit=10):
        """Get user's learning history."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT sentence, correction, timestamp FROM learning_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit))
            
            history = cursor.fetchall()
            conn.close()
            
            return history
        except Exception as e:
            return []
    
    def user_exists(self, username):
        """Check if user exists."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
        except Exception as e:
            return False
    
    def email_exists(self, email):
        """Check if email exists."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
        except Exception as e:
            return False
    
    def get_all_users_count(self):
        """Get total number of registered users."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
        except Exception as e:
            return 0
    
    def delete_user(self, user_id):
        """Deactivate user account."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET is_active = 0
                WHERE id = ?
            """, (user_id,))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            return False
    
    def set_user_language(self, user_id, language):
        """Set user's preferred language."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET language = ?
                WHERE id = ?
            """, (language, user_id))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            return False
    
    def get_user_language(self, user_id):
        """Get user's preferred language."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT language FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            return "English"
        except Exception as e:
            return "English"
