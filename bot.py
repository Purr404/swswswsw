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
DATABASE_URL = os.getenv('DATABASE_URL')

# --- Create the bot instance ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!!', intents=intents, help_command=None)

# === POSTGRESQL DATABASE CURRENCY SYSTEM ===
class DatabaseCurrencySystem:
    def __init__(self):
        self.pool = None
        self.using_database = False
        self.json_file = "user_gems.json"
        self.json_data = {}
        print(f"🔧 Database System Initialized")
        print(f"📊 DATABASE_URL available: {'YES' if DATABASE_URL else 'NO'}")
    
    async def connect(self):
        """Connect to PostgreSQL database"""
        if not DATABASE_URL:
            print("⚠️ No DATABASE_URL found. Using JSON fallback.")
            await self.load_json_data()
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
                max_size=5,
                command_timeout=60
            )
            
            # Test connection
            async with self.pool.acquire() as conn:
                # Create tables if they don't exist
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
            print("✅ Tables created/verified")
            self.using_database = True
            
            # Migrate data from JSON to database
            await self.migrate_json_to_db()
            
            return True
            
        except ImportError:
            print("❌ asyncpg not installed. Using JSON fallback.")
            await self.load_json_data()
            return False
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            await self.load_json_data()
            return False
    
    async def load_json_data(self):
        """Load data from JSON file (fallback)"""
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    self.json_data = json.load(f)
                print(f"📁 Loaded {len(self.json_data)} users from JSON backup")
            else:
                self.json_data = {}
                print("📁 No JSON backup found, starting fresh")
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
            self.json_data = {}
    
    def save_json_data(self):
        """Save data to JSON file (fallback)"""
        if not self.using_database:
            try:
                with open(self.json_file, 'w', encoding='utf-8') as f:
                    json.dump(self.json_data, f, indent=2, ensure_ascii=False)
                print(f"💾 Saved {len(self.json_data)} users to JSON")
                return True
            except Exception as e:
                print(f"❌ Error saving JSON: {e}")
                return False
        return True
    
    async def migrate_json_to_db(self):
        """Migrate data from JSON to PostgreSQL"""
        if not self.json_data or not self.using_database:
            return
        
        print("🔄 Migrating JSON data to PostgreSQL...")
        migrated = 0
        
        for user_id, data in self.json_data.items():
            try:
                async with self.pool.acquire() as conn:
                    # Check if user exists
                    exists = await conn.fetchval(
                        'SELECT user_id FROM user_gems WHERE user_id = $1',
                        user_id
                    )
                    
                    if not exists:
                        # Insert user data
                        await conn.execute('''
                            INSERT INTO user_gems (user_id, gems, total_earned, daily_streak, last_daily)
                            VALUES ($1, $2, $3, $4, $5)
                        ''', 
                        user_id,
                        data.get('gems', 0),
                        data.get('total_earned', 0),
                        data.get('daily_streak', 0),
                        data.get('last_daily')
                        )
                        
                        # Migrate transactions if any
                        transactions = data.get('transactions', [])
                        for tx in transactions[-50:]:  # Only last 50 transactions
                            await conn.execute('''
                                INSERT INTO user_transactions (user_id, type, gems, reason, balance)
                                VALUES ($1, $2, $3, $4, $5)
                            ''',
                            user_id,
                            tx.get('type', 'reward'),
                            tx.get('gems', 0),
                            tx.get('reason', ''),
                            tx.get('balance', 0)
                            )
                        
                        migrated += 1
            except Exception as e:
                print(f"❌ Error migrating user {user_id}: {e}")
        
        print(f"✅ Migrated {migrated} users to PostgreSQL")
    
    async def add_gems(self, user_id: str, gems: int, reason: str = ""):
        """Add gems to a user"""
        if self.using_database and self.pool:
            try:
                import asyncpg
                async with self.pool.acquire() as conn:
                    async with conn.transaction():
                        # Get current balance or create user
                        current = await conn.fetchval(
                            'SELECT gems FROM user_gems WHERE user_id = $1',
                            user_id
                        )
                        
                        if current is None:
                            # Create new user
                            await conn.execute('''
                                INSERT INTO user_gems (user_id, gems, total_earned)
                                VALUES ($1, $2, $2)
                                RETURNING gems
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
                                RETURNING gems
                            ''', user_id, gems)
                            current += gems
                        
                        # Log transaction
                        await conn.execute('''
                            INSERT INTO user_transactions (user_id, type, gems, reason, balance)
                            VALUES ($1, 'reward', $2, $3, $4)
                        ''', user_id, gems, reason, current)
                        
                        print(f"✅ [DB] Added {gems} gems to {user_id}. New balance: {current}")
                        return {"gems": gems, "balance": current}
                        
            except Exception as e:
                print(f"❌ Database error in add_gems: {e}")
                # Fall back to JSON
                return await self._json_add_gems(user_id, gems, reason)
        else:
            # Use JSON fallback
            return await self._json_add_gems(user_id, gems, reason)
    
    async def _json_add_gems(self, user_id: str, gems: int, reason: str = ""):
        """JSON fallback for add_gems"""
        print(f"📝 [JSON] Adding {gems} gems to {user_id}")
        
        # Get or create user
        if user_id not in self.json_data:
            self.json_data[user_id] = {
                "gems": gems,
                "total_earned": gems,
                "daily_streak": 0,
                "last_daily": None,
                "transactions": []
            }
        else:
            self.json_data[user_id]["gems"] += gems
            self.json_data[user_id]["total_earned"] += gems
        
        # Add transaction
        transaction = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "reward",
            "gems": gems,
            "reason": reason,
            "balance": self.json_data[user_id]["gems"]
        }
        
        if "transactions" not in self.json_data[user_id]:
            self.json_data[user_id]["transactions"] = []
        
        self.json_data[user_id]["transactions"].append(transaction)
        
        # Keep only last 50 transactions
        if len(self.json_data[user_id]["transactions"]) > 50:
            self.json_data[user_id]["transactions"] = self.json_data[user_id]["transactions"][-50:]
        
        self.save_json_data()
        print(f"✅ [JSON] Added {gems} gems to {user_id}. New balance: {self.json_data[user_id]['gems']}")
        return transaction
    
    async def get_balance(self, user_id: str):
        """Get user's current gems balance"""
        if self.using_database and self.pool:
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
                        return {"gems": 0, "total_earned": 0}
                        
            except Exception as e:
                print(f"❌ Database error in get_balance: {e}")
                return await self._json_get_balance(user_id)
        else:
            return await self._json_get_balance(user_id)
    
    async def _json_get_balance(self, user_id: str):
        """JSON fallback for get_balance"""
        if user_id in self.json_data:
            return {
                "gems": self.json_data[user_id].get("gems", 0),
                "total_earned": self.json_data[user_id].get("total_earned", 0)
            }
        return {"gems": 0, "total_earned": 0}
    
    async def get_leaderboard(self, limit: int = 10):
        """Get gems leaderboard"""
        if self.using_database and self.pool:
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
        else:
            return await self._json_get_leaderboard(limit)
    
    async def _json_get_leaderboard(self, limit: int = 10):
        """JSON fallback for get_leaderboard"""
        if not self.json_data:
            return []
        
        sorted_users = sorted(
            self.json_data.items(),
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
    
    async def can_claim_daily(self, user_id: str):
        """Check if user can claim daily reward"""
        if self.using_database and self.pool:
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
                    return time_diff.total_seconds() >= 86400
                    
            except Exception as e:
                print(f"❌ Database error in can_claim_daily: {e}")
                return await self._json_can_claim_daily(user_id)
        else:
            return await self._json_can_claim_daily(user_id)
    
    async def _json_can_claim_daily(self, user_id: str):
        """JSON fallback for can_claim_daily"""
        if user_id in self.json_data and self.json_data[user_id].get("last_daily"):
            last_claim_str = self.json_data[user_id]["last_daily"]
            if last_claim_str:
                try:
                    last_claim = datetime.fromisoformat(last_claim_str.replace('Z', '+00:00'))
                    time_diff = datetime.now(timezone.utc) - last_claim
                    return time_diff.total_seconds() >= 86400
                except:
                    return True
        return True
    
    async def claim_daily(self, user_id: str):
        """Claim daily reward with streak bonus"""
        now = datetime.now(timezone.utc)
        
        if self.using_database and self.pool:
            try:
                import asyncpg
                async with self.pool.acquire() as conn:
                    async with conn.transaction():
                        # Get or create user data
                        row = await conn.fetchrow(
                            'SELECT daily_streak, last_daily FROM user_gems WHERE user_id = $1',
                            user_id
                        )
                        
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
        else:
            return await self._json_claim_daily(user_id)
    
    async def _json_claim_daily(self, user_id: str):
        """JSON fallback for claim_daily"""
        now = datetime.now(timezone.utc)
        
        # Get or create user
        if user_id not in self.json_data:
            self.json_data[user_id] = {
                "gems": 0,
                "total_earned": 0,
                "daily_streak": 0,
                "last_daily": None,
                "transactions": []
            }
        
        user = self.json_data[user_id]
        
        # Check streak
        if user.get("last_daily"):
            last_claim_str = user["last_daily"]
            try:
                last_claim = datetime.fromisoformat(last_claim_str.replace('Z', '+00:00'))
                days_diff = (now - last_claim).days
                
                if days_diff == 1:
                    user["daily_streak"] += 1
                elif days_diff > 1:
                    user["daily_streak"] = 1
            except:
                user["daily_streak"] = 1
        else:
            user["daily_streak"] = 1
        
        # Calculate reward
        base_gems = random.randint(1, 100)
        streak_bonus = min(user["daily_streak"] * 0.1, 1.0)
        bonus_gems = int(base_gems * streak_bonus)
        total_gems = base_gems + bonus_gems
        
        # Update user
        user["last_daily"] = now.isoformat()
        
        # Add gems
        await self._json_add_gems(
            user_id=user_id,
            gems=total_gems,
            reason=f"🎁 Daily Reward (Streak: {user['daily_streak']} days)"
        )
        
        return {"gems": total_gems, "streak": user["daily_streak"]}

# Create database system instance
db_currency = DatabaseCurrencySystem()

# --- ANNOUNCEMENT SYSTEM ---
class AnnouncementSystem:
    def __init__(self):
        self.announcement_channels = {}
        self.announcement_images = {}
    
    def create_announcement_embed(self, message, author, title="ANNOUNCEMENT", color=0xFF5500, image_url=None):
        """Create a beautiful announcement embed"""
        embed = discord.Embed(
            title=f"📢 **{title}**",
            description=message,
            color=color,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.set_author(
            name=f"Posted by {author.display_name}",
            icon_url=author.display_avatar.url
        )
        
        if author.guild.icon:
            embed.set_thumbnail(url=author.guild.icon.url)
        
        if image_url:
            embed.set_image(url=image_url)
        
        embed.set_footer(
            text="©️ 558 Discord Server • Official Announcement",
            icon_url="https://cdn.discordapp.com/emojis/1065149931136663624.png"
        )
        
        return embed
    
    async def get_announcement_channel(self, guild):
        """Get or find announcement channel"""
        server_id = str(guild.id)
        
        if server_id in self.announcement_channels:
            channel = guild.get_channel(self.announcement_channels[server_id])
            if channel:
                return channel
        
        for channel in guild.text_channels:
            if any(keyword in channel.name.lower() for keyword in ["announce", "📢", "news"]):
                self.announcement_channels[server_id] = channel.id
                return channel
        
        for channel in guild.text_channels:
            if isinstance(channel, discord.TextChannel):
                return channel
        
        return None

# Create announcement system
announcements = AnnouncementSystem()

# --- QUIZ SYSTEM CLASS ---
class QuizSystem:
    def __init__(self, bot):
        print("=== QuizSystem.__init__ called ===")
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
        self.currency = db_currency
        
        # Load questions
        self.load_questions()
        print(f"✅ QuizSystem initialized with {len(self.quiz_questions)} questions")
    
    def load_questions(self):
        """Load quiz questions"""
        self.quiz_questions = [
            {
                "question": "What is the capital city of France?",
                "correct_answers": ["paris"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "Which planet is known as the Red Planet?",
                "correct_answers": ["mars", "planet mars"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "What is the chemical symbol for gold?",
                "correct_answers": ["au"],
                "points": 200,
                "time_limit": 45
            },
            {
                "question": "Who painted the Mona Lisa?",
                "correct_answers": ["leonardo da vinci", "da vinci", "leonardo"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "What is the largest mammal in the world?",
                "correct_answers": ["blue whale", "whale"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "How many continents are there on Earth?",
                "correct_answers": ["7", "seven"],
                "points": 200,
                "time_limit": 45
            },
            {
                "question": "What is H2O commonly known as?",
                "correct_answers": ["water", "h2o"],
                "points": 200,
                "time_limit": 45
            },
            {
                "question": "Who wrote the play 'Romeo and Juliet'?",
                "correct_answers": ["william shakespeare", "shakespeare"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "What is the fastest land animal?",
                "correct_answers": ["cheetah"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "Which country gifted the Statue of Liberty to the USA?",
                "correct_answers": ["france"],
                "points": 300,
                "time_limit": 60
            }
        ]
    
    def calculate_points(self, answer_time, total_time, max_points):
        """Calculate points based on answer speed"""
        time_left = total_time - answer_time
        if time_left <= 0:
            return 0
        percentage = time_left / total_time
        return int(max_points * percentage)
    
    async def start_quiz(self, channel, logs_channel):
        """Start a new quiz in specified channel"""
        print(f"🚀 Starting quiz in {channel.name}")
        self.quiz_channel = channel
        self.quiz_logs_channel = logs_channel
        self.quiz_running = True
        self.current_question = 0
        self.participants = {}
        
        # Shuffle questions
        random.shuffle(self.quiz_questions)
        
        # Send quiz start message
        embed = discord.Embed(
            title="🎯 **QUIZ STARTING!**",
            description=(
                "**Open-Ended Quiz**\n"
                "Think carefully and type your answers!\n\n"
                "**Rules:**\n"
                "• Type your answer exactly\n"
                "• Spelling matters!\n"
                "• Faster answers = more points!\n"
                "• You can answer multiple times!\n"
                "• Max points: 300 per question\n\n"
                f"First question starts in **5 seconds**!"
            ),
            color=discord.Color.gold()
        )
        start_msg = await channel.send(embed=embed)
        
        # Start countdown
        for i in range(5, 0, -1):
            await start_msg.edit(content=f"⏰ **{i}...**")
            await asyncio.sleep(1)
        
        await start_msg.delete()
        
        # Start first question
        await self.send_question()
    
    async def send_question(self):
        """Send current question with countdown bar"""
        if self.current_question >= len(self.quiz_questions):
            await self.end_quiz()
            return
        
        question = self.quiz_questions[self.current_question]
        self.question_start_time = datetime.now(timezone.utc)
        
        # Initial progress bar (full)
        progress_bar = "🟩" * 20
        
        # Create question embed
        embed = discord.Embed(
            title=f"❓ **Question {self.current_question + 1}/{len(self.quiz_questions)}**",
            description=question["question"],
            color=discord.Color.blue()
        )
        
        # Add countdown bar field
        embed.add_field(
            name=f"⏰ **{question['time_limit']:02d} SECONDS LEFT**",
            value=f"```\n{progress_bar}\n{question['time_limit']:02d} seconds\n```\n"
                  f"**Max Points:** {question['points']} ⭐",
            inline=False
        )
        
        embed.set_footer(text="Type your answer in the chat (multiple attempts allowed)")
        
        # Send question
        self.question_message = await self.quiz_channel.send(embed=embed)
        
        # Start the live countdown
        self.countdown_task.start(question["time_limit"])
        
        # Start question timer (for auto-ending)
        self.start_question_timer(question["time_limit"])
    
    @tasks.loop(seconds=1)
    async def countdown_task(self, total_time):
        """Update live countdown bar every second"""
        if not self.quiz_running:
            self.countdown_task.stop()
            return
        
        try:
            elapsed = (datetime.now(timezone.utc) - self.question_start_time).seconds
            time_left = total_time - elapsed
            
            if time_left <= 0:
                self.countdown_task.stop()
                return
            
            # Create progress bar
            progress = int((time_left / total_time) * 20)
            progress_bar = "🟩" * progress + "⬜" * (20 - progress)
            
            # Update embed
            embed = self.question_message.embeds[0]
            
            # Find and update the time field
            for i, field in enumerate(embed.fields):
                if "⏰" in field.name:
                    embed.set_field_at(
                        i,
                        name=f"⏰ **{time_left:02d} SECONDS LEFT**",
                        value=f"```\n{progress_bar}\n{time_left:02d} seconds\n```\n"
                              f"**Max Points:** {self.quiz_questions[self.current_question]['points']} ⭐",
                        inline=False
                    )
                    break
            
            # Change embed color based on time
            if time_left <= 10:
                embed.color = discord.Color.red()
            elif time_left <= 30:
                embed.color = discord.Color.orange()
            else:
                embed.color = discord.Color.blue()
            
            await self.question_message.edit(embed=embed)
            
        except Exception as e:
            print(f"Countdown error: {e}")
            self.countdown_task.stop()
    
    def start_question_timer(self, time_limit):
        """Start timer for current question"""
        async def timer():
            await asyncio.sleep(time_limit)
            await self.end_question()
        
        if self.question_timer:
            self.question_timer.cancel()
        
        self.question_timer = asyncio.create_task(timer())
    
    async def process_answer(self, user, answer_text):
        """Process user's answer"""
        if not self.quiz_running:
            return False
        
        question = self.quiz_questions[self.current_question]
        answer_time = (datetime.now(timezone.utc) - self.question_start_time).seconds
        
        # Check if time's up
        if answer_time > question["time_limit"]:
            return False
        
        # Initialize user in participants if not exists
        user_id = str(user.id)
        if user_id not in self.participants:
            self.participants[user_id] = {
                "name": user.display_name,
                "score": 0,
                "answers": [],
                "total_time": 0,
                "correct_answers": 0,
                "answered_current": False
            }
        
        # Check if user already got this question right
        if self.participants[user_id]["answered_current"]:
            return False
        
        # Check if answer is correct
        user_answer = answer_text.lower().strip()
        is_correct = any(correct_answer == user_answer 
                        for correct_answer in question["correct_answers"])
        
        # Calculate points (only if correct)
        points = 0
        if is_correct:
            points = self.calculate_points(
                answer_time,
                question["time_limit"],
                question["points"]
            )
            self.participants[user_id]["score"] += points
            self.participants[user_id]["correct_answers"] += 1
            self.participants[user_id]["answered_current"] = True
            print(f"✅ {user.display_name} answered correctly: {answer_text} (+{points} points)")
        
        # Record ALL attempts
        self.participants[user_id]["answers"].append({
            "question": self.current_question,
            "question_text": question["question"][:100],
            "answer": answer_text,
            "correct": is_correct,
            "points": points,
            "time": answer_time
        })
        
        return True
    
    async def end_question(self):
        """End current question"""
        print(f"📝 Ending question {self.current_question + 1}")
        self.countdown_task.stop()
        
        question = self.quiz_questions[self.current_question]
        
        # Show correct answer(s)
        correct_answers = ", ".join([a.capitalize() for a in question["correct_answers"]])
        
        embed = discord.Embed(
            title=f"✅ **Question {self.current_question + 1} Complete**",
            description=f"**Correct answer(s):** {correct_answers}",
            color=discord.Color.green()
        )
        
        await self.quiz_channel.send(embed=embed)
        
        # Wait 3 seconds
        await asyncio.sleep(3)
        
        # Reset for next question
        for user_id in self.participants:
            self.participants[user_id]["answered_current"] = False
        
        # Move to next question
        self.current_question += 1
        await self.send_question()
    
    async def end_quiz(self):
        """End the entire quiz"""
        print("🏁 Quiz finished! Starting reward distribution...")
        self.quiz_running = False
        self.countdown_task.stop()
        
        if self.question_timer:
            self.question_timer.cancel()
        
        # Sort participants by score
        sorted_participants = sorted(
            self.participants.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        # Send quiz finished message
        embed = discord.Embed(
            title="🏆 **QUIZ FINISHED!** 🏆",
            description="Congratulations to all participants!\nDistributing rewards now...",
            color=discord.Color.gold(),
            timestamp=datetime.now(timezone.utc)
        )
        
        await self.quiz_channel.send(embed=embed)
        
        # DISTRIBUTE REWARDS
        print(f"🎁 Distributing rewards to {len(sorted_participants)} participants...")
        rewards_distributed = await self.distribute_quiz_rewards(sorted_participants)
        print(f"✅ Rewards distributed to {len(rewards_distributed)} users")
        
        # Send rewards summary
        if rewards_distributed:
            rewards_embed = discord.Embed(
                title="💰 **Quiz Rewards Distributed!**",
                description=f"**Total Participants:** {len(self.participants)}\n**Total Gems Distributed:** {sum(r.get('gems', 0) for r in rewards_distributed.values())}",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            
            # Show top 3
            top_3_text = ""
            for i, (user_id, data) in enumerate(sorted_participants[:3]):
                reward = rewards_distributed.get(user_id, {})
                gems = reward.get("gems", 0)
                
                medals = ["🥇", "🥈", "🥉"]
                medal = medals[i] if i < len(medals) else f"{i+1}."
                
                top_3_text += f"{medal} **{data['name']}** - {data['score']} pts → 💎 {gems} gems\n"
            
            if top_3_text:
                rewards_embed.add_field(
                    name="🏆 **TOP 3 WINNERS**",
                    value=top_3_text,
                    inline=False
                )
            
            await self.quiz_channel.send(embed=rewards_embed)
            
            # Send DMs to participants
            dm_count = 0
            for user_id, data in self.participants.items():
                reward = rewards_distributed.get(user_id, {})
                if reward and reward.get("gems", 0) > 0:
                    user_obj = self.bot.get_user(int(user_id))
                    if user_obj:
                        try:
                            dm_embed = discord.Embed(
                                title="🎁 **Quiz Rewards Claimed!**",
                                description=f"You earned **{reward['gems']} gems** in the quiz!\nYour score: **{data['score']}** points",
                                color=discord.Color.gold()
                            )
                            await user_obj.send(embed=dm_embed)
                            dm_count += 1
                        except:
                            pass
        
        # Final message
        final_embed = discord.Embed(
            description=f"🎉 **Thank you for participating!** 🎉\n\nUse `!!currency` to check your gems\nUse `!!quiz start` to play again!",
            color=discord.Color.green()
        )
        await self.quiz_channel.send(embed=final_embed)
        
        # Reset for next quiz
        self.quiz_channel = None
        self.quiz_logs_channel = None
        self.current_question = 0
        self.participants = {}
        print("✅ Quiz reset complete")
    
    async def distribute_quiz_rewards(self, sorted_participants):
        """Distribute gems based on quiz performance"""
        print(f"🎁 Starting reward distribution for {len(sorted_participants)} participants")
        rewards = {}
        
        for rank, (user_id, data) in enumerate(sorted_participants, 1):
            print(f"  Processing rank #{rank}: {data['name']} with {data['score']} points")
            
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

# --- DATABASE TEST COMMANDS ---
@bot.command(name="dbstatus")
async def db_status(ctx):
    """Check database connection status"""
    if db_currency.using_database:
        await ctx.send("✅ **Database Status:** Connected to PostgreSQL")
        
        # Test with small transaction
        user_id = str(ctx.author.id)
        result = await db_currency.add_gems(user_id, 1, "Database test")
        
        if isinstance(result, dict) and "balance" in result:
            await ctx.send(f"✅ **Database working!** Test transaction successful.")
        else:
            await ctx.send("⚠️ Database test transaction failed")
    else:
        await ctx.send("⚠️ **Database Status:** Using JSON storage (data may reset on redeploy)")
        
        if DATABASE_URL:
            await ctx.send(f"ℹ️ DATABASE_URL is set but connection failed. Check if asyncpg is installed.")
        else:
            await ctx.send(f"ℹ️ No DATABASE_URL found. Add PostgreSQL in Railway dashboard.")

@bot.command(name="testdb")
async def test_database(ctx):
    """Test database functionality"""
    user_id = str(ctx.author.id)
    
    # Add test gems
    result = await db_currency.add_gems(user_id, 50, "Database test")
    
    if isinstance(result, dict):
        balance = await db_currency.get_balance(user_id)
        await ctx.send(f"✅ **Database Test Successful!**\nAdded 50 gems\nNew balance: **{balance['gems']} gems**")
    else:
        await ctx.send("❌ Database test failed. Using JSON fallback.")

@bot.command(name="checkdata")
async def check_data(ctx):
    """Check if data is saving properly"""
    user_id = str(ctx.author.id)
    
    # Add some gems
    await db_currency.add_gems(user_id, 10, "Data check")
    
    # Get balance
    balance = await db_currency.get_balance(user_id)
    
    if db_currency.using_database:
        storage_type = "PostgreSQL Database"
    else:
        storage_type = "JSON File"
    
    await ctx.send(f"📊 **Data Status:**\n"
                   f"Storage: **{storage_type}**\n"
                   f"Your gems: **{balance['gems']}**\n"
                   f"Data will persist: **{'YES' if db_currency.using_database else 'NO (will reset on redeploy)'}**")

# --- SIMPLE COMMANDS ---
@bot.command(name="announce")
@commands.has_permissions(manage_messages=True)
async def announce(ctx, *, message: str):
    """Send an announcement"""
    channel = await announcements.get_announcement_channel(ctx.guild)
    if not channel:
        await ctx.send("❌ No announcement channel found!")
        return
    
    embed = announcements.create_announcement_embed(
        message=message,
        author=ctx.author
    )
    
    try:
        sent_message = await channel.send("@here", embed=embed)
        await sent_message.add_reaction("📢")
        await sent_message.add_reaction("✅")
        
        await ctx.send(f"✅ Announcement sent to {channel.mention}", delete_after=5)
        await ctx.message.delete(delay=2)
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)[:100]}")

@bot.command(name="quiz")
@commands.has_permissions(manage_messages=True)
async def quiz_start_cmd(ctx, channel: discord.TextChannel = None):
    """Start a quiz"""
    if quiz_system.quiz_running:
        await ctx.send("❌ Quiz is already running!", delete_after=5)
        return
    
    quiz_channel = channel or ctx.channel
    
    if not quiz_channel.permissions_for(ctx.guild.me).send_messages:
        await ctx.send(f"❌ No permission in {quiz_channel.mention}!")
        return
    
    logs_channel = discord.utils.get(ctx.guild.channels, name="quiz-logs")
    if not logs_channel:
        try:
            logs_channel = await ctx.guild.create_text_channel("quiz-logs")
        except:
            logs_channel = ctx.channel
    
    embed = discord.Embed(
        description=f"✅ **Quiz starting in {quiz_channel.mention}!**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, delete_after=10)
    
    await quiz_system.start_quiz(quiz_channel, logs_channel)

@bot.command(name="stopquiz")
@commands.has_permissions(manage_messages=True)
async def stop_quiz(ctx):
    """Stop current quiz"""
    if not quiz_system.quiz_running:
        await ctx.send("❌ No quiz is running!", delete_after=5)
        return
    
    quiz_system.quiz_running = False
    if quiz_system.question_timer:
        quiz_system.question_timer.cancel()
    
    await ctx.send("✅ Quiz stopped!")

@bot.command(name="currency")
async def currency_cmd(ctx):
    """Check your gems"""
    user_id = str(ctx.author.id)
    balance = await db_currency.get_balance(user_id)
    
    embed = discord.Embed(
        title="💰 **Your Gems**",
        description=f"**💎 {balance['gems']} gems**\nTotal earned: **{balance['total_earned']} gems**",
        color=discord.Color.gold()
    )
    
    if db_currency.using_database:
        embed.set_footer(text="✅ Stored in PostgreSQL Database")
    else:
        embed.set_footer(text="⚠️ Stored in JSON File (may reset)")
    
    await ctx.send(embed=embed)

@bot.command(name="daily")
async def daily_cmd(ctx):
    """Claim daily reward"""
    user_id = str(ctx.author.id)
    
    if not await db_currency.can_claim_daily(user_id):
        await ctx.send("⏰ You've already claimed your daily reward today! Come back tomorrow.", delete_after=10)
        return
    
    result = await db_currency.claim_daily(user_id)
    
    if isinstance(result, dict):
        gems_earned = result.get("gems", 50)
        streak = result.get("streak", 1)
        
        embed = discord.Embed(
            title="🎁 **Daily Reward Claimed!**",
            description=f"Here's your daily reward, {ctx.author.mention}!",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="💎 Gems Earned", value=f"**+{gems_earned} gems**", inline=False)
        embed.add_field(name="🔥 Daily Streak", value=f"**{streak} days**", inline=True)
        
        if db_currency.using_database:
            embed.set_footer(text="✅ Rewards saved to database")
        else:
            embed.set_footer(text="⚠️ Rewards saved to JSON (may reset)")
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Error claiming daily reward")

@bot.command(name="leaderboard")
async def leaderboard_cmd(ctx):
    """Show gems leaderboard"""
    leaderboard = await db_currency.get_leaderboard(limit=10)
    
    embed = discord.Embed(
        title="🏆 **Gems Leaderboard**",
        color=discord.Color.gold()
    )
    
    if not leaderboard:
        embed.description = "No data yet! Join a quiz to earn gems!"
    else:
        entries = []
        for i, user in enumerate(leaderboard, 1):
            try:
                user_obj = await bot.fetch_user(int(user["user_id"]))
                username = user_obj.display_name
            except:
                username = f"User {user['user_id'][:8]}"
            
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            medal = medals[i-1] if i <= len(medals) else f"{i}."
            
            entries.append(f"{medal} **{username}** - 💎 {user['gems']:,}")
        
        embed.description = "\n".join(entries)
    
    if db_currency.using_database:
        embed.set_footer(text="✅ Data from PostgreSQL Database")
    else:
        embed.set_footer(text="⚠️ Data from JSON File")
    
    await ctx.send(embed=embed)

# --- ANSWER DETECTION ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if (quiz_system.quiz_running and 
        message.channel == quiz_system.quiz_channel):
        await quiz_system.process_answer(message.author, message.content)
    
    await bot.process_commands(message)

# --- BOT STARTUP ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    
    # Connect to database
    print("🔌 Connecting to PostgreSQL database...")
    connected = await db_currency.connect()
    
    if connected:
        print("✅ Successfully connected to PostgreSQL database!")
        print("✅ Data will persist across redeploys")
    else:
        print("⚠️ Running with JSON fallback storage")
        print("⚠️ Data may reset on redeploy - add PostgreSQL to Railway")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="!!help"
        )
    )
    print("✅ Bot ready with database support!")

# --- RUN BOT ---
if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ ERROR: No TOKEN found!")