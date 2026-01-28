import discord
from discord.ext import commands
import os

TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    print("✅ Bot is ready!")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(
        title="Role Setup",
        description="**Please select your main troop type:**\n• Horde\n• League\n• Nature\n\nReact with emojis to get roles!",
        color=discord.Color.blue()
    )
    msg = await ctx.send(embed=embed)
    # Add reactions for role selection
    await msg.add_reaction("👹")  # Horde
    await msg.add_reaction("🛡️")  # League
    await msg.add_reaction("🌿")  # Nature

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    
    # Map reactions to roles
    role_map = {
        "👹": "Horde",
        "🛡️": "League", 
        "🌿": "Nature"
    }
    
    if str(reaction.emoji) in role_map:
        guild = reaction.message.guild
        role_name = role_map[str(reaction.emoji)]
        role = discord.utils.get(guild.roles, name=role_name)
        
        if not role:
            role = await guild.create_role(name=role_name, color=discord.Color.blue())
        
        await user.add_roles(role)
        
        # Send DM confirmation
        try:
            await user.send(f"✅ You've been given the **{role_name}** role!")
        except:
            pass

if __name__ == "__main__":
    bot.run(TOKEN)