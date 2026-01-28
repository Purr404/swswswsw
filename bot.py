import discord
from discord.ui import Modal, Select, View, Button
import os

TOKEN = os.getenv('TOKEN')

bot = discord.Bot(intents=discord.Intents.all())

# --- ENHANCED MODAL (Like your image) ---
class EnhancedSetupModal(Modal):
    def __init__(self):
        super().__init__(title="Channels & Roles", timeout=None)
        
    async def on_submit(self, interaction: discord.Interaction):
        # Get all selections
        troop = self.children[0].values[0] if self.children[0].values else None
        languages = self.children[1].values if self.children[1].values else []
        server = self.children[2].values[0] if self.children[2].values else None
        
        # Create confirmation
        embed = discord.Embed(
            title="✅ Setup Complete!",
            color=discord.Color.green()
        )
        
        if troop:
            embed.add_field(name="Troop Type", value=troop, inline=True)
        
        if languages:
            embed.add_field(name="Languages", value=", ".join(languages), inline=True)
        
        if server:
            embed.add_field(name="Server Range", value=server, inline=True)
        
        embed.set_footer(text="Roles have been assigned to you")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # TODO: Add role assignment logic here

# --- FUNCTION TO CREATE THE SETUP MESSAGE ---
async def create_setup_message(channel):
    """Creates a persistent setup message in the channel"""
    
    # Create the embed (like your image)
    embed = discord.Embed(
        title="Channels & Roles",
        description="### Customize\nSelect your preferences to access channels and roles.",
        color=0x5865F2
    )
    
    # Create a view with a button that opens the modal
    class OpenModalView(View):
        def __init__(self):
            super().__init__(timeout=None)
        
        @discord.ui.button(label="Start Customization", style=discord.ButtonStyle.primary, emoji="⚙️", custom_id="open_modal")
        async def open_modal(self, interaction: discord.Interaction, button: Button):
            # Create and send modal
            modal = EnhancedSetupModal()
            
            # Add troop selection (required)
            modal.add_item(Select(
                placeholder="Select your main troop type *",
                min_values=1,
                max_values=1,
                options=[
                    discord.SelectOption(label="Horde", emoji="👹", description="Join the Horde forces"),
                    discord.SelectOption(label="League", emoji="🛡️", description="Join the League alliance"),
                    discord.SelectOption(label="Nature", emoji="🌿", description="Join Nature's embrace")
                ]
            ))
            
            # Add language selection (optional, multiple)
            modal.add_item(Select(
                placeholder="Select any languages you speak",
                min_values=0,
                max_values=4,
                options=[
                    discord.SelectOption(label="Chinese", emoji="🇨🇳", description="中文"),
                    discord.SelectOption(label="English", emoji="🇬🇧", description="English"),
                    discord.SelectOption(label="Japanese", emoji="🇯🇵", description="日本語"),
                    discord.SelectOption(label="Korean", emoji="🇰🇷", description="한국어")
                ]
            ))
            
            # Add server selection (required)
            modal.add_item(Select(
                placeholder="Select your server range *",
                min_values=1,
                max_values=1,
                options=[
                    discord.SelectOption(label="Server 1 - Server 107", description="Early servers"),
                    discord.SelectOption(label="Server 108 - Server 224", description="Mid-range servers"),
                    discord.SelectOption(label="Server 225 or Above", description="Newer servers")
                ]
            ))
            
            await interaction.response.send_modal(modal)
    
    # Send the message
    message = await channel.send(embed=embed, view=OpenModalView())
    
    # Pin it for visibility
    try:
        await message.pin()
    except:
        pass
    
    return message

# --- SLASH COMMANDS ---
@bot.slash_command(name="create_setup", description="Create setup message in this channel (admin)")
async def create_setup(ctx):
    if ctx.author.guild_permissions.administrator:
        await create_setup_message(ctx.channel)
        await ctx.respond("✅ Setup message created!", ephemeral=True)
    else:
        await ctx.respond("❌ You need admin permissions!", ephemeral=True)

@bot.slash_command(name="setup_channel", description="Create setup in specific channel (admin)")
async def setup_channel(ctx, channel: discord.TextChannel):
    if ctx.author.guild_permissions.administrator:
        await create_setup_message(channel)
        await ctx.respond(f"✅ Setup created in {channel.mention}!", ephemeral=True)
    else:
        await ctx.respond("❌ You need admin permissions!", ephemeral=True)

# --- PREFIX COMMANDS ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.content.startswith('!'):
        content = message.content.lower()
        
        if content == '!createsetup':
            if message.author.guild_permissions.administrator:
                await create_setup_message(message.channel)
                await message.add_reaction('✅')
        
        elif content == '!ping':
            await message.channel.send('🏓 Pong!')

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="setup messages"
        )
    )

# --- RUN ---
if TOKEN:
    bot.run(TOKEN)