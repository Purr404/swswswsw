import os
import sys
import json
import asyncio
import random
from datetime import datetime, timezone, timedelta

# ULTIMATE ASYNCPG INSTALLER
import subprocess

print("=== ULTIMATE ASYNCPG INSTALLER ===")

# Check if asyncpg is installed
try:
    import asyncpg
    print("✅ asyncpg is already installed")
except ImportError:
    print("❌ asyncpg not found. Installing...")
    try:
        # Install asyncpg
        subprocess.check_call([sys.executable, "-m", "pip", "install", "asyncpg>=0.29.0"])
        print("✅ asyncpg installed successfully!")
        
        # Try to import again
        import asyncpg
        print("✅ asyncpg imported successfully!")
    except Exception as e:
        print(f"❌ Failed to install asyncpg: {e}")
        print("⚠️ Bot will run with JSON fallback only")

# Now continue with the rest of your imports...

print("=== DEBUG INFO ===")
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)
print("Files in directory:", os.listdir('.'))
print("==================")

# Test asyncpg immediately
try:
    import asyncpg
    print("✅ asyncpg is installed")
    
    # Test if we can create a connection
    print("🧪 Testing asyncpg connection capability...")
    ASYNCPG_AVAILABLE = True
except ImportError as e:
    print(f"❌ asyncpg import failed: {e}")
    ASYNCPG_AVAILABLE = False
except Exception as e:
    print(f"⚠️ asyncpg test error: {e}")
    ASYNCPG_AVAILABLE = True  # Might still work

import discord
from discord.ext import commands, tasks
from typing import Optional

