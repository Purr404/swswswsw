import os
import sys
import json
import asyncio
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
import traceback   # used in log_to_discord
import aiohttp
import io
import textwrap
import string
import time
from datetime import datetime, timezone, timedelta, date

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



BOSS_IMAGES = [
    "https://image2url.com/r2/default/images/1772975631054-b8438230-322e-4160-a75e-55364aca1acd.png",
    "https://image2url.com/r2/default/images/1773046503065-c6b43d19-1ca2-49cc-9115-3a5c6b8bf65a.png",
    "https://image2url.com/r2/default/images/1773046646102-02e4016a-4b8e-4fca-9271-07d6f32c4dbd.png",
    "https://image2url.com/r2/default/images/1773046677067-525c294e-a2a7-46af-a503-e97f761c54b0.png",

"https://image2url.com/r2/default/images/1773112080339-ea113862-56ed-48a2-833c-462421d56b15.png",

"https://image2url.com/r2/default/images/1773112137244-8609699c-1699-4bf8-a3d7-91a03b523a53.png",

"https://image2url.com/r2/default/images/1773112167085-d3ed553d-e10f-4fd7-af08-18889868cc58.png",

"https://image2url.com/r2/default/images/1773219794810-a5dbee44-07f0-4f1b-8bf3-4e9043b36e8a.png",

"https://image2url.com/r2/default/images/1773219848872-eaade8df-827f-4f7e-9376-a859b74c6218.png",
    # add more as desired
]



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
    'baby_fox': '<:baby_fox:1480154975069016205>',  # Replace with actual ID
    'baby_tiger': '<:baby_tiger:1480155125493399656>',  # Replace with actual ID
    'baby_purr': '<:baby_purr:1480158366516121660>',  # Replace with actual ID
    'lilia_maid': '<:lilia_maid:1482627569651286056>',  # Replace with actual ID
    
    # Tools/Misc
    'pickaxe': '<:pickaxe:1477024057382666383>',  # Replace with actual ID
    'gem_crn': '<:gem_crn:1484072663772303493>',
    'shadow': '<:shadow:1477258013256454339>',
    'paw': '<:paw:1482627374066565170>',
    'energy_potion': '<:energy_potion:1481365820566409236>',
    'hp_potion': '<:hp_potion:1482023718023598190>',
    'reflect': '<:reflect_dmg:1477608402564808765>',
    'treasure_carriage': '<:treasure_carriage:1477354550502625601>',
    'pet_book': '<:pet_book:1480800927777820762>',
    'pet_box': '<:pet_box:1480855688996589675>',
    'skill_enhancement_stone': '<:skill_enhancement_stone:1480854948123250821>',
    'armors_enhancement_stone': '<:armors_enhancement_stone:1480856847727726592>',
    'sword_enhancement_stone': '<:sword_enhancement_stone:1480855437388681226>',
    'acc_enhancement_stone': '<:acc_enhancement_stone:1480916604203171870>',
    # Titles
    'administrator': '<:administrator:1470082908151742536>',
    'boss_reaper': '<:boss_reaper:1483707209090334820>',
}

# ===== GLOBAL GEM EMOJI FOR CURRENCY =====
GEM_EMOJI = CUSTOM_EMOJIS.get('gem_crn', '💎')

# ============================================================
# EMOJIS HELPER FUNCTIONS 
def get_item_emoji(item_name: str, item_type: str, awakened: bool = False) -> str:
    """
    Return the appropriate custom emoji based on the exact item name.
    Uses a mapping of known item names to their emoji keys.
    """
    # Exact name → emoji key mapping
    EXACT_MAP = {
        # Swords
        "Zenith Sword": "zenith_sword",
        "Abyssal Blade": "abyssal_blade",
        "Dawn Breaker": "dawn_breaker",
        "Bloodmoon Edge": "bloodmoon_edge",
        "Shadowbane": "shadowbane",

        # Bilari Set
        "Bilari Helm": "bilari_helm",
        "Bilari Suit": "bilari_armor",
        "Bilari Gauntlets": "bilari_gloves",
        "Bilari Boots": "bilari_boots",

        # Cryo Set
        "Cryo Helm": "cryo_helm",
        "Cryo Suit": "cryo_armor",
        "Cryo Gauntlets": "cryo_gloves",
        "Cryo Boots": "cryo_boots",

        # Bane Set
        "Bane Helm": "bane_helm",
        "Bane Suit": "bane_armor",
        "Bane Gauntlets": "bane_gloves",
        "Bane Boots": "bane_boots",

        # Champion Set
        "Champion Ring": "champ_ring",
        "Champion Earring": "champ_earring",
        "Champion Pendant": "champ_pen",

        # Defender Set
        "Defender Ring": "def_ring",
        "Defender Earring": "def_earring",
        "Defender Pendant": "def_pen",

        # Angel Set
        "Angel Ring": "wing_ring",
        "Angel Earring": "harp_earring",
        "Angel Pendant": "angel_pen",

        # Pets
        "Baby Fox": "baby_fox",
        "Baby Tiger": "baby_tiger",
        "Baby Purr": "baby_purr",

        # Potions
        "HP Potion": "hp_potion",
        "Energy Potion": "energy_potion",
    }

    # 1. Try exact match first
    if item_name in EXACT_MAP:
        key = EXACT_MAP[item_name]
        emoji = CUSTOM_EMOJIS.get(key)
        if emoji:
            return emoji
        # If key exists but emoji missing, fall through to type‑based logic

    # 2. Fallback to type‑based detection (for any items not in the exact map)
    item_lower = item_name.lower()

    # Potions (already covered by exact map, but keep for safety)
    if 'hp potion' in item_lower:
        return CUSTOM_EMOJIS.get('hp_potion', '💚')
    if 'energy potion' in item_lower:
        return CUSTOM_EMOJIS.get('energy_potion', '⚡')

    # Weapons
    if item_type == 'weapon':
        if 'zenith' in item_lower:
            return CUSTOM_EMOJIS.get('zenith_sword', '⚔️')
        elif 'abyssal' in item_lower:
            return CUSTOM_EMOJIS.get('abyssal_blade', '⚔️')
        elif 'dawn' in item_lower or 'breaker' in item_lower:
            return CUSTOM_EMOJIS.get('dawn_breaker', '⚔️')
        elif 'bloodmoon' in item_lower or 'edge' in item_lower:
            return CUSTOM_EMOJIS.get('bloodmoon_edge', '⚔️')
        elif 'shadowbane' in item_lower:
            return CUSTOM_EMOJIS.get('shadowbane', '⚔️')
        return '⚔️'

    # Armor – exact map already handled the known sets
    elif item_type == 'armor':
        # Try to guess by set name (in case of slight name variations)
        if 'bilari' in item_lower:
            if 'helm' in item_lower or 'helmet' in item_lower:
                return CUSTOM_EMOJIS.get('bilari_helm', '🛡️')
            elif 'suit' in item_lower or 'armor' in item_lower or 'chest' in item_lower:
                return CUSTOM_EMOJIS.get('bilari_armor', '🛡️')
            elif 'gauntlet' in item_lower or 'glove' in item_lower:
                return CUSTOM_EMOJIS.get('bilari_gloves', '🛡️')
            elif 'boot' in item_lower:
                return CUSTOM_EMOJIS.get('bilari_boots', '🛡️')
        elif 'cryo' in item_lower:
            if 'helm' in item_lower or 'helmet' in item_lower:
                return CUSTOM_EMOJIS.get('cryo_helm', '🛡️')
            elif 'suit' in item_lower or 'armor' in item_lower or 'chest' in item_lower:
                return CUSTOM_EMOJIS.get('cryo_armor', '🛡️')
            elif 'gauntlet' in item_lower or 'glove' in item_lower:
                return CUSTOM_EMOJIS.get('cryo_gloves', '🛡️')
            elif 'boot' in item_lower:
                return CUSTOM_EMOJIS.get('cryo_boots', '🛡️')
        elif 'bane' in item_lower:
            if 'helm' in item_lower or 'helmet' in item_lower:
                return CUSTOM_EMOJIS.get('bane_helm', '🛡️')
            elif 'suit' in item_lower or 'armor' in item_lower or 'chest' in item_lower:
                return CUSTOM_EMOJIS.get('bane_armor', '🛡️')
            elif 'gauntlet' in item_lower or 'glove' in item_lower:
                return CUSTOM_EMOJIS.get('bane_gloves', '🛡️')
            elif 'boot' in item_lower:
                return CUSTOM_EMOJIS.get('bane_boots', '🛡️')
        # Fallback generic armor emoji (can be replaced with a custom default)
        return CUSTOM_EMOJIS.get('bilari_armor', '🛡️')

    # Accessories – exact map already handled the known sets
    elif item_type == 'accessory':
        # Try to guess by set name
        if 'champion' in item_lower or 'champ' in item_lower:
            if 'earring' in item_lower:
                return CUSTOM_EMOJIS.get('champ_earring', '💍')
            elif 'pendant' in item_lower or 'pen' in item_lower:
                return CUSTOM_EMOJIS.get('champ_pen', '💍')
            else:
                return CUSTOM_EMOJIS.get('champ_ring', '💍')
        elif 'defender' in item_lower or 'def' in item_lower:
            if 'earring' in item_lower:
                return CUSTOM_EMOJIS.get('def_earring', '💍')
            elif 'pendant' in item_lower or 'pen' in item_lower:
                return CUSTOM_EMOJIS.get('def_pen', '💍')
            else:
                return CUSTOM_EMOJIS.get('def_ring', '💍')
        elif 'angel' in item_lower:
            if 'earring' in item_lower:
                return CUSTOM_EMOJIS.get('harp_earring', '💍')
            elif 'pendant' in item_lower or 'pen' in item_lower:
                return CUSTOM_EMOJIS.get('angel_pen', '💍')
            else:
                return CUSTOM_EMOJIS.get('wing_ring', '💍')
        # If still not matched, return a generic accessory emoji (optional)
        if 'ring' in item_lower:
            return '💍'
        elif 'earring' in item_lower:
            return '📿'
        elif 'pendant' in item_lower or 'pen' in item_lower:
            return '🔮'
        return '💍'

    # Pets
    elif item_type == 'pet':
        if 'fox' in item_lower:
            return CUSTOM_EMOJIS.get('baby_fox', '🦊')
        elif 'tiger' in item_lower:
            return CUSTOM_EMOJIS.get('baby_tiger', '🐯')
        elif 'purr' in item_lower:
            return CUSTOM_EMOJIS.get('baby_purr', '😺')
        return '🐾'

    # Default fallback
    return '📦'

def get_pet_emoji(pet_name: str) -> str:
    """Return the custom emoji for a pet name, with fallback."""
    pet_lower = pet_name.lower()
    if 'fox' in pet_lower:
        return CUSTOM_EMOJIS.get('baby_fox', '🦊')
    elif 'tiger' in pet_lower:
        return CUSTOM_EMOJIS.get('baby_tiger', '🐯')
    elif 'purr' in pet_lower:
        return CUSTOM_EMOJIS.get('baby_purr', '😺')
    # For future exclusive pet
    elif 'lilia' in pet_lower or 'maid' in pet_lower:
        return '✨'
    return '🐾'

# 🔽 INSERT THE NEW HELPER HERE 🔽
async def get_equipped_title_bonuses(user_id: str) -> dict:
    """Return a dict of stat bonuses from the user's equipped title."""
    async with bot.db_pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT t.hp_percent, t.def_percent, t.atk_percent,
                   t.crit_chance, t.dodge_percent, t.dmg_reduction_percent,
                   t.bleed_flat, t.burn_flat, t.crit_dmg_res_percent,
                   t.mining_bonus_percent, t.boss_damage_percent,
                   t.extra_boss_attempts, t.extra_plunder_attempts,
                   t.name, t.emoji
            FROM titles t
            JOIN user_titles ut ON t.title_id = ut.title_id
            WHERE ut.user_id = $1 AND ut.equipped = TRUE
        """, user_id)
    if row:
        return {
            'hp_percent': row['hp_percent'],
            'def_percent': row['def_percent'],
            'atk_percent': row['atk_percent'],
            'crit_chance': row['crit_chance'],
            'dodge_percent': row['dodge_percent'],
            'dmg_reduction_percent': row['dmg_reduction_percent'],
            'bleed_flat': row['bleed_flat'],
            'burn_flat': row['burn_flat'],
            'crit_dmg_res_percent': row['crit_dmg_res_percent'],
            'mining_bonus_percent': row['mining_bonus_percent'],
            'boss_damage_percent': row['boss_damage_percent'],
            'extra_boss_attempts': row['extra_boss_attempts'],
            'extra_plunder_attempts': row['extra_plunder_attempts'],
            'name': row['name'],
            'emoji': row['emoji'] or '🏷️'
        }
    return None

# ============================================================

async def debug_log(self, message: str):
    """Send debug message to the quiz logs channel (best effort)."""
    print(f"🔍 DEBUG: {message}")  # always prints to console
    if self.quiz_logs_channel:
        try:
            await self.quiz_logs_channel.send(f"🔍 `{message}`")
        except:
            pass



SWORD_SKILLS = {
    "Zenith Sword": {
        "name": "Zenith Slash",
        "desc": "A radiant slash that channels celestial energy to empower your next strikes.",
        "effect": "20% chance to increase your ATK by 50% for 2 turns after attacking.",
        "base": 3.0,
        "increment": 0.25,
        "max_level": 20
    },
    "Abyssal Blade": {
        "name": "Abyssal Strike",
        "desc": "A shadowy thrust that weakens armor and leaves a lingering darkness.",
        "effect": "30% chance to reduce target's DEF by 15% for 3 turns.",
        "base": 3.0,
        "increment": 0.28,
        "max_level": 20
    },
    "Dawn Breaker": {
        "name": "Dawn's Wrath",
        "desc": "A fiery overhead smash that ignites the target, dealing burn damage over time.",
        "effect": "25% chance to burn target for 20% of damage dealt over 3 turns.",
        "base": 3.0,
        "increment": 0.22,
        "max_level": 20
    },
    "Bloodmoon Edge": {
        "name": "Bloodmoon Rend",
        "desc": "A ferocious rending slash that causes deep, bleeding wounds.",
        "effect": "Increases bleed chance by 15% and bleed damage by 25% for this attack.",
        "base": 3.0,
        "increment": 0.30,
        "max_level": 20
    },
    "Shadowbane": {
        "name": "Shadowbane",
        "desc": "A precision strike that targets vital points, greatly increasing critical potential.",
        "effect": "Doubles crit chance and adds 50% crit damage for this attack.",
        "base": 3.0,
        "increment": 0.26,
        "max_level": 20
    }
}


# --- Create the bot instance ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!!', intents=intents, help_command=None)
bot.active_bags = {}
bot.db_pool = None

#    FOR TRADING
@tasks.loop(minutes=5)
async def clean_old_trades():
    """Cancel pending trades older than 1 hour."""
    async with bot.db_pool.acquire() as conn:
        await conn.execute("""
            DELETE FROM active_trades
            WHERE status = 'pending' AND created_at < NOW() - INTERVAL '1 hour'
        """)

@bot.command(name='givetitle')
@commands.has_permissions(administrator=True)
async def give_title(ctx, member: discord.Member, *, title_name: str):
    """Give a title to a user (admin only)."""
    user_id = str(member.id)
    async with bot.db_pool.acquire() as conn:
        title = await conn.fetchrow("SELECT title_id FROM titles WHERE name = $1", title_name)
        if not title:
            await ctx.send("❌ Title not found.")
            return
        await conn.execute("""
            INSERT INTO user_titles (user_id, title_id) VALUES ($1, $2)
            ON CONFLICT (user_id, title_id) DO NOTHING
        """, user_id, title['title_id'])
    await ctx.send(f"✅ Gave **{title_name}** to {member.mention}.")

@bot.command(name='mypendingtrades')
async def my_pending_trades(ctx):
    """Show your pending trades."""
    user_id = str(ctx.author.id)
    async with bot.db_pool.acquire() as conn:
        trades = await conn.fetch("""
            SELECT trade_id, initiator_id, receiver_id, created_at
            FROM active_trades
            WHERE (initiator_id = $1 OR receiver_id = $1) AND status = 'pending'
        """, user_id)
    if not trades:
        return await ctx.send("You have no pending trades.")
    lines = []
    for t in trades:
        other_id = t['receiver_id'] if t['initiator_id'] == user_id else t['initiator_id']
        other = await bot.fetch_user(int(other_id))
        lines.append(f"**Trade ID {t['trade_id']}** with {other.mention} (started {t['created_at']})")
    await ctx.send("\n".join(lines))

@bot.command(name='canceltrade')
async def cancel_trade(ctx, trade_id: int):
    """Cancel a pending trade (only participants or admin)."""
    user_id = str(ctx.author.id)
    async with bot.db_pool.acquire() as conn:
        trade = await conn.fetchrow("SELECT * FROM active_trades WHERE trade_id = $1", trade_id)
        if not trade:
            return await ctx.send("❌ Trade not found.")
        if trade['status'] != 'pending':
            return await ctx.send("❌ Trade is not pending.")
        # Check permission: user must be initiator, receiver, or admin
        if user_id not in (trade['initiator_id'], trade['receiver_id']) and not ctx.author.guild_permissions.administrator:
            return await ctx.send("❌ You don't have permission to cancel this trade.")
        await conn.execute("UPDATE active_trades SET status = 'cancelled' WHERE trade_id = $1", trade_id)
    await ctx.send(f"✅ Trade {trade_id} cancelled.")


@bot.event
async def on_raw_message_delete(payload):
    """If a trade message is deleted, cancel the corresponding trade."""
    async with bot.db_pool.acquire() as conn:
        await conn.execute("""
            UPDATE active_trades
            SET status = 'cancelled'
            WHERE message_id = $1 AND status = 'pending'
        """, payload.message_id)


@bot.command(name='editshopimage')
@commands.has_permissions(administrator=True)
async def edit_shop_image(ctx, image_url: str):
    """Permanently change the persistent shop message's image using a direct image URL."""
    async with ctx.bot.db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT channel_id, message_id FROM shop_messages WHERE guild_id = $1", ctx.guild.id)
    if not row:
        await ctx.send("❌ No persistent shop found. Use `!!summonshopto` first.")
        return

    channel = ctx.guild.get_channel(row['channel_id'])
    if not channel:
        await ctx.send("❌ Shop channel no longer exists.")
        return

    try:
        msg = await channel.fetch_message(row['message_id'])
    except discord.NotFound:
        await ctx.send("❌ Shop message not found. It may have been deleted.")
        return

    # Preserve existing embed or create a default one
    embed = msg.embeds[0] if msg.embeds else discord.Embed(title="💎 **GEM SHOP**", color=discord.Color.gold())
    embed.set_image(url=image_url)  # Use the provided external URL

    # Recreate the persistent view
    view = discord.ui.View(timeout=None)
    button = discord.ui.Button(
        label="🛒 Open Shop",
        style=discord.ButtonStyle.primary,
        custom_id="shop_open_main"
    )
    view.add_item(button)

    # Remove any existing attachments (optional)
    await msg.edit(embed=embed, attachments=[], view=view)

    await ctx.send("✅ Shop image updated permanently (now using external URL).")

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

@bot.command(name='setpotionprice')
@commands.has_permissions(administrator=True)
async def set_potion_price(ctx, potion_name: str, new_price: int):
    """Set the price of a potion (single unit)."""
    async with bot.db_pool.acquire() as conn:
        result = await conn.execute("""
            UPDATE shop_items SET price = $1 WHERE name = $2 AND type = 'potion'
        """, new_price, potion_name)
        if result == "UPDATE 0":
            await ctx.send("❌ Potion not found.")
        else:
            await ctx.send(f"✅ Price of **{potion_name}** set to {new_price} gems per unit (×10 = {new_price*10} gems for a batch).")



