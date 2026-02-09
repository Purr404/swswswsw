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


# === DATABASE SYSTEM (PostgreSQL ONLY) ===
class DatabaseSystem:
    def __init__(self):
        self.pool = None
        self.using_database = False

    async def smart_connect(self):
        """Connect to PostgreSQL database"""
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL is required for PostgreSQL connection")

        if not ASYNCPG_AVAILABLE:
            raise ImportError("asyncpg is required for database operations")

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

                    # Create transactions table for history
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS user_transactions (
                            id SERIAL PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            timestamp TIMESTAMP DEFAULT NOW(),
                            type VARCHAR(20),
                            gems INTEGER,
                            reason TEXT,
                            balance_after INTEGER,
                            FOREIGN KEY (user_id) REFERENCES user_gems(user_id) ON DELETE CASCADE
                        )
                    ''')

                self.using_database = True
                print(f"🎉 Success with: {strategy_name}")
                print("✅ Database connected and ready!")
                return True

            except Exception as e:
                print(f"    ❌ Failed: {type(e).__name__}: {str(e)[:100]}")
                continue

        raise ConnectionError("All connection strategies failed. Could not connect to PostgreSQL.")

    async def add_gems(self, user_id: str, gems: int, reason: str = ""):
        """Add gems to a user"""
        if not self.using_database:
            raise RuntimeError("Database not connected")
        
        print(f"🔍 DB DEBUG: add_gems called with user_id={user_id}, gems={gems}, reason='{reason}'")
    
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    # Check if user exists
                    row = await conn.fetchrow(
                        'SELECT gems FROM user_gems WHERE user_id = $1',
                        user_id
                    )
                
                    print(f"🔍 DB DEBUG: User exists check: {row is not None}")

                    if row:
                       # Update existing user
                        await conn.execute('''
                            UPDATE user_gems 
                            SET gems = gems + $2,
                                total_earned = total_earned + $2,
                                updated_at = NOW()
                            WHERE user_id = $1
                            RETURNING gems
                        ''', user_id, gems)
                    
                        # Get new balance
                        new_row = await conn.fetchrow(
                            'SELECT gems FROM user_gems WHERE user_id = $1',
                            user_id
                        )
                        new_balance = new_row['gems']
                        print(f"🔍 DB DEBUG: Updated existing user. New balance: {new_balance}")
                    else:
                        # Create new user
                        await conn.execute('''
                            INSERT INTO user_gems (user_id, gems, total_earned)
                            VALUES ($1, $2, $2)
                            RETURNING gems
                        ''', user_id, gems)
                        new_balance = gems
                        print(f"🔍 DB DEBUG: Created new user. Balance: {new_balance}")

                    # Record transaction
                    await conn.execute('''
                        INSERT INTO user_transactions (user_id, type, gems, reason, balance_after)
                        VALUES ($1, 'reward', $2, $3, $4)
                    ''', user_id, gems, reason, new_balance)
                
                    print(f"🔍 DB DEBUG: Transaction recorded successfully")
                    print(f"✅ DB DEBUG: Added {gems} gems to {user_id} (Balance: {new_balance})")

                    return {"gems": gems, "balance": new_balance}

        except Exception as e:
            print(f"❌ DB DEBUG: Database error in add_gems: {e}")
            import traceback
            traceback.print_exc()
            raise


    async def get_balance(self, user_id: str):
        """Get user balance"""
        if not self.using_database:
            raise RuntimeError("Database not connected")
            
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    'SELECT gems, total_earned FROM user_gems WHERE user_id = $1',
                    user_id
                )

                if row:
                    return {"gems": row['gems'], "total_earned": row['total_earned']}
                else:
                    # Create user if doesn't exist
                    await conn.execute('''
                        INSERT INTO user_gems (user_id, gems, total_earned)
                        VALUES ($1, 0, 0)
                        ON CONFLICT (user_id) DO NOTHING
                    ''', user_id)
                    return {"gems": 0, "total_earned": 0}

        except Exception as e:
            print(f"❌ Database error in get_balance: {e}")
            raise

    async def get_user(self, user_id: str):
        """Get or create user data"""
        if not self.using_database:
            raise RuntimeError("Database not connected")
            
        try:
            async with self.pool.acquire() as conn:
                # Get or create user
                await conn.execute('''
                    INSERT INTO user_gems (user_id, gems, total_earned)
                    VALUES ($1, 0, 0)
                    ON CONFLICT (user_id) DO NOTHING
                ''', user_id)

                # Fetch user data
                row = await conn.fetchrow('''
                    SELECT gems, total_earned, daily_streak, last_daily 
                    FROM user_gems 
                    WHERE user_id = $1
                ''', user_id)

                # Format last_daily for output
                last_daily_str = None
                if row['last_daily']:
                    # Ensure timezone info
                    last_daily = row['last_daily']
                    if last_daily.tzinfo is None:
                        last_daily = last_daily.replace(tzinfo=timezone.utc)
                last_daily_str = last_daily.isoformat()

                # Get recent transactions
                transactions = await conn.fetch('''
                    SELECT timestamp, type, gems, reason, balance_after
                    FROM user_transactions
                    WHERE user_id = $1
                    ORDER BY timestamp DESC
                    LIMIT 10
                ''', user_id)

                return {
                    "gems": row['gems'],
                    "total_earned": row['total_earned'],
                    "daily_streak": row['daily_streak'] or 0,
                    "last_daily": last_daily_str,
                    "transactions": [
                        {
                            "timestamp": tx['timestamp'].isoformat(),
                            "type": tx['type'],
                            "gems": tx['gems'],
                            "reason": tx['reason'],
                            "balance": tx['balance_after']
                        }
                        for tx in transactions
                    ]
                }

        except Exception as e:
            print(f"❌ Database error in get_user: {e}")
            raise

    async def can_claim_daily(self, user_id: str):
        """Check if user can claim daily reward"""
        if not self.using_database:
            raise RuntimeError("Database not connected")
            
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

                # Ensure last_claim has timezone info for comparison
                if last_claim.tzinfo is None:
                    last_claim = last_claim.replace(tzinfo=timezone.utc)
                else:
                    # Convert to UTC if it has timezone
                    last_claim = last_claim.astimezone(timezone.utc)

                # Check if 24 hours have passed
                hours_passed = (now - last_claim).total_seconds() / 3600
                return hours_passed >= 23.5

        except Exception as e:
            print(f"❌ Database error in can_claim_daily: {e}")
            raise

    async def claim_daily(self, user_id: str):
        """Claim daily reward with streak bonus"""
        if not self.using_database:
            raise RuntimeError("Database not connected")
            
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    # Get current streak and last daily
                    row = await conn.fetchrow(
                        'SELECT daily_streak, last_daily FROM user_gems WHERE user_id = $1',
                        user_id
                    )

                    now = datetime.now(timezone.utc)
                    postgres_now = now.replace(tzinfo=None)  # Remove timezone for PostgreSQL

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
                        RETURNING gems
                    ''', user_id, total_gems, new_streak, postgres_now)  # Use postgres_now

                    # Get new balance
                    new_row = await conn.fetchrow(
                        'SELECT gems FROM user_gems WHERE user_id = $1',
                        user_id
                    )
                    new_balance = new_row['gems']

                    # Record transaction
                    await conn.execute('''
                        INSERT INTO user_transactions (user_id, type, gems, reason, balance_after)
                        VALUES ($1, 'daily', $2, $3, $4)
                    ''', user_id, total_gems, f"🎁 Daily Reward (Streak: {new_streak} days)", new_balance)

                    return {"gems": total_gems, "streak": new_streak, "balance": new_balance}

        except Exception as e:
            print(f"❌ Database error in claim_daily: {e}")
            raise

    async def get_leaderboard(self, limit: int = 10):
        """Get gems leaderboard"""
        if not self.using_database:
            raise RuntimeError("Database not connected")
            
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
            raise

    async def deduct_gems(self, user_id: str, gems: int, reason: str = ""):
        """Deduct gems from a user (for purchases)"""
        if not self.using_database:
            raise RuntimeError("Database not connected")
            
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
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
                        RETURNING gems
                    ''', user_id, gems)

                    # Get new balance
                    new_row = await conn.fetchrow(
                        'SELECT gems FROM user_gems WHERE user_id = $1',
                        user_id
                    )
                    new_balance = new_row['gems']

                    # Record transaction
                    await conn.execute('''
                        INSERT INTO user_transactions (user_id, type, gems, reason, balance_after)
                        VALUES ($1, 'purchase', $2, $3, $4)
                    ''', user_id, -gems, reason, new_balance)

                    return True

        except Exception as e:
            print(f"❌ Database error in deduct_gems: {e}")
            raise

    async def get_user_count(self):
        """Get total number of users in database"""
        if not self.using_database:
            raise RuntimeError("Database not connected")
            
        try:
            async with self.pool.acquire() as conn:
                count = await conn.fetchval('SELECT COUNT(*) FROM user_gems')
                return count
        except Exception as e:
            print(f"❌ Database error in get_user_count: {e}")
            raise

    async def get_transactions(self, user_id: str, limit: int = 10):
        """Get user's recent transactions"""
        if not self.using_database:
            raise RuntimeError("Database not connected")
            
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch('''
                    SELECT timestamp, type, gems, reason, balance_after
                    FROM user_transactions
                    WHERE user_id = $1
                    ORDER BY timestamp DESC
                    LIMIT $2
                ''', user_id, limit)

                return [
                    {
                        "timestamp": row['timestamp'].isoformat(),
                        "type": row['type'],
                        "gems": row['gems'],
                        "reason": row['reason'],
                        "balance": row['balance_after']
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"❌ Database error in get_transactions: {e}")
            return []

    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            self.using_database = False
            print("✅ Database connection pool closed")

# CREATE DATABASE INSTANCE
db = DatabaseSystem()

# --- 2. Store user selections ---
user_selections = {}

# === POSTGRESQL CURRENCY SYSTEM ===
class CurrencySystem:
    def __init__(self, database):
        self.db = database
    
    async def get_balance(self, user_id: str):
        """Get user balance from PostgreSQL"""
        return await self.db.get_balance(user_id)
    
    async def add_gems(self, user_id: str, gems: int, reason: str = ""):
        """Add gems to user in PostgreSQL"""
        return await self.db.add_gems(user_id, gems, reason)
    
    async def deduct_gems(self, user_id: str, gems: int, reason: str = ""):
        """Deduct gems from user in PostgreSQL"""
        return await self.db.deduct_gems(user_id, gems, reason)
    
    async def get_user(self, user_id: str):
        """Get or create user data from PostgreSQL"""
        return await self.db.get_user(user_id)
    
    async def can_claim_daily(self, user_id: str):
        """Check if user can claim daily reward"""
        return await self.db.can_claim_daily(user_id)
    
    async def claim_daily(self, user_id: str):
        """Claim daily reward with streak bonus"""
        return await self.db.claim_daily(user_id)
    
    async def get_leaderboard(self, limit: int = 10):
        """Get gems leaderboard from PostgreSQL"""
        return await self.db.get_leaderboard(limit)
    
    async def get_transactions(self, user_id: str, limit: int = 10):
        """Get user's recent transactions"""
        return await self.db.get_transactions(user_id, limit)

# === CREATE SHARED CURRENCY SYSTEM INSTANCE ===
currency_system = CurrencySystem(db)

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



# --- QUIZ SYSTEM CLASS ---
class QuizSystem:
    def __init__(self, bot):
        print("=== QuizSystem.__init__ called ===")
        
        self.bot = bot
        self.currency = currency_system  # Use the SHARED currency system
        self.quiz_questions = []
        self.current_question = 0
        self.participants = {}
        self.question_timer = None
        self.quiz_channel = None
        self.quiz_logs_channel = None
        self.quiz_running = False
        self.question_start_time = None
        
        print(f"✓ Using shared CurrencySystem instance")
        print(f"  currency attribute: {hasattr(self, 'currency')}")
        
        # Load 5 questions
        self.load_questions()
    
    def load_questions(self):
        """Load 5 quiz questions with open-ended answers"""
        self.quiz_questions = [
            {
                "question": "What is the capital city of France?",
                "correct_answers": ["paris"],
                "points": 300,
                "time_limit": 30
            },
            {
                "question": "Which planet is known as the Red Planet?",
                "correct_answers": ["mars", "planet mars"],
                "points": 300,
                "time_limit": 30
            },
            {
                "question": "What is the chemical symbol for gold?",
                "correct_answers": ["au"],
                "points": 200,
                "time_limit": 30
            },
            {
                "question": "Who painted the Mona Lisa?",
                "correct_answers": ["leonardo da vinci", "da vinci", "leonardo"],
                "points": 300,
                "time_limit": 30
            },
            {
                "question": "What is the largest mammal in the world?",
                "correct_answers": ["blue whale", "whale"],
                "points": 300,
                "time_limit": 30
            },

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
        for i in range(10, 0, -1):
            await start_msg.edit(content=f"⏰ **{i}...**")
            await asyncio.sleep(1)
        
        await start_msg.delete()
        
        # Start first question
        await self.send_question()
    
    async def send_question(self):
        """Send current question with countdown bar"""
        print(f"\n" + "="*80)
        print(f"❓❓❓ SEND_QUESTION DEBUG START ❓❓❓")
        print(f"❓ Time: {datetime.now(timezone.utc).strftime('%H:%M:%S')}")
        print(f"❓ current_question: {self.current_question}")
        print(f"❓ total_questions: {len(self.quiz_questions)}")
        print(f"❓ Quiz running: {self.quiz_running}")
        print(f"\n🔥 send_question called - Current: {self.current_question}, Total: {len(self.quiz_questions)}")

        # SAFETY CHECK: If somehow we're at or past the last question
        if self.current_question is None:
            print(f"❌❌❌ ERROR: current_question is None!")
            return
        
        # CHECK IF NO MORE QUESTIONS
        if self.current_question >= len(self.quiz_questions):
            print(f"🚨🚨🚨 CRITICAL: current_question ({self.current_question}) >= total_questions ({len(self.quiz_questions)})")
            print(f"🚨🚨🚨 Quiz should have ended already!")
            print(f"🚨🚨🚨 Calling end_quiz() directly...")
            await self.end_quiz()
            print(f"🔥🔥🔥 NO MORE QUESTIONS! Calling end_quiz()")
            await self.end_quiz()
            return

        print(f"❓ This is Question {self.current_question + 1} of {len(self.quiz_questions)}")

        
        
        question = self.quiz_questions[self.current_question]
        print(f"❓ Question text: {question['question'][:50]}...")
        print(f"❓ Time limit: {question['time_limit']}s")
        print(f"❓ Max points: {question['points']}")

        self.question_start_time = datetime.now(timezone.utc)  # FIXED
        
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
            
            print(f"\n✅ SEND_QUESTION DEBUG COMPLETE - Question sent successfully")
            print("="*80)
            
        except Exception as e:
            print(f"\n❌❌❌ ERROR in send_question: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            await self.end_quiz()
    
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
    print(f"\n" + "="*80)
    print(f"🚨🚨🚨 END_QUESTION DEBUG START 🚨🚨🚨")
    print(f"🚨 Time: {datetime.now(timezone.utc).strftime('%H:%M:%S')}")
    print(f"🚨 current_question BEFORE: {self.current_question}")
    print(f"🚨 Total questions: {len(self.quiz_questions)}")
    print(f"🚨 Quiz running: {self.quiz_running}")
    print(f"🚨 Participants count: {len(self.participants)}")
    print(f"\n🔥 end_question called - Question {self.current_question + 1}/{len(self.quiz_questions)}")

    # Log all participants for debugging
    for user_id, data in self.participants.items():
        print(f"🚨 Participant: {data['name']} - Score: {data['score']}, Answered current: {data.get('answered_current', False)}")

    try:
        self.countdown_task.stop()
    except:
        pass

    # Validate current_question
    if self.current_question is None:
        print(f"❌❌❌ ERROR: current_question is None!")
        return

    if self.current_question < 0 or self.current_question >= len(self.quiz_questions):
        print(f"❌❌❌ ERROR: Invalid current_question: {self.current_question}")
        print(f"❌❌❌ Should be between 0 and {len(self.quiz_questions)-1}")
        return

    question = self.quiz_questions[self.current_question]
    print(f"🚨 Processing question: {question['question'][:50]}...")

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
    reset_count = 0  # <-- ADD THIS - YOU WERE MISSING IT!
    for user_id in self.participants:
        if self.participants[user_id].get("answered_current", False):
            reset_count += 1
        self.participants[user_id]["answered_current"] = False
    
    print(f"🚨 Reset answered_current for {reset_count} users")

    # Move to next question
    old_index = self.current_question
    self.current_question += 1
    
    print(f"\n" + "➡️"*80)
    print(f"➡️ AFTER INCREMENT:")
    print(f"➡️ Changed from index {old_index} to {self.current_question}")
    print(f"➡️ This was Question {old_index + 1} of {len(self.quiz_questions)}")
    print(f"➡️ Total questions: {len(self.quiz_questions)}")
    print(f"➡️ New index: {self.current_question}")
    print(f"➡️ Should end? {self.current_question} == {len(self.quiz_questions)} = {self.current_question == len(self.quiz_questions)}")

    print(f"🔥 New question index: {self.current_question}")
    print(f"🔥 Total questions: {len(self.quiz_questions)}")

    # CHECK IF QUIZ IS FINISHED
    if self.current_question == len(self.quiz_questions):
        print(f"\n" + "🎯"*80)
        print(f"🎯🎯🎯 ALL QUESTIONS DONE! 🎯🎯🎯")
        print(f"🎯 current_question: {self.current_question}")
        print(f"🎯 total_questions: {len(self.quiz_questions)}")
        print(f"🎯 Calling end_quiz() NOW...")
        print("🎯"*80)
        print(f"🔥🔥🔥 QUIZ FINISHED! Calling end_quiz()")
        await self.end_quiz()
    else:
        print(f"\n" + "⏭️"*80)
        print(f"⏭️ MORE QUESTIONS LEFT")
        print(f"⏭️ Next will be Question {self.current_question + 1}")
        print(f"⏭️ Calling send_question()...")
        print("⏭️"*80)
        print(f"🔥 More questions left, calling send_question()")
        await self.send_question()

    print(f"\n✅ END_QUESTION DEBUG COMPLETE")
    print("="*80)
    
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
        print(f"\n" + "🎯"*60)
        print(f"🎯🎯🎯 END_QUIZ CALLED! - Question {self.current_question}/{len(self.quiz_questions)}")
        print(f"🎯 Participants: {len(self.participants)}")
        print(f"🔥 CRITICAL: end_quiz STARTED - Participants: {len(self.participants)}")
        print(f"🔥🔥🔥 Quiz channel: {self.quiz_channel}")
        print(f"🔥🔥🔥 Quiz running: {self.quiz_running}")
        
        # Log all participants
        for user_id, data in self.participants.items():
            print(f"🔥 Participant: {data['name']} (ID: {user_id}) - Score: {data['score']}")
    
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
        total_correct = sum(p['correct_answers'] for p in   self.participants.values())
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

        print(f"\n🔥🔥🔥 ABOUT TO DISTRIBUTE REWARDS")
        print(f"🔥🔥🔥 Sorted participants count: {len(sorted_participants)}")

        # DISTRIBUTE REWARDS FIRST
        print(f"🔥 CRITICAL: About to call distribute_quiz_rewards...")
        
            rewards_distributed = await self.distribute_quiz_rewards(sorted_participants)
            print(f"🔥 CRITICAL: Rewards distributed to {len(rewards_distributed)} users")

        except Exception as e:
            print(f"❌ CRITICAL ERROR in distribute_quiz_rewards: {e}")
            import traceback
            traceback.print_exc()
            rewards_distributed = {}

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
                reward = rewards_distributed.get(str(user.id if user else sorted_participants[i][0]), {})
                gems = reward.get("gems", 0)

                # Calculate accuracy
                user_accuracy = round(data['correct_answers'] / total_questions * 100, 1)

                # Format user mention or name
                if user:
                    user_display = user.mention 
                else:
                    user_display = f"**{data['name']}**"

                top3_text += f"{medal} {user_display}\n"
                top3_text += f"   ⭐ **{data['score']}** points\n"
                top3_text += f"   💎 **{gems} gems** earned\n"
                top3_text += f"   📊 {data['correct_answers']}/{total_questions} correct ({user_accuracy}%)\n\n"

            top3_embed.description = top3_text
            top3_embed.color = colors[0]

            # Set winner's avatar as thumbnail
            if top3_users[0][0] and top3_users[0][0].avatar:
                top3_embed.set_thumbnail(url=top3_users[0][0].avatar.url)

            await self.quiz_channel.send(embed=top3_embed)

        # Wait 2 seconds
        await asyncio.sleep(2)

        # Send FULL LEADERBOARD with pagination if many participants
        if sorted_participants:
            # Create main leaderboard embed
            leaderboard_embed = discord.Embed(
                title="📋 **FINAL LEADERBOARD**",
                description="All participants ranked by score:",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )

            # Split participants into chunks of 15 for readability
            chunk_size = 15
            chunks = [sorted_participants[i:i + chunk_size] 
                     for i in range(0, len(sorted_participants), chunk_size)]

            for chunk_idx, chunk in enumerate(chunks):
                leaderboard_text = ""

                for rank, (user_id, data) in enumerate(chunk, start=chunk_idx * chunk_size + 1):
                    # Get rank emoji
                    rank_emoji = self.get_rank_emoji(rank)

                    # Try to fetch user for avatar in field
                    try:
                        user = await self.bot.fetch_user(int(user_id))
                        user_display = user.display_name
                    except:
                        user_display = data['name']

                    # Calculate user stats
                    user_accuracy = round(data['correct_answers'] / total_questions * 100, 1)
                    avg_time = self.calculate_average_time(data)

                    leaderboard_text += (
                        f"{rank_emoji} **{user_display}**\n"
                        f"   ⭐ {data['score']} pts | 📊 {data['correct_answers']}/{total_questions} ({user_accuracy}%)\n"
                        f"   ⏱️ Avg: {avg_time:.1f}s | 📈 Rank: #{rank}\n"
                    )

                    # Add separator between entries
                    if rank < len(chunk) + chunk_idx * chunk_size:
                        leaderboard_text += "━━━━━━━━━━━━━━━━━━━━\n"

                # Add chunk as a field
                field_name = f"🏆 **Rank {chunk_idx * chunk_size + 1}-{chunk_idx * chunk_size + len(chunk)}**"
                if chunk_idx == 0:
                    field_name = "🏆 **TOP CONTENDERS**"

                leaderboard_embed.add_field(
                    name=field_name,
                    value=leaderboard_text if leaderboard_text else "No participants",
                    inline=False
                )

            # Add footer with quiz completion time
            leaderboard_embed.set_footer(
                text=f"Quiz completed • {total_participants} participants",
                icon_url=self.quiz_channel.guild.icon.url if self.quiz_channel.guild.icon else None
            )

            await self.quiz_channel.send(embed=leaderboard_embed)

        # Send rewards summary
        total_distributed_gems = sum(reward.get("gems", 0) for reward in rewards_distributed.values())
        successful_rewards = sum(1 for reward in rewards_distributed.values() if reward.get("gems", 0) > 0)
    
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
                name="🎁 **Rewards Summary**",
                value=f"**Participants Rewarded:** {successful_rewards}/{len(sorted_participants)}\n"
                      f"**Total Gems Distributed:** {total_distributed_gems} 💎\n"
                      f"**Reward Formula:**\n"
                      f"• Base: 50 gems participation\n"
                      f"• 1st: +500 gems\n"
                      f"• 2nd: +250 gems\n"
                      f"• 3rd: +125 gems\n"
                      f"• Top 10: +75 gems\n"
                      f"• Score bonus: +10 gems per 100 points",
            inline=False
        )

        await self.quiz_channel.send(embed=rewards_embed)

        # Send individual DMs with rewards
        dm_count = 0
        for user_id, data in self.participants.items():
            reward = rewards_distributed.get(user_id, {})
            gems = reward.get("gems", 0)
        
            if gems > 0:
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
                            value=f"💎 **{gems} Gems**",
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
                        dm_count += 1
                        print(f"✅ Sent DM to user {user_id} - {gems} gems")
                    except:
                        print(f"⚠️ Could not send DM to user {user_id}")

        print(f"🔥 CRITICAL: Sent {dm_count} reward DMs")

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
        print(f"🔥 CRITICAL: end_quiz COMPLETED successfully")
        print(f"\n" + "✅"*60)
        print(f"✅✅✅ END_QUIZ COMPLETED SUCCESSFULLY")
        print(f"✅✅✅ All embeds should have been sent")
        print("✅"*60 + "\n")

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
        """Distribute gems based on quiz performance - GUARANTEED WORKING VERSION"""
        print(f"\n" + "="*80)
        print(f"🚀 NUCLEAR DEBUG: distribute_quiz_rewards STARTED")
        print(f"🚀 Participants count: {len(sorted_participants)}")
    
        rewards = {}
    
        if not sorted_participants:
            print(f"⚠️ No participants to reward")
            return rewards
    
        # NUCLEAR DEBUG 1: Check currency system
        print(f"\n🔍 NUCLEAR DEBUG 1: Checking currency system...")
        if not hasattr(self, 'currency'):
            print(f"❌ CRITICAL ERROR: self.currency attribute missing!")
            return rewards
    
        print(f"✅ self.currency exists: {self.currency}")
        print(f"✅ self.currency type: {type(self.currency)}")
    
        # NUCLEAR DEBUG 2: Check if currency methods exist
        required_methods = ['add_gems', 'get_balance']
        for method in required_methods:
            if not hasattr(self.currency, method):
                print(f"❌ CRITICAL ERROR: self.currency.{method} missing!")
                return rewards
            else:
                print(f"✅ self.currency.{method} exists")
    
        # NUCLEAR DEBUG 3: Test database connection
        print(f"\n🔍 NUCLEAR DEBUG 3: Testing database connection...")
        try:
            # Try to get balance of first user to test DB
            test_user_id = str(sorted_participants[0][0])
            test_balance = await self.currency.get_balance(test_user_id)
            print(f"✅ Database test passed: User {test_user_id} has {test_balance['gems']} gems")
        except Exception as e:
            print(f"❌ DATABASE CONNECTION FAILED: {type(e).__name__}: {e}")
            return rewards
    
        # Process each participant
        for rank, (user_id, data) in enumerate(sorted_participants, 1):
            print(f"\n" + "-"*40)
            print(f"🎯 Processing user {user_id} (Rank #{rank})")
            print(f"📊 User data: {data}")
        
            # Calculate rewards
            base_gems = 50  # Participation reward
        
            # Rank bonuses
            if rank == 1:
                base_gems += 500
            elif rank == 2:
                base_gems += 250
            elif rank == 3:
                base_gems += 125
            elif rank <= 10:
                base_gems += 75
        
            # Score bonus
            score_bonus = (data["score"] // 100) * 10
            base_gems += score_bonus
        
            # Perfect score bonus
            max_score = len(self.quiz_questions) * 300
            if data["score"] == max_score:
                base_gems += 250
                reason = f"🎯 Perfect Score! ({data['score']} pts, Rank #{rank})"
            else:
                reason = f"🏆 Quiz Rewards ({data['score']} pts, Rank #{rank})"
        
            # Speed bonus
            speed_bonus = self.calculate_speed_bonus(user_id)
            if speed_bonus:
                base_gems += speed_bonus
                reason += f" + ⚡{speed_bonus} speed bonus"
        
            print(f"💰 Calculated {base_gems} gems for {data['name']}")
            print(f"📝 Reason: {reason}")
        
            # NUCLEAR DEBUG 4: Try to add gems with maximum logging
            print(f"\n🔍 NUCLEAR DEBUG 4: Attempting to add gems...")
            try:
                print(f"📞 Calling: await self.currency.add_gems('{user_id}', {base_gems}, '{reason}')")
            
                # ACTUAL GEM ADDING - This is the critical line
                result = await self.currency.add_gems(
                    user_id=user_id,
                    gems=base_gems,
                    reason=reason
                )
            
                print(f"✅ SUCCESS! add_gems returned: {result}")
            
                if result is None:
                    print(f"❌ WARNING: add_gems returned None (might indicate failure)")
                    rewards[user_id] = {"gems": 0, "rank": rank, "error": "add_gems returned None"}
                elif isinstance(result, dict):
                    print(f"✅ Result type: dict with keys: {list(result.keys())}")
                    if 'balance' in result:
                        print(f"💰 New balance: {result['balance']}")
                
                    rewards[user_id] = {
                        "gems": base_gems,
                        "rank": rank,
                        "result": result
                    }
                
                    # Log to quiz logs
                    try:
                        await self.log_reward(user_id, data["name"], base_gems, rank)
                        print(f"📝 Logged reward successfully")
                    except Exception as log_error:
                        print(f"⚠️ Failed to log reward: {log_error}")
                else:
                    print(f"⚠️ Unexpected result type: {type(result)} - Value: {result}")
                    rewards[user_id] = {"gems": base_gems, "rank": rank, "result": result}
                
            except Exception as e:
                print(f"❌ CRITICAL ERROR in add_gems:")
                print(f"❌ Error type: {type(e).__name__}")
                print(f"❌ Error message: {e}")
                import traceback
                traceback.print_exc()
            
                rewards[user_id] = {
                    "gems": 0,
                    "rank": rank,
                    "error": f"{type(e).__name__}: {str(e)[:100]}"
                }
    
        print(f"\n" + "="*80)
        print(f"🚀 NUCLEAR DEBUG: distribute_quiz_rewards COMPLETED")
        print(f"📊 Final rewards summary:")
        for user_id, reward in rewards.items():
            gems = reward.get("gems", 0)
            if gems > 0:
                print(f"  ✅ {user_id}: {gems} gems")
            else:
                print(f"  ❌ {user_id}: Failed - {reward.get('error', 'Unknown error')}")
        print("="*80)
    
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
    
        # Get user's new balance
        try:
            balance = await self.currency.get_balance(user_id)
            embed.add_field(name="📊 New Balance", value=f"{balance['gems']} gems", inline=True)
        except:
            embed.add_field(name="📊 Status", value="Balance update failed", inline=True)
    
        embed.set_footer(text=f"Quiz completed • {len(self.participants)} participants")
    
        await self.quiz_logs_channel.send(embed=embed)


# === CREATE QUIZ SYSTEM LATER (after database connection) ===
quiz_system = None  # We'll create it in on_ready()

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

@announce_group.command(name="send")
@commands.has_permissions(manage_messages=True)
async def announce_send(ctx, *, message: str):
    """Send an announcement"""
    channel = await announcements.get_announcement_channel(ctx.guild)
    if not channel:
        await ctx.send("❌ No announcement channel found! Use `!!announce channel #channel`")
        return
    
    server_id = str(ctx.guild.id)
    image_url = announcements.announcement_images.get(server_id)
    
    embed = announcements.create_announcement_embed(
        message=message,
        author=ctx.author,
        image_url=image_url
    )
    
    try:
        sent_message = await channel.send("@everyone", embed=embed)
        
        await sent_message.add_reaction("✅")
        
        if server_id in announcements.announcement_images:
            del announcements.announcement_images[server_id]
        
        confirm_embed = discord.Embed(
            description=f"✅ **Announcement Sent!**\n**Channel:** {channel.mention}\n**Link:** [Jump to Message]({sent_message.jump_url})",
            color=discord.Color.green()
        )
        await ctx.send(embed=confirm_embed, delete_after=10)
        await ctx.message.delete(delay=5)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)[:100]}")

@announce_group.command(name="channel")
@commands.has_permissions(administrator=True)
async def announce_channel(ctx, channel: discord.TextChannel):
    """Set the announcement channel"""
    server_id = str(ctx.guild.id)
    announcements.announcement_channels[server_id] = channel.id
    
    embed = discord.Embed(
        description=f"✅ **Announcement channel set to {channel.mention}**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@announce_group.command(name="preview")
@commands.has_permissions(manage_messages=True)
async def announce_preview(ctx, *, message: str):
    """Preview announcement"""
    server_id = str(ctx.guild.id)
    image_url = announcements.announcement_images.get(server_id)
    
    embed = announcements.create_announcement_embed(
        message=message,
        author=ctx.author,
        title="ANNOUNCEMENT PREVIEW",
        color=0x5865F2,
        image_url=image_url
    )
    
    await ctx.send("**📝 Preview:**", embed=embed)
    await ctx.send("*Use `!!announce send` to post.*")

@announce_group.command(name="image")
@commands.has_permissions(manage_messages=True)
async def announce_image(ctx, image_url: str):
    """Set image for next announcement"""
    if not (image_url.startswith("http://") or image_url.startswith("https://")):
        await ctx.send("❌ Please provide a valid image URL")
        return
    
    server_id = str(ctx.guild.id)
    announcements.announcement_images[server_id] = image_url
    
    embed = discord.Embed(
        title="✅ Image Set for Next Announcement",
        color=discord.Color.green()
    )
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)

@announce_group.command(name="urgent")
@commands.has_permissions(manage_messages=True)
async def announce_urgent(ctx, *, message: str):
    """Send urgent announcement (red)"""
    channel = await announcements.get_announcement_channel(ctx.guild)
    if not channel:
        await ctx.send("❌ No announcement channel set!")
        return
    
    embed = announcements.create_announcement_embed(
        message=message,
        author=ctx.author,
        title="🚨 URGENT ANNOUNCEMENT",
        color=0xFF0000,
        image_url=announcements.announcement_images.get(str(ctx.guild.id))
    )
    
    sent_message = await channel.send("@everyone", embed=embed)
    await sent_message.add_reaction("🚨")
    await sent_message.add_reaction("⚠️")
    
    await ctx.send(f"✅ Urgent announcement sent!", delete_after=5)
    await ctx.message.delete(delay=3)

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
    """
    Start a quiz in specific channel
    Usage: !!quiz start #channel  (starts in mentioned channel)
           !!quiz start           (starts in current channel)
    """

    global quiz_system

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

@quiz_group.command(name="stop")
@commands.has_permissions(manage_messages=True)
async def quiz_stop(ctx):
    """Stop current quiz"""

    global quiz_sytem

    if not quiz_system.quiz_running:
        await ctx.send("❌ No quiz is running!", delete_after=5)
        return
    
    quiz_system.quiz_running = False
    if quiz_system.question_timer:
        quiz_system.question_timer.cancel()
    
    await ctx.send("✅ Quiz stopped!")

@quiz_group.command(name="leaderboard")
async def quiz_leaderboard(ctx):
    """Show current quiz leaderboard"""

    global quiz_sytem

    if not quiz_system.participants:
        await ctx.send("❌ No quiz data available!", delete_after=5)
        return
    
    # Create leaderboard embed
    embed = await quiz_system.create_live_leaderboard()
    await ctx.send(embed=embed)

@quiz_group.command(name="addq")
@commands.has_permissions(administrator=True)
async def quiz_addq(ctx, points: int, time_limit: int, *, question_data: str):
    """
    Add a new quiz question
    Format: !!quiz addq 300 60 Question? | correct answer 1 | correct answer 2
    Example: !!quiz addq 300 60 Capital of France? | paris
    """
    try:
        parts = question_data.split(" | ")
        if len(parts) < 2:
            await ctx.send("❌ Format: `Question? | correct answer 1 | correct answer 2`")
            return
        
        new_question = {
            "question": parts[0],
            "correct_answers": [ans.lower().strip() for ans in parts[1:]],
            "points": points,
            "time_limit": time_limit
        }
        
        quiz_system.quiz_questions.append(new_question)
        
        embed = discord.Embed(
            title="✅ **Question Added!**",
            description=new_question["question"],
            color=discord.Color.green()
        )
        
        embed.add_field(name="✅ Correct Answers", 
                       value=", ".join(new_question["correct_answers"]))
        embed.add_field(name="⭐ Points", value=str(points))
        embed.add_field(name="⏱️ Time Limit", value=f"{time_limit}s")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)[:100]}")

# CURRENCY COMMANDS -----
@bot.group(name="currency", invoke_without_command=True)
async def currency_group(ctx):
    """Currency and rewards commands"""
    # Get user balance using SHARED currency system
    user_id = str(ctx.author.id)
    balance = await currency_system.get_balance(user_id)
    
    embed = discord.Embed(
        title="💰 **Your Gems**",
        description=f"**💎 {balance['gems']} gems**\n"
                   f"Total earned: **{balance['total_earned']} gems**",
        color=discord.Color.gold()
    )
    
    # Check daily streak
    user_data = await currency_system.get_user(user_id)
    if user_data["daily_streak"] > 0:
        embed.add_field(
            name="🔥 Daily Streak",
            value=f"{user_data['daily_streak']} days",
            inline=True
        )
    
    # Check next daily
    if await currency_system.can_claim_daily(user_id):
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
    leaderboard = await currency_system.get_leaderboard(limit=10)
    
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
    """Claim daily reward (1-100 gems + streak bonus)"""
    user_id = str(ctx.author.id)
    
    if not await currency_system.can_claim_daily(user_id):
        # Calculate time until next daily
        user = await currency_system.get_user(user_id)
        last_claim = datetime.fromisoformat(user["last_daily"]) if user["last_daily"] else None
        
        if last_claim:
            now = datetime.now(timezone.utc)
            hours_left = 24 - ((now - last_claim).seconds // 3600)
            minutes_left = 60 - ((now - last_claim).seconds % 3600) // 60
            
            await ctx.send(
                f"⏰ You can claim your daily reward in {hours_left}h {minutes_left}m!\n"
                f"Current streak: **{user['daily_streak']} days** 🔥",
                delete_after=10
            )
        else:
            await ctx.send("⚠️ You should be able to claim daily. Try again!")
        return
    
    # Claim daily reward using currency_system
    result = await currency_system.claim_daily(user_id)
    
    embed = discord.Embed(
        title="🎁 **Daily Reward Claimed!**",
        description=f"Here's your daily reward, {ctx.author.mention}!",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="💎 Gems Earned",
        value=f"**+{result['gems']} gems**",
        inline=False
    )
    
    embed.add_field(
        name="🔥 Daily Streak",
        value=f"**{result['streak']} days**",
        inline=True
    )
    
    embed.add_field(
        name="💰 New Balance",
        value=f"**{result['balance']} gems**",
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
    
    balance = await currency_system.get_balance(user_id)
    user_data = await currency_system.get_user(user_id)
    
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
    
    # Recent transactions (last 5)
    if user_data["transactions"]:
        recent = user_data["transactions"][-5:]
        recent_text = []
        for tx in reversed(recent):
            sign = "+" if tx["gems"] > 0 else ""
            reason = tx["reason"][:20] + "..." if len(tx["reason"]) > 20 else tx["reason"]
            recent_text.append(f"`{sign}{tx['gems']}` gems - {reason}")
        
        embed.add_field(
            name="📝 **Recent Activity**",
            value="\n".join(recent_text) if recent_text else "No recent activity",
            inline=False
        )
    
    await ctx.send(embed=embed)

# Update the add command to use PostgreSQL
@bot.command(name="add")
async def add_gems(ctx, amount: int = 100):
    """Add gems to your account"""
    user_id = str(ctx.author.id)
    
    # Use the shared currency system
    result = await currency_system.add_gems(
        user_id=user_id,
        gems=amount,
        reason=f"Command by {ctx.author.name}"
    )
    
    if result:
        balance = await currency_system.get_balance(user_id)
        await ctx.send(f"✅ Added **{amount} gems**\nNew balance: **{balance['gems']} gems**")
    else:
        await ctx.send("❌ Failed to add gems")

@bot.command(name="balance")
async def balance_cmd(ctx):
    """Check your balance"""
    user_id = str(ctx.author.id)
    balance = await currency_system.get_balance(user_id)
    
    embed = discord.Embed(
        title="💰 Your Balance",
        description=f"**💎 {balance['gems']} gems**",
        color=discord.Color.gold()
    )
    
    embed.set_footer(text="Stored in PostgreSQL database")
    await ctx.send(embed=embed)


# --- ANSWER DETECTION ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # GLOBAL DECLARATION
    global quiz_sytem

    quiz = getattr(bot, 'quiz_system', None)
    
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

@bot.command(name="quizdebug")
async def quiz_debug(ctx):
    """Debug quiz participants"""
    if not quiz_system.participants:
        await ctx.send("❌ No quiz participants")
        return
    
    embed = discord.Embed(
        title="🔍 **Quiz Debug**",
        color=discord.Color.orange()
    )
    
    # Show all participants
    participants_info = []
    for user_id, data in quiz_system.participants.items():
        participants_info.append(
            f"**{data['name']}** (ID: {user_id}):\n"
            f"  Score: {data['score']} pts\n"
            f"  Correct: {data['correct_answers']}/{len(quiz_system.quiz_questions)}\n"
            f"  Answers: {len(data['answers'])}"
        )
    
    embed.add_field(
        name="📊 Participants",
        value="\n".join(participants_info),
        inline=False
    )
    
    # Show what rewards would be calculated
    sorted_participants = sorted(
        quiz_system.participants.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )
    
    reward_calc = []
    for rank, (user_id, data) in enumerate(sorted_participants[:5], 1):
        base_gems = 50
        if rank == 1: base_gems += 500
        elif rank == 2: base_gems += 250
        elif rank == 3: base_gems += 125
        elif rank <= 10: base_gems += 75
        
        score_bonus = (data["score"] // 100) * 10
        base_gems += score_bonus
        
        reward_calc.append(
            f"**Rank {rank} ({data['name']})**:\n"
            f"Score: {data['score']} → {base_gems} gems\n"
            f"(50 base + rank bonus + {score_bonus} score bonus)"
        )
    
    if reward_calc:
        embed.add_field(
            name="🧮 Reward Calculation",
            value="\n\n".join(reward_calc),
            inline=False
        )
    
    await ctx.send(embed=embed)


# === EMERGENCY FIX COMMANDS ===
@bot.command(name="emergencyfix")
async def emergency_fix(ctx):
    """Emergency database fix"""
    import subprocess
    
    steps = []
    
    # Step 1: Check asyncpg
    try:
        import asyncpg
        steps.append("✅ asyncpg is installed")
    except:
        steps.append("❌ asyncpg not installed")
        # Try to install it
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "asyncpg"])
            steps.append("✅ Installed asyncpg")
        except:
            steps.append("❌ Failed to install asyncpg")
    
    # Step 2: Check DATABASE_URL
    if DATABASE_URL:
        steps.append(f"✅ DATABASE_URL exists")
        # Show first 50 chars
        masked = DATABASE_URL
        if '@' in DATABASE_URL:
            # Mask password
            parts = DATABASE_URL.split('@')
            if ':' in parts[0]:
                user_part = parts[0].split(':')
                if len(user_part) >= 3:
                    masked = f"{user_part[0]}:****@{parts[1]}"
        steps.append(f"   Format: {masked[:80]}...")
    else:
        steps.append("❌ DATABASE_URL not found")
    
    await ctx.send("**Emergency Fix Report:**\n" + "\n".join(steps))

@bot.command(name="railwayhelp")
async def railway_help(ctx):
    """Step-by-step Railway help"""
    help_text = """
**🎯 STEP-BY-STEP RAILWAY FIX:**

**1. Check Services:**
   - Go to Railway dashboard
   - You should see TWO services:
     • Your Discord bot
     • A PostgreSQL database

**2. If NO PostgreSQL:**
   - Click "New" → "Database" → "PostgreSQL" → "Add"
   - Wait 2 minutes for it to provision

**3. Connect Database to Bot:**
   - Click on your BOT service
   - Go to "Variables" tab
   - Look for `DATABASE_URL`
   - If NOT there, click "New Variable":
     • Name: `DATABASE_URL`
     • Value: Get from PostgreSQL service → "Connect" tab
     • Click "Add"

**4. Restart Everything:**
   - Restart BOTH services
   - Wait 2 minutes
   - Check logs for "✅ Database connected"

**5. Test:**
   - Run `!!testdb` in Discord
   - Should see "✅ Database working!"
    """
    await ctx.send(help_text)

@bot.command(name="quizlink")
async def quiz_link_check(ctx):
    """Check if quiz system is properly linked to PostgreSQL"""
    if quiz_system is None:
        await ctx.send("❌ Quiz system not initialized yet!")
        return
    
    embed = discord.Embed(
        title="🔗 **Quiz System Link Check**",
        color=discord.Color.blue()
    )
    
    # Check database connection
    embed.add_field(
        name="1. Database Connection",
        value=f"Connected: **{db.using_database}**",
        inline=False
    )
    
    # Check currency system
    embed.add_field(
        name="2. Currency System",
        value=f"Type: `{type(currency_system).__name__}`",
        inline=False
    )
    
    # Check quiz system
    embed.add_field(
        name="3. Quiz System",
        value=f"Initialized: **{quiz_system is not None}**",
        inline=False
    )
    
    if quiz_system:
        embed.add_field(
            name="4. Quiz Currency Link",
            value=f"Has currency: **{hasattr(quiz_system, 'currency')}**",
            inline=False
        )
        
        if hasattr(quiz_system, 'currency'):
            # Test if it can actually add gems
            try:
                test_result = await quiz_system.currency.add_gems(
                    user_id=str(ctx.author.id),
                    gems=1,
                    reason="Link test"
                )
                embed.add_field(
                    name="5. Test Transaction",
                    value=f"✅ **SUCCESS!**\nResult: {test_result}",
                    inline=False
                )
            except Exception as e:
                embed.add_field(
                    name="5. Test Transaction",
                    value=f"❌ **FAILED:** {type(e).__name__}: {str(e)[:100]}",
                    inline=False
                )
    
    await ctx.send(embed=embed)

@bot.command(name="nucleartest")
async def nuclear_test(ctx):
    """ULTIMATE test of quiz rewards - bypasses everything"""
    try:
        print(f"\n" + "="*80)
        print(f"💣 NUCLEAR TEST STARTED for {ctx.author.id}")
        
        # Test 1: Check if quiz_system exists
        print(f"\n🔍 Test 1: quiz_system check")
        print(f"   quiz_system: {quiz_system}")
        print(f"   Type: {type(quiz_system)}")
        
        if not quiz_system:
            await ctx.send("❌ quiz_system is None!")
            return
        
        # Test 2: Check currency link
        print(f"\n🔍 Test 2: currency check")
        print(f"   hasattr(quiz_system, 'currency'): {hasattr(quiz_system, 'currency')}")
        
        if hasattr(quiz_system, 'currency'):
            currency = quiz_system.currency
            print(f"   currency object: {currency}")
            print(f"   currency type: {type(currency)}")
            print(f"   Same as currency_system? {currency is currency_system}")
            
            # Test add_gems directly
            print(f"\n🔍 Test 3: Direct add_gems test")
            try:
                print(f"   Calling: await currency.add_gems('{ctx.author.id}', 100, 'Nuclear test')")
                result = await currency.add_gems(
                    user_id=str(ctx.author.id),
                    gems=100,
                    reason="💣 Nuclear test"
                )
                print(f"   Result: {result}")
                
                if result and isinstance(result, dict) and 'balance' in result:
                    print(f"   ✅ SUCCESS! New balance: {result['balance']}")
                    await ctx.send(f"✅ **NUCLEAR TEST PASSED!**\nAdded 100 gems\nNew balance: {result['balance']} gems")
                else:
                    print(f"   ❌ FAILED: Result: {result}")
                    await ctx.send(f"❌ **NUCLEAR TEST FAILED:** add_gems returned: {result}")
                    
            except Exception as e:
                print(f"   ❌ ERROR: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                await ctx.send(f"❌ **NUCLEAR TEST ERROR:** {type(e).__name__}: {str(e)[:200]}")
        else:
            await ctx.send("❌ quiz_system.currency attribute missing!")
            
        print(f"\n" + "="*80)
        
    except Exception as e:
        await ctx.send(f"❌ **NUCLEAR TEST CRASHED:** {type(e).__name__}: {str(e)[:200]}")
        print(f"💥 NUCLEAR TEST CRASHED: {e}")
        import traceback
        traceback.print_exc()


@bot.command(name="manualquizrewards")
@commands.has_permissions(administrator=True)
async def manual_quiz_rewards(ctx, user_id: str, score: int = 500):
    """Manually trigger quiz rewards for testing"""
    try:
        print(f"\n🔧 MANUAL REWARDS TRIGGERED for user {user_id}")
        
        # Simulate quiz participant
        self_participants = {
            user_id: {
                "name": "Test User",
                "score": score,
                "correct_answers": 3,
                "answers": []
            }
        }
        
        # Sort them
        sorted_participants = sorted(
            self_participants.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        # Call distribute_quiz_rewards
        rewards = await quiz_system.distribute_quiz_rewards(sorted_participants)
        
        await ctx.send(f"✅ **Manual rewards triggered!**\nRewards: {rewards}")
        
        # Check balance
        balance = await currency_system.get_balance(user_id)
        await ctx.send(f"💰 **New balance:** {balance['gems']} gems")
        
    except Exception as e:
        await ctx.send(f"❌ **Error:** {type(e).__name__}: {str(e)[:200]}")
        print(f"❌ Manual rewards error: {e}")
        import traceback
        traceback.print_exc()

@bot.command(name="dbtestadd")
async def db_test_add(ctx, user_id: str = None, gems: int = 100):
    """Direct database add_gems test"""
    target_id = user_id or str(ctx.author.id)
    
    try:
        print(f"\n🔍 DB TEST: Direct database test for user {target_id}")
        print(f"🔍 DB TEST: db.using_database = {db.using_database}")
        print(f"🔍 DB TEST: db.pool = {db.pool}")
        
        if not db.using_database:
            await ctx.send("❌ Database not connected")
            return
        
        # Test directly with database
        result = await db.add_gems(
            user_id=target_id,
            gems=gems,
            reason=f"Direct database test by {ctx.author.name}"
        )
        
        await ctx.send(f"✅ **Direct Database Test:**\nAdded {gems} gems\nResult: {result}")
        
        # Verify with get_balance
        balance = await db.get_balance(target_id)
        await ctx.send(f"✅ **Verified Balance:** {balance['gems']} gems")
        
    except Exception as e:
        await ctx.send(f"❌ **Database Error:** {type(e).__name__}: {str(e)[:200]}")
        print(f"❌ DB TEST ERROR: {e}")
        import traceback
        traceback.print_exc()



@bot.command(name="test_question5")
async def test_question5(ctx):
    """Test Question 5 directly"""
    try:
        quiz = bot.quiz_system
        
        if not quiz:
            await ctx.send("❌ No quiz system!")
            return
            
        print(f"\n" + "5️⃣"*60)
        print(f"5️⃣ TESTING QUESTION 5 DIRECTLY")
        
        # Set to Question 5 (index 4)
        quiz.quiz_channel = ctx.channel
        quiz.current_question = 4
        
        print(f"5️⃣ Set current_question to 4")
        print(f"5️⃣ Total questions: {len(quiz.quiz_questions)}")
        
        # Directly call send_question
        print(f"5️⃣ Calling send_question()...")
        await quiz.send_question()
        
        await ctx.send("✅ Testing Question 5. Check console!")
        
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")
        print(f"5️⃣ Test error: {e}")
        import traceback
        traceback.print_exc()


@bot.command(name="quiz_diagnosis")
async def quiz_diagnosis(ctx):
    """Diagnose why quiz rewards aren't working"""
    global quiz_system
    
    print(f"\n" + "🩺"*80)
    print(f"🩺 QUIZ DIAGNOSIS STARTED")
    print(f"🩺 Time: {datetime.now(timezone.utc).strftime('%H:%M:%S')}")
    
    if not quiz_system:
        print(f"❌ CRITICAL: quiz_system is None!")
        await ctx.send("❌ quiz_system is None! Bot may not be fully ready.")
        return
    
    # Check 1: Quiz system state
    print(f"\n🔍 CHECK 1: Quiz System State")
    print(f"  • quiz_system exists: {quiz_system is not None}")
    print(f"  • quiz_running: {quiz_system.quiz_running}")
    print(f"  • current_question: {quiz_system.current_question}")
    print(f"  • total_questions: {len(quiz_system.quiz_questions)}")
    print(f"  • quiz_channel: {quiz_system.quiz_channel}")
    print(f"  • participants: {len(quiz_system.participants)}")
    
    # Check 2: Database connection
    print(f"\n🔍 CHECK 2: Database Connection")
    print(f"  • db.using_database: {db.using_database}")
    print(f"  • currency_system exists: {currency_system is not None}")
    
    # Check 3: Reward system link
    print(f"\n🔍 CHECK 3: Reward System Link")
    print(f"  • quiz_system.currency exists: {hasattr(quiz_system, 'currency')}")
    if hasattr(quiz_system, 'currency'):
        print(f"  • Same as currency_system: {quiz_system.currency is currency_system}")
        print(f"  • Type: {type(quiz_system.currency)}")
    
    # Check 4: Simulate the flow
    print(f"\n🔍 CHECK 4: Flow Simulation")
    print(f"  • If current_question = 0 → after end_question: 1")
    print(f"  • If current_question = 1 → after end_question: 2")
    print(f"  • If current_question = 2 → after end_question: 3")
    print(f"  • If current_question = 3 → after end_question: 4")
    print(f"  • If current_question = 4 → after end_question: 5")
    print(f"  • Should end when: 5 == {len(quiz_system.quiz_questions)}")
    
    # Test direct reward distribution
    print(f"\n🔍 CHECK 5: Direct Reward Test")
    try:
        # Create a test participant
        test_participants = {
            str(ctx.author.id): {
                "name": ctx.author.display_name,
                "score": 500,
                "correct_answers": 5,
                "answers": [],
                "answered_current": False
            }
        }
        
        sorted_test = sorted(test_participants.items(), key=lambda x: x[1]["score"], reverse=True)
        
        print(f"  • Testing distribute_quiz_rewards with 1 participant...")
        rewards = await quiz_system.distribute_quiz_rewards(sorted_test)
        print(f"  • Result: {rewards}")
        
        if rewards and str(ctx.author.id) in rewards:
            print(f"  ✅ Direct reward test PASSED!")
        else:
            print(f"  ❌ Direct reward test FAILED!")
            
    except Exception as e:
        print(f"  ❌ Direct reward test ERROR: {type(e).__name__}: {e}")
    
    print(f"\n🩺 DIAGNOSIS SUMMARY:")
    
    if quiz_system.quiz_running:
        print(f"  ⚠️ There is currently a quiz running!")
        print(f"  ⚠️ Current question: {quiz_system.current_question + 1}/{len(quiz_system.quiz_questions)}")
    
    print(f"  ✅ Database: {'Connected' if db.using_database else 'Not connected'}")
    print(f"  ✅ Currency link: {'OK' if hasattr(quiz_system, 'currency') else 'Missing'}")
    print(f"  ✅ Total questions: {len(quiz_system.quiz_questions)}")
    
    await ctx.send("✅ Quiz diagnosis complete! Check console for detailed report.")
    print("🩺"*80)




@bot.command(name="debug_full_quiz")
async def debug_full_quiz(ctx):
    """Run a debug quiz that logs EVERY step"""
    global quiz_system
    
    try:
        print(f"\n" + "🐛"*80)
        print(f"🐛 DEBUG FULL QUIZ STARTING")
        
        # Reset quiz system
        quiz_system.quiz_running = True
        quiz_system.current_question = 0
        quiz_system.quiz_channel = ctx.channel
        quiz_system.quiz_logs_channel = ctx.channel
        quiz_system.participants = {
            str(ctx.author.id): {
                "name": ctx.author.display_name,
                "score": 0,
                "correct_answers": 0,
                "answers": [],
                "answered_current": False
            }
        }
        
        print(f"🐛 Starting at question 0")
        
        # Manually trigger the full flow
        for expected_end in [1, 2, 3, 4, 5]:
            print(f"\n🐛" + "-"*60)
            print(f"🐛 EXPECTING TO REACH: Question {expected_end}/5")
            print(f"🐛 CURRENT STATE: current_question = {quiz_system.current_question}")
            
            # Send question
            await quiz_system.send_question()
            await asyncio.sleep(2)
            
            # Simulate answer
            quiz_system.participants[str(ctx.author.id)]["score"] += 100
            quiz_system.participants[str(ctx.author.id)]["correct_answers"] += 1
            quiz_system.participants[str(ctx.author.id)]["answered_current"] = True
            
            # End question
            await quiz_system.end_question()
            
            print(f"🐛 AFTER end_question: current_question = {quiz_system.current_question}")
            
            if quiz_system.current_question == 5:
                print(f"🐛✅ REACHED QUESTION 5! Quiz should end now.")
                break
                
            await asyncio.sleep(2)
        
        # If we got here and quiz is still running, something's wrong
        if quiz_system.quiz_running:
            print(f"\n🐛❌ QUIZ DID NOT END AUTOMATICALLY!")
            print(f"🐛❌ current_question: {quiz_system.current_question}")
            print(f"🐛❌ total_questions: {len(quiz_system.quiz_questions)}")
            print(f"🐛❌ Manually calling end_quiz()...")
            await quiz_system.end_quiz()
        
        print(f"\n🐛 DEBUG FULL QUIZ COMPLETE")
        print("🐛"*80)
        
        await ctx.send("✅ Debug quiz complete! Check console for the flow.")
        
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")
        print(f"🐛 Debug error: {e}")
        import traceback
        traceback.print_exc()


@bot.command(name="testendquiz")
async def test_end_quiz(ctx):
    """Test if end_quiz can be called directly"""
    try:
        print(f"\n🧪 Testing end_quiz directly...")
        
        if not quiz_system:
            await ctx.send("❌ quiz_system is None")
            return
        
        # Create dummy participants
        quiz_system.participants = {
            str(ctx.author.id): {
                "name": ctx.author.display_name,
                "score": 500,
                "correct_answers": 3,
                "answers": [],
                "answered_current": False
            }
        }
        
        quiz_system.quiz_channel = ctx.channel
        quiz_system.current_question = 5  # Simulate last question
        
        print(f"🧪 Calling end_quiz()...")
        await quiz_system.end_quiz()
        
        await ctx.send("✅ end_quiz() called successfully! Check logs.")
        
    except Exception as e:
        await ctx.send(f"❌ Error: {type(e).__name__}: {str(e)[:200]}")
        print(f"❌ test_end_quiz error: {e}")
        import traceback
        traceback.print_exc()




# === BOT STARTUP ===
@bot.event
async def on_ready():
    print(f"\n✅ {bot.user} is online!")
    
    # Try to connect to database
    print("\n🔌 Attempting database connection...")
    connected = await db.smart_connect()
    
    if connected:
        print("🎉 DATABASE CONNECTED SUCCESSFULLY!")
        print("✅ Your data will persist across redeploys")
    else:
        print("⚠️ Database connection failed")
    
    # NOW CREATE THE QUIZ SYSTEM AFTER DATABASE IS CONNECTED
    global quiz_system
    quiz_system = QuizSystem(bot)

    bot.quiz_system = quiz_system
    
    # Verify the link
    print(f"\n🔗 SYSTEM LINK VERIFICATION:")
    print(f"  • Database connected: {db.using_database}")
    print(f"  • Currency system exists: {currency_system is not None}")
    print(f"  • Quiz system exists: {quiz_system is not None}")
    if quiz_system:
        print(f"  • Quiz linked to currency: {hasattr(quiz_system, 'currency')}")
        if hasattr(quiz_system, 'currency'):
            print(f"  • Quiz currency is PostgreSQL: {quiz_system.currency is currency_system}")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=""
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