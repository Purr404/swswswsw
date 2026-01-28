import discord
import os
import sys
import asyncio

TOKEN = os.getenv('TOKEN')

print("=" * 50)
print("🚀 STARTING BOT DIAGNOSTIC")
print("=" * 50)

# 1. Check token exists
if not TOKEN:
    print("❌ CRITICAL: TOKEN environment variable not set!")
    print("Set TOKEN in Railway Variables tab")
    sys.exit(1)

print(f"✅ Token found: {TOKEN[:10]}...")

# 2. Try to validate token
import aiohttp
async def check_token():
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bot {TOKEN}"}
            async with session.get("https://discord.com/api/v10/users/@me", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Token valid! Bot: {data['username']}#{data['discriminator']}")
                    return True
                else:
                    print(f"❌ Token invalid! Status: {resp.status}")
                    return False
    except Exception as e:
        print(f"❌ Token check failed: {e}")
        return False

# Run token check
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
token_valid = loop.run_until_complete(check_token())
loop.close()

if not token_valid:
    print("❌ Cannot proceed with invalid token")
    sys.exit(1)

# 3. Setup bot with detailed logging
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

print("\n🔧 Creating bot instance...")
bot = discord.Bot(intents=intents, debug_guilds=[YOUR_SERVER_ID_HERE])  # Add your server ID

# Add event handlers for connection debugging
@bot.event
async def on_connect():
    print("🔗 CONNECTED to Discord gateway")

@bot.event
async def on_ready():
    print("\n" + "=" * 50)
    print(f"✅ BOT IS ONLINE: {bot.user}")
    print(f"✅ ID: {bot.user.id}")
    print(f"✅ Guilds: {len(bot.guilds)}")
    
    for guild in bot.guilds:
        print(f"   - {guild.name} ({guild.id})")
        # Try to get member count
        try:
            await guild.chunk()
            print(f"     Members: {guild.member_count}")
        except:
            print(f"     Members: Could not fetch")
    
    print("=" * 50)
    
    # Set visible online status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Discord"
        ),
        status=discord.Status.online
    )
    print("✅ Presence set to ONLINE")
    
    # Keep-alive
    print("✅ Bot is running...")

@bot.event
async def on_disconnect():
    print("🔌 DISCONNECTED from Discord")

@bot.event
async def on_resumed():
    print("↩️ RESUMED connection")

# Simple test command
@bot.slash_command(name="status", description="Check bot status")
async def status(ctx):
    latency = round(bot.latency * 1000) if bot.latency > 0 else "N/A"
    await ctx.respond(
        f"**Bot Status**\n"
        f"• Online: ✅\n"
        f"• Latency: {latency}ms\n"
        f"• Guilds: {len(bot.guilds)}\n"
        f"• Uptime: Ready!",
        ephemeral=True
    )

print("\n🚀 Starting bot connection...")
print("This may take 10-30 seconds...")

try:
    bot.run(TOKEN, reconnect=True, log_handler=None)
except discord.LoginFailure:
    print("\n❌ LOGIN FAILED: Invalid token!")
    print("1. Go to Discord Developer Portal")
    print("2. Click 'Reset Token'")
    print("3. Copy new token")
    print("4. Update Railway TOKEN variable")
    print("5. Redeploy")
except Exception as e:
    print(f"\n❌ BOT CRASHED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()