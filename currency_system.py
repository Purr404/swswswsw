# currency_system.py
import json
import os
import random
from datetime import datetime
from typing import Dict, List

class CurrencySystem:
    def __init__(self, filename="user_gems.json"):
        self.filename = filename
        self.data = self.load_data()
    
    def load_data(self):
        """Load gems data from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_data(self):
        """Save gems data to JSON file"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving gems data: {e}")
            return False
    
    def get_user(self, user_id: str):
        """Get or create user gems data"""
        if user_id not in self.data:
            self.data[user_id] = {
                "gems": 0,
                "total_earned": 0,
                "last_updated": datetime.utcnow().isoformat(),
                "daily_streak": 0,
                "last_daily": None,
                "transactions": []
            }
        return self.data[user_id]
    
    def add_gems(self, user_id: str, gems: int, reason: str = ""):
        """Add gems to a user with transaction history"""
        user = self.get_user(user_id)
        
        # Add gems
        user["gems"] += gems
        user["total_earned"] += gems
        user["last_updated"] = datetime.utcnow().isoformat()
        
        # Record transaction
        transaction = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "reward",
            "gems": gems,
            "reason": reason,
            "balance": user["gems"]
        }
        user["transactions"].append(transaction)
        
        # Keep only last 50 transactions
        if len(user["transactions"]) > 50:
            user["transactions"] = user["transactions"][-50:]
        
        self.save_data()
        return transaction
    
    def deduct_gems(self, user_id: str, gems: int, reason: str = ""):
        """Deduct gems from a user (for purchases)"""
        user = self.get_user(user_id)
        
        if user["gems"] < gems:
            return False  # Not enough gems
        
        # Deduct gems
        user["gems"] -= gems
        user["last_updated"] = datetime.utcnow().isoformat()
        
        # Record transaction
        transaction = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "purchase",
            "gems": -gems,
            "reason": reason,
            "balance": user["gems"]
        }
        user["transactions"].append(transaction)
        
        self.save_data()
        return transaction
    
    def get_balance(self, user_id: str):
        """Get user's current gems balance"""
        user = self.get_user(user_id)
        return {
            "gems": user["gems"],
            "total_earned": user["total_earned"]
        }
    
    def get_leaderboard(self, limit: int = 10):
        """Get gems leaderboard"""
        if not self.data:
            return []
        
        sorted_users = sorted(
            self.data.items(),
            key=lambda x: x[1]["gems"],
            reverse=True
        )[:limit]
        
        return [
            {
                "user_id": user_id,
                "gems": data["gems"],
                "total_earned": data["total_earned"]
            }
            for user_id, data in sorted_users
        ]
    
    def can_claim_daily(self, user_id: str):
        """Check if user can claim daily reward"""
        user = self.get_user(user_id)
        
        if not user["last_daily"]:
            return True
        
        last_claim = datetime.fromisoformat(user["last_daily"])
        now = datetime.utcnow()
        
        # Check if 24 hours have passed
        hours_passed = (now - last_claim).total_seconds() / 3600
        return hours_passed >= 23.5  # 23.5 hours for some flexibility
    
    def claim_daily(self, user_id: str):
        """Claim daily reward with streak bonus"""
        user = self.get_user(user_id)
        now = datetime.utcnow()
        
        # Check streak
        if user["last_daily"]:
            last_claim = datetime.fromisoformat(user["last_daily"])
            days_diff = (now - last_claim).days
            
            if days_diff == 1:
                user["daily_streak"] += 1
            elif days_diff > 1:
                user["daily_streak"] = 1  # Reset streak
        else:
            user["daily_streak"] = 1
        
        # Base daily reward (1-100 gems)
        base_gems = random.randint(1, 100)
        
        # Streak bonus (extra 10% per day, max 100% bonus)
        streak_bonus = min(user["daily_streak"] * 0.1, 1.0)
        bonus_gems = int(base_gems * streak_bonus)
        
        total_gems = base_gems + bonus_gems
        
        # Update last claim
        user["last_daily"] = now.isoformat()
        
        # Add gems
        return self.add_gems(
            user_id=user_id,
            gems=total_gems,
            reason=f"🎁 Daily Reward (Streak: {user['daily_streak']} days)"
        )