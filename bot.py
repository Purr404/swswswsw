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
        self.load_json_data()
        print(f"\n📊 Database System Status:")
        print(f"  - DATABASE_URL exists: {'YES' if DATABASE_URL else 'NO'}")
        print(f"  - asyncpg available: {'YES' if ASYNCPG_AVAILABLE else 'NO'}")
        
    def load_json_data(self):
        """Load data from JSON file"""
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    self.json_data = json.load(f)
                print(f"  - JSON users loaded: {len(self.json_data)}")
            else:
                self.json_data = {}
                print(f"  - JSON file: Not found (will create)")
        except Exception as e:
            print(f"  - JSON load error: {e}")
            self.json_data = {}
    
    def save_json_data(self):
        """Save data to JSON file"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.json_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving JSON: {e}")
            return False
    
    async def smart_connect(self):
        """Smart database connection that tries multiple approaches"""
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
                    
                    # Create table
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS user_gems (
                            user_id TEXT PRIMARY KEY,
                            gems INTEGER DEFAULT 0,
                            total_earned INTEGER DEFAULT 0,
                            daily_streak INTEGER DEFAULT 0,
                            last_daily TIMESTAMP WITH TIME ZONE,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
        print("💡 Possible solutions:")
        print("  1. Wait 2 minutes for Railway PostgreSQL to be ready")
        print("  2. Restart both bot and PostgreSQL services")
        print("  3. Check DATABASE_URL format in Railway Variables")
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
                # Try to update existing user
                result = await conn.execute('''
                    UPDATE user_gems 
                    SET gems = gems + $2,
                        total_earned = total_earned + $2,
                        updated_at = NOW()
                    WHERE user_id = $1
                    RETURNING gems
                ''', user_id, gems)
                
                if result == 'UPDATE 0':
                    # User doesn't exist, create them
                    await conn.execute('''
                        INSERT INTO user_gems (user_id, gems, total_earned)
                        VALUES ($1, $2, $2)
                    ''', user_id, gems)
                    new_balance = gems
                else:
                    # Parse the new balance from result
                    # Result format: "UPDATE 1"
                    new_balance = gems  # We'll fetch it properly
                    
                    # Fetch actual balance
                    balance = await conn.fetchval(
                        'SELECT gems FROM user_gems WHERE user_id = $1',
                        user_id
                    )
                    new_balance = balance
                
                print(f"✅ [DB] Added {gems} gems to {user_id} (Balance: {new_balance})")
                return {"gems": gems, "balance": new_balance}
                
        except Exception as e:
            print(f"❌ Database error in add_gems: {e}")
            print("🔄 Falling back to JSON...")
            return await self._json_add_gems(user_id, gems, reason)
    
    async def _json_add_gems(self, user_id: str, gems: int, reason: str = ""):
        """JSON version"""
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
        
        self.save_json_data()
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
        """JSON version"""
        if user_id in self.json_data:
            return {
                "gems": self.json_data[user_id].get("gems", 0),
                "total_earned": self.json_data[user_id].get("total_earned", 0)
            }
        return {"gems": 0, "total_earned": 0}
    
    async def can_claim_daily(self, user_id: str):
        """Check if user can claim daily reward (24-hour cooldown)"""
        if self.using_database:
            return await self._db_can_claim_daily(user_id)
        else:
            return await self._json_can_claim_daily(user_id)
    
    async def _db_can_claim_daily(self, user_id: str):
        """Database version of can_claim_daily"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    'SELECT last_daily FROM user_gems WHERE user_id = $1',
                    user_id
                )
                
                if not row or not row['last_daily']:
                    return True  # Never claimed before
                
                last_claim = row['last_daily']
                now = datetime.now(timezone.utc)
                
                # Check if 24 hours have passed
                time_diff = now - last_claim
                return time_diff.total_seconds() >= 86400  # 24 hours in seconds
                
        except Exception as e:
            print(f"❌ Database error in can_claim_daily: {e}")
            return await self._json_can_claim_daily(user_id)
    
    async def _json_can_claim_daily(self, user_id: str):
        """JSON version of can_claim_daily"""
        if user_id not in self.json_data or not self.json_data[user_id].get("last_daily"):
            return True
        
        try:
            last_claim_str = self.json_data[user_id]["last_daily"]
            # Parse the date string
            if isinstance(last_claim_str, str):
                if 'T' in last_claim_str:
                    last_claim = datetime.fromisoformat(last_claim_str.replace('Z', '+00:00'))
                else:
                    last_claim = datetime.strptime(last_claim_str, "%Y-%m-%d %H:%M:%S.%f")
            else:
                return True
                
            # Make timezone-aware if not already
            if last_claim.tzinfo is None:
                last_claim = last_claim.replace(tzinfo=timezone.utc)
                
            now = datetime.now(timezone.utc)
            time_diff = now - last_claim
            return time_diff.total_seconds() >= 86400  # 24 hours in seconds
        except Exception as e:
            print(f"JSON can_claim_daily error: {e}")
            return True
    
    async def get_user(self, user_id: str):
        """Get user data including daily streak"""
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
                            "last_daily": row['last_daily']
                        }
                    else:
                        return {
                            "gems": 0,
                            "total_earned": 0,
                            "daily_streak": 0,
                            "last_daily": None
                        }
                        
            except Exception as e:
                print(f"❌ Database error in get_user: {e}")
                return await self._json_get_user(user_id)
        else:
            return await self._json_get_user(user_id)
    
    async def _json_get_user(self, user_id: str):
        """JSON version of get_user"""
        if user_id not in self.json_data:
            return {
                "gems": 0,
                "total_earned": 0,
                "daily_streak": 0,
                "last_daily": None
            }
        return {
            "gems": self.json_data[user_id].get("gems", 0),
            "total_earned": self.json_data[user_id].get("total_earned", 0),
            "daily_streak": self.json_data[user_id].get("daily_streak", 0),
            "last_daily": self.json_data[user_id].get("last_daily")
        }
    
    async def claim_daily(self, user_id: str):
        """Claim daily reward with streak bonus - FIXED VERSION"""
        now = datetime.now(timezone.utc)
        
        if self.using_database:
            return await self._db_claim_daily(user_id, now)
        else:
            return await self._json_claim_daily(user_id, now)
    
    async def _db_claim_daily(self, user_id: str, now: datetime):
        """Database version of claim_daily - FIXED"""
        try:
            async with self.pool.acquire() as conn:
                # Get current user data in a transaction
                async with conn.transaction():
                    # Get or create user with locking
                    row = await conn.fetchrow('''
                        SELECT gems, daily_streak, last_daily 
                        FROM user_gems 
                        WHERE user_id = $1
                        FOR UPDATE
                    ''', user_id)
                    
                    # Calculate streak
                    if not row or not row['last_daily']:
                        new_streak = 1
                    else:
                        last_claim = row['last_daily']
                        # Check if claimed today (within last 24 hours)
                        time_diff = now - last_claim
                        
                        if time_diff.total_seconds() < 86400:  # Less than 24 hours
                            # Shouldn't happen if can_claim_daily was called, but double-check
                            return {"gems": 0, "streak": row['daily_streak'] or 0, "error": "Already claimed today"}
                        
                        # Check if claimed yesterday (streak continues)
                        days_diff = (now.date() - last_claim.date()).days
                        
                        if days_diff == 1:
                            new_streak = (row['daily_streak'] or 0) + 1
                        else:
                            new_streak = 1
                    
                    # Calculate daily reward
                    base_gems = random.randint(1, 100)
                    streak_bonus = min(new_streak * 0.1, 1.0)  # Max 100% bonus
                    bonus_gems = int(base_gems * streak_bonus)
                    total_gems = base_gems + bonus_gems
                    
                    # Update user
                    if not row:
                        # New user
                        await conn.execute('''
                            INSERT INTO user_gems (user_id, gems, total_earned, daily_streak, last_daily)
                            VALUES ($1, $2, $2, $3, $4)
                        ''', user_id, total_gems, new_streak, now)
                    else:
                        # Existing user
                        await conn.execute('''
                            UPDATE user_gems 
                            SET gems = gems + $2,
                                total_earned = total_earned + $2,
                                daily_streak = $3,
                                last_daily = $4,
                                updated_at = NOW()
                            WHERE user_id = $1
                        ''', user_id, total_gems, new_streak, now)
                    
                    return {"gems": total_gems, "streak": new_streak}
                    
        except Exception as e:
            print(f"❌ Database error in claim_daily: {e}")
            return await self._json_claim_daily(user_id, now)
    
    async def _json_claim_daily(self, user_id: str, now: datetime):
        """JSON version of claim_daily - FIXED"""
        # Get user data
        if user_id not in self.json_data:
            user_data = {
                "gems": 0,
                "total_earned": 0,
                "daily_streak": 0,
                "last_daily": None
            }
        else:
            user_data = self.json_data[user_id].copy()
        
        # Calculate streak
        if not user_data.get("last_daily"):
            new_streak = 1
        else:
            try:
                last_claim_str = user_data["last_daily"]
                if isinstance(last_claim_str, str):
                    if 'T' in last_claim_str:
                        last_claim = datetime.fromisoformat(last_claim_str.replace('Z', '+00:00'))
                    else:
                        last_claim = datetime.strptime(last_claim_str, "%Y-%m-%d %H:%M:%S.%f")
                else:
                    last_claim = last_claim_str
                
                # Make timezone-aware
                if last_claim.tzinfo is None:
                    last_claim = last_claim.replace(tzinfo=timezone.utc)
                
                # Check if claimed within 24 hours (shouldn't happen but double-check)
                time_diff = now - last_claim
                if time_diff.total_seconds() < 86400:
                    return {"gems": 0, "streak": user_data.get("daily_streak", 0), "error": "Already claimed today"}
                
                # Check days difference for streak
                days_diff = (now.date() - last_claim.date()).days
                
                if days_diff == 1:
                    new_streak = user_data.get("daily_streak", 0) + 1
                else:
                    new_streak = 1
            except:
                new_streak = 1
        
        # Calculate daily reward
        base_gems = random.randint(1, 100)
        streak_bonus = min(new_streak * 0.1, 1.0)  # Max 100% bonus
        bonus_gems = int(base_gems * streak_bonus)
        total_gems = base_gems + bonus_gems
        
        # Update user data
        if user_id not in self.json_data:
            self.json_data[user_id] = {}
        
        self.json_data[user_id].update({
            "gems": user_data.get("gems", 0) + total_gems,
            "total_earned": user_data.get("total_earned", 0) + total_gems,
            "daily_streak": new_streak,
            "last_daily": now.isoformat()
        })
        
        self.save_json_data()
        
        return {"gems": total_gems, "streak": new_streak}
    
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
        """JSON version of get_leaderboard"""
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
        """Deduct gems from a user"""
        if self.using_database:
            try:
                async with self.pool.acquire() as conn:
                    # Check if user has enough gems
                    row = await conn.fetchrow(
                        'SELECT gems FROM user_gems WHERE user_id = $1',
                        user_id
                    )
                    
                    if not row or row['gems'] < gems:
                        return False
                    
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
                return await self._json_deduct_gems(user_id, gems)
        else:
            return await self._json_deduct_gems(user_id, gems)
    
    async def _json_deduct_gems(self, user_id: str, gems: int, reason: str = ""):
        """JSON version of deduct_gems"""
        if user_id not in self.json_data or self.json_data[user_id].get("gems", 0) < gems:
            return False
        
        self.json_data[user_id]["gems"] -= gems
        self.save_json_data()
        return True

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

