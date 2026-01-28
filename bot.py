import discord
import os

print(f"Python version check...")
print(f"Discord import check...")

TOKEN = os.getenv('TOKEN')

# Debug: Check discord.py version
try:
    print(f"Discord.py version: {discord.__version__}")
    if discord.__version__.startswith('2'):
        print("✅ Discord.py v2 detected!")
    else:
        print(f"❌ Wrong version: {discord.__version__}")
except:
    print("❌ Cannot get discord version")

# Initialize bot (v2 style)
try:
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = discord.Bot(intents=intents)
    print("✅ discord.Bot() created successfully!")
    
except Exception as e:
    print(f"❌ Error creating bot: {e}")
    print("❌ This means discord.py v1 is installed")
    exit(1)

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