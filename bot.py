import sys
import os

# Check Python path BEFORE importing discord
print("=== PYTHON PATH ===")
for path in sys.path:
    print(f"  {path}")
print("==================")

# Force specific import path
import site
site_packages = None
for path in sys.path:
    if 'site-packages' in path:
        site_packages = path
        print(f"📦 Site-packages: {path}")
        break

# List discord installations
import subprocess
result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
print("=== INSTALLED PACKAGES ===")
for line in result.stdout.split('\n'):
    if 'discord' in line.lower():
        print(f"  {line}")
print("==================")

# Now try importing discord
try:
    import discord
    print(f"✅ Imported discord from: {discord.__file__}")
    print(f"✅ Version: {discord.__version__}")
    
    # Check for Bot attribute
    if hasattr(discord, 'Bot'):
        print("✅ discord.Bot attribute exists!")
    else:
        print("❌ discord.Bot attribute missing!")
        print(f"❌ Available attributes: {[x for x in dir(discord) if not x.startswith('_')][:20]}...")
        
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Only proceed if v2 is confirmed
if not hasattr(discord, 'Bot'):
    print("❌ CRITICAL: discord.py v1 installed, cannot continue")
    sys.exit(1)

TOKEN = os.getenv('TOKEN')

# Create bot (v2 style)
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)
print("✅ Bot object created successfully!")

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")

@bot.command()
async def ping(ctx):
    await ctx.respond("🏓 Pong!")

if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Error: No TOKEN environment variable")