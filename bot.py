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


# LOG TO DISCORD--------------
async def log_to_discord(bot, message, level="INFO", error=None):
    """ALWAYS prints to Railway logs. Best‑effort send to #bot-logs."""
    # --- ALWAYS PRINT TO RAILWAY LOGS (you can see this in Railway dashboard) ---
    print(f"[{level}] {message}")
    if error:
        tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        print(f"TRACEBACK:\n{tb}")

    # --- Best‑effort Discord send – NEVER RAISES ---
    try:
        for guild in bot.guilds:
            channel = discord.utils.get(guild.text_channels, name="bot-logs")
            if channel:
                embed = discord.Embed(
                    title=f"📋 Quiz Log – {level}",
                    description=message[:2000],
                    color=discord.Color.green() if level == "INFO" else discord.Color.red(),
                    timestamp=datetime.now(timezone.utc)
                )
                if error:
                    embed.add_field(name="Traceback", value=f"```py\n{tb[-1000:]}\n```", inline=False)
                await channel.send(embed=embed)
                return
    except Exception as e:
        print(f"⚠️ Failed to send log to Discord: {e}")  # still visible in Railway logs

# END LOG TO DC CODE-----------


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
            
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
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
                            RETURNING gems
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
                            RETURNING gems
                        ''', user_id, gems)
                        new_balance = gems

                    # Record transaction
                    await conn.execute('''
                        INSERT INTO user_transactions (user_id, type, gems, reason, balance_after)
                        VALUES ($1, 'reward', $2, $3, $4)
                    ''', user_id, gems, reason, new_balance)

                    print(f"✅ [DB] Added {gems} gems to {user_id} (Balance: {new_balance}) Reason: {reason}")
                    return {"gems": gems, "balance": new_balance}

        except Exception as e:
            print(f"❌ Database error in add_gems: {e}")
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
                        if last_claim.tzinfo is None:
                            last_claim = last_claim.replace(tzinfo=timezone.utc)
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
    
    def create_announcement_embed(self, message, author, title="", color=0xFF5500, image_url=None):
        """Create a beautiful announcement embed"""
        embed = discord.Embed(
            title=f"{title}",
            description=message,
            color=color,
            
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

# REPLY TO MESSAGES COMMAND
@bot.command(name="reply")
@commands.has_permissions(administrator=True)
async def reply_message(
    ctx,
    channel: discord.TextChannel,
    message_id: int,
    *,
    reply_text: str
):
    try:
        # Fetch the target message
        target_message = await channel.fetch_message(message_id)

        # Reply to that message
        await target_message.reply(reply_text)

        await ctx.message.add_reaction("✅")

    except discord.NotFound:
        await ctx.send("❌ Message not found.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to read or send messages there.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")
# END -----

# FOR DISCORD LOG----------------
async def log_to_discord(bot, message, level="INFO"):
    """Send a log message to #bot-logs channel."""
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name="bot-logs")
        if channel:
            try:
                embed = discord.Embed(
                    title=f"📋 Quiz Log – {level}",
                    description=message[:2000],
                    color=discord.Color.green() if level == "INFO" else discord.Color.red(),
                    timestamp=datetime.now(timezone.utc)
                )
                await channel.send(embed=embed)
                return
            except:
                pass
    print(f"[{level}] {message}")  # fallback


# END ---=====-=-=-=------

class QuizSystem:
    def __init__(self, bot):
        self.bot = bot
        self.currency = currency_system
        self.quiz_questions = []
        self.current_question = 0
        self.participants = {}
        self.quiz_channel = None
        self.quiz_logs_channel = None
        self.quiz_running = False
        self.question_start_time = None
        self._ending = False
        self.load_questions()

        # Countdown loop – will be started per question
        self.countdown_loop = None

    # ------------------------------------------------------------
    # QUESTION LOADING
    # ------------------------------------------------------------
    def load_questions(self):
        self.quiz_questions = [
            {"q": "What is the capital city of France?",          "a": ["paris"],             "pts": 300, "time": 30},
            {"q": "Which planet is known as the Red Planet?",     "a": ["mars", "planet mars"], "pts": 300, "time": 30},
            {"q": "What is the chemical symbol for gold?",        "a": ["au"],                "pts": 200, "time": 30},
            {"q": "Who painted the Mona Lisa?",                  "a": ["leonardo da vinci", "da vinci", "leonardo"], "pts": 300, "time": 30},
            {"q": "What is the largest mammal in the world?",     "a": ["blue whale", "whale"], "pts": 300, "time": 30},
        ]

    # ------------------------------------------------------------
    # POINTS & UTILITIES
    # ------------------------------------------------------------
    def calculate_points(self, answer_time, total_time, max_points):
        time_left = total_time - answer_time
        if time_left <= 0:
            return 0
        return int(max_points * (time_left / total_time))

    def calculate_average_time(self, user_data):
        correct_times = [a['time'] for a in user_data['answers'] if a['correct']]
        return sum(correct_times) / len(correct_times) if correct_times else 0

    def get_rank_emoji(self, rank):
        rank_emojis = {
            1: "🥇", 2: "🥈", 3: "🥉", 4: "4️⃣", 5: "5️⃣",
            6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
        }
        return rank_emojis.get(rank, f"{rank}.")

    # ------------------------------------------------------------
    # QUIZ LIFECYCLE
    # ------------------------------------------------------------
    async def start_quiz(self, channel, logs_channel):
        try:
            self.quiz_channel = channel
            self.quiz_logs_channel = logs_channel
            self.quiz_running = True
            self.current_question = 0
            self.participants = {}
            self.question_start_time = None
            self._ending = False
            random.shuffle(self.quiz_questions)

            embed = discord.Embed(
                title="🎯 **Quiz Time!**",
                description=(
                    "```\n"
                    "• Type your answer in chat\n"
                    "• Correct spelling only!\n"
                    "• Faster answers = more points\n"
                    "• Multiple attempts allowed\n"
                "```\n"
                    f"**First question starts in** ⏰ **10 seconds**"
                ),
                color=0xFFD700  # Gold
            )
            embed.set_footer(text="Good luck! 🍀", icon_url=self.bot.user.display_avatar.url)

            start_msg = await channel.send(embed=embed)
            for i in range(10, 0, -1):
                await start_msg.edit(content=f"⏰ **{i}...**")
                await asyncio.sleep(1)
            await start_msg.delete()
            await self.send_question()
            await log_to_discord(self.bot, "✅ Quiz started", "INFO")
        except Exception as e:
            await log_to_discord(self.bot, "❌ start_quiz failed", "ERROR", e)

    async def send_question(self):
        try:
            if self.current_question >= len(self.quiz_questions):
                await self.end_quiz()
                return

            q = self.quiz_questions[self.current_question]
            self.question_start_time = datetime.now(timezone.utc)

            embed = discord.Embed(
                title=f"❓ **QUESTION{self.current_question+1}/{len(self.quiz_questions)}**",
                description=q["q"],
                color=discord.Color.blue()
            )
            embed.add_field(
                name=f"⏰ **{q['time']:02d} SECONDS LEFT**",
                value=f"```\n{'🟩'*20}\n{q['time']:02d} seconds\n```\n**Max Points:** {q['pts']} ⭐",
                inline=False
            )
            embed.set_footer(text="Multiple attempts allowed")
            self.question_message = await self.quiz_channel.send(embed=embed)

            # --- START COUNTDOWN LOOP (live bar update) ---
            if self.countdown_loop:
                self.countdown_loop.cancel()
            self.countdown_loop = self.bot.loop.create_task(self._run_countdown(q['time']))

            # --- START QUESTION TIMER (calls end_question after time_limit) ---
            self.bot.loop.call_later(q['time'], lambda: asyncio.create_task(self._timer_expired()))
            await log_to_discord(self.bot, f"⏲️ Timer set for {q['time']}s (question {self.current_question+1})", "INFO")

        except Exception as e:
            await log_to_discord(self.bot, "❌ send_question failed", "ERROR", e)

    async def _timer_expired(self):
        """Called when the question time limit is reached."""
        await log_to_discord(self.bot, f"⏰ Timer expired for question {self.current_question+1}", "INFO")
        await self.end_question()

    async def _run_countdown(self, total_time):
        """Live countdown bar update (runs every second)."""
        while self.quiz_running and self.question_start_time:
            elapsed = (datetime.now(timezone.utc) - self.question_start_time).seconds
            time_left = total_time - elapsed
            if time_left <= 0:
                break
            try:
                embed = self.question_message.embeds[0]
                progress = int((time_left / total_time) * 20)
                bar = "🟩" * progress + "⬜" * (20 - progress)

                for i, field in enumerate(embed.fields):
                    if "⏰" in field.name:
                        embed.set_field_at(
                            i,
                            name=f"⏰ **{time_left:02d} SECONDS LEFT**",
                            value=f"```\n{bar}\n{time_left:02d} seconds\n```\n**Max Points:** {self.quiz_questions[self.current_question]['pts']} ⭐",
                            inline=False
                        )
                        break

                embed.color = discord.Color.red() if time_left <= 10 else discord.Color.orange() if time_left <= 30 else discord.Color.blue()
                await self.question_message.edit(embed=embed)
            except Exception as e:
                await log_to_discord(self.bot, "⚠️ Countdown error (non-fatal)", "WARN", e)
            await asyncio.sleep(1)

    # ------------------------------------------------------------
    # ANSWER PROCESSING
    # ------------------------------------------------------------
    async def process_answer(self, user, answer_text):
        try:
            if not self.quiz_running:
                return False
            if self.question_start_time is None:
                return False
            if self.current_question >= len(self.quiz_questions):
                return False

            q = self.quiz_questions[self.current_question]
            answer_time = (datetime.now(timezone.utc) - self.question_start_time).seconds
            if answer_time > q['time']:
                return False

            uid = str(user.id)
            if uid not in self.participants:
                self.participants[uid] = {
                    "name": user.display_name,
                    "score": 0,
                    "answers": [],
                    "correct_answers": 0,
                    "answered_current": False
                }

            if self.participants[uid]["answered_current"]:
                return False

            user_ans = answer_text.lower().strip()
            is_correct = user_ans in [a.lower() for a in q['a']]

            points = 0
            if is_correct:
                points = self.calculate_points(answer_time, q['time'], q['pts'])
                self.participants[uid]["score"] += points
                self.participants[uid]["correct_answers"] += 1
                self.participants[uid]["answered_current"] = True

            self.participants[uid]["answers"].append({
                "question": self.current_question,
                "answer": answer_text,
                "correct": is_correct,
                "points": points,
                "time": answer_time
            })

            if is_correct:
                await self.log_answer(user, q['q'], answer_text, points, answer_time)

            return True
        except Exception as e:
            await log_to_discord(self.bot, f"❌ process_answer error for {user.id}", "ERROR", e)
            return False

    async def log_answer(self, user, question, answer, points, time):
        if not self.quiz_logs_channel:
            return
        try:
            embed = discord.Embed(title="✅ Correct Answer", color=discord.Color.green())
            embed.add_field(name="👤 User", value=user.mention, inline=True)
            embed.add_field(name="📋 Question", value=question[:100], inline=False)
            embed.add_field(name="✏️ Answer", value=answer[:50], inline=True)
            embed.add_field(name="⭐ Points", value=str(points), inline=True)
            embed.add_field(name="⏱️ Time", value=f"{time}s", inline=True)
            embed.add_field(name="Q#", value=str(self.current_question+1), inline=True)
            await self.quiz_logs_channel.send(embed=embed)
        except Exception as e:
            await log_to_discord(self.bot, "⚠️ log_answer failed", "WARN", e)

    # ------------------------------------------------------------
    # END QUESTION / TRANSITION
    # ------------------------------------------------------------
    async def end_question(self):
        """End current question, show stats, and move to next or end quiz."""
        await log_to_discord(self.bot, f"🔚 end_question() called for Q{self.current_question+1}", "INFO")
        try:
            if self.countdown_loop:
                self.countdown_loop.cancel()
            self.question_start_time = None

            q = self.quiz_questions[self.current_question]
            correct = ", ".join([a.capitalize() for a in q['a']])

            embed = discord.Embed(
                title=f"✅ Question {self.current_question+1}/{len(self.quiz_questions)} Complete",
                description=f"**Correct answer(s):** {correct}",
                color=discord.Color.green()
            )

            total_p = len(self.participants)
            total_ans = len([p for p in self.participants.values() if any(a["question"] == self.current_question for a in p["answers"])])
            correct_cnt = len([p for p in self.participants.values() if p.get("answered_current", False)])

            fastest = None
            fastest_name = None
            for uid, data in self.participants.items():
                for ans in data["answers"]:
                    if ans["question"] == self.current_question and ans["correct"]:
                        if fastest is None or ans["time"] < fastest:
                            fastest = ans["time"]
                            fastest_name = data["name"]

            embed.add_field(
                name="📊 Statistics",
                value=f"**Participants:** {total_p}\n**Attempted:** {total_ans}\n"
                      f"**Accuracy:** {round(correct_cnt/total_ans*100,1) if total_ans else 0}%\n"
                      + (f"**Fastest:** {fastest_name} ({fastest}s)" if fastest_name else ""),
                inline=False
            )
            await self.quiz_channel.send(embed=embed)
            await asyncio.sleep(3)

            # LAST QUESTION?
            if self.current_question + 1 == len(self.quiz_questions):
                await log_to_discord(self.bot, "🏁 Last question finished, calling end_quiz()", "INFO")
                await self.end_quiz()
                return

            # NOT LAST: show leaderboard + countdown
            lb_embed = await self.create_leaderboard()
            lb_msg = await self.quiz_channel.send(embed=lb_embed)

            for i in range(5, 0, -1):
                updated = await self.create_leaderboard(countdown=i)
                await lb_msg.edit(embed=updated)
                await asyncio.sleep(1)
            await lb_msg.delete()

            # Reset for next question
            for uid in self.participants:
                self.participants[uid]["answered_current"] = False

            self.current_question += 1
            await self.send_question()
        except Exception as e:
            await log_to_discord(self.bot, "❌ end_question crashed – forcing end_quiz", "CRITICAL", e)
            await self.end_quiz()

    async def create_leaderboard(self, countdown=None):
        try:
            if not self.participants:
                return discord.Embed(title="📊 Leaderboard", description="No participants yet!", color=discord.Color.blue())

            sorted_p = sorted(self.participants.items(), key=lambda x: x[1]["score"], reverse=True)
            embed = discord.Embed(title="📊 LEADERBOARD", color=discord.Color.gold())
            if countdown:
                embed.description = f"**Next question in:** {countdown}s"

            lines = []
            for i, (uid, data) in enumerate(sorted_p):
                status = "⏳ N/A"
                attempts = [a for a in data["answers"] if a["question"] == self.current_question]
                if attempts:
                    last = attempts[-1]
                    if last["correct"]:
                        status = f"✅ +{last['points']} pts ({last['time']}s)"
                    else:
                        status = f"❌ Wrong ({len(attempts)} attempt{'s' if len(attempts)>1 else ''})"

                medal = self.get_rank_emoji(i+1) if i < 10 else f"{i+1}."
                lines.append(f"{medal} **{data['name']}** – {data['score']} pts\n   {status}")

            embed.add_field(name="🏆 Rankings", value="\n".join(lines[:10]), inline=False)
            return embed
        except Exception as e:
            await log_to_discord(self.bot, "❌ create_leaderboard failed", "ERROR", e)
            return discord.Embed(title="⚠️ Leaderboard Error", color=discord.Color.red())

    # ------------------------------------------------------------
    # REWARD DISTRIBUTION
    # ------------------------------------------------------------
    async def distribute_quiz_rewards(self, sorted_participants):
        rewards = {}
        for rank, (uid, data) in enumerate(sorted_participants, 1):
            try:
                base = 50  # participation
                if rank == 1: base += 500
                elif rank == 2: base += 250
                elif rank == 3: base += 125
                elif rank <= 10: base += 75

                base += (data["score"] // 100) * 10          # score bonus
                base += self.calculate_speed_bonus(uid)      # speed bonus

                max_score = len(self.quiz_questions) * 300
                if data["score"] == max_score:
                    base += 250
                    reason = f"🎯 Perfect Score! ({data['score']} pts, Rank #{rank})"
                else:
                    reason = f"🏆 Quiz Rewards ({data['score']} pts, Rank #{rank})"

                # --- ADD GEMS TO DATABASE ---
                result = await self.currency.add_gems(uid, base, reason)
                rewards[uid] = {"gems": base, "rank": rank, "result": result}

                await log_to_discord(self.bot, f"✅ +{base} gems to {data['name']} (Rank #{rank})", "INFO")

                try:
                    await self.log_reward(uid, data['name'], base, rank)
                except Exception as e:
                    await log_to_discord(self.bot, f"⚠️ log_reward failed for {uid}", "WARN", e)

            except Exception as e:
                await log_to_discord(self.bot, f"❌ Failed to add gems to {uid}", "ERROR", e)
                rewards[uid] = {"gems": 0, "rank": rank, "error": str(e)}

        await log_to_discord(self.bot, f"✅ Reward distribution complete. Total entries: {len(rewards)}", "INFO")
        return rewards

    def calculate_speed_bonus(self, user_id):
        if user_id not in self.participants:
            return 0
        bonus = 0
        for ans in self.participants[user_id]["answers"]:
            if ans["correct"] and ans["time"] < 10:
                bonus += max(1, 10 - ans["time"])
        return min(bonus, 50)

    async def log_reward(self, user_id, username, gems, rank):
        if not self.quiz_logs_channel:
            return
        embed = discord.Embed(title="💰 Gems Distributed", color=discord.Color.gold())
        embed.add_field(name="👤 User", value=username, inline=True)
        embed.add_field(name="🏆 Rank", value=f"#{rank}", inline=True)
        embed.add_field(name="💎 Gems", value=f"+{gems}", inline=True)
        await self.quiz_logs_channel.send(embed=embed)

    # ------------------------------------------------------------
    # END QUIZ – FULLY LOGGED
    # ------------------------------------------------------------
    async def end_quiz(self):
        if self._ending:
            await log_to_discord(self.bot, "⚠️ end_quiz already in progress, ignoring", "WARN")
            return
        self._ending = True

        try:
            await log_to_discord(self.bot, f"🚨 end_quiz() CALLED. Participants: {len(self.participants)}", "INFO")

            if not self.quiz_running:
                await log_to_discord(self.bot, "⚠️ Quiz already stopped, aborting end_quiz", "WARN")
                return

            self.quiz_running = False
            self.question_start_time = None
            if self.countdown_loop:
                self.countdown_loop.cancel()

            # --- 1. SHOW FINISHED MESSAGE ---
            try:
                finish = discord.Embed(
                    title="🏆 **QUIZ FINISHED!** 🏆",
                    description="Calculating final scores and rewards...",
                    color=discord.Color.gold()
                )
                await self.quiz_channel.send(embed=finish)
                await asyncio.sleep(2)
            except Exception as e:
                await log_to_discord(self.bot, "⚠️ Failed to send finish embed", "WARN", e)

            # --- 2. CHECK PARTICIPANTS ---
            if not self.participants:
                await self.quiz_channel.send("❌ No participants – no rewards.")
                await log_to_discord(self.bot, "No participants, skipping rewards", "WARN")
                return

            # --- 3. SORT & VALIDATE ---
            sorted_p = sorted(self.participants.items(), key=lambda x: x[1]["score"], reverse=True)
            for _, p in sorted_p:
                p.setdefault("correct_answers", 0)
                p.setdefault("answers", [])
                p.setdefault("score", 0)

            # --- 4. DISTRIBUTE REWARDS ---
            rewards = await self.distribute_quiz_rewards(sorted_p)
            await log_to_discord(self.bot, f"✅ distribute_quiz_rewards returned {len(rewards)} entries", "INFO")

            # --- 5. BUILD FINAL LEADERBOARD ---
            try:
                lb_embed = discord.Embed(title="📊 **FINAL LEADERBOARD**", color=discord.Color.green())

                total_q = len(self.quiz_questions)
                total_correct = sum(p["correct_answers"] for _, p in sorted_p)
                total_attempts = sum(len(p["answers"]) for _, p in sorted_p)
                accuracy = round(total_correct / total_attempts * 100, 1) if total_attempts else 0

                lb_embed.add_field(
                    name="📈 Quiz Statistics",
                    value=f"**Participants:** {len(sorted_p)}\n**Questions:** {total_q}\n**Accuracy:** {accuracy}%",
                    inline=False
                )

                # TOP 10 WITH REWARDS
                top_entries = []
                for i, (uid, data) in enumerate(sorted_p[:10], 1):
                    gems = rewards.get(uid, {}).get("gems", 0)
                    medal = self.get_rank_emoji(i)
                    top_entries.append(f"{medal} **{data['name']}** – {data['score']} pts  💎 +{gems} gems")

                if top_entries:
                    lb_embed.add_field(name="🏆 TOP 10 WINNERS", value="\n".join(top_entries), inline=False)

                if len(sorted_p) > 10:
                    lb_embed.add_field(name="🎁 All Participants", value=f"All {len(sorted_p)} received rewards!\nCheck DMs.", inline=False)

                await self.quiz_channel.send(embed=lb_embed)
                await log_to_discord(self.bot, "✅ Final leaderboard sent", "INFO")
                await asyncio.sleep(2)
            except Exception as e:
                await log_to_discord(self.bot, "❌ Failed to send leaderboard", "ERROR", e)

            # --- 6. REWARDS SUMMARY ---
            try:
                summary = discord.Embed(title="💰 Quiz Rewards Distribute!", color=discord.Color.gold())
                successful = sum(1 for r in rewards.values() if r.get("gems", 0) > 0)
                summary.add_field(name="Distribution count", value=f"**Successful:** {successful}/{len(sorted_p)}", inline=False)
                await self.quiz_channel.send(embed=summary)
                await log_to_discord(self.bot, "✅ Rewards summary sent", "INFO")
            except Exception as e:
                await log_to_discord(self.bot, "⚠️ Failed to send rewards summary", "WARN", e)

            # --- 7. SEND DMs ---
            dm_count = 0
            for uid, data in self.participants.items():
                reward = rewards.get(uid, {})
                if reward and reward.get("gems", 0) > 0:
                    try:
                        user = self.bot.get_user(int(uid))
                        if user:
                            balance = await self.currency.get_balance(uid)
                            dm = discord.Embed(
                                title="🎉 Quiz Rewards!",
                                description=f"**Final Score:** {data['score']} pts\n**Rank:** #{list(self.participants.keys()).index(uid)+1}",
                                color=discord.Color.gold()
                            )
                            dm.add_field(name="*Rewards*", value=f"💎 +{reward['gems']} Gems", inline=False)
                            dm.add_field(name="*New Balance*", value=f"💎 {balance['gems']} Gems", inline=False)
                            await user.send(embed=dm)
                            dm_count += 1
                    except Exception as e:
                        await log_to_discord(self.bot, f"❌ DM failed for {uid}", "WARN", e)

            await log_to_discord(self.bot, f"📨 DMs sent: {dm_count}/{len(self.participants)}", "INFO")

        except Exception as e:
            await log_to_discord(self.bot, "❌❌❌ end_quiz CRITICAL FAILURE", "CRITICAL", e)
            try:
                await self.quiz_channel.send("⚠️ An error occurred while finalizing the quiz. Check bot-logs.")
            except:
                pass
        finally:
            # --- ALWAYS RESET ---
            self.quiz_channel = None
            self.quiz_logs_channel = None
            self.current_question = 0
            self.participants = {}
            self.question_start_time = None
            self.quiz_running = False
            self.countdown_loop = None
            self._ending = False
            await log_to_discord(self.bot, "✅ Quiz system reset complete", "INFO")

# === END CREATE QUIZ SYSTEM WITH SHARED CURRENCY ===
quiz_system = QuizSystem(bot)


# HELPER FUNCTION FOR ADDING GEMS 

async def send_gem_notification(user, admin, amount, new_balance):
    """Send a DM notification to a user when gems are added to their account
    
    Returns:
        bool: True if DM was sent successfully, False otherwise
    """
    try:
        # Don't send DM if the user is the admin (they already see the channel message)
        if user.id == admin.id:
            return True  # Return True since we don't need to send a DM
        
        embed = discord.Embed(
            title="🎁 **You've received Gems!**",
            description=f"**{admin.name}** has added gems to your account.",
            color=discord.Color.gold(),
            
        )
        
        embed.add_field(name="💎 Amount Added", value=f"**+{amount} gems**", inline=True)
        embed.add_field(name="💰 New Balance", value=f"**{new_balance} gems**", inline=True)
        
        embed.set_footer(text="Thank you for joining the server!")
        
        # Try to send DM
        await user.send(embed=embed)
        print(f"✅ Sent DM notification to {user.name} ({user.id}) for +{amount} gems")
        return True
        
    except discord.Forbidden:
        # User has DMs disabled or blocked the bot
        print(f"⚠️ Could not send DM to {user.name} - DMs disabled or blocked")
        return False
    except Exception as e:
        print(f"❌ Error sending DM to {user.name}: {e}")
        return False


# QUIZ DIAGNOSTICS---------
@bot.command(name="quiz_diagnostic")
@commands.has_permissions(administrator=True)
async def quiz_diagnostic(ctx):
    """Test logging and reward system."""
    await log_to_discord(bot, "🧪 Diagnostic: log_to_discord works!", "INFO")
    
    # Test currency.add_gems
    try:
        result = await currency_system.add_gems(str(ctx.author.id), 1, "🧪 Diagnostic test")
        await ctx.send(f"✅ Currency system works! Added 1 gem. New balance: {result['balance']}")
    except Exception as e:
        await ctx.send(f"❌ Currency system FAILED: {e}")
        await log_to_discord(bot, "❌ Diagnostic: currency.add_gems failed", "ERROR", e)
# END QUIZ DIAG---------

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
    # check for exact command match
    message_content = ctx.message.content.strip().lower()

    # only process exact !!currency or !!balance
    if not (message_content == "!!currency" or message_content == "!!balance"):
        return


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
@commands.has_permissions(administrator=True)
async def add_gems(ctx, member: discord.Member = None, amount: int = 100):
    """Add gems to a user's account (Admin only)
    
    Usage:
        !!add @Username 500    - Add 500 gems to mentioned user
        !!add @Username        - Add 100 gems (default) to mentioned user
        !!add 500              - Add 500 gems to yourself (admin only)
    """

    # Validate amount
    if amount <= 0:
        await ctx.send("❌ Amount must be positive!")
        return

    # Optional: Set maximum limit
    MAX_ADD_LIMIT = 10000
    if amount > MAX_ADD_LIMIT:
        await ctx.send(f"❌ Maximum gems per addition is {MAX_ADD_LIMIT}!")
        return

    # If no member mentioned, default to the command user
    if member is None:
        member = ctx.author

    user_id = str(member.id)

    try:
        # Use the shared currency system
        result = await currency_system.add_gems(
            user_id=user_id,
            gems=amount,
            reason=f"Admin addition by {ctx.author.name}"
        )

        if result:
            # Get updated balance
            balance = await currency_system.get_balance(user_id)
            
            # ✅ SEND DM NOTIFICATION TO THE USER
            dm_sent = False
            if member != ctx.author:
                dm_sent = await send_gem_notification(member, ctx.author, amount, balance['gems'])
            else:
                dm_sent = True  # No need to send DM if adding to self

            embed = discord.Embed(
                title="✅ **Gems Added Successfully**",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )

            # Different message if adding to self vs others
            if member == ctx.author:
                embed.description = f"Added gems to your account"
            else:
                embed.description = f"Added gems to {member.mention}'s account"
                
                # Add DM notification status
                if dm_sent:
                    embed.add_field(name="📨 Notification", value="✅ DM sent to user", inline=True)
                else:
                    embed.add_field(name="📨 Notification", value="⚠️ Could not send DM (user has DMs disabled)", inline=True)

            embed.add_field(name="💎 Amount Added", value=f"**+{amount} gems**", inline=True)
            embed.add_field(name="💰 New Balance", value=f"**{balance['gems']} gems**", inline=True)
            embed.add_field(name="👤 Added By", value=ctx.author.mention, inline=True)

            # Add transaction ID if available
            if isinstance(result, dict) and 'transaction_id' in result:
                embed.set_footer(text=f"Transaction ID: {result['transaction_id']}")
            else:
                embed.set_footer(text="Administrator Action")

            await ctx.send(embed=embed)
        else:
            error_embed = discord.Embed(
                title="❌ Failed to Add Gems",
                description="The currency system returned an error.",
                color=discord.Color.red()
            )
            await ctx.send(embed=error_embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error Adding Gems",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)


@add_gems.error
async def add_gems_error(ctx, error):
    """Handle errors for the add command"""
    if isinstance(error, commands.MissingPermissions):
        # Send ephemeral message (only visible to command user)
        try:
            await ctx.send(
                "❌ **Permission Denied:** This command is for administrators only!",
                delete_after=10
            )
        except:
            pass
    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ **Invalid arguments!** Usage:\n"
            "• `!!add @Username 500` - Add 500 gems to mentioned user\n"
            "• `!!add @Username` - Add 100 gems (default)\n"
            "• `!!add 500` - Add 500 gems to yourself (admin only)",
            delete_after=10
        )
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "❌ **Missing arguments!** Usage:\n"
            "• `!!add @Username 500` - Add gems to user\n"
            "• `!!add 500` - Add gems to yourself\n",
            delete_after=10
        )
    else:
        # Log unexpected errors
        print(f"Error in add command: {error}")
        await ctx.send(
            "❌ An unexpected error occurred. Please try again.",
            delete_after=5
        )





@bot.command(name="balance")
async def balance_cmd(ctx):
    """Check your balance"""
    # check for exact command match
    message_content = ctx.message.content.strip().lower()

    # only process exact !!balance command without extra text
    if message_content != "!!balance":
        return


    user_id = str(ctx.author.id)
    balance = await currency_system.get_balance(user_id)
    
    embed = discord.Embed(
        title="💰 Your Balance",
        description=f"**💎 {balance['gems']} gems**",
        color=discord.Color.gold()
    )
    
    embed.set_footer(text="")
    await ctx.send(embed=embed)


# --- ANSWER DETECTION ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Quiz answers
    if quiz_system.quiz_running and message.channel == quiz_system.quiz_channel:
        try:
            await quiz_system.process_answer(message.author, message.content)
        except Exception as e:
            await log_to_discord(bot, f"❌ Error in on_message: {e}", "ERROR")

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
        print("⚠️ Using JSON fallback storage")
        print("❌ Data may reset on redeploy")
    
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