TOKEN = os.getenv('TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

# Debug: Print ALL environment variables that might contain database info
print("\n🔍 Searching for database environment variables...")
for key, value in os.environ.items():
    if any(db_word in key.upper() for db_word in ['DATABASE', 'POSTGRES', 'PG', 'SQL', 'URL']):
        if 'PASS' in key.upper():
            print(f"  {key}: *****")
        else:
            print(f"  {key}: {value[:80]}...")

# --- Create the bot instance ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!!', intents=intents, help_command=None)

# === DATABASE SYSTEM (PostgreSQL) ===
class DatabaseSystem:
    def __init__(self):
        self.pool = None
        self.using_database = False
        self.json_file = "user_gems.json"
        self.json_data = {}
        
    async def connect(self):
        """Connect to PostgreSQL database"""
        if not DATABASE_URL:
            print("❌ No DATABASE_URL - using JSON only")
            return False
        
        if not ASYNCPG_AVAILABLE:
            print("❌ asyncpg not available - using JSON only")
            return False
        
        print("\n🔌 Attempting database connection...")
        
        # Try different connection strategies
        connection_strategies = [
            ("Standard with SSL", {'ssl': 'require'}),
            ("Standard without SSL", {'ssl': None}),
            ("With longer timeout", {'ssl': 'require', 'command_timeout': 30}),
        ]
        
        for strategy_name, strategy_args in connection_strategies:
            print(f"  Trying: {strategy_name}...")
            try:
                self.pool = await asyncpg.create_pool(
                    DATABASE_URL,
                    min_size=1,
                    max_size=3,
                    **strategy_args
                )
                
                # Test connection
                async with self.pool.acquire() as conn:
                    result = await conn.fetchval('SELECT 1')
                    print(f"    ✅ Connection test: {result}")
                    
                    # Create table with all necessary fields
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
                
                self.using_database = True
                print(f"🎉 Success with: {strategy_name}")
                print("✅ Database connected and ready!")
                return True
                
            except Exception as e:
                print(f"    ❌ Failed: {type(e).__name__}: {str(e)[:100]}")
                continue
        
        print("❌ All connection strategies failed")
        print("⚠️ Using JSON fallback storage")
        return False
    
    async def add_gems(self, user_id: str, gems: int, reason: str = ""):
        """Add gems to a user"""
        if self.using_database:
            return await self._db_add_gems(user_id, gems, reason)
        else:
            return await self._json_add_gems(user_id, gems, reason)
    
    async def _db_add_gems(self, user_id: str, gems: int, reason: str = ""):
        """Database version"""
        try:
            async with self.pool.acquire() as conn:
                # Check if user exists
                row = await conn.fetchrow(
                    'SELECT gems FROM user_gems WHERE user_id = $1',
                    user_id
                )
                
                if row:
                    # Update existing user
                    await conn.execute('''
                        UPDATE user_gems 
                        SET gems = gems + $2,
                            total_earned = total_earned + $2,
                            updated_at = NOW()
                        WHERE user_id = $1
                    ''', user_id, gems)
                    
                    # Get new balance
                    new_row = await conn.fetchrow(
                        'SELECT gems FROM user_gems WHERE user_id = $1',
                        user_id
                    )
                    new_balance = new_row['gems']
                else:
                    # Create new user
                    await conn.execute('''
                        INSERT INTO user_gems (user_id, gems, total_earned)
                        VALUES ($1, $2, $2)
                    ''', user_id, gems)
                    new_balance = gems
                
                print(f"✅ [DB] Added {gems} gems to {user_id} (Balance: {new_balance})")
                return {"gems": gems, "balance": new_balance}
                
        except Exception as e:
            print(f"❌ Database error in add_gems: {e}")
            print("🔄 Falling back to JSON...")
            return await self._json_add_gems(user_id, gems, reason)
    
    async def _json_add_gems(self, user_id: str, gems: int, reason: str = ""):
        """JSON version (fallback)"""
        # Load JSON data
        self._load_json_data()
        
        if user_id not in self.json_data:
            self.json_data[user_id] = {
                "gems": gems,
                "total_earned": gems,
                "daily_streak": 0,
                "last_daily": None
            }
        else:
            self.json_data[user_id]["gems"] += gems
            self.json_data[user_id]["total_earned"] += gems
        
        self._save_json_data()
        balance = self.json_data[user_id]["gems"]
        print(f"✅ [JSON] Added {gems} gems to {user_id} (Balance: {balance})")
        return {"gems": gems, "balance": balance}
    
    async def get_balance(self, user_id: str):
        """Get user balance"""
        if self.using_database:
            try:
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
        """JSON version (fallback)"""
        self._load_json_data()
        if user_id in self.json_data:
            return {
                "gems": self.json_data[user_id].get("gems", 0),
                "total_earned": self.json_data[user_id].get("total_earned", 0)
            }
        return {"gems": 0, "total_earned": 0}
    
    async def get_user(self, user_id: str):
        """Get or create user data"""
        if self.using_database:
            try:
                async with self.pool.acquire() as conn:
                    row = await conn.fetchrow(
                        'SELECT gems, total_earned, daily_streak, last_daily FROM user_gems WHERE user_id = $1',
                        user_id
                    )
                    
                    if row:
                        return {
                            "gems": row['gems'],
                            "total_earned": row['total_earned'],
                            "daily_streak": row['daily_streak'] or 0,
                            "last_daily": row['last_daily'],
                            "transactions": []  # Note: Transactions not stored in DB yet
                        }
                    else:
                        # Create user if doesn't exist
                        await conn.execute('''
                            INSERT INTO user_gems (user_id, gems, total_earned)
                            VALUES ($1, 0, 0)
                        ''', user_id)
                        
                        return {
                            "gems": 0,
                            "total_earned": 0,
                            "daily_streak": 0,
                            "last_daily": None,
                            "transactions": []
                        }
                        
            except Exception as e:
                print(f"❌ Database error in get_user: {e}")
                return self._json_get_user(user_id)
        else:
            return self._json_get_user(user_id)
    
    def _json_get_user(self, user_id: str):
        """JSON version of get_user"""
        self._load_json_data()
        if user_id not in self.json_data:
            self.json_data[user_id] = {
                "gems": 0,
                "total_earned": 0,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "daily_streak": 0,
                "last_daily": None,
                "transactions": []
            }
        return self.json_data[user_id]
    
    async def can_claim_daily(self, user_id: str):
        """Check if user can claim daily reward"""
        if self.using_database:
            try:
                async with self.pool.acquire() as conn:
                    row = await conn.fetchrow(
                        'SELECT last_daily FROM user_gems WHERE user_id = $1',
                        user_id
                    )
                    
                    if not row or not row['last_daily']:
                        return True
                    
                    last_claim = row['last_daily']
                    now = datetime.now(timezone.utc)
                    
                    # Check if 24 hours have passed
                    hours_passed = (now - last_claim).total_seconds() / 3600
                    return hours_passed >= 23.5
                    
            except Exception as e:
                print(f"❌ Database error in can_claim_daily: {e}")
                return self._json_can_claim_daily(user_id)
        else:
            return self._json_can_claim_daily(user_id)
    
    def _json_can_claim_daily(self, user_id: str):
        """JSON version"""
        user = self._json_get_user(user_id)
        
        if not user["last_daily"]:
            return True
        
        try:
            last_claim = datetime.fromisoformat(user["last_daily"])
            now = datetime.now(timezone.utc)
            
            # Check if 24 hours have passed
            hours_passed = (now - last_claim).total_seconds() / 3600
            return hours_passed >= 23.5
        except:
            return True
    
    async def claim_daily(self, user_id: str):
        """Claim daily reward with streak bonus"""
        if self.using_database:
            return await self._db_claim_daily(user_id)
        else:
            return await self._json_claim_daily(user_id)
    
    async def _db_claim_daily(self, user_id: str):
        """Database version"""
        try:
            async with self.pool.acquire() as conn:
                # Get current streak and last daily
                row = await conn.fetchrow(
                    'SELECT daily_streak, last_daily FROM user_gems WHERE user_id = $1',
                    user_id
                )
                
                now = datetime.now(timezone.utc)
                
                # Calculate new streak
                if not row or not row['last_daily']:
                    new_streak = 1
                else:
                    last_claim = row['last_daily']
                    days_diff = (now - last_claim).days
                    
                    if days_diff == 1:
                        new_streak = (row['daily_streak'] or 0) + 1
                    elif days_diff > 1:
                        new_streak = 1
                    else:
                        new_streak = row['daily_streak'] or 0
                
                # Base gems (1-100) + streak bonus (up to 100% extra)
                base_gems = random.randint(1, 100)
                streak_bonus = min(new_streak * 0.1, 1.0)
                bonus_gems = int(base_gems * streak_bonus)
                total_gems = base_gems + bonus_gems
                
                # Update user with new daily claim
                await conn.execute('''
                    INSERT INTO user_gems (user_id, gems, total_earned, daily_streak, last_daily)
                    VALUES ($1, $2, $2, $3, $4)
                    ON CONFLICT (user_id) DO UPDATE 
                    SET gems = user_gems.gems + $2,
                        total_earned = user_gems.total_earned + $2,
                        daily_streak = $3,
                        last_daily = $4,
                        updated_at = NOW()
                ''', user_id, total_gems, new_streak, now)
                
                return {"gems": total_gems, "streak": new_streak}
                
        except Exception as e:
            print(f"❌ Database error in claim_daily: {e}")
            return await self._json_claim_daily(user_id)
    
    async def _json_claim_daily(self, user_id: str):
        """JSON version"""
        user = self._json_get_user(user_id)
        now = datetime.now(timezone.utc)
        
        # Check streak
        if user["last_daily"]:
            try:
                last_claim = datetime.fromisoformat(user["last_daily"])
                days_diff = (now - last_claim).days
                
                if days_diff == 1:
                    user["daily_streak"] += 1
                elif days_diff > 1:
                    user["daily_streak"] = 1
            except:
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
        user["last_daily"] = now.isoformat()
        
        # Add gems
        return await self.add_gems(
            user_id=user_id,
            gems=total_gems,
            reason=f"🎁 Daily Reward (Streak: {user['daily_streak']} days)"
        )
    
    async def get_leaderboard(self, limit: int = 10):
        """Get gems leaderboard"""
        if self.using_database:
            try:
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
                return self._json_get_leaderboard(limit)
        else:
            return self._json_get_leaderboard(limit)
    
    def _json_get_leaderboard(self, limit: int = 10):
        """JSON version"""
        self._load_json_data()
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
                "gems": data.get("gems", 0),
                "total_earned": data.get("total_earned", 0)
            }
            for user_id, data in sorted_users
        ]
    
    async def deduct_gems(self, user_id: str, gems: int, reason: str = ""):
        """Deduct gems from a user (for purchases)"""
        if self.using_database:
            try:
                async with self.pool.acquire() as conn:
                    # Check if user has enough gems
                    row = await conn.fetchrow(
                        'SELECT gems FROM user_gems WHERE user_id = $1',
                        user_id
                    )
                    
                    if not row or row['gems'] < gems:
                        return False  # Not enough gems
                    
                    # Deduct gems
                    await conn.execute('''
                        UPDATE user_gems 
                        SET gems = gems - $2,
                            updated_at = NOW()
                        WHERE user_id = $1
                    ''', user_id, gems)
                    
                    return True
                    
            except Exception as e:
                print(f"❌ Database error in deduct_gems: {e}")
                return self._json_deduct_gems(user_id, gems, reason)
        else:
            return self._json_deduct_gems(user_id, gems, reason)
    
    def _json_deduct_gems(self, user_id: str, gems: int, reason: str = ""):
        """JSON version"""
        user = self._json_get_user(user_id)
        
        if user["gems"] < gems:
            return False  # Not enough gems
        
        # Deduct gems
        user["gems"] -= gems
        user["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        self._save_json_data()
        return True
    
    def _load_json_data(self):
        """Load data from JSON file (fallback)"""
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    self.json_data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON data: {e}")
            self.json_data = {}
    
    def _save_json_data(self):
        """Save data to JSON file (fallback)"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.json_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving JSON data: {e}")
            return False

# === CREATE SHARED DATABASE SYSTEM INSTANCE ===
db = DatabaseSystem()

# --- 2. Store user selections ---
user_selections = {}

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

# --- 4. Create announcement system AFTER bot is defined ---
announcements = AnnouncementSystem()

# --- MESSAGE SENDING SYSTEM ---
@bot.group(name="say", invoke_without_command=True)
@commands.has_permissions(manage_messages=True)
async def say_group(ctx):
    """Send messages through the bot"""
    embed = discord.Embed(
        title="💬 Message Sending System",
        description=(
            "**Commands:**\n"
            "• `!!say <message>` - Send message in current channel\n"
            "• `!!say #channel <message>` - Send to specific channel\n"
            "• `!!say embed #channel <title> | <description>` - Send embed\n"
            "• `!!say reply <message_id> <message>` - Reply to a message\n"
            "• `!!say dm @user <message>` - Send DM to user\n"
        ),
        color=0x5865F2
    )
    await ctx.send(embed=embed)

# --- FIXED SAY COMMAND ---
@say_group.command(name="send")
@commands.has_permissions(manage_messages=True)
async def say_send(ctx, target: Optional[discord.TextChannel] = None, *, message: str = None):
    """
    Send a message to any channel
    Usage: !!say #channel Hello everyone!
           !!say Hello (sends in current channel)
    """
    # If no channel provided, send in current channel
    if target is None:
        # The entire content is the message
        message = ctx.message.content[len(ctx.prefix + ctx.command.name) + 1:]
        target_channel = ctx.channel
    else:
        # Channel was provided, message is already set
        target_channel = target

    if not message or message.strip() == "":
        await ctx.send("❌ Please provide a message!")
        return

    try:
        # Send the message
        sent_message = await target_channel.send(message)

        # Send confirmation
        if target_channel != ctx.channel:
            confirm_embed = discord.Embed(
                description=f"✅ **Message sent to {target_channel.mention}**\n[Jump to message]({sent_message.jump_url})",
                color=discord.Color.green()
            )
            await ctx.send(embed=confirm_embed, delete_after=10)
        else:
            # If sending in same channel, just delete command
            await ctx.message.delete(delay=2)

        # Log
        print(f"[SAY] {ctx.author} sent message to #{target_channel.name}: {message[:50]}...")

    except Exception as e:
        await ctx.send(f"❌ Failed to send message: {str(e)[:100]}")

# Alternative simpler version:
@bot.command(name="sendto")
@commands.has_permissions(manage_messages=True)
async def send_to(ctx, channel: discord.TextChannel, *, message: str):
    """
    Send message to specific channel
    Usage: !!sendto #channel Your message here
    """
    try:
        sent_message = await channel.send(message)

        confirm_embed = discord.Embed(
            description=f"✅ **Message sent to {channel.mention}**\n[Jump to message]({sent_message.jump_url})",
            color=discord.Color.green()
        )
        await ctx.send(embed=confirm_embed, delete_after=10)
        await ctx.message.delete(delay=2)

    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)[:100]}")

@bot.command(name="sendhere")
@commands.has_permissions(manage_messages=True)
async def send_here(ctx, *, message: str):
    """
    Send message in current channel
    Usage: !!sendhere Your message here
    """
    try:
        await ctx.send(message)
        await ctx.message.delete(delay=2)
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)[:100]}")

# END SEND MESSAGES COMMAND --------

# --- QUIZ SYSTEM CLASS ---
class QuizSystem:
    def __init__(self, bot):
        print("=== QuizSystem.__init__ called ===")
        
        self.bot = bot
        self.db = db  # Use the shared database system
        self.quiz_questions = []
        self.current_question = 0
        self.participants = {}
        self.question_timer = None
        self.quiz_channel = None
        self.quiz_logs_channel = None
        self.quiz_running = False
        self.question_start_time = None
        
        print(f"✓ Using shared DatabaseSystem instance")
        
        # Load 20 questions
        self.load_questions()
    
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
            },
            {
                "question": "How many sides does a hexagon have?",
                "correct_answers": ["6", "six"],
                "points": 200,
                "time_limit": 45
            },
            {
                "question": "What is the hardest natural substance on Earth?",
                "correct_answers": ["diamond"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "Which gas do plants absorb from the atmosphere?",
                "correct_answers": ["carbon dioxide", "co2"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "What is the smallest country in the world?",
                "correct_answers": ["vatican city", "vatican"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "Which planet has the most moons?",
                "correct_answers": ["saturn"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "What is the capital of Japan?",
                "correct_answers": ["tokyo"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "How many players are on a basketball team?",
                "correct_answers": ["5", "five"],
                "points": 200,
                "time_limit": 45
            },
            {
                "question": "What is the main ingredient in guacamole?",
                "correct_answers": ["avocado"],
                "points": 200,
                "time_limit": 45
            },
            {
                "question": "Which year did World War II end?",
                "correct_answers": ["1945"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "What is the currency of Japan?",
                "correct_answers": ["yen"],
                "points": 300,
                "time_limit": 60
            }
        ]
    
    # ... (ALL THE REST OF THE QUIZSYSTEM METHODS REMAIN THE SAME UNTIL distribute_quiz_rewards) ...
    
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
            
            # Add gems using the SHARED database system
            result = await self.db.add_gems(
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
    
    # ... (REST OF QUIZSYSTEM METHODS REMAIN THE SAME) ...

# === CREATE QUIZ SYSTEM WITH SHARED DATABASE ===
quiz_system = QuizSystem(bot)

# --- ANNOUNCEMENT COMMANDS ---
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

# ... (ALL ANNOUNCEMENT COMMANDS REMAIN THE SAME) ...

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

# ... (ALL QUIZ COMMANDS REMAIN THE SAME) ...

# CURRENCY COMMANDS -----
@bot.group(name="currency", invoke_without_command=True)
async def currency_group(ctx):
    """Currency and rewards commands"""
    # Get user balance using SHARED database system
    user_id = str(ctx.author.id)
    balance = await db.get_balance(user_id)
    
    embed = discord.Embed(
        title="💰 **Your Gems**",
        description=f"**💎 {balance['gems']} gems**\n"
                   f"Total earned: **{balance['total_earned']} gems**",
        color=discord.Color.gold()
    )
    
    # Check daily streak
    user_data = await db.get_user(user_id)
    if user_data["daily_streak"] > 0:
        embed.add_field(
            name="🔥 Daily Streak",
            value=f"{user_data['daily_streak']} days",
            inline=True
        )
    
    # Check next daily
    if await db.can_claim_daily(user_id):
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
    
    # Show storage type
    if db.using_database:
        embed.set_footer(text="💾 Stored in PostgreSQL Database")
    else:
        embed.set_footer(text="📄 Stored in JSON File (Fallback)")
    
    await ctx.send(embed=embed)

@currency_group.command(name="leaderboard")
async def currency_leaderboard(ctx):
    """Show gems leaderboard"""
    leaderboard = await db.get_leaderboard(limit=10)
    
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

@currency_group.command(name="transfer")
@commands.cooldown(1, 300, commands.BucketType.user)  # 5 minute cooldown
async def currency_transfer(ctx, member: discord.Member, amount: int):
    """Transfer gems to another user"""
    if amount <= 0:
        await ctx.send("❌ Amount must be positive!", delete_after=5)
        return
    
    if amount > 1000:
        await ctx.send("❌ Maximum transfer is 1,000 gems!", delete_after=5)
        return
    
    if member.bot:
        await ctx.send("❌ You can't transfer gems to bots!", delete_after=5)
        return
    
    sender_id = str(ctx.author.id)
    receiver_id = str(member.id)
    
    if sender_id == receiver_id:
        await ctx.send("❌ You can't transfer gems to yourself!", delete_after=5)
        return
    
    # Check sender's balance
    sender_balance = await db.get_balance(sender_id)
    
    if sender_balance["gems"] < amount:
        await ctx.send(f"❌ You don't have enough gems! You have {sender_balance['gems']} gems.", delete_after=5)
        return
    
    # Transfer gems (5% tax)
    tax = max(1, amount // 20)  # 5% tax, minimum 1 gem
    net_amount = amount - tax
    
    # Deduct from sender (full amount)
    success = await db.deduct_gems(
        sender_id,
        gems=amount,
        reason=f"Transfer to {member.display_name}"
    )
    
    if not success:
        await ctx.send("❌ Failed to deduct gems!", delete_after=5)
        return
    
    # Add to receiver (after tax)
    await db.add_gems(
        receiver_id,
        gems=net_amount,
        reason=f"Received from {ctx.author.display_name}"
    )
    
    embed = discord.Embed(
        title="✅ **Transfer Successful!**",
        description=f"Sent {amount} gems to {member.mention}\n"
                   f"💰 **Tax:** {tax} gems\n"
                   f"📥 **Net received:** {net_amount} gems",
        color=discord.Color.green()
    )
    
    await ctx.send(embed=embed)

@currency_transfer.error
async def currency_transfer_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        minutes = int(error.retry_after // 60)
        seconds = int(error.retry_after % 60)
        await ctx.send(f"⏰ Transfer cooldown! Try again in {minutes}m {seconds}s.", delete_after=5)

@currency_group.command(name="daily")
async def daily_reward(ctx):
    """Claim daily reward (1-100 gems + streak bonus)"""
    user_id = str(ctx.author.id)
    
    if not await db.can_claim_daily(user_id):
        # Calculate time until next daily
        user = await db.get_user(user_id)
        if user["last_daily"]:
            last_claim = datetime.fromisoformat(user["last_daily"]) if isinstance(user["last_daily"], str) else user["last_daily"]
            now = datetime.now(timezone.utc)
            hours_left = 24 - ((now - last_claim).seconds // 3600)
            minutes_left = 60 - ((now - last_claim).seconds % 3600) // 60
            
            await ctx.send(
                f"⏰ You can claim your daily reward in {hours_left}h {minutes_left}m!\n"
                f"Current streak: **{user['daily_streak']} days** 🔥",
                delete_after=10
            )
        else:
            await ctx.send("🎁 Daily reward is available now!")
        return
    
    # Claim daily reward using database system
    transaction = await db.claim_daily(user_id)
    user = await db.get_user(user_id)
    
    # Extract gems from transaction
    gems_earned = transaction["gems"]
    
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

# Add stats command
@currency_group.command(name="stats")
async def currency_stats(ctx, member: discord.Member = None):
    """Show detailed currency statistics"""
    target = member or ctx.author
    user_id = str(target.id)
    
    balance = await db.get_balance(user_id)
    user_data = await db.get_user(user_id)
    
    embed = discord.Embed(
        title=f"📊 **{target.display_name}'s Gem Stats**",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="💰 **Current Balance**",
        value=f"💎 **{balance['gems']:,} gems**",
        inline=False
    )
    
    embed.add_field(
        name="📈 **Lifetime Earnings**",
        value=f"**{balance['total_earned']:,} gems** earned",
        inline=True
    )
    
    embed.add_field(
        name="🔥 **Daily Streak**",
        value=f"**{user_data['daily_streak']} days**",
        inline=True
    )
    
    # Show storage type
    if db.using_database:
        embed.set_footer(text="💾 PostgreSQL Database | ✅ Persistent storage")
    else:
        embed.set_footer(text="📄 JSON File | ⚠️ May reset on redeploy")
    
    await ctx.send(embed=embed)

# --- ANSWER DETECTION ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Check for quiz answers (any text answer)
    if (quiz_system.quiz_running and 
        message.channel == quiz_system.quiz_channel):
        
        # Process the answer silently (NO REACTIONS)
        await quiz_system.process_answer(message.author, message.content)
    
    await bot.process_commands(message)

# --- HELP COMMAND ---
@bot.command(name="help")
async def custom_help(ctx, command: str = None):
    """Show help for commands"""
    if command:
        # Show specific command help
        cmd = bot.get_command(command)
        if cmd:
            embed = discord.Embed(
                title=f"Help: {cmd.name}",
                description=cmd.help or "No description available",
                color=0x5865F2
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Command not found!")
    else:
        # Show all commands
        embed = discord.Embed(
            title="📚 Bot Commands",
            description="**Announcement System**\n"
                       "• `!!announce` - Announcement management\n"
                       "• `!!a <message>` - Quick announcement\n\n"
                       "**Message System**\n"
                       "• `!!say` - Send messages\n"
                       "• `!!embed` - Send embed message\n"
                       "• `!!dm` - DM a user\n"
                       "• `!!smartreply` - Reply to message\n\n"
                       "**Quiz System**\n"
                       "• `!!quiz` - Quiz management\n\n"
                       "**Currency System**\n"
                       "• `!!currency` - Check your gems\n"
                       "• `!!currency daily` - Claim daily reward\n"
                       "• `!!currency leaderboard` - Top earners\n\n"
                       "**Utility**\n"
                       "• `!!ping` - Check bot latency\n"
                       "• `!!help <command>` - Get command help",
            color=0x5865F2
        )
        await ctx.send(embed=embed)

# === SIMPLE BOT COMMANDS ===
@bot.command(name="ping")
async def ping(ctx):
    """Check if bot is alive"""
    await ctx.send("🏓 Pong!")

@bot.command(name="add")
async def add_gems(ctx, amount: int = 100):
    """Add gems to your account"""
    user_id = str(ctx.author.id)
    
    # Use the shared database system
    result = await db.add_gems(
        user_id=user_id,
        gems=amount,
        reason=f"Command by {ctx.author.name}"
    )
    
    if result:
        balance = await db.get_balance(user_id)
        await ctx.send(f"✅ Added **{amount} gems**\nNew balance: **{balance['gems']} gems**")
    else:
        await ctx.send("❌ Failed to add gems")

@bot.command(name="balance")
async def balance_cmd(ctx):
    """Check your balance"""
    user_id = str(ctx.author.id)
    balance = await db.get_balance(user_id)
    
    embed = discord.Embed(
        title="💰 Your Balance",
        description=f"**💎 {balance['gems']} gems**",
        color=discord.Color.gold()
    )
    
    if db.using_database:
        embed.set_footer(text="💾 Stored in PostgreSQL Database - Persistent")
    else:
        embed.set_footer(text="📄 Stored in JSON File - May reset on redeploy")
    
    await ctx.send(embed=embed)

# === EMERGENCY FIX COMMANDS ===
@bot.command(name="testdb")
async def test_db(ctx):
    """Test database connection"""
    user_id = str(ctx.author.id)
    
    # Add gems using the shared database system
    result = await db.add_gems(
        user_id=user_id,
        gems=10,
        reason="Database test"
    )
    
    if result:
        balance = await db.get_balance(user_id)
        if db.using_database:
            await ctx.send(f"✅ **POSTGRESQL DATABASE WORKING!**\nAdded 10 gems\nNew balance: **{balance['gems']} gems**\n💾 **Storage: PostgreSQL Database**")
        else:
            await ctx.send(f"⚠️ **Using JSON Fallback**\nAdded 10 gems\nNew balance: **{balance['gems']} gems**\n📄 **Storage: JSON File**\n*Data may reset on redeploy*")
    else:
        await ctx.send("❌ **Test failed completely**")

# === BOT STARTUP ===
@bot.event
async def on_ready():
    print(f"\n✅ {bot.user} is online!")
    
    # Connect to database
    print("\n🔌 Connecting to database...")
    connected = await db.connect()
    
    if connected:
        print("🎉 POSTGRESQL DATABASE CONNECTED SUCCESSFULLY!")
        print("✅ Your data will persist across redeploys")
    else:
        print("⚠️ Using JSON fallback storage")
        print("❌ Data may reset on redeploy")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="!!help"
        )
    )
    print("\n🤖 Bot is ready!")

# === ERROR HANDLER ===
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"Command error: {error}")
    await ctx.send(f"❌ Error: {str(error)[:100]}")

# === RUN BOT ===
if __name__ == "__main__":
    if TOKEN:
        print("\n🚀 Starting bot...")
        bot.run(TOKEN)
    else:
        print("❌ ERROR: No TOKEN found in environment variables!")
        print("💡 Set TOKEN environment variable in Railway")