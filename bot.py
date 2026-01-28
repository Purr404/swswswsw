import discord
from discord.ui import Modal, Select, Button, View
import os

TOKEN = os.getenv('TOKEN')

print(f"✅ Py-cord version: {discord.__version__}")

# Use commands.Bot but disable the default help command
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None  # Disable default help
)

# --- MODAL FORM ---
class RoleSetupModal(Modal):
    def __init__(self):
        super().__init__(title="Channels & Roles Setup", timeout=None)
        
        self.troop = Select(
            placeholder="Select your main troop type *",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="Horde", value="horde", emoji="👹"),
                discord.SelectOption(label="League", value="league", emoji="🛡️"),
                discord.SelectOption(label="Nature", value="nature", emoji="🌿")
            ]
        )
        self.add_item(self.troop)
        
        self.languages = Select(
            placeholder="Select any languages you speak",
            min_values=0,
            max_values=4,
            options=[
                discord.SelectOption(label="Chinese", value="chinese", emoji="🇨🇳"),
                discord.SelectOption(label="English", value="english", emoji="🇬🇧"),
                discord.SelectOption(label="Japanese", value="japanese", emoji="🇯🇵"),
                discord.SelectOption(label="Korean", value="korean", emoji="🇰🇷")
            ]
        )
        self.add_item(self.languages)
        
        self.server = Select(
            placeholder="Server range of your main account *",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="Server 1 - Server 107", value="1-107"),
                discord.SelectOption(label="Server 108 - Server 224", value="108-224"),
                discord.SelectOption(label="Server 225 or Above", value="225+")
            ]
        )
        self.add_item(self.server)
    
    async def callback(self, interaction: discord.Interaction):
        troop = self.troop.values[0].capitalize()
        languages = ", ".join([lang.capitalize() for lang in self.languages.values]) if self.languages.values else "None"
        server = self.server.values[0]
        
        embed = discord.Embed(
            title="✅ Setup Complete!",
            description="Your roles have been assigned.",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Your Selections:",
            value=f"**Troop:** {troop}\n"
                  f"**Languages:** {languages}\n"
                  f"**Server:** {server}",
            inline=False
        )
        
        embed.set_footer(text="You now have access to role-specific channels!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        print(f"User {interaction.user} selected: Troop={troop}, Languages={languages}, Server={server}")

# --- BUTTON VIEW ---
class SetupView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Start Role Setup", style=discord.ButtonStyle.primary, emoji="⚙️", custom_id="setup_button")
    async def button_callback(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(RoleSetupModal())

# --- PREFIX COMMANDS ---
@bot.command(name="ping")
async def ping(ctx):
    """Check if bot is alive"""
    await ctx.send("🏓 Pong!")

@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup(ctx):
    """Send the role setup form"""
    embed = discord.Embed(
        title="Channels & Roles",
        description="### Customize\nAnswer questions to get access to more channels and roles.",
        color=0x5865F2
    )
    
    embed.add_field(
        name="Please select your main troop type *",
        value="• 👹 Horde\n• 🛡️ League\n• 🌿 Nature",
        inline=False
    )
    
    embed.add_field(
        name="Please select any languages you speak",
        value="• 🇨🇳 Chinese\n• 🇬🇧 English\n• 🇯🇵 Japanese\n• 🇰🇷 Korean",
        inline=False
    )
    
    embed.add_field(
        name="Please select the server range of your main account *",
        value="• Server 1 - Server 107\n• Server 108 - Server 224\n• Server 225 or Above",
        inline=False
    )
    
    embed.set_footer(text="Click the button below to begin setup")
    
    await ctx.send(embed=embed, view=SetupView())

@bot.command(name="commands")
async def commands_list(ctx):
    """Show all commands"""
    embed = discord.Embed(
        title="Bot Commands",
        description="Prefix: `!`",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🎮 General",
        value="• `!ping` - Check if bot is alive\n"
              "• `!commands` - Show this message",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Setup (Admin Only)",
        value="• `!setup` - Send role setup form in this channel",
        inline=False
    )
    
    await ctx.send(embed=embed)

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    
    # Make button persistent
    bot.add_view(SetupView())
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="for !setup command"
        ),
        status=discord.Status.online
    )
    
    print("✅ Prefix command bot is ready!")
    print("✅ Commands: !ping, !setup, !commands")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need administrator permissions to use this command!")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore unknown commands
    else:
        await ctx.send(f"❌ Error: {str(error)}")

# --- RUN BOT ---
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Error: No TOKEN")