@bot.command(name='fixbossreaper')
@commands.has_permissions(administrator=True)
async def fix_boss_reaper(ctx):
    async with bot.db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO titles (name, emoji, description,
                                boss_damage_percent, extra_boss_attempts, hp_percent)
            VALUES ('Boss Reaper', '<:boss_reaper:1483707209090334820>',
                    'Earned by being the top damage dealer in the server boss. Lasts 24 hours.',
                    5, 1, 10)
            ON CONFLICT (name) DO UPDATE SET
                boss_damage_percent = 5,
                extra_boss_attempts = 1,
                hp_percent = 10,
                emoji = '<:boss_reaper:1483707209090334820>',
                description = 'Earned by being the top damage dealer in the server boss. Lasts 24 hours.';
        """)
    await ctx.send("✅ Boss Reaper title updated with correct stats and expiration description.")

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
@bot.command()
@commands.has_permissions(administrator=True)
async def wipe_old_weapons(ctx):
    """Delete all weapons whose names contain Common, Uncommon, Rare, Epic, or Legendary."""
    # Confirm
    confirm = await ctx.send("⚠️ This will delete **all weapons** whose names contain any rarity word (Common, Uncommon, Rare, Epic, Legendary). Type `CONFIRM` within 30 seconds.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content == "CONFIRM"

    try:
        await bot.wait_for('message', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("❌ Deletion cancelled.")
        return

    async with bot.db_pool.acquire() as conn:
        # Delete weapons where the name contains any of the rarity words
        # Using ILIKE for case‑insensitive match
        result = await conn.execute("""
            DELETE FROM user_weapons
            WHERE generated_name ILIKE '%common%'
               OR generated_name ILIKE '%uncommon%'
               OR generated_name ILIKE '%rare%'
               OR generated_name ILIKE '%epic%'
               OR generated_name ILIKE '%legendary%'
        """)
        count = result.split()[1]
        await ctx.send(f"✅ Deleted **{count}** old rarity weapons.")

@bot.command(name='skill')
async def skill_info(ctx):
    """Show the skill of your currently equipped weapon."""
    user_id = str(ctx.author.id)

    async with bot.db_pool.acquire() as conn:
        weapon = await conn.fetchrow("""
            SELECT uw.id, COALESCE(si.name, uw.generated_name) as name, uw.skill_level
            FROM user_weapons uw
            LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
            WHERE uw.user_id = $1 AND uw.equipped = TRUE
            LIMIT 1
        """, user_id)

    if not weapon:
        return await ctx.send("You don't have a weapon equipped.")

    wname = weapon['name']
    if wname not in SWORD_SKILLS:
        return await ctx.send("Your weapon has no special skill.")

    skill = SWORD_SKILLS[wname]
    current_mult = skill['base'] + (weapon['skill_level'] - 1) * skill['increment']

    embed = discord.Embed(
        title=f"**{skill['name']}**",
        description=skill['desc'],
        color=discord.Color.blue()
    )
    embed.add_field(name="Weapon", value=wname, inline=True)
    embed.add_field(name="Level", value=f"{weapon['skill_level']}/{skill['max_level']}", inline=True)
    embed.add_field(name="Multiplier", value=f"{current_mult:.2f}x ATK", inline=True)
    embed.add_field(name="Effect", value=skill['effect'], inline=False)

    if weapon['skill_level'] < skill['max_level']:
        next_mult = current_mult + skill['increment']
        cost = 500 * (weapon['skill_level'] + 1)
        embed.add_field(name="Next Level", value=f"{next_mult:.2f}x", inline=True)
        embed.add_field(name="Upgrade Cost", value=f"{cost} gems", inline=True)
    else:
        embed.add_field(name="Next Level", value="MAX", inline=True)
        embed.add_field(name="Upgrade Cost", value="MAX", inline=True)

    await ctx.send(embed=embed)

@bot.command(name='upgradeskill')
async def upgrade_skill(ctx):
    """Upgrade your equipped weapon's skill level."""
    user_id = str(ctx.author.id)

    async with bot.db_pool.acquire() as conn:
        weapon = await conn.fetchrow("""
            SELECT uw.id, COALESCE(si.name, uw.generated_name) as name, uw.skill_level
            FROM user_weapons uw
            LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
            WHERE uw.user_id = $1 AND uw.equipped = TRUE
            LIMIT 1
        """, user_id)

    if not weapon:
        return await ctx.send("You don't have a weapon equipped.")

    wname = weapon['name']
    if wname not in SWORD_SKILLS:
        return await ctx.send("Your weapon has no upgradable skill.")

    skill = SWORD_SKILLS[wname]
    current_level = weapon['skill_level']

    if current_level >= skill['max_level']:
        return await ctx.send("Your weapon's skill is already max level.")

    cost = 500 * (current_level + 1)

    # Check gems using global currency_system
    balance = await currency_system.get_balance(user_id)
    if balance['gems'] < cost:
        return await ctx.send(f"Insufficient gems. You need **{cost}** gems.")

    # Deduct gems
    await currency_system.deduct_gems(user_id, cost, f"Upgraded {wname} skill to level {current_level+1}")

    # Update skill level
    async with bot.db_pool.acquire() as conn:
        await conn.execute("UPDATE user_weapons SET skill_level = skill_level + 1 WHERE id = $1", weapon['id'])

    await ctx.send(f"✅ Your **{wname}**'s skill is now **Level {current_level + 1}**!")



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
        """Connect to PostgreSQL with fallback strategies, including skipping SSL verification."""
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL is required for PostgreSQL connection")

        if not ASYNCPG_AVAILABLE:
            raise ImportError("asyncpg is required for database operations")

        print("\n🔌 Attempting database connection...")

        # Connection strategies – try SSL first, then fallback to no SSL, and finally skip verification
        connection_strategies = [
            ("Standard SSL (verify)", {'ssl': 'require', 'command_timeout': 30}),
            ("SSL without verification", {'ssl': {'sslrootcert': None, 'sslmode': 'require'}, 'command_timeout': 30}),
            ("No SSL", {'ssl': None, 'command_timeout': 30}),
            ("No SSL, longer timeout", {'ssl': None, 'command_timeout': 60}),
            ("No extra args", {}),
        ]

        for strategy_name, strategy_args in connection_strategies:
            print(f"  Trying: {strategy_name}...")
            try:
                self.pool = await asyncpg.create_pool(
                    DATABASE_URL,
                    min_size=1,
                    max_size=5,
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

                    await conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS rarities_name_key ON rarities (name);')

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
                            name TEXT NOT NULL UNIQUE,
                            bonus_stat TEXT CHECK (bonus_stat IN ('atk', 'def', 'hp', 'energy')),
                            bonus_value INTEGER DEFAULT 0,
                            image_url TEXT,
                            description TEXT,
                            -- New columns for pet bonuses
                            atk_percent INT DEFAULT 0,
                            def_percent INT DEFAULT 0,
                            hp_percent INT DEFAULT 0,
                            dodge_percent INT DEFAULT 0,
                            bleed_flat INT DEFAULT 0,
                            burn_flat INT DEFAULT 0,
                            energy_bonus INT DEFAULT 0
                        )
                    ''')
                    await conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS pet_types_name_key ON pet_types (name);')

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
                    # ========== PET BONUS COLUMNS (ensure they exist) ==========
                    # (These are safe even if already added by the CREATE TABLE)                   
                    await conn.execute('ALTER TABLE pet_types ADD COLUMN IF NOT EXISTS atk_percent INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE pet_types ADD COLUMN IF NOT EXISTS def_percent INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE pet_types ADD COLUMN IF NOT EXISTS hp_percent INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE pet_types ADD COLUMN IF NOT EXISTS dodge_percent INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE pet_types ADD COLUMN IF NOT EXISTS bleed_flat INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE pet_types ADD COLUMN IF NOT EXISTS burn_flat INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE pet_types ADD COLUMN IF NOT EXISTS energy_bonus INT DEFAULT 0;')

                    # ========== SEED PETS ==========
                    await conn.execute("""
                        INSERT INTO pet_types (name, atk_percent, def_percent, hp_percent, dodge_percent, bleed_flat, burn_flat, energy_bonus, description) VALUES
                        ('Baby Fox', 5, 15, 30, 8, 0, 0, 1, 'A cunning fox that boosts your stats and grants dodge chance.'),
                        ('Baby Tiger', 5, 15, 30, 0, 1000, 0, 1, 'A fierce tiger that enhances your bleed damage.'),
                        ('Baby Purr', 5, 15, 30, 0, 0, 1000, 1, 'A mystical cat that adds burn damage to your attacks.')
                        ON CONFLICT (name) DO NOTHING;
                    """)
                    # ========== TITLE SYSTEM TABLES ==========
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS titles (
                            title_id SERIAL PRIMARY KEY,
                            name TEXT NOT NULL UNIQUE,
                            emoji TEXT,
                            description TEXT,
                            hp_percent INT DEFAULT 0,
                            def_percent INT DEFAULT 0,
                            atk_percent INT DEFAULT 0,
                            crit_chance INT DEFAULT 0,
                            dodge_percent INT DEFAULT 0,
                            dmg_reduction_percent INT DEFAULT 0,
                            bleed_flat INT DEFAULT 0,
                            burn_flat INT DEFAULT 0,
                            crit_dmg_res_percent INT DEFAULT 0,
                            mining_bonus_percent INT DEFAULT 0,
                            boss_damage_percent INT DEFAULT 0,
                            extra_boss_attempts INT DEFAULT 0,
                            extra_plunder_attempts INT DEFAULT 0
                        )
                    ''')

                    # Add columns if they don't exist (for existing tables)
                    await conn.execute('ALTER TABLE titles ADD COLUMN IF NOT EXISTS hp_percent INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE titles ADD COLUMN IF NOT EXISTS def_percent INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE titles ADD COLUMN IF NOT EXISTS atk_percent INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE titles ADD COLUMN IF NOT EXISTS crit_chance INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE titles ADD COLUMN IF NOT EXISTS dodge_percent INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE titles ADD COLUMN IF NOT EXISTS dmg_reduction_percent INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE titles ADD COLUMN IF NOT EXISTS bleed_flat INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE titles ADD COLUMN IF NOT EXISTS burn_flat INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE titles ADD COLUMN IF NOT EXISTS crit_dmg_res_percent INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE titles ADD COLUMN IF NOT EXISTS mining_bonus_percent INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE titles ADD COLUMN IF NOT EXISTS boss_damage_percent INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE titles ADD COLUMN IF NOT EXISTS extra_boss_attempts INT DEFAULT 0;')
                    await conn.execute('ALTER TABLE titles ADD COLUMN IF NOT EXISTS extra_plunder_attempts INT DEFAULT 0;')

                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS user_titles (
                            user_id TEXT NOT NULL REFERENCES user_gems(user_id) ON DELETE CASCADE,
                            title_id INTEGER NOT NULL REFERENCES titles(title_id) ON DELETE CASCADE,
                            equipped BOOLEAN DEFAULT FALSE,
                            obtained_at TIMESTAMP DEFAULT NOW(),
                            PRIMARY KEY (user_id, title_id)
                        )
                    ''')
                    # Ensure only one equipped title per user
                    await conn.execute('''
                        CREATE UNIQUE INDEX IF NOT EXISTS idx_user_titles_equipped
                        ON user_titles (user_id) WHERE equipped = TRUE;
                    ''')
                    await conn.execute('ALTER TABLE user_titles ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ;')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_titles_expires ON user_titles (expires_at);')

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
                    # ========== TRADE SYSTEM TABLES ==========
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS active_trades (
                            trade_id SERIAL PRIMARY KEY,
                            initiator_id TEXT NOT NULL,
                            receiver_id TEXT NOT NULL,
                            channel_id BIGINT NOT NULL,
                            message_id BIGINT,
                            initiator_lock BOOLEAN DEFAULT FALSE,
                            receiver_lock BOOLEAN DEFAULT FALSE,
                            status TEXT DEFAULT 'pending'
                        )
                    ''')


                    await conn.execute("ALTER TABLE active_trades ALTER COLUMN message_id DROP NOT NULL;")
                    await conn.execute("ALTER TABLE active_trades ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();")


                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS trade_items (
                            trade_id INTEGER REFERENCES active_trades(trade_id) ON DELETE CASCADE,
                            user_id TEXT NOT NULL,
                            item_type TEXT NOT NULL,
                            item_id INTEGER NOT NULL,
                            gems INTEGER DEFAULT 0,
                            quantity INTEGER DEFAULT 1
                        )
                    ''')
                    await conn.execute('ALTER TABLE trade_items ADD COLUMN IF NOT EXISTS quantity INTEGER DEFAULT 1;')


                    # ========== MATERIALS TABLE ==========
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS user_materials (
                            user_id TEXT NOT NULL,
                            material_id INTEGER NOT NULL,
                            quantity INTEGER DEFAULT 0,
                            PRIMARY KEY (user_id, material_id),
                            FOREIGN KEY (user_id) REFERENCES user_gems(user_id) ON DELETE CASCADE,
                            FOREIGN KEY (material_id) REFERENCES shop_items(item_id) ON DELETE CASCADE
                        )
                    ''')

                    # ========== ACTIVE EFFECTS TABLE ==========
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS active_effects (
                            effect_id SERIAL PRIMARY KEY,
                            target_id TEXT NOT NULL,
                            effect_type TEXT NOT NULL,
                            value INTEGER NOT NULL,
                            remaining_ticks INTEGER NOT NULL,
                            last_tick TIMESTAMP DEFAULT NOW(),
                            FOREIGN KEY (target_id) REFERENCES user_gems(user_id) ON DELETE CASCADE
                        )
                    ''')
                    # ========== ACTIVE BUFFS/DEBUFFS TABLE ==========
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS active_buffs (
                            buff_id SERIAL PRIMARY KEY,
                            target_id TEXT NOT NULL,
                            effect_type TEXT NOT NULL,
                            value FLOAT NOT NULL,
                            remaining_turns INTEGER NOT NULL,
                            FOREIGN KEY (target_id) REFERENCES user_gems(user_id) ON DELETE CASCADE
                        )
                    ''')
                    # ========== BOSS SYSTEM TABLES ==========
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS boss_config (
                            guild_id BIGINT PRIMARY KEY,
                            channel_id BIGINT NOT NULL,
                            message_id BIGINT,
                            boss_hp BIGINT NOT NULL,
                            max_hp BIGINT NOT NULL,
                            last_reset TIMESTAMPTZ
                        )
                    ''')
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS boss_attempts (
                            user_id TEXT NOT NULL,
                            reset_date DATE NOT NULL,
                            attempts_used INTEGER DEFAULT 0,
                            PRIMARY KEY (user_id, reset_date)
                        )
                    ''')
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS boss_damage (
                            user_id TEXT NOT NULL,
                            reset_date DATE NOT NULL,
                            total_damage BIGINT DEFAULT 0,
                            PRIMARY KEY (user_id, reset_date)
                        )
                    ''')


                    # ========== ADD MISSING COLUMNS TO EXISTING TABLES ==========
                    # These ensure the schema is updated if tables already exist

                    # User weapons
                    await conn.execute('ALTER TABLE user_weapons ADD COLUMN IF NOT EXISTS bleeding_chance FLOAT DEFAULT 0')
                    await conn.execute('ALTER TABLE user_weapons ADD COLUMN IF NOT EXISTS crit_chance FLOAT DEFAULT 0')
                    await conn.execute('ALTER TABLE user_weapons ADD COLUMN IF NOT EXISTS crit_damage FLOAT DEFAULT 0')
                    await conn.execute('ALTER TABLE user_weapons ADD COLUMN IF NOT EXISTS skill_level INTEGER DEFAULT 1')

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
                    await conn.execute("""
                        UPDATE accessory_types 
                        SET slot = 'ring' 
                        WHERE slot IN ('ring1', 'ring2')
                    """)
                    await conn.execute("""
                        UPDATE accessory_types 
                        SET slot = 'earring' 
                        WHERE slot IN ('earring1', 'earring2')
                    """)
                    await conn.execute("""
                        UPDATE accessory_types 
                        SET slot = 'pendant' 
                    WHERE slot = 'pendant'
                    """)  
# 3. Add the new constraint

                    # Update bonus_stat constraint for accessory_types
                    await conn.execute('ALTER TABLE accessory_types DROP CONSTRAINT IF EXISTS accessory_types_bonus_stat_check')
                    await conn.execute('''
                        ALTER TABLE accessory_types ADD CONSTRAINT accessory_types_bonus_stat_check 
                        CHECK (bonus_stat IN ('atk', 'def', 'hp', 'energy', 'crit', 'bleed'))
                    ''')

                    # User accessories
                    await conn.execute('ALTER TABLE user_accessories ADD COLUMN IF NOT EXISTS set_name TEXT')
                    await conn.execute('ALTER TABLE user_accessories ADD COLUMN IF NOT EXISTS purchase_id INTEGER REFERENCES user_purchases(purchase_id) ON DELETE SET NULL')
                    # Modify user_accessories to allow NULL slot and enforce unique equipped slots
                    await conn.execute('ALTER TABLE user_accessories ALTER COLUMN slot DROP NOT NULL;')
                    await conn.execute('ALTER TABLE user_accessories DROP CONSTRAINT IF EXISTS user_accessories_user_id_slot_key;')
                    await conn.execute('''
                        CREATE UNIQUE INDEX IF NOT EXISTS idx_user_accessories_equipped_slot 
                        ON user_accessories (user_id, slot) WHERE equipped = TRUE;
                    ''')

                    # Player stats
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS defense INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS crit_chance FLOAT DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS crit_damage FLOAT DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS defense_bonus INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS reflect_bonus INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS hp_bonus INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS atk_bonus INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS bleed_damage FLOAT DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS respawn_at TIMESTAMPTZ')
                    # Boss system
                    await conn.execute('ALTER TABLE boss_config ADD COLUMN IF NOT EXISTS boss_image_url TEXT')
                    await conn.execute('ALTER TABLE boss_config ADD COLUMN IF NOT EXISTS announce_channel_id BIGINT')
                    # Upgrade system columns
                    await conn.execute('ALTER TABLE user_weapons ADD COLUMN IF NOT EXISTS upgrade_level INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE user_armor ADD COLUMN IF NOT EXISTS upgrade_level INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE user_accessories ADD COLUMN IF NOT EXISTS upgrade_level INTEGER DEFAULT 0')

                    

                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS stolen_sword_stones INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS stolen_armor_stones INTEGER DEFAULT 0')
                    await conn.execute('ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS stolen_acc_stones INTEGER DEFAULT 0')

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
                    for name in ('Sword', 'Axe', 'Dagger'):
                        await conn.execute("""
                            INSERT INTO weapon_types (name_base)
                            SELECT $1
                            WHERE NOT EXISTS (SELECT 1 FROM weapon_types WHERE name_base = $1)
                        """, name)
                    # Seed potions (if not already present)
                    await conn.execute("""
                        INSERT INTO shop_items (name, description, price, type)
                        SELECT 'HP Potion', 'Restores 50% of your max HP.', 50, 'potion'
                        WHERE NOT EXISTS (SELECT 1 FROM shop_items WHERE name = 'HP Potion');
                    """)
                    await conn.execute("""
                        INSERT INTO shop_items (name, description, price, type)
                        SELECT 'Energy Potion', 'Restores 1 energy.', 30, 'potion'
                        WHERE NOT EXISTS (SELECT 1 FROM shop_items WHERE name = 'Energy Potion');
                    """)
                    # ========== SHOP ITEMS FOR PETS ==========
                    # First, drop any existing constraint (safe)
                    await conn.execute("ALTER TABLE shop_items DROP CONSTRAINT IF EXISTS shop_items_type_check;")

                    # Delete any rows that are not in the final allowed type list (including any stray rows)
                    await conn.execute("""
                        DELETE FROM shop_items
                        WHERE type NOT IN ('role', 'color', 'weapon', 'random_weapon_box',
                                           'random_gear_box', 'random_accessories_box', 'pickaxe', 'material', 'potion', 'random_pet_box')
                    """)

                    # Insert the Pet Box (if not already present)
                    await conn.execute("""
                        INSERT INTO shop_items (name, description, price, type)
                        SELECT 'Pet Box', 'Contains a random pet! Open to receive one of: Baby Fox, Baby Tiger, or Baby Purr.', 5000, 'random_pet_box'
                        WHERE NOT EXISTS (SELECT 1 FROM shop_items WHERE name = 'Pet Box');
                    """)

                    # Re‑add the constraint with the updated type list
                    await conn.execute("""
                        ALTER TABLE shop_items ADD CONSTRAINT shop_items_type_check
                        CHECK (type IN ('role', 'color', 'weapon', 'random_weapon_box',
                                        'random_gear_box', 'random_accessories_box', 'pickaxe', 'material', 'potion', 'random_pet_box'));
                    """)

                    # 🔽 ADD TITLES SEED HERE 🔽
                    await conn.execute("""
                        INSERT INTO titles (name, emoji, description,
                                            boss_damage_percent, extra_boss_attempts,
                                            hp_percent, def_percent, atk_percent,
                                            crit_chance, dodge_percent, dmg_reduction_percent,
                                            crit_dmg_res_percent, mining_bonus_percent,
                                            bleed_flat, burn_flat)
                        VALUES
                        ('Boss Reaper', '<:boss_reaper:1483707209090334820>', 'Earned by being the top 1 damage dealer in the server boss.',
                         5, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                        ('Administrator', '<:administrator:1470082908151742536>', 'Exclusive title for Server Administrators.',
                         100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 5000, 5000)
                        ON CONFLICT (name) DO NOTHING;
                    """)
                    # 🔼 END TITLES SEED

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
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_pets_user ON user_pets(user_id)')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_pets_equipped ON user_pets(user_id, equipped)')

                self.using_database = True
                print(f"🎉 Success with: {strategy_name}")
                print("✅ Database connected and ready!")
                return True

            except Exception as e:
                print(f"    ❌ Failed: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                if self.pool:
                    await self.pool.close()
                    self.pool = None
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
        self.quiz_questions: List[Dict] = []
        self.current_question: int = 0
        self.participants: Dict[str, Dict] = {}
        self.quiz_channel: Optional[discord.TextChannel] = None
        self.quiz_logs_channel: Optional[discord.TextChannel] = None
        self.quiz_running: bool = False
        self.question_start_time: Optional[datetime] = None
        self.question_expiry: Optional[datetime] = None   # exact expiry timestamp
        self.question_message: Optional[discord.Message] = None
        self.countdown_loop: Optional[asyncio.Task] = None
        self._timer_handle: Optional[asyncio.TimerHandle] = None   # for call_later
        self._ending: bool = False

        # Constants (for easy tuning)
        self.START_DELAY = 60          # seconds before first question
        self.TRANSITION_TIME = 10       # seconds between questions
        self.PARTICIPATION_BASE = 50    # base gems for anyone with >0 score

        self.load_questions()

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
            {"cat": "📘 English", "q": "Complete the idiom: 'Bite the ___' (meaning to endure something unpleasant).", "a": ["bullet"], "pts": 400, "time": 60},
            {"cat": "📘 English", "q": "What is the correct past participle of the verb 'to ring' (as in a bell)?", "a": ["rung"], "pts": 400, "time": 60},
            {"cat": "📘 English", "q": "In the sentence 'She would have gone if she had known', which tense is 'would have gone'?", "a": ["conditional perfect", "past conditional"], "pts": 500, "time": 60},
            {"cat": "📘 English", "q": "What is the term for a verb that functions as a noun (e.g., 'swimming' in 'Swimming is fun')?", "a": ["gerund"], "pts": 400, "time": 60},
            {"cat": "📘 English", "q": "Complete the idiom: 'Spill the ___' (to reveal secret information).", "a": ["beans"], "pts": 400, "time": 60},
            {"cat": "📘 English", "q": "Which type of conditional is used in: 'If I had seen him, I would have told him'?", "a": ["third conditional", "type 3 conditional"], "pts": 500, "time": 60},
            {"cat": "📘 English", "q": "What is the meaning of the phrasal verb 'to put up with'?", "a": ["tolerate", "endure"], "pts": 400, "time": 60},
            {"cat": "📘 English", "q": "What is the term for two or more words that share the same spelling but have different meanings and origins (e.g., 'bank' – financial institution / river bank)?", "a": ["homograph"], "pts": 400, "time": 60},
            {"cat": "📘 English", "q": "Complete the idiom: '___ the bullet' (to face a difficult situation bravely).", "a": ["bite"], "pts": 400, "time": 60},
            {"cat": "📘 English", "q": "Which tense is used to describe an action that will be completed before a specific time in the future (e.g., 'By next week, I will have finished the project')?", "a": ["future perfect"], "pts": 500, "time": 60},
            {"cat": "📘 English", "q": "What is the correct form: 'Neither the students nor the teacher ___ aware of the change.'", "a": ["is"], "pts": 500, "time": 60},
            {"cat": "📘 English", "q": "What is the meaning of the idiom 'to let the cat out of the bag'?", "a": ["reveal a secret"], "pts": 400, "time": 60},
            {"cat": "📘 English", "q": "In grammar, what is a 'dangling modifier'?", "a": ["a word or phrase that modifies a word not clearly stated in the sentence"], "pts": 500, "time": 60},
            {"cat": "📘 English", "q": "Complete the idiom: '___ the icing on the cake' (something extra that makes a good thing even better).", "a": ["it's", "that's", "that is"], "pts": 400, "time": 60},
            {"cat": "📘 English", "q": "What is the correct plural of 'phenomenon'?", "a": ["phenomena"], "pts": 400, "time": 60},
            {"cat": "📘 English", "q": "Which tense is used in: 'She has been working here for five years'?", "a": ["present perfect continuous", "present perfect progressive"], "pts": 500, "time": 60},
            {"cat": "📘 English", "q": "What is the meaning of the idiom 'to burn the midnight oil'?", "a": ["work late into the night"], "pts": 400, "time": 60},
            {"cat": "📘 English", "q": "Correct the sentence: 'Each of the students have submitted their assignment.' What should replace 'have'?", "a": ["has"], "pts": 500, "time": 60},
            {"cat": "📘 English", "q": "What is the term for a word that is formed by combining two or more words, like 'brunch' (breakfast + lunch)?", "a": ["portmanteau", "blend"], "pts": 500, "time": 60},
            {"cat": "📘 English", "q": "Complete the idiom: '___ the benefit of the doubt' (to believe someone despite lack of proof).", "a": ["give"], "pts": 400, "time": 60},

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
            {"cat": "🧠 Logical Reasoning", "q": "In a certain code, 'APPLE' is written as 'ZKKOV'. How is 'BANANA' written in that code?", "a": ["yzmzmz"], "pts": 400, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "If the day after tomorrow is Sunday, what day was it yesterday?", "a": ["thursday"], "pts": 300, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "A man is looking at a portrait. He says, 'Brothers and sisters have I none, but that man's father is my father's son.' Who is in the portrait?", "a": ["his son", "son"], "pts": 400, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "A rooster lays an egg on top of a barn. Which way does it roll?", "a": ["roosters dont lay eggs", "roosters don't lay eggs", "it doesn't roll"], "pts": 300, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "I have two coins that add up to 30 cents, and one of them is not a nickel. What are the two coins?", "a": ["quarter and nickel", "a quarter and a nickel"], "pts": 400, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "A farmer has 17 cows. All but 9 die. How many are left?", "a": ["9"], "pts": 200, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "What number comes next in the sequence: 2, 3, 5, 9, 17, ?", "a": ["33"], "pts": 300, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "If you write all numbers from 1 to 100, how many times do you write the digit 9?", "a": ["20"], "pts": 400, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "A bat and a ball cost $1.10. The bat costs $1 more than the ball. How much does the ball cost (in cents)?", "a": ["5", "5 cents", ".05"], "pts": 300, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "In a race, you pass the person in second place. What place are you in now?", "a": ["second", "2nd"], "pts": 200, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets (in minutes)?", "a": ["5"], "pts": 300, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "What is the smallest positive integer that is divisible by all numbers from 1 to 10?", "a": ["2520"], "pts": 400, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "A doctor gives you three pills and tells you to take one every half hour. How long (in hours) will they last?", "a": ["1", "one", "1 hour"], "pts": 300, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "A snail falls into a 30‑foot well. Each day it climbs 3 feet, but each night it slips back 2 feet. How many days to get out?", "a": ["28"], "pts": 400, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "What is the next letter in the sequence: J, F, M, A, M, J, ?", "a": ["j"], "pts": 300, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "If a brick weighs 3 pounds plus half a brick, how much does a brick weigh (in pounds)?", "a": ["6"], "pts": 300, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "What is the missing number in the sequence: 1, 11, 21, 1211, 111221, ?", "a": ["312211"], "pts": 400, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "A plane crashes on the border of the US and Canada. Where are the survivors buried?", "a": ["survivors are not buried", "they are not buried", "nowhere"], "pts": 300, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "How many months have 28 days?", "a": ["12", "all", "all 12"], "pts": 200, "time": 60},
            {"cat": "🧠 Logical Reasoning", "q": "Tom is taller than Jerry. Jerry is taller than Spike. Spike is taller than Butch. Who is the shortest?", "a": ["butch"], "pts": 200, "time": 60},

            # 🔢 NUMERICAL REASONING
            {"cat": "🔢 Numerical Reasoning", "q": "Solve: 5x + 3 = 2x + 24.", "a": ["7"], "pts": 200, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "A price was increased by 25% to 250. What was the original price?", "a": ["200"], "pts": 200, "time": 30},
            {"cat": "🔢 Numerical Reasoning", "q": "If the ratio of men to women is 3:5 and there are 40 people, how many are men?", "a": ["15"], "pts": 200, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "Find the next number: 2, 5, 11, 23, 47, ___.", "a": ["95"], "pts": 200, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "If a train travels 180 km in 3 hours, how far will it travel in 5 hours at the same speed?", "a": ["300"], "pts": 200, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "If a car travels at 60 km/h, how many kilometers will it travel in 2 hours 15 minutes?", "a": ["135"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "A train covers a distance of 300 km in 4 hours. What is its speed in km/h?", "a": ["75"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "If a worker earns $15 per hour, how much will he earn in 6 hours 30 minutes?", "a": ["97.5", "$97.50", "97.50"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "A recipe requires 2 cups of flour for 12 cookies. How many cups are needed for 30 cookies?", "a": ["5"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "If a shirt originally costs $40 and is on sale for 25% off, what is the sale price?", "a": ["30", "$30"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "A tank can be filled by a pipe in 3 hours. How much of the tank is filled in 1 hour 15 minutes? (Express as a fraction)", "a": ["5/12", "5/12 of the tank"], "pts": 500, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "The sum of two numbers is 30 and their difference is 10. Find the larger number.", "a": ["20"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "If 5 apples cost $2.50, how much do 8 apples cost?", "a": ["4", "$4", "4.00"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "A rectangle has length 12 cm and width 8 cm. What is its area? (Include units, e.g., 96 cm²)", "a": ["96", "96 cm²", "96 cm2"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "A pizza is cut into 8 slices. If 3 slices are eaten, what fraction remains?", "a": ["5/8"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "If a car uses 8 liters of fuel for 100 km, how many liters are needed for 350 km?", "a": ["28"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "A student scored 85, 90, and 78 on three tests. What is the average score? (Round to one decimal)", "a": ["84.3", "84.33"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "How many minutes are there in 2.5 hours?", "a": ["150"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "If a number is increased by 20% and becomes 60, what was the original number?", "a": ["50"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "A bag contains 3 red, 4 blue, and 5 green marbles. What is the probability of picking a blue marble? (Express as a fraction)", "a": ["1/3", "4/12"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "If it takes 4 workers 6 days to complete a job, how many days would 3 workers take? (Assume same work rate)", "a": ["8"], "pts": 500, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "A store offers a 15% discount on a $200 item. How much is the discount in dollars?", "a": ["30", "$30"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "If the ratio of boys to girls is 3:2 and there are 25 students, how many boys are there?", "a": ["15"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "A square has a perimeter of 36 cm. What is its area? (Include units)", "a": ["81", "81 cm²", "81 cm2"], "pts": 400, "time": 60},
            {"cat": "🔢 Numerical Reasoning", "q": "If a phone costs $500 after a 20% discount, what was the original price?", "a": ["625", "$625"], "pts": 500, "time": 60},

            # 🧩 ABSTRACT & PATTERN ANALYSIS
            {"cat": "🧩 Abstract Reasoning", "q": "Find the next letter sequence: B, E, I, N, T, ___.", "a": ["a"], "pts": 200, "time": 60},
            {"cat": "🧩 Abstract Reasoning", "q": "Find the missing number: 1, 1, 2, 6, 24, 120, ___.", "a": ["720"], "pts": 200, "time": 60},
            {"cat": "🧩 Abstract Reasoning", "q": "If TABLE = 40 (sum of letter positions), what is CHAIR?", "a": ["35"], "pts": 200, "time": 60},
            {"cat": "🧩 Abstract Reasoning", "q": "Find the next number: 4, 9, 19, 39, 79, ___.", "a": ["159"], "pts": 200, "time": 60},
            {"cat": "🧩 Abstract Reasoning", "q": "If RED = 27 and BLUE = 40 (sum of letters), what is GREEN?", "a": ["49"], "pts": 200, "time": 60},

            # 🔬 Science – University Level & Trendy (20 questions, 60 seconds each)
            {"cat": "🔬 Science", "q": "What is the name of the gene‑editing technology that uses a protein called Cas9?", "a": ["crispr", "crispr-cas9", "crispr/cas9"], "pts": 500, "time": 60},
            {"cat": "🔬 Science", "q": "In quantum mechanics, what term describes the phenomenon where particles become correlated and instantaneously affect each other regardless of distance?", "a": ["entanglement", "quantum entanglement"], "pts": 500, "time": 60},
            {"cat": "🔬 Science", "q": "What is the name of the hypothetical particle that is its own antiparticle and is a candidate for dark matter?", "a": ["majorana fermion", "majorana particle"], "pts": 500, "time": 60},
            {"cat": "🔬 Science", "q": "Which neurotransmitter is primarily involved in reward, motivation, and motor control, and is often discussed in addiction studies?", "a": ["dopamine"], "pts": 400, "time": 60},
            {"cat": "🔬 Science", "q": "What is the name of the process by which cells engulf and digest large particles or microorganisms?", "a": ["phagocytosis"], "pts": 400, "time": 60},
            {"cat": "🔬 Science", "q": "In particle physics, what force is mediated by the Higgs boson?", "a": ["mass", "the higgs field gives mass", "it gives mass to particles"], "pts": 500, "time": 60},
            {"cat": "🔬 Science", "q": "What is the name of the largest known protein complex that performs oxidative phosphorylation in mitochondria?", "a": ["atp synthase", "complex v"], "pts": 500, "time": 60},
            {"cat": "🔬 Science", "q": "Which technique, widely used in structural biology, involves firing X‑rays at crystallized proteins to determine their 3D structure?", "a": ["x-ray crystallography"], "pts": 500, "time": 60},
            {"cat": "🔬 Science", "q": "What is the name of the theory proposing that consciousness arises from integrated information in the brain, quantified by Φ (phi)?", "a": ["integrated information theory", "iit"], "pts": 500, "time": 60},
            {"cat": "🔬 Science", "q": "Which element is used as the primary fuel in most nuclear fission reactors?", "a": ["uranium", "u-235", "uranium-235"], "pts": 400, "time": 60},
            {"cat": "🔬 Science", "q": "What is the term for the maximum distance at which a telescope can resolve two point sources as separate?", "a": ["angular resolution", "diffraction limit"], "pts": 400, "time": 60},
            {"cat": "🔬 Science", "q": "Which 2023 Nobel Prize in Physics topic involved attosecond pulses of light to study electron dynamics?", "a": ["attosecond physics", "attosecond pulses"], "pts": 500, "time": 60},
            {"cat": "🔬 Science", "q": "In chemistry, what is the name of the effect where a molecule's reactivity is influenced by the spatial arrangement of its atoms?", "a": ["steric effect", "steric hindrance"], "pts": 400, "time": 60},
            {"cat": "🔬 Science", "q": "What is the name of the protein that bacteria use as an adaptive immune system, leading to the CRISPR technology?", "a": ["cas9", "crispr-associated protein 9"], "pts": 500, "time": 60},
            {"cat": "🔬 Science", "q": "Which space telescope, launched in 2021, observes in the infrared and is the successor to Hubble?", "a": ["james webb", "james webb space telescope", "jwst"], "pts": 400, "time": 60},
            {"cat": "🔬 Science", "q": "What is the name of the geological epoch defined by human impact on Earth's ecosystems, often proposed to have started in the mid‑20th century?", "a": ["anthropocene"], "pts": 400, "time": 60},
            {"cat": "🔬 Science", "q": "In genetics, what does 'CRISPR' stand for?", "a": ["clustered regularly interspaced short palindromic repeats"], "pts": 500, "time": 60},
            {"cat": "🔬 Science", "q": "What is the name of the first quantum computer developed by Google that claimed quantum supremacy in 2019?", "a": ["sycamore"], "pts": 500, "time": 60},
            {"cat": "🔬 Science", "q": "Which enzyme is responsible for unzipping DNA during replication?", "a": ["helicase"], "pts": 400, "time": 60},
            {"cat": "🔬 Science", "q": "What is the term for the minimum energy required to remove an electron from an atom in its ground state?", "a": ["ionization energy", "ionisation energy"], "pts": 400, "time": 60},
        ]

    # ------------------------------------------------------------
    # POINTS & UTILITIES
    # ------------------------------------------------------------
    def calculate_points(self, answer_time: int, total_time: int, max_points: int) -> int:
        """Calculate points based on time left, with a minimum of 1 point."""
        time_left = total_time - answer_time
        if time_left <= 0:
            return 0
        points = int(max_points * (time_left / total_time))
        return max(points, 1)   # guarantee at least 1 point for a correct answer

    def calculate_average_time(self, user_data: Dict) -> float:
        """Calculate average response time for correct answers."""
        correct_times = [a['time'] for a in user_data['answers'] if a['correct']]
        return sum(correct_times) / len(correct_times) if correct_times else 0

    def get_rank_emoji(self, rank: int) -> str:
        """Return an emoji for the given rank (1-10)."""
        rank_emojis = {
            1: "🥇", 2: "🥈", 3: "🥉", 4: "4️⃣", 5: "5️⃣",
            6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
        }
        return rank_emojis.get(rank, f"{rank}.")

    # ------------------------------------------------------------
    # QUIZ LIFECYCLE
    # ------------------------------------------------------------
    async def start_quiz(self, channel: discord.TextChannel, logs_channel: discord.TextChannel):
        """Start the quiz with a 60‑second countdown and 20 random questions."""
        try:
            self.quiz_channel = channel
            self.quiz_logs_channel = logs_channel
            print(f"📢 quiz_logs_channel set to #{logs_channel.name} (ID: {logs_channel.id})")
            await log_to_discord(self.bot, f"📢 quiz_logs_channel set to #{logs_channel.name}", "INFO")
            self.quiz_running = True
            self.current_question = 0
            self.participants = {}
            self.question_start_time = None
            self.question_expiry = None
            self._ending = False

            # --- RANDOMLY SELECT 20 QUESTIONS FROM THE POOL ---
            pool = self.all_questions
            num_questions = min(20, len(pool))
            self.quiz_questions = random.sample(pool, num_questions)
            # No need to shuffle again; sample already randomizes

            await log_to_discord(self.bot, f"📚 Selected {num_questions} random questions", "INFO")

            # --- START EMBED ---
            embed = discord.Embed(
                title="🎯 **Quiz Time!**",
                description=(
                    "```\n"
                    "• Type your answer in chat\n"
                    "• Correct Spelling only!\n"
                    "• Faster answers = more points\n"
                    "• Multiple attempts allowed\n"
                    "```\n"
                    f"**First question starts in** ⏰ **{self.START_DELAY} seconds**"
                ),
                color=0xFFD700
            )

            if channel.guild.icon:
                embed.set_thumbnail(url=channel.guild.icon.url)
            embed.set_footer(text="Good luck! 🍀", icon_url=self.bot.user.display_avatar.url)

            start_msg = await channel.send(embed=embed)

            # Countdown loop with error handling
            for i in range(self.START_DELAY, 0, -1):
                embed.description = (
                    "```\n"
                    "• Type your answer in chat\n"
                    "• Correct Spelling only!\n"
                    "• Faster answers = more points\n"
                    "• Multiple attempts allowed\n"
                    "```\n"
                    f"**First question starts in** ⏰ **{i} seconds**"
                )
                try:
                    await start_msg.edit(embed=embed)
                except discord.NotFound:
                    await log_to_discord(self.bot, "Start message deleted, aborting quiz", "WARN")
                    return
                except Exception as e:
                    await log_to_discord(self.bot, f"Error during countdown edit: {e}", "ERROR")
                    # Continue counting; if edit fails repeatedly, maybe break
                await asyncio.sleep(1)

            await start_msg.delete()
            await self.send_question()
            await log_to_discord(self.bot, "✅ Quiz started", "INFO")
        except Exception as e:
            await log_to_discord(self.bot, "❌ start_quiz failed", "ERROR", e)

    async def send_question(self):
        """Send the next quiz question and start timers."""
        try:
            if self.current_question >= len(self.quiz_questions):
                await self.end_quiz()
                return

            # Cancel any pending timer from previous question
            if self._timer_handle:
                self._timer_handle.cancel()
                self._timer_handle = None

            q = self.quiz_questions[self.current_question]

            # --- QUESTION EMBED WITH CATEGORY ---
            embed = discord.Embed(
                title=f"❓ **{q.get('cat', 'General')}**",
                description=f"```\n{q['q']}\n```",
                color=0x1E90FF
            )
            embed.add_field(
                name=f"⏳ **Time Left**",
                value=f"```\n{'🟩'*20}\n{q['time']:02d} seconds\n```\n**Max Points:** ⭐ {q['pts']}",
                inline=False
            )
            embed.set_footer(
                text=f"Question {self.current_question+1}/{len(self.quiz_questions)} • {q.get('cat', '')}",
                icon_url=self.quiz_channel.guild.icon.url if self.quiz_channel.guild.icon else None
            )

            self.question_message = await self.quiz_channel.send(embed=embed)
            self.question_start_time = datetime.now(timezone.utc)
            self.question_expiry = self.question_start_time + timedelta(seconds=q['time'])

            # --- TIMERS ---
            if self.countdown_loop:
                self.countdown_loop.cancel()
            self.countdown_loop = self.bot.loop.create_task(self._run_countdown(q['time']))

            # Schedule the expiry callback (store handle for cancellation)
            self._timer_handle = self.bot.loop.call_later(
                q['time'],
                lambda: asyncio.create_task(self._timer_expired())
            )

            await log_to_discord(self.bot, f"⏲️ Timer set for {q['time']}s (Q{self.current_question+1})", "INFO")

        except Exception as e:
            await log_to_discord(self.bot, "❌ send_question failed", "ERROR", e)

    async def _timer_expired(self):
        """Called when the question time limit is reached."""
        # Double‑check that the quiz is still running and this question is still current
        if not self.quiz_running or self.current_question >= len(self.quiz_questions):
            return
        await log_to_discord(self.bot, f"⏳ Timer expired for question {self.current_question+1}", "INFO")
        await self.end_question()

    async def _run_countdown(self, total_time: int):
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

                # 4‑color bar based on percentage remaining
                if ratio > 0.75:
                    bar_char = "🟩"      # Green
                    embed_color = discord.Color.blue()
                elif ratio > 0.50:
                    bar_char = "🟨"      # Yellow
                    embed_color = discord.Color.green()
                elif ratio > 0.25:
                    bar_char = "🟧"      # Orange
                    embed_color = discord.Color.orange()
                else:
                    bar_char = "🟥"      # Red
                    embed_color = discord.Color.red()

                bar = bar_char * progress + "⬜" * (20 - progress)

                # Update the timer field
                field_updated = False
                for i, field in enumerate(embed.fields):
                    if "⏳" in field.name:
                        embed.set_field_at(
                            i,
                            name=f"⏳ **{time_left:02d} SECONDS LEFT**",
                            value=f"```\n{bar}\n{time_left:02d} seconds\n```\n**Max Points:** ⭐ {self.quiz_questions[self.current_question]['pts']}",
                            inline=False
                        )
                        field_updated = True
                        break

                if not field_updated:
                    await log_to_discord(self.bot, "Timer field not found in embed", "WARN")
                    break

                embed.color = embed_color
                await self.question_message.edit(embed=embed)

            except Exception as e:
                await log_to_discord(self.bot, "⚠️ Countdown error (non‑fatal)", "WARN", e)
            await asyncio.sleep(1)

        await log_to_discord(self.bot, "⏹️ Countdown finished", "INFO")

    # ------------------------------------------------------------
    # ANSWER PROCESSING
    # ------------------------------------------------------------
    async def process_answer(self, user: discord.User, answer_text: str, message: discord.Message = None) -> bool:
        try:
            await log_to_discord(self.bot, f"[PA] Called by {user.id} ({user.display_name})", "DEBUG")
            await log_to_discord(self.bot, f"[PA] quiz_running={self.quiz_running}", "DEBUG")
            await log_to_discord(self.bot, f"[PA] question_start_time={self.question_start_time}", "DEBUG")
            await log_to_discord(self.bot, f"[PA] question_expiry={self.question_expiry}", "DEBUG")
            await log_to_discord(self.bot, f"[PA] current_question={self.current_question}/{len(self.quiz_questions)}", "DEBUG")

            if not self.quiz_running:
                await log_to_discord(self.bot, "[PA] → quiz not running", "DEBUG")
                return False
            if self.question_start_time is None or self.question_expiry is None:
                await log_to_discord(self.bot, "[PA] → timers not set", "DEBUG")
                return False
            if self.current_question >= len(self.quiz_questions):
                await log_to_discord(self.bot, "[PA] → current_question out of range", "DEBUG")
                return False

            now = datetime.now(timezone.utc)
            # Grace period of 0.5 seconds
            grace = timedelta(seconds=0.5)
            if now > self.question_expiry + grace:
                await log_to_discord(self.bot, f"[PA] → answer after expiry + grace: now={now}, expiry={self.question_expiry}", "DEBUG")
                return False

            q = self.quiz_questions[self.current_question]
            answer_time = (now - self.question_start_time).seconds
            uid = str(user.id)

            if uid not in self.participants:
                await log_to_discord(self.bot, f"[PA] → adding new participant {uid}", "DEBUG")
                self.participants[uid] = {
                    "name": user.display_name,
                    "score": 0,
                    "answers": [],
                    "correct_answers": 0,
                    "answered_current": False
                }

            if self.participants[uid]["answered_current"]:
                await log_to_discord(self.bot, "[PA] → already answered correctly", "DEBUG")
                return False

            user_ans = answer_text.lower().strip()
            correct_answers = [a.lower() for a in q['a']]
            is_correct = user_ans in correct_answers
            await log_to_discord(self.bot, f"[PA] answer='{user_ans}', correct={is_correct}", "DEBUG")

            points = 0
            if is_correct:
                points = self.calculate_points(answer_time, q['time'], q['pts']) 
                self.participants[uid]["score"] += points
                self.participants[uid]["correct_answers"] += 1
                self.participants[uid]["answered_current"] = True
                await log_to_discord(self.bot, f"[PA] → correct! points={points}, new score={self.participants[uid]['score']}", "DEBUG")

            self.participants[uid]["answers"].append({
                "question": self.current_question,
                "answer": answer_text,
                "correct": is_correct,
                "points": points,
                "time": answer_time
            })

            if is_correct:
                await log_to_discord(self.bot, "[PA] → logging to quiz-logs", "DEBUG")
                await self.log_answer(user, q['q'], answer_text, points, answer_time)

            await log_to_discord(self.bot, f"[PA] → done. participants count={len(self.participants)}", "DEBUG")
            return True

        except Exception as e:
            await log_to_discord(self.bot, f"❌ process_answer error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

    async def log_answer(self, user: discord.User, question: str, answer: str, points: int, time: int):
        """Log a correct answer to the logs channel."""
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
        """End current question, show stats, countdown, and move to next."""
        await log_to_discord(self.bot, f"🔚 end_question() called for Q{self.current_question+1}", "INFO")
        try:
            # Cancel the timer handle
            if self._timer_handle:
                self._timer_handle.cancel()
                self._timer_handle = None

            # --- DELETE THE QUESTION MESSAGE ---
            if self.question_message:
                try:
                    await self.question_message.delete()
                    await log_to_discord(self.bot, f"🗑️ Deleted question message for Q{self.current_question+1}", "INFO")
                except Exception as e:
                    await log_to_discord(self.bot, f"⚠️ Could not delete question message: {e}", "WARN")
                finally:
                    self.question_message = None

            # --- STOP COUNTDOWN LOOP ---
            if self.countdown_loop:
                self.countdown_loop.cancel()
                self.countdown_loop = None
            self.question_start_time = None
            self.question_expiry = None

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

            stats_msg = await self.quiz_channel.send(embed=embed)
            self.bot.loop.create_task(self._delete_after(stats_msg, 10))
            await log_to_discord(self.bot, "📊 Statistics embed will self‑destruct in 10s", "INFO")

            # --- LAST QUESTION? ---
            if self.current_question + 1 == len(self.quiz_questions):
                await log_to_discord(self.bot, "🏁 Last question finished, calling end_quiz()", "INFO")
                await self.end_quiz()
                return

            # --- NOT LAST: LEADERBOARD + COUNTDOWN ---
            lb_embed = await self.create_leaderboard()   # initial (no countdown)
            lb_msg = await self.quiz_channel.send(embed=lb_embed)

            for seconds in range(self.TRANSITION_TIME, 0, -1):
                updated = await self.create_leaderboard(countdown=seconds, total=self.TRANSITION_TIME)
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

    async def create_leaderboard(self, countdown: Optional[int] = None, total: int = 10) -> discord.Embed:
        """Create a leaderboard embed, optionally with a countdown bar."""
        try:
            if not self.participants:
                return discord.Embed(title="📊 Leaderboard", description="No participants yet!", color=discord.Color.blue())

            sorted_p = sorted(self.participants.items(), key=lambda x: x[1]["score"], reverse=True)
            embed = discord.Embed(title="📊 **LEADERBOARD**", color=discord.Color.gold())

            # --- COUNTDOWN BAR (if applicable) ---
            if countdown is not None:
                # total should be the full countdown duration (e.g., 10 seconds)
                progress = int((countdown / total) * 10)  # 10 blocks
                ratio = countdown / total

                if ratio > 0.75:
                    bar_char = "🟩"
                elif ratio > 0.50:
                    bar_char = "🟨"
                elif ratio > 0.25:
                    bar_char = "🟧"
                else:
                    bar_char = "🟥"

                bar = bar_char * progress + "⬜" * (10 - progress)
                embed.description = (
                    f"⏳ **Next question in:** `{countdown}s`\n"
                    f"```\n{bar}\n{countdown:02d} / {total:02d} seconds\n```"
                )
            else:
                embed.description = "🏆 **Current standings**"

            # --- RANKINGS WITH PER‑QUESTION STATUS ---
            lines = []
            for i, (uid, data) in enumerate(sorted_p):
                # Determine status for the current question
                attempts = [a for a in data["answers"] if a["question"] == self.current_question]
                if not attempts:
                    status = "❌ No answer"
                else:
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

    async def _delete_after(self, message: discord.Message, delay: int):
        """Delete a message after `delay` seconds."""
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except:
            pass

    # ------------------------------------------------------------
    # REWARD DISTRIBUTION
    # ------------------------------------------------------------
    async def distribute_quiz_rewards(self, sorted_participants: List[Tuple[str, Dict]]) -> Dict[str, Dict]:
        """Give gems to participants who scored > 0."""
        rewards = {}

        # Determine the number of questions for perfect accuracy check
        total_questions = len(self.quiz_questions)

        for rank, (uid, data) in enumerate(sorted_participants, 1):
            # Skip participants with zero score
            if data["score"] <= 0:
                await log_to_discord(self.bot, f"⏭️ Skipping {data['name']} – score 0, no reward", "INFO")
                rewards[uid] = {"gems": 0, "rank": rank, "result": None}
                continue

            try:
                base = self.PARTICIPATION_BASE
                if rank == 1:
                    base += 500
                elif rank == 2:
                    base += 250
                elif rank == 3:
                    base += 125
                elif rank <= 10:
                    base += 75

                base += (data["score"] // 100) * 10          # score bonus
                base += self.calculate_speed_bonus(uid)      # speed bonus

                # Perfect accuracy bonus (all questions correct)
                if data["correct_answers"] == total_questions:
                    base += 250
                    reason = f"🎯 Perfect Accuracy! ({data['correct_answers']}/{total_questions} correct, Rank #{rank})"
                else:
                    reason = f"🏆 Quiz Rewards ({data['score']} pts, Rank #{rank})"

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

    def calculate_speed_bonus(self, user_id: str) -> int:
        """Calculate a small bonus for very fast correct answers (max 50)."""
        if user_id not in self.participants:
            return 0
        bonus = 0
        for ans in self.participants[user_id]["answers"]:
            if ans["correct"] and ans["time"] < 10:
                bonus += max(1, 10 - ans["time"])
        return min(bonus, 50)

    async def log_reward(self, user_id: str, username: str, gems: int, rank: int):
        """Log a reward distribution to the logs channel."""
        if not self.quiz_logs_channel:
            return
        embed = discord.Embed(title="💰 Gems Distributed", color=discord.Color.gold())
        embed.add_field(name="👤 User", value=username, inline=True)
        embed.add_field(name="🏆 Rank", value=f"#{rank}", inline=True)
        embed.add_field(name="💎 Gems", value=f"+{gems}", inline=True)
        await self.quiz_logs_channel.send(embed=embed)

    # ------------------------------------------------------------
    # STOP QUIZ (IMMEDIATE)
    # ------------------------------------------------------------
    async def stop_quiz(self):
        """Immediately stop the quiz and reset all state."""
        await log_to_discord(self.bot, "🛑 stop_quiz() called", "INFO")

        self.quiz_running = False
        self._ending = True

        # Cancel all timers
        if self._timer_handle:
            self._timer_handle.cancel()
            self._timer_handle = None

        if self.countdown_loop:
            self.countdown_loop.cancel()
            self.countdown_loop = None

        # Delete the current question message if it exists
        if self.question_message:
            try:
                await self.question_message.delete()
            except Exception as e:
                await log_to_discord(self.bot, f"Could not delete question message: {e}", "WARN")
            finally:
                self.question_message = None

        self.question_start_time = None
        self.question_expiry = None

        # Reset all state
        self.quiz_channel = None
        self.quiz_logs_channel = None
        self.current_question = 0
        self.participants = {}
        self._ending = False

        await log_to_discord(self.bot, "✅ Quiz stopped and reset", "INFO")

    # ------------------------------------------------------------
    # END QUIZ (FINAL)
    # ------------------------------------------------------------
    async def end_quiz(self):
        """End the quiz, distribute rewards, and send final leaderboard."""
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
            self.question_expiry = None

            # Cancel any remaining timers
            if self._timer_handle:
                self._timer_handle.cancel()
                self._timer_handle = None
            if self.countdown_loop:
                self.countdown_loop.cancel()
                self.countdown_loop = None

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

            rank_map = {uid: i+1 for i, (uid, _) in enumerate(sorted_p)}

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

            # --- 7. SEND DMs (using fetch_user to ensure we get uncached users) ---
            dm_count = 0
            for uid, data in self.participants.items():
                reward = rewards.get(uid, {})
                if reward and reward.get("gems", 0) > 0:
                    try:
                        # Fetch the user even if not cached
                        user = await self.bot.fetch_user(int(uid))
                        if user:
                            balance = await self.currency.get_balance(uid)
                            dm = discord.Embed(
                                title="🎉 Quiz Rewards!",
                                description=f"**Final Score:** {data['score']} pts\n**Rank:** #{rank_map[uid]}",
                                color=discord.Color.gold()
                            )
                            dm.add_field(name="*Rewards*", value=f"💎 +{reward['gems']} Gems", inline=False)
                            dm.add_field(name="*New Balance*", value=f"💎 {balance['gems']} Gems", inline=False)
                            await user.send(embed=dm)
                            dm_count += 1
                    except discord.NotFound:
                        await log_to_discord(self.bot, f"User {uid} not found, DM skipped", "WARN")
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
            self.question_expiry = None
            self.quiz_running = False
            self.countdown_loop = None
            self._timer_handle = None
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
            title=f"🎁 **You've received {GEM_EMOJI}**",
            description=f"**{admin.name}** has added Gems to your account.",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="Amount Added", value=f"**+{amount} {GEM_EMOJI}**", inline=True)
        embed.add_field(name="New Balance", value=f"**{new_balance} {GEM_EMOJI}**", inline=True)
        
        
        
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
    
    # --- Award potions ---
    hp_potion_id = None
    energy_potion_id = None
    async with bot.db_pool.acquire() as conn:
        hp_potion_id = await conn.fetchval("SELECT item_id FROM shop_items WHERE name = 'HP Potion'")
        energy_potion_id = await conn.fetchval("SELECT item_id FROM shop_items WHERE name = 'Energy Potion'")

        if hp_potion_id:
            await conn.execute("""
                INSERT INTO user_materials (user_id, material_id, quantity)
                VALUES ($1, $2, 1)
                ON CONFLICT (user_id, material_id) DO UPDATE
                SET quantity = user_materials.quantity + 1
            """, user_id, hp_potion_id)

        if energy_potion_id:
            await conn.execute("""
                INSERT INTO user_materials (user_id, material_id, quantity)
                VALUES ($1, $2, 1)
                ON CONFLICT (user_id, material_id) DO UPDATE
                SET quantity = user_materials.quantity + 1
            """, user_id, energy_potion_id)

    # Build embed
    embed = discord.Embed(
        title="🎁 **Daily Reward Claimed!**",
        description=f"Here's your daily reward, {ctx.author.mention}!",
        color=discord.Color.gold()
    )

    embed.add_field(name="Gems Earned", value=f"**+{result['gems']} {GEM_EMOJI}**", inline=False)

    potion_text = []
    if hp_potion_id:
        hp_emoji = CUSTOM_EMOJIS.get('hp_potion', '💚')
        potion_text.append(f"{hp_emoji} **1x HP Potion**")
    if energy_potion_id:
        energy_emoji = CUSTOM_EMOJIS.get('energy_potion', '⚡')
        potion_text.append(f"{energy_emoji} **1x Energy Potion**")

    if potion_text:
        field_icon = CUSTOM_EMOJIS.get('hp_potion')
        embed.add_field(
            name=f"{field_icon} Potions",
            value="\n".join(potion_text),
            inline=False
        )

    embed.add_field(
        name="🔥 Daily Streak",
        value=f"**{result['streak']} days**",
        inline=True
    )

    embed.add_field(name="New Balance", value=f"**{result['balance']} {GEM_EMOJI}**", inline=True)

    embed.set_footer(text="Come back tomorrow for more rewards!")
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

            embed.add_field(name="Amount Added", value=f"**+{amount} {GEM_EMOJI}**", inline=True)
            embed.add_field(name="New Balance", value=f"**{balance['gems']} {GEM_EMOJI}**", inline=True)
            embed.add_field(name="Added By", value=ctx.author.mention, inline=True)

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
        title="Your Balance",
        description=f"**{GEM_EMOJI} {balance['gems']} Gems**",
        color=discord.Color.gold()
    )
    
    embed.set_footer(text="")
    await ctx.send(embed=embed)


# --- ANSWER DETECTION ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)

    # --- 1. Handle pending gem input for trades ---
    if user_id in pending_gem_inputs:
        pending = pending_gem_inputs[user_id]
        if time.time() > pending['expires']:
            del pending_gem_inputs[user_id]
            await message.channel.send("⌛ Gem addition timed out.", delete_after=5)
            return

        try:
            gems = int(message.content)
            if gems <= 0:
                raise ValueError
        except ValueError:
            await message.channel.send("❌ Invalid amount. Please enter a positive number.", delete_after=5)
            return

        balance = await currency_system.get_balance(user_id)
        if balance['gems'] < gems:
            await message.channel.send("❌ You don't have that many gems.", delete_after=5)
            return

        async with bot.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO trade_items (trade_id, user_id, item_type, item_id, gems)
                VALUES ($1, $2, 'gems', 0, $3)
            """, pending['trade_id'], user_id, gems)

        try:
            channel = bot.get_channel(pending['channel_id'])
            if channel:
                trade_msg = await channel.fetch_message(pending['message_id'])
                await update_trade_embed(trade_msg, pending['trade_id'])
        except Exception as e:
            print(f"Error updating trade message: {e}")

        await message.channel.send(f"✅ Added **{gems} gems** to the trade.", delete_after=5)
        del pending_gem_inputs[user_id]
        return

    # --- NEW: Handle material quantity input for trades ---
    if user_id in pending_material_inputs:
        pending = pending_material_inputs[user_id]
        if time.time() > pending['expires']:
            del pending_material_inputs[user_id]
            await message.channel.send("⌛ Quantity input timed out.", delete_after=5)
            return

        try:
            qty = int(message.content)
            if qty <= 0:
                raise ValueError
        except ValueError:
            await message.channel.send("❌ Invalid amount. Please enter a positive number.", delete_after=5)
            return

        async with bot.db_pool.acquire() as conn:
            available = await conn.fetchval("""
                SELECT quantity FROM user_materials
                WHERE user_id = $1 AND material_id = $2
            """, user_id, pending['material_id'])
            if not available or available < qty:
                await message.channel.send(f"❌ You only have {available or 0} of that item.", delete_after=5)
                del pending_material_inputs[user_id]
                return

            await conn.execute("""
                INSERT INTO trade_items (trade_id, user_id, item_type, item_id, gems, quantity)
                VALUES ($1, $2, 'material', $3, 0, $4)
            """, pending['trade_id'], user_id, pending['material_id'], qty)

        try:
            channel = bot.get_channel(pending['channel_id'])
            if channel:
                trade_msg = await channel.fetch_message(pending['message_id'])
                await update_trade_embed(trade_msg, pending['trade_id'])
        except Exception as e:
            print(f"Error updating trade message: {e}")

        await message.channel.send(f"✅ Added **{qty}** of that consumable to the trade.", delete_after=5)
        del pending_material_inputs[user_id]
        return

    # --- 2. Quiz answer handling ---
    if quiz_system.quiz_running and message.channel == quiz_system.quiz_channel:
        await log_to_discord(bot, f"📨 QUIZ MSG from {message.author.display_name}: '{message.content[:50]}'", "DEBUG")
        try:
            # Pass the message object to process_answer so we can add reactions
            result = await quiz_system.process_answer(message.author, message.content, message)
            await log_to_discord(bot, f"⏪ process_answer returned: {result}", "DEBUG")
        except Exception as e:
            await log_to_discord(bot, f"❌ Error in on_message: {e}", "ERROR")
        # Continue to process commands if desired (optional)

    # --- 3. Process commands ---
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

#   FOR BLEED AND BURN

@tasks.loop(seconds=1)
async def process_effects():
    try:
        async with bot.db_pool.acquire() as conn:
            # Apply damage from active effects (bleed/burn)
            await conn.execute("""
                UPDATE player_stats
                SET hp = GREATEST(hp - value, 0)
                FROM active_effects
                WHERE player_stats.user_id = active_effects.target_id
                  AND active_effects.remaining_ticks > 0
            """)
            # Decrement ticks
            await conn.execute("""
                UPDATE active_effects
                SET remaining_ticks = remaining_ticks - 1
                WHERE remaining_ticks > 0
            """)
            # Delete expired effects
            await conn.execute("DELETE FROM active_effects WHERE remaining_ticks <= 0")

            # Set respawn timer for players who just died
            await conn.execute("""
                UPDATE player_stats
                SET respawn_at = NOW() + INTERVAL '2 hours'
                WHERE hp <= 0 AND respawn_at IS NULL
            """)
    except Exception as e:
        print(f"❌ process_effects error: {e}")
        traceback.print_exc()

        # If the pool is closed, try to reconnect
        if bot.db_pool and bot.db_pool._closed:
            print("🔄 Database pool closed – attempting to reconnect...")
            try:
                await db.smart_connect()   # this reassigns bot.db_pool internally
            except Exception as re:
                print(f"❌ Reconnection failed: {re}")

@tasks.loop(minutes=1)
async def respawn_task():
    """Respawn dead players with full HP and energy."""
    try:
        async with bot.db_pool.acquire() as conn:
            # Get all users whose respawn time has passed
            dead_users = await conn.fetch("""
                SELECT user_id FROM player_stats
                WHERE respawn_at IS NOT NULL AND respawn_at <= NOW() AT TIME ZONE 'UTC'
            """)
        for dead in dead_users:
            user_id = dead['user_id']
            # Get dynamic stats (includes pet bonuses)
            stats = await get_player_stats(user_id)
            # Update to full HP and full energy (dynamic max)
            async with bot.db_pool.acquire() as conn2:
                await conn2.execute("""
                    UPDATE player_stats
                    SET hp = $1, energy = $2, respawn_at = NULL
                    WHERE user_id = $3
                """, stats['max_hp'], stats['max_energy'], user_id)
        print("respawn_task tick")
    except Exception as e:
        print(f"❌ respawn_task error: {e}")
        traceback.print_exc()

@respawn_task.before_loop
async def before_respawn_task():
    await bot.wait_until_ready()
    while bot.db_pool is None:
        await asyncio.sleep(1)

@tasks.loop(hours=1)
async def remove_expired_titles():
    try:
        async with bot.db_pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM user_titles
                WHERE expires_at IS NOT NULL AND expires_at <= NOW() AT TIME ZONE 'UTC'
            """)
            print("🧹 Removed expired titles.")
    except Exception as e:
        print(f"❌ remove_expired_titles error: {e}")
        traceback.print_exc()

@remove_expired_titles.before_loop
async def before_remove_expired_titles():
    await bot.wait_until_ready()
    while bot.db_pool is None:
        await asyncio.sleep(1)

# === BOT STARTUP ===
@bot.event
async def on_ready():
    print(f"\n✅ {bot.user} is online!")
    # Load persistent guild data only once
    if not hasattr(bot, '_loaded_persistence'):
        print("🔄 Loading persistent guild data...")
        await load_active_bags()               # fortune bags
        await load_shop_persistence(bot)        # shop messages
        await load_mining_persistence(bot)      # mining views
        await load_boss_persistence()           # boss views
        bot._loaded_persistence = True
        print("✅ Persistent guild data loaded.")
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

async def setup_hook():
    """Set up the bot before it connects to Discord."""
    print("🔄 setup_hook: started")
    # 1. Connect to PostgreSQL
    connected = await db.smart_connect()
    if not connected:
        print("⚠️ Database connection failed – some features will not work.")
        # Still add cogs (they may work partially)
        await bot.add_cog(Shop(bot))
        await bot.add_cog(CullingGame(bot, currency_system))
        print("✅ setup_hook: cogs added (no DB)")
        return

    # 2. Add cogs first (they don't need guilds)
    await bot.add_cog(Shop(bot))
    await bot.add_cog(CullingGame(bot, currency_system))
    print("✅ setup_hook: cogs added")

    # 3. Start global background tasks (they don't need guilds either)
    clean_old_trades.start()
    process_effects.start()
    respawn_task.start()
    boss_reset_task.start()
    remove_expired_titles.start()
    print("✅ setup_hook: background tasks started")

bot.setup_hook = setup_hook

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


# ========== INVENTORY CLASSES ==========

class InventoryItemButton(discord.ui.Button):
    def __init__(self, item_data, item_type, row=None, awakened=False):
        self.item_data = item_data
        self.item_type = item_type
        if item_type == 'pet':
            item_emoji = get_pet_emoji(item_data['name'])
        else:
            item_emoji = get_item_emoji(item_data['name'], item_type, awakened=awakened)
        style = discord.ButtonStyle.success if item_data.get('equipped') else discord.ButtonStyle.secondary
        custom_id = f"inv_{item_type}_{item_data['id']}"
        super().__init__(label="", emoji=item_emoji, style=style, custom_id=custom_id, row=row)

    async def callback(self, interaction: discord.Interaction):
        try:
            shop_cog = self.view.cog
            await shop_cog.handle_item_selection(
                interaction, 
                self.item_type, 
                self.item_data['id']
            )
        except Exception as e:
            print(f"Error in InventoryItemButton: {e}")
            traceback.print_exc()
            try:
                await interaction.response.send_message("An error occurred.", ephemeral=True)
            except:
                try:
                    await interaction.followup.send("An error occurred.", ephemeral=True)
                except:
                    pass

class CategoryView(discord.ui.View):
    def __init__(self, user_id, items, item_type, parent_view, page=0):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.items = items
        self.item_type = item_type
        self.parent = parent_view
        self.cog = parent_view.cog
        self.page = page
        self.items_per_page = 20
        self.max_page = (len(items) - 1) // self.items_per_page

        start = self.page * self.items_per_page
        end = min(start + self.items_per_page, len(items))
        page_items = items[start:end]

        if item_type == 'material' or item_type == 'mixed':
            for i, item in enumerate(page_items):
                # Check if it's a title (by looking for 'category' or 'title_id')
                if item.get('category') == 'title' or 'title_id' in item:
                    # Title button
                    emoji = item.get('emoji') or '👑'
                    label = item['name']
                    custom_id = f"inv_title_{item['id']}"
                else:
                    # Material button – using your exact logic (no fallback)
                    name_lower = item['name'].lower()
                    if 'hp potion' in name_lower:
                        emoji = CUSTOM_EMOJIS.get('hp_potion')
                    elif 'energy potion' in name_lower:
                        emoji = CUSTOM_EMOJIS.get('energy_potion')
                    elif 'sword' in name_lower:
                        emoji = CUSTOM_EMOJIS.get('sword_enhancement_stone')
                    elif 'armor' in name_lower:
                        emoji = CUSTOM_EMOJIS.get('armors_enhancement_stone')
                    elif 'accessories' in name_lower:
                        emoji = CUSTOM_EMOJIS.get('acc_enhancement_stone')
                    else:
                        emoji = '📦'
                    label = f"x{item['quantity']}"
                    custom_id = f"inv_material_{item['material_id']}"

                button = discord.ui.Button(
                    label=label,
                    emoji=emoji,
                    style=discord.ButtonStyle.secondary,
                    custom_id=custom_id,
                    row=i // 5
                )
                self.add_item(button)
        else:
            # Weapons, armor, accessories – use InventoryItemButton
            for i, item in enumerate(page_items):
                row = i // 5
                self.add_item(InventoryItemButton(item, item_type, row=row, awakened=item.get('awakened', False)))

        # Pagination buttons
        if self.max_page > 0:
            if self.page > 0:
                self.add_item(discord.ui.Button(
                    label="◀",
                    style=discord.ButtonStyle.secondary,
                    custom_id=f"category_prev_{item_type}_{self.page}",
                    row=4
                ))
            if self.page < self.max_page:
                self.add_item(discord.ui.Button(
                    label="▶",
                    style=discord.ButtonStyle.secondary,
                    custom_id=f"category_next_{item_type}_{self.page}",
                    row=4
                ))

        # Always add back button
        self.add_item(discord.ui.Button(
            label="🔙",
            style=discord.ButtonStyle.secondary,
            custom_id="category_back",
            row=4
        ))



class InventoryView(discord.ui.View):
    def __init__(self, user_id, inventory_data, cog):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.inventory = inventory_data
        self.cog = cog

        paw_emoji = discord.PartialEmoji(name="paw", id=1482627374066565170)
        energy_emoji = discord.PartialEmoji(name="energy_potion", id=1481365820566409236)

        # Add buttons with custom_ids
        self.add_item(discord.ui.Button(
            label="🗡️ Weapons", 
            style=discord.ButtonStyle.primary, 
            custom_id="inventory_weapons", 
            row=0
        ))
        self.add_item(discord.ui.Button(
            label="🛡️ Armor", 
            style=discord.ButtonStyle.primary, 
            custom_id="inventory_armor", 
            row=0
        ))
        self.add_item(discord.ui.Button(
            label="📿 Accessories", 
            style=discord.ButtonStyle.primary, 
            custom_id="inventory_accessories", 
            row=0
        ))
        self.add_item(discord.ui.Button(
            label="Pets",
            emoji=paw_emoji,
            style=discord.ButtonStyle.primary,
            custom_id="inventory_pets",
            row=0
        ))
        self.add_item(discord.ui.Button(
            label="Consumables",
            emoji=energy_emoji,
            style=discord.ButtonStyle.primary,
            custom_id="inventory_materials",
            row=0
        ))    
        self.add_item(discord.ui.Button(
            label="🔄", 
            style=discord.ButtonStyle.secondary, 
            custom_id="inventory_back", 
            row=1
        ))

    def create_main_embed(self):
        """Create the main inventory overview (only items and gems)"""
        print("🔄 create_main_embed called")
        user = self.cog.bot.get_user(int(self.user_id))
        energy_emoji = CUSTOM_EMOJIS.get('energy_potion', '🧪')
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
        embed.add_field(name=f"{energy_emoji} Consumables", value=str(len(self.inventory.get('materials', []))), inline=True)

        print(f"   embed title: {embed.title}")
        return embed

    async def refresh_inventory(self, interaction):
        """Refresh inventory data after equip/unequip"""
        user_id = str(self.user_id)
        async with self.cog.bot.db_pool.acquire() as conn:
            weapons = await conn.fetch("""
                SELECT uw.id, COALESCE(si.name, uw.generated_name) as name,
                       uw.attack, uw.equipped, uw.description,
                       uw.bleeding_chance, uw.crit_chance, uw.crit_damage,
                       COALESCE(si.image_url, uw.image_url) as image_url,
                       r.color as rarity_color,
                       uw.upgrade_level
                FROM user_weapons uw
                LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                LEFT JOIN weapon_variants v ON uw.variant_id = v.variant_id
                LEFT JOIN rarities r ON v.rarity_id = r.rarity_id
                WHERE uw.user_id = $1
                ORDER BY uw.equipped DESC, uw.purchased_at DESC
            """, user_id)

            armor = await conn.fetch("""
                SELECT ua.id, at.name, ua.defense, ua.equipped, at.slot,
                       ua.hp_bonus, ua.reflect_damage, at.set_name,
                       at.image_url, at.description, r.color as rarity_color,
                       ua.upgrade_level
                FROM user_armor ua
                JOIN armor_types at ON ua.armor_id = at.armor_id
                LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                WHERE ua.user_id = $1
                ORDER BY ua.equipped DESC, ua.purchased_at DESC
            """, user_id)

            accessories = await conn.fetch("""
                SELECT ua.id, at.name, ua.bonus_value, at.bonus_stat,
                       ua.equipped, ua.slot, at.set_name,
                       at.image_url, at.description, r.color as rarity_color,
                       ua.upgrade_level
                FROM user_accessories ua
                JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                WHERE ua.user_id = $1
                ORDER BY ua.equipped DESC, ua.purchased_at DESC
            """, user_id)

            materials = await conn.fetch("""
                SELECT um.material_id, si.name, um.quantity, si.description
                FROM user_materials um
                JOIN shop_items si ON um.material_id = si.item_id
                WHERE um.user_id = $1 AND um.quantity > 0
                ORDER BY si.name
            """, user_id)

        balance = await currency_system.get_balance(user_id)

        self.inventory = {
            'weapons': [dict(w) for w in weapons],
            'armor': [dict(a) for a in armor],
            'accessories': [dict(a) for a in accessories],
            'materials': [dict(m) for m in materials],
            'gems': balance['gems']
        }

        await interaction.edit_original_response(embed=self.create_main_embed(), view=self)

    

    async def show_weapons(self, interaction: discord.Interaction):
        try:
            if interaction.user.id != int(self.user_id):
                await interaction.followup.send("Not your inventory!", ephemeral=True)
                return
            if not self.inventory['weapons']:
                await interaction.followup.send("You have no weapons!", ephemeral=True)
                return
            embed = discord.Embed(title="🗡️ **Weapons**", color=discord.Color.red())
            view = CategoryView(self.user_id, self.inventory['weapons'], 'weapon', self)
            await interaction.edit_original_response(embed=embed, view=view) 
        except Exception as e:
            print(f"Error in show_weapons: {e}")
            traceback.print_exc()
            try:
                await interaction.followup.send("An error occurred.", ephemeral=True)
            except:
                pass

    async def show_armor(self, interaction: discord.Interaction):
        try:
            if interaction.user.id != int(self.user_id):
                await interaction.followup.send("Not your inventory!", ephemeral=True)
                return
            if not self.inventory['armor']:
                await interaction.followup.send("You have no armor!", ephemeral=True)
                return
            embed = discord.Embed(title="🛡️ **Armor**", color=discord.Color.blue())
            view = CategoryView(self.user_id, self.inventory['armor'], 'armor', self)
            await interaction.edit_original_response(embed=embed, view=view) 
        except Exception as e:
            print(f"Error in show_armor: {e}")
            traceback.print_exc()
            try:
                await interaction.followup.send("An error occurred.", ephemeral=True)
            except:
                pass

    async def show_accessories(self, interaction: discord.Interaction):
        try:
            if interaction.user.id != int(self.user_id):
                await interaction.followup.send("Not your inventory!", ephemeral=True)
                return
            if not self.inventory['accessories']:
                await interaction.followup.send("You have no accessories!", ephemeral=True)
                return
            embed = discord.Embed(title="📿 **Accessories**", color=discord.Color.green())
            view = CategoryView(self.user_id, self.inventory['accessories'], 'accessory', self)            
            await interaction.edit_original_response(embed=embed, view=view) 
        except Exception as e:
            print(f"Error in show_accessories: {e}")
            traceback.print_exc()
            try:
                await interaction.followup.send("An error occurred.", ephemeral=True)
            except:
                pass

    async def show_pets(self, interaction: discord.Interaction):
        try:
            if interaction.user.id != int(self.user_id):
                await interaction.followup.send("Not your inventory!", ephemeral=True)
                return
            async with self.cog.bot.db_pool.acquire() as conn:
                pets = await conn.fetch("""
                    SELECT up.id, pt.name, up.equipped,
                           pt.atk_percent, pt.def_percent, pt.hp_percent,
                           pt.dodge_percent, pt.bleed_flat, pt.burn_flat, pt.energy_bonus
                    FROM user_pets up
                    JOIN pet_types pt ON up.pet_id = pt.pet_id
                    WHERE up.user_id = $1
                    ORDER BY up.equipped DESC, up.purchased_at DESC
                """, self.user_id)
            if not pets:
                await interaction.followup.send("You have no pets!", ephemeral=True)
                return

            # Get custom paw emoji from CUSTOM_EMOJIS
            paw_emoji = CUSTOM_EMOJIS.get('paw', '🐾')  # fallback to '🐾' if missing

            # Convert to list of dicts with required keys for CategoryView
            pet_list = [dict(pet) for pet in pets]
            # Create CategoryView with item_type='pet'
            embed = discord.Embed(title=f"{paw_emoji} **Pets**", color=discord.Color.purple())
            view = CategoryView(self.user_id, pet_list, 'pet', self)
            await interaction.edit_original_response(embed=embed, view=view)
        except Exception as e:
            print(f"Error in show_pets: {e}")
            traceback.print_exc()
            await interaction.followup.send("An error occurred.", ephemeral=True)


    async def show_materials(self, interaction: discord.Interaction):
        try:
            if interaction.user.id != int(self.user_id):
                await interaction.followup.send("Not your inventory!", ephemeral=True)
                return

            # Fetch materials
            materials = self.inventory.get('materials', [])
            # Fetch titles from database
            async with self.cog.bot.db_pool.acquire() as conn:
                titles = await conn.fetch("""
                    SELECT t.title_id as id, t.name, t.emoji,
                           ut.equipped, t.hp_percent, t.def_percent,
                           t.atk_percent, t.crit_chance, t.dodge_percent,
                           t.dmg_reduction_percent, t.bleed_flat, t.burn_flat,
                           t.crit_dmg_res_percent, t.mining_bonus_percent,
                           t.boss_damage_percent, t.extra_boss_attempts,
                           t.extra_plunder_attempts
                    FROM titles t
                    JOIN user_titles ut ON t.title_id = ut.title_id
                    WHERE ut.user_id = $1
                    ORDER BY ut.equipped DESC, t.name
                """, self.user_id)

            # Build combined list with category markers
            combined = []
            for m in materials:
                m_dict = dict(m)
                m_dict['category'] = 'material'
                combined.append(m_dict)
            for t in titles:
                t_dict = dict(t)
                t_dict['category'] = 'title'
                combined.append(t_dict)

            if not combined:
                await interaction.followup.send("You have no consumables or titles!", ephemeral=True)
                return

            # Use your custom energy emoji in the title
            energy_emoji = CUSTOM_EMOJIS.get('energy_potion', '🧪')
            embed = discord.Embed(title=f"{energy_emoji} **Consumables & Titles**", color=discord.Color.light_grey())
            view = CategoryView(self.user_id, combined, 'mixed', self)
            await interaction.edit_original_response(embed=embed, view=view)
        except Exception as e:
            print(f"Error in show_materials: {e}")
            traceback.print_exc()
            try:
                await interaction.followup.send("An error occurred.", ephemeral=True)
            except:
                pass

    async def back_to_main(self, interaction: discord.Interaction):
        try:
            if interaction.user.id != int(self.user_id):
                await interaction.response.send_message("Not your inventory!", ephemeral=True)
                return
            await interaction.response.edit_message(embed=self.create_main_embed(), view=self)
        except Exception as e:
            print(f"Error in back_to_main: {e}")
            traceback.print_exc()
            await interaction.response.send_message("An error occurred.", ephemeral=True)




# ========== TRADING SYSTEM ==========

# Dictionary to track users who are in the middle of adding gems
pending_gem_inputs = {}  # key: user_id (str), value: {"trade_id": int, "message_id": int, "channel_id": int, "expires": float}
pending_material_inputs = {}  # key: user_id, value: {"trade_id": int, "material_id": int, "message_id": int, "channel_id": int, "expires": float}

async def update_trade_embed(message: discord.Message, trade_id: int):
    """Fetch trade data and edit the given message with updated embed."""
    async with bot.db_pool.acquire() as conn:
        trade = await conn.fetchrow("SELECT * FROM active_trades WHERE trade_id = $1", trade_id)
        if not trade:
            await message.edit(content="Trade not found.", view=None)
            return
        items = await conn.fetch("SELECT * FROM trade_items WHERE trade_id = $1", trade_id)

    initiator = bot.get_user(int(trade['initiator_id'])) or await bot.fetch_user(int(trade['initiator_id']))
    receiver = bot.get_user(int(trade['receiver_id'])) or await bot.fetch_user(int(trade['receiver_id']))

    initiator_offers = []
    receiver_offers = []

    for it in items:
            user_id = it['user_id']
            if it['gems'] > 0:
                offer = f"💎 {it['gems']} gems"
            else:
                qty = it.get('quantity', 1)
                offer = await get_trade_item_display(it['item_type'], it['item_id'], qty)
            if user_id == trade['initiator_id']:
                initiator_offers.append(offer)
            else:
                receiver_offers.append(offer)

    embed = discord.Embed(title="🔄 Trade Session", color=discord.Color.blue())
    embed.add_field(
        name=f"📦 {initiator.display_name} offers:",
        value="\n".join(initiator_offers) if initiator_offers else "Nothing yet",
        inline=True
    )
    embed.add_field(
        name=f"📦 {receiver.display_name} offers:",
        value="\n".join(receiver_offers) if receiver_offers else "Nothing yet",
        inline=True
    )
    status = f"Initiator locked: {'✅' if trade['initiator_lock'] else '❌'}\nReceiver locked: {'✅' if trade['receiver_lock'] else '❌'}"
    embed.add_field(name="Status", value=status, inline=False)

    await message.edit(embed=embed)


async def get_item_name(item_type: str, item_id: int) -> str:
    """Return a display name for an item given its type and ID."""
    async with bot.db_pool.acquire() as conn:
        if item_type == 'weapon':
            row = await conn.fetchrow("""
                SELECT COALESCE(si.name, uw.generated_name) as name
                FROM user_weapons uw
                LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                WHERE uw.id = $1
            """, item_id)
            return row['name'] if row else "Unknown Weapon"
        elif item_type == 'armor':
            row = await conn.fetchrow("""
                SELECT at.name
                FROM user_armor ua
                JOIN armor_types at ON ua.armor_id = at.armor_id
                WHERE ua.id = $1
            """, item_id)
            return row['name'] if row else "Unknown Armor"
        elif item_type == 'accessory':
            row = await conn.fetchrow("""
                SELECT at.name
                FROM user_accessories ua
                JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                WHERE ua.id = $1
            """, item_id)
            return row['name'] if row else "Unknown Accessory"
        elif item_type == 'material':
            row = await conn.fetchrow("SELECT name FROM shop_items WHERE item_id = $1", item_id)
            return row['name'] if row else "Unknown Material"
    return "Unknown"

async def get_trade_item_display(item_type: str, item_id: int, quantity: int = 1) -> str:
    """Return a formatted string for a trade item, including emoji and stats. Quantity is used for materials."""
    async with bot.db_pool.acquire() as conn:
        if item_type == 'weapon':
            row = await conn.fetchrow("""
                SELECT uw.attack, COALESCE(si.name, uw.generated_name) as name
                FROM user_weapons uw
                LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                WHERE uw.id = $1
            """, item_id)
            if row:
                emoji = get_item_emoji(row['name'], 'weapon')
                return f"{emoji} **{row['name']}** (ATK {row['attack']})"
        elif item_type == 'armor':
            row = await conn.fetchrow("""
                SELECT ua.defense, ua.hp_bonus, at.name
                FROM user_armor ua
                JOIN armor_types at ON ua.armor_id = at.armor_id
                WHERE ua.id = $1
            """, item_id)
            if row:
                emoji = get_item_emoji(row['name'], 'armor')
                hp = row['hp_bonus'] or 0
                return f"{emoji} **{row['name']}** (DEF {row['defense']} | HP +{hp})"
        elif item_type == 'accessory':
            row = await conn.fetchrow("""
                SELECT ua.bonus_value, at.name, at.bonus_stat
                FROM user_accessories ua
                JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                WHERE ua.id = $1
            """, item_id)
            if row:
                emoji = get_item_emoji(row['name'], 'accessory')
                stat_display = row['bonus_stat'].upper()
                return f"{emoji} **{row['name']}** (+{row['bonus_value']} {stat_display})"
        elif item_type == 'material':
            row = await conn.fetchrow("""
                SELECT name FROM shop_items WHERE item_id = $1
            """, item_id)
            if row:
                name_lower = row['name'].lower()
                if 'hp potion' in name_lower:
                    emoji = CUSTOM_EMOJIS.get('hp_potion', '🧪')
                elif 'energy potion' in name_lower:
                    emoji = CUSTOM_EMOJIS.get('energy_potion', '⚡')
                elif 'sword' in name_lower:
                    emoji = CUSTOM_EMOJIS.get('sword_enhancement_stone', '💎')
                elif 'armor' in name_lower:
                    emoji = CUSTOM_EMOJIS.get('armors_enhancement_stone', '💎')
                elif 'accessories' in name_lower:
                    emoji = CUSTOM_EMOJIS.get('acc_enhancement_stone', '💎')
                else:
                    emoji = '📦'
                return f"{emoji} **{row['name']}** x{quantity}"
        elif item_type == 'pet':
            row = await conn.fetchrow("""
                SELECT pt.name
                FROM user_pets up
                JOIN pet_types pt ON up.pet_id = pt.pet_id
                WHERE up.id = $1
            """, item_id)
            if row:
                emoji = get_pet_emoji(row['name'])
                return f"{emoji} **{row['name']}**"
    return "Unknown item"


class TradeView(discord.ui.View):
    def __init__(self, trade_id: int, initiator_id: str, receiver_id: str, message_id: int):
        super().__init__(timeout=300)
        self.trade_id = trade_id
        self.initiator_id = initiator_id
        self.receiver_id = receiver_id
        self.message_id = message_id
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return str(interaction.user.id) in (self.initiator_id, self.receiver_id)

    @discord.ui.button(label="➕", style=discord.ButtonStyle.primary, row=0)
    async def add_item_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        view = CategorySelectView(self, user_id)
        await interaction.response.send_message("Choose an item category:", view=view, ephemeral=True)

    @discord.ui.button(label="💎", style=discord.ButtonStyle.primary, row=0)
    async def add_gems_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        pending_gem_inputs[user_id] = {
            "trade_id": self.trade_id,
            "message_id": self.message_id,
            "channel_id": interaction.channel.id,
            "expires": time.time() + 60
        }
        await interaction.response.send_message(
            "💬 Please type the amount of gems you want to add in chat (within 60 seconds).",
            ephemeral=True
        )

    @discord.ui.button(label="🔒", style=discord.ButtonStyle.success, row=1)
    async def lock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        async with bot.db_pool.acquire() as conn:
            if user_id == self.initiator_id:
                await conn.execute("UPDATE active_trades SET initiator_lock = TRUE WHERE trade_id = $1", self.trade_id)
            else:
                await conn.execute("UPDATE active_trades SET receiver_lock = TRUE WHERE trade_id = $1", self.trade_id)
            row = await conn.fetchrow("SELECT initiator_lock, receiver_lock FROM active_trades WHERE trade_id = $1", self.trade_id)
            if row and row['initiator_lock'] and row['receiver_lock']:
                await self.execute_trade(interaction)
                return
        await update_trade_embed(interaction.message, self.trade_id)
        await interaction.response.defer()

    @discord.ui.button(label="❌", style=discord.ButtonStyle.danger, row=1)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with bot.db_pool.acquire() as conn:
            await conn.execute("UPDATE active_trades SET status = 'cancelled' WHERE trade_id = $1", self.trade_id)
            await conn.execute("DELETE FROM trade_items WHERE trade_id = $1", self.trade_id)
        await interaction.message.edit(content="🚫 Trade cancelled.", embed=None, view=None)
        self.stop()

    async def execute_trade(self, interaction: discord.Interaction):
        async with bot.db_pool.acquire() as conn:
            async with conn.transaction():
                items = await conn.fetch("SELECT * FROM trade_items WHERE trade_id = $1", self.trade_id)
                for it in items:
                    if it['gems'] > 0:
                        sender = it['user_id']
                        receiver = self.receiver_id if sender == self.initiator_id else self.initiator_id
                        await currency_system.deduct_gems(sender, it['gems'], f"Trade with {receiver}")
                        await currency_system.add_gems(receiver, it['gems'], f"Trade with {sender}")
                    else:
                        table_map = {
                            'weapon': 'user_weapons',
                            'armor': 'user_armor',
                            'accessory': 'user_accessories',
                            'material': 'user_materials'
                        }
                        if it['item_type'] == 'material':
                            qty_in_trade = it['quantity']
                            current_qty = await conn.fetchval("SELECT quantity FROM user_materials WHERE user_id = $1 AND material_id = $2", it['user_id'], it['item_id'])
                            if current_qty and current_qty >= qty_in_trade:
                                await conn.execute("UPDATE user_materials SET quantity = quantity - $1 WHERE user_id = $2 AND material_id = $3", qty_in_trade, it['user_id'], it['item_id'])
                                new_owner = self.receiver_id if it['user_id'] == self.initiator_id else self.initiator_id
                                await conn.execute("""
                                    INSERT INTO user_materials (user_id, material_id, quantity)
                                    VALUES ($1, $2, $3)
                                    ON CONFLICT (user_id, material_id) DO UPDATE
                                    SET quantity = user_materials.quantity + $3
                                """, new_owner, it['item_id'], qty_in_trade)
                        else:
                            new_owner = self.receiver_id if it['user_id'] == self.initiator_id else self.initiator_id
                            await conn.execute(f"UPDATE {table_map[it['item_type']]} SET user_id = $1 WHERE id = $2", new_owner, it['item_id'])
                await conn.execute("UPDATE active_trades SET status = 'completed' WHERE trade_id = $1", self.trade_id)
                await conn.execute("DELETE FROM trade_items WHERE trade_id = $1", self.trade_id)

        await interaction.message.edit(content="✅ Trade completed successfully!", embed=None, view=None)
        self.stop()

class CategorySelectView(discord.ui.View):
    def __init__(self, trade_view: TradeView, user_id: str):
        super().__init__(timeout=60)
        self.trade_view = trade_view
        self.user_id = user_id

    @discord.ui.button(label="⚔️ Weapons", style=discord.ButtonStyle.primary, row=0)
    async def weapons_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_items(interaction, 'weapon')

    @discord.ui.button(label="🛡️ Armor", style=discord.ButtonStyle.primary, row=0)
    async def armor_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_items(interaction, 'armor')

    @discord.ui.button(label="📿 Accessories", style=discord.ButtonStyle.primary, row=1)
    async def accessories_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_items(interaction, 'accessory')

    # Consumables button with energy potion emoji
    @discord.ui.button(label="Consumables", 
                       emoji=discord.PartialEmoji(name="energy_potion", id=1481365820566409236), 
                       style=discord.ButtonStyle.primary, row=1)
    async def consumables_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_items(interaction, 'material')

    # Pets button with paw emoji
    @discord.ui.button(label="Pets", 
                       emoji=discord.PartialEmoji(name="paw", id=1482627374066565170), 
                       style=discord.ButtonStyle.primary, row=2)
    async def pets_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_items(interaction, 'pet')

    async def show_items(self, interaction: discord.Interaction, category: str):
        # Fetch items of the selected category with their stats
        async with bot.db_pool.acquire() as conn:
            if category == 'weapon':
                items = await conn.fetch("""
                    SELECT uw.id, COALESCE(si.name, uw.generated_name) as name,
                           uw.attack
                    FROM user_weapons uw
                    LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                    WHERE uw.user_id = $1
                """, self.user_id)
            elif category == 'armor':
                items = await conn.fetch("""
                    SELECT ua.id, at.name,
                           ua.defense, ua.hp_bonus, ua.reflect_damage
                    FROM user_armor ua
                    JOIN armor_types at ON ua.armor_id = at.armor_id
                    WHERE ua.user_id = $1
                """, self.user_id)
            elif category == 'accessory':
                items = await conn.fetch("""
                    SELECT ua.id, at.name,
                           ua.bonus_value, at.bonus_stat
                    FROM user_accessories ua
                    JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                    WHERE ua.user_id = $1
                """, self.user_id)
            elif category == 'material':
                items = await conn.fetch("""
                    SELECT um.material_id as id, si.name, um.quantity
                    FROM user_materials um
                    JOIN shop_items si ON um.material_id = si.item_id
                    WHERE um.user_id = $1 AND um.quantity > 0
                """, self.user_id)
            elif category == 'pet':
                items = await conn.fetch("""
                    SELECT up.id, pt.name, up.equipped,
                           pt.atk_percent, pt.def_percent, pt.hp_percent,
                           pt.dodge_percent, pt.bleed_flat, pt.burn_flat, pt.energy_bonus
                    FROM user_pets up
                    JOIN pet_types pt ON up.pet_id = pt.pet_id
                    WHERE up.user_id = $1
                    ORDER BY up.equipped DESC, up.purchased_at DESC
                """, self.user_id)
            else:
                return await interaction.response.send_message("Invalid category.", ephemeral=True)

        if not items:
            return await interaction.response.send_message(f"You have no {category}s to trade.", ephemeral=True)

        # Create paginated view with all items
        view = ItemPaginationView(self.trade_view, self.user_id, category, items)
        await interaction.response.send_message(f"Select a {category}:", view=view, ephemeral=True)

        async def select_callback(select_interaction: discord.Interaction):
            value = select.values[0]
            cat, item_id = value.split(':')
            async with bot.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO trade_items (trade_id, user_id, item_type, item_id)
                    VALUES ($1, $2, $3, $4)
                """, self.trade_view.trade_id, self.user_id, cat, int(item_id))
            await select_interaction.response.send_message(f"✅ {category.capitalize()} added to trade.", ephemeral=True)
            # Update the main trade message
            if self.trade_view.message:
                await update_trade_embed(self.trade_view.message, self.trade_view.trade_id)

        select.callback = select_callback
        view = discord.ui.View()
        view.add_item(select)

        # If there are more than 25 items, add a note
        if len(items) > 25:
            await interaction.response.send_message(
                f"Showing first 25 {category}s (you have {len(items)} total).",
                view=view, ephemeral=True
            )
        else:
            await interaction.response.send_message(f"Select a {category}:", view=view, ephemeral=True)

    def get_category_emoji(self, category: str) -> str:
        return {
            'weapon': '⚔️',
            'armor': '🛡️',
            'accessory': '📿',
            'material': '📦'
        }.get(category, '📦')


class ItemPaginationView(discord.ui.View):
    def __init__(self, trade_view: TradeView, user_id: str, category: str, items: list):
        super().__init__(timeout=60)
        self.trade_view = trade_view
        self.user_id = user_id
        self.category = category
        self.items = items
        self.page = 0
        self.max_page = (len(items) - 1) // 25
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        start = self.page * 25
        end = min(start + 25, len(self.items))
        page_items = self.items[start:end]

        options = []
        for item in page_items:
            if self.category == 'pet':
                emoji = get_pet_emoji(item['name'])
            else:
                emoji = get_item_emoji(item['name'], self.category)
            # Build label with stats
            if self.category == 'weapon':
                label = f"{item['name']} (ATK {item['attack']})"
            elif self.category == 'armor':
                parts = [f"DEF {item['defense']}"]
                if item['hp_bonus']:
                    parts.append(f"HP+{item['hp_bonus']}")
                if item['reflect_damage']:
                    parts.append(f"Reflect {item['reflect_damage']}%")
                label = f"{item['name']} ({', '.join(parts)})"
            elif self.category == 'accessory':
                stat_name = item['bonus_stat'].upper()
                label = f"{item['name']} (+{item['bonus_value']} {stat_name})"
            elif self.category == 'material':
                label = f"{item['name']} x{item['quantity']}"
            elif self.category == 'pet':
                # Just show the name – stats are shown when selecting
                label = f"{item['name']}"
            else:
                label = item['name'][:100]

            # Truncate if too long
            if len(label) > 100:
                label = label[:97] + "..."

            options.append(discord.SelectOption(
                label=label,
                value=f"{self.category}:{item['id']}",
                emoji=emoji
            ))

        select = discord.ui.Select(
            placeholder=f"Choose a {self.category} (page {self.page+1}/{self.max_page+1})",
            options=options
        )
        select.callback = self.select_callback
        self.add_item(select)

        if self.page > 0:
            prev = discord.ui.Button(label="◀ Previous", style=discord.ButtonStyle.secondary)
            prev.callback = self.prev_page
            self.add_item(prev)
        if self.page < self.max_page:
            nxt = discord.ui.Button(label="Next ▶", style=discord.ButtonStyle.secondary)
            nxt.callback = self.next_page
            self.add_item(nxt)

    async def select_callback(self, interaction: discord.Interaction):
        select = self.children[0]
        value = select.values[0]
        cat, item_id = value.split(':')
        item_id = int(item_id)

        if cat == 'material':
            pending_material_inputs[str(interaction.user.id)] = {
                "trade_id": self.trade_view.trade_id,
                "material_id": item_id,
                "message_id": self.trade_view.message_id,
                "channel_id": interaction.channel.id,
                "expires": time.time() + 60
            }
            await interaction.response.send_message(
                "💬 Please type the amount you want to add (within 60 seconds).",
                ephemeral=True
            )
            return

        async with bot.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO trade_items (trade_id, user_id, item_type, item_id, gems, quantity)
                VALUES ($1, $2, $3, $4, 0, 1)
            """, self.trade_view.trade_id, str(interaction.user.id), cat, item_id)

        await interaction.response.send_message(f"✅ {cat.capitalize()} added to trade.", ephemeral=True)
        if self.trade_view.message:
            await update_trade_embed(self.trade_view.message, self.trade_view.trade_id)


@bot.command(name='trade')
async def trade_start(ctx, member: discord.Member):
    if member == ctx.author:
        return await ctx.send("You can't trade with yourself.")

    async with bot.db_pool.acquire() as conn:
        for uid in (str(ctx.author.id), str(member.id)):
            existing = await conn.fetchval("SELECT 1 FROM active_trades WHERE (initiator_id = $1 OR receiver_id = $1) AND status = 'pending'", uid)
            if existing:
                user = ctx.author if uid == str(ctx.author.id) else member
                return await ctx.send(f"{user.mention} is already in a pending trade.")

        trade_id = await conn.fetchval("""
            INSERT INTO active_trades (initiator_id, receiver_id, channel_id)
            VALUES ($1, $2, $3)
            RETURNING trade_id
        """, str(ctx.author.id), str(member.id), ctx.channel.id)

    embed = discord.Embed(
        title="🔄 Trade Session",
        description=f"{ctx.author.mention} wants to trade with {member.mention}\n\nUse the buttons below to add items and lock in.",
        color=discord.Color.blue()
    )
    view = TradeView(trade_id, str(ctx.author.id), str(member.id), None)  # message_id unknown yet
    msg = await ctx.send(embed=embed, view=view)
    view.message = msg
    # Update the view with the actual message_id and store it in DB
    view.message_id = msg.id
    async with bot.db_pool.acquire() as conn:
        await conn.execute("UPDATE active_trades SET message_id = $1 WHERE trade_id = $2", msg.id, trade_id)

#    MY PROFILE CLASS

class ProfileView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = user_id
        
        # Create button manually
        button = discord.ui.Button(label="🔄", style=discord.ButtonStyle.secondary)
        button.callback = self.refresh_button
        self.add_item(button)

    async def refresh_button(self, interaction: discord.Interaction):
        """Callback for the refresh button – receives only the interaction."""
        print(f"DEBUG: interaction type = {type(interaction)}")
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("This is not your profile.", ephemeral=True)
            return
        await interaction.response.defer()
        embed = await build_profile_embed(self.user_id, interaction.user)
        await interaction.edit_original_response(embed=embed, view=self)

async def build_profile_embed(user_id: str, member: discord.Member):
    """Build the profile embed (used by both myprofile and refresh button)."""
    BASE_HP = 1000
    BASE_DEF = 500

    async with bot.db_pool.acquire() as conn:
        player = await conn.fetchrow("SELECT hp, max_hp, energy, max_energy FROM player_stats WHERE user_id = $1", user_id)
        if not player:
            await conn.execute("INSERT INTO player_stats (user_id, hp, max_hp, energy, max_energy) VALUES ($1, $2, $2, 3, 3) ON CONFLICT DO NOTHING", user_id, BASE_HP)
            player = {'hp': BASE_HP, 'max_hp': BASE_HP, 'energy': 3, 'max_energy': 3}

        weapon = await conn.fetchrow("""
            SELECT uw.id, COALESCE(si.name, uw.generated_name) as name,
                   uw.attack, uw.bleeding_chance, uw.crit_chance, uw.crit_damage,
                   COALESCE(si.image_url, uw.image_url) as image_url
            FROM user_weapons uw
            LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
            WHERE uw.user_id = $1 AND uw.equipped = TRUE
            LIMIT 1
        """, user_id)

        armor_pieces = await conn.fetch("""
            SELECT at.name, ua.defense, at.slot, ua.reflect_damage,
                   ua.hp_bonus, at.set_name, ua.equipped, at.image_url
            FROM user_armor ua
            JOIN armor_types at ON ua.armor_id = at.armor_id
            WHERE ua.user_id = $1 AND ua.equipped = TRUE
        """, user_id)
        armor_dict = {a['slot']: a for a in armor_pieces}

        accessories = await conn.fetch("""
            SELECT ua.id, at.name, ua.bonus_value, at.bonus_stat,
                   ua.slot, at.set_name, at.image_url
            FROM user_accessories ua
            JOIN accessory_types at ON ua.accessory_id = at.accessory_id
            WHERE ua.user_id = $1 AND ua.equipped = TRUE
        """, user_id)
        acc_dict = {a['slot']: a for a in accessories}

        # Fetch equipped pet (if any)
        pet = await conn.fetchrow("""
            SELECT pt.name
            FROM user_pets up
            JOIN pet_types pt ON up.pet_id = pt.pet_id
            WHERE up.user_id = $1 AND up.equipped = TRUE
        """, user_id)

    # ===== TITLE BONUSES (fetch early for emoji) =====
    title_bonuses = await get_equipped_title_bonuses(user_id)
    title_emoji = title_bonuses['emoji'] if title_bonuses else None
    boss_dmg_percent = title_bonuses['boss_damage_percent'] if title_bonuses else 0

    # --- Flat stats from gear ---
    total_atk = 0
    total_def = BASE_DEF
    total_crit_chance = 0.0
    total_crit_damage = 0.0
    total_bleed_chance = 0.0
    total_bleed_damage = 0.0
    total_reflect = 0
    hp_from_gear = BASE_HP

    if weapon:
        total_atk += weapon['attack']
        total_bleed_chance += weapon['bleeding_chance'] or 0
        total_crit_chance += weapon['crit_chance'] or 0
        total_crit_damage += weapon['crit_damage'] or 0

    for armor in armor_pieces:
        total_def += armor['defense']
        total_reflect += armor['reflect_damage'] or 0
        hp_from_gear += armor['hp_bonus'] or 0

    for acc in accessories:
        stat = acc['bonus_stat']
        val = acc['bonus_value']
        if stat == 'atk':
            total_atk += val
        elif stat == 'def':
            total_def += val
        elif stat == 'hp':
            hp_from_gear += val
        elif stat == 'crit':
            total_crit_chance += val
        elif stat == 'bleed':
            total_bleed_damage += val

    # --- Multipliers from sets ---
    atk_mult = 1.0
    def_mult = 1.0
    hp_mult = 1.0
    reflect_add = 0
    crit_chance_add = 0
    crit_damage_add = 0

    # Armor set
    armor_sets = {}
    for armor in armor_pieces:
        if armor['set_name']:
            armor_sets[armor['set_name']] = armor_sets.get(armor['set_name'], 0) + 1
    for set_name, count in armor_sets.items():
        if count >= 4:
            sname = set_name.lower()
            if sname in ('bilari', 'cryo', 'bane'):
                crit_chance_add += 10
                crit_damage_add += 25
                def_mult *= 1.15
                reflect_add += 20
                hp_mult *= 1.20

    # Accessory set
    accessory_sets = {}
    for acc in accessories:
        if acc['set_name']:
            accessory_sets[acc['set_name']] = accessory_sets.get(acc['set_name'], 0) + 1
    for set_name, count in accessory_sets.items():
        if count >= 5:
            sname = set_name.lower()
            if sname == 'champion':
                atk_mult *= 1.20
                def_mult *= 1.15
                hp_mult *= 1.15
            elif sname == 'defender':
                def_mult *= 1.20
                reflect_add += 10
                hp_mult *= 1.15
            elif sname == 'angel':
                crit_chance_add += 15
                total_bleed_damage += 20
                hp_mult *= 1.15

    # Apply set multipliers
    total_atk = int(total_atk * atk_mult)
    total_def = int(total_def * def_mult)
    max_hp_after_sets = int(hp_from_gear * hp_mult)
    total_reflect += reflect_add
    total_crit_chance += crit_chance_add
    total_crit_damage += crit_damage_add

    # --- Pet bonuses ---
    pet_energy_bonus = 0
    pet_dodge = 0
    pet_hp_mult = 1.0
    pet_atk_mult = 1.0
    pet_def_mult = 1.0
    if pet:
        async with bot.db_pool.acquire() as conn:
            pet_stats = await conn.fetchrow("""
                SELECT atk_percent, def_percent, hp_percent,
                       dodge_percent, bleed_flat, burn_flat, energy_bonus
                FROM pet_types WHERE name = $1
            """, pet['name'])
        if pet_stats:
            pet_atk_mult = 1 + pet_stats['atk_percent'] / 100
            pet_def_mult = 1 + pet_stats['def_percent'] / 100
            pet_hp_mult = 1 + pet_stats['hp_percent'] / 100
            pet_energy_bonus = pet_stats['energy_bonus']
            pet_dodge = pet_stats['dodge_percent']

    # Apply pet multipliers
    total_atk = int(total_atk * pet_atk_mult)
    total_def = int(total_def * pet_def_mult)
    max_hp_after_pet = int(max_hp_after_sets * pet_hp_mult)

    # ========== TITLE BONUSES ==========
    title_hp_mult = 1.0
    if title_bonuses:
        # ATK% and DEF% multipliers
        total_atk = int(total_atk * (1 + title_bonuses['atk_percent'] / 100))
        total_def = int(total_def * (1 + title_bonuses['def_percent'] / 100))
        # HP% multiplier
        title_hp_mult = 1 + title_bonuses['hp_percent'] / 100
        # Additive stats
        total_crit_chance += title_bonuses['crit_chance']
        pet_dodge += title_bonuses['dodge_percent']  # add title dodge to display
        # Store other bonuses for display
        boss_dmg_percent = title_bonuses['boss_damage_percent']

    # Final max HP after title multiplier
    max_hp = int(max_hp_after_pet * title_hp_mult)

    current_hp = player['hp']
    if current_hp > max_hp:
        current_hp = max_hp

    max_energy = player['max_energy'] + pet_energy_bonus
    current_energy = player['energy']
    if current_energy > max_energy:
        current_energy = max_energy

    # ===== BUILD EMBED =====
    title_suffix = f" {title_emoji}" if title_emoji else ""
    embed = discord.Embed(
        title=f"**{member.display_name}'s Profile**{title_suffix}",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    hp_percent = (current_hp / max_hp) * 10
    hp_bar = "🟥" * int(hp_percent) + "⬛" * (10 - int(hp_percent))

    energy_percent = (current_energy / max_energy) * 10
    energy_bar = "🟨" * int(energy_percent) + "⬛" * (10 - int(energy_percent))

    def_bar = "🟦" * 10

    vitals_text = (
        f"{hp_bar} `{current_hp}/{max_hp} HP`\n"
        f"{def_bar} `{total_def} DEF`\n"
        f"{energy_bar} `{current_energy}/{max_energy} Energy`"
    )
    embed.description = vitals_text

    stats_lines = [
        f"**ATK:** {total_atk}",
        f"**Crit Chance:** {total_crit_chance:.1f}%",
        f"**Crit Damage:** {total_crit_damage:.1f}%",
        f"**Bleed Chance:** {total_bleed_chance:.1f}%",
        f"**Bleed Damage:** {total_bleed_damage:.1f}%",
        f"**Reflect Damage:** {total_reflect}%",
    ]
    if pet_dodge > 0:
        stats_lines.append(f"**Dodge:** {pet_dodge}%")

    # Title-specific stats
    if title_bonuses:       
        if title_bonuses['dmg_reduction_percent']:
            stats_lines.append(f"**DMG RED.:** +{title_bonuses['dmg_reduction_percent']}%")
        if title_bonuses['crit_dmg_res_percent']:
            stats_lines.append(f"**Crit RES:** +{title_bonuses['crit_dmg_res_percent']}%")    
        if boss_dmg_percent:
            stats_lines.append(f"**Boss DMG:** +{boss_dmg_percent}%")

    embed.add_field(name="**STATS**", value="\n".join(stats_lines), inline=False)

    def slot_emoji(slot, item=None):
        if item:
            if slot == 'weapon':
                return get_item_emoji(item['name'], 'weapon')
            elif slot in ('helm', 'suit', 'gauntlets', 'boots'):
                return get_item_emoji(item['name'], 'armor')
            else:
                return get_item_emoji(item['name'], 'accessory')
        return "*none*"

    pet_emoji = get_pet_emoji(pet['name']) if pet else "🐾"

    row1 = (
        f"{slot_emoji('helm', armor_dict.get('helm'))} "
        f"{slot_emoji('suit', armor_dict.get('suit'))} "
        f"{slot_emoji('weapon', weapon)}"
    )
    row2 = (
        f"{slot_emoji('gauntlets', armor_dict.get('gauntlets'))} "
        f"{slot_emoji('boots', armor_dict.get('boots'))} "
        f"{pet_emoji}"
    )
    row3 = (
        f"{slot_emoji('ring1', acc_dict.get('ring1'))} "
        f"{slot_emoji('earring1', acc_dict.get('earring1'))} "
        f"{slot_emoji('pendant', acc_dict.get('pendant'))} "
        f"{slot_emoji('earring2', acc_dict.get('earring2'))} "
        f"{slot_emoji('ring2', acc_dict.get('ring2'))}"
    )
    embed.add_field(name="**Equipped Gears**", value=f"{row1}\n{row2}\n{row3}", inline=False)

    return embed


@bot.command(name='myprofile')
async def my_profile(ctx):
    """Display your character profile with a refresh button."""
    user_id = str(ctx.author.id)
    embed = await build_profile_embed(user_id, ctx.author)
    view = ProfileView(user_id)
    await ctx.send(embed=embed, view=view)



#    END



# =============================================================================
# SHOP SYSTEM – Persistent Interactive Shop
# =============================================================================
class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SHOP_IMAGE_URL = "https://cdn.discordapp.com/attachments/1470664051242700800/1471797792262455306/d4387e84d53fd24697a4218a9f6924a5.png?ex=6992e102&is=69918f82&hm=8a7bf535085e1dd0af98d977c5cc9766ecf463b73dbb5330444ff739b62c3571&"       
        self.booking_sessions = {}

    async def cog_load(self):
        """Called when the cog is loaded – safe to start tasks."""
        self.check_expired_purchases.start()

    def cog_unload(self):
        self.check_expired_purchases.cancel()

    # Unicode fallbacks for emojis that are not custom
    RING_UNICODE = "💍"
    GEM_UNICODE = "💎"
    TREASURE_UNICODE = "🎁"

    # ----- Upgrade System Helpers -----
    def upgrade_stone_cost(self, current_level: int) -> int:
        """Return stone cost to upgrade from given level."""
        return 2 * current_level + 1   # 1,3,5,...,19

    def upgrade_success_rate(self, current_level: int) -> int:
        """Return success percentage for upgrade from given level."""
        base = 100 - current_level * 10
        return max(30, base)

    def get_upgrade_multiplier(self, item_type: str) -> float:
        """Return stat multiplier for one upgrade based on item type."""
        if item_type == 'armor':
            return 1.05
        else:  # weapon or accessory
            return 1.10

    def get_armor_multipliers(self) -> tuple:
        """Return (def_mult, hp_mult) for one armor upgrade."""
        return 1.15, 1.20   # 15% DEF, 20% HP

    def get_stone_emoji(self, item_type: str) -> str:
        """Return the custom emoji for the enhancement stone of the given item type."""
        if item_type == 'weapon':
            return CUSTOM_EMOJIS.get('sword_enhancement_stone', '💎')
        elif item_type == 'armor':
            return CUSTOM_EMOJIS.get('armors_enhancement_stone', '💎')
        else:  # accessory
            return CUSTOM_EMOJIS.get('acc_enhancement_stone', '💎')

    def build_main_categories(self):
        embed = discord.Embed(
            title="🛍️ Shop Categories",
            description="Select a category to browse.",
            color=discord.Color.blue()
        )
        view = discord.ui.View(timeout=300)

        customization_emoji = discord.PartialEmoji(name="shadow", id=1477258013256454339)
        equipment_emoji = discord.PartialEmoji(name="zenith_sword", id=1477018808068866150)
        paw_emoji = discord.PartialEmoji(name="paw", id=1482627374066565170)
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
        button_pets = discord.ui.Button(
            label="Pets",
            emoji=paw_emoji,
            style=discord.ButtonStyle.secondary,
            custom_id="shop_maincat_pets"
        )
        button_tools = discord.ui.Button(
            label="Supplies",
            emoji=tools_emoji,
            style=discord.ButtonStyle.secondary,
            custom_id="shop_maincat_tools"
        )

        view.add_item(button_custom)
        view.add_item(button_equip)
        view.add_item(button_pets)
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
                    label="Open Shop",
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
            label="Open Shop",
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



    class UpgradeConfirmView(discord.ui.View):
        def __init__(self, cog, item_type: str, item_id: int, cost: int, chance: int, stone_emoji: str):
            super().__init__(timeout=60)
            self.cog = cog
            self.item_type = item_type
            self.item_id = item_id
            self.cost = cost
            self.chance = chance
            self.stone_emoji = stone_emoji

        @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
        async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer(ephemeral=True)
            await self.cog.handle_upgrade(interaction, self.item_type, self.item_id)

        @discord.ui.button(label="No", style=discord.ButtonStyle.secondary)
        async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer(ephemeral=True)
            embed = discord.Embed(
                title="❌ Upgrade Cancelled",
                description="You have cancelled the upgrade.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed, view=None)

    async def show_upgrade_confirmation(self, interaction: discord.Interaction, item_type: str, item_id: int):
        """Show an ephemeral confirmation dialog with Yes/No buttons."""
        user_id = str(interaction.user.id)
        await interaction.response.defer(ephemeral=True)

        stone_name_map = {
            'weapon': 'Sword Enhancement Stone',
            'armor': 'Armor Enhancement Stone',
            'accessory': 'Accessories Enhancement Stone'
        }
        stone_name = stone_name_map[item_type]

        async with self.bot.db_pool.acquire() as conn:
            # Get stone item_id
            stone_item = await conn.fetchrow("SELECT item_id FROM shop_items WHERE name = $1", stone_name)
            if not stone_item:
                await interaction.followup.send("❌ Enhancement stone not found. Contact admin.", ephemeral=True)
                return
            stone_id = stone_item['item_id']

            # Get item's current upgrade level
            table_map = {
                'weapon': 'user_weapons',
                'armor': 'user_armor',
                'accessory': 'user_accessories'
            }
            table = table_map[item_type]
            row = await conn.fetchrow(f"SELECT upgrade_level FROM {table} WHERE id = $1 AND user_id = $2", item_id, user_id)
            if not row:
                await interaction.followup.send("❌ Item not found.", ephemeral=True)
                return
            current_level = row['upgrade_level']
            if current_level >= 10:
                await interaction.followup.send("❌ Item is already at max level.", ephemeral=True)
                return

            # Get user's stone quantity
            stones_qty = await conn.fetchval("SELECT quantity FROM user_materials WHERE user_id = $1 AND material_id = $2", user_id, stone_id) or 0

        cost = self.upgrade_stone_cost(current_level)
        chance = self.upgrade_success_rate(current_level)
        stone_emoji = self.get_stone_emoji(item_type)

        embed = discord.Embed(
            title="⬆️ Confirm Upgrade",
            description=f"Do you want to upgrade this **{item_type}** to **+{current_level+1}**?",
            color=discord.Color.orange()
        )
        embed.add_field(name="You need", value=f"{stone_emoji} **{cost}** {stone_name}", inline=True)        
        embed.add_field(name="You have", value=f"{stone_emoji} **{stones_qty}**", inline=True)
        embed.add_field(name="Success rate", value=f"**{chance}%**", inline=True)
        embed.add_field(name="On Failure", value="Stones are consumed, item remains at current level.", inline=False)

        view = self.UpgradeConfirmView(self, item_type, item_id, cost, chance, stone_emoji)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


    async def handle_upgrade(self, interaction: discord.Interaction, item_type: str, item_id: int):
        """Perform the upgrade after confirmation."""
        user_id = str(interaction.user.id)

        stone_name_map = {
            'weapon': 'Sword Enhancement Stone',
            'armor': 'Armor Enhancement Stone',
            'accessory': 'Accessories Enhancement Stone'
        }
        stone_name = stone_name_map[item_type]

        async with self.bot.db_pool.acquire() as conn:
            # Get stone item_id
            stone_item = await conn.fetchrow("SELECT item_id FROM shop_items WHERE name = $1", stone_name)
            if not stone_item:
                embed = discord.Embed(
                    title="❌ Error",
                    description="Enhancement stone not found. Contact admin.",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed, view=None)
                return
            stone_id = stone_item['item_id']

            table_map = {
                'weapon': 'user_weapons',
                'armor': 'user_armor',
                'accessory': 'user_accessories'
            }
            table = table_map[item_type]

            # Fetch current upgrade level and stats
            if item_type == 'weapon':
                row = await conn.fetchrow(f"SELECT upgrade_level, attack FROM {table} WHERE id = $1 AND user_id = $2", item_id, user_id)
                if not row:
                    embed = discord.Embed(
                        title="❌ Error",
                        description="Weapon not found.",
                        color=discord.Color.red()
                    )
                    await interaction.edit_original_response(embed=embed, view=None)
                    return
                current_level, current_stat = row['upgrade_level'], row['attack']
            elif item_type == 'armor':
                row = await conn.fetchrow(f"SELECT upgrade_level, defense, hp_bonus FROM {table} WHERE id = $1 AND user_id = $2", item_id, user_id)
                if not row:
                    embed = discord.Embed(
                        title="❌ Error",
                        description="Armor not found.",
                        color=discord.Color.red()
                    )
                    await interaction.edit_original_response(embed=embed, view=None)
                    return
                current_level, current_def, current_hp = row['upgrade_level'], row['defense'], row['hp_bonus']
            else:  # accessory
                row = await conn.fetchrow(f"SELECT upgrade_level, bonus_value FROM {table} WHERE id = $1 AND user_id = $2", item_id, user_id)
                if not row:
                    embed = discord.Embed(
                        title="❌ Error",
                        description="Accessory not found.",
                        color=discord.Color.red()
                    )
                    await interaction.edit_original_response(embed=embed, view=None)
                    return
                current_level, current_stat = row['upgrade_level'], row['bonus_value']

            if current_level >= 10:
                embed = discord.Embed(
                    title="❌ Error",
                    description="Item is already at max level (+10).",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed, view=None)
                return

            required_stones = self.upgrade_stone_cost(current_level)
            success_chance = self.upgrade_success_rate(current_level)

            # Check user's stones
            stones_qty = await conn.fetchval("SELECT quantity FROM user_materials WHERE user_id = $1 AND material_id = $2", user_id, stone_id)
            if not stones_qty or stones_qty < required_stones:
                stone_emoji = self.get_stone_emoji(item_type)
                embed = discord.Embed(
                    title="❌ Insufficient Stones",
                    description=f"You need **{required_stones}** {stone_emoji} **{stone_name}** to upgrade.\nYou have: **{stones_qty or 0}**",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed, view=None)
                return

            # Deduct stones
            await conn.execute("UPDATE user_materials SET quantity = quantity - $1 WHERE user_id = $2 AND material_id = $3", required_stones, user_id, stone_id)

            # Determine success
            success = random.randint(1, 100) <= success_chance

            if success:
                multiplier = self.get_upgrade_multiplier(item_type)

                # Update upgrade level
                await conn.execute(f"UPDATE {table} SET upgrade_level = upgrade_level + 1 WHERE id = $1", item_id)

                # Apply stat increase
                if item_type == 'weapon':
                    new_stat = round(current_stat * multiplier)
                    await conn.execute(f"UPDATE {table} SET attack = $1 WHERE id = $2", new_stat, item_id)
                elif item_type == 'armor':
                    def_mult, hp_mult = self.get_armor_multipliers()
                    new_def = round(current_def * def_mult)
                    new_hp = round(current_hp * hp_mult)
                    await conn.execute(f"UPDATE {table} SET defense = $1, hp_bonus = $2 WHERE id = $3", new_def, new_hp, item_id)
                else:  # accessory
                    new_stat = round(current_stat * multiplier)
                    await conn.execute(f"UPDATE {table} SET bonus_value = $1 WHERE id = $2", new_stat, item_id)

                embed = discord.Embed(
                    title="✅ Upgrade Successful",
                    description=f"Your item is now **+{current_level+1}**!",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="❌ Upgrade Failed",
                    description=f"Lost **{required_stones}** stones. Item remains **+{current_level}**.",
                    color=discord.Color.red()
                )

            await interaction.edit_original_response(embed=embed, view=None)

        # Refresh the public item view (the message that contains the item details)
        # This will edit the public message with updated stats.
        await self.handle_item_selection(interaction, item_type, item_id)
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
            elif main_cat == "pets":                
                await self.show_pets(interaction)
            elif main_cat == "tools":
                await self.show_tools(interaction)

        # ✅ Correct: secret_shop_ is at the same level as other top‑level elifs
        elif custom_id.startswith("secret_shop_"):
            # Log for debugging (visible in Railway logs)
            print(f"[DEBUG] secret_shop button pressed with custom_id: {custom_id}")

            try:
                parts = custom_id.split("_")
                if len(parts) < 3:
                    raise ValueError("custom_id too short")
                purchase_id = int(parts[2])
            except (ValueError, IndexError) as e:
                print(f"[ERROR] Failed to parse purchase_id: {e}")
                # Send error message immediately (acknowledges the interaction)
                await interaction.response.send_message("❌ Invalid ticket ID.", ephemeral=True)
                return

            # Call the handler – it will defer first
            await self.secret_shop_button(interaction, purchase_id)

        elif custom_id == "shop_back_to_main":
            # Build the main categories embed and view
            embed, view = self.build_main_categories()
            # Edit the current message
            await interaction.response.edit_message(embed=embed, view=view)

        elif custom_id.startswith("shop_buy_"):
            item_id = int(custom_id.replace("shop_buy_", ""))
            await self.purchase_item(interaction, item_id)

        elif custom_id.startswith("buy_potion_10_"):
            item_id = int(custom_id.replace("buy_potion_10_", ""))
            await self.purchase_potion_batch(interaction, item_id, 10)


        # ===== INVENTORY BUTTON HANDLERS =====
        # Use helper methods instead of accessing view
        elif custom_id == "inventory_weapons":
            await self.handle_inventory_action(interaction, "weapons")
        
        elif custom_id == "inventory_armor":
            await self.handle_inventory_action(interaction, "armor")
        
        elif custom_id == "inventory_accessories":
            await self.handle_inventory_action(interaction, "accessories") 
   
        elif custom_id == "inventory_pets":
            await self.handle_inventory_action(interaction, "pets")

        elif custom_id == "inventory_back":
            await self.handle_inventory_action(interaction, "back")

        elif custom_id == "inventory_materials":
            await self.handle_inventory_action(interaction, "materials")

        elif custom_id.startswith("inv_material_"):
            parts = custom_id.split('_')
            if len(parts) >= 3:
                material_id = int(parts[2])
                await self.handle_material_selection(interaction, material_id)
        elif custom_id.startswith("inv_title_"):
            parts = custom_id.split('_')
            if len(parts) >= 3:
                title_id = int(parts[2])
                await self.handle_title_selection(interaction, title_id)

        elif custom_id == "item_back_materials":
            await self.handle_inventory_action(interaction, "materials")

        elif custom_id == "back_to_materials":
            await self.handle_inventory_action(interaction, "materials")

        # ===== INVENTORY ITEM BUTTONS =====
        elif custom_id.startswith("inv_"):
            # Format: inv_{item_type}_{item_id}
            parts = custom_id.split('_')
            if len(parts) >= 3:
                item_type = parts[1]
                item_id = int(parts[2])
                await self.handle_item_selection(interaction, item_type, item_id)

        # ===== EQUIP/UNEQUIP BUTTONS =====
        elif custom_id.startswith("equip_"):
            parts = custom_id.split('_')
            if len(parts) >= 3:
                item_type = parts[1]
                item_id = int(parts[2])
                await self.handle_equip_action(interaction, item_type, item_id)

        elif custom_id.startswith("unequip_"):
            parts = custom_id.split('_')
            if len(parts) >= 3:
                item_type = parts[1]
                item_id = int(parts[2])
                await self.handle_unequip_action(interaction, item_type, item_id)

        # ===== BACK BUTTONS =====
        elif custom_id == "category_back":
            await self.handle_inventory_action(interaction, "back")

        elif custom_id.startswith("upgrade_confirm_"):
            # format: upgrade_confirm_{item_type}_{item_id}
            parts = custom_id.split('_')
            if len(parts) >= 4:
                item_type = parts[2]
                item_id = int(parts[3])
                await self.show_upgrade_confirmation(interaction, item_type, item_id)

        # ===== PAGINATION BUTTONS =====   <-- INSERT HERE
        elif custom_id.startswith("category_prev_"):
            # Format: category_prev_{item_type}_{current_page}
            parts = custom_id.split('_')
            if len(parts) >= 4:
                item_type = parts[2]
                current_page = int(parts[3])
                new_page = current_page - 1
                await self.handle_category_page(interaction, item_type, new_page)

        elif custom_id.startswith("category_next_"):
            parts = custom_id.split('_')
            if len(parts) >= 4:
                item_type = parts[2]
                current_page = int(parts[3])
                new_page = current_page + 1
                await self.handle_category_page(interaction, item_type, new_page)


        elif custom_id.startswith("item_back_"):
            # format: item_back_{item_type}
            parts = custom_id.split('_')
            if len(parts) >= 3:
                item_type = parts[2]
                await self.handle_back_to_category(interaction, item_type)

    # HELPER METHODS
    async def handle_category_page(self, interaction: discord.Interaction, item_type: str, page: int):
        """Fetch items and show the category page."""
        try:
            user_id = str(interaction.user.id)

            # Fetch items of the requested type
            async with self.bot.db_pool.acquire() as conn:
                if item_type == 'weapon':
                    items = await conn.fetch("""
                        SELECT uw.id, COALESCE(si.name, uw.generated_name) as name,
                               uw.attack, uw.equipped, uw.description,
                               uw.bleeding_chance, uw.crit_chance, uw.crit_damage,
                               COALESCE(si.image_url, uw.image_url) as image_url,
                               r.color as rarity_color
                        FROM user_weapons uw
                        LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                        LEFT JOIN weapon_variants v ON uw.variant_id = v.variant_id
                        LEFT JOIN rarities r ON v.rarity_id = r.rarity_id
                        WHERE uw.user_id = $1
                        ORDER BY uw.equipped DESC, uw.purchased_at DESC
                    """, user_id)
                    embed_title = "🗡️ **Weapons**"
                    embed_color = discord.Color.red()
                elif item_type == 'armor':
                    items = await conn.fetch("""
                        SELECT ua.id, at.name, ua.defense, ua.equipped, at.slot,
                               ua.hp_bonus, ua.reflect_damage, at.set_name,
                               at.image_url, at.description, r.color as rarity_color
                        FROM user_armor ua
                        JOIN armor_types at ON ua.armor_id = at.armor_id
                        LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                        WHERE ua.user_id = $1
                        ORDER BY ua.equipped DESC, ua.purchased_at DESC
                    """, user_id)
                    embed_title = "🛡️ **Armor**"
                    embed_color = discord.Color.blue()
                else:  # accessory
                    items = await conn.fetch("""
                        SELECT ua.id, at.name, ua.bonus_value, at.bonus_stat,
                               ua.equipped, ua.slot, at.set_name,
                               at.image_url, at.description, r.color as rarity_color
                        FROM user_accessories ua
                        JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                        LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                        WHERE ua.user_id = $1
                        ORDER BY ua.equipped DESC, ua.purchased_at DESC
                    """, user_id)
                    embed_title = "📿 **Accessories**"
                    embed_color = discord.Color.green()

            items_list = [dict(item) for item in items]

            # Need a parent InventoryView – fetch full inventory data
            async with self.bot.db_pool.acquire() as conn:
                weapons_full = await conn.fetch("""
                    SELECT uw.id, COALESCE(si.name, uw.generated_name) as name,
                           uw.attack, uw.equipped, uw.description,
                           uw.bleeding_chance, uw.crit_chance, uw.crit_damage,
                           COALESCE(si.image_url, uw.image_url) as image_url,
                           r.color as rarity_color
                    FROM user_weapons uw
                    LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                    LEFT JOIN weapon_variants v ON uw.variant_id = v.variant_id
                    LEFT JOIN rarities r ON v.rarity_id = r.rarity_id
                    WHERE uw.user_id = $1
                    ORDER BY uw.equipped DESC, uw.purchased_at DESC
                """, user_id)
                armor_full = await conn.fetch("""
                    SELECT ua.id, at.name, ua.defense, ua.equipped, at.slot,
                           ua.hp_bonus, ua.reflect_damage, at.set_name,
                           at.image_url, at.description, r.color as rarity_color
                    FROM user_armor ua
                    JOIN armor_types at ON ua.armor_id = at.armor_id
                    LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                    WHERE ua.user_id = $1
                    ORDER BY ua.equipped DESC, ua.purchased_at DESC
                """, user_id)
                accessories_full = await conn.fetch("""
                    SELECT ua.id, at.name, ua.bonus_value, at.bonus_stat,
                           ua.equipped, ua.slot, at.set_name,
                           at.image_url, at.description, r.color as rarity_color
                    FROM user_accessories ua
                    JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                    LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                    WHERE ua.user_id = $1
                    ORDER BY ua.equipped DESC, ua.purchased_at DESC
                """, user_id)

            balance = await currency_system.get_balance(user_id)
            inventory_data = {
                'weapons': [dict(w) for w in weapons_full],
                'armor': [dict(a) for a in armor_full],
                'accessories': [dict(a) for a in accessories_full],
                'gems': balance['gems']
            }
            parent_view = InventoryView(user_id, inventory_data, self)

            # Create the category view for the requested page
            category_view = CategoryView(user_id, items_list, item_type, parent_view, page=page)

            # Create embed with page info
            embed = discord.Embed(title=embed_title, color=embed_color)
            total_pages = (len(items_list) - 1) // 20 + 1
            embed.set_footer(text=f"Page {page+1}/{total_pages}")

            await interaction.response.edit_message(embed=embed, view=category_view)

        except Exception as e:
            print(f"Error in handle_category_page: {e}")
            traceback.print_exc()
            await interaction.response.send_message("An error occurred.", ephemeral=True)
   


    async def handle_inventory_action(self, interaction: discord.Interaction, action: str):
        print(f"🔄 handle_inventory_action called with action: {action}")
        try:
            await interaction.response.defer(ephemeral=True)
            user_id = str(interaction.user.id)
            print(f"   user_id: {user_id}, action: {action}")

            # Fetch fresh inventory data
            async with self.bot.db_pool.acquire() as conn:
                weapons = await conn.fetch("""
                    SELECT uw.id, COALESCE(si.name, uw.generated_name) as name,
                           uw.attack, uw.equipped, uw.description,
                           uw.bleeding_chance, uw.crit_chance, uw.crit_damage,
                           COALESCE(si.image_url, uw.image_url) as image_url,
                           r.color as rarity_color,
                           uw.upgrade_level
                    FROM user_weapons uw
                    LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                    LEFT JOIN weapon_variants v ON uw.variant_id = v.variant_id
                    LEFT JOIN rarities r ON v.rarity_id = r.rarity_id
                    WHERE uw.user_id = $1
                    ORDER BY uw.equipped DESC, uw.purchased_at DESC
                """, user_id)

                armor = await conn.fetch("""
                    SELECT ua.id, at.name, ua.defense, ua.equipped, at.slot,
                           ua.hp_bonus, ua.reflect_damage, at.set_name,
                           at.image_url, at.description, r.color as rarity_color,
                           ua.upgrade_level
                    FROM user_armor ua
                    JOIN armor_types at ON ua.armor_id = at.armor_id
                    LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                    WHERE ua.user_id = $1
                    ORDER BY ua.equipped DESC, ua.purchased_at DESC
                """, user_id)

                accessories = await conn.fetch("""
                    SELECT ua.id, at.name, ua.bonus_value, at.bonus_stat,
                           ua.equipped, ua.slot, at.set_name,
                           at.image_url, at.description, r.color as rarity_color,
                           ua.upgrade_level
                    FROM user_accessories ua
                    JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                    LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                    WHERE ua.user_id = $1
                    ORDER BY ua.equipped DESC, ua.purchased_at DESC
                """, user_id)

                materials = await conn.fetch("""
                    SELECT um.material_id, si.name, um.quantity, si.description
                    FROM user_materials um
                    JOIN shop_items si ON um.material_id = si.item_id
                    WHERE um.user_id = $1 AND um.quantity > 0
                    ORDER BY si.name
                """, user_id)

            balance = await currency_system.get_balance(user_id)
        
            inventory_data = {
                'weapons': [dict(w) for w in weapons],
                'armor': [dict(a) for a in armor],
                'accessories': [dict(a) for a in accessories],
                'materials': [dict(m) for m in materials],  
                'gems': balance['gems']
            }

            # Create a temporary inventory view
            temp_view = InventoryView(user_id, inventory_data, self)

            if action == "weapons":
                await temp_view.show_weapons(interaction)
            elif action == "armor":
                await temp_view.show_armor(interaction)
            elif action == "accessories":
                await temp_view.show_accessories(interaction)
            elif action == "pets":
                await temp_view.show_pets(interaction)
            elif action == "materials":
                await temp_view.show_materials(interaction)
            elif action == "back":
                print("✅ back action triggered")
                # Create the main embed
                try:
                    embed = temp_view.create_main_embed()
                    print(f"   embed title: {embed.title}")
                    print(f"   embed fields: {len(embed.fields)}")
                except Exception as e:
                    print(f"❌ create_main_embed failed: {e}")
                    traceback.print_exc()
                    embed = discord.Embed(title="⚠️ Error", description="Could not load inventory.", color=discord.Color.red())
                
                # Edit the message
                try:
                    await interaction.edit_original_response(embed=embed, view=temp_view)
                    print("✅ edit_original_response succeeded")
                except Exception as e:
                    print(f"❌ edit_original_response failed: {e}")
                    traceback.print_exc()
                    await interaction.followup.send("Failed to update inventory view.", ephemeral=True)
                
                print("✅ back action completed")
            else:
                print(f"⚠️ Unknown action: {action}")
        except Exception as e:
            print(f"❌ Error in handle_inventory_action: {e}")
            traceback.print_exc()
            try:
                await interaction.followup.send("An error occurred while processing your request.", ephemeral=True)
            except:
                pass


    async def handle_item_selection(self, interaction: discord.Interaction, item_type: str, item_id: int):
        """Handle when a user clicks on an item - shows all stats"""
        if interaction.response.is_done():
            print(f"WARNING: Interaction already done for {item_type} {item_id} – ignoring.")
            return

        # Simple flag to prevent double execution (in case of double-click)
        if hasattr(self, '_processing_item') and self._processing_item:
            print("Already processing an item, ignoring duplicate click.")
            return
        self._processing_item = True

        user_id = str(interaction.user.id)

        deferred = False
        try:
            await interaction.response.defer(ephemeral=True)
            deferred = True
        except (ConnectionResetError, asyncio.TimeoutError, discord.HTTPException) as e:
            print(f"Defer failed: {e}")
            deferred = False

        try:
            # Fetch the specific item with all stats
            async with self.bot.db_pool.acquire() as conn:
                if item_type == 'weapon':
                    item = await conn.fetchrow("""
                        SELECT uw.id, COALESCE(si.name, uw.generated_name) as name,
                               uw.attack, uw.equipped, uw.description,
                               uw.bleeding_chance, uw.crit_chance, uw.crit_damage,
                               COALESCE(si.image_url, uw.image_url) as image_url,
                               r.color as rarity_color,
                               uw.upgrade_level
                        FROM user_weapons uw
                        LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                        LEFT JOIN weapon_variants v ON uw.variant_id = v.variant_id
                        LEFT JOIN rarities r ON v.rarity_id = r.rarity_id
                        WHERE uw.id = $1 AND uw.user_id = $2
                    """, item_id, user_id)

                elif item_type == 'armor':
                    item = await conn.fetchrow("""
                        SELECT ua.id, at.name, ua.defense, ua.equipped, at.slot,
                               ua.hp_bonus, ua.reflect_damage, at.set_name,
                               at.image_url, at.description, r.color as rarity_color,
                               ua.upgrade_level
                        FROM user_armor ua
                        JOIN armor_types at ON ua.armor_id = at.armor_id
                        LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                        WHERE ua.id = $1 AND ua.user_id = $2
                    """, item_id, user_id)

                elif item_type == 'accessory':
                    item = await conn.fetchrow("""
                        SELECT ua.id, at.name, ua.bonus_value, at.bonus_stat,
                               ua.equipped, ua.slot, at.set_name,
                               at.image_url, at.description, r.color as rarity_color,
                               ua.upgrade_level
                        FROM user_accessories ua
                        JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                        LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                        WHERE ua.id = $1 AND ua.user_id = $2
                    """, item_id, user_id)

                # ===== NEW: PET BRANCH =====
                elif item_type == 'pet':
                    item = await conn.fetchrow("""
                        SELECT up.id, pt.name, up.equipped,
                               pt.atk_percent, pt.def_percent, pt.hp_percent,
                               pt.dodge_percent, pt.bleed_flat, pt.burn_flat, pt.energy_bonus,
                               pt.description
                        FROM user_pets up
                        JOIN pet_types pt ON up.pet_id = pt.pet_id
                        WHERE up.id = $1 AND up.user_id = $2
                    """, item_id, user_id)

            if not item:           
                await interaction.followup.send("Item not found.", ephemeral=True)
                return

            current_level = item.get('upgrade_level', 0)

            # Get the custom emoji for this item
            if item_type == 'pet':
                item_emoji = get_pet_emoji(item['name'])
            else:
                item_emoji = get_item_emoji(item['name'], item_type)
            current_level = item.get('upgrade_level', 0)
            level_str = f" +{current_level}" if current_level > 0 else ""
        
            # Create detail embed with emoji and upgrade level in title
            embed = discord.Embed(
                title=f"{item_emoji} **{item['name']}**{level_str}",
                color=discord.Color.gold()
            )

            if item.get('image_url'):
                embed.set_image(url=item['image_url'])

            stats = []
        
            # ===== WEAPON STATS =====
            if item_type == 'weapon':
                stats.append(f"⚔️ **ATK:** `{item['attack']}`")
                stats.append(f"🩸 **Bleeding Chance:** `{item['bleeding_chance']}%`")
                stats.append(f"⚡ **Critical Chance:** `{item['crit_chance']}%`")
                stats.append(f"💥 **Critical Damage:** `{item['crit_damage']}%`")
                # Get skill info from SWORD_SKILLS
                wname = item['name']
                if wname in SWORD_SKILLS:
                    skill = SWORD_SKILLS[wname]
                    mult = skill['base'] + (item.get('skill_level', 1) - 1) * skill['increment']
                    stats.append(f"**Skill:** {skill['name']} Lv.{item.get('skill_level', 1)} ({mult:.1f}x)")
                    stats.append(f"*{skill['effect']}*")
            
            # ===== ARMOR STATS =====
            elif item_type == 'armor':
                stats.append(f"🛡️ **DEF:** `{item['defense']}`")
                stats.append(f"❤️ **HP Bonus:** `+{item['hp_bonus']}`")
                if item['reflect_damage'] and item['reflect_damage'] > 0:
                    stats.append(f"🔄 **Reflect DMG:** `{item['reflect_damage']}%`")
                if item.get('set_name'):
                    stats.append(f"⚔️ **Set:** `{item['set_name']}`")
                
            # ===== ACCESSORY STATS =====
            elif item_type == 'accessory':
                bonus_emoji = '⚔️' if item['bonus_stat'] == 'atk' else '🛡️' if item['bonus_stat'] == 'def' else '❤️'
                stats.append(f"{bonus_emoji} **{item['bonus_stat'].upper()}:** `+{item['bonus_value']}`")
                stats.append(f"📌 **Slot:** `{item['slot']}`")
                if item.get('set_name'):
                    stats.append(f"⚔️ **Set:** `{item['set_name']}`")

            # ===== PET STATS =====
            elif item_type == 'pet':
                stats_lines = []
                if item['atk_percent']:
                    stats_lines.append(f"⚔️ **ATK +{item['atk_percent']}%**")
                if item['def_percent']:
                    stats_lines.append(f"🛡️ **DEF +{item['def_percent']}%**")
                if item['hp_percent']:
                    stats_lines.append(f"❤️ **HP +{item['hp_percent']}%**")
                if item['dodge_percent']:
                    stats_lines.append(f"💨 **Dodge +{item['dodge_percent']}%**")
                if item['bleed_flat']:
                    stats_lines.append(f"🩸 **Bleed +{item['bleed_flat']}**")
                if item['burn_flat']:
                    stats_lines.append(f"🔥 **Burn +{item['burn_flat']}**")
                if item['energy_bonus']:
                    stats_lines.append(f"⚡ **Energy +{item['energy_bonus']}**")
                embed.description = "\n".join(stats_lines) if stats_lines else "No special stats."
                embed.add_field(name="Description", value=item['description'] or "No description.", inline=False)

            # For non-pet items, we already built stats in a list; add them as description
            if item_type != 'pet':
                stats.append(f"**Description:** {item.get('description', 'No description')}")
                embed.description = "\n".join(stats)

            if item.get('rarity_color'):
                embed.color = item['rarity_color']

            status = "✅ **EQUIPPED**" if item.get('equipped') else "❌ **NOT EQUIPPED**"
            embed.add_field(name="Status", value=status, inline=False)

            # ===== ADD SET BONUS INFORMATION IF APPLICABLE =====
            if item_type in ['armor', 'accessory'] and item.get('set_name'):
                set_name = item['set_name'].lower()
            
                # Check how many pieces of this set the user has equipped
                async with self.bot.db_pool.acquire() as conn:
                    if item_type == 'armor':
                        equipped_count = await conn.fetchval("""
                            SELECT COUNT(*) FROM user_armor 
                            WHERE user_id = $1 AND set_name = $2 AND equipped = TRUE
                        """, user_id, item['set_name'])
                    
                        # Define armor set bonuses
                        set_bonuses = {
                            'bilari': "⚡ +10% Crit Chance, 💥 +25% Crit DMG, 🛡️ +15% DEF, 🔄 +20% Reflect, ❤️ +20% HP",
                            'cryo': "⚡ +10% Crit Chance, 💥 +25% Crit DMG, 🛡️ +15% DEF, 🔄 +20% Reflect, ❤️ +20% HP",
                            'bane': "⚡ +10% Crit Chance, 💥 +25% Crit DMG, 🛡️ +15% DEF, 🔄 +20% Reflect, ❤️ +20% HP",
                        }
                    
                    else:  # accessory
                        # For accessories, count by type (rings, earrings, pendant)
                        rings = await conn.fetchval("""
                            SELECT COUNT(*) FROM user_accessories ua
                            JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                            WHERE ua.user_id = $1 AND at.set_name = $2 
                            AND at.slot LIKE 'ring%' AND ua.equipped = TRUE
                        """, user_id, item['set_name'])
                    
                        earrings = await conn.fetchval("""
                            SELECT COUNT(*) FROM user_accessories ua
                            JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                            WHERE ua.user_id = $1 AND at.set_name = $2 
                            AND at.slot LIKE 'earring%' AND ua.equipped = TRUE
                        """, user_id, item['set_name'])
                    
                        pendant = await conn.fetchval("""
                            SELECT 1 FROM user_accessories ua
                            JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                            WHERE ua.user_id = $1 AND at.set_name = $2 
                            AND at.slot = 'pendant' AND ua.equipped = TRUE
                        """, user_id, item['set_name'])
                    
                        equipped_count = rings + earrings + (1 if pendant else 0)
                    
                        # Define accessory set bonuses
                        set_bonuses = {
                            'champion': "❤️ +15% HP, 🛡️ +15% DEF, ⚔️ +20% ATK",
                            'defender': "❤️ +15% HP, 🛡️ +20% DEF, 🔄 +10% Reflect",
                            'angel': "❤️ +15% HP, ⚡ +15% Crit Chance, 🩸 +20% Bleed DMG",
                        }
                
                    # Show set progress
                    if item_type == 'armor':
                        progress_text = f"**Set Progress:** {equipped_count}/4 pieces equipped"
                        required = 4
                    else:
                        progress_text = f"**Set Progress:** {equipped_count}/5 pieces equipped (2 Rings + 2 Earrings + 1 Pendant)"
                        required = 5
                
                    embed.add_field(name="Set Collection", value=progress_text, inline=False)
                
                    # Show set bonus if complete
                    if equipped_count >= required:
                        bonus_text = set_bonuses.get(item['set_name'].lower(), "Complete set bonus activated!")
                        embed.add_field(name="✨ SET BONUS ACTIVE", value=bonus_text, inline=False)
                    else:
                        missing = required - equipped_count
                        bonus_text = set_bonuses.get(item['set_name'].lower(), "Complete set for bonus!")
                        embed.add_field(name=f"⏳ Set Bonus ({missing} more to go)", value=bonus_text, inline=False)

            # Create action view - ONLY show the relevant button
            view = discord.ui.View(timeout=60)
        
            # Add ONLY the button that matches current state
            if item.get('equipped'):
                # Item is equipped - show UNEQUIP button
                view.add_item(discord.ui.Button(
                    label="Unequip", 
                    style=discord.ButtonStyle.danger, 
                    custom_id=f"unequip_{item_type}_{item_id}", 
                    row=0
                ))
            else:
                # Item is not equipped - show EQUIP button
                view.add_item(discord.ui.Button(
                    label="Equip", 
                    style=discord.ButtonStyle.success, 
                    custom_id=f"equip_{item_type}_{item_id}", 
                    row=0
                ))
            # Upgrade button (if not max level) – only for weapons/armor/accessories
            if item_type in ('weapon', 'armor', 'accessory') and current_level < 10:
                view.add_item(discord.ui.Button(
                    label="Upgrade",
                    style=discord.ButtonStyle.primary,
                    custom_id=f"upgrade_confirm_{item_type}_{item_id}",
                    row=0
                ))
            # Always show back button
            view.add_item(discord.ui.Button(
                label="🔙", 
                style=discord.ButtonStyle.secondary, 
                custom_id=f"item_back_{item_type}", 
                row=1
            ))

            if deferred:
                await interaction.edit_original_response(embed=embed, view=view)
            else:
                await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            print(f"Error in handle_item_selection: {e}")
            traceback.print_exc()
            try:
                await interaction.followup.send("An error occurred.", ephemeral=True)
            except:
                pass
        finally:
            # Reset the flag
            self._processing_item = False

    async def handle_equip_action(self, interaction: discord.Interaction, item_type: str, item_id: int):
        """Handle equipping an item"""
        try:
            user_id = str(interaction.user.id)
            await interaction.response.defer(ephemeral=True)

            async with self.bot.db_pool.acquire() as conn:
                if item_type == 'weapon':
                    # Unequip all weapons first
                    await conn.execute("UPDATE user_weapons SET equipped = FALSE WHERE user_id = $1", user_id)
                    # Equip selected weapon
                    await conn.execute("UPDATE user_weapons SET equipped = TRUE WHERE id = $1 AND user_id = $2", item_id, user_id)
                    # Get item name
                    item_row = await conn.fetchrow("""
                        SELECT COALESCE(si.name, uw.generated_name) as name 
                        FROM user_weapons uw 
                        LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id 
                        WHERE uw.id = $1
                    """, item_id)
                    item = item_row['name'] if item_row else "Unknown"
                
                elif item_type == 'armor':
                    # Get slot
                    slot = await conn.fetchval("""
                        SELECT at.slot FROM user_armor ua
                        JOIN armor_types at ON ua.armor_id = at.armor_id
                        WHERE ua.id = $1
                    """, item_id)
                    # Unequip other armor in same slot
                    await conn.execute("""
                        UPDATE user_armor SET equipped = FALSE 
                        WHERE user_id = $1 AND armor_id IN 
                        (SELECT armor_id FROM armor_types WHERE slot = $2)
                    """, user_id, slot)
                    # Equip new armor
                    await conn.execute("UPDATE user_armor SET equipped = TRUE WHERE id = $1 AND user_id = $2", item_id, user_id)
                    # Get item name
                    item_row = await conn.fetchval("""
                        SELECT at.name FROM user_armor ua 
                        JOIN armor_types at ON ua.armor_id = at.armor_id 
                        WHERE ua.id = $1
                    """, item_id)
                    item = item_row if item_row else "Unknown"
                
                elif item_type == 'accessory':
                    # Get accessory details: current slot and category
                    acc_info = await conn.fetchrow("""
                        SELECT ua.slot, at.slot as category
                        FROM user_accessories ua
                        JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                        WHERE ua.id = $1
                    """, item_id)
                    if not acc_info:
                        await interaction.followup.send("Accessory not found.", ephemeral=True)
                        return

                    current_slot = acc_info['slot']
                    category = acc_info['category']  # 'ring', 'earring', or 'pendant'

                    # Determine possible slots for this category
                    if category == 'ring':
                        possible_slots = ['ring1', 'ring2']
                    elif category == 'earring':
                        possible_slots = ['earring1', 'earring2']
                    else:  # pendant
                        possible_slots = ['pendant']

                    # If current_slot is NULL, assign an available slot
                    if current_slot is None:
                        # Find already occupied slots for this category
                        occupied = await conn.fetch("""
                            SELECT slot FROM user_accessories
                            WHERE user_id = $1 AND equipped = TRUE AND slot IS NOT NULL
                        """, user_id)
                        occupied_slots = [row['slot'] for row in occupied]
                        available = [s for s in possible_slots if s not in occupied_slots]
                        if not available:
                            await interaction.followup.send(f"No available {category} slots. Unequip one first.", ephemeral=True)
                            return
                        new_slot = available[0]
                        # Assign the slot
                        await conn.execute("UPDATE user_accessories SET slot = $1 WHERE id = $2", new_slot, item_id)
                        slot = new_slot
                    else:
                        slot = current_slot
                        # If already has a slot, unequip any other accessory in that slot (safety)
                        await conn.execute("UPDATE user_accessories SET equipped = FALSE WHERE user_id = $1 AND slot = $2 AND id != $3", user_id, slot, item_id)

                    # Equip this accessory
                    await conn.execute("UPDATE user_accessories SET equipped = TRUE WHERE id = $1", item_id)

                    # Get item name
                    item_row = await conn.fetchval("""
                        SELECT at.name FROM user_accessories ua 
                        JOIN accessory_types at ON ua.accessory_id = at.accessory_id 
                        WHERE ua.id = $1
                    """, item_id)
                    item = item_row if item_row else "Unknown"

                elif item_type == 'title':
                    # Unequip all titles
                    await conn.execute("UPDATE user_titles SET equipped = FALSE WHERE user_id = $1", user_id)
                    # Equip selected title
                    await conn.execute("UPDATE user_titles SET equipped = TRUE WHERE user_id = $1 AND title_id = $2", user_id, item_id)
                    # Fetch title name and emoji
                    title_row = await conn.fetchrow("SELECT name, emoji FROM titles WHERE title_id = $1", item_id)
                    if title_row:
                        item = title_row['name']
                        item_emoji = title_row['emoji'] or '👑'
                    else:
                        item = "Unknown Title"
                        item_emoji = '👑'
                    # Send confirmation immediately
                    await interaction.followup.send(f"**Equipped** {item_emoji}", ephemeral=True)

                elif item_type == 'pet':
                    # Unequip all pets
                    await conn.execute("UPDATE user_pets SET equipped = FALSE WHERE user_id = $1", user_id)
                    # Equip selected pet
                    await conn.execute("UPDATE user_pets SET equipped = TRUE WHERE id = $1 AND user_id = $2", item_id, user_id)
                    # Get pet name
                    item = await conn.fetchval("""
                        SELECT pt.name FROM user_pets up
                        JOIN pet_types pt ON up.pet_id = pt.pet_id
                        WHERE up.id = $1
                    """, item_id)

            # For non-title items, get emoji via helper and send confirmation
            if item_type != 'title':
                item_emoji = get_item_emoji(item, item_type)
                await interaction.followup.send(f"**Equipped**{item_emoji}", ephemeral=True)

            # If the item can affect HP (armor or accessory), update player's HP
            if item_type in ('armor', 'accessory'):
                await self.update_player_hp_after_equip(user_id)

            # Refresh inventory data (including materials and titles for consumables view)
            async with self.bot.db_pool.acquire() as conn:
                weapons = await conn.fetch("""
                    SELECT uw.id, COALESCE(si.name, uw.generated_name) as name,
                           uw.attack, uw.equipped, uw.description,
                           uw.bleeding_chance, uw.crit_chance, uw.crit_damage,
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
                           ua.hp_bonus, ua.reflect_damage, at.set_name,
                           at.image_url, at.description, r.color as rarity_color
                    FROM user_armor ua
                    JOIN armor_types at ON ua.armor_id = at.armor_id
                    LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                    WHERE ua.user_id = $1
                    ORDER BY ua.equipped DESC, ua.purchased_at DESC
                """, user_id)

                accessories = await conn.fetch("""
                    SELECT ua.id, at.name, ua.bonus_value, at.bonus_stat,
                           ua.equipped, ua.slot, at.set_name,
                           at.image_url, at.description, r.color as rarity_color
                    FROM user_accessories ua
                    JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                    LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                    WHERE ua.user_id = $1
                    ORDER BY ua.equipped DESC, ua.purchased_at DESC
                """, user_id)

                materials = await conn.fetch("""
                    SELECT um.material_id, si.name, um.quantity, si.description
                    FROM user_materials um
                    JOIN shop_items si ON um.material_id = si.item_id
                    WHERE um.user_id = $1 AND um.quantity > 0
                    ORDER BY si.name
                """, user_id)

                # Fetch titles for the combined consumables view
                titles = await conn.fetch("""
                    SELECT t.title_id as id, t.name, t.emoji, ut.equipped,
                           t.hp_percent, t.def_percent, t.atk_percent,
                           t.crit_chance, t.dodge_percent, t.dmg_reduction_percent,
                           t.bleed_flat, t.burn_flat, t.crit_dmg_res_percent,
                           t.mining_bonus_percent, t.boss_damage_percent,
                           t.extra_boss_attempts, t.extra_plunder_attempts
                    FROM titles t
                    JOIN user_titles ut ON t.title_id = ut.title_id
                    WHERE ut.user_id = $1
                    ORDER BY ut.equipped DESC, t.name
                """, user_id)

            balance = await currency_system.get_balance(user_id)

            inventory_data = {
                'weapons': [dict(w) for w in weapons],
                'armor': [dict(a) for a in armor],
                'accessories': [dict(a) for a in accessories],
                'materials': [dict(m) for m in materials],
                'gems': balance['gems']
            }

            temp_inventory_view = InventoryView(user_id, inventory_data, self)

            # Redirect based on item type
            if item_type == 'weapon':
                await temp_inventory_view.show_weapons(interaction)
            elif item_type == 'armor':
                await temp_inventory_view.show_armor(interaction)
            elif item_type == 'accessory':
                await temp_inventory_view.show_accessories(interaction)
            elif item_type == 'pet':
                await temp_inventory_view.show_pets(interaction)
            elif item_type == 'title':
                # After equipping title, go to consumables (which includes titles)
                await temp_inventory_view.show_materials(interaction)
            else:
                # fallback to main inventory
                embed = temp_inventory_view.create_main_embed()
                await interaction.edit_original_response(embed=embed, view=temp_inventory_view)

        except Exception as e:
            print(f"Error in handle_equip_action: {e}")
            traceback.print_exc()
            try:
                await interaction.followup.send("An error occurred while equipping.", ephemeral=True)
            except:
                pass
                  

    async def handle_unequip_action(self, interaction: discord.Interaction, item_type: str, item_id: int):
        """Handle unequipping an item"""
        try:
            user_id = str(interaction.user.id)
            await interaction.response.defer(ephemeral=True)

            async with self.bot.db_pool.acquire() as conn:
                if item_type == 'weapon':
                    await conn.execute("UPDATE user_weapons SET equipped = FALSE WHERE id = $1 AND user_id = $2", item_id, user_id)
                    item_row = await conn.fetchrow("""
                        SELECT COALESCE(si.name, uw.generated_name) as name 
                        FROM user_weapons uw 
                        LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id 
                        WHERE uw.id = $1
                    """, item_id)
                    item = item_row['name'] if item_row else "Unknown"
                
                elif item_type == 'armor':
                    await conn.execute("UPDATE user_armor SET equipped = FALSE WHERE id = $1 AND user_id = $2", item_id, user_id)
                    item_row = await conn.fetchval("""
                        SELECT at.name FROM user_armor ua 
                        JOIN armor_types at ON ua.armor_id = at.armor_id 
                        WHERE ua.id = $1
                    """, item_id)
                    item = item_row if item_row else "Unknown"
                
                elif item_type == 'accessory':
                    await conn.execute("""
                        UPDATE user_accessories 
                        SET equipped = FALSE, slot = NULL 
                        WHERE id = $1 AND user_id = $2
                    """, item_id, user_id)
                    item_row = await conn.fetchval("""
                        SELECT at.name FROM user_accessories ua 
                        JOIN accessory_types at ON ua.accessory_id = at.accessory_id 
                        WHERE ua.id = $1
                    """, item_id)
                    item = item_row if item_row else "Unknown"

                elif item_type == 'title':
                    await conn.execute("UPDATE user_titles SET equipped = FALSE WHERE user_id = $1 AND title_id = $2", user_id, item_id)
                    # Fetch title name and emoji
                    title_row = await conn.fetchrow("SELECT name, emoji FROM titles WHERE title_id = $1", item_id)
                    if title_row:
                        item = title_row['name']
                        item_emoji = title_row['emoji'] or '👑'
                    else:
                        item = "Unknown Title"
                        item_emoji = '👑'

                elif item_type == 'pet':
                    await conn.execute("UPDATE user_pets SET equipped = FALSE WHERE id = $1 AND user_id = $2", item_id, user_id)
                    item = await conn.fetchval("""
                        SELECT pt.name FROM user_pets up
                        JOIN pet_types pt ON up.pet_id = pt.pet_id
                        WHERE up.id = $1
                    """, item_id)

            # For non-title items, get emoji via helper
            if item_type != 'title':
                item_emoji = get_item_emoji(item, item_type)
        
            await interaction.followup.send(f"**Unequipped** {item_emoji}", ephemeral=True)
        
            # Refresh inventory data (including materials and titles)
            async with self.bot.db_pool.acquire() as conn:
                weapons = await conn.fetch("""
                    SELECT uw.id, COALESCE(si.name, uw.generated_name) as name,
                           uw.attack, uw.equipped, uw.description,
                           uw.bleeding_chance, uw.crit_chance, uw.crit_damage,
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
                           ua.hp_bonus, ua.reflect_damage, at.set_name,
                           at.image_url, at.description, r.color as rarity_color
                    FROM user_armor ua
                    JOIN armor_types at ON ua.armor_id = at.armor_id
                    LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                    WHERE ua.user_id = $1
                    ORDER BY ua.equipped DESC, ua.purchased_at DESC
                """, user_id)

                accessories = await conn.fetch("""
                    SELECT ua.id, at.name, ua.bonus_value, at.bonus_stat,
                           ua.equipped, ua.slot, at.set_name,
                           at.image_url, at.description, r.color as rarity_color
                    FROM user_accessories ua
                    JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                    LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                    WHERE ua.user_id = $1
                    ORDER BY ua.equipped DESC, ua.purchased_at DESC
                """, user_id)

                materials = await conn.fetch("""
                    SELECT um.material_id, si.name, um.quantity, si.description
                    FROM user_materials um
                    JOIN shop_items si ON um.material_id = si.item_id
                    WHERE um.user_id = $1 AND um.quantity > 0
                    ORDER BY si.name
                """, user_id)

                # Fetch titles for the combined consumables view
                titles = await conn.fetch("""
                    SELECT t.title_id as id, t.name, t.emoji, ut.equipped,
                           t.hp_percent, t.def_percent, t.atk_percent,
                           t.crit_chance, t.dodge_percent, t.dmg_reduction_percent,
                           t.bleed_flat, t.burn_flat, t.crit_dmg_res_percent,
                           t.mining_bonus_percent, t.boss_damage_percent,
                           t.extra_boss_attempts, t.extra_plunder_attempts
                    FROM titles t
                    JOIN user_titles ut ON t.title_id = ut.title_id
                    WHERE ut.user_id = $1
                    ORDER BY ut.equipped DESC, t.name
                """, user_id)

            balance = await currency_system.get_balance(user_id)

            inventory_data = {
                'weapons': [dict(w) for w in weapons],
                'armor': [dict(a) for a in armor],
                'accessories': [dict(a) for a in accessories],
                'materials': [dict(m) for m in materials],
                'gems': balance['gems']
            }

            # Create temporary inventory view
            temp_inventory_view = InventoryView(user_id, inventory_data, self)

            # Add titles to the view's inventory data for later use (optional, but show_materials already fetches fresh)
            # For simplicity, we'll just call show_materials which does its own fetch.

            if item_type == 'weapon':
                await temp_inventory_view.show_weapons(interaction)
            elif item_type == 'armor':
                await temp_inventory_view.show_armor(interaction)
            elif item_type == 'accessory':
                await temp_inventory_view.show_accessories(interaction)
            elif item_type == 'pet':
                await temp_inventory_view.show_pets(interaction)
            elif item_type == 'title':
                # After unequipping title, go to consumables (which includes titles)
                await temp_inventory_view.show_materials(interaction)
            else:
                # fallback to main inventory
                embed = temp_inventory_view.create_main_embed()
                await interaction.edit_original_response(embed=embed, view=temp_inventory_view)

        except Exception as e:
            print(f"Error in handle_unequip_action: {e}")
            traceback.print_exc()
            try:
                await interaction.followup.send("An error occurred while unequipping.", ephemeral=True)
            except:
                pass


    async def update_player_hp_after_equip(self, user_id: str):
        """Recalculate max HP based on equipped gear (flat bonuses + set bonuses) and set current HP to new max."""
        BASE_HP = 1000
        async with self.bot.db_pool.acquire() as conn:
            # Fetch equipped armor with set_name and hp_bonus
            armor_rows = await conn.fetch("""
                SELECT ua.hp_bonus, at.set_name
                FROM user_armor ua
                JOIN armor_types at ON ua.armor_id = at.armor_id
                WHERE ua.user_id = $1 AND ua.equipped = TRUE
            """, user_id)

            # Sum flat HP bonuses from armor
            flat_hp = sum(row['hp_bonus'] or 0 for row in armor_rows)

            # Count armor sets
            armor_set_counts = {}
            for row in armor_rows:
                if row['set_name']:
                    armor_set_counts[row['set_name']] = armor_set_counts.get(row['set_name'], 0) + 1

            # Fetch equipped accessories with set_name
            acc_rows = await conn.fetch("""
                SELECT at.set_name
                FROM user_accessories ua
                JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                WHERE ua.user_id = $1 AND ua.equipped = TRUE
            """, user_id)

            # Count accessory sets
            acc_set_counts = {}
            for row in acc_rows:
                if row['set_name']:
                    acc_set_counts[row['set_name']] = acc_set_counts.get(row['set_name'], 0) + 1

            # Start max HP with base + flat bonuses
            max_hp = BASE_HP + flat_hp

            # Apply armor set bonuses (if full set equipped)
            for set_name, count in armor_set_counts.items():
                if count >= 4:  # all 4 armor pieces
                    sname = set_name.lower()
                    if sname in ('bilari', 'cryo', 'bane'):
                        max_hp += int(BASE_HP * 0.20)  # +20% of base HP

            # Apply accessory set bonuses
            for set_name, count in acc_set_counts.items():
                if count >= 5:
                    sname = set_name.lower()
                    if sname == 'champion':
                        max_hp += int(BASE_HP * 0.15)  # +15% HP
                    elif sname == 'defender':
                        max_hp += int(BASE_HP * 0.15)  # +15% HP
                    elif sname == 'angel':
                        max_hp += int(BASE_HP * 0.15)  # +15% HP

            # Update player_stats: set current HP to new max and store max_hp
            await conn.execute("""
                UPDATE player_stats 
                SET hp = $1, max_hp = $1 
                WHERE user_id = $2
            """, max_hp, user_id)      


    async def handle_material_selection(self, interaction: discord.Interaction, material_id: int):
        user_id = str(interaction.user.id)
        await interaction.response.defer(ephemeral=False)

        async with self.bot.db_pool.acquire() as conn:
            material = await conn.fetchrow("""
                SELECT si.name, si.description, um.quantity
                FROM user_materials um
                JOIN shop_items si ON um.material_id = si.item_id
                WHERE um.user_id = $1 AND um.material_id = $2
            """, user_id, material_id)

        if not material:
            await interaction.followup.send("Material not found.", ephemeral=True)
            return

        # Determine emoji based on name – use a single variable 'emoji'
        name_lower = material['name'].lower()
        if 'hp potion' in name_lower:
            emoji = CUSTOM_EMOJIS.get('hp_potion', '🧪')
        elif 'energy potion' in name_lower:
            emoji = CUSTOM_EMOJIS.get('energy_potion', '⚡')
        elif 'sword' in name_lower:
            emoji = CUSTOM_EMOJIS.get('sword_enhancement_stone', '💎')
        elif 'armor' in name_lower:
            emoji = CUSTOM_EMOJIS.get('armors_enhancement_stone', '💎')
        elif 'accessories' in name_lower:
            emoji = CUSTOM_EMOJIS.get('acc_enhancement_stone', '💎')
        else:
            emoji = '📦'

        embed = discord.Embed(
            title=f"{emoji} **{material['name']}**",
            description=material['description'] or "No description available.",
            color=discord.Color.light_grey()
        )
        embed.add_field(name="Quantity", value=str(material['quantity']), inline=True)

        view = discord.ui.View(timeout=60)
        view.add_item(discord.ui.Button(label="🔙", style=discord.ButtonStyle.secondary, custom_id="back_to_materials", row=0))

        await interaction.edit_original_response(embed=embed, view=view)


    async def handle_title_selection(self, interaction: discord.Interaction, title_id: int):
        user_id = str(interaction.user.id)
        await interaction.response.defer(ephemeral=False)

        async with self.bot.db_pool.acquire() as conn:
            title = await conn.fetchrow("""
                SELECT t.title_id, t.name, t.emoji, t.description,
                       t.hp_percent, t.def_percent, t.atk_percent,
                       t.crit_chance, t.dodge_percent, t.dmg_reduction_percent,
                       t.bleed_flat, t.burn_flat, t.crit_dmg_res_percent,
                       t.mining_bonus_percent, t.boss_damage_percent,
                       t.extra_boss_attempts, t.extra_plunder_attempts,
                       ut.equipped
                FROM titles t
                JOIN user_titles ut ON t.title_id = ut.title_id
                WHERE t.title_id = $1 AND ut.user_id = $2
            """, title_id, user_id)

        if not title:
            await interaction.followup.send("Title not found.", ephemeral=True)
            return

        emoji = title['emoji'] or '👑'
        embed = discord.Embed(
            title=f"{emoji} **{title['name']}**",
            description=title['description'] or "No description.",
            color=discord.Color.gold()
        )

        stats = []
        if title['hp_percent']:
            stats.append(f"HP +{title['hp_percent']}%")
        if title['def_percent']:
            stats.append(f"DEF +{title['def_percent']}%")
        if title['atk_percent']:
            stats.append(f"ATK +{title['atk_percent']}%")
        if title['crit_chance']:
            stats.append(f"Crit Chance +{title['crit_chance']}%")
        if title['dodge_percent']:
            stats.append(f"Dodge +{title['dodge_percent']}%")
        if title['dmg_reduction_percent']:
            stats.append(f"Damage Reduction +{title['dmg_reduction_percent']}%")
        if title['bleed_flat']:
            stats.append(f"Bleed +{title['bleed_flat']}")
        if title['burn_flat']:
            stats.append(f"Burn +{title['burn_flat']}")
        if title['crit_dmg_res_percent']:
            stats.append(f"Crit DMG RES +{title['crit_dmg_res_percent']}%")
        if title['mining_bonus_percent']:
            stats.append(f"Mining Bonus +{title['mining_bonus_percent']}%")
        if title['boss_damage_percent']:
            stats.append(f"Boss DMG +{title['boss_damage_percent']}%")
        if title['extra_boss_attempts']:
            stats.append(f"+{title['extra_boss_attempts']} Boss Attempts")
        if title['extra_plunder_attempts']:
            stats.append(f"+{title['extra_plunder_attempts']} Plunder Attempts")

        if stats:
            embed.add_field(name="Stats", value="\n".join(stats), inline=False)
        else:
            embed.add_field(name="Stats", value="No bonuses.", inline=False)

        status = "✅ **EQUIPPED**" if title['equipped'] else "❌ **NOT EQUIPPED**"
        embed.add_field(name="Status", value=status, inline=False)

        view = discord.ui.View(timeout=60)
        if title['equipped']:
            view.add_item(discord.ui.Button(
                label="Unequip",
                style=discord.ButtonStyle.danger,
                custom_id=f"unequip_title_{title_id}",
                row=0
            ))
        else:
            view.add_item(discord.ui.Button(
                label="Equip",
                style=discord.ButtonStyle.success,
                custom_id=f"equip_title_{title_id}",
                row=0
            ))
        view.add_item(discord.ui.Button(
            label="🔙",
            style=discord.ButtonStyle.secondary,
            custom_id="item_back_materials",
            row=1
        ))

        await interaction.edit_original_response(embed=embed, view=view)



    async def handle_back_to_category(self, interaction: discord.Interaction, item_type: str):
        """Return from item detail to the category view."""
        user_id = str(interaction.user.id)
        await interaction.response.defer(ephemeral=True)

        # Fetch fresh inventory data
        async with self.bot.db_pool.acquire() as conn:
            weapons = await conn.fetch("""
                SELECT uw.id, COALESCE(si.name, uw.generated_name) as name,
                       uw.attack, uw.equipped, uw.description,
                       uw.bleeding_chance, uw.crit_chance, uw.crit_damage,
                       COALESCE(si.image_url, uw.image_url) as image_url,
                       r.color as rarity_color,
                       uw.upgrade_level
                FROM user_weapons uw
                LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                LEFT JOIN weapon_variants v ON uw.variant_id = v.variant_id
                LEFT JOIN rarities r ON v.rarity_id = r.rarity_id
                WHERE uw.user_id = $1
                ORDER BY uw.equipped DESC, uw.purchased_at DESC
            """, user_id)

            armor = await conn.fetch("""
                SELECT ua.id, at.name, ua.defense, ua.equipped, at.slot,
                       ua.hp_bonus, ua.reflect_damage, at.set_name,
                       at.image_url, at.description, r.color as rarity_color,
                       ua.upgrade_level
                FROM user_armor ua
                JOIN armor_types at ON ua.armor_id = at.armor_id
                LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                WHERE ua.user_id = $1
                ORDER BY ua.equipped DESC, ua.purchased_at DESC
            """, user_id)

            accessories = await conn.fetch("""
                SELECT ua.id, at.name, ua.bonus_value, at.bonus_stat,
                       ua.equipped, ua.slot, at.set_name,
                       at.image_url, at.description, r.color as rarity_color,
                       ua.upgrade_level
                FROM user_accessories ua
                JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                WHERE ua.user_id = $1
                ORDER BY ua.equipped DESC, ua.purchased_at DESC
            """, user_id)

            materials = await conn.fetch("""
                SELECT um.material_id, si.name, um.quantity, si.description
                FROM user_materials um
                JOIN shop_items si ON um.material_id = si.item_id
                WHERE um.user_id = $1 AND um.quantity > 0
                ORDER BY si.name
            """, user_id)

        balance = await currency_system.get_balance(user_id)

        inventory_data = {
            'weapons': [dict(w) for w in weapons],
            'armor': [dict(a) for a in armor],
            'accessories': [dict(a) for a in accessories],
            'materials': [dict(m) for m in materials],
            'gems': balance['gems']
        }

        # Create a temporary view and show the appropriate category
        temp_view = InventoryView(user_id, inventory_data, self)

        if item_type == 'weapon':
            await temp_view.show_weapons(interaction)
        elif item_type == 'armor':
            await temp_view.show_armor(interaction)
        elif item_type == 'accessory':
            await temp_view.show_accessories(interaction)
        elif item_type == 'pet':     
            await temp_view.show_pets(interaction)
        elif item_type == 'material':
            await temp_view.show_materials(interaction)

    @commands.command(name='fix_shop_constraint')
    @commands.has_permissions(administrator=True)
    async def fix_shop_constraint(self, ctx):
        """Add 'material' to the allowed types in shop_items."""
        async with self.bot.db_pool.acquire() as conn:
            # Drop the old constraint and recreate with 'material' included
            await conn.execute("ALTER TABLE shop_items DROP CONSTRAINT IF EXISTS shop_items_type_check;")
            await conn.execute("""
                ALTER TABLE shop_items ADD CONSTRAINT shop_items_type_check 
                CHECK (type IN ('role', 'color', 'weapon', 'random_weapon_box', 
                                'random_gear_box', 'random_accessories_box', 'pickaxe', 'material'))
            """)
        await ctx.send("✅ Shop items type constraint updated to include 'material'.")


    @commands.command(name='addstones')
    @commands.has_permissions(administrator=True)
    async def add_stones(self, ctx):
        """Add enhancement stone items to the shop (admin only)."""
        async with self.bot.db_pool.acquire() as conn:
            stones = [
                ('Sword Enhancement Stone', 'Use to upgrade weapons.', 1, 'material'),
                ('Armor Enhancement Stone', 'Use to upgrade armor.', 1, 'material'),
                ('Accessories Enhancement Stone', 'Use to upgrade accessories.', 1, 'material')
            ]
            for name, desc, price, typ in stones:
                exists = await conn.fetchval("SELECT 1 FROM shop_items WHERE name = $1", name)
                if not exists:
                    await conn.execute("""
                        INSERT INTO shop_items (name, description, price, type)
                        VALUES ($1, $2, $3, $4)
                    """, name, desc, price, typ)
        await ctx.send("✅ Enhancement stones have been added to the shop database.")

    @commands.command(name='givestones')
    @commands.has_permissions(administrator=True)
    async def give_stones(self, ctx, *args):
        """
        Give enhancement stones to a user. Admins only.
        Usage: !!givestones [@user] <sword|armor|acc> <amount> [type amount ...]
        Example: !!givestones @purr404 sword 10 armor 5 acc 3
        """
        if not args:
            await ctx.send("❌ Usage: `!!givestones [@user] <sword|armor|acc> <amount> [type amount ...]`")
            return

        # Determine if first argument is a member
        target = None
        start_idx = 0
        if len(args) >= 1 and ctx.message.mentions:
            target = ctx.message.mentions[0]
            start_idx = 1
        else:
            target = ctx.author
            start_idx = 0

        # Parse remaining args as type‑amount pairs
        pairs = []
        i = start_idx
        while i < len(args):
            if i + 1 >= len(args):
                await ctx.send("❌ Missing amount for stone type `{}`.".format(args[i]))
                return
            stone_type = args[i].lower()
            try:
                amount = int(args[i+1])
            except ValueError:
                await ctx.send(f"❌ Invalid amount for `{stone_type}`: must be a number.")
                return
            if stone_type not in ('sword', 'armor', 'acc'):
                await ctx.send(f"❌ Invalid stone type `{stone_type}`. Use `sword`, `armor`, or `acc`.")
                return
            if amount <= 0:
                await ctx.send(f"❌ Amount must be positive for `{stone_type}`.")
                return
            pairs.append((stone_type, amount))
            i += 2

        if not pairs:
            await ctx.send("❌ No valid stone types specified.")
            return

        stone_map = {
            'sword': ('Sword Enhancement Stone', CUSTOM_EMOJIS.get('sword_enhancement_stone', '💎')),
            'armor': ('Armor Enhancement Stone', CUSTOM_EMOJIS.get('armors_enhancement_stone', '💎')),
            'acc': ('Accessories Enhancement Stone', CUSTOM_EMOJIS.get('acc_enhancement_stone', '💎'))
        }

        user_id = str(target.id)

        async with self.bot.db_pool.acquire() as conn:
            for stone_type, amount in pairs:
                stone_name, emoji = stone_map[stone_type]
                stone_id = await conn.fetchval("SELECT item_id FROM shop_items WHERE name = $1", stone_name)
                if not stone_id:
                    await ctx.send(f"❌ {stone_name} not found in shop. Run the SQL to add it first.")
                    return

                await conn.execute("""
                    INSERT INTO user_materials (user_id, material_id, quantity)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id, material_id) DO UPDATE
                    SET quantity = user_materials.quantity + $3
                """, user_id, stone_id, amount)

        # Build DM message
        dm_lines = []
        for stone_type, amount in pairs:
            name, emoji = stone_map[stone_type]
            dm_lines.append(f"{amount} {emoji} {name}")

        dm_text = " and ".join(dm_lines)
        dm_embed = discord.Embed(
            title="🎁 You received an item!",
            description=f"**{ctx.author.display_name}** gave you {dm_text}!",
            color=discord.Color.blue()
        )

        try:
            await target.send(embed=dm_embed)
        except discord.Forbidden:
            print(f"Could not DM {target} about stone gift.")
        except Exception as e:
            print(f"Error sending DM to {target}: {e}")

        # Build confirmation message
        confirm_lines = []
        for stone_type, amount in pairs:
            name, emoji = stone_map[stone_type]
            confirm_lines.append(f"{amount} {emoji} {name}")
        confirm_text = ", ".join(confirm_lines)
        await ctx.send(f"✅ Added {confirm_text} to {target.mention}'s inventory.")

    @commands.command(name='givepotions')
    @commands.has_permissions(administrator=True)
    async def give_potion(self, ctx, *args):
        """
        Give potions to a user. Admins only.
        Usage: !!givepotion [@user] <hp|energy> <amount> [hp|energy amount ...]
        Example: !!givepotion @purr404 hp 10 energy 20
        """
        if not args:
            await ctx.send("❌ Usage: `!!givepotion [@user] <hp|energy> <amount> [hp|energy amount ...]`")
            return

        # Determine if first argument is a member
        target = None
        start_idx = 0
        if len(args) >= 1 and isinstance(ctx.message.mentions, list) and ctx.message.mentions:
            # If there's a mention, the first arg is the member
            target = ctx.message.mentions[0]
            start_idx = 1
        else:
            target = ctx.author
            start_idx = 0

        # Parse remaining args as type‑amount pairs
        pairs = []
        i = start_idx
        while i < len(args):
            if i + 1 >= len(args):
                await ctx.send("❌ Missing amount for potion type `{}`.".format(args[i]))
                return
            potion_type = args[i].lower()
            try:
                amount = int(args[i+1])
            except ValueError:
                await ctx.send(f"❌ Invalid amount for `{potion_type}`: must be a number.")
                return
            if potion_type not in ('hp', 'energy'):
                await ctx.send(f"❌ Invalid potion type `{potion_type}`. Use `hp` or `energy`.")
                return
            if amount <= 0:
                await ctx.send(f"❌ Amount must be positive for `{potion_type}`.")
                return
            pairs.append((potion_type, amount))
            i += 2

        if not pairs:
            await ctx.send("❌ No valid potion types specified.")
            return

        potion_map = {
            'hp': ('HP Potion', CUSTOM_EMOJIS.get('hp_potion', '💚')),
            'energy': ('Energy Potion', CUSTOM_EMOJIS.get('energy_potion', '⚡'))
        }

        user_id = str(target.id)

        async with self.bot.db_pool.acquire() as conn:
            for potion_type, amount in pairs:
                potion_name, emoji = potion_map[potion_type]
                potion_id = await conn.fetchval("SELECT item_id FROM shop_items WHERE name = $1", potion_name)
                if not potion_id:
                    await ctx.send(f"❌ {potion_name} not found in shop. Run the SQL to add it first.")
                    return

                await conn.execute("""
                    INSERT INTO user_materials (user_id, material_id, quantity)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id, material_id) DO UPDATE
                    SET quantity = user_materials.quantity + $3
                """, user_id, potion_id, amount)

        # Build DM message
        dm_lines = []
        for potion_type, amount in pairs:
            name, emoji = potion_map[potion_type]
            dm_lines.append(f"{amount} {emoji} {name}")

        dm_text = " and ".join(dm_lines)
        dm_embed = discord.Embed(
            title="🎁 You received an item!",
            description=f"**{ctx.author.display_name}** sent you {dm_text}!",
            color=discord.Color.green()
        )

        try:
            await target.send(embed=dm_embed)
        except discord.Forbidden:
            print(f"Could not DM {target} about potion gift.")
        except Exception as e:
            print(f"Error sending DM to {target}: {e}")

        # Build confirmation message
        confirm_lines = []
        for potion_type, amount in pairs:
            name, emoji = potion_map[potion_type]
            confirm_lines.append(f"{amount} {emoji} {name}")
        confirm_text = ", ".join(confirm_lines)
        await ctx.send(f"✅ Added {confirm_text} to {target.mention}'s inventory.")

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
            title=f"{CUSTOM_EMOJIS.get('pickaxe', '⛏️')} Supplies",
            description="Purchase tools and consumables in batches!",
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
            potions = await conn.fetch("""
                SELECT item_id, name, description, price
                FROM shop_items
                WHERE type = 'potion'
                ORDER BY name
            """)

        if pickaxes:
            for pick in pickaxes:
                button = discord.ui.Button(
                    label=f"⛏️ {pick['name']} – {pick['price']}g",
                    style=discord.ButtonStyle.primary,
                    custom_id=f"shop_buy_{pick['item_id']}"
                )
                view.add_item(button)

        if potions:
            for potion in potions:
                name_lower = potion['name'].lower()
                if 'hp potion' in name_lower:
                    emoji = CUSTOM_EMOJIS.get('hp_potion', '🧪')
                else:
                    emoji = CUSTOM_EMOJIS.get('energy_potion', '⚡')
                batch_price = potion['price'] * 10
                button = discord.ui.Button(
                    label=f"x10 {potion['name']} – {batch_price}g",
                    emoji=emoji,
                    style=discord.ButtonStyle.primary,
                    custom_id=f"buy_potion_10_{potion['item_id']}"
                )
                view.add_item(button)

        back = discord.ui.Button(
            label="◀ Back",
            style=discord.ButtonStyle.secondary,
            custom_id="shop_back_to_main"
        )
        view.add_item(back)

        await interaction.response.edit_message(embed=embed, view=view)


    async def show_pets(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{CUSTOM_EMOJIS.get('paw', '🐾')} Pets",
            description="Purchase a Pet Box to receive a random companion! Each pet grants unique bonuses and **+1 Energy** when equipped.",
            color=discord.Color.purple()
        )
        view = discord.ui.View(timeout=300)

        async with self.bot.db_pool.acquire() as conn:
            pet_boxes = await conn.fetch("""
                SELECT item_id, name, description, price
                FROM shop_items
                WHERE type = 'random_pet_box'
                ORDER BY price ASC
            """)

        if pet_boxes:
            for box in pet_boxes:
                button = discord.ui.Button(
                    label=f"{box['name']} – {box['price']}g",
                    emoji=CUSTOM_EMOJIS.get('pet_box', '📦'),
                    style=discord.ButtonStyle.primary,
                    custom_id=f"shop_buy_{box['item_id']}"
                )
                view.add_item(button)
        else:
            embed.description = "No pet boxes available yet."

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

            stats = (
                f"⚔️ **ATK:** {attack}\n"
                f"🩸 **Bleed Chance:** {bleed_chance}%\n"
                f"⚡ **Crit Chance:** {crit_chance}%\n"
                f"💥 **Crit Damage:** {crit_damage}%"
            ) 

            combined_description = f"{stats}\n\n*{description}*"
            weapon_embed = discord.Embed(
                title=f"{get_item_emoji(weapon_name, 'weapon')} **{weapon_name}**",
                description=combined_description,
                color=discord.Color.red()
            )

            if weapon_name in SWORD_SKILLS:
                skill = SWORD_SKILLS[weapon_name]
                mult = skill['base']  # level 1 multiplier
                weapon_embed.add_field(name="Skill", value=f"{skill['name']} (Lv.1, {mult}x ATK)", inline=False)
                weapon_embed.add_field(name="Effect", value=skill['effect'], inline=False)
          
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

            description = f"A sturdy {piece} from the **{set_data['name']}** set."
            if reflect:
                description += f" Reflects {reflect}% damage."
            description += f"\n\n*Complete the {set_data['name']} set (all 4 pieces) to activate bonus stats!*"

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

            stats = f"🛡️ **DEF:** {defense}\n❤️ **HP:** +{hp_bonus}"
            if reflect:
                stats += f"\n{CUSTOM_EMOJIS['reflect']} **Reflect:** {reflect}%"

            combined_description = f"{stats}\n\n*{description}*"
            armor_embed = discord.Embed(
                title=f"{emoji} **{armor_name}**",
                description=combined_description,
                color=set_data['color']
            )
            
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

            slot = None
           
            bonus_value = random.randint(set_data['range'][0], set_data['range'][1])
            emoji_key = emoji_map.get((set_name, piece), 'ring_1')
            emoji = CUSTOM_EMOJIS.get(emoji_key, self.RING_UNICODE)
            accessory_name = f"{set_data['name']} {piece.capitalize()}"

            description = f"A {piece} from the **{set_data['name']}** set, granting {set_data['stat'].upper()} bonus."
            description += f"\n\n*Complete the {set_data['name']} set (2 rings, 2 earrings, 1 pendant) to activate bonus stats!*"

            async with self.bot.db_pool.acquire() as conn:
            # Insert into accessory_types using the CATEGORY (piece), not a specific slot
                acc_type = await conn.fetchrow("""
                    INSERT INTO accessory_types (name, slot, bonus_stat, bonus_value, set_name, description)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING accessory_id
                """, accessory_name, piece, set_data['stat'], bonus_value, set_name, description)   # <-- piece, not slot

                purchase_id = await conn.fetchval("""
                    INSERT INTO user_purchases (user_id, item_id, price_paid, expires_at)
                    VALUES ($1, $2, $3, $4)
                    RETURNING purchase_id
                """, user_id, item['item_id'], item['price'], now + timedelta(days=7))

                # Insert into user_accessories with slot = NULL and equipped = FALSE explicitly
                await conn.execute("""
                    INSERT INTO user_accessories (user_id, accessory_id, bonus_value, slot, set_name, purchase_id, equipped)
                    VALUES ($1, $2, $3, $4, $5, $6, FALSE)
                """, user_id, acc_type['accessory_id'], bonus_value, slot, set_name, purchase_id)

            box_embed = discord.Embed(
                title="📦 Random Accessory Box",
                description=f"{self.TREASURE_UNICODE} Opening box...\nYou received: **{accessory_name}**",
                color=set_data['color']
            )
            await interaction.followup.send(embed=box_embed, ephemeral=True)
            
            stat_emoji = '⚔️' if set_data['stat'] == 'atk' else '🛡️'
            stats = f"{stat_emoji} **{set_data['stat'].upper()}:** +{bonus_value}\n📌 **Slot:** {piece.capitalize()} (unequipped)"

            combined_description = f"{stats}\n\n*{description}*"
            acc_embed = discord.Embed(
                title=f"{emoji} **{accessory_name}**",
                description=combined_description,
                color=set_data['color']
            )
            
            
            await interaction.followup.send(embed=acc_embed, ephemeral=True)

            await self.send_shop_log(interaction.guild, interaction.user, item['name'], item['price'], balance['gems'] - item['price'])
            return

        # ========== RANDOM PET BOX ==========
        if item['type'] == 'random_pet_box':
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

            # Fetch all pet types (excluding Lilia Maid for now)
            async with self.bot.db_pool.acquire() as conn:
                pets = await conn.fetch("""
                    SELECT pet_id, name FROM pet_types
                    WHERE name IN ('Baby Fox', 'Baby Tiger', 'Baby Purr')
                """)
                if not pets:
                    await interaction.followup.send("❌ No pets available in database.", ephemeral=True)
                    return
                chosen = random.choice(pets)
                pet_id = chosen['pet_id']
                pet_name = chosen['name']

                # Insert into user_pets (unequipped by default)
                await conn.execute("""
                    INSERT INTO user_pets (user_id, pet_id, equipped)
                    VALUES ($1, $2, FALSE)
                """, user_id, pet_id)

            # Get pet emoji
            pet_emoji = get_pet_emoji(pet_name)

            # Build result embed
            embed = discord.Embed(
                title="📦 Pet Box Opened!",
                description=f"You received {pet_emoji} **{pet_name}**!",
                color=discord.Color.purple()
            )
            # Add pet stats to the embed
            async with self.bot.db_pool.acquire() as conn:
                pet_stats = await conn.fetchrow("""
                    SELECT atk_percent, def_percent, hp_percent, dodge_percent,
                           bleed_flat, burn_flat, energy_bonus
                    FROM pet_types WHERE pet_id = $1
                """, pet_id)
            if pet_stats:
                stats_lines = [
                    f"⚔️ ATK +{pet_stats['atk_percent']}%",
                    f"🛡️ DEF +{pet_stats['def_percent']}%",
                    f"❤️ HP +{pet_stats['hp_percent']}%",
                ]
                if pet_stats['dodge_percent']:
                    stats_lines.append(f"Dodge +{pet_stats['dodge_percent']}%")
                if pet_stats['bleed_flat']:
                    stats_lines.append(f"🩸 Bleed +{pet_stats['bleed_flat']}")
                if pet_stats['burn_flat']:
                    stats_lines.append(f"🔥 Burn +{pet_stats['burn_flat']}")
                if pet_stats['energy_bonus']:
                    stats_lines.append(f"Energy +{pet_stats['energy_bonus']}")
                embed.add_field(name="Stats", value="\n".join(stats_lines), inline=False)

            await interaction.followup.send(embed=embed, ephemeral=True)
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


    async def purchase_potion_batch(self, interaction: discord.Interaction, item_id: int, batch_size: int = 10):
        await interaction.response.defer(ephemeral=True)
        user_id = str(interaction.user.id)

        async with self.bot.db_pool.acquire() as conn:
            potion = await conn.fetchrow("SELECT name, price FROM shop_items WHERE item_id = $1", item_id)
            if not potion:
                await interaction.followup.send("❌ Potion not found.", ephemeral=True)
                return

        total_cost = potion['price'] * batch_size

        balance = await currency_system.get_balance(user_id)
        if balance['gems'] < total_cost:
            await interaction.followup.send(f"❌ You need {total_cost} gems. You have {balance['gems']}.", ephemeral=True)
            return

        success = await currency_system.deduct_gems(user_id, total_cost, f"Purchased {batch_size}x {potion['name']}")
        if not success:
            await interaction.followup.send("❌ Failed to deduct gems.", ephemeral=True)
            return

        async with self.bot.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO user_materials (user_id, material_id, quantity)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id, material_id) DO UPDATE
                SET quantity = user_materials.quantity + $3
            """, user_id, item_id, batch_size)

        name_lower = potion['name'].lower()
        if 'hp potion' in name_lower:
            emoji = CUSTOM_EMOJIS.get('hp_potion', '🧪')
        else:
            emoji = CUSTOM_EMOJIS.get('energy_potion', '⚡')

        await interaction.followup.send(
            f"✅ Purchased **{batch_size}x {emoji} {potion['name']}** for **{total_cost} gems**.",
            ephemeral=True
        )

        # Log to shop logs
        await self.send_shop_log(interaction.guild, interaction.user, f"{batch_size}x {potion['name']}", total_cost, balance['gems'] - total_cost)

        

    # -------------------------------------------------------------------------
    # SECRET SHOP (Treasure Carriage booking)
    # -------------------------------------------------------------------------
    async def secret_shop_button(self, interaction: discord.Interaction, purchase_id: int):
        """Handle the Continue button after buying a Treasure Carriage."""
        try:
            print(f"[DEBUG] secret_shop_button called for purchase_id: {purchase_id}")

            # 🔥 DEFER FIRST – ALWAYS
            await interaction.response.defer(ephemeral=True)
            print("[DEBUG] Defer successful")

            # Validate purchase_id (should be int, but safeguard)
            if not isinstance(purchase_id, int):
                await interaction.followup.send("❌ Invalid ticket ID.", ephemeral=True)
                return

            print("[DEBUG] Querying database for purchase...")
            async with self.bot.db_pool.acquire() as conn:
                purchase = await conn.fetchrow(
                    "SELECT * FROM user_purchases WHERE purchase_id = $1 AND used = FALSE",
                    purchase_id
                )

            if not purchase:
                print("[DEBUG] Purchase not found or already used")
                await interaction.followup.send("❌ This ticket has already been used or does not exist.", ephemeral=True)
                return

            print("[DEBUG] Purchase found, attempting to send DM...")
            try:
                await interaction.user.send(
                    "**Treasure Carriage Booking**\nPlease reply with your **in‑game name** (IGN)."
                )
                print("[DEBUG] DM sent successfully")
            except discord.Forbidden:
                print("[DEBUG] Cannot DM user (Forbidden)")
                await interaction.followup.send(
                    "❌ I can't DM you. Please enable DMs from server members and try again.",
                    ephemeral=True
                )
                return

            # Store session
            self.booking_sessions[interaction.user.id] = {
                "purchase_id": purchase_id,
                "step": "ign"
            }
            print(f"[DEBUG] Session stored for user {interaction.user.id}")

            await interaction.followup.send("📨 Check your DM to continue.", ephemeral=True)
            print("[DEBUG] Followup sent successfully")

        except Exception as e:
            # Log the full error
            import traceback
            print(f"❌❌❌ UNHANDLED EXCEPTION in secret_shop_button: {e}")
            traceback.print_exc()

            # Attempt to notify the user
            try:
                # If interaction hasn't been responded to yet, send a message
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ An unexpected error occurred. Please contact an admin.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ An unexpected error occurred. Please contact an admin.", ephemeral=True)
            except Exception as followup_error:
                print(f"❌ Could not send followup: {followup_error}")

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
            row = await conn.fetchrow("SELECT hp, respawn_at FROM player_stats WHERE user_id = $1", user_id)
        if row and row['hp'] <= 0:
            respawn = row['respawn_at']
            if respawn:
                if respawn.tzinfo is None:
                    respawn = respawn.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                remaining = respawn - now
                if remaining.total_seconds() <= 0:
                    msg = "You are dead and cannot access your inventory. (respawn time already passed)"
                else:
                    hours = int(remaining.total_seconds() // 3600)
                    minutes = int((remaining.total_seconds() % 3600) // 60)
                    if hours > 0:
                        time_str = f"{hours}h {minutes}m"
                    else:
                        time_str = f"{minutes}m"
                    msg = f"You are dead and cannot access your inventory. Revives in {time_str}."
            else:
                msg = "You are dead and cannot access your inventory."
            await ctx.send(msg)
            return

        async with self.bot.db_pool.acquire() as conn:
            weapons = await conn.fetch("""
                SELECT uw.id, COALESCE(si.name, uw.generated_name) as name,
                       uw.attack, uw.equipped, uw.description,
                       COALESCE(si.image_url, uw.image_url) as image_url,
                       r.color as rarity_color,
                       uw.upgrade_level
                FROM user_weapons uw
                LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                LEFT JOIN weapon_variants v ON uw.variant_id = v.variant_id
                LEFT JOIN rarities r ON v.rarity_id = r.rarity_id
                WHERE uw.user_id = $1
                ORDER BY uw.equipped DESC, uw.purchased_at DESC
            """, user_id)

            armor = await conn.fetch("""
                SELECT ua.id, at.name, ua.defense, ua.equipped, at.slot,
                       at.image_url, at.description, r.color as rarity_color,
                       ua.upgrade_level
                FROM user_armor ua
                JOIN armor_types at ON ua.armor_id = at.armor_id
                LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                WHERE ua.user_id = $1
                ORDER BY ua.equipped DESC, ua.purchased_at DESC
            """, user_id)

            accessories = await conn.fetch("""
                SELECT ua.id, at.name, ua.bonus_value, at.bonus_stat,
                       ua.equipped, ua.slot, at.image_url, at.description,
                       r.color as rarity_color,
                       ua.upgrade_level
                FROM user_accessories ua
                JOIN accessory_types at ON ua.accessory_id = at.accessory_id
                LEFT JOIN rarities r ON at.rarity_id = r.rarity_id
                WHERE ua.user_id = $1
                ORDER BY ua.equipped DESC, ua.purchased_at DESC
            """, user_id)

            materials = await conn.fetch("""
                SELECT um.material_id, si.name, um.quantity, si.description
                FROM user_materials um
                JOIN shop_items si ON um.material_id = si.item_id
                WHERE um.user_id = $1 AND um.quantity > 0
                ORDER BY si.name
            """, user_id)
        balance = await currency_system.get_balance(user_id)

        inventory_data = {
            'weapons': [dict(w) for w in weapons],
            'armor': [dict(a) for a in armor],
            'accessories': [dict(a) for a in accessories],
            'materials': [dict(m) for m in materials],
            'gems': balance['gems']
        }

        view = InventoryView(user_id, inventory_data, self)
        await ctx.send(embed=view.create_main_embed(), view=view)





# CULLING GAME 

class CullingGame(commands.Cog):
    def __init__(self, bot, currency_system):
        self.bot = bot
        self.currency = currency_system
        self.mining_channel = None
        self.mining_message = None


    async def cog_load(self):
        """Start background tasks after the cog is loaded."""
        self.energy_regen.start()
        self.check_max_mining.start()


    async def load_mining_messages(self, guild_id: int):
        """Reattach the mining view after restart."""
        print(f"🔄 load_mining_messages for guild {guild_id}: started")
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
        print(f"🔄 Found channel #{channel.name}, fetching message {row['message_id']}")
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
                print(f"🧹 Deleted mining config for guild {guild_id}")

    def cog_unload(self):
        self.energy_regen.cancel()
        self.check_max_mining.cancel()

# ------------------------------------------------------------------
    # Energy Regen Task
    # ------------------------------------------------------------------
    @tasks.loop(hours=1)
    async def energy_regen(self):
        try:
            async with self.bot.db_pool.acquire() as conn:
                alive = await conn.fetch("SELECT user_id FROM player_stats WHERE hp > 0")
            now = datetime.utcnow()
            for player in alive:
                user_id = player['user_id']
                stats = await get_player_stats(user_id)
                if stats['energy'] < stats['max_energy']:
                    async with self.bot.db_pool.acquire() as conn2:
                        last = await conn2.fetchval("SELECT last_energy_regen FROM player_stats WHERE user_id = $1", user_id)
                    if last.tzinfo is not None:
                        last = last.replace(tzinfo=None)
                    if (now - last) >= timedelta(hours=1):
                        new_energy = stats['energy'] + 1
                        async with self.bot.db_pool.acquire() as conn3:
                            await conn3.execute("""
                                UPDATE player_stats
                                SET energy = $1, last_energy_regen = $2
                                WHERE user_id = $3
                            """, new_energy, now, user_id)
            print("energy_regen tick")
        except Exception as e:
            print(f"❌ energy_regen error: {e}")
            traceback.print_exc()

    @energy_regen.before_loop
    async def before_energy_regen(self):
        await self.bot.wait_until_ready()
        while self.bot.db_pool is None:
            await asyncio.sleep(1)


    @tasks.loop(minutes=30)
    async def check_max_mining(self):
        async with self.bot.db_pool.acquire() as conn:
            miners = await conn.fetch("""
                SELECT user_id, mining_start, stolen_gems,
                       stolen_sword_stones, stolen_armor_stones, stolen_acc_stones
                FROM player_stats 
                WHERE mining_start IS NOT NULL
            """)
            now = datetime.utcnow()
            for miner in miners:
                user_id = miner['user_id']
                start = miner['mining_start']
                if start.tzinfo is not None:
                    start = start.replace(tzinfo=None)
                minutes_mined = int((now - start).total_seconds() / 60)
                if minutes_mined >= 720:
                    # Gems
                    gems_earned = (minutes_mined * 5) // 6
                    gems_earned = min(gems_earned, 600)
                    stolen_gems = miner['stolen_gems'] or 0
                    net_gems = max(0, gems_earned - stolen_gems)

                    # Stones earned (total)
                    total_stones = self.generate_stones_for_minutes(720)  # full 12h
                    stolen_sword = miner['stolen_sword_stones'] or 0
                    stolen_armor = miner['stolen_armor_stones'] or 0
                    stolen_acc   = miner['stolen_acc_stones'] or 0

                    net_sword = max(0, total_stones['sword'] - stolen_sword)
                    net_armor = max(0, total_stones['armor'] - stolen_armor)
                    net_acc   = max(0, total_stones['acc'] - stolen_acc)

                    # Award gems
                    if net_gems > 0:
                        await self.currency.add_gems(user_id, net_gems, "Mining completed (12h max)")

                    # Award stones (only net stones)
                    stone_ids = {}
                    for name, key in [('Sword Enhancement Stone','sword'), ('Armor Enhancement Stone','armor'), ('Accessories Enhancement Stone','acc')]:
                        sid = await conn.fetchval("SELECT item_id FROM shop_items WHERE name = $1", name)
                        stone_ids[key] = sid

                    if net_sword > 0 and stone_ids['sword']:
                        await conn.execute("""
                            INSERT INTO user_materials (user_id, material_id, quantity)
                            VALUES ($1, $2, $3)
                            ON CONFLICT (user_id, material_id) DO UPDATE
                            SET quantity = user_materials.quantity + $3
                        """, user_id, stone_ids['sword'], net_sword)
                    if net_armor > 0 and stone_ids['armor']:
                        await conn.execute("""
                            INSERT INTO user_materials (user_id, material_id, quantity)
                            VALUES ($1, $2, $3)
                            ON CONFLICT (user_id, material_id) DO UPDATE
                            SET quantity = user_materials.quantity + $3
                        """, user_id, stone_ids['armor'], net_armor)
                    if net_acc > 0 and stone_ids['acc']:
                        await conn.execute("""
                            INSERT INTO user_materials (user_id, material_id, quantity)
                            VALUES ($1, $2, $3)
                            ON CONFLICT (user_id, material_id) DO UPDATE
                            SET quantity = user_materials.quantity + $3
                        """, user_id, stone_ids['acc'], net_acc)

                    # Reset mining
                    await conn.execute("""
                        UPDATE player_stats 
                        SET mining_start = NULL, stolen_gems = 0,
                            stolen_sword_stones = 0, stolen_armor_stones = 0, stolen_acc_stones = 0
                        WHERE user_id = $1
                    """, user_id)

                    # DM the user – PASS TOTAL STONES, NOT NET
                    await self.send_mining_complete_dm(
                        int(user_id),
                        net_gems,
                        stolen_gems,
                        {'sword': net_sword, 'armor': net_armor, 'acc': net_acc},
                        {'sword': stolen_sword, 'armor': stolen_armor, 'acc': stolen_acc}
                    )


    @check_max_mining.before_loop
    async def before_check_max_mining(self):
        await self.bot.wait_until_ready()
        while self.bot.db_pool is None:
            await asyncio.sleep(1)


    def generate_stones_for_minutes(self, minutes: int) -> dict:
        """
        Returns dict with keys 'sword', 'armor', 'acc' and total stones earned
        for the given minutes (as if no theft occurred).
        """
        stone_names = ['Sword Enhancement Stone', 'Armor Enhancement Stone', 'Accessories Enhancement Stone']
        stone_keys = ['sword', 'armor', 'acc']
        total = {key: 0 for key in stone_keys}
        intervals = minutes // 10
        for _ in range(intervals):
            if random.random() < 0.2:
                idx = random.randint(0, 2)
                qty = random.randint(1, 3)
                total[stone_keys[idx]] += qty
        return total



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



    async def send_mining_complete_dm(self, user_id: int, gems_earned: int, gems_stolen: int,
                                      stone_drops: dict, stolen_stones: dict):
        """
        Send a DM when mining reaches 12 hours.
        - stone_drops: dict with keys 'sword', 'armor', 'acc' – net stones the user keeps.
        - stolen_stones: dict with same keys – stones stolen from the user.
        """
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

        # --- Resources Mined section ---
        mined_lines = []
        if gems_earned > 0:
            mined_lines.append(f"{gems_earned} 💎")
        if stone_drops.get('sword', 0) > 0:
            mined_lines.append(f"{stone_drops['sword']} {CUSTOM_EMOJIS.get('sword_enhancement_stone', '💎')}")
        if stone_drops.get('armor', 0) > 0:
            mined_lines.append(f"{stone_drops['armor']} {CUSTOM_EMOJIS.get('armors_enhancement_stone', '💎')}")
        if stone_drops.get('acc', 0) > 0:
            mined_lines.append(f"{stone_drops['acc']} {CUSTOM_EMOJIS.get('acc_enhancement_stone', '💎')}")

        if mined_lines:
            embed.add_field(name="**Resources Mined**", value="\n".join(mined_lines), inline=False)

        # --- Resources Stolen section ---
        stolen_lines = []
        if gems_stolen > 0:
            stolen_lines.append(f"{gems_stolen} 💎")
        if stolen_stones.get('sword', 0) > 0:
            stolen_lines.append(f"{stolen_stones['sword']} {CUSTOM_EMOJIS.get('sword_enhancement_stone', '💎')}")
        if stolen_stones.get('armor', 0) > 0:
            stolen_lines.append(f"{stolen_stones['armor']} {CUSTOM_EMOJIS.get('armors_enhancement_stone', '💎')}")
        if stolen_stones.get('acc', 0) > 0:
            stolen_lines.append(f"{stolen_stones['acc']} {CUSTOM_EMOJIS.get('acc_enhancement_stone', '💎')}")

        if stolen_lines:
            embed.add_field(name="**Resources Stolen**", value="\n".join(stolen_lines), inline=False)

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
                SET mining_start = $1,
                    stolen_gems = 0,
                    stolen_sword_stones = 0,
                    stolen_armor_stones = 0,
                    stolen_acc_stones = 0
                WHERE user_id = $2
            """, now, user_id)

        return "✅ You have started mining! You will earn gems over time."

    async def stop_mining_for_user(self, user_id: str) -> str:
        async with self.bot.db_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT mining_start, stolen_gems,
                       stolen_sword_stones, stolen_armor_stones, stolen_acc_stones
                FROM player_stats WHERE user_id = $1
            """, user_id)
            if not row or not row['mining_start']:
                return "❌ You are not mining."

            start = row['mining_start']
            if start.tzinfo is not None:
                start = start.replace(tzinfo=None)
            now = datetime.utcnow()
            minutes_mined = int((now - start).total_seconds() / 60)
            minutes_mined = min(minutes_mined, 12 * 60)

            # Gems
            gems_earned = (minutes_mined * 5) // 6
            stolen_gems = row['stolen_gems'] or 0
            net_gems = max(0, gems_earned - stolen_gems)

            # Stones earned total (no theft applied yet)
            total_stones = self.generate_stones_for_minutes(minutes_mined)

            # Stolen stones per type
            stolen_sword = row['stolen_sword_stones'] or 0
            stolen_armor = row['stolen_armor_stones'] or 0
            stolen_acc   = row['stolen_acc_stones'] or 0

            net_sword = max(0, total_stones['sword'] - stolen_sword)
            net_armor = max(0, total_stones['armor'] - stolen_armor)
            net_acc   = max(0, total_stones['acc'] - stolen_acc)

            # Award gems
            if net_gems > 0:
                await self.currency.add_gems(user_id, net_gems, "Mining reward")

            # Award stones – fetch item IDs once
            stone_ids = {}
            for name, key in [('Sword Enhancement Stone','sword'), ('Armor Enhancement Stone','armor'), ('Accessories Enhancement Stone','acc')]:
                sid = await conn.fetchval("SELECT item_id FROM shop_items WHERE name = $1", name)
                stone_ids[key] = sid

            stone_drops_final = {}  # for result message
            if net_sword > 0 and stone_ids['sword']:
                await conn.execute("""
                    INSERT INTO user_materials (user_id, material_id, quantity)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id, material_id) DO UPDATE
                    SET quantity = user_materials.quantity + $3
                """, user_id, stone_ids['sword'], net_sword)
                stone_drops_final['Sword Enhancement Stone'] = net_sword
            if net_armor > 0 and stone_ids['armor']:
                await conn.execute("""
                    INSERT INTO user_materials (user_id, material_id, quantity)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id, material_id) DO UPDATE
                    SET quantity = user_materials.quantity + $3
                """, user_id, stone_ids['armor'], net_armor)
                stone_drops_final['Armor Enhancement Stone'] = net_armor
            if net_acc > 0 and stone_ids['acc']:
                await conn.execute("""
                    INSERT INTO user_materials (user_id, material_id, quantity)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id, material_id) DO UPDATE
                    SET quantity = user_materials.quantity + $3
                """, user_id, stone_ids['acc'], net_acc)
                stone_drops_final['Accessories Enhancement Stone'] = net_acc

            # Reset mining state
            await conn.execute("""
                UPDATE player_stats
                SET mining_start = NULL, stolen_gems = 0,
                    stolen_sword_stones = 0, stolen_armor_stones = 0, stolen_acc_stones = 0
                WHERE user_id = $1
            """, user_id)

        # Build result message
        result = f"✅ You mined for **{minutes_mined} minutes** and earned **{net_gems} gems**."
        if stone_drops_final:
            lines = []
            for name, qty in stone_drops_final.items():
                if 'Sword' in name:
                    emoji = CUSTOM_EMOJIS.get('sword_enhancement_stone', '💎')
                elif 'Armor' in name:
                    emoji = CUSTOM_EMOJIS.get('armors_enhancement_stone', '💎')
                else:
                    emoji = CUSTOM_EMOJIS.get('acc_enhancement_stone', '💎')
                lines.append(f"{emoji} {name}: {qty}")
            result += "\n\nYou also found:\n" + "\n".join(lines)
        if stolen_gems > 0:
            result += f"\n\n😭 **Stolen Gems:** {stolen_gems}"
        if stolen_sword > 0 or stolen_armor > 0 or stolen_acc > 0:
            stolen_lines = []
            if stolen_sword > 0:
                stolen_lines.append(f"{CUSTOM_EMOJIS.get('sword_enhancement_stone', '💎')} Sword: {stolen_sword}")
            if stolen_armor > 0:
                stolen_lines.append(f"{CUSTOM_EMOJIS.get('armors_enhancement_stone', '💎')} Armor: {stolen_armor}")
            if stolen_acc > 0:
                stolen_lines.append(f"{CUSTOM_EMOJIS.get('acc_enhancement_stone', '💎')} Accessory: {stolen_acc}")
            result += "\n\n😭 **Stolen Stones:**\n" + "\n".join(stolen_lines)
        return result

    async def plunder_user(self, attacker_id: str, defender_id: str, guild: discord.Guild = None) -> str:
        if attacker_id == defender_id:
            return "❌ You cannot plunder yourself."

        if not await self.has_weapon(attacker_id):
            return "❌ You don't have any weapon! Buy one from the shop first."
        if not await self.has_weapon(defender_id):
            return "❌ That user doesn't have any weapon and cannot be plundered."

        await self.ensure_player_stats(attacker_id)
        await self.ensure_player_stats(defender_id)

        async with self.bot.db_pool.acquire() as conn:
            # Attacker energy & daily limits
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

            # Defender mining info
            defender = await conn.fetchrow("""
                SELECT mining_start, stolen_gems,
                       stolen_sword_stones, stolen_armor_stones, stolen_acc_stones
                FROM player_stats WHERE user_id = $1
            """, defender_id)
            if not defender or not defender['mining_start']:
                return "❌ That user is not mining."

            start = defender['mining_start']
            if start.tzinfo is not None:
                start = start.replace(tzinfo=None)
            now = datetime.utcnow()
            minutes_mined = int((now - start).total_seconds() / 60)

            # 2‑hour protection
            if minutes_mined < 120:
                return "❌ That user has been mining for less than 2 hours and is protected from plunder."

            # Gems available
            gems_earned = (minutes_mined * 5) // 6
            stolen_gems = defender['stolen_gems'] or 0
            gems_available = max(0, gems_earned - stolen_gems)
            if gems_available <= 0:
                gems_steal = 0
            else:
                gems_steal = int(gems_available * 0.3)
                if gems_steal <= 0:
                    gems_steal = 1

            # Stones available (per type)
            total_stones = self.generate_stones_for_minutes(minutes_mined)
            stolen_sword = defender['stolen_sword_stones'] or 0
            stolen_armor = defender['stolen_armor_stones'] or 0
            stolen_acc   = defender['stolen_acc_stones'] or 0

            sword_available = max(0, total_stones['sword'] - stolen_sword)
            armor_available = max(0, total_stones['armor'] - stolen_armor)
            acc_available   = max(0, total_stones['acc'] - stolen_acc)

            stone_steals = {}
            if sword_available > 0:
                stone_steals['sword'] = max(1, int(sword_available * 0.3))
            if armor_available > 0:
                stone_steals['armor'] = max(1, int(armor_available * 0.3))
            if acc_available > 0:
                stone_steals['acc'] = max(1, int(acc_available * 0.3))

            # If nothing to steal, abort
            if gems_steal == 0 and not stone_steals:
                return "❌ That user has nothing left to plunder."

            # --- Update defender's stolen counters ---
            new_stolen_gems = stolen_gems + gems_steal
            new_stolen_sword = stolen_sword + stone_steals.get('sword', 0)
            new_stolen_armor = stolen_armor + stone_steals.get('armor', 0)
            new_stolen_acc   = stolen_acc   + stone_steals.get('acc', 0)

            await conn.execute("""
                UPDATE player_stats
                SET stolen_gems = $1,
                    stolen_sword_stones = $2,
                    stolen_armor_stones = $3,
                    stolen_acc_stones = $4
                WHERE user_id = $5
            """, new_stolen_gems, new_stolen_sword, new_stolen_armor, new_stolen_acc, defender_id)

            # --- Give stolen gems to attacker ---
            if gems_steal > 0:
                await self.currency.add_gems(attacker_id, gems_steal, f"Plundered from <@{defender_id}>")

            # --- Give stolen stones to attacker ---
            stone_ids = {}
            for name, key in [('Sword Enhancement Stone','sword'), ('Armor Enhancement Stone','armor'), ('Accessories Enhancement Stone','acc')]:
                sid = await conn.fetchval("SELECT item_id FROM shop_items WHERE name = $1", name)
                stone_ids[key] = sid

            for key, qty in stone_steals.items():
                if qty > 0 and stone_ids[key]:
                    await conn.execute("""
                        INSERT INTO user_materials (user_id, material_id, quantity)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (user_id, material_id) DO UPDATE
                        SET quantity = user_materials.quantity + $3
                    """, attacker_id, stone_ids[key], qty)

            # --- Deduct energy and increment plunder count ---
            await conn.execute("""
                UPDATE player_stats
                SET energy = energy - 1, plunder_count = plunder_count + 1
                WHERE user_id = $1
            """, attacker_id)

        # --- Notifications ---
        attacker_name = (await self.bot.fetch_user(int(attacker_id))).name
        defender_user = self.bot.get_user(int(defender_id))
        if defender_user:
            try:
                embed = discord.Embed(
                    title="😭 You've been plundered!",
                    description=f"**{attacker_name}** plundered you.",
                    color=discord.Color.red()
                )
                stolen_lines = []
                if gems_steal > 0:
                    stolen_lines.append(f"{gems_steal} 💎")
                if 'sword' in stone_steals:
                    stolen_lines.append(f"{stone_steals['sword']} {CUSTOM_EMOJIS.get('sword_enhancement_stone', '💎')}")
                if 'armor' in stone_steals:
                    stolen_lines.append(f"{stone_steals['armor']} {CUSTOM_EMOJIS.get('armors_enhancement_stone', '💎')}")
                if 'acc' in stone_steals:
                    stolen_lines.append(f"{stone_steals['acc']} {CUSTOM_EMOJIS.get('acc_enhancement_stone', '💎')}")

                if stolen_lines:
                    embed.add_field(name="**Stolen**", value="\n".join(stolen_lines), inline=False)
                else:
                    embed.add_field(name="**Stolen**", value="Nothing was stolen!", inline=False)

                await defender_user.send(embed=embed)
            except:
                pass

        # --- Public announcement (ONLY in #global-chat) ---
        if guild:
            channel = discord.utils.get(guild.text_channels, name="🌍global-chat")
            if channel:
                attacker = guild.get_member(int(attacker_id))
                defender = guild.get_member(int(defender_id))
                if attacker and defender:
                    public_parts = []
                    if gems_steal > 0:
                        public_parts.append(f"{gems_steal} 💎")
                    if 'sword' in stone_steals:
                        sword_emoji = CUSTOM_EMOJIS.get('sword_enhancement_stone', '💎')
                        public_parts.append(f"{stone_steals['sword']} {sword_emoji}")
                    if 'armor' in stone_steals:
                        armor_emoji = CUSTOM_EMOJIS.get('armors_enhancement_stone', '💎')
                        public_parts.append(f"{stone_steals['armor']} {armor_emoji}")
                    if 'acc' in stone_steals:
                        acc_emoji = CUSTOM_EMOJIS.get('acc_enhancement_stone', '💎')
                        public_parts.append(f"{stone_steals['acc']} {acc_emoji}")

                    if public_parts:
                        message = f"{attacker.mention} plundered {defender.mention} and stole " + ", ".join(public_parts) + "!"
                    else:
                        message = f"{attacker.mention} plundered {defender.mention} and stole nothing!"
                    await channel.send(message)

        # Return message to the attacker (ephemeral)
        result_parts = []
        if gems_steal > 0:
            result_parts.append(f"{gems_steal} 💎")
        if 'sword' in stone_steals:
            sword_emoji = CUSTOM_EMOJIS.get('sword_enhancement_stone', '💎')
            result_parts.append(f"{stone_steals['sword']} {sword_emoji}")
        if 'armor' in stone_steals:
            armor_emoji = CUSTOM_EMOJIS.get('armors_enhancement_stone', '💎')
            result_parts.append(f"{stone_steals['armor']} {armor_emoji}")
        if 'acc' in stone_steals:
            acc_emoji = CUSTOM_EMOJIS.get('acc_enhancement_stone', '💎')
            result_parts.append(f"{stone_steals['acc']} {acc_emoji}")

        if result_parts:
            result = f"You plundered " + ", ".join(result_parts) + f" from <@{defender_id}>!"
        else:
            result = "❌ You stole nothing (shouldn't happen)."
        return result




@bot.command(name='attack')
async def attack(ctx, target: discord.Member):
    """Start a duel with another player."""
    attacker_id = str(ctx.author.id)
    defender_id = str(target.id)

    if attacker_id == defender_id:
        return await ctx.send("You can't attack yourself.")

    # Fetch stats
    a_stats = await get_player_stats(attacker_id)
    d_stats = await get_player_stats(defender_id)

    # --- Attacker dead check with countdown ---
    if a_stats['hp'] <= 0:
        async with bot.db_pool.acquire() as conn:
            db_respawn = await conn.fetchval("SELECT respawn_at FROM player_stats WHERE user_id = $1", attacker_id)
        if db_respawn:
            if db_respawn.tzinfo is None:
                db_respawn = db_respawn.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            remaining = db_respawn - now
            if remaining.total_seconds() <= 0:
                return await ctx.send("You are dead and cannot attack! (respawn time already passed)")
            else:
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                seconds = int(remaining.total_seconds() % 60)
                if hours > 0:
                    time_str = f"{hours}h {minutes}m"
                elif minutes > 0:
                    time_str = f"{minutes}m {seconds}s"
                else:
                    time_str = f"{seconds}s"
                return await ctx.send(f"You are dead and cannot attack! Revives in {time_str}.")
        else:
            return await ctx.send("You are dead and cannot attack! (no respawn time set)")

    # --- Defender dead check with countdown ---
    if d_stats['hp'] <= 0:
        async with bot.db_pool.acquire() as conn:
            db_respawn = await conn.fetchval("SELECT respawn_at FROM player_stats WHERE user_id = $1", defender_id)
        if db_respawn:
            if db_respawn.tzinfo is None:
                db_respawn = db_respawn.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            remaining = db_respawn - now
            if remaining.total_seconds() <= 0:
                return await ctx.send("That player is already dead! (respawn time already passed)")
            else:
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                seconds = int(remaining.total_seconds() % 60)
                if hours > 0:
                    time_str = f"{hours}h {minutes}m"
                elif minutes > 0:
                    time_str = f"{minutes}m {seconds}s"
                else:
                    time_str = f"{seconds}s"
                return await ctx.send(f"That player is already dead! Revives in {time_str}.")
        else:
            return await ctx.send("That player is already dead!")

    # Create the initial embed
    view = AttackView(attacker_id, defender_id, ctx.channel.id, None)
    embed = await view.build_duel_embed()
    msg = await ctx.send(embed=embed, view=view)
    view.message_id = msg.id


async def format_gear_grid(user_id: str) -> str:
    """Return a formatted string of the user's equipped gear (3 lines) including pet."""
    async with bot.db_pool.acquire() as conn:
        weapon_name = await conn.fetchval("""
            SELECT COALESCE(si.name, uw.generated_name)
            FROM user_weapons uw
            LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
            WHERE uw.user_id = $1 AND uw.equipped = TRUE
            LIMIT 1
        """, user_id)
        armor = await conn.fetch("""
            SELECT at.name, at.slot
            FROM user_armor ua
            JOIN armor_types at ON ua.armor_id = at.armor_id
            WHERE ua.user_id = $1 AND ua.equipped = TRUE
        """, user_id)
        acc = await conn.fetch("""
            SELECT at.name, ua.slot
            FROM user_accessories ua
            JOIN accessory_types at ON ua.accessory_id = at.accessory_id
            WHERE ua.user_id = $1 AND ua.equipped = TRUE
        """, user_id)
        # Fetch equipped pet
        pet_name = await conn.fetchval("""
            SELECT pt.name
            FROM user_pets up
            JOIN pet_types pt ON up.pet_id = pt.pet_id
            WHERE up.user_id = $1 AND up.equipped = TRUE
        """, user_id)

    def slot_emoji(slot_type, item_name=None):
        if item_name:
            if slot_type == 'weapon':
                return get_item_emoji(item_name, 'weapon')
            elif slot_type in ('helm', 'suit', 'gauntlets', 'boots'):
                return get_item_emoji(item_name, 'armor')
            else:
                return get_item_emoji(item_name, 'accessory')
        return '*none*'

    armor_dict = {a['slot']: a['name'] for a in armor}
    acc_dict = {a['slot']: a['name'] for a in acc}

    weapon_emoji = slot_emoji('weapon', weapon_name) if weapon_name else '*none*'
    helm = slot_emoji('armor', armor_dict.get('helm'))
    suit = slot_emoji('armor', armor_dict.get('suit'))
    gauntlets = slot_emoji('armor', armor_dict.get('gauntlets'))
    boots = slot_emoji('armor', armor_dict.get('boots'))
    ring1 = slot_emoji('accessory', acc_dict.get('ring1'))
    ring2 = slot_emoji('accessory', acc_dict.get('ring2'))
    earring1 = slot_emoji('accessory', acc_dict.get('earring1'))
    earring2 = slot_emoji('accessory', acc_dict.get('earring2'))
    pendant = slot_emoji('accessory', acc_dict.get('pendant'))

    # Pet emoji – use actual pet emoji if equipped, otherwise default paw
    pet_emoji = get_pet_emoji(pet_name) if pet_name else "🐾"

    line1 = f"{weapon_emoji}"
    line2 = f"{helm} {suit} {gauntlets} {boots} {pet_emoji}"
    line3 = f"{ring1} {earring1} {pendant} {earring2} {ring2}"
    return f"{line1}\n{line2}\n{line3}"


#    ATTACKVIEW----------

class AttackView(discord.ui.View):
    def __init__(self, attacker_id: str, defender_id: str, channel_id: int, message_id: int):
        super().__init__(timeout=300)
        self.attacker_id = attacker_id   # original challenger
        self.defender_id = defender_id   # original opponent
        self.channel_id = channel_id
        self.message_id = message_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return str(interaction.user.id) in (self.attacker_id, self.defender_id)

    @discord.ui.button(label="Attack", style=discord.ButtonStyle.danger)
    async def attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer()

            # Determine who is the attacker this turn
            if str(interaction.user.id) == self.attacker_id:
                current_attacker_id = self.attacker_id
                current_defender_id = self.defender_id
                attacker_user = interaction.user
                defender_user = bot.get_user(int(self.defender_id)) or await bot.fetch_user(int(self.defender_id))
            else:
                current_attacker_id = self.defender_id
                current_defender_id = self.attacker_id
                attacker_user = interaction.user
                defender_user = bot.get_user(int(self.attacker_id)) or await bot.fetch_user(int(self.attacker_id))

            # Fetch fresh stats
            a_stats = await get_player_stats(current_attacker_id)
            d_stats = await get_player_stats(current_defender_id)

            # --- Attacker dead check ---
            if a_stats['hp'] <= 0:
                async with bot.db_pool.acquire() as conn:
                    db_respawn = await conn.fetchval("SELECT respawn_at FROM player_stats WHERE user_id = $1", current_attacker_id)
                if db_respawn:
                    if db_respawn.tzinfo is None:
                        db_respawn = db_respawn.replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    remaining = db_respawn - now
                    if remaining.total_seconds() <= 0:
                        msg = "You are dead and cannot attack! (respawn time already passed)"
                    else:
                        hours = int(remaining.total_seconds() // 3600)
                        minutes = int((remaining.total_seconds() % 3600) // 60)
                        time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                        msg = f"You are dead and cannot attack! Revives in {time_str}."
                else:
                    msg = "You are dead and cannot attack! (no respawn time set)"
                await interaction.followup.send(msg, ephemeral=True)
                return

            # --- Defender dead check ---
            if d_stats['hp'] <= 0:
                async with bot.db_pool.acquire() as conn:
                    db_respawn = await conn.fetchval("SELECT respawn_at FROM player_stats WHERE user_id = $1", current_defender_id)
                if db_respawn:
                    if db_respawn.tzinfo is None:
                        db_respawn = db_respawn.replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    remaining = db_respawn - now
                    if remaining.total_seconds() <= 0:
                        msg = "Target is already dead! (respawn time already passed)"
                    else:
                        hours = int(remaining.total_seconds() // 3600)
                        minutes = int((remaining.total_seconds() % 3600) // 60)
                        time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                        msg = f"Target is already dead! Revives in {time_str}."
                else:
                    msg = "Target is already dead!"
                await interaction.followup.send(msg, ephemeral=True)
                return

            # --- Energy check ---
            if a_stats['energy'] < 1:
                await interaction.followup.send("Not enough energy!", ephemeral=True)
                return

            # --- Get equipped weapon ---
            async with bot.db_pool.acquire() as conn:
                weapon = await conn.fetchrow("""
                    SELECT uw.id, COALESCE(si.name, uw.generated_name) as name, uw.skill_level
                    FROM user_weapons uw
                    LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                    WHERE uw.user_id = $1 AND uw.equipped = TRUE
                    LIMIT 1
                """, current_attacker_id)

            if not weapon:
                await interaction.followup.send("You don't have a weapon equipped!", ephemeral=True)
                return

            wname = weapon['name']
            if wname not in SWORD_SKILLS:
                await interaction.followup.send("Your weapon has no skill!", ephemeral=True)
                return

            skill = SWORD_SKILLS[wname]
            level = weapon['skill_level']
            multiplier = skill['base'] + (level - 1) * skill['increment']

            # --- Skill-specific modifiers ---
            crit_mult = 1.0
            crit_damage_bonus = 0
            bleed_chance_bonus = 0
            bleed_damage_mult = 1.0

            if skill['name'] == "Bloodmoon Rend":
                bleed_chance_bonus = 15
                bleed_damage_mult = 1.25
            elif skill['name'] == "Shadowbane":
                crit_mult = 2.0
                crit_damage_bonus = 50

            effective_crit_chance = a_stats['crit_chance'] * crit_mult
            effective_crit_damage = a_stats['crit_damage'] + crit_damage_bonus
            effective_bleed_chance = a_stats['bleed_chance'] + bleed_chance_bonus

            # --- Dodge check ---
            dodged = False
            if random.random() < d_stats['dodge'] / 100:
                dodged = True

            # --- Damage calculation ---
            if not dodged:
                base_damage = a_stats['atk'] * multiplier
                damage = int(max(base_damage - d_stats['def'] * 0.5, a_stats['atk'] * 0.2))

                is_crit = random.random() < effective_crit_chance / 100
                if is_crit:
                    damage = int(damage * (1 + effective_crit_damage / 100))

                # Apply damage to defender
                new_defender_hp = max(0, d_stats['hp'] - damage)
                await update_player_hp(current_defender_id, new_defender_hp)
                if new_defender_hp == 0:
                    async with bot.db_pool.acquire() as conn:
                        await conn.execute("""
                            UPDATE player_stats
                            SET respawn_at = NOW() + INTERVAL '2 hours'
                            WHERE user_id = $1 AND respawn_at IS NULL
                        """, current_defender_id)

                # Reflect damage
                reflect_damage = 0
                if d_stats['reflect'] > 0:
                    reflect_damage = int(damage * d_stats['reflect'] / 100)
                    if reflect_damage > 0:
                        new_attacker_hp = max(0, a_stats['hp'] - reflect_damage)
                        await update_player_hp(current_attacker_id, new_attacker_hp)
                        if new_attacker_hp == 0:
                            async with bot.db_pool.acquire() as conn:
                                await conn.execute("""
                                    UPDATE player_stats
                                    SET respawn_at = NOW() + INTERVAL '2 hours'
                                    WHERE user_id = $1 AND respawn_at IS NULL
                                """, current_attacker_id)

                # Bleed
                bleed_applied = False
                bleed_tick = 0
                if random.random() < effective_bleed_chance / 100:
                    bleed_tick = int(a_stats['atk'] * (a_stats['bleed_damage'] * bleed_damage_mult / 100)) + a_stats.get('bleed_flat_bonus', 0)
                    if bleed_tick > 0:
                        bleed_applied = True
                        async with bot.db_pool.acquire() as conn:
                            await conn.execute("""
                                INSERT INTO active_effects (target_id, effect_type, value, remaining_ticks)
                                VALUES ($1, 'bleed', $2, 3)
                            """, current_defender_id, bleed_tick)

                # Burn (Dawn Breaker)
                burn_applied = False
                burn_tick = 0
                if skill['name'] == "Dawn's Wrath":
                    burn_chance = 25
                    burn_damage_percent = 20
                    if random.random() < burn_chance / 100:
                        burn_tick = int(damage * burn_damage_percent / 100) + a_stats.get('burn_flat_bonus', 0)
                        if burn_tick > 0:
                            burn_applied = True
                            async with bot.db_pool.acquire() as conn:
                                await conn.execute("""
                                    INSERT INTO active_effects (target_id, effect_type, value, remaining_ticks)
                                    VALUES ($1, 'burn', $2, 3)
                                """, current_defender_id, burn_tick)

                # Buffs/Debuffs
                buff_applied = None
                if skill['name'] == "Zenith Slash" and random.random() < 0.20:
                    async with bot.db_pool.acquire() as conn:
                        await conn.execute("""
                            INSERT INTO active_buffs (target_id, effect_type, value, remaining_turns)
                            VALUES ($1, 'atk_mult', 1.5, 2)
                        """, current_attacker_id)
                    buff_applied = f"{attacker_user.display_name} gains 50% ATK boost for 2 turns!"

                if skill['name'] == "Abyssal Strike" and random.random() < 0.30:
                    async with bot.db_pool.acquire() as conn:
                        await conn.execute("""
                            INSERT INTO active_buffs (target_id, effect_type, value, remaining_turns)
                            VALUES ($1, 'def_mult', 0.85, 3)
                        """, current_defender_id)
                    buff_applied = f"{defender_user.display_name}'s DEF reduced by 15% for 3 turns!"

            else:  # dodged
                damage = 0
                is_crit = False
                reflect_damage = 0
                bleed_applied = False
                burn_applied = False
                buff_applied = None

            # Deduct energy from attacker (always)
            new_energy = a_stats['energy'] - 1
            await update_player_energy(current_attacker_id, new_energy)

            # --- Decrement buff turns for both participants ---
            async with bot.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE active_buffs SET remaining_turns = remaining_turns - 1
                    WHERE target_id IN ($1, $2) AND remaining_turns > 0
                """, current_attacker_id, current_defender_id)
                await conn.execute("DELETE FROM active_buffs WHERE remaining_turns <= 0")

            # --- Build action text ---
            attacker_name = attacker_user.display_name
            defender_name = defender_user.display_name
            skill_name = skill['name']
            action_lines = []
            if dodged:
                action_lines.append(f"{defender_name} dodged the attack!")
            else:
                base_line = f"{attacker_name} uses {skill_name} and deals **{damage}** damage to {defender_name}"
                if is_crit:
                    base_line += " 💥 CRITICAL!"
                action_lines.append(base_line)

                if reflect_damage > 0:
                    action_lines.append(f"{defender_name} reflected **{reflect_damage}** damage to {attacker_name}")

                if bleed_applied:
                    action_lines.append(f"{defender_name} is bleeding, taking {bleed_tick} damage per second for 3s")

                if burn_applied:
                    action_lines.append(f"{defender_name} is burning, taking {burn_tick} damage per second for 3s")

                if buff_applied:
                    action_lines.append(buff_applied)

            action_text = "\n".join(action_lines)

            # --- Update the message ---
            channel = bot.get_channel(self.channel_id)
            try:
                msg = await channel.fetch_message(self.message_id)
            except:
                await interaction.followup.send("Message not found.", ephemeral=True)
                return

            new_embed = await self.build_duel_embed(action_text)
            await msg.edit(embed=new_embed, view=self)

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            await log_to_discord(bot, f"Error in attack_button: {e}", level="ERROR", error=e)
            await interaction.followup.send("❌ An error occurred. Check bot‑logs.", ephemeral=True)

    # --- Potion button (row 0, next to Attack) ---
    @discord.ui.button(label="Potion", style=discord.ButtonStyle.danger, row=0)
    async def use_potion_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Opens an ephemeral view to choose a potion."""
        view = self.PotionChoiceView(self, str(interaction.user.id))
        await interaction.response.send_message("Choose a potion to use:", view=view, ephemeral=True)

    class PotionChoiceView(discord.ui.View):
        """Ephemeral view with HP and Energy potion buttons."""
        def __init__(self, parent_view, user_id):
            super().__init__(timeout=60)
            self.parent_view = parent_view
            self.user_id = user_id

        @discord.ui.button(label="HP Potion", emoji=CUSTOM_EMOJIS.get('hp_potion'), style=discord.ButtonStyle.success)
        async def hp_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if str(interaction.user.id) != self.user_id:
                await interaction.response.send_message("This is not your potion choice.", ephemeral=True)
                return
            await self.parent_view.use_potion(interaction, 'hp')

        @discord.ui.button(label="Energy Potion", emoji=CUSTOM_EMOJIS.get('energy_potion'), style=discord.ButtonStyle.primary)
        async def energy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if str(interaction.user.id) != self.user_id:
                await interaction.response.send_message("This is not your potion choice.", ephemeral=True)
                return
            await self.parent_view.use_potion(interaction, 'energy')

    async def use_potion(self, interaction: discord.Interaction, potion_type: str):
        """Consume the chosen potion and apply its effect, with full‑stat checks."""
        await interaction.response.defer(ephemeral=True)
        user_id = str(interaction.user.id)

        # Fetch dynamic player stats (includes pet bonuses)
        stats = await get_player_stats(user_id)
        if not stats:
            await interaction.followup.send("❌ Could not retrieve your stats.", ephemeral=True)
            return

        current_hp = stats['hp']
        max_hp = stats['max_hp']
        current_energy = stats['energy']
        max_energy = stats['max_energy']

        # Fetch potion item IDs
        async with bot.db_pool.acquire() as conn:
            hp_id = await conn.fetchval("SELECT item_id FROM shop_items WHERE name = 'HP Potion'")
            energy_id = await conn.fetchval("SELECT item_id FROM shop_items WHERE name = 'Energy Potion'")

        if potion_type == 'hp':
            potion_id = hp_id
            potion_name = "HP Potion"
            emoji = CUSTOM_EMOJIS.get('hp_potion')
        else:
            potion_id = energy_id
            potion_name = "Energy Potion"
            emoji = CUSTOM_EMOJIS.get('energy_potion')

        if not potion_id:
            await interaction.followup.send("❌ Potion not configured. Contact admin.", ephemeral=True)
            return

        # Check inventory and stats
        async with bot.db_pool.acquire() as conn:
            qty = await conn.fetchval("SELECT quantity FROM user_materials WHERE user_id = $1 AND material_id = $2", user_id, potion_id)
            if not qty or qty < 1:
                await interaction.followup.send(f"❌ You don't have any {potion_name}.", ephemeral=True)
                return

            # ❌ DEAD CHECK – block all potion use if dead
            hp_check = await conn.fetchval("SELECT hp FROM player_stats WHERE user_id = $1", user_id)
            if hp_check <= 0:
                await interaction.followup.send("❌ You are dead and cannot use any potions.", ephemeral=True)
                return

            if potion_type == 'hp':
                if current_hp >= max_hp:
                    await interaction.followup.send(f"Your HP is already full! ({current_hp}/{max_hp})", ephemeral=True)
                    return
                heal = max(1, int(max_hp * 0.5))
                new_hp = min(current_hp + heal, max_hp)
                effect = f"healed **{new_hp - current_hp}** HP"

            else:  # energy
                if current_energy >= max_energy:
                    await interaction.followup.send(f"Your energy is already full! ({current_energy}/{max_energy})", ephemeral=True)
                    return
                new_energy = current_energy + 1
                effect = "restored **1** energy"

            # Deduct potion and apply effect
            await conn.execute("UPDATE user_materials SET quantity = quantity - 1 WHERE user_id = $1 AND material_id = $2", user_id, potion_id)

            if potion_type == 'hp':
                await conn.execute("UPDATE player_stats SET hp = $1 WHERE user_id = $2", new_hp, user_id)
            else:
                await conn.execute("UPDATE player_stats SET energy = $1 WHERE user_id = $2", new_energy, user_id)

        # Build action message for main duel embed
        action_message = f"{interaction.user.display_name} used {emoji} **{potion_name}** and {effect}!"

        # Update main duel embed
        channel = bot.get_channel(self.channel_id)
        try:
            msg = await channel.fetch_message(self.message_id)
        except:
            await interaction.followup.send("Main duel message not found.", ephemeral=True)
            return

        new_embed = await self.build_duel_embed(action_message)
        await msg.edit(embed=new_embed, view=self)

        # Confirm to user
        await interaction.followup.send(f"You used {emoji} **{potion_name}**.", ephemeral=True)

    async def build_duel_embed(self, action_text: str = None):
        """Build the duel embed with vertical stats, gear grids, and action result."""
        a_stats = await get_player_stats(self.attacker_id)
        d_stats = await get_player_stats(self.defender_id)
        a_user = bot.get_user(int(self.attacker_id))
        d_user = bot.get_user(int(self.defender_id))

        # Get title emoji if equipped
        a_title = a_stats.get('equipped_title')
        d_title = d_stats.get('equipped_title')
        a_title_emoji = f" {a_title[1]}" if a_title else ""
        d_title_emoji = f" {d_title[1]}" if d_title else ""

        embed = discord.Embed(
            title=f"{a_user.display_name} vs {d_user.display_name}",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=a_user.display_avatar.url)

        def hp_bar(current, max_hp):
            if current <= 0:
                return "⬛" * 10 + " DEAD!"
            percent = current / max_hp
            filled = int(percent * 10)
            return "🟥" * filled + "⬛" * (10 - filled) + f" `{current}/{max_hp}`"

        def energy_bar(current, max_energy):
            percent = current / max_energy
            filled = int(percent * 10)
            return "🟨" * filled + "⬛" * (10 - filled) + f" `{current}/{max_energy}`"

        def def_bar(value):
            return "🟦" * 10 + f" `{value} DEF`"

        a_hp = hp_bar(a_stats['hp'], a_stats['max_hp'])
        a_def = def_bar(a_stats['def'])
        a_energy = energy_bar(a_stats['energy'], a_stats['max_energy'])
        a_stats_text = f"{a_hp}\n{a_def}\n{a_energy}"

        d_hp = hp_bar(d_stats['hp'], d_stats['max_hp'])
        d_def = def_bar(d_stats['def'])
        d_energy = energy_bar(d_stats['energy'], d_stats['max_energy'])
        d_stats_text = f"{d_hp}\n{d_def}\n{d_energy}"

        a_gear = await format_gear_grid(self.attacker_id)
        d_gear = await format_gear_grid(self.defender_id)

        embed.add_field(
            name=f"{a_user.display_name}'s Stats{a_title_emoji}",
            value=a_stats_text,
            inline=False
        )
        embed.add_field(name="Gears", value=a_gear, inline=False)
        embed.add_field(name="▬" * 20, value="\u200b", inline=False)
        embed.add_field(
            name=f"{d_user.display_name}'s Stats{d_title_emoji}",
            value=d_stats_text,
            inline=False
        )
        embed.add_field(name="Gears", value=d_gear, inline=False)

        if action_text:
            embed.add_field(name="▬" * 20, value=action_text, inline=False)
        else:
            embed.add_field(name="▬" * 20, value="Click Attack to begin!", inline=False)

        return embed
#  END 

async def get_player_stats(user_id: str):
    """Return dict of player stats including dynamically recalculated max HP and pet bonuses."""
    BASE_HP = 1000
    BASE_DEF = 500

    async with bot.db_pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT hp, max_hp, energy, max_energy, respawn_at
            FROM player_stats WHERE user_id = $1
        """, user_id)
        if not row:
            await conn.execute("""
                INSERT INTO player_stats (user_id, hp, max_hp, energy, max_energy)
                VALUES ($1, $2, $2, 3, 3)
            """, user_id, BASE_HP)
            row = {'hp': BASE_HP, 'max_hp': BASE_HP, 'energy': 3, 'max_energy': 3, 'respawn_at': None}

        weapon = await conn.fetchrow("""
            SELECT attack, bleeding_chance, crit_chance, crit_damage
            FROM user_weapons
            WHERE user_id = $1 AND equipped = TRUE
            LIMIT 1
        """, user_id)

        armor = await conn.fetch("""
            SELECT defense, reflect_damage, hp_bonus, set_name
            FROM user_armor
            WHERE user_id = $1 AND equipped = TRUE
        """, user_id)

        accessories = await conn.fetch("""
            SELECT at.bonus_stat, ua.bonus_value, at.set_name
            FROM user_accessories ua
            JOIN accessory_types at ON ua.accessory_id = at.accessory_id
            WHERE ua.user_id = $1 AND ua.equipped = TRUE
        """, user_id)

    # --- Base stats from gear (flat) ---
    atk = 0
    defense = BASE_DEF
    crit_chance = 0.0
    crit_damage = 0.0
    bleed_chance = 0.0
    bleed_damage = 0.0
    reflect = 0
    hp_from_gear = BASE_HP  # start with base HP, then add flat bonuses

    if weapon:
        atk += weapon['attack']
        bleed_chance += weapon['bleeding_chance'] or 0
        crit_chance += weapon['crit_chance'] or 0
        crit_damage += weapon['crit_damage'] or 0

    for a in armor:
        defense += a['defense']
        reflect += a['reflect_damage'] or 0
        hp_from_gear += a['hp_bonus'] or 0

    for acc in accessories:
        stat = acc['bonus_stat']
        val = acc['bonus_value']
        if stat == 'atk':
            atk += val
        elif stat == 'def':
            defense += val
        elif stat == 'hp':
            hp_from_gear += val
        elif stat == 'crit':
            crit_chance += val
        elif stat == 'bleed':
            bleed_damage += val

    # --- Multipliers from sets ---
    atk_mult = 1.0
    def_mult = 1.0
    hp_mult = 1.0
    reflect_add = 0
    crit_chance_add = 0
    crit_damage_add = 0

    # Armor set bonuses
    armor_sets = {}
    for a in armor:
        if a['set_name']:
            armor_sets[a['set_name']] = armor_sets.get(a['set_name'], 0) + 1
    for set_name, count in armor_sets.items():
        if count >= 4:
            sname = set_name.lower()
            if sname in ('bilari', 'cryo', 'bane'):
                crit_chance_add += 10
                crit_damage_add += 25
                def_mult *= 1.15
                reflect_add += 20
                hp_mult *= 1.20   # 20% HP multiplier

    # Accessory set bonuses
    accessory_sets = {}
    for acc in accessories:
        if acc['set_name']:
            accessory_sets[acc['set_name']] = accessory_sets.get(acc['set_name'], 0) + 1
    for set_name, count in accessory_sets.items():
        if count >= 5:
            sname = set_name.lower()
            if sname == 'champion':
                atk_mult *= 1.20
                def_mult *= 1.15
                hp_mult *= 1.15
            elif sname == 'defender':
                def_mult *= 1.20
                reflect_add += 10
                hp_mult *= 1.15
            elif sname == 'angel':
                crit_chance_add += 15
                bleed_damage += 20
                hp_mult *= 1.15

    # Apply multipliers to flat stats
    atk = int(atk * atk_mult)
    defense = int(defense * def_mult)
    # HP multiplier applies to the total gear HP (including base)
    max_hp_after_sets = int(hp_from_gear * hp_mult)   # HP after sets
    reflect += reflect_add
    crit_chance += crit_chance_add
    crit_damage += crit_damage_add

    # ========== PET BONUSES ==========
    energy_bonus = 0
    dodge = 0
    bleed_flat_bonus = 0
    burn_flat_bonus = 0
    pet_atk_mult = 1.0
    pet_def_mult = 1.0
    pet_hp_mult = 1.0

    async with bot.db_pool.acquire() as conn:
        pet = await conn.fetchrow("""
            SELECT pt.atk_percent, pt.def_percent, pt.hp_percent,
                   pt.dodge_percent, pt.bleed_flat, pt.burn_flat, pt.energy_bonus
            FROM user_pets up
            JOIN pet_types pt ON up.pet_id = pt.pet_id
            WHERE up.user_id = $1 AND up.equipped = TRUE
        """, user_id)
    if pet:
        pet_atk_mult = 1 + pet['atk_percent'] / 100
        pet_def_mult = 1 + pet['def_percent'] / 100
        pet_hp_mult = 1 + pet['hp_percent'] / 100
        energy_bonus = pet['energy_bonus']
        dodge = pet['dodge_percent']
        bleed_flat_bonus = pet['bleed_flat']
        burn_flat_bonus = pet['burn_flat']

    # Apply pet multipliers
    atk = int(atk * pet_atk_mult)
    defense = int(defense * pet_def_mult)
    max_hp_after_pet = int(max_hp_after_sets * pet_hp_mult)   # HP after sets and pet

    # ========== TITLE BONUSES ==========
    # Initialize title variables with defaults
    title_atk_mult = 1.0
    title_def_mult = 1.0
    title_hp_mult = 1.0
    crit_dmg_res = 0
    mining_bonus_percent = 0
    boss_damage_percent = 0
    extra_boss_attempts = 0
    extra_plunder_attempts = 0
    equipped_title = None

    title_bonuses = await get_equipped_title_bonuses(user_id)
    if title_bonuses:
        title_atk_mult = 1 + title_bonuses['atk_percent'] / 100
        title_def_mult = 1 + title_bonuses['def_percent'] / 100
        title_hp_mult = 1 + title_bonuses['hp_percent'] / 100
        crit_chance += title_bonuses['crit_chance']
        dodge += title_bonuses['dodge_percent']
        bleed_flat_bonus += title_bonuses['bleed_flat']
        burn_flat_bonus += title_bonuses['burn_flat']
        crit_dmg_res = title_bonuses['crit_dmg_res_percent']
        mining_bonus_percent = title_bonuses['mining_bonus_percent']
        boss_damage_percent = title_bonuses['boss_damage_percent']
        extra_boss_attempts = title_bonuses['extra_boss_attempts']
        extra_plunder_attempts = title_bonuses['extra_plunder_attempts']
        equipped_title = (title_bonuses['name'], title_bonuses['emoji'])

    # Apply title multipliers
    atk = int(atk * title_atk_mult)
    defense = int(defense * title_def_mult)
    max_hp = int(max_hp_after_pet * title_hp_mult)   # Final HP after all multipliers

    current_hp = row['hp']
    if current_hp > max_hp:
        current_hp = max_hp

    # --- Adjust max energy with pet bonus ---
    max_energy = row['max_energy'] + energy_bonus
    current_energy = row['energy']
    if current_energy > max_energy:
        current_energy = max_energy

    # --- Active buffs ---
    async with bot.db_pool.acquire() as conn:
        buffs = await conn.fetch("SELECT * FROM active_buffs WHERE target_id = $1", user_id)
    for buff in buffs:
        if buff['effect_type'] == 'atk_mult':
            atk = int(atk * buff['value'])
        elif buff['effect_type'] == 'def_mult':
            defense = int(defense * buff['value'])

    return {
        'hp': current_hp,
        'max_hp': max_hp,
        'energy': current_energy,
        'max_energy': max_energy,
        'respawn_at': row['respawn_at'],
        'atk': atk,
        'def': defense,
        'crit_chance': crit_chance,
        'crit_damage': crit_damage,
        'bleed_chance': bleed_chance,
        'bleed_damage': bleed_damage,
        'reflect': reflect,
        'dodge': dodge,
        'bleed_flat_bonus': bleed_flat_bonus,
        'burn_flat_bonus': burn_flat_bonus,
        'crit_dmg_res': crit_dmg_res,
        'mining_bonus_percent': mining_bonus_percent,
        'boss_damage_percent': boss_damage_percent,
        'extra_boss_attempts': extra_boss_attempts,
        'extra_plunder_attempts': extra_plunder_attempts,
        'equipped_title': equipped_title,
    }

async def update_player_hp(user_id: str, new_hp: int):
    async with bot.db_pool.acquire() as conn:
        await conn.execute("UPDATE player_stats SET hp = $1 WHERE user_id = $2", new_hp, user_id)

async def update_player_energy(user_id: str, new_energy: int):
    async with bot.db_pool.acquire() as conn:
        await conn.execute("UPDATE player_stats SET energy = $1 WHERE user_id = $2", new_energy, user_id)

async def get_equipped_emojis(user_id: str) -> str:
    """Return a string of custom emojis representing the user's equipped gear."""
    async with bot.db_pool.acquire() as conn:
        weapon_name = await conn.fetchval("""
            SELECT COALESCE(si.name, uw.generated_name)
            FROM user_weapons uw
            LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
            WHERE uw.user_id = $1 AND uw.equipped = TRUE
            LIMIT 1
        """, user_id)
        armor = await conn.fetch("""
            SELECT at.name, at.slot
            FROM user_armor ua
            JOIN armor_types at ON ua.armor_id = at.armor_id
            WHERE ua.user_id = $1 AND ua.equipped = TRUE
        """, user_id)
        acc = await conn.fetch("""
            SELECT at.name, ua.slot
            FROM user_accessories ua
            JOIN accessory_types at ON ua.accessory_id = at.accessory_id
            WHERE ua.user_id = $1 AND ua.equipped = TRUE
        """, user_id)

    emojis = []
    if weapon_name:
        emojis.append(get_item_emoji(weapon_name, 'weapon'))
    # Order armor by slot
    slot_order = {'helm':0, 'suit':1, 'gauntlets':2, 'boots':3}
    armor.sort(key=lambda x: slot_order.get(x['slot'], 99))
    for a in armor:
        emojis.append(get_item_emoji(a['name'], 'armor'))
    # Accessories – you can decide the order; here just append all
    for a in acc:
        emojis.append(get_item_emoji(a['name'], 'accessory'))
    return ' '.join(emojis) if emojis else 'None'



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
        kwargs['custom_id'] = f"stop_mining_{target_id}"   # ✅ include custom_id
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
        kwargs['custom_id'] = f"plunder_{target_id}"       # ✅ include custom_id
        super().__init__(**kwargs)
        self.target_id = target_id
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            if str(interaction.user.id) == self.target_id:
                await interaction.followup.send("❌ You cannot plunder yourself.", ephemeral=True)
                return
            result = await self.cog.plunder_user(str(interaction.user.id), self.target_id, interaction.guild)
            await interaction.followup.send(result, ephemeral=True)
        except Exception as e:
            print(f"Error in plunder button: {e}")
            traceback.print_exc()
            await interaction.followup.send("❌ An error occurred.", ephemeral=True)









# ========== BOSS SYSTEM ==========



class BossAttackView(discord.ui.View):
    _last_update = {}
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)  # persistent view
        self.guild_id = guild_id

    @discord.ui.button(label="Attack", style=discord.ButtonStyle.danger, custom_id="boss_attack")
    async def attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        # 1. Fetch boss config
        async with bot.db_pool.acquire() as conn:
            config = await conn.fetchrow("SELECT boss_hp, max_hp FROM boss_config WHERE guild_id = $1", self.guild_id)
        if not config:
            await interaction.followup.send("❌ Boss not configured.", ephemeral=True)
            return
        if config['boss_hp'] <= 0:
            await interaction.followup.send("❌ The boss is already dead! Wait for the daily reset.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        reset_date = self.get_reset_date()

        # 2. Check daily attempts
        async with bot.db_pool.acquire() as conn:
            attempt_row = await conn.fetchrow("SELECT attempts_used FROM boss_attempts WHERE user_id = $1 AND reset_date = $2", user_id, reset_date)
            attempts_used = attempt_row['attempts_used'] if attempt_row else 0
            if attempts_used >= 5:
                await interaction.followup.send("❌ You have used all 5 attempts for today. Come back tomorrow!", ephemeral=True)
                return

        # 3. Get player stats (includes ATK, crit, and active buffs)
        a_stats = await get_player_stats(user_id)
        if not a_stats:
            await interaction.followup.send("❌ Could not load your stats.", ephemeral=True)
            return

        # 4. Fetch equipped weapon and its skill
        async with bot.db_pool.acquire() as conn:
            weapon = await conn.fetchrow("""
                SELECT uw.id, COALESCE(si.name, uw.generated_name) as name, uw.skill_level
                FROM user_weapons uw
                LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                WHERE uw.user_id = $1 AND uw.equipped = TRUE
                LIMIT 1
            """, user_id)

        if not weapon:
            # No weapon equipped – use a basic attack
            skill_mult = 1.0
            skill_name = "Basic Attack"
            crit_mult = 1.0
            crit_damage_bonus = 0
        else:
            wname = weapon['name']
            if wname in SWORD_SKILLS:
                skill_data = SWORD_SKILLS[wname]
                level = weapon['skill_level']
                skill_mult = skill_data['base'] + (level - 1) * skill_data['increment']
                skill_name = skill_data['name']

                # Skill‑specific modifiers (only those that affect damage/crit)
                crit_mult = 1.0
                crit_damage_bonus = 0
                if skill_data['name'] == "Shadowbane":
                    crit_mult = 2.0
                    crit_damage_bonus = 50
                # Bloodmoon Rend affects bleed, which we ignore for boss, so no change.
            else:
                # Weapon has no registered skill – treat as basic
                skill_mult = 1.0
                skill_name = "Attack"
                crit_mult = 1.0
                crit_damage_bonus = 0

        # 5. Effective crit stats for this attack
        effective_crit_chance = a_stats['crit_chance'] * crit_mult
        effective_crit_damage = a_stats['crit_damage'] + crit_damage_bonus

        # 6. Base damage (no defense subtraction)
        base_damage = a_stats['atk'] * skill_mult
        # Add a small random variance (±5%) for fun – remove if you want deterministic damage
        variance = random.uniform(0.95, 1.05)
        damage = int(base_damage * variance)

        # 7. Critical hit
        is_crit = random.random() < effective_crit_chance / 100
        if is_crit:
            damage = int(damage * (1 + effective_crit_damage / 100))

        # 8. Update boss HP (with row lock to prevent race conditions)
        async with bot.db_pool.acquire() as conn:
            async with conn.transaction():
                current_hp = await conn.fetchval("SELECT boss_hp FROM boss_config WHERE guild_id = $1 FOR UPDATE", self.guild_id)
                new_hp = max(0, current_hp - damage)
                await conn.execute("UPDATE boss_config SET boss_hp = $1 WHERE guild_id = $2", new_hp, self.guild_id)

        # 9. Update attempts
        async with bot.db_pool.acquire() as conn:
            if attempt_row:
                await conn.execute("UPDATE boss_attempts SET attempts_used = attempts_used + 1 WHERE user_id = $1 AND reset_date = $2", user_id, reset_date)
            else:
                await conn.execute("INSERT INTO boss_attempts (user_id, reset_date, attempts_used) VALUES ($1, $2, 1)", user_id, reset_date)

        # 10. Update total damage for leaderboard
        async with bot.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO boss_damage (user_id, reset_date, total_damage)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id, reset_date) DO UPDATE
                SET total_damage = boss_damage.total_damage + $3
            """, user_id, reset_date, damage)
       

        # 11. Update the public boss message with new HP
        await self.update_boss_message(interaction, new_hp, config['max_hp'])

        # 12. Stone drop chance (20% for 2-5 random stones)
        stone_dropped = False
        if random.random() < 0.35:
            stone_name = random.choice([
                'Sword Enhancement Stone',
                'Armor Enhancement Stone',
                'Accessories Enhancement Stone'
            ])
            stone_qty = random.randint(2, 15)

            async with bot.db_pool.acquire() as conn:
                stone_id = await conn.fetchval("SELECT item_id FROM shop_items WHERE name = $1", stone_name)
                if stone_id:
                    await conn.execute("""
                        INSERT INTO user_materials (user_id, material_id, quantity)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (user_id, material_id) DO UPDATE
                        SET quantity = user_materials.quantity + $3
                    """, user_id, stone_id, stone_qty)
            stone_dropped = True

        # 13. Send feedback to the user
        crit_text = " 💥 CRITICAL!" if is_crit else ""
        message = f"✅ You used **{skill_name}** and dealt **{damage}** damage to the boss{crit_text}!\nAttempts left: {4 - attempts_used}."
        if stone_dropped:
            # Get the stone emoji from CUSTOM_EMOJIS using the stone name
            # Determine stone emoji based on stone name
            name_lower = stone_name.lower()
            if 'sword' in name_lower:
                stone_emoji = CUSTOM_EMOJIS.get('sword_enhancement_stone', '⚔️')
            elif 'armor' in name_lower:
                stone_emoji = CUSTOM_EMOJIS.get('armors_enhancement_stone', '🛡️')
            elif 'accessories' in name_lower:
                stone_emoji = CUSTOM_EMOJIS.get('acc_enhancement_stone', '💍')
            else:
                stone_emoji = '💎'

            message += f"\nYou also found **{stone_qty}** {stone_emoji} **{stone_name}**!"

        await interaction.followup.send(message, ephemeral=True)

    @discord.ui.button(label="🏆 Rankings", style=discord.ButtonStyle.secondary, custom_id="boss_rankings")
    async def rankings_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        reset_date = self.get_reset_date()
        async with bot.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT user_id, total_damage
                FROM boss_damage
                WHERE reset_date = $1
                ORDER BY total_damage DESC
                LIMIT 10
            """, reset_date)

        if not rows:
            await interaction.response.send_message("No damage recorded yet. Attack the boss!", ephemeral=True)
            return

        embed = discord.Embed(title="🏆 Boss Damage Leaderboard", color=discord.Color.gold())
        desc_lines = []
        for idx, row in enumerate(rows, start=1):
            user = bot.get_user(int(row['user_id']))
            name = user.display_name if user else f"User {row['user_id'][:6]}"
            desc_lines.append(f"{idx}. **{name}** – {row['total_damage']} damage")
        embed.description = "\n".join(desc_lines)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def update_boss_message(self, interaction: discord.Interaction, current_hp: int, max_hp: int):
        """Edit the main boss embed with updated HP, with a per‑guild cooldown."""
        now = time.time()
        guild_id = self.guild_id
        # Cooldown: at least 2 seconds between updates for this guild
        if guild_id in self.__class__._last_update and now - self.__class__._last_update[guild_id] < 2:
            return
        self.__class__._last_update[guild_id] = now

        async with bot.db_pool.acquire() as conn:
            msg_id = await conn.fetchval("SELECT message_id FROM boss_config WHERE guild_id = $1", self.guild_id)
        if not msg_id:
            return
        channel = interaction.channel
        try:
            msg = await channel.fetch_message(msg_id)
            embed = await self.build_boss_embed(current_hp, max_hp)
            await msg.edit(embed=embed)
        except discord.NotFound:
            # Message deleted – clear from DB
            async with bot.db_pool.acquire() as conn2:
                await conn2.execute("UPDATE boss_config SET message_id = NULL WHERE guild_id = $1", self.guild_id)
        except discord.HTTPException as e:
            if e.status == 429:
                print(f"⚠️ Rate limit hit for guild {guild_id}, skipping this update.")
            else:
                print(f"❌ Failed to edit boss message: {e}")


    async def build_boss_embed(self, current_hp: int, max_hp: int) -> discord.Embed:
        """Fetch current boss image URL from DB and build embed."""
        async with bot.db_pool.acquire() as conn:
            image_url = await conn.fetchval("SELECT boss_image_url FROM boss_config WHERE guild_id = $1", self.guild_id)
        if not image_url:
            # fallback if none set
            image_url = "https://example.com/boss_image.png"

        percent = current_hp / max_hp
        filled = int(percent * 20)
        bar = "🟥" * filled + "⬛" * (20 - filled)
        embed = discord.Embed(
            title="**Server Boss**",
            description=(
                "Click the button below to attack the boss! You have **5 attempts per day**.\n\n"
                "**Rewards:** Top 10 get gems (1st: 1000, 2nd: 500, 3rd: 250, 4th-10th: 100)."
            ),
            color=discord.Color.red()
        )
        embed.add_field(name="HP", value=f"{bar} `{current_hp}/{max_hp}`", inline=False)
        embed.set_image(url=image_url)
        return embed

    @staticmethod
    def get_reset_date() -> date:
        """Return the date of the current boss cycle (based on 10 AM PHT = 2 AM UTC)."""
        now = datetime.now(timezone.utc)
        reset_hour_utc = 2
        if now.hour < reset_hour_utc:
            return (now - timedelta(days=1)).date()
        else:
            return now.date()



@bot.command(name='bossannounce')
@commands.has_permissions(administrator=True)
async def boss_announce(ctx, channel: discord.TextChannel):
    """Set the channel where boss reset announcements will be sent."""
    async with bot.db_pool.acquire() as conn:
        await conn.execute("UPDATE boss_config SET announce_channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
    await ctx.send(f"✅ Boss reset announcements will now be sent to {channel.mention}")


@bot.command(name='setboss')
@commands.has_permissions(administrator=True)
async def set_boss(ctx, channel: discord.TextChannel, hp: int = 100000):
    """Set the boss channel and initial HP."""
    async with bot.db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO boss_config (guild_id, channel_id, boss_hp, max_hp)
            VALUES ($1, $2, $3, $3)
            ON CONFLICT (guild_id) DO UPDATE
            SET channel_id = $2, boss_hp = $3, max_hp = $3
        """, ctx.guild.id, channel.id, hp)
    await ctx.send(f"✅ Boss channel set to {channel.mention}. Now use `!!spawnboss` to create the attack message.")



@bot.command(name='bossmaxhp')
@commands.has_permissions(administrator=True)
async def boss_max_hp(ctx, new_max_hp: int):
    """Set the boss's maximum HP (will take effect after next reset)."""
    if new_max_hp <= 0:
        return await ctx.send("❌ HP must be positive.")
    async with bot.db_pool.acquire() as conn:
        await conn.execute("UPDATE boss_config SET max_hp = $1 WHERE guild_id = $2", new_max_hp, ctx.guild.id)
    await ctx.send(f"✅ Boss max HP set to {new_max_hp}. It will respawn with this HP at the next reset.")



@bot.command(name='spawnboss')
@commands.has_permissions(administrator=True)
async def spawn_boss(ctx):
    """Create the persistent boss attack message in the configured channel."""
    async with bot.db_pool.acquire() as conn:
        config = await conn.fetchrow("SELECT channel_id, boss_hp, max_hp FROM boss_config WHERE guild_id = $1", ctx.guild.id)
    if not config:
        return await ctx.send("❌ Boss not configured. Use `!!setboss` first.")

    channel = ctx.guild.get_channel(config['channel_id'])
    if not channel:
        return await ctx.send("❌ Boss channel not found.")

    # Pick a random initial image
    initial_image = random.choice(BOSS_IMAGES) if BOSS_IMAGES else None

    # Store the image in the database
    async with bot.db_pool.acquire() as conn2:
        await conn2.execute("UPDATE boss_config SET boss_image_url = $1 WHERE guild_id = $2", initial_image, ctx.guild.id)

    # Build embed with the new image
    temp_view = BossAttackView(ctx.guild.id)
    embed = await temp_view.build_boss_embed(config['boss_hp'], config['max_hp'])
    view = BossAttackView(ctx.guild.id)
    msg = await channel.send(embed=embed, view=view)

    async with bot.db_pool.acquire() as conn3:
        await conn3.execute("UPDATE boss_config SET message_id = $1 WHERE guild_id = $2", msg.id, ctx.guild.id)

    await ctx.send(f"✅ Boss spawned in {channel.mention}!")

@bot.command(name='bossleaderboard')
async def boss_leaderboard(ctx):
    """Show current damage rankings."""
    reset_date = BossAttackView.get_reset_date()
    async with bot.db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT user_id, total_damage
            FROM boss_damage
            WHERE reset_date = $1
            ORDER BY total_damage DESC
            LIMIT 10
        """, reset_date)

    if not rows:
        return await ctx.send("No damage recorded yet. Attack the boss!")

    embed = discord.Embed(title="🏆 Boss Damage Leaderboard", color=discord.Color.gold())
    desc_lines = []
    for idx, row in enumerate(rows, start=1):
        user = bot.get_user(int(row['user_id']))
        name = user.display_name if user else f"User {row['user_id'][:6]}"
        desc_lines.append(f"{idx}. **{name}** – {row['total_damage']} damage")
    embed.description = "\n".join(desc_lines)
    await ctx.send(embed=embed)



from discord.ext import tasks

@tasks.loop(minutes=1)
async def boss_reset_task():
    now = datetime.now(timezone.utc)
    if now.hour == 2 and now.minute == 0:   # 10 AM PHT
        await perform_boss_reset()

async def perform_boss_reset():
    """Compute rankings, send rewards, reset boss HP, pick new image, and clear daily data."""
    async with bot.db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT guild_id, channel_id, message_id, max_hp FROM boss_config")
    for row in rows:
        guild_id = row['guild_id']
        channel_id = row['channel_id']
        message_id = row['message_id']
        max_hp = row['max_hp']
        reset_date = (datetime.now(timezone.utc) - timedelta(days=1)).date()

        # --- Fetch and distribute rankings (same as before) ---
        async with bot.db_pool.acquire() as conn2:
            rankings = await conn2.fetch("""
                SELECT user_id, total_damage
                FROM boss_damage
                WHERE reset_date = $1
                ORDER BY total_damage DESC
            """, reset_date)

        if rankings:
            for idx, r in enumerate(rankings, start=1):
                user_id = r['user_id']
                damage = r['total_damage']
                if idx == 1:
                    gems = 1000
                elif idx == 2:
                    gems = 500
                elif idx == 3:
                    gems = 250
                elif idx <= 10:
                    gems = 100
                else:
                    continue
                await currency_system.add_gems(user_id, gems, f"Boss damage rank #{idx}")
                try:
                    user = await bot.fetch_user(int(user_id))
                    if user:
                        embed = discord.Embed(title="🏆 Boss Rewards", color=discord.Color.gold())
                        embed.description = f"You ranked **#{idx}** with **{damage}** damage!"
                        embed.add_field(name="Reward", value=f"💎 {gems} gems")
                        await user.send(embed=embed)
                except:
                    pass


            # --- Award Boss Reaper title to top 1 (with 24h expiration) ---
            top_user_id = rankings[0]['user_id']
            async with bot.db_pool.acquire() as conn_title:
                title_row = await conn_title.fetchrow("SELECT title_id, emoji FROM titles WHERE name = 'Boss Reaper'")
                if title_row:
                    title_id = title_row['title_id']
                    emoji = title_row['emoji'] or '🏷️'
                    expires_at = datetime.now(timezone.utc) + timedelta(days=1)
                    await conn_title.execute("""
                        INSERT INTO user_titles (user_id, title_id, equipped, expires_at)
                        VALUES ($1, $2, FALSE, $3)
                        ON CONFLICT (user_id, title_id) DO UPDATE
                        SET expires_at = $3
                    """, top_user_id, title_id, expires_at)
                    try:
                        user = await bot.fetch_user(int(top_user_id))
                        if user:
                            await user.send(
                                f"🏆 Congratulations! You were the top damage dealer in the Server Boss "
                                f"and have earned the {emoji} **Boss Reaper** title for the next 24 hours!"
                            )
                    except:
                        pass

        # --- Pick a new random boss image ---
        new_image_url = random.choice(BOSS_IMAGES) if BOSS_IMAGES else None

        # --- Reset boss HP and update image ---
        async with bot.db_pool.acquire() as conn3:
            await conn3.execute("""
                UPDATE boss_config
                SET boss_hp = $1, boss_image_url = COALESCE($2, boss_image_url)
                WHERE guild_id = $3
            """, max_hp, new_image_url, guild_id)
            # Clear old attempts/damage
            await conn3.execute("DELETE FROM boss_attempts WHERE reset_date = $1", reset_date)
            await conn3.execute("DELETE FROM boss_damage WHERE reset_date = $1", reset_date)

        # --- Update the boss message if it exists ---
        if channel_id and message_id:
            guild = bot.get_guild(guild_id)
            if guild:
                channel = guild.get_channel(channel_id)
                if channel:
                    try:
                        msg = await channel.fetch_message(message_id)
                        temp_view = BossAttackView(guild_id)
                        embed = await temp_view.build_boss_embed(max_hp, max_hp)
                        await msg.edit(embed=embed)
                    except Exception as e:
                        print(f"Failed to update boss message: {e}")

        # --- Send announcement to the designated channel ---
        if guild:
            async with bot.db_pool.acquire() as conn4:
                announce_id = await conn4.fetchval("SELECT announce_channel_id FROM boss_config WHERE guild_id = $1", guild_id)
            announce_channel = None
            if announce_id:
                announce_channel = guild.get_channel(announce_id)
            if not announce_channel:
                # fallback to boss channel
                announce_channel = guild.get_channel(channel_id)
            if announce_channel:
                try:
                    await announce_channel.send("**Boss has Respawned!**")
                except Exception as e:
                    print(f"Failed to send announcement: {e}")


@boss_reset_task.before_loop
async def before_boss_reset():
    await bot.wait_until_ready()
    while bot.db_pool is None:
        await asyncio.sleep(1)



async def load_boss_persistence():
    print("🔄 load_boss_persistence: started")
    async with bot.db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT guild_id, channel_id, message_id FROM boss_config WHERE message_id IS NOT NULL")
    print(f"🔄 load_boss_persistence: found {len(rows)} boss messages")
    for row in rows:
        guild = bot.get_guild(row['guild_id'])
        if not guild:
            print(f"⚠️ load_boss_persistence: guild {row['guild_id']} not found")
            continue
        channel = guild.get_channel(row['channel_id'])
        if not channel:
            print(f"⚠️ load_boss_persistence: channel {row['channel_id']} not found in guild {guild.id}")
            continue
        print(f"  -> Attempting to reattach boss view in #{channel.name} (message {row['message_id']})")
        try:
            msg = await channel.fetch_message(row['message_id'])
            view = BossAttackView(row['guild_id'])
            await msg.edit(view=view)
            print(f"  ✅ Reattached boss view in #{channel.name}")
        except Exception as e:
            print(f"  ❌ Failed to reattach boss view: {e}")
            traceback.print_exc()
    print("✅ load_boss_persistence: finished")



async def load_shop_persistence(bot):
    shop_cog = bot.get_cog('Shop')
    if shop_cog:
        await shop_cog.load_shop_messages()

async def load_mining_persistence(bot):
    print("🔄 load_mining_persistence: started")
    cog = bot.get_cog('CullingGame')
    if not cog:
        print("❌ load_mining_persistence: CullingGame cog not found!")
        return
    print(f"🔄 load_mining_persistence: found cog, iterating over {len(bot.guilds)} guilds")
    for guild in bot.guilds:
        print(f"  -> Processing guild {guild.id} ({guild.name})")
        try:
            await cog.load_mining_messages(guild.id)
        except Exception as e:
            print(f"❌ Error in load_mining_messages for guild {guild.id}: {e}")
            traceback.print_exc()
    print("✅ load_mining_persistence: finished")



# === RUN BOT ===
if __name__ == "__main__":
    if TOKEN:
        print("\n🚀 Starting bot...")
        bot.run(TOKEN)
    else:
        print("❌ ERROR: No TOKEN found in environment variables!")
        print("💡 Set TOKEN environment variable in Railway")

