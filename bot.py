import discord
from discord.ext import commands
import os

TOKEN = os.getenv('TOKEN')

# Use commands.Bot for v1 compatibility
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="for !setup"
        )
    )

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    """Send setup message"""
    embed = discord.Embed(
        title="Channels & Roles",
        description="Click the button below to setup your roles",
        color=discord.Color.blue()
    )
    
    # Send a button that users can click
    # Note: Buttons in v1 require different syntax
    await ctx.send(embed=embed)

if __name__ == "__main__":
    bot.run(TOKEN)