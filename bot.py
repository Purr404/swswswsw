import os
import sys
import json
import asyncio
import asyncpg  # ADD THIS LINE

print("=== DEBUG INFO ===")
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)
print("Files in directory:", os.listdir('.'))
print("==================")

import discord
from discord.ext import commands, tasks
import random
from discord.ui import View, Button
from datetime import datetime, timezone
from typing import Optional

def utc_now():
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)

TOKEN = os.getenv('TOKEN')


# --- 1. FIRST: Create the bot instance ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!!', intents=intents, help_command=None)

# --- 2. Store user selections ---
user_selections = {}


# === UPDATED CURRENCY SYSTEM WITH POSTGRESQL ===
class CurrencySystem:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """Connect to PostgreSQL database"""
        DATABASE_URL = os.getenv('DATABASE_URL')
        
        if not DATABASE_URL:
            print("⚠️ No DATABASE_URL found. Data will reset on redeploy!")
            return False
        
        try:
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                DATABASE_URL,
                ssl='require',
                min_size=1,
                max_size=10
            )
            
            # Create table if not exists
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_currency (
                        user_id TEXT PRIMARY KEY,
                        gems INTEGER DEFAULT 0,
                        total_earned INTEGER DEFAULT 0,
                        daily_streak INTEGER DEFAULT 0,
                        last_daily TIMESTAMP,
                        transactions JSONB DEFAULT '[]'::jsonb,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                ''')
            
            print("✅ Connected to PostgreSQL database")
            print("✅ Table 'user_currency' is ready")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            return False
    
    async def get_user(self, user_id: str):
        """Get user data, create if doesn't exist"""
        if not self.pool:
            return await self._create_default_user(user_id)
        
        try:
            async with self.pool.acquire() as conn:
                # Try to get user
                row = await conn.fetchrow(
                    'SELECT * FROM user_currency WHERE user_id = $1',
                    user_id
                )
                
                # If user doesn't exist, create them
                if not row:
                    await conn.execute('''
                        INSERT INTO user_currency (user_id) 
                        VALUES ($1)
                    ''', user_id)
                    
                    # Get the new user
                    row = await conn.fetchrow(
                        'SELECT * FROM user_currency WHERE user_id = $1',
                        user_id
                    )
                
                # Convert to dictionary
                user_data = dict(row)
                
                # Parse JSON transactions if needed
                if isinstance(user_data.get('transactions'), str):
                    try:
                        user_data['transactions'] = json.loads(user_data['transactions'])
                    except:
                        user_data['transactions'] = []
                
                return user_data
                
        except Exception as e:
            print(f"❌ Database error: {e}")
            return await self._create_default_user(user_id)
    
    async def _create_default_user(self, user_id: str):
        """Create default user data (fallback)"""
        return {
            "user_id": user_id,
            "gems": 0,
            "total_earned": 0,
            "daily_streak": 0,
            "last_daily": None,
            "transactions": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    
    async def add_gems(self, user_id: str, gems: int, reason: str = ""):
        """Add gems to user"""
        if not self.pool:
            print("⚠️ No database connection, gems won't be saved permanently!")
            return {"gems": gems, "error": "No database"}
        
        try:
            async with self.pool.acquire() as conn:
                # Get current gems
                current = await conn.fetchval(
                    'SELECT gems FROM user_currency WHERE user_id = $1',
                    user_id
                ) or 0
                
                # Create transaction record
                transaction = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "type": "reward",
                    "gems": gems,
                    "reason": reason,
                    "balance": current + gems
                }
                
                # Update user
                await conn.execute('''
                    UPDATE user_currency 
                    SET gems = gems + $2,
                        total_earned = total_earned + $2,
                        updated_at = NOW(),
                        transactions = transactions || $3::jsonb
                    WHERE user_id = $1
                ''', user_id, gems, json.dumps(transaction))
                
                return transaction
                
        except Exception as e:
            print(f"❌ Error adding gems: {e}")
            return {"gems": gems, "error": str(e)}
    
    async def deduct_gems(self, user_id: str, gems: int, reason: str = ""):
        """Deduct gems from a user"""
        if not self.pool:
            print("⚠️ No database connection")
            return False
        
        try:
            async with self.pool.acquire() as conn:
                # Check if user has enough gems
                current = await conn.fetchval(
                    'SELECT gems FROM user_currency WHERE user_id = $1',
                    user_id
                ) or 0
                
                if current < gems:
                    return False
                
                # Create transaction
                transaction = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "type": "purchase",
                    "gems": -gems,
                    "reason": reason,
                    "balance": current - gems
                }
                
                # Update user
                await conn.execute('''
                    UPDATE user_currency 
                    SET gems = gems - $2,
                        updated_at = NOW(),
                        transactions = transactions || $3::jsonb
                    WHERE user_id = $1
                ''', user_id, gems, json.dumps(transaction))
                
                return transaction
                
        except Exception as e:
            print(f"❌ Error deducting gems: {e}")
            return False
    
    async def get_balance(self, user_id: str):
        """Get user's gem balance"""
        user = await self.get_user(user_id)
        return {
            "gems": user.get("gems", 0),
            "total_earned": user.get("total_earned", 0)
        }
    
    async def get_leaderboard(self, limit: int = 10):
        """Get top users by gems"""
        if not self.pool:
            return []
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch('''
                    SELECT user_id, gems, total_earned 
                    FROM user_currency 
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
            print(f"❌ Error getting leaderboard: {e}")
            return []
    
    async def can_claim_daily(self, user_id: str):
        """Check if user can claim daily reward"""
        user = await self.get_user(user_id)
        
        if not user["last_daily"]:
            return True
        
        last_claim = user["last_daily"]
        if isinstance(last_claim, str):
            last_claim = datetime.fromisoformat(last_claim.replace('Z', '+00:00'))
        
        now = datetime.now(timezone.utc)
        hours_passed = (now - last_claim).total_seconds() / 3600
        return hours_passed >= 23.5
    
    async def claim_daily(self, user_id: str):
        """Claim daily reward with streak bonus"""
        user = await self.get_user(user_id)
        now = datetime.now(timezone.utc)
        
        # Check streak
        if user["last_daily"]:
            last_claim = user["last_daily"]
            if isinstance(last_claim, str):
                last_claim = datetime.fromisoformat(last_claim.replace('Z', '+00:00'))
            
            days_diff = (now - last_claim).days
            
            if days_diff == 1:
                user["daily_streak"] += 1
            elif days_diff > 1:
                user["daily_streak"] = 1
        else:
            user["daily_streak"] = 1
        
        # Base daily reward (1-100 gems)
        base_gems = random.randint(1, 100)
        
        # Streak bonus (extra 10% per day, max 100% bonus)
        streak_bonus = min(user["daily_streak"] * 0.1, 1.0)
        bonus_gems = int(base_gems * streak_bonus)
        
        total_gems = base_gems + bonus_gems
        
        # Update last claim
        if not self.pool:
            user["last_daily"] = now.isoformat()
        else:
            try:
                async with self.pool.acquire() as conn:
                    await conn.execute('''
                        UPDATE user_currency 
                        SET last_daily = $2,
                            daily_streak = $3,
                            updated_at = NOW()
                        WHERE user_id = $1
                    ''', user_id, now, user["daily_streak"])
            except Exception as e:
                print(f"❌ Error updating daily: {e}")
        
        # Add gems
        return await self.add_gems(
            user_id=user_id,
            gems=total_gems,
            reason=f"🎁 Daily Reward (Streak: {user['daily_streak']} days)"
        )


# CURRENCY CLASS END ----------

# --- 3. ANNOUNCEMENT SYSTEM CLASS ---
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
        
        # YOUR CUSTOM FOOTER
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

# --- 4. Create announcement system ---
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

        # Initialize CurrencySystem
        self.currency = CurrencySystem()
        
        # Load 20 questions
        self.load_questions()
    
    async def init_currency(self):
        """Initialize currency system"""
        await self.currency.connect()
    
    def load_questions(self):
        """Load 20 quiz questions with open-ended answers"""
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
            # ... (keep your existing questions)
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
        """Process user's answer - allow multiple attempts"""
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
        
        # Check if answer is correct (case-insensitive, trim spaces)
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
        
        # Record ALL attempts (both correct and incorrect)
        self.participants[user_id]["answers"].append({
            "question": self.current_question,
            "question_text": question["question"][:100],
            "answer": answer_text,
            "correct": is_correct,
            "points": points,
            "time": answer_time
        })
        
        # Log to quiz logs ONLY if correct
        if is_correct:
            await self.log_answer(user, question["question"], answer_text, points, answer_time)
        
        return True
    
    async def log_answer(self, user, question, answer, points, time):
        """Log ONLY correct answers to quiz logs channel"""
        if not self.quiz_logs_channel:
            return
        
        embed = discord.Embed(
            title="✅ **Correct Answer Logged**",
            color=discord.Color.green(),
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(name="👤 User", value=user.mention, inline=True)
        embed.add_field(name="📋 Question", value=question[:100], inline=False)
        embed.add_field(name="✏️ Answer", value=answer[:50], inline=True)
        embed.add_field(name="⭐ Points", value=str(points), inline=True)
        embed.add_field(name="⏱️ Time", value=f"{time}s", inline=True)
        embed.add_field(name="Question #", value=str(self.current_question + 1), inline=True)
        
        await self.quiz_logs_channel.send(embed=embed)
    
    async def end_question(self):
        """End current question and show live leaderboard"""
        self.countdown_task.stop()
        
        question = self.quiz_questions[self.current_question]
        
        # Show correct answer(s)
        correct_answers = ", ".join([a.capitalize() for a in question["correct_answers"]])
        
        embed = discord.Embed(
            title=f"✅ **Question {self.current_question + 1} Complete**",
            description=f"**Correct answer(s):** {correct_answers}",
            color=discord.Color.green()
        )
        
        # Show statistics for this question
        total_participants = len([p for p in self.participants.values()])
        total_answered = len([p for p in self.participants.values() if any(a["question"] == self.current_question for a in p["answers"])])
        correct_count = len([p for p in self.participants.values() if p.get("answered_current", False)])
        
        # Find fastest correct answer
        fastest_time = None
        fastest_user = None
        for user_id, data in self.participants.items():
            for answer in data["answers"]:
                if answer["question"] == self.current_question and answer["correct"]:
                    if fastest_time is None or answer["time"] < fastest_time:
                        fastest_time = answer["time"]
                        fastest_user = data["name"]
        
        embed.add_field(
            name="📊 **Question Statistics**",
            value=f"**Total Participants:** {total_participants}\n"
                  f"**Attempted This Q:** {total_answered}\n"
                  f"**Got It Right:** {correct_count}\n"
                  f"**Accuracy:** {round(correct_count/total_answered*100 if total_answered > 0 else 0, 1)}%\n"
                  + (f"**Fastest:** {fastest_user} ({fastest_time}s)" if fastest_user else "**Fastest:** No correct answers"),
            inline=False
        )
        
        await self.quiz_channel.send(embed=embed)
        
        # Wait 3 seconds
        await asyncio.sleep(3)
        
        # SHOW LIVE LEADERBOARD WITH ALL USERS
        leaderboard_embed = await self.create_live_leaderboard()
        leaderboard_message = await self.quiz_channel.send(embed=leaderboard_embed)
        
        # Countdown to next question with leaderboard showing
        countdown_seconds = 5
        for i in range(countdown_seconds, 0, -1):
            # Update leaderboard countdown
            updated_embed = await self.create_live_leaderboard(countdown=i)
            await leaderboard_message.edit(embed=updated_embed)
            await asyncio.sleep(1)
        
        await leaderboard_message.delete()
        
        # Reset answered_current for all users for next question
        for user_id in self.participants:
            self.participants[user_id]["answered_current"] = False
        
        # Move to next question
        self.current_question += 1
        await self.send_question()
    
    async def create_live_leaderboard(self, countdown=None):
        """Create a live leaderboard embed showing all participants"""
        if not self.participants:
            embed = discord.Embed(
                title="📊 **Current Leaderboard**",
                description="No participants yet!",
                color=discord.Color.blue()
            )
            return embed
        
        # Sort by score (highest first)
        sorted_participants = sorted(
            self.participants.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        # Calculate statistics
        total_questions = self.current_question + 1
        max_possible = total_questions * 300
        
        embed = discord.Embed(
            title="📊 **LIVE LEADERBOARD**",
            color=discord.Color.gold()
        )
        
        # Add countdown if provided
        if countdown:
            embed.description = f"**Next question in:** {countdown} seconds\n"
        
        # Show question progress
        embed.add_field(
            name="📈 **Progress**",
            value=f"**Question:** {self.current_question + 1}/{len(self.quiz_questions)}\n"
                  f"**Max Possible:** {max_possible} points",
            inline=False
        )
        
        # Create leaderboard entries
        leaderboard_lines = []
        for i, (user_id, data) in enumerate(sorted_participants):
            # Check user status for current question
            q_status = "⏳ Not attempted"
            current_q_points = 0
            attempts_count = 0
            
            # Count attempts for current question
            for answer in data["answers"]:
                if answer["question"] == self.current_question:
                    attempts_count += 1
                    if answer["correct"]:
                        q_status = f"✅ +{answer['points']} pts ({answer['time']}s)"
                        current_q_points = answer['points']
                        break
                    else:
                        q_status = f"❌ Wrong ({attempts_count} attempt{'s' if attempts_count > 1 else ''})"
            
            # Format line with emoji based on rank
            rank_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            emoji = rank_emoji[i] if i < len(rank_emoji) else f"{i+1}."
            
            leaderboard_lines.append(
                f"{emoji} **{data['name']}**\n"
                f"   Total: **{data['score']}** pts | This Q: {q_status}"
            )
        
        # Split leaderboard into chunks (10 per field)
        for i in range(0, len(leaderboard_lines), 10):
            chunk = leaderboard_lines[i:i + 10]
            embed.add_field(
                name=f"**Rank {i+1}-{i+len(chunk)}**" if i > 0 else "**🏆 TOP 10**",
                value="\n".join(chunk),
                inline=False
            )
        
        # Add statistics
        total_participants = len(self.participants)
        attempted_this_q = len([p for p in self.participants.values() 
                               if any(a["question"] == self.current_question for a in p["answers"])])
        correct_this_q = len([p for p in self.participants.values() if p.get("answered_current", False)])
        
        embed.add_field(
            name="📊 **Statistics**",
            value=f"**Participants:** {total_participants}\n"
                  f"**Attempted Q{self.current_question + 1}:** {attempted_this_q}/{total_participants}\n"
                  f"**Correct Q{self.current_question + 1}:** {correct_this_q}/{total_participants}",
            inline=True
        )
        
        embed.set_footer(text=f"Question {self.current_question + 1} of {len(self.quiz_questions)} | Multiple attempts allowed")
        
        return embed
    
    async def end_quiz(self):
        """End the entire quiz with improved leaderboard"""
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
        
        # First, send a congratulations embed
        embed = discord.Embed(
            title="🏆 **QUIZ FINISHED!** 🏆",
            description="Congratulations to all participants!\nHere are the final results:",
            color=discord.Color.gold(),
            timestamp=datetime.now(timezone.utc)
        )
        
        # Add quiz statistics
        total_questions = len(self.quiz_questions)
        total_correct = sum(p['correct_answers'] for p in self.participants.values())
        total_attempts = sum(len(p['answers']) for p in self.participants.values())
        total_participants = len(self.participants)
        
        embed.add_field(
            name="📊 **Quiz Statistics**",
            value=(
                f"**• Participants:** {total_participants}\n"
                f"**• Questions:** {total_questions}\n"
                f"**• Total Attempts:** {total_attempts}\n"
                f"**• Correct Answers:** {total_correct}\n"
                f"**• Overall Accuracy:** {round(total_correct/total_attempts*100 if total_attempts > 0 else 0, 1)}%\n"
                f"**• Max Possible:** {total_questions * 300} pts"
            ),
            inline=False
        )
        
        await self.quiz_channel.send(embed=embed)
        
        # Wait 2 seconds
        await asyncio.sleep(2)
        
        # Send TOP 3 WINNERS with avatars
        if len(sorted_participants) >= 3:
            # Get top 3 users
            top3_embed = discord.Embed(
                title="🎉 **TOP 3 WINNERS** 🎉",
                color=discord.Color.nitro_pink()
            )
            
            # Fetch user objects for top 3
            top3_users = []
            for i in range(min(3, len(sorted_participants))):
                user_id = int(sorted_participants[i][0])
                user_data = sorted_participants[i][1]
                
                try:
                    user = await self.bot.fetch_user(user_id)
                    top3_users.append((user, user_data))
                except:
                    # Fallback if can't fetch user
                    top3_users.append((None, user_data))
            
            # Define medals and colors
            medals = ["🥇", "🥈", "🥉"]
            colors = [0xFFD700, 0xC0C0C0, 0xCD7F32]  # Gold, Silver, Bronze
            
            # Create top 3 display
            top3_text = ""
            for i, (user, data) in enumerate(top3_users):
                medal = medals[i]
                
                # Calculate accuracy
                user_accuracy = round(data['correct_answers'] / total_questions * 100, 1)
                
                # Format user mention or name
                user_display = user.mention if user else f"**{data['name']}**"
                
                top3_text += (
                    f"{medal} **{user_display}**\n"
                    f"   ⭐ **{data['score']}** points\n"
                    f"   📊 {data['correct_answers']}/{total_questions} correct ({user_accuracy}%)\n"
                    f"   ⏱️ Avg time per correct answer: {self.calculate_average_time(data):.1f}s\n\n"
                )
            
            top3_embed.description = top3_text
            top3_embed.color = colors[0]  # Gold color for winner
            
            # Set winner's avatar as thumbnail
            if top3_users[0][0] and top3_users[0][0].avatar:
                top3_embed.set_thumbnail(url=top3_users[0][0].avatar.url)
            
            await self.quiz_channel.send(embed=top3_embed)
        
        # Wait 2 seconds
        await asyncio.sleep(2)
        
        # DISTRIBUTE REWARDS
        print(f"🔔 Starting reward distribution for {len(sorted_participants)} participants...")
        rewards_distributed = await self.distribute_quiz_rewards(sorted_participants)
        print(f"🔔 Rewards distributed to {len(rewards_distributed)} users")
        
        # Send rewards summary
        rewards_embed = discord.Embed(
            title="💰 **Quiz Rewards Distributed!**",
            color=discord.Color.green(),
            timestamp=datetime.now(timezone.utc)
        )
        
        # Show top 3 with rewards
        top_3 = []
        for i, (user_id, data) in enumerate(sorted_participants[:3]):
            reward = rewards_distributed.get(user_id, {})
            gems = reward.get("gems", 0)
            
            medal = ["🥇", "🥈", "🥉"][i]
            top_3.append(
                f"{medal} **{data['name']}** - {data['score']} pts\n"
                f"   Reward: 💎 {gems} gems"
            )
        
        if top_3:
            rewards_embed.add_field(
                name="🏆 **TOP 3 WINNERS**",
                value="\n".join(top_3),
                inline=False
            )
        
        # Show participation rewards
        if len(sorted_participants) > 3:
            rewards_embed.add_field(
                name="🎁 **Participation Rewards**",
                value=f"All {len(sorted_participants)} participants received:\n"
                      f"• 💎 50 gems for joining\n"
                      f"• +10 gems per 100 points scored\n"
                      f"• Speed bonuses for fast answers!",
                inline=False
            )
        
        await self.quiz_channel.send(embed=rewards_embed)
        
        # Send individual DMs with rewards
        for user_id, data in self.participants.items():
            reward = rewards_distributed.get(user_id, {})
            if reward:
                user_obj = self.bot.get_user(int(user_id))
                if user_obj:
                    try:
                        dm_embed = discord.Embed(
                            title="🎁 **Quiz Rewards Claimed!**",
                            description=f"**Quiz Results:**\n"
                                      f"Final Score: **{data['score']}** points\n"
                                      f"Rank: **#{list(self.participants.keys()).index(user_id) + 1}**",
                            color=discord.Color.gold()
                        )
                        
                        dm_embed.add_field(
                            name="💰 **Rewards Earned**",
                            value=f"💎 **{reward['gems']} Gems**",
                            inline=False
                        )
                        
                        balance = await self.currency.get_balance(user_id)
                        dm_embed.add_field(
                            name="📊 **New Balance**",
                            value=f"💎 Total Gems: **{balance['gems']}**",
                            inline=False
                        )
                        
                        dm_embed.set_footer(text="Use !!currency to check your gems!")
                        await user_obj.send(embed=dm_embed)
                    except:
                        pass  # User has DMs disabled
        
        # Wait 2 seconds
        await asyncio.sleep(2)
        
        # Final message
        final_embed = discord.Embed(
            description="🎉 **Thank you for participating!** 🎉\n\nUse `!!quiz start` to play again!",
            color=discord.Color.green()
        )
        final_embed.set_footer(text="Quiz System • Powered by 558 Discord Server")
        
        await self.quiz_channel.send(embed=final_embed)
        
        # Reset for next quiz
        self.quiz_channel = None
        self.quiz_logs_channel = None
        self.current_question = 0
        self.participants = {}
    
    def calculate_average_time(self, user_data):
        """Calculate average time for correct answers"""
        correct_times = [a['time'] for a in user_data['answers'] if a['correct']]
        if not correct_times:
            return 0
        return sum(correct_times) / len(correct_times)
    
    def get_rank_emoji(self, rank):
        """Get appropriate emoji for rank position"""
        rank_emojis = {
            1: "🥇",
            2: "🥈", 
            3: "🥉",
            4: "4️⃣",
            5: "5️⃣",
            6: "6️⃣",
            7: "7️⃣",
            8: "8️⃣",
            9: "9️⃣",
            10: "🔟"
        }
        return rank_emojis.get(rank, f"{rank}.")
    
    async def distribute_quiz_rewards(self, sorted_participants):
        """Distribute gems based on quiz performance"""
        rewards = {}
        total_participants = len(sorted_participants)
        
        for rank, (user_id, data) in enumerate(sorted_participants, 1):
            base_gems = 50  # Participation reward
            
            # Rank-based bonuses
            if rank == 1:  # 1st place
                base_gems += 500
            elif rank == 2:  # 2nd place
                base_gems += 250
            elif rank == 3:  # 3rd place
                base_gems += 125
            elif rank <= 10:  # Top 10
                base_gems += 75
            
            # Score-based bonus: 10 gems per 100 points
            score_bonus = (data["score"] // 100) * 10
            base_gems += score_bonus
            
            # Perfect score bonus
            max_score = len(self.quiz_questions) * 300
            if data["score"] == max_score:
                base_gems += 250
                reason = f"🎯 Perfect Score! ({data['score']} pts, Rank #{rank})"
            else:
                reason = f"🏆 Quiz Rewards ({data['score']} pts, Rank #{rank})"
            
            # Speed bonus for fast answers
            speed_bonus = self.calculate_speed_bonus(user_id)
            if speed_bonus:
                base_gems += speed_bonus
                reason += f" + ⚡{speed_bonus} speed bonus"
            
            # Add gems to user
            transaction = await self.currency.add_gems(
                user_id=user_id,
                gems=base_gems,
                reason=reason
            )
            
            rewards[user_id] = {
                "gems": base_gems,
                "rank": rank
            }
            
            # Log reward distribution
            await self.log_reward(user_id, data["name"], base_gems, rank)
        
        return rewards
    
    def calculate_speed_bonus(self, user_id):
        """Calculate speed bonus for fast answers"""
        if user_id not in self.participants:
            return 0
        
        speed_bonus = 0
        for answer in self.participants[user_id]["answers"]:
            if answer["correct"] and answer["time"] < 10:
                # Bonus gems for answering under 10 seconds
                speed_bonus += max(1, 10 - answer["time"])
        
        return min(speed_bonus, 50)  # Cap at 50 gems
    
    async def log_reward(self, user_id, username, gems, rank):
        """Log reward distribution"""
        if not self.quiz_logs_channel:
            return
        
        embed = discord.Embed(
            title="💰 **Gems Distributed**",
            color=discord.Color.gold(),
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(name="👤 User", value=username, inline=True)
        embed.add_field(name="🏆 Rank", value=f"#{rank}", inline=True)
        embed.add_field(name="💎 Gems", value=f"+{gems}", inline=True)
        
        await self.quiz_logs_channel.send(embed=embed)

# Create quiz system instance
quiz_system = QuizSystem(bot)

# --- ANNOUNCEMENT COMMANDS (keep your existing ones) ---
@bot.group(name="announce", invoke_without_command=True)
@commands.has_permissions(manage_messages=True)
async def announce_group(ctx):
    """Announcement management system"""
    embed = discord.Embed(
        title="📢 **Announcement System**",
        description=(
            "**Commands:**\n"
            "• `!!announce send <message>` - Send announcement\n"
            "• `!!announce channel #channel` - Set announcement channel\n"
            "• `!!announce preview <message>` - Preview announcement\n"
            "• `!!announce image <url>` - Add image to announcement\n"
            "• `!!announce urgent <message>` - Red urgent announcement\n"
        ),
        color=0x5865F2
    )
    await ctx.send(embed=embed)

# ... (keep all your existing announcement commands)

# --- QUIZ COMMANDS ---
@bot.group(name="quiz", invoke_without_command=True)
@commands.has_permissions(manage_messages=True)
async def quiz_group(ctx):
    """Quiz system commands"""
    embed = discord.Embed(
        title="🎯 **Quiz System**",
        description="**Commands:**\n"
                   "• `!!quiz start` - Start quiz in THIS channel\n"
                   "• `!!quiz start #channel` - Start quiz in specific channel\n"
                   "• `!!quiz stop` - Stop current quiz\n"
                   "• `!!quiz leaderboard` - Show current scores\n"
                   "• `!!quiz addq` - Add a new question",
        color=0x5865F2
    )
    await ctx.send(embed=embed)

@quiz_group.command(name="start")
@commands.has_permissions(manage_messages=True)
async def quiz_start(ctx, channel: discord.TextChannel = None):
    """Start a quiz"""
    if quiz_system.quiz_running:
        await ctx.send("❌ Quiz is already running!", delete_after=5)
        return
    
    # Determine which channel to use
    quiz_channel = channel or ctx.channel
    
    # Check permissions
    if not quiz_channel.permissions_for(ctx.guild.me).send_messages:
        await ctx.send(f"❌ I don't have permission to send messages in {quiz_channel.mention}!")
        return
    
    # Find or create quiz-logs channel
    logs_channel = discord.utils.get(ctx.guild.channels, name="quiz-logs")
    if not logs_channel:
        try:
            logs_channel = await ctx.guild.create_text_channel(
                "quiz-logs",
                reason="Auto-created quiz logs channel"
            )
        except:
            logs_channel = ctx.channel
    
    # Confirm
    embed = discord.Embed(
        description=f"✅ **Quiz starting in {quiz_channel.mention}!**\n"
                   f"Logs will go to {logs_channel.mention}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, delete_after=10)
    
    # Start quiz
    await quiz_system.start_quiz(quiz_channel, logs_channel)

# ... (keep other quiz commands)

# --- CURRENCY COMMANDS ---
@bot.group(name="currency", invoke_without_command=True)
async def currency_group(ctx):
    """Currency and rewards commands"""
    # Get user balance
    user_id = str(ctx.author.id)
    balance = await quiz_system.currency.get_balance(user_id)
    
    embed = discord.Embed(
        title="💰 **Your Gems**",
        description=f"**💎 {balance['gems']} gems**\n"
                   f"Total earned: **{balance['total_earned']} gems**",
        color=discord.Color.gold()
    )
    
    # Check daily streak
    user_data = await quiz_system.currency.get_user(user_id)
    if user_data["daily_streak"] > 0:
        embed.add_field(
            name="🔥 Daily Streak",
            value=f"{user_data['daily_streak']} days",
            inline=True
        )
    
    # Check next daily
    if await quiz_system.currency.can_claim_daily(user_id):
        embed.add_field(
            name="🎁 Daily Reward",
            value="Available now!",
            inline=True
        )
    else:
        embed.add_field(
            name="⏰ Next Daily",
            value="Check back soon",
            inline=True
        )
    
    embed.set_footer(text="Earn more by participating in quizzes!")
    await ctx.send(embed=embed)

@currency_group.command(name="leaderboard")
async def currency_leaderboard(ctx):
    """Show gems leaderboard"""
    leaderboard = await quiz_system.currency.get_leaderboard(limit=10)
    
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
    
    await ctx.send(embed=embed)

@currency_group.command(name="daily")
async def daily_reward(ctx):
    """Claim daily reward"""
    user_id = str(ctx.author.id)
    
    if not await quiz_system.currency.can_claim_daily(user_id):
        # Calculate time until next daily
        user = await quiz_system.currency.get_user(user_id)
        last_claim = user["last_daily"]
        if last_claim and isinstance(last_claim, str):
            last_claim = datetime.fromisoformat(last_claim.replace('Z', '+00:00'))
        
        if last_claim:
            now = datetime.now(timezone.utc)
            next_claim = last_claim.replace(tzinfo=timezone.utc) + timedelta(hours=24)
            time_left = next_claim - now
            
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60
            
            await ctx.send(
                f"⏰ You can claim your daily reward in {hours}h {minutes}m!\n"
                f"Current streak: **{user['daily_streak']} days** 🔥",
                delete_after=10
            )
        return
    
    # Claim daily reward
    transaction = await quiz_system.currency.claim_daily(user_id)
    user = await quiz_system.currency.get_user(user_id)
    
    # Extract gems from transaction
    gems_earned = transaction["gems"] if isinstance(transaction, dict) else 100
    
    embed = discord.Embed(
        title="🎁 **Daily Reward Claimed!**",
        description=f"Here's your daily reward, {ctx.author.mention}!",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="💎 Gems Earned",
        value=f"**+{gems_earned} gems**",
        inline=False
    )
    
    embed.add_field(
        name="🔥 Daily Streak",
        value=f"**{user['daily_streak']} days**",
        inline=True
    )
    
    embed.set_footer(text="Come back tomorrow for more gems!")
    await ctx.send(embed=embed)

# --- TEST DATABASE COMMAND ---
@bot.command(name="testdb")
async def test_database(ctx):
    """Test if database is working"""
    user_id = str(ctx.author.id)
    
    # Add test gems
    result = await quiz_system.currency.add_gems(user_id, 10, "Test reward")
    
    if isinstance(result, dict) and "error" in result:
        await ctx.send(f"❌ Database error: {result['error']}\n⚠️ Data will reset on redeploy!")
    else:
        balance = await quiz_system.currency.get_balance(user_id)
        await ctx.send(f"✅ Database working! You now have {balance['gems']} gems\n✅ Your gems will persist after redeploy!")

# --- ANSWER DETECTION ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Check for quiz answers
    if (quiz_system.quiz_running and 
        message.channel == quiz_system.quiz_channel):
        
        # Process the answer silently
        await quiz_system.process_answer(message.author, message.content)
    
    await bot.process_commands(message)

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    
    # Initialize currency database
    await quiz_system.init_currency()
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="!!help"
        )
    )
    print("✅ Bot ready with PostgreSQL database!")

# --- RUN BOT ---
if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ ERROR: No TOKEN found in environment variables!")