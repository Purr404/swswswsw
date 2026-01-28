import discord
import os

TOKEN = os.getenv('TOKEN')

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}!")

@bot.command()
async def ping(ctx):
    await ctx.respond("🏓 Pong!")

bot.run(TOKEN)