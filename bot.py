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

# === CHECK FOR DISCORD-UI-COMPONENTS ===
try:
    import discord_ui
    from discord_ui import Components, Button, LinkButton, View
    UI_AVAILABLE = True
    print("✅ discord-ui-components is installed")
    print(f"✅ Version: {discord_ui.__version__ if hasattr(discord_ui, '__version__') else 'Unknown'}")
except ImportError as e:
    print(f"❌ discord-ui-components import failed: {e}")
    UI_AVAILABLE = False
except Exception as e:
    print(f"⚠️ Other error with discord-ui-components: {e}")
    UI_AVAILABLE = False

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
            # Removed: streak_booster and transfer_pass
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

# --- 2. Store user selections ---
user_selections = {}

# === CHECK FOR DISCORD-UI-COMPONENTS ===
try:
    import discord_ui
    from discord_ui import Components, Button, LinkButton, View
    UI_AVAILABLE = True
    print("✅ discord-ui-components is installed")
    print(f"✅ Version: {discord_ui.__version__ if hasattr(discord_ui, '__version__') else 'Unknown'}")
except ImportError as e:
    print(f"❌ discord-ui-components import failed: {e}")
    UI_AVAILABLE = False
except Exception as e:
    print(f"⚠️ Other error with discord-ui-components: {e}")
    UI_AVAILABLE = False

