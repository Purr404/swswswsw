import os
import sys
import json
import asyncio
import random
from datetime import datetime, timezone, timedelta
import traceback   # used in log_to_discord
import aiohttp
import io
import textwrap

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
print("discord.py version:", discord.__version__)
print("discord.__file__:", discord.__file__)
print("discord.ui dir:", dir(discord.ui))
print("Has TextInput?", hasattr(discord.ui, 'TextInput'))
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
bot.active_bags = {}
bot.db_pool = None


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
                bot.db_pool = self.pool   #  FORTUNE BAG POOL

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

                    # FORTUNE BAG TABLES
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS fortune_bags (
                        message_id BIGINT PRIMARY KEY,
                        channel_id BIGINT NOT NULL,
                        remaining INTEGER NOT NULL,
                        total INTEGER NOT NULL DEFAULT 1000,
                        dropper_id BIGINT NOT NULL,
                        active BOOLEAN NOT NULL DEFAULT TRUE
                        )
                    ''')

                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS fortune_bag_participants (
                        message_id BIGINT REFERENCES fortune_bags(message_id) ON DELETE CASCADE,
                       user_id BIGINT NOT NULL,
                       earned INTEGER NOT NULL,
                       PRIMARY KEY (message_id, user_id)
                        )
                    ''')
                    # ========== SHOP SYSTEM TABLES ==========
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS shop_items (
                            item_id SERIAL PRIMARY KEY,
                            name TEXT NOT NULL,
                            description TEXT,
                            price INTEGER NOT NULL CHECK (price > 0),
                            type TEXT NOT NULL CHECK (type IN ('role', 'color')),
                            role_id BIGINT,
                            color_hex TEXT,
                            created_at TIMESTAMP DEFAULT NOW(),
                            updated_at TIMESTAMP DEFAULT NOW()
                        )
                    ''')
                    # Add guild_id column if not exists (for role removal on expiration)
                    await conn.execute('ALTER TABLE shop_items ADD COLUMN IF NOT EXISTS guild_id BIGINT')

                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS user_purchases (
                            purchase_id SERIAL PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            item_id INTEGER REFERENCES shop_items(item_id) ON DELETE CASCADE,
                            price_paid INTEGER NOT NULL,
                            purchased_at TIMESTAMP DEFAULT NOW()
                        )
                    ''')

                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS shop_messages (
                            guild_id BIGINT PRIMARY KEY,
                            channel_id BIGINT NOT NULL,
                            message_id BIGINT NOT NULL
                        )
                    ''')
                    # Create carriage_bookings table
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS carriage_bookings (
                            booking_id SERIAL PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            ign TEXT NOT NULL,
                            ride_time TIMESTAMP NOT NULL,
                            booked_at TIMESTAMP DEFAULT NOW(),
                            purchase_id INTEGER REFERENCES user_purchases(purchase_id) ON DELETE CASCADE
                        )
                    ''')
                    
                    await conn.execute('''
                         CREATE TABLE IF NOT EXISTS weapon_types (
                             type_id SERIAL PRIMARY KEY,
                             name_base TEXT NOT NULL
                        )
                    ''')

                    # Create rarities table
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS rarities (
                            rarity_id SERIAL PRIMARY KEY,
                            name TEXT NOT NULL UNIQUE,
                            color INTEGER,
                            display_order INTEGER DEFAULT 0
                        )
                    ''')

                    # Create weapon_variants table (links type + rarity)
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS weapon_variants (
                            variant_id SERIAL PRIMARY KEY,
                            type_id INTEGER NOT NULL REFERENCES weapon_types(type_id) ON DELETE CASCADE,
                            rarity_id INTEGER NOT NULL REFERENCES rarities(rarity_id) ON DELETE CASCADE,
                            min_attack INTEGER NOT NULL,
                            max_attack INTEGER NOT NULL,
                            image_url TEXT,
                            UNIQUE(type_id, rarity_id)
                        )
                    ''')

                    # Add variant_id column to user_weapons (if not exists)
                    await conn.execute('''
                        ALTER TABLE user_weapons ADD COLUMN IF NOT EXISTS variant_id INTEGER REFERENCES weapon_variants(variant_id) ON DELETE SET NULL
                    ''')
                    # Seed default rarities (if not present)
                    await conn.execute('''
                        INSERT INTO rarities (name, display_order) VALUES
                        ('Common', 1),
                        ('Uncommon', 2),
                        ('Rare', 3),
                        ('Epic', 4),
                        ('Legendary', 5)
                        ON CONFLICT (name) DO NOTHING
                    ''')

                    # Seed default weapon types (if not present)
                    await conn.execute('''
                    INSERT INTO weapon_types (name_base) VALUES
                    ('Sword'), ('Axe'), ('Dagger')
                    ON CONFLICT DO NOTHING
                    ''')

                    # Seed some variants –  URLs with actual ones.
                    rows = await conn.fetch("SELECT type_id, name_base FROM weapon_types")
                    type_map = {row['name_base']: row['type_id'] for row in rows}
                    rows = await conn.fetch("SELECT rarity_id, name FROM rarities")
                    rarity_map = {row['name']: row['rarity_id'] for row in rows}

                    # Example for Sword variants (replace image URLs)
                    if 'Sword' in type_map and 'Common' in rarity_map:
                    await conn.execute('''
                        INSERT INTO weapon_variants (type_id, rarity_id, min_attack, max_attack, image_url) VALUES
                        ($1, $2, 50, 100, 'https://example.com/sword_common.png'),
                        ($1, $3, 101, 180, 'https://example.com/sword_uncommon.png'),
                        ($1, $4, 181, 270, 'https://example.com/sword_rare.png'),
                        ($1, $5, 271, 380, 'https://example.com/sword_epic.png'),
                        ($1, $6, 381, 500, 'https://example.com/sword_legendary.png')
                        ON CONFLICT (type_id, rarity_id) DO NOTHING
                    ''', type_map['Sword'], rarity_map['Common'], rarity_map['Uncommon'], rarity_map['Rare'], rarity_map['Epic'], rarity_map['Legendary'])



                    # Allow 'weapon' as a valid type
                    await conn.execute('ALTER TABLE shop_items DROP CONSTRAINT IF EXISTS shop_items_type_check')
                    await conn.execute('ALTER TABLE shop_items ADD CONSTRAINT shop_items_type_check CHECK (type IN (\'role\', \'color\', \'weapon\'))')
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS user_weapons (
                            id SERIAL PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            weapon_item_id INTEGER REFERENCES shop_items(item_id) ON DELETE CASCADE,
                            attack INTEGER NOT NULL,
                            purchased_at TIMESTAMP DEFAULT NOW()
                        )
                    ''')
                    # Add purchase_id column to user_weapons if not exists
                    await conn.execute('ALTER TABLE user_weapons ADD COLUMN IF NOT EXISTS purchase_id INTEGER REFERENCES user_purchases(purchase_id) ON DELETE SET NULL')

                    # Ensure expires_at column exists and is timezone‑aware
                    await conn.execute('ALTER TABLE user_purchases ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ')
# If the column already existed as TIMESTAMP (naive), convert it:
                    await conn.execute('ALTER TABLE user_purchases ALTER COLUMN expires_at TYPE TIMESTAMPTZ')
                    await conn.execute('ALTER TABLE user_purchases ADD COLUMN IF NOT EXISTS used BOOLEAN DEFAULT FALSE')
                    # Add image_url column for weapons (if not exists)
                    await conn.execute('ALTER TABLE shop_items ADD COLUMN IF NOT EXISTS image_url TEXT')

                    # Optional indexes
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_purchases_user ON user_purchases(user_id)')


                    # Optional indexes for performance
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_fortune_bags_active ON fortune_bags(active)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_participants_message_id ON fortune_bag_participants(message_id)')

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


# FORTUNE BAG SYSTEM CLASS
class FortuneBag:
    def __init__(self, message_id: int, channel_id: int, dropper_id: int,
                 remaining: int = 1000, total: int = 1000, active: bool = True):
        self.message_id = message_id
        self.channel_id = channel_id
        self.dropper_id = dropper_id
        self.remaining = remaining
        self.total = total
        self.active = active

    async def award(self, bot: commands.Bot, user_id: int) -> int:
        async with bot.db_pool.acquire() as conn:
            async with conn.transaction():
                row = await conn.fetchrow(
                    "SELECT remaining FROM fortune_bags WHERE message_id = $1 FOR UPDATE",
                    self.message_id
                )
                if not row or row['remaining'] <= 0:
                    return 0

                # Check if user already claimed from this bag
                existing = await conn.fetchval(
                    "SELECT 1 FROM fortune_bag_participants WHERE message_id = $1 AND user_id = $2",
                    self.message_id, user_id
                )
                if existing:
                    return -1


                amount = random.randint(1, min(100, row['remaining']))
                new_remaining = row['remaining'] - amount

                await conn.execute(
                    "UPDATE fortune_bags SET remaining = $1 WHERE message_id = $2",
                    new_remaining, self.message_id
                )

                await conn.execute("""
                    INSERT INTO fortune_bag_participants (message_id, user_id, earned)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (message_id, user_id)
                    DO UPDATE SET earned = fortune_bag_participants.earned + $3
                """, self.message_id, user_id, amount)

                self.remaining = new_remaining
                if new_remaining <= 0:
                    self.active = False
                    await conn.execute(
                        "UPDATE fortune_bags SET active = FALSE WHERE message_id = $1",
                        self.message_id
                    )

        # 🔥 ADD THIS – give real gems to user's permanent balance
        await currency_system.add_gems(
            user_id=str(user_id),          # convert to string – your table uses TEXT
            gems=amount,
            reason="🎁 Fortune Bag"
        )

        return amount

async def post_leaderboard(bag: FortuneBag, channel: discord.TextChannel, bot: commands.Bot):
    async with bot.db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT user_id, earned FROM fortune_bag_participants
            WHERE message_id = $1
            ORDER BY earned DESC
        """, bag.message_id)

    embed = discord.Embed(
        title="💎🏆",
        description="The bag is empty! Here's who earned gems:",
        color=discord.Color.green()
    )

    for idx, row in enumerate(rows, start=1):
        user = bot.get_user(row['user_id']) or await bot.fetch_user(row['user_id'])
        embed.add_field(
            name=f"{idx}. {user.display_name}",
            value=f"{row['earned']} gems",
            inline=False
        )
        if idx == 1:
            embed.set_thumbnail(url=user.display_avatar.url)

    await channel.send(embed=embed)


# END FORTUNE BAG SYSTEM CLASS -------------

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

## QUIZ SYSTEM-----------

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
        """Load a large pool of categorized quiz questions."""
        self.all_questions = [
            # 🎨 Arts & Literature
            {"cat": "🎨 Arts & Literature", "q": "Who painted the Mona Lisa?", "a": ["leonardo da vinci", "da vinci", "leonardo"], "pts": 300, "time": 30},
            {"cat": "🎨 Arts & Literature", "q": "Who wrote 'Romeo and Juliet'?", "a": ["shakespeare", "william shakespeare"], "pts": 300, "time": 30},
            {"cat": "🎨 Arts & Literature", "q": "Who painted The Starry Night?", "a": ["van gogh", "vincent van gogh"], "pts": 300, "time": 30},
            {"cat": "🎨 Arts & Literature", "q": "What is the best‑selling book series of all time?", "a": ["harry potter"], "pts": 300, "time": 30},
            {"cat": "🎨 Arts & Literature", "q": "Who sculpted David?", "a": ["michelangelo"], "pts": 300, "time": 30},

            # 🏛️ History
            {"cat": "🏛️ History", "q": "In which year did the Titanic sink?", "a": ["1912"], "pts": 300, "time": 30},
            {"cat": "🏛️ History", "q": "Who was the first US president?", "a": ["washington", "george washington"], "pts": 300, "time": 30},
            {"cat": "🏛️ History", "q": "When did World War II end?", "a": ["1945"], "pts": 300, "time": 30},
            {"cat": "🏛️ History", "q": "Who was the first man on the moon?", "a": ["armstrong", "neil armstrong"], "pts": 300, "time": 30},
            {"cat": "🏛️ History", "q": "What year did the Berlin Wall fall?", "a": ["1989"], "pts": 300, "time": 30},

            # 🎵 Entertainment
            {"cat": "🎵 Entertainment", "q": "Which band performed 'Bohemian Rhapsody'?", "a": ["queen"], "pts": 300, "time": 30},
            {"cat": "🎵 Entertainment", "q": "What is the highest‑grossing film of all time?", "a": ["avatar"], "pts": 300, "time": 30},
            {"cat": "🎵 Entertainment", "q": "Who created Mickey Mouse?", "a": ["disney", "walt disney"], "pts": 300, "time": 30},
            {"cat": "🎵 Entertainment", "q": "What year was the first iPhone released?", "a": ["2007"], "pts": 300, "time": 30},
            {"cat": "🎵 Entertainment", "q": "What is the name of the protagonist in 'The Legend of Zelda'?", "a": ["link"], "pts": 300, "time": 30},

            # 🏅 Sports
            {"cat": "🏅 Sports", "q": "How many players are on a soccer team?", "a": ["11"], "pts": 200, "time": 30},
            {"cat": "🏅 Sports", "q": "What country won the FIFA World Cup in 2018?", "a": ["france"], "pts": 300, "time": 30},
            {"cat": "🏅 Sports", "q": "What is the diameter of a basketball hoop in inches?", "a": ["18"], "pts": 400, "time": 30},
            {"cat": "🏅 Sports", "q": "Who has won the most Olympic gold medals?", "a": ["phelps", "michael phelps"], "pts": 300, "time": 30},
            {"cat": "🏅 Sports", "q": "What sport is played at Wimbledon?", "a": ["tennis"], "pts": 200, "time": 30},

            # 🍔 Food & Drink
            {"cat": "🍔 Food & Drink", "q": "What is the main ingredient in guacamole?", "a": ["avocado"], "pts": 200, "time": 30},
            {"cat": "🍔 Food & Drink", "q": "Which country is famous for croissants?", "a": ["france"], "pts": 200, "time": 30},
            {"cat": "🍔 Food & Drink", "q": "What type of pasta is shaped like small rice grains?", "a": ["orzo"], "pts": 400, "time": 30},
            {"cat": "🍔 Food & Drink", "q": "What is the national drink of Japan?", "a": ["sake"], "pts": 300, "time": 30},
            {"cat": "🍔 Food & Drink", "q": "What fruit is dried to make prunes?", "a": ["plum", "plums"], "pts": 300, "time": 30},

            # 📘 ENGLISH – Professional Precision
            {"cat": "📘 Advanced English", "q": "Correct the sentence: The data suggests that the results is inaccurate.", "a": ["are"], "pts": 200, "time": 30},
            {"cat": "📘 English", "q": "Provide the synonym of 'parsimonious'.", "a": ["stingy", "frugal"], "pts": 200, "time": 30},
            {"cat": "📘 English", "q": "Provide the antonym of 'transient'.", "a": ["permanent", "lasting"], "pts": 200, "time": 30},
            {"cat": "📘 English", "q": "What rhetorical device is used in: 'Time is a thief'?", "a": ["metaphor"], "pts": 200, "time": 30},
            {"cat": "📘 English", "q": "Give the correct form: Neither the officers nor the chief ___ present.", "a": ["was"], "pts": 200, "time": 30},

            # 🔤 WORD ANALOGY
            {"cat": "🔤 Word Analogy", "q": "Complete the analogy: Ephemeral is to Permanent as Mutable is to ___.", "a": ["immutable"], "pts": 200, "time": 30},
            {"cat": "🔤 Word Analogy", "q": "Complete the analogy: Prologue is to Epilogue as Prelude is to ___.", "a": ["postlude"], "pts": 200, "time": 30},
            {"cat": "🔤 Word Analogy", "q": "Complete the analogy: Catalyst is to Acceleration as Inhibitor is to ___.", "a": ["slowdown", "deceleration"], "pts": 200, "time": 30},
            {"cat": "🔤 Word Analogy", "q": "Complete the analogy: Architect is to Blueprint as Composer is to ___.", "a": ["score", "music score"], "pts": 200, "time": 30},
            {"cat": "🔤 Word Analogy", "q": "Complete the analogy: Veneer is to Surface as Core is to ___.", "a": ["center", "centre"], "pts": 200, "time": 30},

            # 🧠 LOGICAL REASONING
            {"cat": "🧠 Logical Reasoning", "q": "All analysts are critical thinkers. Some critical thinkers are researchers. What can be logically inferred about analysts and researchers?", "a": ["some analysts may be researchers", "analysts may be researchers"], "pts": 200, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "If every efficient worker is punctual and some punctual workers are managers, what is a possible conclusion about efficient workers?", "a": ["some efficient workers may be managers", "efficient workers may be managers"], "pts": 200, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "If some metals are conductive and all conductive materials transmit electricity, what can be concluded about some metals?", "a": ["some metals transmit electricity"], "pts": 200, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "A is older than B. B is older than C. D is younger than C. Who is the youngest?", "a": ["d"], "pts": 200, "time": 30},

            # 🔢 NUMERICAL REASONING
            {"cat": "🔢 Numerical Reasoning", "q": "Solve: 5x + 3 = 2x + 24.", "a": ["7"], "pts": 200, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "A price was increased by 25% to 250. What was the original price?", "a": ["200"], "pts": 200, "time": 30},
            {"cat": "🔢 Numerical Reasoning", "q": "If the ratio of men to women is 3:5 and there are 40 people, how many are men?", "a": ["15"], "pts": 200, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "Find the next number: 2, 5, 11, 23, 47, ___.", "a": ["95"], "pts": 200, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "If a train travels 180 km in 3 hours, how far will it travel in 5 hours at the same speed?", "a": ["300"], "pts": 200, "time": 60},

            # 🧩 ABSTRACT & PATTERN ANALYSIS
            {"cat": "🧩 Abstract Reasoning", "q": "Find the next letter sequence: B, E, I, N, T, ___.", "a": ["a"], "pts": 200, "time": 60},
            {"cat": "🧩 Abstract Reasoning", "q": "Find the missing number: 1, 1, 2, 6, 24, 120, ___.", "a": ["720"], "pts": 200, "time": 60},
            {"cat": "🧩 Abstract Reasoning", "q": "If TABLE = 40 (sum of letter positions), what is CHAIR?", "a": ["35"], "pts": 200, "time": 60},
            {"cat": "🧩 Abstract Reasoning", "q": "Find the next number: 4, 9, 19, 39, 79, ___.", "a": ["159"], "pts": 200, "time": 60},
            {"cat": "🧩 Abstract Reasoning", "q": "If RED = 27 and BLUE = 40 (sum of letters), what is GREEN?", "a": ["49"], "pts": 200, "time": 60},
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

            # --- RANDOMLY SELECT 20 QUESTIONS FROM THE POOL ---
            pool = self.all_questions
            num_questions = min(20, len(pool))   # use 20 or fewer if pool is smaller
            self.quiz_questions = random.sample(pool, num_questions)
            random.shuffle(self.quiz_questions)   # extra shuffle for good measure

            await log_to_discord(self.bot, f"📚 Selected {num_questions} randomquestions", "INFO")

            # --- START EMBED (unchanged) ---
            embed = discord.Embed(
                title="🎯 **Quiz Time!**",
                description=(
                    "```\n"
                    "• Type your answer in chat\n"
                    "• Correct Spelling only!\n"
                    "• Faster answers = more points\n"
                    "• Multiple attempts allowed\n"
                    "```\n"
                    f"**First question starts in** ⏰ **60 seconds**"
                ),
                color=0xFFD700
            )

            if channel.guild.icon:
                embed.set_thumbnail(url=channel.guild.icon.url)
            embed.set_footer(text="Good luck! 🍀", icon_url=self.bot.user.display_avatar.url)

            start_msg = await channel.send(embed=embed)
            for i in range(60, 0, -1):
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

            # --- QUESTION EMBED WITH CATEGORY ---
            embed = discord.Embed(
                title=f"❓ **{q.get('cat', 'General')}**",  # Category in title
                description=f"```\n{q['q']}\n```",
                color=0x1E90FF
            )
            # Timer bar and points
            embed.add_field(
                name=f"⏳ **Time Left**",
                value=f"```\n{'🟩'*20}\n{q['time']:02d} seconds\n```\n**Max Points:** ⭐ {q['pts']}",
                inline=False
            )
            embed.set_footer(text=f"Question {self.current_question+1}/{len(self.quiz_questions)} • {q.get('cat', '')}", 
                         icon_url=self.quiz_channel.guild.icon.url if self.quiz_channel.guild.icon else None)

            self.question_message = await self.quiz_channel.send(embed=embed)

            # --- TIMERS ---
            if self.countdown_loop:
                self.countdown_loop.cancel()
            self.countdown_loop = self.bot.loop.create_task(self._run_countdown(q['time']))

            self.bot.loop.call_later(q['time'], lambda: asyncio.create_task(self._timer_expired()))
            await log_to_discord(self.bot, f"⏲️ Timer set for {q['time']}s (Q{self.current_question+1})", "INFO")

        except Exception as e:
            await log_to_discord(self.bot, "❌ send_question failed", "ERROR", e)

    async def _timer_expired(self):
        """Called when the question time limit is reached."""
        await log_to_discord(self.bot, f"⏳ Timer expired for question {self.current_question+1}", "INFO")
        await self.end_question()

    async def _run_countdown(self, total_time):
        """Live countdown bar – updates every second with 4‑color progress."""
        await log_to_discord(self.bot, f"⏳ Countdown started for {total_time}s", "INFO")
        while self.quiz_running and self.question_start_time:
            try:
                elapsed = (datetime.now(timezone.utc) - self.question_start_time).seconds
                time_left = total_time - elapsed
                if time_left <= 0:
                    break

                if not self.question_message:
                    await log_to_discord(self.bot, "⚠️ Question message missing – stopping countdown", "WARN")
                    break

                embed = self.question_message.embeds[0]
                progress = int((time_left / total_time) * 20)  # 20 blocks
                ratio = time_left / total_time

                # --- 4‑COLOR BAR (based on percentage) ---
                if ratio > 0.75:               # > 75% time left
                    bar_char = "🟩"            # Green
                    embed_color = discord.Color.blue()
                elif ratio > 0.50:             # 50% – 75%
                    bar_char = "🟨"            # Yellow
                    embed_color = discord.Color.green()
                elif ratio > 0.25:             # 25% – 50%
                    bar_char = "🟧"            # Orange
                    embed_color = discord.Color.orange()
                else:                          # < 25%
                    bar_char = "🟥"            # Red
                    embed_color = discord.Color.red()
  
                bar = bar_char * progress + "⬜" * (20 - progress)

                # Update the timer field
                for i, field in enumerate(embed.fields):
                    if "⏳" in field.name:
                        embed.set_field_at(
                         i,
                            name=f"⏳ **{time_left:02d} SECONDS LEFT**",
                            value=f"```\n{bar}\n{time_left:02d} seconds\n```\n**Max Points:** ⭐ {self.quiz_questions[self.current_question]['pts']}",
                            inline=False
                        )
                        break

                # Set embed border color
                embed.color = embed_color

                await self.question_message.edit(embed=embed)
            except Exception as e:
                await log_to_discord(self.bot, "⚠️ Countdown error (non‑fatal)", "WARN", e)
            await asyncio.sleep(1)

        await log_to_discord(self.bot, "⏹️ Countdown finished", "INFO")

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
        """End current question, show stats (auto‑delete), countdown 10s, next question."""
        await log_to_discord(self.bot, f"🔚 end_question() called for Q{self.current_question+1}", "INFO")
        try:
            # --- DELETE THE QUESTION MESSAGE ---
            if hasattr(self, 'question_message') and self.question_message:
                try:
                    await self.question_message.delete()
                    await log_to_discord(self.bot, f"🗑️ Deleted question message for Q{self.current_question+1}", "INFO")
                except Exception as e:
                    await log_to_discord(self.bot, f"⚠️ Could not delete question message: {e}", "WARN")

            # --- STOP COUNTDOWN TIMER ---
            if self.countdown_loop:
                self.countdown_loop.cancel()
            self.question_start_time = None

            q = self.quiz_questions[self.current_question]
            correct = "`, `".join([a.capitalize() for a in q['a']])

            # --- STATISTICS EMBED ---
            embed = discord.Embed(
                title=f"✅ **Question {self.current_question+1}/{len(self.quiz_questions)} Complete**",
                description=f"**Correct answer{'s' if len(q['a'])>1 else ''}:** `{correct}`",
                color=0x32CD32
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

            stats = [
                f"👥 **Participants:** {total_p}",
                f"✏️ **Attempted:** {total_ans}",
                f"✅ **Correct:** {correct_cnt}",
                f"📊 **Accuracy:** {round(correct_cnt/total_ans*100,1) if total_ans else 0}%"
            ]
            if fastest_name:
                stats.append(f"⚡ **Fastest:** {fastest_name} ({fastest}s)")

            embed.add_field(name="📋 Statistics", value="\n".join(stats), inline=False)
            embed.set_footer(text=f"Question {self.current_question+1}/{len(self.quiz_questions)}")

            # --- SEND STATS & AUTO‑DELETE AFTER 5 SECONDS ---
            stats_msg = await self.quiz_channel.send(embed=embed)
            self.bot.loop.create_task(self._delete_after(stats_msg, 10))
            await log_to_discord(self.bot, "📊 Statistics embed will self‑destruct in 5s", "INFO")

            # --- LAST QUESTION? ---
            if self.current_question + 1 == len(self.quiz_questions):
                await log_to_discord(self.bot, "🏁 Last question finished, calling end_quiz()", "INFO")
                await self.end_quiz()
                return

            # --- NOT LAST: LEADERBOARD + 10‑SECOND COUNTDOWN ---
            lb_embed = await self.create_leaderboard()          # initial (no countdown yet)
            lb_msg = await self.quiz_channel.send(embed=lb_embed)
 
            for seconds in range(10, 0, -1):                   # 🔥 10 seconds
                updated = await self.create_leaderboard(countdown=seconds)
                await lb_msg.edit(embed=updated)
                await asyncio.sleep(1)

            await lb_msg.delete()
            await log_to_discord(self.bot, "🗑️ Leaderboard deleted, moving to next question", "INFO")

            # --- RESET FOR NEXT QUESTION ---
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
            embed = discord.Embed(title="📊 **LEADERBOARD**", color=discord.Color.gold())

            # --- 10‑SECOND COUNTDOWN BAR (COLOR‑CODED) ---
            if countdown is not None:
                total = 15  # exactly 20 seconds
                progress = int((countdown / total) * 10)  # 10 blocks
                ratio = countdown / total

                # Choose bar color based on percentage remaining
                if ratio > 0.75:
                    bar_char = "🟩"  # Green
                elif ratio > 0.50:
                    bar_char = "🟨"  # Yellow
                elif ratio > 0.25:
                    bar_char = "🟧"  # Orange
                else:
                    bar_char = "🟥"  # Red

                bar = bar_char * progress + "⬜" * (10 - progress)
                embed.description = (
                    f"⏳ **Next question in:** `{countdown}s`\n"
                    f"```\n{bar}\n{countdown:02d} / {total:02d} seconds\n```"
                )
            else:
                embed.description = "🏆 **Current standings**"

            # --- RANKINGS WITH PER‑QUESTION STATUS (unchanged) ---
            lines = []
            for i, (uid, data) in enumerate(sorted_p):
                status = "⏳"
                attempts = [a for a in data["answers"] if a["question"] == self.current_question]
                if attempts:
                    last = attempts[-1]
                    if last["correct"]:
                        status = f"✅ +{last['points']} pts ({last['time']}s)"
                    else:
                        status = f"❌ ({len(attempts)} attempt{'s' if len(attempts)>1 else ''})"

                medal = self.get_rank_emoji(i+1) if i < 10 else f"{i+1}."
                lines.append(f"{medal} **{data['name']}** – {data['score']} pts\n   {status}")

            embed.add_field(name="🏆 Rankings", value="\n".join(lines[:10]), inline=False)
            embed.set_footer(text=f"Total participants: {len(self.participants)}")
            return embed

        except Exception as e:
            await log_to_discord(self.bot, "❌ create_leaderboard failed", "ERROR", e)
            return discord.Embed(title="⚠️ Leaderboard Error", color=discord.Color.red())


    async def _delete_after(self, message, delay):
        """Delete a message after `delay` seconds."""
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except:
            pass

    # ------------------------------------------------------------
    # REWARD DISTRIBUTION
    # ------------------------------------------------------------
    async def distribute_quiz_rewards(self, sorted_participants):
        """Give gems only to participants who scored > 0."""
        rewards = {}
        for rank, (uid, data) in enumerate(sorted_participants, 1):
            # --- SKIP PARTICIPANTS WITH ZERO SCORE ---
            if data["score"] <= 0:
                await log_to_discord(self.bot, f"⏭️ Skipping {data['name']} – score 0, no reward", "INFO")
                rewards[uid] = {"gems": 0, "rank": rank, "result": None}
                continue

            try:
                base = 50  # participation (only for those who scored >0)
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

    async def stop_quiz(self):
        """Immediately stop the quiz and reset."""
        await log_to_discord(self.bot, "🛑 stop_quiz() called", "INFO")  # ✅ self.bot first

        self.quiz_running = False
        self._ending = True

        if self.countdown_loop:
            self.countdown_loop.cancel()
            self.countdown_loop = None

        self.question_start_time = None

        # Reset all state
        self.quiz_channel = None
        self.quiz_logs_channel = None
        self.current_question = 0
        self.participants = {}
        self._ending = False

        await log_to_discord(self.bot, "✅ Quiz stopped and reset", "INFO")  # ✅ self.bot first


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
                    title="🏁 **QUIZ FINISHED!** 🏁",
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
                summary = discord.Embed(title="Quiz Rewards Distributed!", color=discord.Color.gold())
                successful = sum(1 for r in rewards.values() if r.get("gems", 0) > 0)
                summary.add_field(name="Distribution count", value=f"*Successful:* {successful}/{len(sorted_p)}", inline=False)
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
    """Stop the currently running quiz immediately."""
    if not quiz_system.quiz_running:
        await ctx.send("❌ No quiz is currently running.", delete_after=5)
        return

    # Ask for confirmation
    confirm = await ctx.send("⚠️ **Are you sure?** This will stop the quiz and **no rewards will be distributed**. Reply with `yes` or `no` (15 seconds).")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["yes", "no"]

    try:
        reply = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("⏰ Timeout – quiz continues.", delete_after=5)
        return

    if reply.content.lower() == "no":
        await ctx.send("✅ Stop cancelled. Quiz continues.", delete_after=5)
        return

    # --- STOP THE QUIZ ---
    await ctx.send("🛑 Stopping quiz...")

    try:
        # Remember the quiz channel before reset
        quiz_channel = quiz_system.quiz_channel

        # Stop the quiz (resets everything)
        await quiz_system.stop_quiz()

        # Delete the current question message if it exists
        if hasattr(quiz_system, 'question_message') and quiz_system.question_message:
            try:
                await quiz_system.question_message.delete()
            except:
                pass

        # Send notification to the original quiz channel
        if quiz_channel:
            embed = discord.Embed(
                title="🛑 **Quiz Stopped**",
                description=(
                    f"The Quiz has been manually stopped by {ctx.author.mention}.\n"
                    "**No rewards were distributed.**"
                ),
                color=discord.Color.red()
            )
            
            await quiz_channel.send(embed=embed)

        # Confirm in the command channel
        await ctx.send("✅ Quiz has been successfully stopped and reset.")
        await log_to_discord(bot, f"Quiz manually stopped by {ctx.author}", "INFO")

    except Exception as e:
        await ctx.send(f"❌ Error while stopping quiz: {str(e)[:100]}")
        await log_to_discord(bot, f"Error in quiz_stop: {e}", "ERROR")

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

# FORTUNE BAG COMMAND
@bot.command(name='fortunebagto')
async def fortune_bag_to(ctx, channel: discord.TextChannel):
    """Send a fortune bag image to the specified channel with a clickable button."""
    # 1. Image URL – replace with your actual image URL
    IMAGE_URL = "https://image2url.com/r2/default/images/1771341429734-6e403054-e4a3-4ef3-9207-f4b24f390a3e.png"
    
    # 2. Download the image and create a discord.File
    async with aiohttp.ClientSession() as session:
        async with session.get(IMAGE_URL) as resp:
            if resp.status != 200:
                return await ctx.send("❌ Failed to fetch fortune bag image.")
            data = await resp.read()
    
    # 3. Send as a plain message with attachment
    file = discord.File(io.BytesIO(data), filename="fortune-bag.png")
    view = discord.ui.View(timeout=None)
    button = discord.ui.Button(
        label="🎁 Open Bag",  # You can set label to empty string if you want no text, but button needs some label.
        style=discord.ButtonStyle.primary,
        custom_id=f"openbag_temp_{ctx.message.id}"  # temporary, will update after we know message_id
    )
    view.add_item(button)
    
    msg = await channel.send(file=file, view=view)
    
    # 4. Update button custom_id to use the actual message_id
    view = discord.ui.View(timeout=None)
    button = discord.ui.Button(
        label="🎁 Open Bag",
        style=discord.ButtonStyle.primary,
        custom_id=f"openbag_{msg.id}"
    )
    view.add_item(button)
    await msg.edit(view=view)
    
    # 5. Store in database (same as before)
    bag = FortuneBag(msg.id, channel.id, ctx.author.id, 1000)
    async with bot.db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO fortune_bags (message_id, channel_id, remaining, total, dropper_id, active)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, bag.message_id, bag.channel_id, bag.remaining, bag.total, bag.dropper_id, bag.active)
    
    bot.active_bags[msg.id] = bag
    await ctx.send(f"✅ Fortune bag sent to {channel.mention}!", delete_after=5)


# END------



# === BOT STARTUP ===
@bot.event
async def on_ready():
    print(f"\n✅ {bot.user} is online!")
    
    # Try to connect to database
    print("\n🔌 Attempting database connection...")
    connected = await db.smart_connect()

    if connected:
        print("🎉 DATABASE CONNECTED SUCCESSFULLY!")
        await load_active_bags()
        await load_shop_persistence(bot)
        print("✅ Your data will persist across redeploys")
    else:
        print("⚠️ Database not connected – fortune bags and shop will not be available.")
        print("❌ Data may reset on redeploy")


    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=""
        )
    )
    print("\n🤖 Bot is ready!")


# FORTUNE BAG ON READY
async def load_active_bags():
    async with bot.db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT message_id, channel_id, remaining, total, dropper_id FROM fortune_bags WHERE active = TRUE"
        )
    for row in rows:
        bag = FortuneBag(
            message_id=row['message_id'],
            channel_id=row['channel_id'],
            dropper_id=row['dropper_id'],
            remaining=row['remaining'],
            total=row['total']
        )
        bot.active_bags[bag.message_id] = bag

        # Re‑attach view
        channel = bot.get_channel(bag.channel_id)
        if channel:
            try:
                msg = await channel.fetch_message(bag.message_id)
                view = discord.ui.View(timeout=None)
                button = discord.ui.Button(
                    label="Open Bag",
                    style=discord.ButtonStyle.primary,
                    custom_id=f"openbag_{bag.message_id}"
                )
                view.add_item(button)
                await msg.edit(view=view)
            except discord.NotFound:
                async with bot.db_pool.acquire() as conn:
                    await conn.execute(
                        "UPDATE fortune_bags SET active = FALSE WHERE message_id = $1",
                        bag.message_id
                    )

bot.setup_hook = lambda: bot.loop.create_task(load_active_bags())

# END ------

# FORTUNE BAG HANDLER

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data["custom_id"]
        if custom_id.startswith("openbag_"):
            await handle_open_bag(interaction)

async def handle_open_bag(interaction: discord.Interaction):
    message_id = int(interaction.message.id)
    bag = bot.active_bags.get(message_id)
    if not bag or not bag.active:
        await interaction.response.send_message(
            "This bag is empty!", 
            ephemeral=True
        )
        return

    awarded = await bag.award(bot, interaction.user.id)

    # --- CASE 1: Bag empty ---
    if awarded == 0:
        await interaction.response.send_message(
            "All Gems have already claimed!",
            ephemeral=True
        )
        return

    # --- CASE 2: User already claimed ---
    if awarded == -1:
        await interaction.response.send_message(
            "You've already opened this bag!\n",
            ephemeral=True
        )
        # Auto‑delete after 10 seconds
        await asyncio.sleep(10)
        await interaction.delete_original_response()
        return

    # --- CASE 3: Success ---
    # Get user's updated gem balance
    balance = await currency_system.get_balance(str(interaction.user.id))
    
    # Add ❤️ reaction to the bag message
    try:
        await interaction.message.add_reaction("❤️")
    except:
        pass

    # If bag became empty, disable button and post leaderboard
    if bag.remaining <= 0:
        view = discord.ui.View.from_message(interaction.message)
        for child in view.children:
            child.disabled = True
        await interaction.message.edit(view=view)
        await post_leaderboard(bag, interaction.channel, bot)

    # Send ephemeral success message
    await interaction.response.send_message(
        f"You opened the bag and found **{awarded} Gems**!\n"
        f"**New balance:** {balance['gems']} gems\n"
        f"{bag.remaining} Gems remain in the bag",
        ephemeral=True
    )

    # Auto‑delete after 10 seconds
    await asyncio.sleep(10)
    await interaction.delete_original_response()
    #  END ------

# === ERROR HANDLER ===
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"Command error: {error}")
    await ctx.send(f"❌ Error: {str(error)[:100]}")







# =============================================================================
# SHOP SYSTEM – Persistent Interactive Shop
# =============================================================================
class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SHOP_IMAGE_URL = "https://cdn.discordapp.com/attachments/1470664051242700800/1471797792262455306/d4387e84d53fd24697a4218a9f6924a5.png?ex=6992e102&is=69918f82&hm=8a7bf535085e1dd0af98d977c5cc9766ecf463b73dbb5330444ff739b62c3571&"  # 🔁 REPLACE
        self.check_expired_purchases.start()
        self.booking_sessions = {}

    def cog_unload(self):
        self.check_expired_purchases.cancel()
        

    # -------------------------------------------------------------------------
    # BACKGROUND TASK: Remove expired roles every hour
    # -------------------------------------------------------------------------
    @tasks.loop(hours=1)
    async def check_expired_purchases(self):
        """Remove expired purchases: delete record and remove role from user."""
        # Wait for bot to be fully ready and db_pool to be set
        await self.bot.wait_until_ready()
        if not hasattr(self.bot, 'db_pool') or self.bot.db_pool is None:
            print("⏳ check_expired_purchases: db_pool not ready, skipping.")
            return

        try:
            async with self.bot.db_pool.acquire() as conn:
                # Fetch expired purchases with guild_id
                rows = await conn.fetch("""
                    SELECT up.user_id, up.item_id, si.role_id, si.guild_id, si.name
                    FROM user_purchases up
                    JOIN shop_items si ON up.item_id = si.item_id
                    WHERE up.expires_at < NOW()
                """)

                for row in rows:
                    user_id = row['user_id']
                    guild_id = row['guild_id']
                    role_id = row['role_id']
                    item_name = row['name']

                    guild = self.bot.get_guild(guild_id)
                    if guild:
                        member = guild.get_member(int(user_id))
                        if member:
                            role = guild.get_role(role_id)
                            if role:
                                try:
                                    await member.remove_roles(role, reason="Shop item expired (7 days)")
                                    print(f"✅ Removed expired role '{item_name}' from {member} (ID: {user_id})")
                                except discord.Forbidden:
                                    print(f"❌ No permission to remove role {role_id} from user {user_id} in guild {guild_id}")
                                except Exception as e:
                                    print(f"⚠️ Error removing role: {e}")
                            else:
                                print(f"⚠️ Role {role_id} not found in guild {guild_id}")
                        else:
                            print(f"⚠️ Member {user_id} not found in guild {guild_id}")
                    else:
                        print(f"⚠️ Guild {guild_id} not found")

                # Delete all expired purchase records
                result = await conn.execute("DELETE FROM user_purchases WHERE expires_at < NOW()")
                print(f"🧹 Cleaned up {result.split()[1]} expired purchase records.")
        except Exception as e:
            print(f"❌ Error in check_expired_purchases: {e}")
    # -------------------------------------------------------------------------
    # LOAD PERSISTENT SHOP MESSAGES
    # -------------------------------------------------------------------------
    async def load_shop_messages(self):
        async with self.bot.db_pool.acquire() as conn:
            rows = await conn.fetch("SELECT guild_id, channel_id, message_id FROM shop_messages")
        for row in rows:
            guild = self.bot.get_guild(row['guild_id'])
            if not guild:
                continue
            channel = guild.get_channel(row['channel_id'])
            if not channel:
                continue
            try:
                msg = await channel.fetch_message(row['message_id'])
                view = discord.ui.View(timeout=None)
                button = discord.ui.Button(
                    label="🛒 Open Shop",
                    style=discord.ButtonStyle.primary,
                    custom_id="shop_open_main"
                )
                view.add_item(button)
                await msg.edit(view=view)
                print(f"✅ Reattached shop view in #{channel.name}")
            except Exception as e:
                print(f"⚠️ Failed to reattach shop message {row['message_id']}: {e}")

    # -------------------------------------------------------------------------
    # ADMIN COMMAND – Summon permanent shop
    # -------------------------------------------------------------------------
    @commands.command(name='summonshopto')
    @commands.has_permissions(administrator=True)
    async def summon_shop_to(self, ctx, channel: discord.TextChannel):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.SHOP_IMAGE_URL) as resp:
                if resp.status != 200:
                    return await ctx.send("❌ Failed to fetch shop image.")
                data = await resp.read()
        file = discord.File(io.BytesIO(data), filename="shop.png")

        embed = discord.Embed(
            title="💎 **GEM SHOP**",
            description="",
            color=discord.Color.gold()
        )
        embed.set_image(url="attachment://shop.png")

        view = discord.ui.View(timeout=None)
        button = discord.ui.Button(
            label="🛒 Open Shop",
            style=discord.ButtonStyle.primary,
            custom_id="shop_open_main"
        )
        view.add_item(button)

        msg = await channel.send(file=file, embed=embed, view=view)

        async with self.bot.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO shop_messages (guild_id, channel_id, message_id)
                VALUES ($1, $2, $3)
                ON CONFLICT (guild_id) DO UPDATE
                SET channel_id = $2, message_id = $3
            """, ctx.guild.id, channel.id, msg.id)

        await ctx.send(f"✅ Shop permanently summoned to {channel.mention}!", delete_after=5)
        await ctx.message.delete(delay=5)

    # -------------------------------------------------------------------------
    # INTERACTION HANDLER
    # -------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return

        custom_id = interaction.data["custom_id"]

        if custom_id == "shop_open_main":
            await self.show_main_categories(interaction)
        elif custom_id.startswith("shop_maincat_"):
            main_cat = custom_id.replace("shop_maincat_", "")
            await self.show_subcategories(interaction, main_cat)
        elif custom_id.startswith("shop_subcat_"):
            subcat = custom_id.replace("shop_subcat_", "")
            await self.show_items(interaction, subcat)
        elif custom_id == "shop_back_to_main":
            await self.show_main_categories(interaction)
        elif custom_id == "shop_back_to_sub":
            await self.show_main_categories(interaction)  # Simplified
        elif custom_id.startswith("shop_buy_"):
            item_id = int(custom_id.replace("shop_buy_", ""))
            await self.purchase_item(interaction, item_id)
        elif custom_id.startswith("secret_shop_"):
            purchase_id = int(custom_id.split("_")[2])
            await self.secret_shop_button(interaction, purchase_id)
    # -------------------------------------------------------------------------
    # SHOW MAIN CATEGORIES
    # -------------------------------------------------------------------------
    async def show_main_categories(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🛍️ Shop Categories",
            description="Select a category to browse.",
            color=discord.Color.blue()
        )
        view = discord.ui.View(timeout=300)
        # Main categories (you can add more later)
        main_cats = [
            ("🎨 Customization", "customization"),
            ("🗡️ Weapons", "weapons")
        ]
        for label, cat_id in main_cats:
            button = discord.ui.Button(
                label=label,
                style=discord.ButtonStyle.secondary,
                custom_id=f"shop_maincat_{cat_id}"
            )
            view.add_item(button)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    # -------------------------------------------------------------------------
    # SHOW SUBCATEGORIES
    # -------------------------------------------------------------------------
    async def show_subcategories(self, interaction: discord.Interaction, main_cat: str):
        if main_cat == "customization":
            embed = discord.Embed(
                title="🎨 Customization",
                description="What would you like to buy?",
                color=discord.Color.purple()
            )
            view = discord.ui.View(timeout=300)
            # Subcategories
            subcats = [
                ("🪯 Roles", "roles"),
                ("🎨 Name Color Change", "colors")
            ]
        elif main_cat == "weapons":
            embed = discord.Embed(
                title="⚔️ Weapons Shop",
                description="Choose a weapon to purchase. Each weapon gets a random attack bonus!",
                color=discord.Color.red()
            )
            view = discord.ui.View(timeout=300)
            # For now, we'll just show all weapons directly (no subcategories)
            # Call a method to list weapon items
            await self.show_weapon_items(interaction, embed, view)

            for label, sub_id in subcats:
                button = discord.ui.Button(
                    label=label,
                    style=discord.ButtonStyle.primary,
                    custom_id=f"shop_subcat_{sub_id}"
                )
                view.add_item(button)
            # Back button
            back = discord.ui.Button(
                label="◀ Back to Categories",
                style=discord.ButtonStyle.secondary,
                custom_id="shop_back_to_main"
            )
            view.add_item(back)
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            # Handle other main cats if needed
            await interaction.response.send_message("Coming soon!", ephemeral=True)

    # -------------------------------------------------------------------------
    # SHOW ITEMS FOR A SUBCATEGORY
    # -------------------------------------------------------------------------
    async def show_items(self, interaction: discord.Interaction, subcat: str):
        # subcat = "roles" or "colors"
        item_type = "role" if subcat == "roles" else "color"
        async with self.bot.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT item_id, name, description, price, type
                FROM shop_items
                WHERE type = $1
                ORDER BY price ASC
            """, item_type)

        if not rows:
            embed = discord.Embed(
                title=f"🛍️ {subcat.title()}",
                description="No items available in this category yet.",
                color=discord.Color.red()
            )
            view = discord.ui.View(timeout=300)
            back = discord.ui.Button(
                label="◀ Back",
                style=discord.ButtonStyle.secondary,
                custom_id="shop_back_to_main"  # Goes to main cats for simplicity
            )
            view.add_item(back)
            await interaction.response.edit_message(embed=embed, view=view)
            return

        embed = discord.Embed(
            title=f"🛍️ {subcat.title()}",
            description="Click an item to purchase it with gems.",
            color=discord.Color.gold()
        )
        view = discord.ui.View(timeout=300)

        for row in rows:
            label = f"{row['name']} – {row['price']} gems"
            button = discord.ui.Button(
                label=label[:80],
                style=discord.ButtonStyle.primary,
                custom_id=f"shop_buy_{row['item_id']}"
            )
            view.add_item(button)

        back = discord.ui.Button(
            label="◀ Back",
            style=discord.ButtonStyle.secondary,
            custom_id="shop_back_to_main"
        )
        view.add_item(back)

        await interaction.response.edit_message(embed=embed, view=view)


    async def show_weapon_items(self, interaction: discord.Interaction, embed, view):
        """Display all weapon items."""
        async with self.bot.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT item_id, name, description, price
                FROM shop_items
                WHERE type = 'weapon'
                ORDER BY price ASC
            """)

        if not rows:
            embed.description = "No weapons available yet."
            back = discord.ui.Button(label="◀ Back", style=discord.ButtonStyle.secondary, custom_id="shop_back_to_main")
            view.add_item(back)
            await interaction.response.edit_message(embed=embed, view=view)
            return

        for row in rows:
            label = f"{row['name']} – {row['price']} gems"
            button = discord.ui.Button(
                label=label[:80],
                style=discord.ButtonStyle.primary,
                custom_id=f"shop_buy_{row['item_id']}"
            )
            view.add_item(button)

        back = discord.ui.Button(label="◀ Back", style=discord.ButtonStyle.secondary, custom_id="shop_back_to_main")
        view.add_item(back)

        await interaction.response.edit_message(embed=embed, view=view)


# RARITY
    @commands.group(name='rarity', invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def rarity_admin(self, ctx):
        """Manage rarities for weapons."""
        embed = discord.Embed(
            title="✨ Rarity Admin",
            description=(
                "`!!rarity add <name> [color]` – e.g. `Epic 0xFFD700`\n"
                "`!!rarity list`\n"
                "`!!rarity remove <name>`"
            ),
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    @rarity_admin.command(name='add')
    @commands.has_permissions(administrator=True)
    async def rarity_add(self, ctx, name: str, color: int = None):
        async with self.bot.db_pool.acquire() as conn:
            try:
                await conn.execute(
                    "INSERT INTO rarities (name, color) VALUES ($1, $2)",
                    name, color
                )
                await ctx.send(f"✅ Added rarity: **{name}**")
            except asyncpg.UniqueViolationError:
                await ctx.send(f"❌ Rarity '{name}' already exists.")

    @rarity_admin.command(name='list')
    @commands.has_permissions(administrator=True)
    async def rarity_list(self, ctx):
        async with self.bot.db_pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM rarities ORDER BY display_order, name")
        if not rows:
            await ctx.send("No rarities defined yet.")
            return
        embed = discord.Embed(title="Rarities", color=discord.Color.blue())
        for r in rows:
            embed.add_field(
                name=f"ID {r['rarity_id']}: {r['name']}",
                value=f"Color: {r['color'] or 'Default'}",
                inline=False
            )
        await ctx.send(embed=embed)

    @rarity_admin.command(name='remove')
    @commands.has_permissions(administrator=True)
    async def rarity_remove(self, ctx, name: str):
        async with self.bot.db_pool.acquire() as conn:
            result = await conn.execute("DELETE FROM rarities WHERE name = $1", name)
        if result == "DELETE 0":
            await ctx.send(f"❌ Rarity '{name}' not found.")
        else:
            await ctx.send(f"✅ Removed rarity: **{name}**")
# END RARITY

# VARIANT
    @commands.group(name='variant', invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def variant_admin(self, ctx):
        """Link a weapon type with a rarity (create a variant)."""
        embed = discord.Embed(
            title="🔗 Weapon Variant Admin",
            description=(
                "`!!variant add <type_id> <rarity_id> <min_atk> <max_atk> <image_url>`\n"
                "`!!variant list [type_id]`\n"
                "`!!variant remove <variant_id>`"
            ),
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)

    @variant_admin.command(name='add')
    @commands.has_permissions(administrator=True)
    async def variant_add(self, ctx, type_id: int, rarity_id: int, min_attack: int, max_attack: int, image_url: str):
        if min_attack < 0 or max_attack < min_attack:
            await ctx.send("❌ Invalid attack range.")
            return
        if not (image_url.startswith('http://') or image_url.startswith('https://')):
            await ctx.send("❌ Image URL must start with http:// or https://")
            return

        async with self.bot.db_pool.acquire() as conn:
            type_exists = await conn.fetchval("SELECT 1 FROM weapon_types WHERE type_id = $1", type_id)
            rarity_exists = await conn.fetchval("SELECT 1 FROM rarities WHERE rarity_id = $1", rarity_id)
            if not type_exists:
                await ctx.send(f"❌ Weapon type {type_id} not found.")
                return
            if not rarity_exists:
                await ctx.send(f"❌ Rarity {rarity_id} not found.")
                return

            try:
                await conn.execute("""
                    INSERT INTO weapon_variants (type_id, rarity_id, min_attack, max_attack, image_url)
                    VALUES ($1, $2, $3, $4, $5)
                """, type_id, rarity_id, min_attack, max_attack, image_url)
                await ctx.send(f"✅ Added variant for type {type_id} + rarity {rarity_id} (ATK {min_attack}–{max_attack})")
            except asyncpg.UniqueViolationError:
                await ctx.send("❌ This variant already exists (type + rarity combination is unique).")

    @variant_admin.command(name='list')
    @commands.has_permissions(administrator=True)
    async def variant_list(self, ctx, type_id: int = None):
        async with self.bot.db_pool.acquire() as conn:
            if type_id:
                rows = await conn.fetch("""
                    SELECT v.*, t.name_base, r.name as rarity_name
                    FROM weapon_variants v
                    JOIN weapon_types t ON v.type_id = t.type_id
                    JOIN rarities r ON v.rarity_id = r.rarity_id
                    WHERE v.type_id = $1
                    ORDER BY r.display_order, t.name_base
               """, type_id)
            else:
                rows = await conn.fetch("""
                    SELECT v.*, t.name_base, r.name as rarity_name
                    FROM weapon_variants v
                    JOIN weapon_types t ON v.type_id = t.type_id
                    JOIN rarities r ON v.rarity_id = r.rarity_id
                    ORDER BY t.name_base, r.display_order
                """)
        if not rows:
            await ctx.send("No variants found.")
            return
        embed = discord.Embed(title="Weapon Variants", color=discord.Color.green())
        for r in rows:
            embed.add_field(
                name=f"ID {r['variant_id']}: {r['rarity_name']} {r['name_base']}",
                value=f"ATK: {r['min_attack']}–{r['max_attack']}",
                inline=False
            )
        await ctx.send(embed=embed)

    @variant_admin.command(name='remove')
    @commands.has_permissions(administrator=True)
    async def variant_remove(self, ctx, variant_id: int):
        async with self.bot.db_pool.acquire() as conn:
            result = await conn.execute("DELETE FROM weapon_variants WHERE variant_id = $1", variant_id)
        if result == "DELETE 0":
            await ctx.send(f"❌ Variant {variant_id} not found.")
        else:
            await ctx.send(f"✅ Removed variant {variant_id}.")
# END VARIANT

# RANDOM BOX
    @commands.command(name='addrandombox')
    @commands.has_permissions(administrator=True)
    async def add_random_box(self, ctx, name: str, price: int, *, description: str = "Open to get a random weapon!", image_url: str = None):
        """Add a random weapon box item to the shop."""
        if image_url and not (image_url.startswith('http://') or image_url.startswith('https://')):
            await ctx.send("❌ Invalid image URL.")
            return
        async with self.bot.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO shop_items (name, description, price, type, guild_id, image_url)
                VALUES ($1, $2, $3, 'random_weapon_box', $4, $5)
            """, name, description, price, ctx.guild.id, image_url)
        await ctx.send(f"✅ Added random weapon box **{name}** for **{price} gems**.")
# END RANDOM BOX


    # -------------------------------------------------------------------------
    # PURCHASE ITEM – with duplicate & expiration checks
    # -------------------------------------------------------------------------
    async def purchase_item(self, interaction: discord.Interaction, item_id: int):
        await interaction.response.defer(ephemeral=True)

        # Fetch item details
        async with self.bot.db_pool.acquire() as conn:
            item = await conn.fetchrow(
                "SELECT * FROM shop_items WHERE item_id = $1",
                item_id
            )
        if not item:
            await interaction.followup.send("❌ This item no longer exists.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        now = datetime.now(timezone.utc)

        # ========== WEAPON PURCHASE ==========
        if item['type'] == 'weapon':
            # Check if user already owns this weapon (in user_weapons)
            async with self.bot.db_pool.acquire() as conn:
                exists = await conn.fetchval("""
                    SELECT 1 FROM user_weapons
                    WHERE user_id = $1 AND weapon_item_id = $2
                """, user_id, item_id)
            if exists:
                embed = discord.Embed(
                    title="❌ Already Owned",
                    description=f"You already own **{item['name']}**.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Check balance
            balance = await currency_system.get_balance(user_id)
            if balance['gems'] < item['price']:
                embed = discord.Embed(
                    title="❌ Insufficient Gems",
                    description=f"You need **{item['price']} gems** to buy **{item['name']}**.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Deduct gems
            success = await currency_system.deduct_gems(
                user_id=user_id,
                gems=item['price'],
                reason=f"🛒 Purchased {item['name']}"
            )
            if not success:
                await interaction.followup.send("❌ Failed to deduct gems.", ephemeral=True)
                return

            # Generate random attack
            attack = random.randint(50, 500)

            # Insert into user_weapons (no purchase record needed)
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO user_weapons (user_id, weapon_item_id, attack)
                    VALUES ($1, $2, $3)
                """, user_id, item_id, attack)

            # Compact embed for weapon
            desc = item.get('description') or "No description available."
            wrapped_desc = "\n".join(textwrap.wrap(desc, width=45))
            embed = discord.Embed(
                title=f"{item['name']} (+{attack} ATK)",
                description=f"*{wrapped_desc}*",
                color=discord.Color.red()
            )
            if item.get('image_url'):
                embed.set_image(url=item['image_url'])
            embed.set_footer(text="Added to your collection!")

            await interaction.followup.send(embed=embed, ephemeral=True)
            return   # <-- stop here – weapon handled

        # ========== RANDOM WEAPON BOX ==========
        if item['type'] == 'random_weapon_box':
        balance = await currency_system.get_balance(user_id)
        if balance['gems'] < item['price']:
            embed = discord.Embed(
                title="❌ Insufficient Gems",
                description=f"You need **{item['price']} gems** to buy **{item['name']}**.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        success = await currency_system.deduct_gems(user_id, item['price'], f"🛒 Purchased {item['name']}")
        if not success:
            await interaction.followup.send("❌ Failed to deduct gems.", ephemeral=True)
            return

        # Fetch all variants with type and rarity info
        async with self.bot.db_pool.acquire() as conn:
            variants = await conn.fetch("""
                SELECT v.*, t.name_base, r.name as rarity_name
                FROM weapon_variants v
                JOIN weapon_types t ON v.type_id = t.type_id
                JOIN rarities r ON v.rarity_id = r.rarity_id
            """)
            adjectives = await conn.fetch("SELECT word FROM weapon_adjectives")
            suffixes = await conn.fetch("SELECT phrase FROM weapon_suffixes")

        if not variants:
            await interaction.followup.send("❌ No weapon variants configured. Contact an admin.", ephemeral=True)
            return

        # Randomly pick a variant, adjective, suffix
        chosen = random.choice(variants)
        adj = random.choice(adjectives)['word'] if adjectives else ""
        suffix = random.choice(suffixes)['phrase'] if suffixes else ""

        # Build name: e.g., "Epic Flaming Sword of Destruction"
        parts = [chosen['rarity_name']]
        if adj:
            parts.append(adj)
        parts.append(chosen['name_base'])
        if suffix:
            parts.append(suffix)
        weapon_name = " ".join(parts)

        # Generate attack within variant's range
        attack = random.randint(chosen['min_attack'], chosen['max_attack'])

        # Insert into user_weapons (create a purchase record if needed)
        async with self.bot.db_pool.acquire() as conn:
            purchase_id = await conn.fetchval("""
                INSERT INTO user_purchases (user_id, item_id, price_paid, expires_at)
                VALUES ($1, $2, $3, $4)
                RETURNING purchase_id
            """, user_id, item['item_id'], item['price'], datetime.now(timezone.utc) + timedelta(days=7))

            await conn.execute("""
                INSERT INTO user_weapons (user_id, weapon_item_id, attack, purchase_id, generated_name, image_url, variant_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, user_id, None, attack, purchase_id, weapon_name, chosen['image_url'], chosen['variant_id'])

        # Show result: box image then weapon image
        box_embed = discord.Embed(
            title="🎁 Mystery Box Opened!",
            description=f"You received: **{weapon_name}**",
            color=discord.Color.purple()
       )
        if item['image_url']:
            box_embed.set_image(url=item['image_url'])
        await interaction.followup.send(embed=box_embed, ephemeral=True)

        weapon_embed = discord.Embed(
            title=f"{weapon_name} (+{attack} ATK)",
            description=f"*A random weapon from the box.*",
            color=discord.Color.red()
        )
        if chosen['image_url']:
            weapon_embed.set_image(url=chosen['image_url'])
        await interaction.followup.send(embed=weapon_embed, ephemeral=True)

        # Log the purchase
        await self.send_shop_log(interaction.guild, interaction.user, item['name'], item['price'], balance['gems'] - item['price'])
        return

        # ========== NON-WEAPON ITEMS (roles/colors) ==========
        # Check user_purchases for existing active purchase
        async with self.bot.db_pool.acquire() as conn:
            active = await conn.fetchval("""
                SELECT 1 FROM user_purchases
                WHERE user_id = $1 AND item_id = $2 AND expires_at > $3 AND used = FALSE
            """, user_id, item_id, now)
        if active:
            embed = discord.Embed(
                title="❌ Already Owned",
                description="You already own this item and it hasn't expired yet.\nIt will expire in a few days – you can buy it again after that.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Balance check
        balance = await currency_system.get_balance(user_id)
        if balance['gems'] < item['price']:
            embed = discord.Embed(
                title="❌ Insufficient Gems",
                description=f"You need **{item['price']} gems** to buy **{item['name']}**.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Role assignment
        guild = interaction.guild
        member = interaction.user
        role = guild.get_role(item['role_id'])
        if not role:
            await interaction.followup.send("❌ The role for this item no longer exists.", ephemeral=True)
            return
        try:
            await member.add_roles(role, reason=f"Shop purchase: {item['name']}")
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to assign that role.", ephemeral=True)
            return
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to assign role: {e}", ephemeral=True)
            return

        # Deduct gems
        success = await currency_system.deduct_gems(
            user_id=user_id,
            gems=item['price'],
            reason=f"🛒 Purchased {item['name']}"
        )
        if not success:
            await interaction.followup.send("❌ Failed to deduct gems.", ephemeral=True)
            return

        # Record purchase with expiration (7 days)
        expires_at = now + timedelta(days=7)
        async with self.bot.db_pool.acquire() as conn:
            purchase_id = await conn.fetchval("""
                INSERT INTO user_purchases (user_id, item_id, price_paid, expires_at)
                VALUES ($1, $2, $3, $4)
                RETURNING purchase_id
            """, user_id, item_id, item['price'], expires_at)

        # Success embed for non-weapons
        new_balance = await currency_system.get_balance(user_id)
        embed = discord.Embed(
            title="✅ Purchase Successful!",
            description=f"You have bought **{item['name']}** for **{item['price']} gems**.",
            color=discord.Color.green()
        )
        embed.add_field(name="💰 New Balance", value=f"{new_balance['gems']} gems")
        embed.add_field(name="⏳ Expires", value=f"<t:{int(expires_at.timestamp())}:R>", inline=False)
        if item['type'] == 'color' and item.get('color_hex'):
            embed.color = discord.Color(int(item['color_hex'].lstrip('#'), 16))
        embed.set_footer(text="Thank you for shopping!")

        await interaction.followup.send(embed=embed, ephemeral=True)

        # --- SPECIAL CASE: Treasure Carriage ---
        if item['name'].lower() == "treasure carriage":  # case-insensitive match
            # Send ephemeral message with a button to open the secret shop
            view = discord.ui.View(timeout=300)
            button = discord.ui.Button(
                label="Continue",
                style=discord.ButtonStyle.primary,
                custom_id=f"secret_shop_{purchase_id}"
            )
            view.add_item(button)

            embed = discord.Embed(
                title="🎫 Treasure Carriage Seat Purchased!",
                description=(
                    f"You have bought a **Treasure Carriage** Seat for **{item['price']} gems**.\n"
                    f"Click the button below to continue " 
                    f"and book your ride (in‑game name + time).\n\n"
                    f"⚠️ This button will disappear after use or after 5 minutes of inactivity."
                ),
                color=discord.Color.gold()
            )
            embed.set_footer(text="The item will be removed after you book your ride.")

            # Store the purchase_id in the view for later use? Not needed, it's in custom_id.
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)

            # Log the purchase normally as well
            await self.send_shop_log(guild, member, item['name'], item['price'], balance['gems'] - item['price'])
            return  # stop here – don't send the normal success embed

        # Success message
        new_balance = await currency_system.get_balance(user_id)
        # Send log to #shop-logs
        await self.send_shop_log(interaction.guild, interaction.user, item['name'], item['price'], new_balance['gems'])
        embed = discord.Embed(
            title="✅ Purchase Successful!",
            description=f"You have bought **{item['name']}** for **{item['price']} gems**.",
            color=discord.Color.green()
        )
        embed.add_field(name="💰 New Balance", value=f"{new_balance['gems']} gems")
        embed.add_field(name="⏳ Expires", value=f"<t:{int(expires_at.timestamp())}:R>", inline=False)
        if item['type'] == 'color' and item.get('color_hex'):
            embed.color = discord.Color(int(item['color_hex'].lstrip('#'), 16))
        embed.set_footer(text="Thank you for shopping!")

        await interaction.followup.send(embed=embed, ephemeral=True)


    # SECRET SHOP ===============
    async def secret_shop_button(self, interaction: discord.Interaction, purchase_id: int):
        """Start DM booking process."""
        async with self.bot.db_pool.acquire() as conn:
            purchase = await conn.fetchrow(
                "SELECT * FROM user_purchases WHERE purchase_id = $1 AND used = FALSE",
                purchase_id
            )
        if not purchase:
            await interaction.response.send_message("❌ Ticket already used.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        try:
            await interaction.user.send("**Treasure Carriage Booking**\nPlease reply with your **in‑game name** (IGN).")
            self.booking_sessions[interaction.user.id] = {"purchase_id": purchase_id, "step": "ign"}
            await interaction.followup.send("📨 Check your DM to continue.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("❌ I can't DM you. Enable DMs and try again.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not isinstance(message.channel, discord.DMChannel):
            return
        user_id = message.author.id
        if user_id not in self.booking_sessions:
            return

        session = self.booking_sessions[user_id]

        if session["step"] == "ign":
            ign = message.content.strip()
            if len(ign) > 32:
                await message.channel.send("❌ IGN too long (max 32). Try again:")
                return
            session["ign"] = ign
            session["step"] = "time"
            await message.channel.send("✅ Got it. Now provide **ride time** in UTC: `YYYY-MM-DD HH:MM`")

        elif session["step"] == "time":
            print(f"[DEBUG TIME] Received: '{message.content}'")
            try:
                dt = datetime.strptime(message.content.strip(), "%Y-%m-%d %H:%M")
                dt = dt.replace(tzinfo=timezone.utc)
                if dt < datetime.now(timezone.utc):
                    await message.channel.send("❌ Time must be in future. Try again:")
                    return
                print("[DEBUG TIME] Parsed successfully:", dt)
            except ValueError as e:
                print(f"[DEBUG TIME] Parse error: {e}")
                await message.channel.send("❌ Invalid format. Use `YYYY-MM-DD HH:MM`")
                return

            # Save booking
            purchase_id = session["purchase_id"]
            ign = session["ign"]
            print(f"[DEBUG TIME] Purchase ID: {purchase_id}, IGN: {ign}")

            try:
                dt_naive = dt.replace(tzinfo=None)  # remove timezone
                async with self.bot.db_pool.acquire() as conn:
                    async with conn.transaction():
                        await conn.execute("""
                            INSERT INTO carriage_bookings (user_id, ign, ride_time, purchase_id)
                            VALUES ($1, $2, $3, $4)
                        """, str(user_id), ign, dt_naive, purchase_id)
                        await conn.execute("UPDATE user_purchases SET used = TRUE WHERE purchase_id = $1", purchase_id)
                print("[DEBUG TIME] Database insert/update succeeded")
            except Exception as e:
                print(f"[DEBUG TIME] Database error: {e}")
                await message.channel.send("❌ Database error – booking failed. Please contact an admin.")
                return

            # Remove role
            try:
                async with self.bot.db_pool.acquire() as conn:
                    row = await conn.fetchrow("""
                        SELECT si.role_id, si.guild_id
                        FROM shop_items si
                        JOIN user_purchases up ON up.item_id = si.item_id
                        WHERE up.purchase_id = $1
                    """, purchase_id)
                print(f"[DEBUG TIME] Role row: {row}")
            except Exception as e:
                print(f"[DEBUG TIME] Role fetch error: {e}")
                row = None

            if row:
                guild = self.bot.get_guild(row['guild_id'])
                if guild:
                    member = guild.get_member(user_id)
                    if member:
                        role = guild.get_role(row['role_id'])
                        if role:
                            try:
                                await member.remove_roles(role, reason="Carriage used")
                                print("[DEBUG TIME] Role removed")
                            except Exception as e:
                                print(f"[DEBUG TIME] Role removal error: {e}")

            # Confirm to user
            embed = discord.Embed(title="✅ Schedule Confirmed!", color=discord.Color.green())
            embed.description = f"**IGN:** {ign}\n**Ride Time:** <t:{int(dt.timestamp())}:F>\n\nYour ride has been scheduled. Please wait for confirmation."
            await message.channel.send(embed=embed)
            print("[DEBUG TIME] Confirmation sent")

            # Notify admins
            if row and (guild := self.bot.get_guild(row['guild_id'])):
                log_channel = discord.utils.get(guild.text_channels, name="carriage-logs")
                if log_channel:
                    try:
                        log_embed = discord.Embed(title="🚂 New Carriage Booking", color=discord.Color.blue())
                        log_embed.add_field(name="User", value=f"{member.mention} (`{user_id}`)" if member else f"`{user_id}`")
                        log_embed.add_field(name="IGN", value=ign)
                        log_embed.add_field(name="Ride Time", value=f"<t:{int(dt.timestamp())}:F>")
                        log_embed.add_field(name="Purchase ID", value=str(purchase_id))
                        if member:
                            log_embed.set_thumbnail(url=member.display_avatar.url)
                        await log_channel.send(embed=log_embed)
                        print("[DEBUG TIME] Admin log sent")
                    except Exception as e:
                        print(f"[DEBUG TIME] Admin log error: {e}")

            # Clean up session
            del self.booking_sessions[user_id]
            print("[DEBUG TIME] Session deleted")


# END SECRET SHOP =================


    # SHOP LOGS

    async def send_shop_log(self, guild: discord.Guild, user: discord.Member, item_name: str, price: int, balance: int):
        """Send a purchase log to the #shop-logs channel if it exists."""
        # Find channel named "shop logs" (case‑insensitive)
        channel = discord.utils.get(guild.text_channels, name="shop logs")
        if not channel:
            return  # No log channel found

        embed = discord.Embed(
            title="🛒 **Shop Purchase**",
            color=discord.Color.green(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="👤 User", value=f"{user.mention} (`{user.id}`)", inline=False)
        embed.add_field(name="📦 Item", value=item_name, inline=True)
        embed.add_field(name="💎 Price", value=f"{price} gems", inline=True)
        embed.add_field(name="💰 New Balance", value=f"{balance} gems", inline=True)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="Shop Logger")

        try:
            await channel.send(embed=embed)
        except Exception as e:
            print(f"⚠️ Failed to send shop log: {e}")

    #END SHOP LOGS


    #

    @commands.command(name='myweapon')
    async def my_weapon(self, ctx):
        user_id = str(ctx.author.id)
        async with self.bot.db_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    COALESCE(si.name, uw.generated_name) as name,
                    COALESCE(si.image_url, uw.image_url) as image_url,
                    si.description,
                    uw.attack
                FROM user_weapons uw
                LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                WHERE uw.user_id = $1
                ORDER BY uw.purchased_at DESC
                LIMIT 1
            """, user_id)

        if not row:
            await ctx.send("You don't own any weapons yet.")
            return

        desc = row['description'] or "No description available."
        wrapped_desc = "\n".join(textwrap.wrap(desc, width=45))

        embed = discord.Embed(
            title=f"{row['name']} (+{row['attack']} ATK)",
            description=f"*{wrapped_desc}*",
            color=discord.Color.red()
        )
        if row['image_url']:
            embed.set_image(url=row['image_url'])

        await ctx.send(embed=embed)


    # ADMIN COMMANDS (unchanged, but we need to add guild_id to shop_items? Not now.)
    # -------------------------------------------------------------------------
    @commands.group(name='shopadmin', invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def shop_admin(self, ctx):
        embed = discord.Embed(
            title="🛠️ Shop Admin",
            description=(
                "`!!shopadmin add role <name> <price> <role_id>`\n"
                "`!!shopadmin add color <name> <price> <role_id> <hex>`\n"
                "`!!shopadmin remove <item_id>`\n"
                "`!!shopadmin edit price <item_id> <new_price>`\n"
                "`!!shopadmin edit description <item_id> <new_desc>`"
            ),
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

    @shop_admin.command(name='add')
    @commands.has_permissions(administrator=True)
    async def shop_add(self, ctx, item_type: str, name: str, price: int, role_id: int = None, color_hex: str = None, image_url: str = None):
        item_type = item_type.lower()
        if item_type not in ('role', 'color', 'weapon'):
            await ctx.send("❌ Type must be `role`, `color`, or `weapon`.")
            return

        # Validate based on type
        if item_type == 'role':
            if not role_id:
                await ctx.send("❌ For role items, you must provide a role_id.")
                return
            # Validate role exists
            role = ctx.guild.get_role(role_id)
            if not role:
                await ctx.send(f"❌ Role with ID `{role_id}` not found.")
                return
            description = f"Role: {role.name}"
        elif item_type == 'color':
            if not role_id or not color_hex:
                await ctx.send("❌ For color items, you must provide role_id and color_hex.")
                return
            if not color_hex.startswith('#') or len(color_hex) != 7:
                await ctx.send("❌ Color hex must be `#RRGGBB`.")
                return
            role = ctx.guild.get_role(role_id)
            if not role:
                await ctx.send(f"❌ Role with ID `{role_id}` not found.")
                return
            description = f"Color: {color_hex}"
        else:  # weapon
            role_id = None
            color_hex = None
            description = f"Weapon: {name}"

        # Optional image URL validation
        if image_url and not (image_url.startswith('http://') or image_url.startswith('https://')):
            await ctx.send("❌ Image URL must start with `http://` or `https://`.")
            return

        async with self.bot.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO shop_items (name, description, price, type, role_id, color_hex, guild_id, image_url)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, name, description, price, item_type, role_id, color_hex, ctx.guild.id, image_url)

        await ctx.send(f"✅ Added **{name}** ({item_type}) for **{price} gems**.")

    @shop_admin.command(name='addweapon')
    @commands.has_permissions(administrator=True)
    async def shop_add_weapon(self, ctx, name: str, price: int, description: str, image_url: str = None):
        """Add a weapon with custom description.
        Usage: !!shopadmin addweapon "Dragon Slayer" 500 "A legendary blade forged in dragon fire." [image_url]
    """
        # Optional image URL validation
        if image_url and not (image_url.startswith('http://') or image_url.startswith('https://')):
            await ctx.send("❌ Image URL must start with `http://` or `https://`.")
            return

        async with self.bot.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO shop_items (name, description, price, type, role_id, color_hex, guild_id, image_url)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, name, description, price, 'weapon', None, None, ctx.guild.id, image_url)

        await ctx.send(f"✅ Added weapon **{name}** for **{price} gems** with custom description.")

    @shop_admin.command(name='remove')
    @commands.has_permissions(administrator=True)
    async def shop_remove(self, ctx, item_id: int):
        async with self.bot.db_pool.acquire() as conn:
            result = await conn.execute("DELETE FROM shop_items WHERE item_id = $1", item_id)
        if result == "DELETE 0":
            await ctx.send(f"❌ Item #{item_id} not found.")
        else:
            await ctx.send(f"✅ Removed item #{item_id}.")

    @shop_admin.command(name='edit')
    @commands.has_permissions(administrator=True)
    async def shop_edit(self, ctx, item_id: int, field: str, *, value: str):
        field = field.lower()
        if field not in ('price', 'description'):
            await ctx.send("❌ Can only edit `price` or `description`.")
            return

        async with self.bot.db_pool.acquire() as conn:
            if field == 'price':
                try:
                    val = int(value)
                    if val <= 0:
                        await ctx.send("❌ Price must be positive.")
                        return
                    await conn.execute("UPDATE shop_items SET price = $1 WHERE item_id = $2", val, item_id)
                except ValueError:
                    await ctx.send("❌ Price must be a number.")
                    return
            else:
                await conn.execute("UPDATE shop_items SET description = $1 WHERE item_id = $2", value, item_id)

        await ctx.send(f"✅ Updated `{field}` of item #{item_id}.")

    @commands.command(name='adminweapons')
    @commands.has_permissions(administrator=True)
    async def admin_list_weapons(self, ctx, user: discord.Member):
        """List all weapons owned by a user with their IDs (admin only)."""
        user_id = str(user.id)
        async with self.bot.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT uw.id, si.name, uw.attack
                FROM user_weapons uw
                JOIN shop_items si ON uw.weapon_item_id = si.item_id
                WHERE uw.user_id = $1
                ORDER BY uw.purchased_at DESC
            """, user_id)

        if not rows:
            await ctx.send(f"{user.display_name} doesn't own any weapons.")
            return

        embed = discord.Embed(
            title=f"🗡️ {user.display_name}'s Weapons",
            color=discord.Color.blue()
        )
        for row in rows:
            embed.add_field(
                name=f"ID: {row['id']}",
                value=f"**{row['name']}** (+{row['attack']} ATK)",
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(name='adminremoveweapon')
    @commands.has_permissions(administrator=True)
    async def admin_remove_weapon(self, ctx, weapon_id: int):
        """Remove a weapon by its unique ID and allow re-purchase (admin only)."""
        async with self.bot.db_pool.acquire() as conn:
            # Get weapon info and linked purchase_id
            row = await conn.fetchrow("""
                SELECT uw.id, si.name, uw.user_id, uw.purchase_id
                FROM user_weapons uw
                JOIN shop_items si ON uw.weapon_item_id = si.item_id
                WHERE uw.id = $1
            """, weapon_id)

            if not row:
                await ctx.send(f"❌ Weapon with ID `{weapon_id}` not found.")
                return

            # Delete the weapon
            await conn.execute("DELETE FROM user_weapons WHERE id = $1", weapon_id)

            # Mark the associated purchase as used so the item can be bought again
            if row['purchase_id']:
                await conn.execute("UPDATE user_purchases SET used = TRUE WHERE purchase_id = $1", row['purchase_id'])

        user = self.bot.get_user(int(row['user_id']))
        user_mention = user.mention if user else f"User ID {row['user_id']}"

        embed = discord.Embed(
            title="✅ Weapon Removed",
            description=f"Removed **{row['name']}** (ID: {weapon_id}) from {user_mention}. They can now buy it again.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)


# TEMPORARY COMMAND

    @commands.command(name='clear_carriage')
    @commands.has_permissions(administrator=True)
    async def clear_carriage(self, ctx, user: discord.Member = None):
        """Admin only: Clear the Treasure Carriage purchase for a user (mark as used)."""
        print(f"[DEBUG] clear_carriage called by {ctx.author}")
        await ctx.send("Command received, processing...")   # temporary

        target = user or ctx.author
        user_id = str(target.id)

        # Check database connection
        if not self.bot.db_pool:
            await ctx.send("❌ Database not connected.")
            return

        async with self.bot.db_pool.acquire() as conn:
            # Find the active Treasure Carriage purchase
            row = await conn.fetchrow("""
                SELECT up.purchase_id 
                FROM user_purchases up
                JOIN shop_items si ON up.item_id = si.item_id
                WHERE up.user_id = $1 
                  AND si.name ILIKE '%treasure carriage%' 
                  AND up.used = FALSE 
                  AND up.expires_at > NOW()
                LIMIT 1
            """, user_id)

            if not row:
                await ctx.send(f"❌ No active Treasure Carriage purchase found for {target.mention}.")
                return

            purchase_id = row['purchase_id']

            # Mark as used
            await conn.execute("UPDATE user_purchases SET used = TRUE WHERE purchase_id = $1", purchase_id)

            # Remove role if still present
            guild = ctx.guild
            member = guild.get_member(target.id)
            if member:
                role_row = await conn.fetchrow("""
                    SELECT si.role_id 
                    FROM shop_items si
                    JOIN user_purchases up ON up.item_id = si.item_id
                    WHERE up.purchase_id = $1
                """, purchase_id)
                if role_row:
                    role = guild.get_role(role_row['role_id'])
                    if role and role in member.roles:
                        try:
                            await member.remove_roles(role, reason="Cleared by admin")
                        except Exception as e:
                            print(f"Role removal error: {e}")

        await ctx.send(f"✅ Cleared Treasure Carriage purchase for {target.mention}. They can now buy it again.")

# Add the shop cog to the bot
bot.add_cog(Shop(bot))


async def load_shop_persistence(bot):
    shop_cog = bot.get_cog('Shop')
    if shop_cog:
        await shop_cog.load_shop_messages()




# === RUN BOT ===
if __name__ == "__main__":
    if TOKEN:
        print("\n🚀 Starting bot...")
        bot.run(TOKEN)
    else:
        print("❌ ERROR: No TOKEN found in environment variables!")
        print("💡 Set TOKEN environment variable in Railway")

