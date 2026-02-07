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

# Check for discord-components
print("\n=== CHECKING DISCORD-COMPONENTS ===")
try:
    import discord_components
    from discord_components import DiscordComponents, Components, Button, Select, SelectOption
    COMPONENTS_AVAILABLE = True
    print("✅ discord-components is installed!")
except ImportError as e:
    print(f"❌ discord-components not available: {e}")
    print("💡 Add 'discord-components>=2.1.2' to requirements.txt")
    COMPONENTS_AVAILABLE = False
    discord_components = None

# ... rest of your imports and asyncpg setup ...

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
        print(f"\n📊 Database System Status:")
        print(f"  - DATABASE_URL exists: {'YES' if DATABASE_URL else 'NO'}")
        print(f"  - asyncpg available: {'YES' if ASYNCPG_AVAILABLE else 'NO'}")
        
    async def smart_connect(self):
        """Connect to PostgreSQL database"""
        if not DATABASE_URL:
            print("❌ No DATABASE_URL found!")
            print("💡 Set DATABASE_URL environment variable in Railway")
            return False
        
        if not ASYNCPG_AVAILABLE:
            print("❌ asyncpg not available!")
            print("💡 Add asyncpg to requirements.txt: asyncpg>=0.29.0")
            return False
        
        print("\n🔌 Connecting to PostgreSQL...")
        
        try:
            self.pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=1,
                max_size=3,
                ssl='require',
                command_timeout=30
            )
            
            # Test connection
            async with self.pool.acquire() as conn:
                result = await conn.fetchval('SELECT 1')
                print(f"    ✅ Connection test: {result}")
                
                # Create main gems table
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
                
                # Create shop tables
                await self.create_shop_tables()
            
            self.using_database = True
            print("🎉 PostgreSQL Database Connected Successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {type(e).__name__}: {str(e)[:200]}")
            print("💡 Check your DATABASE_URL in Railway Variables")
            return False
    
    async def create_shop_tables(self):
        """Create shop tables in PostgreSQL"""
        try:
            async with self.pool.acquire() as conn:
                # Create shop_purchases table
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS shop_purchases (
                        id SERIAL PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        item_id INTEGER NOT NULL,
                        item_name TEXT NOT NULL,
                        item_type TEXT NOT NULL,
                        price INTEGER NOT NULL,
                        purchased_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                ''')
                
                # Create shop_active_items table
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS shop_active_items (
                        id SERIAL PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        item_id INTEGER NOT NULL,
                        item_type TEXT NOT NULL,
                        role_id TEXT,
                        expires_at TIMESTAMP WITH TIME ZONE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                ''')
                
                # Create indexes
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_shop_purchases_user ON shop_purchases(user_id)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_shop_purchases_time ON shop_purchases(purchased_at DESC)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_shop_active_items_user ON shop_active_items(user_id)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_shop_active_items_expires ON shop_active_items(expires_at)')
                
                print("✅ Shop tables created successfully!")
                return True
                
        except Exception as e:
            print(f"❌ Error creating shop tables: {e}")
            return False
    
    # === GEM MANAGEMENT ===
    async def add_gems(self, user_id: str, gems: int, reason: str = ""):
        """Add gems to a user"""
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
                    # Get new balance
                    row = await conn.fetchrow(
                        'SELECT gems FROM user_gems WHERE user_id = $1',
                        user_id
                    )
                    new_balance = row['gems'] if row else gems
                
                print(f"✅ [DB] Added {gems} gems to {user_id} (Balance: {new_balance})")
                return {"gems": gems, "balance": new_balance}
                
        except Exception as e:
            print(f"❌ Database error in add_gems: {e}")
            raise
    
    async def get_balance(self, user_id: str):
        """Get user balance"""
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
            return {"gems": 0, "total_earned": 0}
    
    async def deduct_gems(self, user_id: str, gems: int, reason: str = ""):
        """Deduct gems from a user"""
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
            return False
    
    # === DAILY REWARD SYSTEM ===
    async def can_claim_daily(self, user_id: str):
        """Check if user can claim daily reward"""
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
                return time_diff.total_seconds() >= 86400
                
        except Exception as e:
            print(f"❌ Database error in can_claim_daily: {e}")
            return True
    
    async def get_user(self, user_id: str):
        """Get user data"""
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
            return {
                "gems": 0,
                "total_earned": 0,
                "daily_streak": 0,
                "last_daily": None
            }
    
    async def claim_daily(self, user_id: str):
        """Claim daily reward"""
        now = datetime.now(timezone.utc)
        
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    # Get user data with lock
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
                        time_diff = now - last_claim
                        
                        if time_diff.total_seconds() < 86400:
                            return {"gems": 0, "streak": row['daily_streak'] or 0, "error": "Already claimed today"}
                        
                        days_diff = (now.date() - last_claim.date()).days
                        
                        if days_diff == 1:
                            new_streak = (row['daily_streak'] or 0) + 1
                        else:
                            new_streak = 1
                    
                    # Calculate daily reward
                    base_gems = random.randint(1, 100)
                    streak_bonus = min(new_streak * 0.1, 1.0)
                    bonus_gems = int(base_gems * streak_bonus)
                    total_gems = base_gems + bonus_gems
                    
                    # Update user
                    if not row:
                        await conn.execute('''
                            INSERT INTO user_gems (user_id, gems, total_earned, daily_streak, last_daily)
                            VALUES ($1, $2, $2, $3, $4)
                        ''', user_id, total_gems, new_streak, now)
                    else:
                        await conn.execute('''
                            UPDATE user_gems 
                            SET gems = gems + $2,
                                total_earned = total_earned + $2,
                                daily_streak = $3,
                                last_daily = $4,
                                updated_at = NOW()
                            WHERE user_id = $1
                        ''', user_id, total_gems, new_streak, now)
                    
                    return {
                        "gems": total_gems, 
                        "streak": new_streak,
                        "base_gems": base_gems,
                        "bonus_gems": bonus_gems
                    }
                    
        except Exception as e:
            print(f"❌ Database error in claim_daily: {e}")
            return {"gems": 0, "streak": 0, "error": "Database error"}
    
    # === LEADERBOARD ===
    async def get_leaderboard(self, limit: int = 10):
        """Get gems leaderboard"""
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
            return []
    
    # === SHOP SYSTEM ===
    async def shop_get_items(self):
        """Get all shop items (SIMPLIFIED - no boosters)"""
        shop_items = [
            {
                "id": 1,
                "name": "🛡️ Role Color Change",
                "description": "Change your role color for 7 days",
                "price": 500,
                "type": "role_color",
                "duration_days": 7
            },
            {
                "id": 2,
                "name": "🎨 Custom Nickname Color",
                "description": "Set a custom color for your nickname",
                "price": 300,
                "type": "nickname_color",
                "duration_days": 30
            },
            {
                "id": 3,
                "name": "🌟 Special Role",
                "description": "Get a special 'Gem Master' role",
                "price": 1000,
                "type": "special_role",
                "duration_days": 30
            },
            {
                "id": 4,
                "name": "🎁 Mystery Box",
                "description": "Random reward between 50-500 gems",
                "price": 250,
                "type": "mystery_box",
                "min_gems": 50,
                "max_gems": 500
            }
        ]
        return shop_items
    
    async def shop_purchase(self, user_id: str, item_id: int):
        """Purchase an item"""
        items = await self.shop_get_items()
        item = next((i for i in items if i["id"] == item_id), None)
        
        if not item:
            return {"success": False, "error": "Item not found"}
        
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    # Check balance
                    row = await conn.fetchrow(
                        'SELECT gems FROM user_gems WHERE user_id = $1',
                        user_id
                    )
                    
                    if not row or row['gems'] < item["price"]:
                        return {"success": False, "error": "Not enough gems"}
                    
                    # Deduct gems
                    await conn.execute('''
                        UPDATE user_gems 
                        SET gems = gems - $2,
                            updated_at = NOW()
                        WHERE user_id = $1
                    ''', user_id, item["price"])
                    
                    # Get new balance
                    new_balance_row = await conn.fetchrow(
                        'SELECT gems FROM user_gems WHERE user_id = $1',
                        user_id
                    )
                    new_balance = new_balance_row['gems'] if new_balance_row else 0
                    
                    # Record purchase
                    await conn.execute('''
                        INSERT INTO shop_purchases 
                        (user_id, item_id, item_name, item_type, price)
                        VALUES ($1, $2, $3, $4, $5)
                    ''', user_id, item["id"], item["name"], item["type"], item["price"])
                    
                    # For timed items, add to active_items
                    if "duration_days" in item:
                        expires_at = datetime.now(timezone.utc) + timedelta(days=item["duration_days"])
                        await conn.execute('''
                            INSERT INTO shop_active_items 
                            (user_id, item_id, item_type, expires_at)
                            VALUES ($1, $2, $3, $4)
                        ''', user_id, item["id"], item["type"], expires_at)
                    
                    return {
                        "success": True, 
                        "item": item,
                        "new_balance": new_balance
                    }
                    
        except Exception as e:
            print(f"❌ Database error in shop_purchase: {e}")
            return {"success": False, "error": "Database error"}
    
    async def shop_get_user_purchases(self, user_id: str, limit: int = 20):
        """Get user's purchase history"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch('''
                    SELECT item_id, item_name, item_type, price, purchased_at
                    FROM shop_purchases
                    WHERE user_id = $1
                    ORDER BY purchased_at DESC
                    LIMIT $2
                ''', user_id, limit)
                
                purchases = []
                for row in rows:
                    purchases.append({
                        "item_id": row['item_id'],
                        "item_name": row['item_name'],
                        "item_type": row['item_type'],
                        "price": row['price'],
                        "purchased_at": row['purchased_at'].isoformat() if row['purchased_at'] else None
                    })
                
                return purchases
                
        except Exception as e:
            print(f"❌ Database error getting purchases: {e}")
            return []
    
    async def shop_cleanup_expired(self):
        """Clean up expired items"""
        try:
            async with self.pool.acquire() as conn:
                # Delete expired active items
                deleted = await conn.execute('''
                    DELETE FROM shop_active_items 
                    WHERE expires_at < NOW()
                ''')
                
                if deleted != 'DELETE 0':
                    print(f"✅ Cleaned up {deleted.split()[1]} expired shop items")
        except Exception as e:
            print(f"❌ Error cleaning up shop items: {e}")

# === CREATE SHARED DATABASE SYSTEM INSTANCE ===
db = DatabaseSystem()

# === SHOP SYSTEM CLASS ===
class ShopSystem:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        print("✅ ShopSystem created")
    
    async def process_purchase(self, user, item_id, guild):
        """Process item purchase"""
        # Get item info
        items = await self.db.shop_get_items()
        item = next((i for i in items if i["id"] == item_id), None)
        
        if not item:
            return {"success": False, "message": "❌ Item not found!"}
        
        # Purchase item from database
        result = await self.db.shop_purchase(str(user.id), item_id)
        
        if not result["success"]:
            return {"success": False, "message": f"❌ {result['error']}"}
        
        # Process item based on type
        item_result = await self._process_item_type(user, item, guild)
        
        return {
            "success": True,
            "message": f"✅ **Purchase Successful!**\nYou bought: **{item['name']}**\n{item_result['message']}\nNew balance: **💎 {result['new_balance']:,} gems**",
            "item": item,
            "item_result": item_result
        }
    
    async def _process_item_type(self, user, item, guild):
        """Process different item types"""
        if item["type"] == "role_color":
            return await self._process_role_color(user, item, guild)
        elif item["type"] == "nickname_color":
            return await self._process_nickname_color(user, item, guild)
        elif item["type"] == "special_role":
            return await self._process_special_role(user, item, guild)
        elif item["type"] == "mystery_box":
            return await self._process_mystery_box(user, item)
        
        return {"success": False, "message": "Item type not implemented"}
    
    async def _process_role_color(self, user, item, guild):
        """Process role color purchase"""
        try:
            # Create or get custom role
            role_name = f"Gem-{user.name[:20]}"
            role = discord.utils.get(guild.roles, name=role_name)
            
            if not role:
                # Create new role
                role = await guild.create_role(
                    name=role_name,
                    color=discord.Color.random(),
                    reason=f"Gem shop purchase by {user.name}"
                )
                print(f"✅ Created new role {role_name} for {user.name}")
            else:
                # Update existing role color
                await role.edit(color=discord.Color.random())
                print(f"✅ Updated role color for {user.name}")
            
            # Add role to user (removing old ones if any)
            gem_roles = [r for r in user.roles if r.name.startswith("Gem-")]
            for gem_role in gem_roles:
                if gem_role != role:
                    await user.remove_roles(gem_role, reason="Removing old gem role")
            
            # Add new role
            await user.add_roles(role, reason="Gem shop purchase")
            
            return {
                "success": True,
                "message": f"🎨 Your custom role **{role.name}** has been set with color **#{role.color.value:06x}**!\nIt will expire in {item['duration_days']} days."
            }
        except Exception as e:
            print(f"Error in role color processing: {e}")
            return {"success": False, "message": f"Failed to set role: {str(e)[:100]}"}
    
    async def _process_nickname_color(self, user, item, guild):
        """Process nickname color purchase"""
        try:
            # Generate random color
            color = discord.Color.random()
            
            embed = discord.Embed(
                title="🎨 **Nickname Color Applied!**",
                description=f"Your nickname now has a custom color for {item['duration_days']} days!",
                color=color
            )
            
            embed.add_field(
                name="Color Preview",
                value=f"Hex: `#{color.value:06x}`",
                inline=True
            )
            
            return {
                "success": True,
                "message": f"🎨 Custom nickname color set for {item['duration_days']} days!",
                "embed": embed
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to set color: {str(e)[:100]}"}
    
    async def _process_special_role(self, user, item, guild):
        """Process special role purchase"""
        try:
            # Find or create "Gem Master" role
            role_name = "💎 Gem Master"
            role = discord.utils.get(guild.roles, name=role_name)
            
            if not role:
                # Create the role
                role = await guild.create_role(
                    name=role_name,
                    color=discord.Color.gold(),
                    hoist=True,
                    mentionable=True,
                    reason="Gem shop special role"
                )
            
            # Add role to user
            await user.add_roles(role, reason="Gem shop purchase")
            
            return {
                "success": True,
                "message": f"🌟 You now have the **{role_name}** role for {item['duration_days']} days!"
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to set role: {str(e)[:100]}"}
    
    async def _process_mystery_box(self, user, item):
        """Process mystery box purchase"""
        try:
            # Random gems between min and max
            gems_won = random.randint(item["min_gems"], item["max_gems"])
            
            # Add gems to user using database
            await self.db.add_gems(
                str(user.id),
                gems=gems_won,
                reason="Mystery Box Prize"
            )
            
            # Determine rarity
            if gems_won >= 400:
                rarity = "✨ **LEGENDARY!**"
                color = 0xFFD700  # Gold
            elif gems_won >= 250:
                rarity = "⚡ **RARE!**"
                color = 0x9B59B6  # Purple
            elif gems_won >= 150:
                rarity = "🌟 **UNCOMMON!**"
                color = 0x3498DB  # Blue
            else:
                rarity = "🎁 **COMMON**"
                color = 0x2ECC71  # Green
            
            # Create embed for result
            embed = discord.Embed(
                title="🎁 **MYSTERY BOX OPENED!**",
                description=f"{rarity}\nYou won: **💎 {gems_won:,} gems**!",
                color=color
            )
            
            return {
                "success": True,
                "message": f"🎁 **Mystery Box Opened!**\n{rarity}\nYou won: **💎 {gems_won:,} gems**!",
                "embed": embed
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to open box: {str(e)[:100]}"}

# === CREATE SHOP SYSTEM INSTANCE ===
shop_system = ShopSystem(bot, db)
print("✅ ShopSystem instance created")


# === BEAUTIFUL VISUAL SHOP WITH BUTTONS ===
class VisualShopUI:
    def __init__(self, bot, db, shop_system):
        self.bot = bot
        self.db = db
        self.shop_system = shop_system
        print("✅ VisualShopUI created")
    
    async def setup_shop_channel(self, guild):
        """Setup shop channel with beautiful button interface"""
        try:
            # Initialize discord-components
            DiscordComponents(self.bot)
            
            # Find or create shop channel
            shop_channel = discord.utils.get(guild.text_channels, name="shops")
            if not shop_channel:
                shop_channel = await guild.create_text_channel(
                    "shops",
                    topic="🛒 Interactive Gem Shop - Click buttons to shop!",
                    reason="Auto-created shop channel"
                )
                print(f"✅ Created shop channel: #{shop_channel.name}")
            
            # Clear channel
            try:
                await shop_channel.purge(limit=100)
            except:
                pass
            
            # Create BEAUTIFUL shop interface
            embed = discord.Embed(
                title="🛒 **WELCOME TO THE GEM SHOP!** 🛒",
                description=(
                    "**✨ CLICK BUTTONS TO SHOP! ✨**\n\n"
                    "🌟 **No commands needed!** Just click buttons!\n"
                    "💎 **Use your gems** to unlock amazing items!\n"
                    "🎮 **Interactive shopping experience!**\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**🎯 HOW TO USE:**\n"
                    "1. Click 📦 to browse items\n"
                    "2. Click buttons to view details\n"
                    "3. Click BUY to purchase\n"
                    "4. Get items instantly!\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                ),
                color=discord.Color.gold()
            )
            
            embed.add_field(
                name="💎 **EARN MORE GEMS**",
                value=(
                    "• Click 🎰 for daily rewards\n"
                    "• Join quizzes (`!!quiz`)\n"
                    "• Win events and giveaways\n"
                    "• Purchase mystery boxes"
                ),
                inline=False
            )
            
            embed.set_footer(text="🛒 Interactive Shop • Powered by discord-components")
            
            # Create buttons
            buttons = [
                Button(style=3, label="📦 BROWSE ITEMS", custom_id="browse_items", emoji="📦"),
                Button(style=2, label="💰 MY BALANCE", custom_id="check_balance", emoji="💰"),
                Button(style=2, label="📜 HISTORY", custom_id="view_history", emoji="📜"),
                Button(style=1, label="🎰 DAILY", custom_id="daily_reward", emoji="🎰"),
                Button(style=2, label="❓ HELP", custom_id="shop_help", emoji="❓")
            ]
            
            # Send message with buttons
            message = await shop_channel.send(
                embed=embed,
                components=[buttons]
            )
            
            print(f"✅ Beautiful shop setup complete in #{shop_channel.name}")
            return shop_channel
            
        except Exception as e:
            print(f"❌ Error setting up shop: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def show_shop_items(self, user):
        """Show shop items with buttons"""
        try:
            items = await self.db.shop_get_items()
            user_id = str(user.id)
            balance = await self.db.get_balance(user_id)
            
            embed = discord.Embed(
                title="📦 **SHOP ITEMS**",
                description=f"**Your Balance:** 💎 **{balance['gems']:,} gems**\n\n"
                           "**Click an item to view details:**",
                color=discord.Color.blue()
            )
            
            # Create item buttons
            buttons = []
            for i, item in enumerate(items[:4]):  # Max 4 items per row
                emoji = "🛒"
                if item["type"] == "role_color":
                    emoji = "🎨"
                elif item["type"] == "nickname_color":
                    emoji = "🛡️"
                elif item["type"] == "special_role":
                    emoji = "🌟"
                elif item["type"] == "mystery_box":
                    emoji = "🎁"
                
                buttons.append(
                    Button(
                        style=2,
                        label=f"{item['name']} - 💎{item['price']}",
                        custom_id=f"view_item_{item['id']}",
                        emoji=emoji
                    )
                )
            
            # Add navigation buttons
            nav_buttons = [
                Button(style=1, label="⬅️ BACK", custom_id="back_to_shop", emoji="⬅️"),
                Button(style=3, label="🛒 MAIN SHOP", custom_id="main_shop", emoji="🛒")
            ]
            
            # Add items to embed
            for item in items:
                embed.add_field(
                    name=f"{item['name']}",
                    value=f"💎 **{item['price']:,}** • {item['description']}",
                    inline=False
                )
            
            return embed, [buttons, nav_buttons]
            
        except Exception as e:
            print(f"❌ Error showing items: {e}")
            return None, None
    
    async def show_item_details(self, user, item_id):
        """Show item details with buy button"""
        try:
            items = await self.db.shop_get_items()
            item = next((i for i in items if i["id"] == item_id), None)
            
            if not item:
                return None, None
            
            user_id = str(user.id)
            balance = await self.db.get_balance(user_id)
            can_afford = balance["gems"] >= item["price"]
            
            embed = discord.Embed(
                title=f"🛒 **{item['name']}**",
                color=discord.Color.gold() if can_afford else discord.Color.red()
            )
            
            # Item details
            embed.description = f"**{item['description']}**\n\n"
            
            if item["type"] == "role_color":
                embed.description += "🎨 **Get a custom role with unique color!**"
            elif item["type"] == "nickname_color":
                embed.description += "🛡️ **Custom color for your nickname!**"
            elif item["type"] == "special_role":
                embed.description += "🌟 **Exclusive 'Gem Master' role!**"
            elif item["type"] == "mystery_box":
                embed.description += f"🎁 **Win {item['min_gems']}-{item['max_gems']} gems!**"
            
            # Price and balance
            embed.add_field(name="💰 **PRICE**", value=f"💎 **{item['price']:,}**", inline=True)
            embed.add_field(name="💰 **YOUR BALANCE**", value=f"💎 **{balance['gems']:,}**", inline=True)
            embed.add_field(name="💳 **CAN AFFORD**", value="✅ **YES**" if can_afford else "❌ **NO**", inline=True)
            
            # Create buttons
            buy_button = Button(
                style=3 if can_afford else 2,
                label="✅ BUY NOW" if can_afford else "❌ NEED MORE GEMS",
                custom_id=f"buy_item_{item_id}",
                emoji="💳",
                disabled=not can_afford
            )
            
            back_button = Button(style=2, label="⬅️ BACK TO ITEMS", custom_id="back_to_items", emoji="⬅️")
            shop_button = Button(style=1, label="🛒 MAIN SHOP", custom_id="main_shop", emoji="🛒")
            
            return embed, [[buy_button], [back_button, shop_button]]
            
        except Exception as e:
            print(f"❌ Error showing item details: {e}")
            return None, None

# === CREATE SHOP UI INSTANCE ===
if COMPONENTS_AVAILABLE:
    visual_shop = VisualShopUI(bot, db, shop_system)
    print("✅ VisualShopUI instance created")
else:
    print("❌ discord-components not available, shop will use commands")
    visual_shop = None

# === BUTTON INTERACTION HANDLER ===
@bot.event
async def on_button_click(interaction):
    """Handle button clicks"""
    try:
        user = interaction.user
        custom_id = interaction.custom_id
        
        # Defer response
        await interaction.respond(type=6)  # Defer
        
        if custom_id == "browse_items":
            embed, components = await visual_shop.show_shop_items(user)
            if embed and components:
                await interaction.send(embed=embed, components=components)
        
        elif custom_id.startswith("view_item_"):
            item_id = int(custom_id.split("_")[-1])
            embed, components = await visual_shop.show_item_details(user, item_id)
            if embed and components:
                await interaction.send(embed=embed, components=components)
        
        elif custom_id.startswith("buy_item_"):
            item_id = int(custom_id.split("_")[-1])
            result = await shop_system.process_purchase(user, item_id, user.guild)
            
            if result["success"]:
                embed = discord.Embed(
                    title="✅ **PURCHASE SUCCESSFUL!**",
                    description=f"**{result['item']['name']}** purchased!\n{result['message']}",
                    color=discord.Color.green()
                )
                await interaction.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="❌ **PURCHASE FAILED**",
                    description=result.get("message", "Unknown error"),
                    color=discord.Color.red()
                )
                await interaction.send(embed=embed)
        
        elif custom_id == "check_balance":
            balance = await db.get_balance(str(user.id))
            embed = discord.Embed(
                title="💰 **YOUR BALANCE**",
                description=f"💎 **{balance['gems']:,} gems**\nTotal earned: **{balance['total_earned']:,}**",
                color=discord.Color.gold()
            )
            await interaction.send(embed=embed)
        
        elif custom_id == "daily_reward":
            embed = discord.Embed(
                title="🎰 **DAILY REWARD**",
                description="Use `!!currency daily` to claim your daily reward!",
                color=discord.Color.blue()
            )
            await interaction.send(embed=embed)
        
        elif custom_id == "shop_help":
            embed = discord.Embed(
                title="❓ **SHOP HELP**",
                description=(
                    "**How to use the shop:**\n\n"
                    "📦 **Browse Items** - View all items\n"
                    "💰 **My Balance** - Check your gems\n"
                    "📜 **History** - View purchases\n"
                    "🎰 **Daily** - Claim daily reward\n\n"
                    "**To buy:** Click an item, then click BUY!"
                ),
                color=discord.Color.blue()
            )
            await interaction.send(embed=embed)
        
        elif custom_id in ["back_to_shop", "main_shop"]:
            # Recreate main shop
            channel = interaction.channel
            embed = discord.Embed(
                title="🛒 **BACK TO SHOP** 🛒",
                description="Welcome back to the gem shop!",
                color=discord.Color.gold()
            )
            
            buttons = [
                Button(style=3, label="📦 BROWSE ITEMS", custom_id="browse_items", emoji="📦"),
                Button(style=2, label="💰 MY BALANCE", custom_id="check_balance", emoji="💰"),
                Button(style=1, label="🎰 DAILY", custom_id="daily_reward", emoji="🎰"),
                Button(style=2, label="❓ HELP", custom_id="shop_help", emoji="❓")
            ]
            
            await interaction.send(embed=embed, components=[buttons])
        
        elif custom_id == "back_to_items":
            embed, components = await visual_shop.show_shop_items(user)
            if embed and components:
                await interaction.send(embed=embed, components=components)
    
    except Exception as e:
        print(f"Button click error: {e}")
        await interaction.send("❌ An error occurred. Please try again.")


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
        
        # Double-check we have a valid question
        if self.current_question < 0 or self.current_question >= len(self.quiz_questions):
            print(f"❌ Invalid current_question: {self.current_question}")
            await self.end_quiz()
            return
        
        question = self.quiz_questions[self.current_question]
        self.question_start_time = datetime.now(timezone.utc)
        
        # Initial progress bar (full) - GREEN for full time
        progress_bar = "🟩" * 20
        
        # Create question embed
        embed = discord.Embed(
            title=f"❓ **Question {self.current_question + 1}/{len(self.quiz_questions)}**",
            description=question["question"],
            color=discord.Color.green()
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
        
        # Check if we have a valid current question
        if self.current_question < 0 or self.current_question >= len(self.quiz_questions):
            print(f"❌ Invalid current_question in countdown: {self.current_question}")
            self.countdown_task.stop()
            return
        
        try:
            elapsed = (datetime.now(timezone.utc) - self.question_start_time).seconds
            time_left = total_time - elapsed
            
            if time_left <= 0:
                self.countdown_task.stop()
                return
            
            # Calculate progress percentage
            progress_percentage = time_left / total_time
            progress = int(progress_percentage * 20)
            
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
            
            # Create progress bar with appropriate color
            progress_bar = bar_char * progress + "⬜" * (20 - progress)
            
            # Update embed
            embed = self.question_message.embeds[0]
            
            # Update embed color
            embed.color = embed_color
            
            # Find and update the time field
            for i, field in enumerate(embed.fields):
                if "⏰" in field.name:
                    embed.set_field_at(
                        i,
                        name=time_field_name,
                        value=f"```\n{progress_bar}\n{time_left:02d} seconds\n```\n"
                              f"**Max Points:** {self.quiz_questions[self.current_question]['points']} ⭐",
                        inline=False
                    )
                    break
            
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
        
        # Check if we're between questions or quiz has ended
        if self.current_question >= len(self.quiz_questions):
            print(f"❌ Quiz has ended, ignoring answer from {user.name}")
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
        
        # Wait 2 seconds
        await asyncio.sleep(2)
        
        # SHOW LIVE LEADERBOARD WITH ALL USERS
        leaderboard_embed = await self.create_live_leaderboard()
        leaderboard_message = await self.quiz_channel.send(embed=leaderboard_embed)
        
        # Countdown to next question with leaderboard showing
        countdown_seconds = 3
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
    
    # Show storage type
    if db.using_database:
        embed.set_footer(text="💾 Stored in PostgreSQL Database")
    else:
        embed.set_footer(text="📄 Stored in JSON File (Fallback)")
    
    await ctx.send(embed=embed)

# CURRENCY DAILY---------
@currency_group.command(name="daily")
async def daily_reward(ctx):
    """Claim daily reward"""
    user_id = str(ctx.author.id)
    
    # Check if user can claim daily
    can_claim = await db.can_claim_daily(user_id)
    
    if not can_claim:
        # Show cooldown message
        user = await db.get_user(user_id)
        
        if user["last_daily"]:
            try:
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

                    embed = discord.Embed(
                        title="⏰ **Daily Reward Cooldown!**",
                        description=f"Please wait before claiming your daily reward again.",
                        color=discord.Color.orange()
                    )
                    
                    embed.add_field(
                        name="⏳ Time Remaining",
                        value=f"**{hours_left}h {minutes_left}m {seconds_left}s**",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="🔥 Current Streak",
                        value=f"**{user.get('daily_streak', 0)} days**",
                        inline=True
                    )
                    
                    embed.set_footer(text="Come back later to continue your streak!")
                    await ctx.send(embed=embed, delete_after=30)
                else:
                    pass
            except Exception as e:
                print(f"Error calculating time: {e}")
        
        return
    
    # Claim daily reward
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

    # Show detailed breakdown
    embed.add_field(
        name="💰 Reward Breakdown",
        value=f"**Base:** {transaction.get('base_gems', '?')} gems\n"
              f"**Streak Bonus:** +{transaction.get('bonus_gems', '?')} gems",
        inline=False
    )

    embed.add_field(
        name="💎 Total Earned",
        value=f"**+{gems_earned} gems**",
        inline=True
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

    # Show next claim time
    next_claim_time = datetime.now(timezone.utc) + timedelta(hours=24)
    embed.add_field(
        name="⏰ Next Daily Available",
        value=f"<t:{int(next_claim_time.timestamp())}:R>",
        inline=False
    )

    embed.set_footer(text="Come back tomorrow for more gems!")
    await ctx.send(embed=embed)

# --- ANSWER DETECTION ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Check for quiz answers (any text answer)
    if (quiz_system.quiz_running and 
        message.channel == quiz_system.quiz_channel and
        quiz_system.current_question < len(quiz_system.quiz_questions)):  # ADD THIS CHECK
        
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
                       "**Quiz System**\n"
                       "• `!!quiz` - Quiz management\n\n"
                       "**Currency System**\n"
                       "• `!!currency` - Check your gems\n"
                       "• `!!currency daily` - Claim daily reward\n\n"
                       "**Utility**\n"
                       "• `!!ping` - Check bot latency\n"
                       "• `!!help <command>` - Get command help",
            color=0x5865F2
        )
        await ctx.send(embed=embed)

# === SIMPLE BOT COMMANDS ===
@bot.command(name="swswswsw")
async def ping(ctx):
    """Check if bot is alive"""
    await ctx.send("Meooow~")

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

# === WORKING SETUPSHOP COMMAND ===
@bot.command(name="setupshop")
@commands.has_permissions(administrator=True)
async def setup_shop(ctx):
    """Setup the visual shop channel (Admin only)"""
    if not COMPONENTS_AVAILABLE:
        embed = discord.Embed(
            title="❌ **MISSING DEPENDENCY**",
            description=(
                "**discord-components** is not installed!\n\n"
                "💡 **Add this to requirements.txt:**\n"
                "```\ndiscord-components>=2.1.2\n```\n"
                "Then redeploy your bot on Railway."
            ),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    await ctx.send("🛒 Setting up beautiful visual shop...")
    
    shop_channel = await visual_shop.setup_shop_channel(ctx.guild)
    
    if shop_channel:
        embed = discord.Embed(
            title="✅ **VISUAL SHOP READY!**",
            description=(
                f"The shop is now live in {shop_channel.mention}!\n\n"
                "**✨ FEATURES:**\n"
                "• Beautiful button interface\n"
                "• Click to browse items\n"
                "• One-click purchases\n"
                "• No commands needed!\n\n"
                "**🎯 HOW IT WORKS:**\n"
                "1. Visit the shop channel\n"
                "2. Click 📦 to browse\n"
                "3. Click an item to view\n"
                "4. Click BUY to purchase\n"
                "5. Get items instantly!"
            ),
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Failed to setup shop channel!")

# ... rest of your bot code ...
# === BOT STARTUP ===
@bot.event
async def on_ready():
    print(f"\n✅ {bot.user} is online!")
    
    # Connect to PostgreSQL ONLY
    print("\n🔌 Connecting to PostgreSQL Database...")
    connected = await db.smart_connect()
    
    if connected:
        print("🎉 PostgreSQL Database Connected Successfully!")
        print("✅ All data stored in PostgreSQL")
        print("🛒 Shop system: READY")
    else:
        print("❌ FATAL: Could not connect to PostgreSQL!")
        return
    
    # Setup visual shop in first available guild
    if bot.guilds and UI_AVAILABLE and visual_shop is not None:
        guild = bot.guilds[0]
        print(f"\n🛒 Setting up shop in '{guild.name}'...")
        
        # Find existing shop channel or create it
        shop_channel = discord.utils.get(guild.text_channels, name="shops")
        if not shop_channel:
            await visual_shop.setup_shop_channel(guild)
        else:
            print(f"✅ Shop channel already exists: #{shop_channel.name}")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Visual Shop • Click & Buy!"
        )
    )
    print("\n🤖 Bot is ready!")
    print("🛒 Visual shop is available in #shops channel")
    print("📚 Commands:")
    print("  • !!setupshop - Setup/refresh shop interface")
    print("  • !!quiz - Quiz system")
    print("  • !!currency - Gem management")

# === BUTTON INTERACTION HANDLER ===
@bot.event
async def on_interaction(interaction):
    """Handle button interactions"""
    if not hasattr(interaction, 'custom_id'):
        return
    
    if not UI_AVAILABLE or visual_shop is None:
        return
    
    custom_id = interaction.custom_id
    
    # Defer the response (important for buttons)
    try:
        await interaction.defer(ephemeral=True)
    except:
        pass
    
    user = interaction.user
    
    try:
        # Handle different button actions
        if custom_id == "browse_items":
            await interaction.send("📦 Browse items feature coming soon!", ephemeral=True)
            
        elif custom_id == "check_balance":
            await interaction.send("💰 Balance check coming soon!", ephemeral=True)
                
        elif custom_id == "view_history":
            await interaction.send("📜 Purchase history coming soon!", ephemeral=True)
                
        elif custom_id == "daily_reward":
            await interaction.send("🎰 Use `!!currency daily` to claim your daily reward!", ephemeral=True)
            
        elif custom_id == "shop_help":
            help_embed = discord.Embed(
                title="❓ **SHOP HELP**",
                description="**How to use the shop:**\n\n"
                           "🛒 **Browse Items** - View all available items\n"
                           "💰 **My Balance** - Check your gem balance\n"
                           "📜 **My Purchases** - View purchase history\n"
                           "🎰 **Daily Reward** - Claim daily gems\n\n"
                           "**How it works:**\n"
                           "1. Click 'BROWSE ITEMS'\n"
                           "2. Select an item number\n"
                           "3. View item details\n"
                           "4. Click 'BUY NOW' if you have enough gems\n"
                           "5. Receive your item instantly!",
                color=discord.Color.blue()
            )
            await interaction.send(embed=help_embed, ephemeral=True)
            
    except Exception as e:
        print(f"Button interaction error: {e}")
        await interaction.send("❌ An error occurred. Please try again.", ephemeral=True)

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