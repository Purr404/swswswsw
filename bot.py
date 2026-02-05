import os
import sys
import json
import asyncio
import random
from datetime import datetime, timezone, timedelta

print("=== DEBUG INFO ===")
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)
print("Files in directory:", os.listdir('.'))
print("==================")

import discord
from discord.ext import commands, tasks
from typing import Optional

TOKEN = os.getenv('TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')  # This will be set by Railway automatically

# --- Create the bot instance ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!!', intents=intents, help_command=None)

# === DATABASE CURRENCY SYSTEM ===
class DatabaseCurrencySystem:
    def __init__(self):
        self.connection = None
        self.initialized = False
        print(f"🔧 Database URL available: {'YES' if DATABASE_URL else 'NO'}")
    
    async def connect(self):
        """Connect to PostgreSQL database"""
        if not DATABASE_URL:
            print("⚠️ No DATABASE_URL found. Using JSON fallback.")
            self.initialized = False
            return False
        
        try:
            # Try to import asyncpg
            import asyncpg
            print("✅ asyncpg module available")
            
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                DATABASE_URL,
                ssl='require',
                min_size=1,
                max_size=5
            )
            
            # Create table if not exists
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_gems (
                        user_id TEXT PRIMARY KEY,
                        gems INTEGER DEFAULT 0,
                        total_earned INTEGER DEFAULT 0,
                        daily_streak INTEGER DEFAULT 0,
                        last_daily TIMESTAMP,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                ''')
                
                # Create transactions table
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_transactions (
                        id SERIAL PRIMARY KEY,
                        user_id TEXT REFERENCES user_gems(user_id),
                        type TEXT,
                        gems INTEGER,
                        reason TEXT,
                        balance INTEGER,
                        timestamp TIMESTAMP DEFAULT NOW()
                    )
                ''')
            
            print("✅ Connected to PostgreSQL database")
            self.initialized = True
            return True
            
        except ImportError:
            print("❌ asyncpg not installed. Using JSON fallback.")
            self.initialized = False
            return False
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            self.initialized = False
            return False
    
    async def add_gems(self, user_id: str, gems: int, reason: str = ""):
        """Add gems to a user"""
        if not self.initialized:
            return await self._json_add_gems(user_id, gems, reason)
        
        try:
            import asyncpg
            async with self.pool.acquire() as conn:
                # Start transaction
                async with conn.transaction():
                    # Get current balance
                    current = await conn.fetchval(
                        'SELECT gems FROM user_gems WHERE user_id = $1',
                        user_id
                    )
                    
                    if current is None:
                        # User doesn't exist, create them
                        await conn.execute('''
                            INSERT INTO user_gems (user_id, gems, total_earned)
                            VALUES ($1, $2, $2)
                        ''', user_id, gems)
                        current = gems
                    else:
                        # Update existing user
                        await conn.execute('''
                            UPDATE user_gems 
                            SET gems = gems + $2,
                                total_earned = total_earned + $2,
                                updated_at = NOW()
                            WHERE user_id = $1
                        ''', user_id, gems)
                        current += gems
                    
                    # Log transaction
                    await conn.execute('''
                        INSERT INTO user_transactions (user_id, type, gems, reason, balance)
                        VALUES ($1, 'reward', $2, $3, $4)
                    ''', user_id, gems, reason, current)
                    
                    print(f"✅ Database: Added {gems} gems to {user_id}. New balance: {current}")
                    return {"gems": gems, "balance": current}
                    
        except Exception as e:
            print(f"❌ Database error in add_gems: {e}")
            return await self._json_add_gems(user_id, gems, reason)
    
    async def _json_add_gems(self, user_id: str, gems: int, reason: str = ""):
        """JSON fallback for add_gems"""
        print(f"📝 Using JSON fallback for {user_id}")
        
        # Load existing data
        data = {}
        if os.path.exists("user_gems.json"):
            try:
                with open("user_gems.json", 'r') as f:
                    data = json.load(f)
            except:
                data = {}
        
        # Get or create user
        if user_id not in data:
            data[user_id] = {
                "gems": gems,
                "total_earned": gems,
                "daily_streak": 0,
                "last_daily": None
            }
        else:
            data[user_id]["gems"] += gems
            data[user_id]["total_earned"] += gems
        
        # Save to file
        with open("user_gems.json", 'w') as f:
            json.dump(data, f, indent=2)
        
        return {"gems": gems, "balance": data[user_id]["gems"]}
    
    async def get_balance(self, user_id: str):
        """Get user's current gems balance"""
        if not self.initialized:
            return await self._json_get_balance(user_id)
        
        try:
            import asyncpg
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    'SELECT gems, total_earned FROM user_gems WHERE user_id = $1',
                    user_id
                )
                
                if row:
                    return {"gems": row['gems'], "total_earned": row['total_earned']}
                else:
                    # User doesn't exist, return default
                    return {"gems": 0, "total_earned": 0}
                    
        except Exception as e:
            print(f"❌ Database error in get_balance: {e}")
            return await self._json_get_balance(user_id)
    
    async def _json_get_balance(self, user_id: str):
        """JSON fallback for get_balance"""
        if os.path.exists("user_gems.json"):
            try:
                with open("user_gems.json", 'r') as f:
                    data = json.load(f)
                    if user_id in data:
                        return {
                            "gems": data[user_id].get("gems", 0),
                            "total_earned": data[user_id].get("total_earned", 0)
                        }
            except:
                pass
        return {"gems": 0, "total_earned": 0}
    
    async def get_leaderboard(self, limit: int = 10):
        """Get gems leaderboard"""
        if not self.initialized:
            return await self._json_get_leaderboard(limit)
        
        try:
            import asyncpg
            async with self.pool.acquire() as conn:
                rows = await conn.fetch('''
                    SELECT user_id, gems, total_earned 
                    FROM user_gems 
                    ORDER BY gems DESC 
                    LIMIT $1
                ''', limit)
                
                return [
                    {
                        "user_id": row['user_id'],
                        "gems": row['gems'],
                        "total_earned": row['total_earned']
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"❌ Database error in get_leaderboard: {e}")
            return await self._json_get_leaderboard(limit)
    
    async def _json_get_leaderboard(self, limit: int = 10):
        """JSON fallback for get_leaderboard"""
        if os.path.exists("user_gems.json"):
            try:
                with open("user_gems.json", 'r') as f:
                    data = json.load(f)
                
                sorted_users = sorted(
                    data.items(),
                    key=lambda x: x[1].get("gems", 0),
                    reverse=True
                )[:limit]
                
                return [
                    {
                        "user_id": user_id,
                        "gems": user_data.get("gems", 0),
                        "total_earned": user_data.get("total_earned", 0)
                    }
                    for user_id, user_data in sorted_users
                ]
            except:
                pass
        return []
    
    async def can_claim_daily(self, user_id: str):
        """Check if user can claim daily reward"""
        if not self.initialized:
            return await self._json_can_claim_daily(user_id)
        
        try:
            import asyncpg
            async with self.pool.acquire() as conn:
                last_daily = await conn.fetchval(
                    'SELECT last_daily FROM user_gems WHERE user_id = $1',
                    user_id
                )
                
                if not last_daily:
                    return True
                
                # Check if 24 hours have passed
                time_diff = datetime.now(timezone.utc) - last_daily
                return time_diff.total_seconds() >= 86400  # 24 hours
                
        except Exception as e:
            print(f"❌ Database error in can_claim_daily: {e}")
            return await self._json_can_claim_daily(user_id)
    
    async def _json_can_claim_daily(self, user_id: str):
        """JSON fallback for can_claim_daily"""
        if os.path.exists("user_gems.json"):
            try:
                with open("user_gems.json", 'r') as f:
                    data = json.load(f)
                
                if user_id in data and data[user_id].get("last_daily"):
                    last_claim = datetime.fromisoformat(data[user_id]["last_daily"])
                    time_diff = datetime.now(timezone.utc) - last_claim
                    return time_diff.total_seconds() >= 86400
            except:
                pass
        return True
    
    async def claim_daily(self, user_id: str):
        """Claim daily reward"""
        if not self.initialized:
            return await self._json_claim_daily(user_id)
        
        try:
            import asyncpg
            async with self.pool.acquire() as conn:
                # Get user data
                row = await conn.fetchrow(
                    'SELECT daily_streak, last_daily FROM user_gems WHERE user_id = $1',
                    user_id
                )
                
                now = datetime.now(timezone.utc)
                
                if row:
                    last_daily = row['last_daily']
                    current_streak = row['daily_streak'] or 0
                    
                    # Check streak
                    if last_daily:
                        days_diff = (now - last_daily).days
                        if days_diff == 1:
                            current_streak += 1
                        elif days_diff > 1:
                            current_streak = 1
                    else:
                        current_streak = 1
                    
                    # Update user
                    await conn.execute('''
                        UPDATE user_gems 
                        SET last_daily = $2,
                            daily_streak = $3,
                            updated_at = NOW()
                        WHERE user_id = $1
                    ''', user_id, now, current_streak)
                else:
                    # Create new user
                    current_streak = 1
                    await conn.execute('''
                        INSERT INTO user_gems (user_id, last_daily, daily_streak)
                        VALUES ($1, $2, $3)
                    ''', user_id, now, current_streak)
                
                # Calculate daily reward
                base_gems = random.randint(1, 100)
                streak_bonus = min(current_streak * 0.1, 1.0)
                bonus_gems = int(base_gems * streak_bonus)
                total_gems = base_gems + bonus_gems
                
                # Add gems
                await self.add_gems(
                    user_id=user_id,
                    gems=total_gems,
                    reason=f"🎁 Daily Reward (Streak: {current_streak} days)"
                )
                
                return {"gems": total_gems, "streak": current_streak}
                
        except Exception as e:
            print(f"❌ Database error in claim_daily: {e}")
            return await self._json_claim_daily(user_id)
    
    async def _json_claim_daily(self, user_id: str):
        """JSON fallback for claim_daily"""
        # Load data
        data = {}
        if os.path.exists("user_gems.json"):
            try:
                with open("user_gems.json", 'r') as f:
                    data = json.load(f)
            except:
                data = {}
        
        # Get user
        if user_id not in data:
            data[user_id] = {
                "gems": 0,
                "total_earned": 0,
                "daily_streak": 0,
                "last_daily": None
            }
        
        user = data[user_id]
        now = datetime.now(timezone.utc)
        
        # Check streak
        if user.get("last_daily"):
            last_claim = datetime.fromisoformat(user["last_daily"])
            days_diff = (now - last_claim).days
            
            if days_diff == 1:
                user["daily_streak"] += 1
            elif days_diff > 1:
                user["daily_streak"] = 1
        else:
            user["daily_streak"] = 1
        
        # Calculate reward
        base_gems = random.randint(1, 100)
        streak_bonus = min(user["daily_streak"] * 0.1, 1.0)
        bonus_gems = int(base_gems * streak_bonus)
        total_gems = base_gems + bonus_gems
        
        # Update user
        user["gems"] += total_gems
        user["total_earned"] += total_gems
        user["last_daily"] = now.isoformat()
        
        # Save
        with open("user_gems.json", 'w') as f:
            json.dump(data, f, indent=2)
        
        return {"gems": total_gems, "streak": user["daily_streak"]}

# --- Continue with the rest of your code (QuizSystem, etc.) ---
# Just replace CurrencySystem with DatabaseCurrencySystem

# Create currency system
currency_system = DatabaseCurrencySystem()

# --- QUIZ SYSTEM (UPDATED) ---
class QuizSystem:
    def __init__(self, bot):
        self.bot = bot
        self.quiz_questions = []
        self.current_question = 0
        self.participants = {}
        self.question_timer = None
        self.quiz_channel = None
        self.quiz_logs_channel = None
        self.quiz_running = False
        self.question_start_time = None
        
        # Use the database currency system
        self.currency = currency_system
        
        # Load questions
        self.load_questions()
        print("✅ QuizSystem initialized")
    
    # ... (keep all your existing QuizSystem methods) ...
    # Just make sure to use self.currency for all currency operations
    
    async def distribute_quiz_rewards(self, sorted_participants):
        """Distribute gems based on quiz performance"""
        print(f"🎁 Distributing rewards to {len(sorted_participants)} participants")
        rewards = {}
        
        for rank, (user_id, data) in enumerate(sorted_participants, 1):
            base_gems = 50  # Participation reward
            
            # Rank-based bonuses
            if rank == 1:
                base_gems += 500
            elif rank == 2:
                base_gems += 250
            elif rank == 3:
                base_gems += 125
            elif rank <= 10:
                base_gems += 75
            
            # Score-based bonus
            score_bonus = (data["score"] // 100) * 10
            base_gems += score_bonus
            
            # Perfect score bonus
            max_score = len(self.quiz_questions) * 300
            if data["score"] == max_score:
                base_gems += 250
                reason = f"🎯 Perfect Score! ({data['score']} pts, Rank #{rank})"
            else:
                reason = f"🏆 Quiz Rewards ({data['score']} pts, Rank #{rank})"
            
            # Add gems using database
            result = await self.currency.add_gems(
                user_id=user_id,
                gems=base_gems,
                reason=reason
            )
            
            rewards[user_id] = {
                "gems": base_gems,
                "rank": rank
            }
            
            print(f"  ✅ {data['name']}: {base_gems} gems (Rank #{rank})")
        
        return rewards

# Create quiz system
quiz_system = QuizSystem(bot)

# --- DATABASE TEST COMMAND ---
@bot.command(name="dbstatus")
async def db_status(ctx):
    """Check database status"""
    if currency_system.initialized:
        await ctx.send("✅ **Database Status:** Connected to PostgreSQL")
        
        # Test database
        user_id = str(ctx.author.id)
        await currency_system.add_gems(user_id, 10, "Test")
        balance = await currency_system.get_balance(user_id)
        
        await ctx.send(f"✅ **Test Successful!**\nYour balance: {balance['gems']} gems")
    else:
        await ctx.send("⚠️ **Database Status:** Using JSON fallback (data may reset)")
        
        if DATABASE_URL:
            await ctx.send(f"ℹ️ DATABASE_URL is set but connection failed.")
        else:
            await ctx.send(f"ℹ️ No DATABASE_URL found. Add PostgreSQL in Railway dashboard.")

# --- BOT STARTUP ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    
    # Connect to database
    print("🔌 Connecting to database...")
    connected = await currency_system.connect()
    
    if connected:
        print("✅ Database connected successfully!")
    else:
        print("⚠️ Running without database - using JSON fallback")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="!!help"
        )
    )
    print("✅ Bot ready!")

# --- Run bot ---
if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ ERROR: No TOKEN found!")