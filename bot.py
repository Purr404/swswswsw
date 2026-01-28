import discord
import os
import sys
import asyncio

TOKEN = os.getenv('TOKEN')

print("=" * 50)
print("🚀 STARTING BOT")
print("=" * 50)

if not TOKEN:
    print("❌ No TOKEN found")
    sys.exit(1)

print(f"✅ Token: {TOKEN[:15]}...")

# Setup bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# SIMPLIFIED: No debug_guilds
bot = discord.Bot(intents=intents)

# Connection events
@bot.event
async def on_connect():
    print("🔗 Connected to Discord")

@bot.event
async def on_ready():
    print("\n" + "=" * 50)
    print(f"✅ BOT ONLINE: {bot.user}")
    print(f"✅ ID: {bot.user.id}")
    
    # Set online status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="for /setup"
        ),
        status=discord.Status.online
    )
    print("✅ Presence set to ONLINE")
    print("=" * 50)

@bot.event
async def on_disconnect():
    print("🔌 Disconnected")

# Your modal form code will go here later
@bot.slash_command(name="ping", description="Check if bot is alive")
async def ping(ctx):
    await ctx.respond("🏓 Pong!")

@bot.slash_command(name="setup", description="Setup roles")
@discord.default_permissions(administrator=True)
async def setup(ctx):
    await ctx.respond("✅ Setup command works! Modal coming soon...")

print("\n🚀 Connecting to Discord...")
try:
    bot.run(TOKEN, reconnect=True)
except Exception as e:
    print(f"❌ Error: {e}")