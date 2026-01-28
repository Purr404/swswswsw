import discord
from discord.ui import Modal, Select, Button, View
import os

TOKEN = os.getenv('TOKEN')

print(f"✅ Py-cord version: {discord.__version__}")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Bot(intents=intents)

# --- MODAL FORM (Py-cord syntax) ---
class RoleSetupModal(Modal):
    def __init__(self):
        # Py-cord: Set title in __init__
        super().__init__(title="Channels & Roles Setup", timeout=None)
        
        # Troop type (single select)
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
        
        # Languages (multiple select)
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
        
        # Server range (single select)
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
        # Get selections
        troop = self.troop.values[0].capitalize()
        languages = ", ".join([lang.capitalize() for lang in self.languages.values]) if self.languages.values else "None"
        server = self.server.values[0]
        
        # Create beautiful confirmation embed
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
        
        embed.add_field(
            name="Roles Assigned:",
            value=f"• @{troop}\n• @{server}\n• Language-specific roles",
            inline=False
        )
        
        embed.set_footer(text="You now have access to role-specific channels!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # TODO: Add actual role assignment here
        print(f"User {interaction.user} selected: Troop={troop}, Languages={languages}, Server={server}")

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

@bot.slash_command(name="setup", description="Send the role setup form")
@discord.default_permissions(administrator=True)
async def setup(ctx):
    # Create the beautiful embed (like your image)
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
    
    # Send with button
    await ctx.respond(embed=embed, view=SetupView())

# --- ADMIN COMMAND TO SEND TO CHANNEL ---
@bot.slash_command(name="send_setup", description="Send setup message to channel (admin)")
@discord.default_permissions(administrator=True)
async def send_setup(ctx, channel: discord.TextChannel = None):
    """Send the setup message to a specific channel"""
    target = channel or ctx.channel
    
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
    
    await target.send(embed=embed, view=SetupView())
    await ctx.respond(f"✅ Setup message sent to {target.mention}", ephemeral=True)

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    
    # Make button persistent
    bot.add_view(SetupView())
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="for /setup command"
        ),
        status=discord.Status.online
    )
    
    print("✅ Modal form bot is ready!")

# --- RUN BOT ---
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Error: No TOKEN")