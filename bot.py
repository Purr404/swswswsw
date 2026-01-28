import discord
from discord.ext import commands
from discord.ui import Modal, Select, View, Button, TextInput

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- MODAL 1: Main Setup Form ---
class SetupModal(Modal, title="Channels & Roles Setup"):
    def __init__(self):
        super().__init__(timeout=None)
        
        # Dropdown for troop type
        self.troop_type = Select(
            placeholder="Select your main troop type *",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="Horde", value="horde", emoji="👹"),
                discord.SelectOption(label="League", value="league", emoji="🛡️", default=True),
                discord.SelectOption(label="Nature", value="nature", emoji="🌿")
            ]
        )
        self.add_item(self.troop_type)
        
        # Multiple select for languages
        self.languages = Select(
            placeholder="Select any languages you speak",
            min_values=0,
            max_values=4,
            options=[
                discord.SelectOption(label="Chinese", value="chinese", emoji="🇨🇳"),
                discord.SelectOption(label="English", value="english", emoji="🇬🇧", default=True),
                discord.SelectOption(label="Japanese", value="japanese", emoji="🇯🇵"),
                discord.SelectOption(label="Korean", value="korean", emoji="🇰🇷", default=True)
            ]
        )
        self.add_item(self.languages)
        
        # Dropdown for server range
        self.server_range = Select(
            placeholder="Server range of your main account *",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="Server 1 - Server 107", value="1-107"),
                discord.SelectOption(label="Server 108 - Server 224", value="108-224"),
                discord.SelectOption(label="Server 225 or Above", value="225+", default=True)
            ]
        )
        self.add_item(self.server_range)

    async def on_submit(self, interaction: discord.Interaction):
        # Process the selections
        troop = self.troop_type.values[0]
        languages = self.languages.values
        server = self.server_range.values[0]
        
        # Find or create roles (simplified - you'd want error handling)
        guild = interaction.guild
        
        # Assign troop role
        troop_role = discord.utils.get(guild.roles, name=troop.capitalize())
        if not troop_role:
            troop_role = await guild.create_role(name=troop.capitalize(), color=discord.Color.blue())
        
        # Assign language roles
        lang_roles = []
        for lang in languages:
            lang_role = discord.utils.get(guild.roles, name=lang.capitalize())
            if not lang_role:
                lang_role = await guild.create_role(name=lang.capitalize(), color=discord.Color.green())
            lang_roles.append(lang_role)
        
        # Assign server role
        server_role = discord.utils.get(guild.roles, name=server)
        if not server_role:
            server_role = await guild.create_role(name=server, color=discord.Color.red())
        
        # Apply roles to user
        member = interaction.user
        await member.add_roles(troop_role, *lang_roles, server_role)
        
        # Create confirmation embed
        embed = discord.Embed(
            title="✅ Setup Complete!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Roles Assigned:",
            value=f"**Troop:** {troop.capitalize()}\n"
                  f"**Languages:** {', '.join(lang.capitalize() for lang in languages) or 'None'}\n"
                  f"**Server Range:** {server}",
            inline=False
        )
        
        embed.set_footer(text="You now have access to additional channels!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# --- BUTTON to open the modal ---
class SetupButton(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Start Setup", style=discord.ButtonStyle.primary, emoji="⚙️", custom_id="setup_button")
    async def setup_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(SetupModal())

# --- COMMAND to send the initial message ---
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    """Send the setup message with button"""
    
    embed = discord.Embed(
        title="Channels & Roles",
        description="### Customize\nAnswer questions to get access to more channels and roles.",
        color=0x5865F2  # Discord blurple
    )
    
    embed.add_field(
        name="Please select your main troop type *",
        value="• Horde\n• League\n• Nature",
        inline=False
    )
    
    embed.add_field(
        name="Please select any languages you speak",
        value="• Chinese\n• English\n• Japanese\n• Korean",
        inline=False
    )
    
    embed.add_field(
        name="Please select the server range of your main account *",
        value="• Server 1 - Server 107\n• Server 108 - Server 224\n• Server 225 or Above",
        inline=False
    )
    
    embed.set_footer(text="Click the button below to begin setup")
    
    view = SetupButton()
    await ctx.send(embed=embed, view=view)
    
    # Also send as a persistent message (can be pinned)
    await ctx.message.delete()

# --- Event for bot ready ---
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    # Add persistent view
    bot.add_view(SetupButton())
    
    # Change bot status
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="for !setup command"
    ))

# --- Run the bot ---
bot.run('YOUR_BOT_TOKEN_HERE')