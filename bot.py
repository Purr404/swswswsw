import discord
from discord.ui import Modal, Select, View, Button
import os
import asyncio

TOKEN = os.getenv('TOKEN')

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

# --- SIMPLIFIED MODAL (More Reliable) ---
class SetupModal(Modal):
    def __init__(self):
        super().__init__(title="Setup Your Roles", timeout=300)  # 5 minute timeout
        
        # Troop selection
        self.troop_select = Select(
            placeholder="Select your main troop type *",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="Horde", emoji="👹"),
                discord.SelectOption(label="League", emoji="🛡️"),
                discord.SelectOption(label="Nature", emoji="🌿")
            ]
        )
        self.add_item(self.troop_select)
        
        # Language selection
        self.lang_select = Select(
            placeholder="Select languages you speak",
            min_values=0,
            max_values=4,
            options=[
                discord.SelectOption(label="Chinese", emoji="🇨🇳"),
                discord.SelectOption(label="English", emoji="🇬🇧"),
                discord.SelectOption(label="Japanese", emoji="🇯🇵"),
                discord.SelectOption(label="Korean", emoji="🇰🇷")
            ]
        )
        self.add_item(self.lang_select)
        
        # Server selection
        self.server_select = Select(
            placeholder="Select your server range *",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="Server 1 - 107"),
                discord.SelectOption(label="Server 108 - 224"),
                discord.SelectOption(label="Server 225+")
            ]
        )
        self.add_item(self.server_select)
    
    async def callback(self, interaction: discord.Interaction):
        # Defer first to prevent timeout
        await interaction.response.defer(ephemeral=True)
        
        # Get values
        troop = self.troop_select.values[0] if self.troop_select.values else "Not selected"
        languages = ", ".join(self.lang_select.values) if self.lang_select.values else "None"
        server = self.server_select.values[0] if self.server_select.values else "Not selected"
        
        # Create simple response first
        await interaction.followup.send(
            f"✅ **Setup Complete!**\n"
            f"**Troop:** {troop}\n"
            f"**Languages:** {languages}\n"
            f"**Server:** {server}\n\n"
            f"Your roles will be assigned shortly.",
            ephemeral=True
        )
        
        print(f"[SETUP] {interaction.user} chose: {troop}, {languages}, {server}")

# --- VIEW WITH RETRY LOGIC ---
class SetupView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Start Customization", style=discord.ButtonStyle.primary, emoji="⚙️", custom_id="setup_start")
    async def start_callback(self, interaction: discord.Interaction, button: Button):
        try:
            # Create and send modal immediately
            modal = SetupModal()
            await interaction.response.send_modal(modal)
            print(f"[MODAL] Opened for {interaction.user}")
        except Exception as e:
            print(f"[ERROR] Modal failed: {e}")
            await interaction.response.send_message(
                "❌ Failed to open setup form. Please try again.",
                ephemeral=True
            )

# --- CREATE SETUP MESSAGE ---
async def send_setup_embed(channel):
    """Send the setup message to a channel"""
    
    embed = discord.Embed(
        title="Channels & Roles",
        description=(
            "### Customize\n"
            "Set up your preferences to access server channels and roles.\n\n"
            "**Please select your main troop type ***\n"
            "• Horde\n• League\n• Nature\n\n"
            "**Please select any languages you speak**\n"
            "• Chinese\n• English\n• Japanese\n• Korean\n\n"
            "**Please select your server range ***\n"
            "• Server 1 - 107\n• Server 108 - 224\n• Server 225+"
        ),
        color=0x5865F2
    )
    
    embed.set_footer(text="Click the button below to begin")
    
    view = SetupView()
    message = await channel.send(embed=embed, view=view)
    
    # Try to pin
    try:
        await message.pin()
        print(f"[SETUP] Message pinned in {channel.name}")
    except:
        pass
    
    return message

# --- COMMANDS ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Prefix commands
    if message.content.lower().startswith('!createsetup'):
        if message.author.guild_permissions.administrator:
            await message.delete()
            await send_setup_embed(message.channel)
        else:
            await message.channel.send("❌ Admin only!", delete_after=5)
    
    elif message.content.lower() == '!ping':
        await message.channel.send('🏓 Pong!')
    
    elif message.content.lower() == '!help':
        embed = discord.Embed(
            title="Bot Commands",
            description="**Admin:**\n!createsetup - Create role setup\n\n**Everyone:**\n!ping - Check bot status",
            color=0x5865F2
        )
        await message.channel.send(embed=embed)

# --- SLASH COMMANDS (Alternative) ---
@bot.slash_command(name="setup", description="Create role setup message (admin)")
async def slash_setup(ctx):
    if ctx.author.guild_permissions.administrator:
        await ctx.defer(ephemeral=True)
        await send_setup_embed(ctx.channel)
        await ctx.followup.send("✅ Setup created!", ephemeral=True)
    else:
        await ctx.respond("❌ Admin only!", ephemeral=True)

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    bot.add_view(SetupView())  # Make view persistent
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="for !createsetup"
        )
    )
    
    print("✅ Bot ready! Use !createsetup or /setup")

# Error handling
@bot.event
async def on_application_command_error(ctx, error):
    print(f"[SLASH ERROR] {error}")
    await ctx.respond(f"❌ Error: {str(error)[:100]}", ephemeral=True)

# --- RUN ---
if __name__ == "__main__":
    if TOKEN:
        print("🚀 Starting bot...")
        bot.run(TOKEN)
    else:
        print("❌ ERROR: No TOKEN environment variable")
        print("Set TOKEN in Railway Variables")