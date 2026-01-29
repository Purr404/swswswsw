# currency_system.py
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class CurrencySystem:
    def __init__(self, filename="user_currency.json"):
        self.filename = filename
        self.data = self.load_data()
    
    def load_data(self):
        """Load currency data from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_data(self):
        """Save currency data to JSON file"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving currency data: {e}")
            return False
    
    def get_user(self, user_id: str):
        """Get or create user currency data"""
        if user_id not in self.data:
            self.data[user_id] = {
                "gems": 0,
                "gold": 0,
                "total_earned": 0,
                "last_updated": datetime.utcnow().isoformat(),
                "transactions": []
            }
        return self.data[user_id]
    
    def add_rewards(self, user_id: str, gems: int = 0, gold: int = 0, reason: str = ""):
        """Add gems/gold to a user with transaction history"""
        user = self.get_user(user_id)
        
        # Add currency
        user["gems"] += gems
        user["gold"] += gold
        user["total_earned"] += gems + gold
        user["last_updated"] = datetime.utcnow().isoformat()
        
        # Record transaction
        transaction = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "reward",
            "gems": gems,
            "gold": gold,
            "reason": reason,
            "new_balance": {
                "gems": user["gems"],
                "gold": user["gold"]
            }
        }
        user["transactions"].append(transaction)
        
        # Keep only last 50 transactions
        if len(user["transactions"]) > 50:
            user["transactions"] = user["transactions"][-50:]
        
        self.save_data()
        return transaction
    
    def deduct_currency(self, user_id: str, gems: int = 0, gold: int = 0, reason: str = ""):
        """Deduct gems/gold from a user (for purchases)"""
        user = self.get_user(user_id)
        
        if user["gems"] < gems or user["gold"] < gold:
            return False  # Not enough currency
        
        # Deduct currency
        user["gems"] -= gems
        user["gold"] -= gold
        user["last_updated"] = datetime.utcnow().isoformat()
        
        # Record transaction
        transaction = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "purchase",
            "gems": -gems,
            "gold": -gold,
            "reason": reason,
            "new_balance": {
                "gems": user["gems"],
                "gold": user["gold"]
            }
        }
        user["transactions"].append(transaction)
        
        self.save_data()
        return transaction
    
    def get_balance(self, user_id: str):
        """Get user's current balance"""
        user = self.get_user(user_id)
        return {
            "gems": user["gems"],
            "gold": user["gold"],
            "total_earned": user["total_earned"]
        }
    
    def get_leaderboard(self, limit: int = 10, by: str = "gems"):
        """Get currency leaderboard"""
        if not self.data:
            return []
        
        sorted_users = sorted(
            self.data.items(),
            key=lambda x: x[1].get(by, 0),
            reverse=True
        )[:limit]
        
        return [
            {
                "user_id": user_id,
                "gems": data["gems"],
                "gold": data["gold"],
                "total_earned": data["total_earned"]
            }
            for user_id, data in sorted_users
        ]
    
    def get_user_stats(self, user_id: str):
        """Get detailed user statistics"""
        user = self.get_user(user_id)
        return {
            **user,
            "transaction_count": len(user["transactions"])
        }