import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, Select
import os

TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Use discord.Bot for v2
bot = discord.Bot(intents=intents)

# --- MODAL FORM ---
class RoleSetupModal(Modal):
    def __init__(self):
        super().__init__(title="Role Setup", timeout=None)
        
        self.troop = Select(
            placeholder="Select troop type",
            options=[
                discord.SelectOption(label="Horde", emoji="👹"),
                discord.SelectOption(label="League", emoji="🛡️"),
                discord.SelectOption(label="Nature", emoji="🌿")
            ]
        )
        self.add_item(self.troop)
        
        self.languages = Select(
            placeholder="Select languages",
            min_values=0,
            max_values=4,
            options=[
                discord.SelectOption(label="Chinese", emoji="🇨🇳"),
                discord.SelectOption(label="English", emoji="🇬🇧"),
                discord.SelectOption(label="Japanese", emoji="🇯🇵"),
                discord.SelectOption(label="Korean", emoji="🇰🇷")
            ]
        )
        self.add_item(self.languages)
        
        self.server = Select(
            placeholder="Select server range",
            options=[
                discord.SelectOption(label="Server 1-107"),
                discord.SelectOption(label="Server 108-224"),
                discord.SelectOption(label="Server 225+")
            ]
        )
        self.add_item(self.server)
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"✅ Setup complete!\n"
            f"Troop: {self.troop.values[0]}\n"
            f"Languages: {', '.join(self.languages.values) if self.languages.values else 'None'}\n"
            f"Server: {self.server.values[0]}",
            ephemeral=True
        )

# --- BUTTON VIEW ---
class SetupView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Start Setup", style=discord.ButtonStyle.primary, emoji="⚙️")
    async def button_callback(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(RoleSetupModal())

# --- SLASH COMMANDS ---
@bot.slash_command(name="ping", description="Check if bot is alive")
async def ping(ctx):
    await ctx.respond("🏓 Pong!")

@bot.slash_command(name="setup", description="Setup roles (admin only)")
@discord.default_permissions(administrator=True)
async def setup(ctx):
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
    
    await ctx.respond(embed=embed, view=SetupView())

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    print(f"✅ Discord.py version: {discord.__version__}")
    
    # Add persistent view
    bot.add_view(SetupView())
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="for /setup"
        )
    )

# --- START BOT ---
if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ Error: Set TOKEN environment variable")