# --- 5. ANNOUNCEMENT COMMANDS ---
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
        sent_message = await channel.send("@here", embed=embed)
        
        await sent_message.add_reaction("📢")
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
        
        # Load 5 questions
        self.load_questions()
    
    def load_questions(self):
        """Load 5 quiz questions with open-ended answers"""
        self.quiz_questions = [
            {
                "question": "What is the capital city of France?",
                "correct_answers": ["paris"],
                "points": 300,
                "time_limit": 15
            },
            {
                "question": "Which planet is known as the Red Planet?",
                "correct_answers": ["mars", "planet mars"],
                "points": 300,
                "time_limit": 15
            },
            {
                "question": "What is the chemical symbol for gold?",
                "correct_answers": ["au"],
                "points": 200,
                "time_limit": 15
            },
            {
                "question": "Who painted the Mona Lisa?",
                "correct_answers": ["leonardo da vinci", "da vinci", "leonardo"],
                "points": 300,
                "time_limit": 15
            },
            {
                "question": "What is the largest mammal in the world?",
                "correct_answers": ["blue whale", "whale"],
                "points": 300,
                "time_limit": 15
            },
            {
                "question": "How many continents are there on Earth?",
                "correct_answers": ["7", "seven"],
                "points": 200,
                "time_limit": 45
            }
        ]
        print(f"✅ Loaded {len(self.quiz_questions)} questions for testing")

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
                f"First question starts in **10 seconds**!"
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

            # Determine bar color based on time left
            if time_left <= 5:  # Last 5 seconds: RED
                bar_char = "🟥"  # Red square
                embed_color = discord.Color.red()
                time_field_name = f"⏰ **⏳ {time_left:02d} SECONDS LEFT - HURRY!**"
            elif time_left <= total_time * 0.5:  # Below 50%: ORANGE/YELLOW
                bar_char = "🟨"  # Yellow square
                embed_color = discord.Color.orange()
                time_field_name = f"⏰ **⏳ {time_left:02d} SECONDS LEFT**"
            else:  # Above 50%: GREEN
                bar_char = "🟩"  # Green square
                embed_color = discord.Color.green()
                time_field_name = f"⏰ **{time_left:02d} SECONDS LEFT**"
            
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
        print(f"❌ Quiz not running, ignoring answer from {user.name}")
        return False
    
    question = self.quiz_questions[self.current_question]
    answer_time = (datetime.now(timezone.utc) - self.question_start_time).seconds
    
    # Check if time's up
    if answer_time > question["time_limit"]:
        print(f"❌ Time's up for {user.name}, answer ignored")
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
        print(f"✅ New participant added: {user.display_name}")
    
    # Check if user already got this question right
    if self.participants[user_id]["answered_current"]:
        print(f"⚠️ {user.display_name} already answered this question correctly")
        return False
    
    # Check if answer is correct (case-insensitive, trim spaces)
    user_answer = answer_text.lower().strip()
    is_correct = any(correct_answer == user_answer 
                    for correct_answer in question["correct_answers"])
    
    print(f"\n=== ANSWER PROCESSING ===")
    print(f"User: {user.display_name}")
    print(f"Answer: {user_answer}")
    print(f"Correct answers: {question['correct_answers']}")
    print(f"Is correct: {is_correct}")
    print(f"Answer time: {answer_time}s")
    
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
        print(f"✅ Correct! Points awarded: {points}")
        print(f"Total score: {self.participants[user_id]['score']}")
    else:
        print(f"❌ Incorrect answer")
    
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
    
