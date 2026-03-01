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
import string

async def log_to_discord(bot, message, level="INFO", error=None):
    """ALWAYS prints to Railway logs. Best‑effort send to #bot-logs."""
    print(f"[{level}] {message}")
    if error:
        tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        print(f"TRACEBACK:\n{tb}")

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
        print(f"⚠️ Failed to send log to Discord: {e}")

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

# ========== 🔥 CUSTOM DISCORD EMOJIS MAPPING 🔥 ==========
# Copy these exact emoji codes from Discord
CUSTOM_EMOJIS = {
    # 5 Swords
    'zenith_sword': '<:zenith_sword:1477018808068866150>',
    'abyssal_blade': '<:abyssal_blade:1477020694272544928>',
    'dawn_breaker': '<:dawn_breaker:1477020740913201172>',
    'bloodmoon_edge': '<:bloodmoon_egde:1477020810219749519>',
    'shadowbane': '<:shadowbane:1477020849096622220>',
    
    # Bilari Set
    'bilari_helm': '<:bilari_helm:1475222013650931923>',
    'bilari_armor': '<:bilari_armor:1475222678351908914>',
    'bilari_gloves': '<:bilari_gloves:1475222924515344444>',
    'bilari_boots': '<:bilari_boots:1475223007843713207>',
    
    # Cryo Set
    'cryo_helm': '<:cryo_helm:1475940413390065724>',
    'cryo_armor': '<:cryo_armor:1475940347099222169>',
    'cryo_gloves': '<:cryo_gloves:1475940251959689486>',
    'cryo_boots': '<:cryo_boots:1475940150063403162>',
    
    # Bane Set
    'bane_helm': '<:bane_helm:1477017964791206101>',
    'bane_armor': '<:bane_armor:1477017926434426941>',
    'bane_gloves': '<:bane_gloves:1477017850597343594>',
    'bane_boots': '<:bane_boots:1477017746159046799>',
    
    # Champion Set
    'champ_ring': '<:champ_ring:1477132404165578836>',
    'champ_earring': '<:champ_earring:1477131963981889546>',
    'champ_pen': '<:champ_pen:1477132494519271425>',
    
    # Defender Set
    'def_ring': '<:def_ring:1477133279802036225>',
    'def_earring': '<:def_earring:1477133318917980260>',
    'def_pen': '<:def_pen:1477133384387133704>',
    
    # Angel Set
    'wing_ring': '<:wing_ring:1477134740862800065>',
    'harp_earring': '<:harp_earring:1477134791253164186>',
    'angel_pen': '<:angel_pen:1477134827017994280>',
    
    # Pets (you can add these later when you have the emoji IDs)
    'pet_dragon': '<:pet_dragon:000000000000000000>',  # Replace with actual ID
    'pet_griffin': '<:pet_griffin:000000000000000000>',  # Replace with actual ID
    'pet_lion': '<:pet_lion:000000000000000000>',  # Replace with actual ID
    
    # Tools/Misc
    'pickaxe': '<:pickaxe:1477024057382666383>',  # Replace with actual ID
    'shadow': '<:shadow:1477258013256454339>',
    'treasure_carriage': '<:treasure_carriage:1477354550502625601>',

}
# ============================================================
# EMOJIS HELPER FUNCTIONS 
def get_item_emoji(item_name: str, item_type: str) -> str:
    """Return the appropriate custom emoji based on item name and type."""
    item_lower = item_name.lower()
    
    # Weapons (5 specific swords)
    if item_type == 'weapon':
        if 'zenith' in item_lower:
            return CUSTOM_EMOJIS['zenith_sword']
        elif 'abyssal' in item_lower:
            return CUSTOM_EMOJIS['abyssal_blade']
        elif 'dawn' in item_lower or 'breaker' in item_lower:
            return CUSTOM_EMOJIS['dawn_breaker']
        elif 'bloodmoon' in item_lower or 'edge' in item_lower:
            return CUSTOM_EMOJIS['bloodmoon_edge']
        elif 'shadowbane' in item_lower:
            return CUSTOM_EMOJIS['shadowbane']
        return CUSTOM_EMOJIS['zenith_sword']
    
    # Armor Sets
    elif item_type == 'armor':
        # Bilari Set
        if 'bilari' in item_lower:
            if 'helm' in item_lower:
                return CUSTOM_EMOJIS['bilari_helm']
            elif 'suit' in item_lower or 'armor' in item_lower:
                return CUSTOM_EMOJIS['bilari_armor']
            elif 'gauntlet' in item_lower or 'glove' in item_lower:
                return CUSTOM_EMOJIS['bilari_gloves']
            elif 'boot' in item_lower:
                return CUSTOM_EMOJIS['bilari_boots']
        
        # Cryo Set
        elif 'cryo' in item_lower:
            if 'helm' in item_lower:
                return CUSTOM_EMOJIS['cryo_helm']
            elif 'suit' in item_lower or 'armor' in item_lower:
                return CUSTOM_EMOJIS['cryo_armor']
            elif 'gauntlet' in item_lower or 'glove' in item_lower:
                return CUSTOM_EMOJIS['cryo_gloves']
            elif 'boot' in item_lower:
                return CUSTOM_EMOJIS['cryo_boots']
        
        # Bane Set
        elif 'bane' in item_lower:
            if 'helm' in item_lower:
                return CUSTOM_EMOJIS['bane_helm']
            elif 'suit' in item_lower or 'armor' in item_lower:
                return CUSTOM_EMOJIS['bane_armor']
            elif 'gauntlet' in item_lower or 'glove' in item_lower:
                return CUSTOM_EMOJIS['bane_gloves']
            elif 'boot' in item_lower:
                return CUSTOM_EMOJIS['bane_boots']
        
        return CUSTOM_EMOJIS['bilari_armor']
    
    # Accessories
    elif item_type == 'accessory':
        # Champion Set
        if 'champion' in item_lower or 'champ' in item_lower:
            if 'ring' in item_lower:
                return CUSTOM_EMOJIS['champ_ring']
            elif 'earring' in item_lower:
                return CUSTOM_EMOJIS['champ_earring']
            elif 'pendant' in item_lower or 'pen' in item_lower:
                return CUSTOM_EMOJIS['champ_pen']
        
        # Defender Set
        elif 'defender' in item_lower or 'def' in item_lower:
            if 'ring' in item_lower:
                return CUSTOM_EMOJIS['def_ring']
            elif 'earring' in item_lower:
                return CUSTOM_EMOJIS['def_earring']
            elif 'pendant' in item_lower or 'pen' in item_lower:
                return CUSTOM_EMOJIS['def_pen']
        
        # Angel Set
        elif 'angel' in item_lower:
            if 'ring' in item_lower:
                return CUSTOM_EMOJIS['wing_ring']
            elif 'earring' in item_lower:
                return CUSTOM_EMOJIS['harp_earring']
            elif 'pendant' in item_lower or 'pen' in item_lower:
                return CUSTOM_EMOJIS['angel_pen']
        
        return CUSTOM_EMOJIS['champ_ring']
    
    # Pets
    elif item_type == 'pet':
        if 'dragon' in item_lower:
            return CUSTOM_EMOJIS['pet_dragon']
        elif 'griffin' in item_lower:
            return CUSTOM_EMOJIS['pet_griffin']
        elif 'lion' in item_lower:
            return CUSTOM_EMOJIS['pet_lion']
        return CUSTOM_EMOJIS['pet_dragon']
    
    # Default fallback
    return '📦'
# ============================================================


# --- Create the bot instance ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!!', intents=intents, help_command=None)
bot.active_bags = {}
bot.db_pool = None

@bot.command(name='testemojis')
async def test_emojis(ctx):
    """Test if custom emojis are working"""
    embed = discord.Embed(title="Emoji Test", color=discord.Color.blue())
    
    # Test a few emojis
    test_emojis = [
        f"Zenith Sword: {CUSTOM_EMOJIS['zenith_sword']}",
        f"Bilari Helm: {CUSTOM_EMOJIS['bilari_helm']}",
        f"Champion Ring: {CUSTOM_EMOJIS['champ_ring']}",
        f"Defender Ring: {CUSTOM_EMOJIS['def_ring']}",
        f"Angel Ring: {CUSTOM_EMOJIS['wing_ring']}",
    ]
    
    embed.description = "\n".join(test_emojis)
    await ctx.send(embed=embed)
    
    # Also send raw message
    await ctx.send(f"Raw: {CUSTOM_EMOJIS['zenith_sword']}")

@bot.command(name='checkperms')
async def check_permissions(ctx):
    """Check if bot has necessary permissions"""
    bot_member = ctx.guild.me
    permissions = bot_member.guild_permissions
    
    embed = discord.Embed(
        title="Bot Permissions",
        color=discord.Color.blue()
    )
    
    # Check critical permissions
    embed.add_field(
        name="Use External Emojis",
        value="✅ Yes" if permissions.external_emojis else "❌ No - This is likely the issue!",
        inline=False
    )
    
    embed.add_field(
        name="Send Messages",
        value="✅ Yes" if permissions.send_messages else "❌ No",
        inline=True
    )
    
    embed.add_field(
        name="Embed Links",
        value="✅ Yes" if permissions.embed_links else "❌ No",
        inline=True
    )
    
    await ctx.send(embed=embed)

@bot.command(name='checkemojis')
async def check_emojis(ctx):
    """Check if bot can access your custom emojis"""
    guild = ctx.guild
    bot_guilds = bot.guilds
    
    embed = discord.Embed(
        title="Emoji Access Check",
        color=discord.Color.blue()
    )
    
    # List all guilds the bot is in
    guild_list = [f"• {g.name} (ID: {g.id})" for g in bot_guilds]
    embed.add_field(
        name="Bot is in these servers:",
        value="\n".join(guild_list) or "None",
        inline=False
    )
    
    # Check if current guild has the emojis
    emoji_ids = [
        1477018808068866150,  # zenith_sword
        1475222013650931923,  # bilari_helm
        1477132404165578836,  # champ_ring
    ]
    
    found_emojis = []
    missing_emojis = []
    
    for emoji_id in emoji_ids:
        emoji = discord.utils.get(guild.emojis, id=emoji_id)
        if emoji:
            found_emojis.append(f"✅ {emoji.name} (ID: {emoji_id})")
        else:
            missing_emojis.append(f"❌ Emoji ID: {emoji_id}")
    
    if found_emojis:
        embed.add_field(name="Found Emojis", value="\n".join(found_emojis), inline=False)
    if missing_emojis:
        embed.add_field(name="Missing Emojis", value="\n".join(missing_emojis), inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def testpartial(ctx):
    view = discord.ui.View()
    emoji = discord.PartialEmoji(name="def_ring", id=1477133279802036225)
    button = discord.ui.Button(label="Test", emoji=emoji, style=discord.ButtonStyle.primary)
    view.add_item(button)
    await ctx.send("PartialEmoji test:", view=view)
@bot.command()
@commands.has_permissions(administrator=True)
async def testremove(ctx, member: discord.Member, role: discord.Role):
    try:
        await member.remove_roles(role)
        await ctx.send(f"Removed {role.name} from {member.mention}")
    except Exception as e:
        await ctx.send(f"Failed: {e}")
@bot.command()
@commands.has_permissions(administrator=True)
async def checkcolors(ctx):
    """List all color items and their role IDs."""
    async with bot.db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT item_id, name, role_id FROM shop_items WHERE type = 'color'")
    if not rows:
        await ctx.send("No color items found.")
        return
    msg = "**Color Items & Role IDs:**\n"
    for r in rows:
        msg += f"ID {r['item_id']}: {r['name']} – Role ID: {r['role_id']}\n"
    await ctx.send(msg[:1900])  # avoid message length limit
@bot.command()
@commands.has_permissions(administrator=True)
async def testexpire(ctx):
    """Manually trigger expired purchase check."""
    cog = bot.get_cog('Shop')
    if cog:
        await cog.check_expired_purchases()
        await ctx.send("✅ Expiration check completed. Check logs.")
    else:
        await ctx.send("❌ Shop cog not found.")
@bot.command()
async def recentpurchases(ctx):
    async with bot.db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT up.user_id, si.name, up.expires_at
            FROM user_purchases up
            JOIN shop_items si ON up.item_id = si.item_id
            WHERE si.type = 'color'
            ORDER BY up.purchased_at DESC
            LIMIT 5
        """)
    msg = "\n".join([f"{r['name']} – expires {r['expires_at']}" for r in rows])
    await ctx.send(msg or "No purchases.")
@bot.command()
@commands.has_permissions(administrator=True)
async def fixguild(ctx):
    """Set guild_id for role/color items to current guild."""
    guild_id = ctx.guild.id
    async with bot.db_pool.acquire() as conn:
        result = await conn.execute("""
            UPDATE shop_items SET guild_id = $1 
            WHERE type IN ('role', 'color') AND guild_id IS NULL
        """, guild_id)
        await ctx.send(f"✅ Updated {result.split()[1]} items with guild_id {guild_id}.")

@bot.command()
async def checkmember(ctx, member: discord.Member):
    user_id = str(member.id)
    async with bot.db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT si.name, up.expires_at
            FROM user_purchases up
            JOIN shop_items si ON up.item_id = si.item_id
            WHERE up.user_id = $1 AND si.type IN ('role', 'color') AND up.used = FALSE
        """, user_id)
    if not rows:
        await ctx.send(f"{member.mention} has no active color/role purchases.")
        return
    msg = f"**{member.display_name}'s purchases:**\n"
    for r in rows:
        expires = r['expires_at']
        status = "EXPIRED" if expires < datetime.now(timezone.utc) else "active"
        msg += f"{r['name']} – expires {expires} ({status})\n"
    await ctx.send(msg)
