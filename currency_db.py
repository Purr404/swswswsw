# currency_db.py
import sqlite3
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional

class CurrencyDatabase:
    def __init__(self, db_file="currency.db"):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        # Users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                gems INTEGER DEFAULT 0,
                total_earned INTEGER DEFAULT 0,
                daily_streak INTEGER DEFAULT 0,
                last_daily TEXT,
                last_updated TEXT
            )
        ''')
        
        # Transactions table
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                type TEXT,
                gems INTEGER,
                reason TEXT,
                timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: str, username: str = None):
        """Get or create user"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()
        
        if not user:
            # Create new user
            now = datetime.now(timezone.utc).isoformat()
            c.execute('''
                INSERT INTO users 
                (user_id, username, gems, total_earned, last_updated)
                VALUES (?, ?, 0, 0, ?)
            ''', (user_id, username or f"User_{user_id[:8]}", now))
            conn.commit()
            
            # Get the newly created user
            c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = c.fetchone()
        
        conn.close()
        
        # Convert to dict
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'gems': user[2],
                'total_earned': user[3],
                'daily_streak': user[4],
                'last_daily': user[5],
                'last_updated': user[6]
            }
        return None
    
    def add_gems(self, user_id: str, gems: int, reason: str = "", username: str = None):
        """Add gems to user"""
        user = self.get_user(user_id, username)
        
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        # Update user gems
        new_gems = user['gems'] + gems
        new_total = user['total_earned'] + gems
        now = datetime.now(timezone.utc).isoformat()
        
        c.execute('''
            UPDATE users 
            SET gems = ?, total_earned = ?, last_updated = ?, username = COALESCE(?, username)
            WHERE user_id = ?
        ''', (new_gems, new_total, now, username, user_id))
        
        # Record transaction
        c.execute('''
            INSERT INTO transactions (user_id, type, gems, reason, timestamp)
            VALUES (?, 'reward', ?, ?, ?)
        ''', (user_id, gems, reason, now))
        
        conn.commit()
        conn.close()
        
        return {
            'gems': gems,
            'new_balance': new_gems,
            'reason': reason
        }
    
    def get_balance(self, user_id: str):
        """Get user balance"""
        user = self.get_user(user_id)
        if user:
            return {
                'gems': user['gems'],
                'total_earned': user['total_earned']
            }
        return {'gems': 0, 'total_earned': 0}
    
    def get_leaderboard(self, limit: int = 10):
        """Get leaderboard"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute('''
            SELECT user_id, username, gems, total_earned 
            FROM users 
            ORDER BY gems DESC 
            LIMIT ?
        ''', (limit,))
        
        leaderboard = []
        for row in c.fetchall():
            leaderboard.append({
                'user_id': row[0],
                'username': row[1],
                'gems': row[2],
                'total_earned': row[3]
            })
        
        conn.close()
        return leaderboard