async def end_quiz(self):
    """End the entire quiz with improved leaderboard"""
    print(f"\n=== QUIZ ENDING ===")
    print(f"Quiz running: {self.quiz_running}")
    print(f"Current question: {self.current_question}")
    print(f"Total questions: {len(self.quiz_questions)}")
    print(f"Participants count: {len(self.participants)}")
    
    self.quiz_running = False
    self.countdown_task.stop()
    
    if self.question_timer:
        self.question_timer.cancel()
    
    if not self.participants:
        print("❌ No participants - sending empty quiz message")
        embed = discord.Embed(
            title="🏆 **QUIZ FINISHED!** 🏆",
            description="The quiz has ended!\n\nNo participants joined this round.",
            color=discord.Color.gold(),
            timestamp=datetime.now(timezone.utc)
        )
        await self.quiz_channel.send(embed=embed)
        
        # Reset for next quiz
        self.quiz_channel = None
        self.quiz_logs_channel = None
        self.current_question = 0
        self.participants = {}
        return
    
    # Sort participants by score
    sorted_participants = sorted(
        self.participants.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )
    
    print(f"\nSorted participants (top 3):")
    for i, (user_id, data) in enumerate(sorted_participants[:3], 1):
        print(f"  {i}. {data['name']}: {data['score']} pts")
    
    # First, send a congratulations embed
    embed = discord.Embed(
        title="🏆 **QUIZ FINISHED!** 🏆",
        description="Congratulations to all participants!\nHere are the final results:",
        color=discord.Color.gold(),
        timestamp=datetime.now(timezone.utc)
    )
    
    # Add quiz statistics
    total_questions = len(self.quiz_questions)
    total_correct = sum(p.get('correct_answers', 0) for p in self.participants.values())
    total_attempts = sum(len(p.get('answers', [])) for p in self.participants.values())
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
    
    # DISTRIBUTE REWARDS
    print(f"\n=== CALLING DISTRIBUTE_QUIZ_REWARDS ===")
    rewards_distributed = await self.distribute_quiz_rewards(sorted_participants)
    print(f"Rewards distributed count: {len(rewards_distributed)}")

    # Send rewards summary
    if rewards_distributed:
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
    else:
        print("❌ No rewards were distributed!")
        error_embed = discord.Embed(
            title="⚠️ **No Rewards Distributed**",
            description="No rewards could be distributed for this quiz.\nPlease contact an administrator.",
            color=discord.Color.red()
        )
        await self.quiz_channel.send(embed=error_embed)
    
    # Send individual DMs with rewards
    dm_count = 0
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
                    
                    balance = await self.db.get_balance(user_id)
                    dm_embed.add_field(
                        name="📊 **New Balance**",
                        value=f"💎 Total Gems: **{balance['gems']}**",
                        inline=False
                    )
                    
                    dm_embed.set_footer(text="Use !!currency to check your gems!")
                    await user_obj.send(embed=dm_embed)
                    dm_count += 1
                except:
                    pass  # User has DMs disabled
    
    print(f"✅ DMs sent to {dm_count} users")
    
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
    print("✅ Quiz reset complete")
    

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
    print(f"\n=== DISTRIBUTING QUIZ REWARDS ===")
    print(f"Total participants: {len(sorted_participants)}")
    
    rewards = {}
    total_participants = len(sorted_participants)
    
    for rank, (user_id, data) in enumerate(sorted_participants, 1):
        print(f"\nProcessing user {user_id} (Rank #{rank})")
        print(f"Username: {data['name']}")
        print(f"Score: {data['score']} points")
        print(f"Correct answers: {data.get('correct_answers', 0)}")
        
        base_gems = 50  # Participation reward
        print(f"Base participation gems: {base_gems}")
        
        # Rank-based bonuses
        if rank == 1:  # 1st place
            base_gems += 500
            print(f"1st place bonus: +500 gems")
        elif rank == 2:  # 2nd place
            base_gems += 250
            print(f"2nd place bonus: +250 gems")
        elif rank == 3:  # 3rd place
            base_gems += 125
            print(f"3rd place bonus: +125 gems")
        elif rank <= 10:  # Top 10
            base_gems += 75
            print(f"Top 10 bonus: +75 gems")
        
        # Score-based bonus: 10 gems per 100 points
        score_bonus = (data["score"] // 100) * 10
        base_gems += score_bonus
        print(f"Score bonus ({data['score']} pts): +{score_bonus} gems")
        
        # Perfect score bonus
        max_score = len(self.quiz_questions) * 300
        if data["score"] == max_score:
            base_gems += 250
            reason = f"🎯 Perfect Score! ({data['score']} pts, Rank #{rank})"
            print(f"Perfect score bonus: +250 gems")
        else:
            reason = f"🏆 Quiz Rewards ({data['score']} pts, Rank #{rank})"
        
        # Speed bonus for fast answers
        speed_bonus = self.calculate_speed_bonus(user_id)
        if speed_bonus:
            base_gems += speed_bonus
            reason += f" + ⚡{speed_bonus} speed bonus"
            print(f"Speed bonus: +{speed_bonus} gems")
        
        print(f"Total gems to award: {base_gems}")
        
        # Add gems using the SHARED database system
        try:
            result = await self.db.add_gems(
                user_id=user_id,
                gems=base_gems,
                reason=reason
            )
            print(f"Database add_gems result: {result}")
            
            rewards[user_id] = {
                "gems": base_gems,
                "rank": rank
            }
            
            # Log reward distribution
            await self.log_reward(user_id, data["name"], base_gems, rank)
            print(f"✅ Rewards logged for {data['name']}")
            
        except Exception as e:
            print(f"❌ Error adding gems to {user_id}: {e}")
    
    print(f"\n=== REWARDS DISTRIBUTION COMPLETE ===")
    print(f"Total rewards distributed: {len(rewards)}")
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
        embed.add_field(name="📊 Total", value=f"{gems} gems", inline=True)
        
        await self.quiz_logs_channel.send(embed=embed)

# === CREATE QUIZ SYSTEM WITH SHARED DATABASE ===
quiz_system = QuizSystem(bot)

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
    can_claim = await db.can_claim_daily(user_id)
    if can_claim:
        embed.add_field(
            name="🎁 Daily Reward",
            value="Available now!",
            inline=True
        )
    else:
        # Calculate time until next daily
        user_data = await db.get_user(user_id)
        if user_data["last_daily"]:
            try:
                last_claim = user_data["last_daily"]
                if isinstance(last_claim, str):
                    if 'T' in last_claim:
                        last_claim = datetime.fromisoformat(last_claim.replace('Z', '+00:00'))
                    else:
                        last_claim = datetime.strptime(last_claim, "%Y-%m-%d %H:%M:%S.%f")
                
                # Make timezone-aware
                if last_claim.tzinfo is None:
                    last_claim = last_claim.replace(tzinfo=timezone.utc)
                
                next_claim = last_claim + timedelta(hours=24)
                now = datetime.now(timezone.utc)
                
                if next_claim > now:
                    time_left = next_claim - now
                    hours = time_left.seconds // 3600
                    minutes = (time_left.seconds % 3600) // 60
                    seconds = time_left.seconds % 60
                    
                    embed.add_field(
                        name="⏰ Next Daily",
                        value=f"{hours}h {minutes}m {seconds}s",
                        inline=True
                    )
            except:
                embed.add_field(
                    name="🎁 Daily Reward",
                    value="Available now!",
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
    """Claim daily reward (1-100 gems + streak bonus) - FIXED VERSION"""
    user_id = str(ctx.author.id)
    
    # Check if user can claim daily
    can_claim = await db.can_claim_daily(user_id)
    
    if not can_claim:
        # User CANNOT claim daily - show cooldown
        user = await db.get_user(user_id)
        if user["last_daily"]:
            try:
                # Parse last claim time
                last_claim = user["last_daily"]
                if isinstance(last_claim, str):
                    if 'T' in last_claim:
                        last_claim = datetime.fromisoformat(last_claim.replace('Z', '+00:00'))
                    else:
                        last_claim = datetime.strptime(last_claim, "%Y-%m-%d %H:%M:%S.%f")
                
                # Make timezone-aware
                if last_claim.tzinfo is None:
                    last_claim = last_claim.replace(tzinfo=timezone.utc)

                now = datetime.now(timezone.utc)
                next_claim = last_claim + timedelta(hours=24)

                if next_claim > now:
                    time_left = next_claim - now
                    hours_left = time_left.seconds // 3600
                    minutes_left = (time_left.seconds % 3600) // 60
                    seconds_left = time_left.seconds % 60

                    await ctx.send(
                        f"⏰ **Daily Reward Cooldown!**\n"
                        f"You can claim again in **{hours_left}h {minutes_left}m {seconds_left}s**\n"
                        f"Current streak: **{user['daily_streak']} days** 🔥",
                        delete_after=15
                    )
                else:
                    # If time is up, let them claim
                    pass
            except Exception as e:
                print(f"Error calculating time: {e}")
                # If error, let them claim anyway
                pass
        
        # Send message and return (don't give reward)
        return
    
    # User CAN claim daily - give them the reward
    transaction = await db.claim_daily(user_id)
    
    # Check if claim was successful
    if "error" in transaction:
        await ctx.send(f"❌ {transaction['error']}", delete_after=10)
        return
    
    gems_earned = transaction["gems"]
    user = await db.get_user(user_id)

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

    if user['daily_streak'] >= 7:
        embed.add_field(
            name="🏆 Weekly Bonus!",
            value="You've maintained a 7-day streak! 🎉",
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
                       "• `!!announce` - Announcement management\n\n"
                       "**Message System**\n"
                       "• `!!say` - Send messages\n\n"
                       "**Quiz System**\n"
                       "• `!!quiz` - Quiz management\n\n"
                       "**Currency System**\n"
                       "• `!!currency` - Check your gems\n"
                       "• `!!currency daily` - Claim daily reward\n"
                       "• `!!currency leaderboard` - Top earners\n"
                       "• `!!currency transfer` - Transfer gems\n"
                       "• `!!currency stats` - Detailed stats\n\n"
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
@commands.has_permissions(manage_messages=True)  # ONLY STAFF CAN USE THIS
async def add_gems(ctx, member: discord.Member, amount: int):
    """Add gems to a user's account (Staff only)"""
    user_id = str(member.id)
    
    # Use the shared database system
    result = await db.add_gems(
        user_id=user_id,
        gems=amount,
        reason=f"Added by staff {ctx.author.name}"
    )
    
    if result:
        balance = await db.get_balance(user_id)
        await ctx.send(f"✅ Added **{amount} gems** to {member.mention}\nNew balance: **{balance['gems']} gems**")
    else:
        await ctx.send("❌ Failed to add gems")

@bot.command(name="balance")
async def balance_cmd(ctx, member: discord.Member = None):
    """Check your balance or another user's balance"""
    target = member or ctx.author
    user_id = str(target.id)
    balance = await db.get_balance(user_id)
    
    embed = discord.Embed(
        title=f"💰 {target.display_name}'s Balance",
        description=f"**💎 {balance['gems']} gems**\nTotal earned: **{balance['total_earned']} gems**",
        color=discord.Color.gold()
    )
    
    if db.using_database:
        embed.set_footer(text="💾 Stored in PostgreSQL Database - Persistent")
    else:
        embed.set_footer(text="📄 Stored in JSON File - May reset on redeploy")
    
    await ctx.send(embed=embed)

# TEST REWARDS COMMAND ----
@bot.command(name="testrewards")
@commands.has_permissions(manage_messages=True)
async def test_rewards(ctx):
    """Test quiz reward distribution manually"""
    # Simulate some participants
    quiz_system.participants = {
        str(ctx.author.id): {
            "name": ctx.author.display_name,
            "score": 1500,  # High score
            "correct_answers": 5,
            "answers": [{"correct": True, "points": 300, "time": 5} for _ in range(5)]
        }
    }
    
    # Sort participants
    sorted_participants = sorted(
        quiz_system.participants.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )
    
    # Distribute rewards
    rewards = await quiz_system.distribute_quiz_rewards(sorted_participants)  # Fixed typo here!
    
    # Check user's new balance
    user_id = str(ctx.author.id)
    balance = await db.get_balance(user_id)
    
    embed = discord.Embed(
        title="✅ **Test Rewards Distributed!**",
        description=f"Test completed successfully!",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="💰 Rewards Given",
        value=f"💎 **{rewards.get(user_id, {}).get('gems', 0)} gems**",
        inline=False
    )
    
    embed.add_field(
        name="📊 New Balance",
        value=f"💎 **{balance['gems']} gems**",
        inline=False
    )
    
    await ctx.send(embed=embed)

#END TEST REWARDS CMD -----

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
    
    # Connect to database - FIXED: use smart_connect() not connect()
    print("\n🔌 Connecting to database...")
    connected = await db.smart_connect()  # CHANGED FROM connect() TO smart_connect()
    
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