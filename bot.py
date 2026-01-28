import discord
from discord.ui import Modal, Select, Button, View
import os

TOKEN = os.getenv('TOKEN')

print(f"✅ Py-cord version: {discord.__version__}")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Bot(intents=intents)

# --- PY-CORD MODAL (CORRECT SYNTAX) ---
class RoleSetupModal(Modal):
    def __init__(self):
        # Py-cord: Set title in __init__, not class definition
        super().__init__(title="Role Setup", timeout=None)
        
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
        # Create confirmation message
        troop = self.troop.values[0]
        languages = ", ".join([lang.capitalize() for lang in self.languages.values]) if self.languages.values else "None"
        server = self.server.values[0]
        
        embed = discord.Embed(
            title="✅ Setup Complete!",
            description=f"**Troop:** {troop.capitalize()}\n"
                       f"**Languages:** {languages}\n"
                       f"**Server:** {server}",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Roles Assigned:",
            value=f"• @{troop.capitalize()}\n• @{server}\n• Language roles",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# --- BUTTON VIEW ---
class SetupView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Start Role Setup", style=discord.ButtonStyle.primary, emoji="⚙️", custom_id="setup_button")
    async def button_callback(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(RoleSetupModal())

# --- SLASH COMMANDS ---
@bot.slash_command(name="ping", description="Check if bot is alive")
async def ping(ctx):
    await ctx.respond("🏓 Pong!")

@bot.slash_command(name="setup", description="Send role setup form")
@discord.default_permissions(administrator=True)
async def setup(ctx):
    # Create the setup embed (like your image)
    embed = discord.Embed(
        title="Channels & Roles",
        description="### Customize\nAnswer questions to get access to more channels and roles.",
        color=0x5865F2  # Discord blurple
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
    
    # Send embed with button
    await ctx.respond(embed=embed, view=SetupView())

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    
    # Make button persistent (works after bot restart)
    bot.add_view(SetupView())
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="for /setup command"
        )
    )
    
    print("✅ Bot is ready! Use /setup in Discord")

# --- RUN BOT ---
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Error: Set TOKEN environment variable")