# === VISUAL SHOP UI WITH BUTTONS ===
class VisualShopUI:
    def __init__(self, bot, db, shop_system):
        self.bot = bot
        self.db = db
        self.shop_system = shop_system
        self.shop_message_id = None
        self.shop_channel_id = None
        self.current_page = {}
        print("✅ VisualShopUI created")
    
    async def setup_shop_channel(self, guild):
        """Setup the shop channel with visual interface"""
        try:
            # Find or create shop channel
            shop_channel = discord.utils.get(guild.text_channels, name="shops")
            if not shop_channel:
                try:
                    shop_channel = await guild.create_text_channel(
                        "shops",
                        topic="🎮 Interactive Gem Shop - Browse and buy items with gems!",
                        reason="Auto-created shop channel"
                    )
                    print(f"✅ Created shop channel: #{shop_channel.name}")
                except Exception as e:
                    print(f"❌ Failed to create shop channel: {e}")
                    return None
            
            self.shop_channel_id = shop_channel.id
            
            # Clear existing messages in shop channel
            try:
                await shop_channel.purge(limit=100)
                print("✅ Cleared shop channel")
            except:
                pass
            
            # Create welcome embed
            welcome_embed = discord.Embed(
                title="🛒 **WELCOME TO THE GEM SHOP** 🛒",
                description=(
                    "**Browse, Click, Buy!**\n\n"
                    "🌟 **No commands needed!** Just click buttons below.\n"
                    "💎 **Use your gems** to unlock special items!\n"
                    "🎯 **Click 'BROWSE ITEMS' to get started!**\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "💡 **How it works:**\n"
                    "1. Click BROWSE ITEMS\n"
                    "2. Click item numbers to view details\n"
                    "3. Click BUY to purchase\n"
                    "4. Get your item instantly!\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                ),
                color=discord.Color.gold()
            )
            
            # Add info about earning gems
            welcome_embed.add_field(
                name="💎 **EARN MORE GEMS**",
                value=(
                    "• Join quizzes (`!!quiz`)\n"
                    "• Claim daily rewards (`!!currency daily`)\n"
                    "• Win events and giveaways\n"
                    "• Purchase mystery boxes"
                ),
                inline=False
            )
            
            welcome_embed.set_footer(text="🛒 Interactive Shop • Click buttons to shop!")
            
            # Create buttons row
            components = Components()
            
            # Main shop buttons
            main_row = [
                Button.custom("📦 BROWSE ITEMS", "browse_items", style=3, emoji="📦"),
                Button.custom("💰 MY BALANCE", "check_balance", style=2, emoji="💰"),
                Button.custom("📜 MY PURCHASES", "view_history", style=2, emoji="📜"),
                Button.custom("🎰 DAILY REWARD", "daily_reward", style=1, emoji="🎰"),
                Button.custom("❓ HELP", "shop_help", style=2, emoji="❓")
            ]
            
            # Send welcome message with buttons
            welcome_msg = await shop_channel.send(
                embed=welcome_embed,
                components=components.add_components(*main_row)
            )
            
            # Store message ID for interaction handling
            self.shop_message_id = welcome_msg.id
            
            print(f"✅ Shop UI setup complete in #{shop_channel.name}")
            return shop_channel
            
        except Exception as e:
            print(f"❌ Error setting up shop: {e}")
            return None
    
    async def browse_items(self, user, page=0):
        """Show items browse page"""
        try:
            items = await self.db.shop_get_items()
            user_id = str(user.id)
            balance = await self.db.get_balance(user_id)
            
            # Calculate items per page (4 items per page)
            items_per_page = 4
            total_pages = (len(items) + items_per_page - 1) // items_per_page
            
            # Get items for current page
            start_idx = page * items_per_page
            end_idx = start_idx + items_per_page
            page_items = items[start_idx:end_idx]
            
            # Create browse embed
            embed = discord.Embed(
                title="📦 **BROWSE SHOP ITEMS**",
                description=f"**Your Balance:** 💎 **{balance['gems']:,} gems**\n\n"
                           f"**Page {page + 1}/{total_pages}** • Click item number to view details:",
                color=discord.Color.blue()
            )
            
            # Add items with emoji indicators
            for i, item in enumerate(page_items):
                # Get emoji based on item type
                if item["type"] == "role_color":
                    emoji = "🎨"
                    info = f"Duration: {item.get('duration_days', 7)} days"
                elif item["type"] == "nickname_color":
                    emoji = "🛡️"
                    info = f"Duration: {item.get('duration_days', 30)} days"
                elif item["type"] == "special_role":
                    emoji = "🌟"
                    info = f"Duration: {item.get('duration_days', 30)} days"
                elif item["type"] == "mystery_box":
                    emoji = "🎁"
                    info = f"Win {item.get('min_gems', 50)}-{item.get('max_gems', 500)} gems"
                else:
                    emoji = "🛒"
                    info = "Special item"
                
                # Add item to embed
                embed.add_field(
                    name=f"{emoji} **{item['name']}** - 💎 {item['price']:,}",
                    value=f"{item['description']}\n*{info}*",
                    inline=False
                )
            
            embed.set_footer(text=f"💎 Balance: {balance['gems']:,} gems • Page {page + 1}/{total_pages}")
            
            # Create buttons
            components = Components()
            
            # Item selection buttons (up to 4 items per page)
            item_buttons = []
            for i, item in enumerate(page_items):
                item_buttons.append(
                    Button.custom(
                        label=f"VIEW #{item['id']}",
                        custom_id=f"view_item_{item['id']}",
                        style=2,
                        emoji=["1️⃣", "2️⃣", "3️⃣", "4️⃣"][i]
                    )
                )
            
            # Navigation buttons
            nav_buttons = [
                Button.custom("◀️ PREV", f"browse_page_{max(0, page-1)}", style=1, disabled=(page == 0)),
                Button.custom("🛒 BACK TO SHOP", "back_to_shop", style=3),
                Button.custom("NEXT ▶️", f"browse_page_{min(total_pages-1, page+1)}", style=1, disabled=(page >= total_pages-1))
            ]
            
            return embed, components.add_components(*item_buttons, *nav_buttons)
            
        except Exception as e:
            print(f"❌ Error in browse_items: {e}")
            return None, None
    
    async def view_item_details(self, user, item_id):
        """Show detailed view of an item"""
        try:
            items = await self.db.shop_get_items()
            item = next((i for i in items if i["id"] == item_id), None)
            
            if not item:
                return None, None
            
            user_id = str(user.id)
            balance = await self.db.get_balance(user_id)
            can_afford = balance["gems"] >= item["price"]
            
            # Create detailed embed
            embed = discord.Embed(
                title=f"🛒 **{item['name']}**",
                color=discord.Color.gold() if can_afford else discord.Color.red()
            )
            
            # Add item details
            embed.description = f"**{item['description']}**\n\n"
            
            # Add item-specific details
            if item["type"] == "role_color":
                embed.description += (
                    "🎨 **What you get:**\n"
                    "• Custom role with unique color\n"
                    "• Role appears in member list\n"
                    "• Customize your identity\n\n"
                    f"⏰ **Duration:** {item.get('duration_days', 7)} days\n"
                    "🔄 **Renewable:** Purchase again to extend"
                )
                
            elif item["type"] == "nickname_color":
                embed.description += (
                    "🛡️ **What you get:**\n"
                    "• Custom color for your nickname\n"
                    "• Stand out in chat\n"
                    "• Unique identity\n\n"
                    f"⏰ **Duration:** {item.get('duration_days', 30)} days\n"
                    "🎨 **Color:** Randomly generated"
                )
                
            elif item["type"] == "special_role":
                embed.description += (
                    "🌟 **What you get:**\n"
                    "• Exclusive 'Gem Master' role\n"
                    "• Golden-colored role\n"
                    "• Special recognition\n"
                    "• Role is mentionable\n\n"
                    f"⏰ **Duration:** {item.get('duration_days', 30)} days\n"
                    "👑 **Prestige:** Shows you're a gem master!"
                )
                
            elif item["type"] == "mystery_box":
                embed.description += (
                    "🎁 **What you get:**\n"
                    "• Random amount of gems\n"
                    "• Chance to win big!\n"
                    "• Instant reward\n"
                    "• No waiting period\n\n"
                    f"💰 **Prize Range:** {item.get('min_gems', 50)}-{item.get('max_gems', 500)} gems\n"
                    "🎲 **Rarity:** Random chance for bonus!"
                )
            
            # Price and balance info
            embed.add_field(
                name="💰 **PRICE**",
                value=f"💎 **{item['price']:,} gems**",
                inline=True
            )
            
            embed.add_field(
                name="💰 **YOUR BALANCE**",
                value=f"💎 **{balance['gems']:,} gems**",
                inline=True
            )
            
            embed.add_field(
                name="💳 **CAN AFFORD**",
                value="✅ **YES**" if can_afford else "❌ **NO**",
                inline=True
            )
            
            # Create buttons
            components = Components()
            
            buy_button = Button.custom(
                label="✅ BUY NOW" if can_afford else "❌ NEED MORE GEMS",
                custom_id=f"buy_item_{item_id}",
                style=3 if can_afford else 2,
                emoji="💳",
                disabled=not can_afford
            )
            
            back_button = Button.custom(
                label="↩️ BACK TO BROWSE",
                custom_id="back_to_browse",
                style=2
            )
            
            shop_button = Button.custom(
                label="🛒 BACK TO SHOP",
                custom_id="back_to_shop",
                style=1
            )
            
            return embed, components.add_components(buy_button, back_button, shop_button)
            
        except Exception as e:
            print(f"❌ Error in view_item_details: {e}")
            return None, None
    
    async def process_purchase(self, user, item_id):
        """Process item purchase"""
        try:
            # Get item info
            items = await self.db.shop_get_items()
            item = next((i for i in items if i["id"] == item_id), None)
            
            if not item:
                return "❌ Item not found!"
            
            # Check balance first
            user_id = str(user.id)
            balance = await self.db.get_balance(user_id)
            
            if balance["gems"] < item["price"]:
                return f"❌ You need **💎 {item['price'] - balance['gems']:,} more gems** to buy this!"
            
            # Purchase item
            result = await self.shop_system.process_purchase(user, item_id, user.guild)
            
            if not result["success"]:
                return result["message"]
            
            # Success message
            success_message = (
                f"✅ **PURCHASE SUCCESSFUL!**\n\n"
                f"**Item:** {item['name']}\n"
                f"**Price:** 💎 {item['price']:,} gems\n"
                f"**New Balance:** 💎 {result.get('new_balance', 0):,} gems\n\n"
            )
            
            # Add item-specific message
            if "item_result" in result and "message" in result["item_result"]:
                success_message += f"**What you got:** {result['item_result']['message']}\n\n"
            
            success_message += "🎉 **Enjoy your purchase!**"
            
            return success_message
            
        except Exception as e:
            print(f"❌ Error in process_purchase: {e}")
            return f"❌ Error: {str(e)[:100]}"
    
    async def show_balance(self, user):
        """Show user's balance"""
        try:
            user_id = str(user.id)
            balance = await self.db.get_balance(user_id)
            user_data = await self.db.get_user(user_id)
            
            embed = discord.Embed(
                title="💰 **YOUR GEM WALLET**",
                color=discord.Color.gold()
            )
            
            embed.add_field(
                name="💎 **CURRENT BALANCE**",
                value=f"**{balance['gems']:,} gems**",
                inline=False
            )
            
            embed.add_field(
                name="📈 **TOTAL EARNED**",
                value=f"**{balance['total_earned']:,} gems** lifetime",
                inline=True
            )
            
            embed.add_field(
                name="🔥 **DAILY STREAK**",
                value=f"**{user_data.get('daily_streak', 0)} days**",
                inline=True
            )
            
            # Add earning methods
            embed.add_field(
                name="💡 **EARN MORE GEMS**",
                value=(
                    "• Click 🎰 for daily rewards\n"
                    "• Join quizzes (`!!quiz`)\n"
                    "• Participate in events\n"
                    "• Win giveaways"
                ),
                inline=False
            )
            
            return embed
            
        except Exception as e:
            print(f"❌ Error in show_balance: {e}")
            return None

# === CREATE VISUAL SHOP UI INSTANCE ===
if UI_AVAILABLE:
    visual_shop = VisualShopUI(bot, db, shop_system)
    print("✅ VisualShopUI instance created")
else:
    print("❌ Cannot create VisualShopUI - discord-ui-components not available")
    visual_shop = None

# VISUAL UI ===============================================



# --- SHOP SYSTEM CLASS ---
class ShopSystem:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
    
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
            # Remove any existing gem roles first
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


#  END SHOPCLASS SYSTEM

# === CREATE SHOP SYSTEM ===
shop_system = ShopSystem(bot, db)

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
    progress_bar = "🟩" * 20  # <-- THIS LINE SHOULD HAVE 8 SPACES (2 tabs/indents)
    
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
    
    # ... rest of the code ...
        
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
    
async def end_quiz(self):
    """End the entire quiz with improved leaderboard"""
    print(f"\n=== QUIZ ENDING ===")
    print(f"Quiz running: {self.quiz_running}")
    print(f"Current question: {self.current_question}")
    print(f"Total questions: {len(self.quiz_questions)}")
    print(f"Participants count: {len(self.participants)}")
    
    # Debug: Show all participants and their scores
    if self.participants:
        print("\n=== PARTICIPANTS DATA ===")
        for user_id, data in self.participants.items():
            print(f"User: {data['name']} (ID: {user_id})")
            print(f"  Score: {data['score']}")
            print(f"  Correct answers: {data.get('correct_answers', 0)}")
            print(f"  Total answers: {len(data.get('answers', []))}")
    
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
    
    print(f"\n=== SORTED PARTICIPANTS ===")
    for i, (user_id, data) in enumerate(sorted_participants[:5], 1):
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
    
    print(f"\n=== QUIZ STATISTICS ===")
    print(f"Total questions: {total_questions}")
    print(f"Total participants: {total_participants}")
    print(f"Total correct answers: {total_correct}")
    print(f"Total attempts: {total_attempts}")
    
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
    
    if rewards_distributed:
        print("\n=== REWARDS DISTRIBUTED ===")
        for user_id, reward in rewards_distributed.items():
            print(f"  User ID: {user_id}")
            print(f"    Gems: {reward.get('gems', 0)}")
            print(f"    Rank: {reward.get('rank', 'N/A')}")

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
                    print(f"Sending DM to {data['name']}...")
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
                    print(f"✅ DM sent to {data['name']}")
                except Exception as e:
                    print(f"❌ Failed to send DM to {data['name']}: {e}")
    
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
    
    # === ADD THIS MISSING METHOD ===
async def distribute_quiz_rewards(self, sorted_participants):
    """Distribute gems based on quiz performance"""
    print(f"\n=== DISTRIBUTING QUIZ REWARDS ===")
    print(f"Total participants: {len(sorted_participants)}")
    
    rewards = {}
    total_participants = len(sorted_participants)
    
    if total_participants == 0:
        print("❌ No participants to reward!")
        return rewards
    
    for rank, (user_id, data) in enumerate(sorted_participants, 1):
        print(f"\nProcessing user {user_id} (Rank #{rank})")
        print(f"Username: {data['name']}")
        print(f"Score: {data.get('score', 0)} points")
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
        score = data.get("score", 0)
        score_bonus = (score // 100) * 10
        base_gems += score_bonus
        print(f"Score bonus ({score} pts): +{score_bonus} gems")
        
        # Perfect score bonus
        max_score = len(self.quiz_questions) * 300
        if score == max_score:
            base_gems += 250
            reason = f"🎯 Perfect Score! ({score} pts, Rank #{rank})"
            print(f"Perfect score bonus: +250 gems")
        else:
            reason = f"🏆 Quiz Rewards ({score} pts, Rank #{rank})"
        
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
    
    # === ADD THIS MISSING METHOD ===
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
    
    # === ADD THIS MISSING METHOD ===
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

# END DAILY CMD--------

# === SHOP COMMANDS ===
shop_system = ShopSystem(bot, db)  # Create shop system instance

@bot.group(name="shop", invoke_without_command=True)
async def shop_group(ctx):
    """Shop system - Buy items with gems"""
    # Get user balance
    user_id = str(ctx.author.id)
    balance = await db.get_balance(user_id)
    
    # Get shop items
    items = await db.shop_get_items()
    
    # Create embed
    embed = discord.Embed(
        title="🛒 **Gem Shop**",
        description=f"Your balance: **💎 {balance['gems']:,} gems**\n\n"
                   "Use `!!shop buy <number>` to purchase an item!",
        color=discord.Color.gold()
    )
    
    # Add shop items
    for item in items:
        # Format item info
        if item["type"] == "role_color":
            emoji = "🛡️"
            duration = f"({item['duration_days']} days)"
        elif item["type"] == "nickname_color":
            emoji = "🎨"
            duration = f"({item['duration_days']} days)"
        elif item["type"] == "special_role":
            emoji = "🌟"
            duration = f"({item['duration_days']} days)"
        elif item["type"] == "mystery_box":
            emoji = "🎁"
            duration = f"(Win {item['min_gems']}-{item['max_gems']} gems)"
        else:
            emoji = "🛒"
            duration = ""
        
        embed.add_field(
            name=f"{emoji} **[{item['id']}] {item['name']}** - 💎 {item['price']:,}",
            value=f"{item['description']} {duration}",
            inline=False
        )
    
    # Add tips
    embed.add_field(
        name="💡 **How to Buy**",
        value="`!!shop buy 1` - Buy item #1\n"
              "`!!shop balance` - Check your gems\n"
              "`!!shop history` - View purchase history",
        inline=False
    )
    
    if db.using_database:
        embed.set_footer(text="💾 PostgreSQL Database | Shop items will expire based on duration")
    else:
        embed.set_footer(text="⚠️ JSON Fallback Mode | Some features limited")
    
    await ctx.send(embed=embed)

@shop_group.command(name="buy")
async def shop_buy(ctx, item_id: int):
    """Buy an item from the shop"""
    # Get shop items to validate item exists
    items = await db.shop_get_items()
    item_exists = any(item["id"] == item_id for item in items)
    
    if not item_exists:
        await ctx.send(f"❌ Item #{item_id} not found in shop!")
        return
    
    # Process purchase
    result = await shop_system.process_purchase(ctx.author, item_id, ctx.guild)
    
    if result["success"]:
        # Send success message
        await ctx.send(result["message"])
        
        # Send additional embed if present
        if "embed" in result.get("item_result", {}):
            await ctx.send(embed=result["item_result"]["embed"])
    else:
        await ctx.send(result["message"])

@shop_group.command(name="balance")
async def shop_balance(ctx):
    """Check your gem balance for shopping"""
    user_id = str(ctx.author.id)
    balance = await db.get_balance(user_id)
    
    embed = discord.Embed(
        title="💰 **Shopping Balance**",
        description=f"**{ctx.author.mention}, you have:**\n"
                   f"💎 **{balance['gems']:,} gems**\n\n"
                   f"*Total earned: {balance['total_earned']:,} gems*",
        color=discord.Color.gold()
    )
    
    # Add earning tips
    embed.add_field(
        name="💎 **Earn More Gems**",
        value="• `!!currency daily` - Daily reward\n"
              "• `!!quiz start` - Join quizzes\n"
              "• `!!shop buy 4` - Mystery box (gamble)",
        inline=False
    )
    
    await ctx.send(embed=embed)

@shop_group.command(name="history")
async def shop_history(ctx, limit: int = 10):
    """View your purchase history"""
    user_id = str(ctx.author.id)
    
    # Get purchases from database
    purchases = await db.shop_get_user_purchases(user_id, limit)
    
    if not purchases:
        embed = discord.Embed(
            title="📜 **Purchase History**",
            description="You haven't purchased anything yet!\n"
                       "Use `!!shop` to browse available items.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"📜 **Purchase History for {ctx.author.display_name}**",
        description=f"Last {len(purchases)} purchases:",
        color=discord.Color.blue()
    )
    
    # Format purchases
    for i, purchase in enumerate(purchases[:10], 1):
        # Format purchase time
        if purchase["purchased_at"]:
            try:
                purchase_time = datetime.fromisoformat(purchase["purchased_at"].replace('Z', '+00:00'))
                time_str = f"<t:{int(purchase_time.timestamp())}:R>"
            except:
                time_str = purchase["purchased_at"][:10]
        else:
            time_str = "Unknown"
        
        embed.add_field(
            name=f"{i}. {purchase['item_name']}",
            value=f"**Type:** {purchase['item_type']}\n"
                  f"**Price:** 💎 {purchase['price']:,}\n"
                  f"**When:** {time_str}",
            inline=True
        )
    
    # Add total spent
    total_spent = sum(p["price"] for p in purchases)
    embed.add_field(
        name="💰 **Total Spent**",
        value=f"💎 **{total_spent:,} gems**",
        inline=False
    )
    
    embed.set_footer(text=f"Showing last {len(purchases)} purchases")
    await ctx.send(embed=embed)

@bot.command(name="setupshop")
@commands.has_permissions(administrator=True)
async def setup_shop(ctx):
    """Setup the visual shop channel (Admin only)"""
    if not UI_AVAILABLE or visual_shop is None:
        await ctx.send("❌ Visual shop requires `discord-ui-components`!\n"
                      "💡 Add it to requirements.txt and redeploy.")
        return
    
    await ctx.send("🛒 Setting up visual shop interface...")
    
    shop_channel = await visual_shop.setup_shop_channel(ctx.guild)
    
    if shop_channel:
        embed = discord.Embed(
            title="✅ **Visual Shop Setup Complete!**",
            description=f"The interactive shop is now available in {shop_channel.mention}!\n\n"
                       "**Features:**\n"
                       "• Browse items with buttons\n"
                       "• Click to view details\n"
                       "• One-click purchases\n"
                       "• No commands needed!\n\n"
                       "Users can now just visit the shop channel and interact with the buttons.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Failed to setup shop channel!")
# END SHOP CMD ---=========
# REFRESH CMD -----------
@bot.command(name="refreshshop")
@commands.has_permissions(administrator=True)
async def refresh_shop(ctx):
    """Refresh the shop interface"""
    await ctx.send("🔄 Refreshing shop interface...")
    
    # Clear and recreate shop
    shop_channel = await visual_shop.setup_shop_channel(ctx.guild)
    
    if shop_channel:
        await ctx.send(f"✅ Shop refreshed in {shop_channel.mention}")
    else:
        await ctx.send("❌ Failed to refresh shop!")

# END REFRESH CMD 

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

# QUIZ TEST ----

@bot.command(name="quiztest")
@commands.has_permissions(manage_messages=True)
async def quiz_test(ctx):
    """Test if quiz rewards are working"""
    # Create a fake quiz completion
    quiz_system.quiz_channel = ctx.channel
    quiz_system.participants = {
        str(ctx.author.id): {
            "name": ctx.author.display_name,
            "score": 1200,  # Good score
            "correct_answers": 4,
            "answers": [
                {"correct": True, "points": 300, "time": 3},
                {"correct": True, "points": 280, "time": 5},
                {"correct": True, "points": 300, "time": 2},
                {"correct": True, "points": 320, "time": 1}
            ]
        }
    }
    
    # Call end_quiz directly
    await quiz_system.end_quiz()
    
    await ctx.send("✅ Quiz test completed! Check console for logs and your gems with `!!currency`")

# TESTREWARDS ----

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
    if bot.guilds:
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
# END ON READY -------------------

# Daily cleanup task
@tasks.loop(hours=24)
async def daily_cleanup():
    """Daily cleanup of expired shop items"""
    await db.shop_cleanup_expired()

# Start cleanup task when bot is ready
@bot.event
async def on_ready():
    # ... existing on_ready code ...
    daily_cleanup.start()
    print("✅ Started daily cleanup task")

# BUTTON HANDLER===================
@bot.event
async def on_interaction(interaction):
    """Handle button interactions"""
    if not hasattr(interaction, 'custom_id'):
        return
    
    custom_id = interaction.custom_id
    
    # Defer the response (important for buttons)
    await interaction.defer(ephemeral=True)
    
    user = interaction.user
    
    try:
        # Handle different button actions
        if custom_id == "browse_items":
            embed, components = await visual_shop.browse_items(user)
            await interaction.send(embed=embed, components=components, ephemeral=True)
            
        elif custom_id == "check_balance":
            embed = await visual_shop.show_balance(user)
            await interaction.send(embed=embed, ephemeral=True)
            
        elif custom_id == "view_history":
            embed, components = await visual_shop.show_purchase_history(user)
            if components:
                await interaction.send(embed=embed, components=components, ephemeral=True)
            else:
                await interaction.send(embed=embed, ephemeral=True)
                
        elif custom_id == "daily_reward":
            # You can redirect to daily command or handle it here
            await interaction.send("🎁 Use `!!currency daily` to claim your daily reward!", ephemeral=True)
            
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
            
        elif custom_id == "back_to_shop":
            # Get original shop welcome message
            if visual_shop.shop_channel_id:
                channel = bot.get_channel(visual_shop.shop_channel_id)
                if channel:
                    try:
                        msg = await channel.fetch_message(visual_shop.shop_message_id)
                        await interaction.send(f"🛒 [Go back to shop]({msg.jump_url})", ephemeral=True)
                    except:
                        await interaction.send("🛒 Returning to shop...", ephemeral=True)
            
        elif custom_id.startswith("view_item_"):
            item_id = int(custom_id.split("_")[-1])
            embed, components = await visual_shop.view_item_details(user, item_id)
            if embed:
                await interaction.send(embed=embed, components=components, ephemeral=True)
            else:
                await interaction.send("❌ Item not found!", ephemeral=True)
                
        elif custom_id.startswith("browse_page_"):
            page = int(custom_id.split("_")[-1])
            embed, components = await visual_shop.browse_items(user, page)
            await interaction.send(embed=embed, components=components, ephemeral=True)
            
        elif custom_id.startswith("buy_item_"):
            item_id = int(custom_id.split("_")[-1])
            result = await visual_shop.process_purchase(user, item_id, interaction)
            
            # Send purchase result
            await interaction.send(result, ephemeral=True)
            
            # Also update user's balance display
            balance_embed = await visual_shop.show_balance(user)
            await interaction.send(embed=balance_embed, ephemeral=True)
            
        elif custom_id == "back_to_browse":
            embed, components = await visual_shop.browse_items(user)
            await interaction.send(embed=embed, components=components, ephemeral=True)
            
        elif custom_id.startswith("history_page_"):
            page = int(custom_id.split("_")[-1])
            embed, components = await visual_shop.show_purchase_history(user, page)
            if components:
                await interaction.send(embed=embed, components=components, ephemeral=True)
            else:
                await interaction.send(embed=embed, ephemeral=True)
                
    except Exception as e:
        print(f"Button interaction error: {e}")
        await interaction.send("❌ An error occurred. Please try again.", ephemeral=True)

# END BUTTON INTERACTION HANDLER =========================

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