@bot.command()
async def checkexpired(ctx, member: discord.Member):
    user_id = str(member.id)
    async with bot.db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT up.purchase_id, si.name, si.guild_id, up.expires_at
            FROM user_purchases up
            JOIN shop_items si ON up.item_id = si.item_id
            WHERE up.user_id = $1 AND si.type IN ('role', 'color') AND up.used = FALSE
        """, user_id)
    if not rows:
        await ctx.send(f"{member.mention} has no active role/color purchases.")
        return
    msg = f"**{member.display_name}'s purchases:**\n"
    for r in rows:
        guild_id = r['guild_id']
        expires = r['expires_at']
        status = "EXPIRED" if expires < datetime.now(timezone.utc) else "active"
        msg += f"ID {r['purchase_id']}: {r['name']} – guild_id: {guild_id} – expires {expires} ({status})\n"
    await ctx.send(msg[:1900])

@bot.command()
@commands.has_permissions(administrator=True)
async def fixoldguild(ctx, purchase_id: int, guild_id: int):
    """Manually set guild_id for a specific purchase's shop item."""
    async with bot.db_pool.acquire() as conn:
        # Get the item_id from the purchase
        row = await conn.fetchrow("SELECT item_id FROM user_purchases WHERE purchase_id = $1", purchase_id)
        if not row:
            await ctx.send("Purchase not found.")
            return
        item_id = row['item_id']
        await conn.execute("UPDATE shop_items SET guild_id = $1 WHERE item_id = $2", guild_id, item_id)
        await ctx.send(f"✅ Updated item {item_id} with guild_id {guild_id}.")

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
                bot.db_pool = self.pool

                async with self.pool.acquire() as conn:
                    result = await conn.fetchval('SELECT 1')
                    print(f"    ✅ Connection test: {result}")

                    # ========== CORE TABLES ==========
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
                            user_id TEXT NOT NULL,
                            timestamp TIMESTAMP DEFAULT NOW(),
                            type VARCHAR(20),
                            gems INTEGER,
                            reason TEXT,
                            balance_after INTEGER,
                            FOREIGN KEY (user_id) REFERENCES user_gems(user_id) ON DELETE CASCADE
                        )
                    ''')

                    # ========== FORTUNE BAG TABLES ==========
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
                            type TEXT NOT NULL,
                            role_id BIGINT,
                            color_hex TEXT,
                            guild_id BIGINT,
                            image_url TEXT,
                            created_at TIMESTAMP DEFAULT NOW(),
                            updated_at TIMESTAMP DEFAULT NOW()
                        )
                    ''')

                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS user_purchases (
                            purchase_id SERIAL PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            item_id INTEGER REFERENCES shop_items(item_id) ON DELETE CASCADE,
                            price_paid INTEGER NOT NULL,
                            purchased_at TIMESTAMP DEFAULT NOW(),
                            expires_at TIMESTAMPTZ,
                            used BOOLEAN DEFAULT FALSE
                        )
                    ''')

                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS shop_messages (
                            guild_id BIGINT PRIMARY KEY,
                            channel_id BIGINT NOT NULL,
                            message_id BIGINT NOT NULL
                        )
                    ''')

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

                    # ========== WEAPON SYSTEM TABLES ==========
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS weapon_types (
                            type_id SERIAL PRIMARY KEY,
                            name_base TEXT NOT NULL
                        )
                    ''')

                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS rarities (
                            rarity_id SERIAL PRIMARY KEY,
                            name TEXT NOT NULL UNIQUE,
                            color INTEGER,
                            display_order INTEGER DEFAULT 0
                        )
                    ''')

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

                    # ========== USER WEAPONS ==========
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS user_weapons (
                            id SERIAL PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            weapon_item_id INTEGER REFERENCES shop_items(item_id) ON DELETE CASCADE,
                            attack INTEGER NOT NULL,
                            purchase_id INTEGER REFERENCES user_purchases(purchase_id) ON DELETE SET NULL,
                            generated_name TEXT,
                            image_url TEXT,
                            variant_id INTEGER REFERENCES weapon_variants(variant_id) ON DELETE SET NULL,
                            description TEXT,
                            equipped BOOLEAN DEFAULT FALSE,
                            purchased_at TIMESTAMP DEFAULT NOW()
                        )
                    ''')

                    # ========== ARMOR SYSTEM TABLES ==========
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS armor_types (
                            armor_id SERIAL PRIMARY KEY,
                            name TEXT NOT NULL,
                            slot TEXT NOT NULL CHECK (slot IN ('helm', 'suit', 'gauntlets', 'boots')),
                            defense INTEGER NOT NULL DEFAULT 0,
                            rarity_id INTEGER REFERENCES rarities(rarity_id) ON DELETE SET NULL,
                            image_url TEXT,
                            description TEXT,
                            created_at TIMESTAMP DEFAULT NOW()
                        )
                    ''')

                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS user_armor (
                            id SERIAL PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            armor_id INTEGER REFERENCES armor_types(armor_id) ON DELETE CASCADE,
                            defense INTEGER NOT NULL,
                            equipped BOOLEAN DEFAULT FALSE,
                            purchased_at TIMESTAMP DEFAULT NOW(),
                            FOREIGN KEY (user_id) REFERENCES user_gems(user_id) ON DELETE CASCADE
                        )
                    ''')

                    # ========== ACCESSORY SYSTEM TABLES ==========
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS accessory_types (
                            accessory_id SERIAL PRIMARY KEY,
                            name TEXT NOT NULL,
                            slot TEXT NOT NULL CHECK (slot IN ('ring', 'pendant', 'earring')),
                            bonus_stat TEXT NOT NULL CHECK (bonus_stat IN ('atk', 'def', 'hp', 'energy')),
                            bonus_value INTEGER NOT NULL DEFAULT 0,
                            rarity_id INTEGER REFERENCES rarities(rarity_id) ON DELETE SET NULL,
                            image_url TEXT,
                            description TEXT,
                            created_at TIMESTAMP DEFAULT NOW()
                        )
                    ''')

                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS user_accessories (
                            id SERIAL PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            accessory_id INTEGER REFERENCES accessory_types(accessory_id) ON DELETE CASCADE,
                            bonus_value INTEGER NOT NULL,
                            equipped BOOLEAN DEFAULT FALSE,
                            slot TEXT NOT NULL CHECK (slot IN ('ring1', 'ring2', 'pendant', 'earring1', 'earring2')),
                            purchased_at TIMESTAMP DEFAULT NOW(),
                            FOREIGN KEY (user_id) REFERENCES user_gems(user_id) ON DELETE CASCADE,
                            UNIQUE(user_id, slot)
                        )
                    ''')

                    # ========== PET SYSTEM TABLES ==========
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS pet_types (
                            pet_id SERIAL PRIMARY KEY,
                            name TEXT NOT NULL,
                            bonus_stat TEXT CHECK (bonus_stat IN ('atk', 'def', 'hp', 'energy')),
                            bonus_value INTEGER DEFAULT 0,
                            image_url TEXT,
                            description TEXT
                        )
                    ''')

                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS user_pets (
                            id SERIAL PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            pet_id INTEGER REFERENCES pet_types(pet_id) ON DELETE CASCADE,
                            equipped BOOLEAN DEFAULT FALSE,
                            purchased_at TIMESTAMP DEFAULT NOW(),
                            FOREIGN KEY (user_id) REFERENCES user_gems(user_id) ON DELETE CASCADE
                        )
                    ''')

                    # ========== PLAYER STATS ==========
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS player_stats (
                            user_id TEXT PRIMARY KEY REFERENCES user_gems(user_id) ON DELETE CASCADE,
                            hp INTEGER NOT NULL DEFAULT 1000,
                            max_hp INTEGER NOT NULL DEFAULT 1000,
                            energy INTEGER NOT NULL DEFAULT 3,
                            max_energy INTEGER NOT NULL DEFAULT 3,
                            last_energy_regen TIMESTAMP DEFAULT NOW(),
                            mining_start TIMESTAMP,
                            mining_message_id BIGINT,
                            mining_channel_id BIGINT,
                            pending_reward INTEGER DEFAULT 0,
                            stolen_gems INTEGER DEFAULT 0,
                            plunder_count INTEGER DEFAULT 0,
                            last_plunder_reset DATE DEFAULT CURRENT_DATE,
                            has_pickaxe BOOLEAN DEFAULT FALSE
                        )
                    ''')

                    # ========== MINING CONFIG ==========
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS mining_config (
                            guild_id BIGINT PRIMARY KEY,
                            channel_id BIGINT NOT NULL,
                            message_id BIGINT
                        )
                    ''')

                    # ========== ATTACK LOGS ==========
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS attack_logs (
                            id SERIAL PRIMARY KEY,
                            attacker_id TEXT NOT NULL,
                            defender_id TEXT NOT NULL,
                            timestamp TIMESTAMP DEFAULT NOW(),
                            damage INTEGER,
                            attacker_weapon TEXT,
                            defender_hp_left INTEGER
                        )
                    ''')

                    # ========== NEW SET BONUSES TABLE ==========
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS user_set_bonuses (
                            user_id TEXT NOT NULL,
                            set_name TEXT NOT NULL,
                            set_type TEXT NOT NULL CHECK (set_type IN ('armor', 'accessory')),
                            pieces_owned INTEGER DEFAULT 0,
                            pieces_equipped INTEGER DEFAULT 0,
                            bonus_active BOOLEAN DEFAULT FALSE,
                            activated_at TIMESTAMP,
                            PRIMARY KEY (user_id, set_name, set_type),
                            FOREIGN KEY (user_id) REFERENCES user_gems(user_id) ON DELETE CASCADE
                        )
                    ''')

                    # ========== ADD MISSING COLUMNS TO EXISTING TABLES ==========
                    # These ensure the schema is updated if tables already exist

                    # User weapons
                    await conn.execute('ALTER TABLE user_weapons ADD COLUMN IF NOT EXISTS bleeding_chance FLOAT DEFAULT 0')
                    await conn.execute('ALTER TABLE user_weapons ADD COLUMN IF NOT EXISTS crit_chance FLOAT DEFAULT 0')
                    await conn.execute('ALTER TABLE user_weapons ADD COLUMN IF NOT EXISTS crit_damage FLOAT DEFAULT 0')

                    # Armor types
                    await conn.execute('ALTER TABLE armor_types ADD COLUMN IF NOT EXISTS hp_bonus INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE armor_types ADD COLUMN IF NOT EXISTS reflect_damage INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE armor_types ADD COLUMN IF NOT EXISTS set_name TEXT')

                    # User armor
                    await conn.execute('ALTER TABLE user_armor ADD COLUMN IF NOT EXISTS hp_bonus INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE user_armor ADD COLUMN IF NOT EXISTS reflect_damage INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE user_armor ADD COLUMN IF NOT EXISTS set_name TEXT')
                    await conn.execute('ALTER TABLE user_armor ADD COLUMN IF NOT EXISTS purchase_id INTEGER REFERENCES user_purchases(purchase_id) ON DELETE SET NULL')

                    # Accessory types
                    await conn.execute('ALTER TABLE accessory_types ADD COLUMN IF NOT EXISTS set_name TEXT')                   
                    await conn.execute('ALTER TABLE accessory_types ADD COLUMN IF NOT EXISTS slot_count INTEGER DEFAULT 1')
                    # Update slot constraint for accessory_types
                    await conn.execute('ALTER TABLE accessory_types DROP CONSTRAINT IF EXISTS accessory_types_slot_check')
                    await conn.execute('''
                        ALTER TABLE accessory_types ADD CONSTRAINT accessory_types_slot_check 
                        CHECK (slot IN ('ring1', 'ring2', 'earring1', 'earring2', 'pendant'))
                    ''')
                    # Update bonus_stat constraint for accessory_types
                    await conn.execute('ALTER TABLE accessory_types DROP CONSTRAINT IF EXISTS accessory_types_bonus_stat_check')
                    await conn.execute('''
                        ALTER TABLE accessory_types ADD CONSTRAINT accessory_types_bonus_stat_check 
                        CHECK (bonus_stat IN ('atk', 'def', 'hp', 'energy', 'crit', 'bleed'))
                    ''')

                    # User accessories
                    await conn.execute('ALTER TABLE user_accessories ADD COLUMN IF NOT EXISTS set_name TEXT')
                    await conn.execute('ALTER TABLE user_accessories ADD COLUMN IF NOT EXISTS purchase_id INTEGER REFERENCES user_purchases(purchase_id) ON DELETE SET NULL')

                    # Player stats
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS defense INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS crit_chance FLOAT DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS crit_damage FLOAT DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS defense_bonus INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS reflect_bonus INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS hp_bonus INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS atk_bonus INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS bleed_damage FLOAT DEFAULT 0')

                    # Update shop_items type constraint
                    await conn.execute('ALTER TABLE shop_items DROP CONSTRAINT IF EXISTS shop_items_type_check')
                    await conn.execute('''
                        ALTER TABLE shop_items ADD CONSTRAINT shop_items_type_check 
                        CHECK (type IN ('role', 'color', 'weapon', 'random_weapon_box', 
                                        'random_gear_box', 'random_accessories_box', 'pickaxe'))
                    ''')

                    # Update armor_types slot constraint to include new slots
                    await conn.execute('ALTER TABLE armor_types DROP CONSTRAINT IF EXISTS armor_types_slot_check')
                    await conn.execute('''
                        ALTER TABLE armor_types ADD CONSTRAINT armor_types_slot_check 
                        CHECK (slot IN ('helm', 'suit', 'gauntlets', 'boots'))
                    ''')

                    # ========== SEED DATA ==========
                    # Seed rarities
                    await conn.execute('''
                        INSERT INTO rarities (name, color, display_order) VALUES
                        ('Common', 0xFFFFFF, 1),
                        ('Uncommon', 0x00FF00, 2),
                        ('Rare', 0x0000FF, 3),
                        ('Epic', 0x800080, 4),
                        ('Legendary', 0xFFD700, 5)
                        ON CONFLICT (name) DO UPDATE SET color = EXCLUDED.color
                    ''')

                    # Seed weapon types
                    await conn.execute('''
                        INSERT INTO weapon_types (name_base) VALUES
                        ('Sword'), ('Axe'), ('Dagger')
                        ON CONFLICT DO NOTHING
                    ''')

                    # ========== CREATE INDEXES ==========
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_purchases_user ON user_purchases(user_id)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_weapons_user ON user_weapons(user_id)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_weapons_equipped ON user_weapons(user_id, equipped)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_armor_user ON user_armor(user_id)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_armor_equipped ON user_armor(user_id, equipped)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_armor_set ON user_armor(user_id, set_name)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_armor_equipped_set ON user_armor(user_id, equipped, set_name)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_accessories_user ON user_accessories(user_id)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_accessories_equipped ON user_accessories(user_id, equipped, slot)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_accessories_set ON user_accessories(user_id, set_name)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_accessories_equipped_set ON user_accessories(user_id, equipped, set_name)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_pets_user ON user_pets(user_id)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_fortune_bags_active ON fortune_bags(active)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_participants_message_id ON fortune_bag_participants(message_id)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_set_bonuses_user ON user_set_bonuses(user_id)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_set_bonuses_active ON user_set_bonuses(user_id, bonus_active)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_weapons_effects ON user_weapons(user_id, equipped) WHERE equipped = TRUE')

                self.using_database = True
                print(f"🎉 Success with: {strategy_name}")
                print("✅ Database connected and ready!")
                return True

            except Exception as e:
                print(f"    ❌ Failed: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
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


# === SIMPLE BOT COMMANDS ===
@bot.command(name="meow")
async def ping(ctx):
    """Check if bot is alive"""
    await ctx.send("Meow~")

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
        await load_mining_persistence(bot)
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


@bot.event
async def on_error(event, *args, **kwargs):
    """Global error handler for uncaught exceptions."""
    error = sys.exc_info()[1]
    if error:
        await log_to_discord(bot, f"Unhandled exception in `{event}`", "ERROR", error)
    else:
        await log_to_discord(bot, f"Unknown error in `{event}`", "ERROR")


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
    """Handle command errors and log them."""
    if isinstance(error, commands.CommandNotFound):
        return  # ignore unknown commands
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
        return
    if isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid arguments. Check `!!help` for usage.")
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument.")
        return

    # Log unexpected errors to Discord
    await log_to_discord(bot, f"Error in command `{ctx.command}` by {ctx.author}", "ERROR", error)

    # Also inform the user
    await ctx.send("❌ An unexpected error occurred. The developers have been notified.")


# INVENTORY CLASS 


class InventoryItemButton(discord.ui.Button):
    def __init__(self, item_data, item_type):
        self.item_data = item_data
        self.item_type = item_type
        label = f"{item_data['name']}"
        if item_type == 'weapon':
            label += f" (+{item_data['attack']} ATK)"
        elif item_type == 'armor':
            label += f" ({item_data['defense']} DEF)"
        elif item_type == 'accessory':
            label += f" (+{item_data['bonus_value']} {item_data['bonus_stat']})"

        style = discord.ButtonStyle.success if item_data.get('equipped') else discord.ButtonStyle.secondary
        super().__init__(label=label[:50], style=style, custom_id=f"inv_{item_type}_{item_data['id']}")

    async def callback(self, interaction: discord.Interaction):
        try:
            view = self.view
            await view.show_item_details(interaction, self.item_data, self.item_type)
        except Exception as e:
            print(f"Error in InventoryItemButton: {e}")
            traceback.print_exc()
            await interaction.response.send_message("An error occurred.", ephemeral=True)


class CategoryView(discord.ui.View):
    def __init__(self, user_id, items, item_type, parent_view):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.items = items
        self.item_type = item_type
        self.parent = parent_view

    @discord.ui.button(label="🔙", style=discord.ButtonStyle.secondary, row=4)
    async def go_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("Not your inventory!", ephemeral=True)
            return
        await interaction.response.edit_message(embed=self.parent.create_main_embed(), view=self.parent)


class ItemActionView(discord.ui.View):
    def __init__(self, user_id, item_data, item_type, parent_view):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.item_data = item_data
        self.item_type = item_type
        self.parent = parent_view  # This is InventoryView

    @discord.ui.button(label="⚔️ Equip", style=discord.ButtonStyle.success, row=0)
    async def equip_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != int(self.user_id):
                await interaction.response.send_message("Not your inventory!", ephemeral=True)
                return

            if self.item_data.get('equipped'):
                await interaction.response.send_message("This item is already equipped!", ephemeral=True)
                return

            await interaction.response.defer(ephemeral=True)

            async with self.parent.cog.bot.db_pool.acquire() as conn:
                if self.item_type == 'weapon':
                    await conn.execute("UPDATE user_weapons SET equipped = FALSE WHERE user_id = $1", str(self.user_id))
                    await conn.execute("UPDATE user_weapons SET equipped = TRUE WHERE id = $1", self.item_data['id'])

                elif self.item_type == 'armor':
                    slot = self.item_data.get('slot', 'armor')
                    await conn.execute("""
                        UPDATE user_armor SET equipped = FALSE 
                        WHERE user_id = $1 AND armor_id IN 
                        (SELECT armor_id FROM armor_types WHERE slot = $2)
                    """, str(self.user_id), slot)
                    await conn.execute("UPDATE user_armor SET equipped = TRUE WHERE id = $1", self.item_data['id'])

                elif self.item_type == 'accessory':
                    slot = self.item_data['slot']
                    await conn.execute("""
                        UPDATE user_accessories SET equipped = FALSE 
                        WHERE user_id = $1 AND slot = $2
                    """, str(self.user_id), slot)
                    await conn.execute("UPDATE user_accessories SET equipped = TRUE WHERE id = $1", self.item_data['id'])

            await interaction.followup.send(f"Equipped **{self.item_data['name']}**!", ephemeral=True)
            await self.parent.refresh_inventory(interaction)  # FIXED: removed .parent
        except Exception as e:
            print(f"Error in equip_item: {e}")
            traceback.print_exc()
            await interaction.followup.send("An error occurred while equipping.", ephemeral=True)

    @discord.ui.button(label="Unequip", style=discord.ButtonStyle.danger, row=0)
    async def unequip_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("Not your inventory!", ephemeral=True)
            return

        if not self.item_data.get('equipped'):
            await interaction.response.send_message("This item is not equipped!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        async with self.parent.cog.bot.db_pool.acquire() as conn:
            if self.item_type == 'weapon':
                await conn.execute("UPDATE user_weapons SET equipped = FALSE WHERE id = $1", self.item_data['id'])
            elif self.item_type == 'armor':
                await conn.execute("UPDATE user_armor SET equipped = FALSE WHERE id = $1", self.item_data['id'])
            elif self.item_type == 'accessory':
                await conn.execute("UPDATE user_accessories SET equipped = FALSE WHERE id = $1", self.item_data['id'])

        await interaction.response.send_message(f"Unequipped **{self.item_data['name']}**!", ephemeral=True)
        await self.parent.refresh_inventory(interaction)

    @discord.ui.button(label="🔙", style=discord.ButtonStyle.secondary, row=1)
    async def go_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("Not your inventory!", ephemeral=True)
            return
        embed = discord.Embed(title=f"**{self.item_type.capitalize()}s**", color=discord.Color.blue())
        view = CategoryView(self.user_id, self.parent.items, self.item_type, self.parent)
        await interaction.response.edit_message(embed=embed, view=view)


class InventoryView(discord.ui.View):
    def __init__(self, user_id, inventory_data, cog):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.inventory = inventory_data
        self.cog = cog

    def create_main_embed(self):
        """Create the main inventory overview (only items and gems)"""
        user = self.cog.bot.get_user(int(self.user_id))
        embed = discord.Embed(
            title=f"📦 **{user.display_name if user else 'Unknown'}'s Inventory**",
            description=f"💰 **Gems:** {self.inventory['gems']}",
            color=discord.Color.purple()
        )
        if user:
            embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(name="⚔️ Weapons", value=str(len(self.inventory['weapons'])), inline=True)
        embed.add_field(name="🛡️ Armor", value=str(len(self.inventory['armor'])), inline=True)
        embed.add_field(name="📿 Accessories", value=str(len(self.inventory['accessories'])), inline=True)

        return embed

    async def refresh_inventory(self, interaction):
        """Refresh inventory data after equip/unequip"""
        user_id = str(self.user_id)
        async with self.cog.bot.db_pool.acquire() as conn:
            weapons = await conn.fetch("""
                SELECT uw.id, COALESCE(si.name, uw.generated_name) as name,
                       uw.attack, uw.equipped, uw.description,
                       COALESCE(si.image_url, uw.image_url) as image_url,
                       r.color as rarity_color
                FROM user_weapons uw
                LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                LEFT JOIN weapon_variants v ON uw.variant_id = v.variant_id
                LEFT JOIN rarities r ON v.rarity_id = r.rarity_id
                WHERE uw.user_id = $1
                ORDER BY uw.equipped DESC, uw.purchased_at DESC
            """, user_id)

            armor = await conn.fetch("""
                SELECT ua.id, at.name, ua.defense, ua.equipped, at.slot,
                       at.image_url, at.description, r.color as rarity_color
                FROM user_armor ua
                JOIN armor_types at ON ua.armor_id = at.armor_id
                LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                WHERE ua.user_id = $1
                ORDER BY ua.equipped DESC, ua.purchased_at DESC
            """, user_id)

            accessories = await conn.fetch("""
                SELECT ua.id, at.name, ua.bonus_value, at.bonus_stat,
                       ua.equipped, ua.slot, at.image_url, at.description,
                       r.color as rarity_color
                FROM user_accessories ua
                JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                WHERE ua.user_id = $1
                ORDER BY ua.equipped DESC, ua.purchased_at DESC
            """, user_id)

        balance = await currency_system.get_balance(user_id)

        self.inventory = {
            'weapons': [dict(w) for w in weapons],
            'armor': [dict(a) for a in armor],
            'accessories': [dict(a) for a in accessories],
            'gems': balance['gems']
        }

        await interaction.edit_original_response(embed=self.create_main_embed(), view=self)

    async def show_item_details(self, interaction: discord.Interaction, item_data, item_type):
        embed = discord.Embed(
            title=f"**{item_data['name']}**",
            color=discord.Color.gold()
        )

        if item_data.get('image_url'):
            embed.set_image(url=item_data['image_url'])

        stats = []
        if item_type == 'weapon':
            stats.append(f"⚔️ **ATK:** +{item_data['attack']}")
        elif item_type == 'armor':
            stats.append(f"🛡️ **DEF:** +{item_data['defense']}")
        elif item_type == 'accessory':
            stats.append(f"✨ **{item_data['bonus_stat'].upper()}:** +{item_data['bonus_value']}")
            stats.append(f"📌 **Slot:** {item_data['slot']}")

        stats.append(f"📝 **Description:** {item_data.get('description', 'No description')}")
        embed.description = "\n".join(stats)

        if item_data.get('rarity_color'):
            embed.color = item_data['rarity_color']

        status = "**EQUIPPED**" if item_data.get('equipped') else "**NOT EQUIPPED**"
        embed.add_field(name="Status", value=status, inline=False)

        view = ItemActionView(self.user_id, item_data, item_type, self)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="🗡️ Weapons", style=discord.ButtonStyle.primary, row=0)
    async def show_weapons(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != int(self.user_id):
                await interaction.response.send_message("Not your inventory!", ephemeral=True)
                return

            if not self.inventory['weapons']:
                await interaction.response.send_message("You have no weapons!", ephemeral=True)
                return

            embed = discord.Embed(title="🗡️ **Weapons**", color=discord.Color.red())
            view = CategoryView(self.user_id, self.inventory['weapons'], 'weapon', self)

            for weapon in self.inventory['weapons'][:6]:
                view.add_item(InventoryItemButton(weapon, 'weapon'))

            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            print(f"Error in show_weapons: {e}")
            traceback.print_exc()
            await interaction.response.send_message("An error occurred.", ephemeral=True)

    @discord.ui.button(label="🛡️ Armor", style=discord.ButtonStyle.primary, row=0)
    async def show_armor(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("Not your inventory!", ephemeral=True)
            return

        if not self.inventory['armor']:
            await interaction.response.send_message("You have no armor!", ephemeral=True)
            return

        embed = discord.Embed(title="🛡️ **Armor**", color=discord.Color.blue())
        view = CategoryView(self.user_id, self.inventory['armor'], 'armor', self)

        for armor in self.inventory['armor'][:6]:
            view.add_item(InventoryItemButton(armor, 'armor'))

        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="📿 Accessories", style=discord.ButtonStyle.primary, row=0)
    async def show_accessories(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("Not your inventory!", ephemeral=True)
            return

        if not self.inventory['accessories']:
            await interaction.response.send_message("You have no accessories!", ephemeral=True)
            return

        embed = discord.Embed(title="📿 **Accessories**", color=discord.Color.green())
        view = CategoryView(self.user_id, self.inventory['accessories'], 'accessory', self)

        for accessory in self.inventory['accessories'][:6]:
            view.add_item(InventoryItemButton(accessory, 'accessory'))

        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="🔙", style=discord.ButtonStyle.secondary, row=1)
    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("Not your inventory!", ephemeral=True)
            return
        await interaction.response.edit_message(embed=self.create_main_embed(), view=self)



# END




# =============================================================================
# SHOP SYSTEM – Persistent Interactive Shop
# =============================================================================
class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SHOP_IMAGE_URL = "https://cdn.discordapp.com/attachments/1470664051242700800/1471797792262455306/d4387e84d53fd24697a4218a9f6924a5.png?ex=6992e102&is=69918f82&hm=8a7bf535085e1dd0af98d977c5cc9766ecf463b73dbb5330444ff739b62c3571&"
        self.check_expired_purchases.start()
        self.booking_sessions = {}

    def cog_unload(self):
        self.check_expired_purchases.cancel()

    # Unicode fallbacks for emojis that are not custom
    RING_UNICODE = "💍"
    GEM_UNICODE = "💎"
    TREASURE_UNICODE = "🎁"

    def build_main_categories(self):
        embed = discord.Embed(
            title="🛍️ Shop Categories",
            description="Select a category to browse.",
            color=discord.Color.blue()
        )
        view = discord.ui.View(timeout=300)

        customization_emoji = discord.PartialEmoji(name="shadow", id=1477258013256454339)
        equipment_emoji = discord.PartialEmoji(name="zenith_sword", id=1477018808068866150)
        tools_emoji = discord.PartialEmoji(name="pickaxe", id=1477024057382666383)

        button_custom = discord.ui.Button(
            label="Customization",
            emoji=customization_emoji,
            style=discord.ButtonStyle.secondary,
            custom_id="shop_maincat_customization"
        )
        button_equip = discord.ui.Button(
            label="Equipment",
            emoji=equipment_emoji,
            style=discord.ButtonStyle.secondary,
            custom_id="shop_maincat_equipment"
        )
        button_tools = discord.ui.Button(
            label="Tools",
            emoji=tools_emoji,
            style=discord.ButtonStyle.secondary,
            custom_id="shop_maincat_tools"
        )

        view.add_item(button_custom)
        view.add_item(button_equip)
        view.add_item(button_tools)

        return embed, view

    # -------------------------------------------------------------------------
    # BACKGROUND TASK: Remove expired roles every minute
    # -------------------------------------------------------------------------
    @tasks.loop(minutes=1)
    async def check_expired_purchases(self):
        await self.bot.wait_until_ready()
        if not hasattr(self.bot, 'db_pool') or self.bot.db_pool is None:
            print("⏳ check_expired_purchases: db_pool not ready, skipping.")
            return

        try:
            async with self.bot.db_pool.acquire() as conn:
                # Fetch expired purchases that are still unused and have a role_id
                rows = await conn.fetch("""
                    SELECT up.purchase_id, up.user_id, si.role_id, si.guild_id, si.name
                    FROM user_purchases up
                    JOIN shop_items si ON up.item_id = si.item_id
                    WHERE up.expires_at < NOW() AND up.used = FALSE AND si.role_id IS NOT NULL
                """)

                print(f"🔍 Expiration check: found {len(rows)} expired purchases with roles.")

                for row in rows:
                    purchase_id = row['purchase_id']
                    user_id = row['user_id']
                    guild_id = row['guild_id']
                    role_id = row['role_id']
                    item_name = row['name']

                    guild = self.bot.get_guild(guild_id)
                    if not guild:
                        print(f"⚠️ Guild {guild_id} not found for expired item {item_name} (purchase {purchase_id}) – skipping, will retry.")
                        continue

                    member = guild.get_member(int(user_id))
                    if not member:
                        print(f"⚠️ Member {user_id} not found in guild {guild_id} for expired item {item_name} – deleting purchase record (member left).")
                        await conn.execute("DELETE FROM user_purchases WHERE purchase_id = $1", purchase_id)
                        continue

                    role = guild.get_role(role_id)
                    if not role:
                        print(f"⚠️ Role {role_id} not found in guild {guild_id} for expired item {item_name} – deleting purchase record.")
                        await conn.execute("DELETE FROM user_purchases WHERE purchase_id = $1", purchase_id)
                        continue

                    try:
                        await member.remove_roles(role, reason=f"Shop item expired: {item_name}")
                        print(f"✅ Removed expired role '{item_name}' from {member} (ID: {user_id})")
                        await conn.execute("DELETE FROM user_purchases WHERE purchase_id = $1", purchase_id)
                    except discord.Forbidden as e:
                        print(f"❌ Forbidden: Cannot remove role {role_id} from {user_id} – {e}")
                        # Do NOT delete record – will retry
                    except Exception as e:
                        print(f"⚠️ Unexpected error removing role: {e}")
                        import traceback
                        traceback.print_exc()
                        # Do NOT delete record

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

            if main_cat == "customization":
                await self.show_customization(interaction)
            elif main_cat == "equipment":
                await self.show_equipment(interaction)
            elif main_cat == "tools":
                await self.show_tools(interaction)

        elif custom_id == "shop_back_to_main":
            # Build the main categories embed and view
            embed, view = self.build_main_categories()
            # Edit the current message
            await interaction.response.edit_message(embed=embed, view=view)

        elif custom_id.startswith("shop_buy_"):
            item_id = int(custom_id.replace("shop_buy_", ""))
            await self.purchase_item(interaction, item_id)

    # -------------------------------------------------------------------------
    # SHOW MAIN CATEGORIES (using PartialEmoji for custom emojis)
    # -------------------------------------------------------------------------
    async def show_main_categories(self, interaction: discord.Interaction):
        embed, view = self.build_main_categories()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    # -------------------------------------------------------------------------
    # SHOW CUSTOMIZATION CATEGORY (uses Unicode for ring and gem)
    # -------------------------------------------------------------------------
    async def show_customization(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{CUSTOM_EMOJIS['shadow']} Customization",
            description="Choose what you'd like to customize.",
            color=discord.Color.purple()
        )
        view = discord.ui.View(timeout=300)

        async with self.bot.db_pool.acquire() as conn:
            role_items = await conn.fetch("""
                SELECT item_id, name, description, price
                FROM shop_items
                WHERE type = 'role'
                ORDER BY price ASC
            """)
            color_items = await conn.fetch("""
                SELECT item_id, name, description, price
                FROM shop_items
                WHERE type = 'color'
                ORDER BY price ASC
            """)

        if role_items:
            for item in role_items:
                if 'treasure carriage' in item['name'].lower():
                    button_emoji = discord.PartialEmoji(name="treasure_carriage", id=1477354550502625601)
                else:                
                    button_emoji = None

                button = discord.ui.Button(
                    label=f"{item['name'][:15]} – {item['price']}g",
                    emoji=button_emoji,
                    style=discord.ButtonStyle.primary,
                    custom_id=f"shop_buy_{item['item_id']}"
                )
                view.add_item(button)

        if color_items:
            for item in color_items:
                button = discord.ui.Button(
                    label=f"🎨 {item['name'][:15]} – {item['price']}g",
                    style=discord.ButtonStyle.primary,
                    custom_id=f"shop_buy_{item['item_id']}"
                )
                view.add_item(button)

        if not role_items and not color_items:
            embed.description = "No customization items available yet."

        back = discord.ui.Button(
            label="◀ Back",
            style=discord.ButtonStyle.secondary,
            custom_id="shop_back_to_main"
        )
        view.add_item(back)

        await interaction.response.edit_message(embed=embed, view=view)
    # -------------------------------------------------------------------------
    # SHOW EQUIPMENT CATEGORY (all random boxes)
    # -------------------------------------------------------------------------
    async def show_equipment(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{CUSTOM_EMOJIS['zenith_sword']} Equipment",
            description="Purchase random boxes to get weapons, armor, and accessories with random stats!",
            color=discord.Color.orange()
        )
        view = discord.ui.View(timeout=300)

        async with self.bot.db_pool.acquire() as conn:
            weapon_boxes = await conn.fetch("""
                SELECT item_id, name, description, price
                FROM shop_items
                WHERE type = 'random_weapon_box'
                ORDER BY price ASC
            """)
            armor_boxes = await conn.fetch("""
                SELECT item_id, name, description, price
                FROM shop_items
                WHERE type = 'random_gear_box'
                ORDER BY price ASC
            """)
            accessory_boxes = await conn.fetch("""
                SELECT item_id, name, description, price
                FROM shop_items
                WHERE type = 'random_accessories_box'
                ORDER BY price ASC
            """)

        if weapon_boxes:
            for box in weapon_boxes:
                button = discord.ui.Button(
                    label=f"🗡️ {box['name'][:15]} – {box['price']}g",
                    style=discord.ButtonStyle.primary,
                    custom_id=f"shop_buy_{box['item_id']}"
                )
                view.add_item(button)

        if armor_boxes:
            for box in armor_boxes:
                button = discord.ui.Button(
                    label=f"🛡️ {box['name'][:15]} – {box['price']}g",
                    style=discord.ButtonStyle.primary,
                    custom_id=f"shop_buy_{box['item_id']}"
                )
                view.add_item(button)

        if accessory_boxes:
            for box in accessory_boxes:
                button = discord.ui.Button(
                    label=f"💍 {box['name'][:15]} – {box['price']}g",
                    style=discord.ButtonStyle.primary,
                    custom_id=f"shop_buy_{box['item_id']}"
                )
                view.add_item(button)

        if not weapon_boxes and not armor_boxes and not accessory_boxes:
            embed.description = "No equipment boxes available yet."

        back = discord.ui.Button(
            label="◀ Back",
            style=discord.ButtonStyle.secondary,
            custom_id="shop_back_to_main"
        )
        view.add_item(back)

        await interaction.response.edit_message(embed=embed, view=view)

    # -------------------------------------------------------------------------
    # SHOW TOOLS CATEGORY (pickaxes)
    # -------------------------------------------------------------------------
    async def show_tools(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{CUSTOM_EMOJIS['pickaxe']} Tools",
            description="Purchase tools to enhance your gameplay!",
            color=discord.Color.orange()
        )
        view = discord.ui.View(timeout=300)

        async with self.bot.db_pool.acquire() as conn:
            pickaxes = await conn.fetch("""
                SELECT item_id, name, description, price
                FROM shop_items
                WHERE type = 'pickaxe'
                ORDER BY price ASC
            """)

        if pickaxes:
            tools_info = (
                f"{CUSTOM_EMOJIS['pickaxe']} **Pickaxes**\n\n"                
                f"**Purchase a pickaxe to begin your mining journey!**"
            )
            embed.description = tools_info

            for pick in pickaxes:
                button = discord.ui.Button(
                    label=f"⛏️ {pick['name'][:15]} – {pick['price']}g",
                    style=discord.ButtonStyle.primary,
                    custom_id=f"shop_buy_{pick['item_id']}"
                )
                view.add_item(button)
        else:
            embed.description = "No tools available yet."

        back = discord.ui.Button(
            label="◀ Back",
            style=discord.ButtonStyle.secondary,
            custom_id="shop_back_to_main"
        )
        view.add_item(back)

        await interaction.response.edit_message(embed=embed, view=view)

    # -------------------------------------------------------------------------
    # PURCHASE ITEM HANDLER (includes all box types)
    # -------------------------------------------------------------------------
    async def purchase_item(self, interaction: discord.Interaction, item_id: int):
        await interaction.response.defer(ephemeral=True)

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

            # Get all weapon items from shop_items
            async with self.bot.db_pool.acquire() as conn:
                weapons = await conn.fetch("""
                    SELECT item_id, name, description FROM shop_items
                    WHERE type = 'weapon'
                """)
            if not weapons:
                await interaction.followup.send("❌ No weapons available in the shop.", ephemeral=True)
                return

            chosen = random.choice(weapons)
            weapon_name = chosen['name']
            weapon_item_id = chosen['item_id']
            description = chosen['description'] or "A random weapon."

            # Generate random stats
            attack = random.randint(405, 750)
            bleed_chance = round(random.uniform(5.0, 9.0), 1)
            crit_chance = round(random.uniform(9.0, 25.0), 1)
            crit_damage = round(random.uniform(23.0, 35.0), 1)

            async with self.bot.db_pool.acquire() as conn:
                purchase_id = await conn.fetchval("""
                    INSERT INTO user_purchases (user_id, item_id, price_paid, expires_at)
                    VALUES ($1, $2, $3, $4)
                    RETURNING purchase_id
                """, user_id, item['item_id'], item['price'], now + timedelta(days=7))

                await conn.execute("""
                    INSERT INTO user_weapons (
                        user_id, weapon_item_id, attack, purchase_id, description,
                        bleeding_chance, crit_chance, crit_damage
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, user_id, weapon_item_id, attack, purchase_id, description,
                   bleed_chance, crit_chance, crit_damage)

            box_embed = discord.Embed(
                title="📦 Random Weapon Box",
                description=f"{self.TREASURE_UNICODE} Opening box...\nYou received: **{weapon_name}**",
                color=discord.Color.purple()
            )
            await interaction.followup.send(embed=box_embed, ephemeral=True)

            weapon_embed = discord.Embed(
                title=f"{get_item_emoji(weapon_name, 'weapon')} **{weapon_name}** (+{attack} ATK)",
                description=description,
                color=discord.Color.red()
            )
            stats = (
                f"⚔️ **ATK:** {attack}\n"
                f"🩸 **Bleed Chance:** {bleed_chance}%\n"
                f"⚡ **Crit Chance:** {crit_chance}%\n"
                f"💥 **Crit Damage:** {crit_damage}%"
            )         
            await interaction.followup.send(embed=weapon_embed, ephemeral=True)

            await self.send_shop_log(interaction.guild, interaction.user, item['name'], item['price'], balance['gems'] - item['price'])
            return

        # ========== RANDOM ARMOR BOX ==========
        if item['type'] == 'random_gear_box':
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

            # Armor sets and pieces
            armor_sets = {
                'bilari': {'name': 'Bilari', 'color': 0x4A90E2},
                'cryo': {'name': 'Cryo', 'color': 0x00FFFF},
                'bane': {'name': 'Bane', 'color': 0x8B0000},
            }
            pieces = ['helm', 'suit', 'gauntlets', 'boots']
            piece_ranges = {
                'helm': {'def': (441, 946), 'hp': (1000, 2000), 'reflect': False},
                'suit': {'def': (959, 1549), 'hp': (1500, 3000), 'reflect': (5, 15)},
                'gauntlets': {'def': (441, 946), 'hp': (1000, 2000), 'reflect': False},
                'boots': {'def': (210, 705), 'hp': (700, 1400), 'reflect': False},
            }

            set_name = random.choice(list(armor_sets.keys()))
            set_data = armor_sets[set_name]
            piece = random.choice(pieces)
            ranges = piece_ranges[piece]

            defense = random.randint(ranges['def'][0], ranges['def'][1])
            hp_bonus = random.randint(ranges['hp'][0], ranges['hp'][1])
            reflect = random.randint(ranges['reflect'][0], ranges['reflect'][1]) if ranges['reflect'] else 0

            # Map piece to emoji key (bilari_helm, bilari_armor, etc.)
            emoji_map = {
                'helm': '_helm',
                'suit': '_armor',
                'gauntlets': '_gloves',
                'boots': '_boots'
            }
            emoji_key = f"{set_name}{emoji_map[piece]}"
            emoji = CUSTOM_EMOJIS.get(emoji_key, '🛡️')
            armor_name = f"{set_data['name']} {piece.capitalize()}"

            async with self.bot.db_pool.acquire() as conn:
                # Check if armor_type exists
                armor_type = await conn.fetchrow("SELECT armor_id FROM armor_types WHERE name = $1", armor_name)
                if not armor_type:
                    armor_type = await conn.fetchrow("""
                        INSERT INTO armor_types (name, slot, defense, hp_bonus, reflect_damage, set_name)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        RETURNING armor_id
                    """, armor_name, piece, defense, hp_bonus, reflect, set_data['name'])
                    armor_id = armor_type['armor_id']
                else:
                    armor_id = armor_type['armor_id']

                purchase_id = await conn.fetchval("""
                    INSERT INTO user_purchases (user_id, item_id, price_paid, expires_at)
                    VALUES ($1, $2, $3, $4)
                    RETURNING purchase_id
                """, user_id, item['item_id'], item['price'], now + timedelta(days=7))

                await conn.execute("""
                    INSERT INTO user_armor (user_id, armor_id, defense, hp_bonus, reflect_damage, set_name, purchase_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, user_id, armor_id, defense, hp_bonus, reflect, set_data['name'], purchase_id)

            box_embed = discord.Embed(
                title="📦 Random Armor Box",
                description=f"{self.TREASURE_UNICODE} Opening box...\nYou received: **{armor_name}**",
                color=set_data['color']
            )
            await interaction.followup.send(embed=box_embed, ephemeral=True)

            armor_embed = discord.Embed(
                title=f"{emoji} **{armor_name}**",
                color=set_data['color']
            )
            stats = f"🛡️ **DEF:** {defense}\n❤️ **HP:** +{hp_bonus}"
            if reflect:
                stats += f"\n🔄 **Reflect:** {reflect}%"
            
            await interaction.followup.send(embed=armor_embed, ephemeral=True)

            await self.send_shop_log(interaction.guild, interaction.user, item['name'], item['price'], balance['gems'] - item['price'])
            return

        # ========== RANDOM ACCESSORY BOX ==========
        if item['type'] == 'random_accessories_box':
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

            # Accessory sets
            accessory_sets = {
                'champion': {'name': 'Champion', 'color': 0xFFD700, 'stat': 'atk', 'range': (55, 150)},
                'defender': {'name': 'Defender', 'color': 0x4A90E2, 'stat': 'def', 'range': (55, 150)},
                'angel': {'name': 'Angel', 'color': 0xFF69B4, 'stat': 'atk', 'range': (55, 300)},
            }
            piece_types = ['ring', 'earring', 'pendant']
            slots = {
                'ring': ['ring1', 'ring2'],
                'earring': ['earring1', 'earring2'],
                'pendant': ['pendant']
            }
            emoji_map = {
                ('champion', 'ring'): 'champ_ring',
                ('champion', 'earring'): 'champ_earring',
                ('champion', 'pendant'): 'champ_pen',
                ('defender', 'ring'): 'def_ring',
                ('defender', 'earring'): 'def_earring',
                ('defender', 'pendant'): 'def_pen',
                ('angel', 'ring'): 'wing_ring',
                ('angel', 'earring'): 'harp_earring',
                ('angel', 'pendant'): 'angel_pen',
            }

            set_name = random.choice(list(accessory_sets.keys()))
            set_data = accessory_sets[set_name]
            piece = random.choice(piece_types)

            # Check available slot
            async with self.bot.db_pool.acquire() as conn:
                taken = await conn.fetch("SELECT slot FROM user_accessories WHERE user_id = $1", user_id)
                taken_slots = [row['slot'] for row in taken]
                available_slots = [s for s in slots[piece] if s not in taken_slots]
                if not available_slots:
                    await interaction.followup.send(f"❌ You already have all {piece} slots filled. Unequip one first.", ephemeral=True)
                    return
                slot = random.choice(available_slots)

            bonus_value = random.randint(set_data['range'][0], set_data['range'][1])
            emoji_key = emoji_map.get((set_name, piece), 'ring_1')
            emoji = CUSTOM_EMOJIS.get(emoji_key, self.RING_UNICODE)
            accessory_name = f"{set_data['name']} {piece.capitalize()}"

            async with self.bot.db_pool.acquire() as conn:
                acc_type = await conn.fetchrow("""
                    INSERT INTO accessory_types (name, slot, bonus_stat, bonus_value, set_name)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING accessory_id
                """, accessory_name, slot, set_data['stat'], bonus_value, set_name)

                purchase_id = await conn.fetchval("""
                    INSERT INTO user_purchases (user_id, item_id, price_paid, expires_at)
                    VALUES ($1, $2, $3, $4)
                    RETURNING purchase_id
                """, user_id, item['item_id'], item['price'], now + timedelta(days=7))

                await conn.execute("""
                    INSERT INTO user_accessories (user_id, accessory_id, bonus_value, slot, set_name, purchase_id)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, user_id, acc_type['accessory_id'], bonus_value, slot, set_name, purchase_id)

            box_embed = discord.Embed(
                title="📦 Random Accessory Box",
                description=f"{self.TREASURE_UNICODE} Opening box...\nYou received: **{accessory_name}**",
                color=set_data['color']
            )
            await interaction.followup.send(embed=box_embed, ephemeral=True)

            acc_embed = discord.Embed(
                title=f"{emoji} **{accessory_name}**",
                color=set_data['color']
            )
            stat_emoji = '⚔️' if set_data['stat'] == 'atk' else '🛡️'
            stats = f"{stat_emoji} **{set_data['stat'].upper()}:** +{bonus_value}\n📌 **Slot:** {slot}"
            
            await interaction.followup.send(embed=acc_embed, ephemeral=True)

            await self.send_shop_log(interaction.guild, interaction.user, item['name'], item['price'], balance['gems'] - item['price'])
            return

        # ========== WEAPON PURCHASE (direct) ==========
        if item['type'] == 'weapon':
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

            attack = random.randint(50, 500)  # or your desired range
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO user_weapons (user_id, weapon_item_id, attack)
                    VALUES ($1, $2, $3)
                """, user_id, item_id, attack)

            desc = item.get('description') or "No description available."
            embed = discord.Embed(
                title=f"{item['name']} (+{attack} ATK)",
                description=f"*{desc}*",
                color=discord.Color.red()
            )
            if item.get('image_url'):
                embed.set_image(url=item['image_url'])
            embed.set_footer(text="Added to your collection!")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # ========== PICKAXE PURCHASE ==========
        if item['type'] == 'pickaxe':
            balance = await currency_system.get_balance(user_id)
            if balance['gems'] < item['price']:
                embed = discord.Embed(
                    title="❌ Insufficient Gems",
                    description=f"You need **{item['price']} gems** to buy **{item['name']}**.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            async with self.bot.db_pool.acquire() as conn:
                has_pickaxe = await conn.fetchval("SELECT has_pickaxe FROM player_stats WHERE user_id = $1", user_id)
                if has_pickaxe:
                    await interaction.followup.send("❌ You already own a pickaxe! You cannot buy another.", ephemeral=True)
                    return

            success = await currency_system.deduct_gems(user_id, item['price'], f"🛒 Purchased {item['name']}")
            if not success:
                await interaction.followup.send("❌ Failed to deduct gems.", ephemeral=True)
                return

            await self.bot.get_cog('CullingGame').ensure_player_stats(user_id)
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("UPDATE player_stats SET has_pickaxe = TRUE WHERE user_id = $1", user_id)

            embed = discord.Embed(
                title="✅ Pickaxe Purchased!",
                description=f"You now own **{item['name']}**. You can start mining!",
                color=discord.Color.gold()
            )
            if item.get('image_url'):
                embed.set_image(url=item['image_url'])
            await interaction.followup.send(embed=embed, ephemeral=True)

            await self.send_shop_log(interaction.guild, interaction.user, item['name'], item['price'], balance['gems'] - item['price'])
            return

        # ========== NON-WEAPON ITEMS (roles/colors) ==========
        # Check for existing active purchase
        async with self.bot.db_pool.acquire() as conn:
            active = await conn.fetchval("""
                SELECT 1 FROM user_purchases
                WHERE user_id = $1 AND item_id = $2 AND expires_at > $3 AND used = FALSE
            """, user_id, item_id, now)
        if active:
            embed = discord.Embed(
                title="❌ Already Owned",
                description="You already own this item and it hasn't expired yet.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

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

        success = await currency_system.deduct_gems(user_id, item['price'], f"🛒 Purchased {item['name']}")
        if not success:
            await interaction.followup.send("❌ Failed to deduct gems.", ephemeral=True)
            return

        expires_at = now + timedelta(days=7)
        async with self.bot.db_pool.acquire() as conn:
            purchase_id = await conn.fetchval("""
                INSERT INTO user_purchases (user_id, item_id, price_paid, expires_at)
                VALUES ($1, $2, $3, $4)
                RETURNING purchase_id
            """, user_id, item_id, item['price'], expires_at)

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

        # Special case: Treasure Carriage
        if item['name'].lower() == "treasure carriage":
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
                    f"Click the button below to continue and book your ride."
                ),
                color=discord.Color.gold()
            )
            embed.set_footer(text="The item will be removed after you book your ride.")
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            return

        await self.send_shop_log(interaction.guild, interaction.user, item['name'], item['price'], new_balance['gems'])

    # -------------------------------------------------------------------------
    # SECRET SHOP (Treasure Carriage booking)
    # -------------------------------------------------------------------------
    async def secret_shop_button(self, interaction: discord.Interaction, purchase_id: int):
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
            try:
                dt = datetime.strptime(message.content.strip(), "%Y-%m-%d %H:%M")
                dt = dt.replace(tzinfo=timezone.utc)
                if dt < datetime.now(timezone.utc):
                    await message.channel.send("❌ Time must be in future. Try again:")
                    return
            except ValueError:
                await message.channel.send("❌ Invalid format. Use `YYYY-MM-DD HH:MM`")
                return

            purchase_id = session["purchase_id"]
            ign = session["ign"]
            dt_naive = dt.replace(tzinfo=None)

            try:
                async with self.bot.db_pool.acquire() as conn:
                    async with conn.transaction():
                        await conn.execute("""
                            INSERT INTO carriage_bookings (user_id, ign, ride_time, purchase_id)
                            VALUES ($1, $2, $3, $4)
                        """, str(user_id), ign, dt_naive, purchase_id)
                        await conn.execute("UPDATE user_purchases SET used = TRUE WHERE purchase_id = $1", purchase_id)
            except Exception as e:
                print(f"[DEBUG TIME] Database error: {e}")
                await message.channel.send("❌ Database error – booking failed. Please contact an admin.")
                return

            # Remove role if any
            try:
                async with self.bot.db_pool.acquire() as conn:
                    row = await conn.fetchrow("""
                        SELECT si.role_id, si.guild_id
                        FROM shop_items si
                        JOIN user_purchases up ON up.item_id = si.item_id
                        WHERE up.purchase_id = $1
                    """, purchase_id)
                if row:
                    guild = self.bot.get_guild(row['guild_id'])
                    if guild:
                        member = guild.get_member(user_id)
                        if member:
                            role = guild.get_role(row['role_id'])
                            if role:
                                await member.remove_roles(role, reason="Carriage used")
            except Exception as e:
                print(f"[DEBUG TIME] Role removal error: {e}")

            embed = discord.Embed(title="✅ Schedule Confirmed!", color=discord.Color.green())
            embed.description = f"**IGN:** {ign}\n**Ride Time:** <t:{int(dt.timestamp())}:F>\n\nYour ride has been scheduled. Please wait for confirmation."
            await message.channel.send(embed=embed)

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
                        await log_channel.send(embed=log_embed)
                    except Exception as e:
                        print(f"[DEBUG TIME] Admin log error: {e}")

            del self.booking_sessions[user_id]

    # -------------------------------------------------------------------------
    # SHOP LOGS
    # -------------------------------------------------------------------------
    async def send_shop_log(self, guild: discord.Guild, user: discord.Member, item_name: str, price: int, balance: int):
        channel = discord.utils.get(guild.text_channels, name="shop logs")
        if not channel:
            return
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

    # -------------------------------------------------------------------------
    # ADMIN COMMANDS
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
                "`!!shopadmin edit description <item_id> <new_desc>`\n"
                "`!!shopadmin addweaponbox <name> <price> [description]`\n"
                "`!!shopadmin addarmorbox <name> <price> [description]`\n"
                "`!!shopadmin addaccessorybox <name> <price> [description]`\n"
                "`!!shopadmin addpickaxe <name> <price> [description]`"
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

        if item_type == 'role':
            if not role_id:
                await ctx.send("❌ For role items, you must provide a role_id.")
                return
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
        if image_url and not (image_url.startswith('http://') or image_url.startswith('https://')):
            await ctx.send("❌ Image URL must start with `http://` or `https://`.")
            return
        async with self.bot.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO shop_items (name, description, price, type, role_id, color_hex, guild_id, image_url)
                VALUES ($1, $2, $3, 'weapon', NULL, NULL, $4, $5)
            """, name, description, price, ctx.guild.id, image_url)
        await ctx.send(f"✅ Added weapon **{name}** for **{price} gems**.")

    @shop_admin.command(name='addweaponbox')
    @commands.has_permissions(administrator=True)
    async def add_weapon_box(self, ctx, name: str, price: int, description: str = "Open to get a random weapon!"):
        async with self.bot.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO shop_items (name, description, price, type, guild_id)
                VALUES ($1, $2, $3, 'random_weapon_box', $4)
            """, name, description, price, ctx.guild.id)
        await ctx.send(f"✅ Added random weapon box **{name}** for **{price} gems**.")

    @shop_admin.command(name='addarmorbox')
    @commands.has_permissions(administrator=True)
    async def add_armor_box(self, ctx, name: str, price: int, description: str = "Contains a random piece of armor!"):
        async with self.bot.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO shop_items (name, description, price, type, guild_id)
                VALUES ($1, $2, $3, 'random_gear_box', $4)
            """, name, description, price, ctx.guild.id)
        await ctx.send(f"✅ Added random armor box **{name}** for **{price} gems**.")

    @shop_admin.command(name='addaccessorybox')
    @commands.has_permissions(administrator=True)
    async def add_accessory_box(self, ctx, name: str, price: int, description: str = "Contains a random accessory piece!"):
        async with self.bot.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO shop_items (name, description, price, type, guild_id)
                VALUES ($1, $2, $3, 'random_accessories_box', $4)
            """, name, description, price, ctx.guild.id)
        await ctx.send(f"✅ Added random accessory box **{name}** for **{price} gems**.")

    @shop_admin.command(name='addpickaxe')
    @commands.has_permissions(administrator=True)
    async def add_pickaxe(self, ctx, name: str, price: int, description: str = "A sturdy pickaxe for mining."):
        async with self.bot.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO shop_items (name, description, price, type, guild_id)
                VALUES ($1, $2, $3, 'pickaxe', $4)
            """, name, description, price, ctx.guild.id)
        await ctx.send(f"✅ Added pickaxe **{name}** for **{price} gems**.")

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

    # -------------------------------------------------------------------------
    # UTILITY COMMANDS
    # -------------------------------------------------------------------------
    @commands.command(name='listweapons')
    async def list_weapons(self, ctx):
        user_id = str(ctx.author.id)
        async with self.bot.db_pool.acquire() as conn:
            weapons = await conn.fetch("""
                SELECT uw.id, COALESCE(si.name, uw.generated_name) as name, uw.attack
                FROM user_weapons uw
                LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                WHERE uw.user_id = $1
                ORDER BY uw.purchased_at DESC
            """, user_id)
        if not weapons:
            await ctx.send("You don't own any weapons.")
            return
        lines = [f"ID {w['id']}: {w['name']} (+{w['attack']} ATK)" for w in weapons]
        await ctx.send("**Your weapons:**\n" + "\n".join(lines))

    @commands.command(name='removeweapon')
    async def remove_weapon(self, ctx, weapon_id: int):
        user_id = str(ctx.author.id)
        async with self.bot.db_pool.acquire() as conn:
            weapon = await conn.fetchrow(
                "SELECT id, COALESCE(si.name, uw.generated_name) as name "
                "FROM user_weapons uw "
                "LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id "
                "WHERE uw.id = $1 AND uw.user_id = $2",
                weapon_id, user_id
            )
            if not weapon:
                await ctx.send("❌ Weapon not found or does not belong to you.")
                return
            confirm = await ctx.send(f"Are you sure you want to delete **{weapon['name']}**? Reply with `yes` within 30 seconds.")
            def check(m): return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "yes"
            try:
                await self.bot.wait_for('message', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("⏰ Deletion cancelled.")
                return
            await conn.execute("DELETE FROM user_weapons WHERE id = $1", weapon_id)
            await ctx.send(f"✅ Weapon **{weapon['name']}** deleted.")


    @bot.command()
    @commands.has_permissions(administrator=True)
    async def wipeallweapons(ctx):
        """⚠️ DANGER: Delete ALL weapons from ALL users."""
        # Confirmation
        confirm = await ctx.send("⚠️ **WARNING:** This will delete **ALL weapons** from **ALL users**. This cannot be undone. Type `CONFIRM` within 30 seconds to proceed.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content == "CONFIRM"

        try:
            await bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("❌ Deletion cancelled (timeout).")
            return

        # Perform deletion
        async with bot.db_pool.acquire() as conn:
            result = await conn.execute("DELETE FROM user_weapons")
            count = result.split()[1]  # Number of deleted rows
            await ctx.send(f"✅ Deleted **{count}** weapons from all users.")


    @commands.command(name='adminweapons')
    @commands.has_permissions(administrator=True)
    async def admin_list_weapons(self, ctx, user: discord.Member):
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
        embed = discord.Embed(title=f"🗡️ {user.display_name}'s Weapons", color=discord.Color.blue())
        for row in rows:
            embed.add_field(name=f"ID: {row['id']}", value=f"**{row['name']}** (+{row['attack']} ATK)", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='adminremoveweapon')
    @commands.has_permissions(administrator=True)
    async def admin_remove_weapon(self, ctx, weapon_id: int):
        async with self.bot.db_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT uw.id, si.name, uw.user_id, uw.purchase_id
                FROM user_weapons uw
                JOIN shop_items si ON uw.weapon_item_id = si.item_id
                WHERE uw.id = $1
            """, weapon_id)
            if not row:
                await ctx.send(f"❌ Weapon with ID `{weapon_id}` not found.")
                return
            await conn.execute("DELETE FROM user_weapons WHERE id = $1", weapon_id)
            if row['purchase_id']:
                await conn.execute("UPDATE user_purchases SET used = TRUE WHERE purchase_id = $1", row['purchase_id'])
        user = self.bot.get_user(int(row['user_id']))
        user_mention = user.mention if user else f"User ID {row['user_id']}"
        embed = discord.Embed(title="✅ Weapon Removed", color=discord.Color.green())
        embed.description = f"Removed **{row['name']}** (ID: {weapon_id}) from {user_mention}. They can now buy it again."
        await ctx.send(embed=embed)

    @commands.command(name='clear_carriage')
    @commands.has_permissions(administrator=True)
    async def clear_carriage(self, ctx, user: discord.Member = None):
        target = user or ctx.author
        user_id = str(target.id)
        if not self.bot.db_pool:
            await ctx.send("❌ Database not connected.")
            return
        async with self.bot.db_pool.acquire() as conn:
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
            await conn.execute("UPDATE user_purchases SET used = TRUE WHERE purchase_id = $1", purchase_id)
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

# Make sure to add the cog to the bot after this definition




    # INVENTORY COMMAND
    @commands.command(name='myinventory')
    async def my_inventory(self, ctx):
        """Display your interactive MMORPG inventory"""         
        user_id = str(ctx.author.id)

        async with self.bot.db_pool.acquire() as conn:
            weapons = await conn.fetch("""
                SELECT uw.id, COALESCE(si.name, uw.generated_name) as name,
                       uw.attack, uw.equipped, uw.description,
                       COALESCE(si.image_url, uw.image_url) as image_url,
                       r.color as rarity_color
                FROM user_weapons uw
                LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                LEFT JOIN weapon_variants v ON uw.variant_id = v.variant_id
                LEFT JOIN rarities r ON v.rarity_id = r.rarity_id
                WHERE uw.user_id = $1
                ORDER BY uw.equipped DESC, uw.purchased_at DESC
            """, user_id)

            armor = await conn.fetch("""
                SELECT ua.id, at.name, ua.defense, ua.equipped, at.slot,
                       at.image_url, at.description, r.color as rarity_color
                FROM user_armor ua
                JOIN armor_types at ON ua.armor_id = at.armor_id
                LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                WHERE ua.user_id = $1
                ORDER BY ua.equipped DESC, ua.purchased_at DESC
            """, user_id)

            accessories = await conn.fetch("""
                SELECT ua.id, at.name, ua.bonus_value, at.bonus_stat,
                       ua.equipped, ua.slot, at.image_url, at.description,
                       r.color as rarity_color
                FROM user_accessories ua
                JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                WHERE ua.user_id = $1
                ORDER BY ua.equipped DESC, ua.purchased_at DESC
            """, user_id)

        balance = await currency_system.get_balance(user_id)

        inventory_data = {
            'weapons': [dict(w) for w in weapons],
            'armor': [dict(a) for a in armor],
            'accessories': [dict(a) for a in accessories],
            'gems': balance['gems']
        }

        view = InventoryView(user_id, inventory_data, self)
        await ctx.send(embed=view.create_main_embed(), view=view)


    @commands.command(name='myprofile')
    async def my_profile(self, ctx):
        """Display your character profile with all equipped gear"""
        user_id = str(ctx.author.id)

        async with self.bot.db_pool.acquire() as conn:
            player = await conn.fetchrow("""
                SELECT hp, max_hp, energy, max_energy, defense 
                FROM player_stats WHERE user_id = $1
            """, user_id)

            weapon = await conn.fetchrow("""
                SELECT COALESCE(si.name, uw.generated_name) as name, uw.attack,
                       COALESCE(si.image_url, uw.image_url) as image_url
                FROM user_weapons uw
                LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                WHERE uw.user_id = $1 AND uw.equipped = TRUE
                LIMIT 1
            """, user_id)

            armor = await conn.fetch("""
                SELECT at.name, ua.defense, at.slot, at.image_url
                FROM user_armor ua
                JOIN armor_types at ON ua.armor_id = at.armor_id
                WHERE ua.user_id = $1 AND ua.equipped = TRUE
            """, user_id)

            accessories = await conn.fetch("""
                SELECT at.name, ua.bonus_value, at.bonus_stat, ua.slot, at.image_url
                FROM user_accessories ua
                JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                WHERE ua.user_id = $1 AND ua.equipped = TRUE
            """, user_id)

        total_atk = weapon['attack'] if weapon else 0
        total_def = player['defense'] if player else 0

        for acc in accessories:
            if acc['bonus_stat'] == 'atk':
                total_atk += acc['bonus_value']
            elif acc['bonus_stat'] == 'def':
                total_def += acc['bonus_value']

        embed = discord.Embed(
            title=f"📜 **{ctx.author.display_name}'s Profile**",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        if player:
            hp_percent = (player['hp'] / player['max_hp']) * 10
            hp_bar = "❤️" + "🟥" * int(hp_percent) + "⬛" * (10 - int(hp_percent))
            energy_percent = (player['energy'] / player['max_energy']) * 10
            energy_bar = "⚡" + "🟨" * int(energy_percent) + "⬛" * (10 - int(energy_percent))

            stats = (
                f"{hp_bar} `{player['hp']}/{player['max_hp']} HP`\n"
                f"{energy_bar} `{player['energy']}/{player['max_energy']} Energy`\n"
                f"⚔️ **ATK:** `{total_atk}` | 🛡️ **DEF:** `{total_def}`"
            )
            embed.description = stats

        equipment = []

        if weapon:
            equipment.append(f"⚔️ **Weapon:** {weapon['name']} (+{weapon['attack']} ATK)")
            if weapon['image_url']:
                embed.set_image(url=weapon['image_url'])
        else:
            equipment.append("⚔️ **Weapon:** `None`")

        armor_dict = {a['slot']: a for a in armor}
        equipment.append(f"🪖 **Helm:** {armor_dict.get('helm', {}).get('name', '`None`')}")
        equipment.append(f"👕 **Armor:** {armor_dict.get('armor', {}).get('name', '`None`')}")
        equipment.append(f"🧤 **Gloves:** {armor_dict.get('gloves', {}).get('name', '`None`')}")
        equipment.append(f"👢 **Boots:** {armor_dict.get('boots', {}).get('name', '`None`')}")

        embed.add_field(name="🎽 **Armor**", value="\n".join(equipment[1:]), inline=False)

        acc_dict = {a['slot']: a for a in accessories}
        acc_list = []
        acc_list.append(f"💍 **Ring 1:** {acc_dict.get('ring1', {}).get('name', '`None`')}")
        acc_list.append(f"💍 **Ring 2:** {acc_dict.get('ring2', {}).get('name', '`None`')}")
        acc_list.append(f"📿 **Pendant:** {acc_dict.get('pendant', {}).get('name', '`None`')}")
        acc_list.append(f"👂 **Earring 1:** {acc_dict.get('earring1', {}).get('name', '`None`')}")
        acc_list.append(f"👂 **Earring 2:** {acc_dict.get('earring2', {}).get('name', '`None`')}")

        embed.add_field(name="📿 **Accessories**", value="\n".join(acc_list), inline=False)
        embed.add_field(name="🐾 **Pet**", value="`Coming Soon`", inline=False)
        embed.insert_field_at(0, name="🗡️ **Weapon**", value=equipment[0], inline=False)

        await ctx.send(embed=embed)




# CULLING GAME 

class CullingGame(commands.Cog):
    def __init__(self, bot, currency_system):
        self.bot = bot
        self.currency = currency_system
        self.mining_channel = None
        self.mining_message = None
        self.energy_regen.start()
        self.check_max_mining.start()

    async def load_mining_messages(self, guild_id: int):
        """Reattach the mining view after restart."""
        async with self.bot.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT channel_id, message_id FROM mining_config WHERE guild_id = $1",
                guild_id   
            )
            if not row:
                print(f"ℹ️ No mining config found for guild {guild_id}.")
                return
            channel = self.bot.get_channel(row['channel_id'])
            if not channel:
                print(f"❌ Mining channel not found for guild {guild_id}.")
                return
            try:
                msg = await channel.fetch_message(row['message_id'])
                self.mining_channel = channel.id
                self.mining_message = msg
                view = MiningMainView(self.bot, self)
                await msg.edit(view=view)
                print(f"✅ Reattached mining view in #{channel.name} (guild {guild_id})")
            except Exception as e:
                print(f"❌ Failed to reattach mining view for guild {guild_id}: {e}")
                traceback.print_exc()
                async with self.bot.db_pool.acquire() as conn2:
                    await conn2.execute("DELETE FROM mining_config WHERE guild_id = $1", guild_id)

    def cog_unload(self):
        self.energy_regen.cancel()
        self.check_max_mining.cancel()

# ------------------------------------------------------------------
    # Energy Regen Task
    # ------------------------------------------------------------------
    @tasks.loop(hours=1)
    async def energy_regen(self):
        """Give 1 energy every hour to all players (up to max)."""
        async with self.bot.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT user_id, energy, max_energy, last_energy_regen
                FROM player_stats
                WHERE energy < max_energy
            """)
            now = datetime.utcnow()  # naive UTC
            for row in rows:
                last = row['last_energy_regen']
                if last.tzinfo is not None:
                    last = last.replace(tzinfo=None)
                if (now - last) >= timedelta(hours=1):
                    new_energy = min(row['energy'] + 1, row['max_energy'])
                    await conn.execute("""
                        UPDATE player_stats
                        SET energy = $1, last_energy_regen = $2
                        WHERE user_id = $3
                    """, new_energy, now, row['user_id'])

    @energy_regen.before_loop
    async def before_energy_regen(self):
        await self.bot.wait_until_ready()
        while self.bot.db_pool is None:
            await asyncio.sleep(1)


    @tasks.loop(minutes=30)  # Check every 30 minutes
    async def check_max_mining(self):
        """Automatically stop miners who have reached 12 hours."""
        async with self.bot.db_pool.acquire() as conn:
            # Get all active miners
            miners = await conn.fetch("""
                SELECT user_id, mining_start, stolen_gems 
                FROM player_stats 
                WHERE mining_start IS NOT NULL
            """)
        
            now = datetime.utcnow()
            for miner in miners:
                user_id = miner['user_id']
                start = miner['mining_start']
                if start.tzinfo is not None:
                    start = start.replace(tzinfo=None)
            
                hours_mined = (now - start).total_seconds() / 3600
            
                if hours_mined >= 12:
                    # Calculate final reward
                    intervals = 6  # 12 hours // 2 = 6 intervals
                    gems_earned = intervals * 50  # 300 gems max
                    stolen = miner['stolen_gems'] or 0
                    final_gems = max(0, gems_earned - stolen)
                
                    # Add gems to user
                    if final_gems > 0:
                        await self.currency.add_gems(user_id, final_gems, "Mining completed (12h max)")
                
                    # Reset mining status
                    await conn.execute("""
                        UPDATE player_stats 
                        SET mining_start = NULL, pending_reward = 0, stolen_gems = 0 
                        WHERE user_id = $1
                    """, user_id)
                
                    # Send DM notification
                    await self.send_mining_complete_dm(int(user_id), final_gems, stolen)
                
                    print(f"⏰ Auto-stopped mining for user {user_id} after 12 hours")

    @check_max_mining.before_loop
    async def before_check_max_mining(self):
        await self.bot.wait_until_ready()
        while self.bot.db_pool is None:
            await asyncio.sleep(1)



    # ------------------------------------------------------------------
    # Helper: Weapon ownership check
    # ------------------------------------------------------------------
    async def has_weapon(self, user_id: str) -> bool:
        async with self.bot.db_pool.acquire() as conn:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM user_weapons WHERE user_id = $1",
                user_id
            )
            return count > 0

    async def ensure_player_stats(self, user_id: str):
        async with self.bot.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO player_stats (user_id, hp, max_hp, energy, max_energy, last_energy_regen)
                VALUES ($1, 1000, 1000, 3, 3, NOW())
                ON CONFLICT (user_id) DO NOTHING
            """, user_id)


    async def has_pickaxe(self, user_id: str) -> bool:
        async with self.bot.db_pool.acquire() as conn:
            val = await conn.fetchval("SELECT has_pickaxe FROM player_stats WHERE user_id = $1", user_id)
            return val or False



    async def send_mining_complete_dm(self, user_id: int, gems_earned: int, gems_stolen: int):
        """Send DM notification when mining completes."""
        user = self.bot.get_user(user_id)
        if not user:
            try:
                user = await self.bot.fetch_user(user_id)
            except:
                return
    
        embed = discord.Embed(
            title="⛏️ Mining Complete!",
            description="You have reached the maximum mining time of 12 hours.",
            color=discord.Color.gold()
        )
        embed.add_field(name="💰 Gems Earned", value=f"{gems_earned}", inline=True)
        embed.add_field(name="😭 Gems Stolen", value=f"{gems_stolen}", inline=True)
        embed.add_field(name="📊 Total", value=f"{gems_earned + gems_stolen} (before theft)", inline=False)
    
        try:
            await user.send(embed=embed)
        except:
            print(f"❌ Could not send DM to user {user_id}")



    # ------------------------------------------------------------------
    # Admin: Set mining channel and send permanent message
    # ------------------------------------------------------------------
    @commands.command(name='setminingchannel')
    @commands.has_permissions(administrator=True)
    async def set_mining_channel(self, ctx, channel: discord.TextChannel):
        # Delete old mining message if exists
        async with self.bot.db_pool.acquire() as conn:
            old = await conn.fetchrow("SELECT message_id FROM mining_config WHERE guild_id = $1", ctx.guild.id)
            if old and old['message_id']:
                try:
                    old_channel = self.bot.get_channel(self.mining_channel) or channel
                    old_msg = await old_channel.fetch_message(old['message_id'])
                    await old_msg.delete()
                except:
                    pass

        # Send new message with image and buttons
        embed = discord.Embed(
            title="⛏️ Mining Zone",
            description="Click **Start Mining** to begin earning gems.\n"
                    "Click **Miners** to see who is currently mining and plunder them!",
            color=discord.Color.gold()
        )
        embed.set_image(url="https://image2url.com/r2/default/images/1771824770304-309985b9-7ce9-4a46-b029-c59a5d065952.png")

        view = MiningMainView(self.bot, self)
        msg = await channel.send(embed=embed, view=view)

        # Store in database
        async with self.bot.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO mining_config (guild_id, channel_id, message_id)
                VALUES ($1, $2, $3)
                ON CONFLICT (guild_id) DO UPDATE SET channel_id = $2, message_id = $3
            """, ctx.guild.id, channel.id, msg.id)

        self.mining_channel = channel.id
        self.mining_message = msg   # <-- store the message object
        await ctx.send(f"✅ Mining channel set to {channel.mention} with interactive buttons.", delete_after=5)


    @commands.command(name='miningstatus')
    async def mining_status(self, ctx):
        """Check your current mining progress."""
        user_id = str(ctx.author.id)
        async with self.bot.db_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT mining_start, stolen_gems 
                FROM player_stats 
                WHERE user_id = $1 AND mining_start IS NOT NULL
            """, user_id)
    
        if not row:
            await ctx.send("❌ You are not currently mining.")
            return
    
        start = row['mining_start']
        if start.tzinfo is not None:
            start = start.replace(tzinfo=None)
        now = datetime.utcnow()
        hours_mined = (now - start).total_seconds() / 3600
        hours_remaining = max(0, 12 - hours_mined)
    
        # Calculate current pending gems
        intervals = int(hours_mined // 2)
        pending = intervals * 50
        stolen = row['stolen_gems'] or 0
        projected = max(0, pending - stolen)
    
        embed = discord.Embed(
            title="⛏️ Mining Status",
            color=discord.Color.blue()
        )
        embed.add_field(name="⏱️ Time Mined", value=f"{hours_mined:.1f} / 12 hours", inline=False)
        embed.add_field(name="⏳ Time Remaining", value=f"{hours_remaining:.1f} hours", inline=False)
        embed.add_field(name="💰 Current Gems", value=f"{projected}", inline=True)
        embed.add_field(name="😭 Stolen", value=f"{stolen}", inline=True)
    
        await ctx.send(embed=embed)






    # ------------------------------------------------------------------
    # Core mining logic (called by buttons)
    # ------------------------------------------------------------------
    async def start_mining_for_user(self, user_id: str, channel: discord.TextChannel) -> str:
        if not await self.has_pickaxe(user_id):
            return "❌ You don't have a Pickaxe! Buy one from the shop first."

        await self.ensure_player_stats(user_id)

        async with self.bot.db_pool.acquire() as conn:
            existing = await conn.fetchval("SELECT mining_start FROM player_stats WHERE user_id = $1", user_id)
            if existing:
                return "❌ You are already mining! Use the **Stop Mining** button in the miners list to finish."

            now = datetime.utcnow() 
            await conn.execute("""
                UPDATE player_stats
                SET mining_start = $1, pending_reward = 0
                WHERE user_id = $2
            """, now, user_id)

        return "✅ You have started mining! You will earn gems over time."

    async def stop_mining_for_user(self, user_id: str) -> str:
        async with self.bot.db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT mining_start, stolen_gems FROM player_stats WHERE user_id = $1", user_id)
            if not row or not row['mining_start']:
                return "❌ You are not mining."

            start = row['mining_start']
            if start.tzinfo is not None:
                start = start.replace(tzinfo=None)
            now = datetime.utcnow()
            hours_mined = (now - start).total_seconds() / 3600
            hours_mined = min(hours_mined, 12)
            intervals = int(hours_mined // 2)
            gems_earned = intervals * 50
            stolen = row['stolen_gems'] or 0
            gems_earned = max(0, gems_earned - stolen)

            if gems_earned > 0:
                await self.currency.add_gems(user_id, gems_earned, "Mining reward")

            await conn.execute("""
                UPDATE player_stats
                SET mining_start = NULL, pending_reward = 0, stolen_gems = 0
                WHERE user_id = $1
            """, user_id)

        return f"✅ You mined for **{hours_mined:.1f} hours** and earned **{gems_earned} gems**."

    async def plunder_user(self, attacker_id: str, defender_id: str) -> str:
        if attacker_id == defender_id:
            return "❌ You cannot plunder yourself."

        if not await self.has_weapon(attacker_id):
            return "❌ You don't have any weapon! Buy one from the shop first."
        if not await self.has_weapon(defender_id):
            return "❌ That user doesn't have any weapon and cannot be plundered."

        await self.ensure_player_stats(attacker_id)
        await self.ensure_player_stats(defender_id)

        async with self.bot.db_pool.acquire() as conn:
            today = datetime.utcnow().date()
            stats = await conn.fetchrow("""
                SELECT energy, plunder_count, last_plunder_reset
                FROM player_stats WHERE user_id = $1
            """, attacker_id)
            if not stats or stats['energy'] < 1:
                return "❌ You need at least 1 energy to plunder."
            if stats['last_plunder_reset'] != today:
                await conn.execute("UPDATE player_stats SET plunder_count = 0, last_plunder_reset = $1 WHERE user_id = $2", today, attacker_id)
                plunder_count = 0
            else:
                plunder_count = stats['plunder_count']
            if plunder_count >= 2:
                return "❌ You have already used your 2 plunders today."

            defender = await conn.fetchrow("SELECT mining_start FROM player_stats WHERE user_id = $1", defender_id)
            if not defender or not defender['mining_start']:
                return "❌ That user is not mining."

            start = defender['mining_start']
            if start.tzinfo is not None:
                start = start.replace(tzinfo=None)
            now = datetime.utcnow()
            hours_mined = (now - start).total_seconds() / 3600
            intervals = int(hours_mined // 2)
            pending = intervals * 50
            if pending == 0:
                return "❌ That user hasn't mined enough yet (need at least 2 hours)."

            steal = int(pending * 0.3)
            await self.currency.add_gems(attacker_id, steal, f"Plundered from <@{defender_id}>")
            await conn.execute("""
                UPDATE player_stats
                SET stolen_gems = stolen_gems + $1
                WHERE user_id = $2
            """, steal, defender_id)
            await conn.execute("""
                UPDATE player_stats
                SET energy = energy - 1, plunder_count = plunder_count + 1
                WHERE user_id = $1
            """, attacker_id)

        return f"💰 You plundered **{steal} gems** from <@{defender_id}>!"

    # ------------------------------------------------------------------
    # Attack Command
    # ------------------------------------------------------------------
    @commands.command(name='attack')
    async def attack(self, ctx, target: discord.Member):
        attacker_id = str(ctx.author.id)
        defender_id = str(target.id)

        if attacker_id == defender_id:
            await ctx.send("❌ You cannot attack yourself.")
            return

        if not await self.has_weapon(attacker_id):
            await ctx.send("❌ You don't have any weapon! Buy one from the shop first.")
            return
        if not await self.has_weapon(defender_id):
            await ctx.send(f"❌ {target.mention} doesn't have any weapon and cannot be attacked.")
            return

        await self.ensure_player_stats(attacker_id)
        await self.ensure_player_stats(defender_id)

        async with self.bot.db_pool.acquire() as conn:
            energy = await conn.fetchval("SELECT energy FROM player_stats WHERE user_id = $1", attacker_id)
            if not energy or energy < 1:
                await ctx.send("❌ You need at least 1 energy to attack.")
                return

            weapon = await conn.fetchrow("""
                SELECT uw.attack, COALESCE(si.name, uw.generated_name) as name, uw.image_url
                FROM user_weapons uw
                LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                WHERE uw.user_id = $1
                ORDER BY uw.purchased_at DESC
                LIMIT 1
            """, attacker_id)
            if not weapon:
                await ctx.send("❌ You don't have a weapon to attack with!")
                return

            defender_stats = await conn.fetchrow("SELECT hp FROM player_stats WHERE user_id = $1", defender_id)
            defender_weapon = await conn.fetchrow("""
                SELECT uw.attack, COALESCE(si.name, uw.generated_name) as name
                FROM user_weapons uw
                LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                WHERE uw.user_id = $1
                ORDER BY uw.purchased_at DESC
                LIMIT 1
            """, defender_id)

            await conn.execute("UPDATE player_stats SET energy = energy - 1 WHERE user_id = $1", attacker_id)

        embed = discord.Embed(
            title="⚔️ Attack Initiated!",
            description=f"{ctx.author.mention} is attacking {target.mention}!",
            color=discord.Color.orange()
        )
        embed.add_field(name="Attacker's Weapon", value=f"{weapon['name']} (+{weapon['attack']} ATK)", inline=True)
        if defender_weapon:
            embed.add_field(name="Defender's Weapon", value=f"{defender_weapon['name']} (+{defender_weapon['attack']} ATK)", inline=True)
        embed.add_field(name="Defender's HP", value=f"{defender_stats['hp']} / 1000", inline=False)
        if weapon['image_url']:
            embed.set_thumbnail(url=weapon['image_url'])

        view = AttackView(attacker_id, defender_id, weapon['attack'], self.bot)
        await ctx.send(embed=embed, view=view)

    # ------------------------------------------------------------------
    # HP Check Command
    # ------------------------------------------------------------------
    @commands.command(name='hp')
    async def check_hp(self, ctx):
        user_id = str(ctx.author.id)
        if not await self.has_weapon(user_id):
            await ctx.send("❌ You don't have any weapon! Buy one from the shop first to join the Culling Game.")
            return
        async with self.bot.db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT hp, energy FROM player_stats WHERE user_id = $1", user_id)
        if not row:
            await ctx.send("You don't have any stats yet. Buy a weapon to join the Culling Game!")
            return
        await ctx.send(f"❤️ HP: {row['hp']}/1000 | ⚡ Energy: {row['energy']}/3")

# END CULLING GAME CLASS

    @commands.command(name='showconfig')
    @commands.has_permissions(administrator=True)
    async def show_mining_config(self, ctx):
        async with self.bot.db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM mining_config LIMIT 1")
        if row:
            await ctx.send(f"**Mining Config**\nGuild: {row['guild_id']}\nChannel: {row['channel_id']}\nMessage: {row['message_id']}")
        else:
            await ctx.send("No mining config found in database.")

class MiningMainView(discord.ui.View):
    def __init__(self, bot, cog):
        super().__init__(timeout=None)
        self.bot = bot
        self.cog = cog

        # Start Mining button
        self.start_button = discord.ui.Button(
            label="⛏️ Start Mining",
            style=discord.ButtonStyle.primary,
            custom_id="mining_start_fixed"
        )
        self.start_button.callback = self.start_mining_callback
        self.add_item(self.start_button)

        # Miners button
        self.miners_button = discord.ui.Button(
            label="👥 Miners",
            style=discord.ButtonStyle.secondary,
            custom_id="mining_list_fixed"
        )
        self.miners_button.callback = self.show_miners_callback
        self.add_item(self.miners_button)

    async def start_mining_callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            if self.cog.mining_channel is None or interaction.channel.id != self.cog.mining_channel:
                await interaction.followup.send("❌ You can only use this in the mining channel.", ephemeral=True)
                return
            result = await self.cog.start_mining_for_user(str(interaction.user.id), interaction.channel)
            await interaction.followup.send(result, ephemeral=True)
        except Exception as e:
            print(f"Error in start_mining: {e}")
            traceback.print_exc()
            await interaction.followup.send("❌ An error occurred. Please try again later.", ephemeral=True)

    async def show_miners_callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            async with self.bot.db_pool.acquire() as conn:
                miners = await conn.fetch("""
                    SELECT user_id, mining_start
                    FROM player_stats
                    WHERE mining_start IS NOT NULL
                    ORDER BY mining_start
                """)
            if not miners:
                await interaction.followup.send("No one is currently mining.", ephemeral=True)
                return

            miner_list = []
            for m in miners:
                user_id = m['user_id']
                # First try cache
                member = interaction.guild.get_member(int(user_id))
                if member:
                    name = member.display_name
                else:
                    # 🔹 KEY CHANGE: Attempt to fetch from API
                    try:
                        member = await interaction.guild.fetch_member(int(user_id))
                        name = member.display_name
                    except:
                        # 🔹 Fallback to global username or truncated ID
                        user = self.bot.get_user(int(user_id))
                        if user:
                            name = user.name
                        else:
                            name = f"User {user_id[:6]}"
                miner_list.append((user_id, name))
                print(f"DEBUG: Miner {user_id} -> {name}")

            embed = discord.Embed(
                title="Current Miners",
                description="Click a button to plunder that miner.",
                color=discord.Color.blue()
            )
            view = MinersListView(miner_list, self.cog, str(interaction.user.id))
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            print(f"Error in show_miners: {e}")
            traceback.print_exc()
            await interaction.followup.send(f"❌ Error: {type(e).__name__} – {str(e)}", ephemeral=True)


class MinersListView(discord.ui.View):
    def __init__(self, miner_list, cog, requester_id):
        super().__init__(timeout=60)
        self.cog = cog
        self.requester_id = requester_id
        for user_id, name in miner_list:
            if user_id == requester_id:
                # Show Stop Mining button for self
                button = StopMiningButton(user_id, cog, label="⏹️ Stop Mining", style=discord.ButtonStyle.secondary)
            else:
                # Show Plunder button for others
                button = PlunderButton(user_id, cog, label=f"Plunder {name}", style=discord.ButtonStyle.danger)
            self.add_item(button)


class StopMiningButton(discord.ui.Button):
    def __init__(self, target_id, cog, **kwargs):
        super().__init__(**kwargs)
        self.target_id = target_id
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            if str(interaction.user.id) != self.target_id:
                await interaction.followup.send("❌ You can only stop your own mining.", ephemeral=True)
                return
            result = await self.cog.stop_mining_for_user(self.target_id)
            await interaction.followup.send(result, ephemeral=True)
        except Exception as e:
            print(f"Error in stop mining button: {e}")
            traceback.print_exc()
            await interaction.followup.send("❌ An error occurred.", ephemeral=True)

class PlunderButton(discord.ui.Button):
    def __init__(self, target_id, cog, **kwargs):
        super().__init__(**kwargs)
        self.target_id = target_id
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            if str(interaction.user.id) == self.target_id:
                await interaction.followup.send("❌ You cannot plunder yourself.", ephemeral=True)
                return
            result = await self.cog.plunder_user(str(interaction.user.id), self.target_id)
            await interaction.followup.send(result, ephemeral=True)
        except Exception as e:
            print(f"Error in plunder button: {e}")
            traceback.print_exc()
            await interaction.followup.send("❌ An error occurred.", ephemeral=True)


class AttackView(discord.ui.View):
    def __init__(self, attacker_id, defender_id, attack_power, bot):
        super().__init__(timeout=60)
        self.attacker_id = attacker_id
        self.defender_id = defender_id
        self.attack_power = attack_power
        self.bot = bot

    @discord.ui.button(label="Resolve Attack", style=discord.ButtonStyle.danger)
    async def resolve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.defender_id:
            await interaction.response.send_message("Only the defender can resolve this attack.", ephemeral=True)
            return
        await interaction.response.defer()
        damage = self.attack_power
        async with self.bot.db_pool.acquire() as conn:
            defender = await conn.fetchrow("SELECT hp FROM player_stats WHERE user_id = $1", self.defender_id)
            if not defender:
                await interaction.followup.send("Defender stats not found.")
                return
            new_hp = defender['hp'] - damage
            if new_hp < 0:
                new_hp = 0
            await conn.execute("UPDATE player_stats SET hp = $1 WHERE user_id = $2", new_hp, self.defender_id)
            await conn.execute("""
                INSERT INTO attack_logs (attacker_id, defender_id, damage)
                VALUES ($1, $2, $3)
            """, self.attacker_id, self.defender_id, damage)
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        embed = discord.Embed(
            title="⚔️ Attack Result",
            description=f"{interaction.user.mention} took **{damage} damage**!",
            color=discord.Color.red()
        )
        embed.add_field(name="HP Remaining", value=f"{new_hp} / 1000")
        await interaction.followup.send(embed=embed)
        if new_hp == 0:
            await interaction.followup.send(f"{interaction.user.mention} has been defeated! They will respawn with 1000 HP.")
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("UPDATE player_stats SET hp = 1000 WHERE user_id = $1", self.defender_id)



# Add the shop cog to the bot
bot.add_cog(Shop(bot))


async def load_shop_persistence(bot):
    shop_cog = bot.get_cog('Shop')
    if shop_cog:
        await shop_cog.load_shop_messages()

async def load_mining_persistence(bot):
    cog = bot.get_cog('CullingGame')
    if not cog:
        print("❌ CullingGame cog not found.")
        return
    for guild in bot.guilds:
        await cog.load_mining_messages(guild.id)


bot.add_cog(CullingGame(bot, currency_system))



# === RUN BOT ===
if __name__ == "__main__":
    if TOKEN:
        print("\n🚀 Starting bot...")
        bot.run(TOKEN)
    else:
        print("❌ ERROR: No TOKEN found in environment variables!")
        print("💡 Set TOKEN environment variable in Railway")

