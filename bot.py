import os
import sys
import json
import asyncio
import random
from datetime import datetime, timezone, timedelta
# ULTIMATE ASYNCPG INSTALLER
import subprocess
import sys
import os

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

# === SIMPLE BUT EFFECTIVE DATABASE SYSTEM ===
class SmartDatabaseSystem:
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

# Create database system
db = SmartDatabaseSystem()

# --- SIMPLE QUIZ SYSTEM ---
class QuizSystem:
    def __init__(self, bot):
        self.bot = bot
        self.currency = db
        self.quiz_running = False
        print("✅ QuizSystem initialized")
    
    async def distribute_quiz_rewards(self, participants):
        """Simple reward distribution"""
        rewards = {}
        for user_id, data in participants.items():
            # Simple fixed reward for testing
            gems = 100
            await self.currency.add_gems(user_id, gems, "Quiz reward")
            rewards[user_id] = {"gems": gems}
        return rewards

quiz_system = QuizSystem(bot)

# === EMERGENCY FIX COMMANDS ===
@bot.command(name="emergencyfix")
async def emergency_fix(ctx):
    """Emergency database fix"""
    import subprocess
    import sys
    
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
    
    # Step 3: Test connection
    if DATABASE_URL and ASYNCPG_AVAILABLE:
        try:
            import asyncpg
            conn = await asyncpg.connect(DATABASE_URL, timeout=10)
            steps.append("✅ Direct connection successful!")
            await conn.close()
        except Exception as e:
            steps.append(f"❌ Connection failed: {type(e).__name__}")
            steps.append(f"   Error: {str(e)[:100]}")
    
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

@bot.command(name="testdb")
async def test_db(ctx):
    """Test database connection"""
    user_id = str(ctx.author.id)
    
    # Try to add gems
    result = await db.add_gems(user_id, 10, "Database test")
    
    if isinstance(result, dict):
        balance = await db.get_balance(user_id)
        
        if db.using_database:
            await ctx.send(f"✅ **DATABASE WORKING!**\nAdded 10 gems\nNew balance: **{balance['gems']} gems**\nStorage: **PostgreSQL**")
        else:
            await ctx.send(f"⚠️ **Using JSON Fallback**\nAdded 10 gems\nNew balance: **{balance['gems']} gems**\nStorage: **JSON File**\n*Data may reset on redeploy*")
    else:
        await ctx.send("❌ **Test failed completely**")

@bot.command(name="checkenv")
async def check_env(ctx):
    """Check all database environment variables"""
    import os
    
    db_vars = []
    for key in sorted(os.environ.keys()):
        if any(word in key.upper() for word in ['DB', 'DATABASE', 'POSTGRES', 'PG', 'SQL', 'URL', 'HOST', 'PORT', 'USER', 'PASS']):
            value = os.environ[key]
            if 'PASS' in key.upper() or 'PASSWORD' in key.upper():
                db_vars.append(f"`{key}`: `*****`")
            else:
                db_vars.append(f"`{key}`: `{value}`")
    
    if db_vars:
        await ctx.send("**Database Environment Variables:**\n" + "\n".join(db_vars[:10]))  # First 10
    else:
        await ctx.send("❌ No database environment variables found!")

# === SIMPLE BOT COMMANDS ===
@bot.command(name="ping")
async def ping(ctx):
    """Check if bot is alive"""
    await ctx.send("🏓 Pong!")

@bot.command(name="add")
async def add_gems(ctx, amount: int = 100):
    """Add gems to your account"""
    user_id = str(ctx.author.id)
    result = await db.add_gems(user_id, amount, f"Command by {ctx.author.name}")
    
    if isinstance(result, dict):
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
        embed.set_footer(text="✅ Stored in PostgreSQL - Persistent")
    else:
        embed.set_footer(text="⚠️ Stored in JSON - May reset on redeploy")
    
    await ctx.send(embed=embed)

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