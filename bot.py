import discord
from discord.ext import commands
from discord.ui import View, Button
import os

TOKEN = os.getenv('TOKEN')

# Use commands.Bot for prefix commands
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Store user selections
user_selections = {}

# --- MAIN SETUP VIEW ---
class RoleSetupView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.selected_troop = None
        self.selected_languages = []
        self.selected_server = None
    
    # --- TROOP SELECTION (Row 0) ---
    @discord.ui.button(label="Horde", style=discord.ButtonStyle.gray, emoji="👹", row=0, custom_id="horde_btn")
    async def horde_btn(self, interaction: discord.Interaction, button: Button):
        await self.handle_troop_selection(interaction, "Horde", button)
    
    @discord.ui.button(label="League", style=discord.ButtonStyle.gray, emoji="🛡️", row=0, custom_id="league_btn")
    async def league_btn(self, interaction: discord.Interaction, button: Button):
        await self.handle_troop_selection(interaction, "League", button)
    
    @discord.ui.button(label="Nature", style=discord.ButtonStyle.gray, emoji="🌿", row=0, custom_id="nature_btn")
    async def nature_btn(self, interaction: discord.Interaction, button: Button):
        await self.handle_troop_selection(interaction, "Nature", button)
    
    async def handle_troop_selection(self, interaction, troop, clicked_button):
        # Reset all troop buttons to gray
        for child in self.children:
            if child.custom_id in ["horde_btn", "league_btn", "nature_btn"]:
                child.style = discord.ButtonStyle.gray
        
        # Set selected button to green
        clicked_button.style = discord.ButtonStyle.green
        self.selected_troop = troop
        
        # Update message
        embed = interaction.message.embeds[0]
        embed.set_field_at(
            0,
            name="Please select your main troop type *",
            value=f"✅ {troop}\n⬜ League\n⬜ Nature" if troop == "Horde" else 
                  f"⬜ Horde\n✅ {troop}\n⬜ Nature" if troop == "League" else
                  f"⬜ Horde\n⬜ League\n✅ {troop}",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(f"✅ Selected troop: **{troop}**", ephemeral=True)
    
    # --- LANGUAGE SELECTION (Row 1) ---
    @discord.ui.button(label="Chinese", style=discord.ButtonStyle.gray, emoji="🇨🇳", row=1, custom_id="chinese_btn")
    async def chinese_btn(self, interaction: discord.Interaction, button: Button):
        await self.toggle_language(interaction, "Chinese", button)
    
    @discord.ui.button(label="English", style=discord.ButtonStyle.green, emoji="🇬🇧", row=1, custom_id="english_btn")
    async def english_btn(self, interaction: discord.Interaction, button: Button):
        await self.toggle_language(interaction, "English", button)
    
    @discord.ui.button(label="Japanese", style=discord.ButtonStyle.gray, emoji="🇯🇵", row=1, custom_id="japanese_btn")
    async def japanese_btn(self, interaction: discord.Interaction, button: Button):
        await self.toggle_language(interaction, "Japanese", button)
    
    @discord.ui.button(label="Korean", style=discord.ButtonStyle.green, emoji="🇰🇷", row=1, custom_id="korean_btn")
    async def korean_btn(self, interaction: discord.Interaction, button: Button):
        await self.toggle_language(interaction, "Korean", button)
    
    async def toggle_language(self, interaction, language, button):
        if language in self.selected_languages:
            # Remove if already selected
            self.selected_languages.remove(language)
            button.style = discord.ButtonStyle.gray
        else:
            # Add if not selected
            self.selected_languages.append(language)
            button.style = discord.ButtonStyle.green
        
        # Update message
        await interaction.response.edit_message(view=self)
        langs_text = ", ".join(self.selected_languages) if self.selected_languages else "None"
        await interaction.followup.send(f"🌐 Languages: **{langs_text}**", ephemeral=True)
    
    # --- SERVER SELECTION (Row 2) ---
    @discord.ui.button(label="Server 1-107", style=discord.ButtonStyle.gray, row=2, custom_id="server1_btn")
    async def server1_btn(self, interaction: discord.Interaction, button: Button):
        await self.handle_server_selection(interaction, "1-107", button)
    
    @discord.ui.button(label="Server 108-224", style=discord.ButtonStyle.gray, row=2, custom_id="server2_btn")
    async def server2_btn(self, interaction: discord.Interaction, button: Button):
        await self.handle_server_selection(interaction, "108-224", button)
    
    @discord.ui.button(label="Server 225+", style=discord.ButtonStyle.green, row=2, custom_id="server3_btn")
    async def server3_btn(self, interaction: discord.Interaction, button: Button):
        await self.handle_server_selection(interaction, "225+", button)
    
    async def handle_server_selection(self, interaction, server, clicked_button):
        # Reset all server buttons
        for child in self.children:
            if child.custom_id in ["server1_btn", "server2_btn", "server3_btn"]:
                child.style = discord.ButtonStyle.gray
        
        # Set selected to green
        clicked_button.style = discord.ButtonStyle.green
        self.selected_server = server
        
        # Update message
        embed = interaction.message.embeds[0]
        embed.set_field_at(
            2,
            name="Please select the server range of your main account *",
            value=f"⬜ 1-107\n⬜ 108-224\n✅ 225+" if server == "225+" else
                  f"⬜ 1-107\n✅ 108-224\n⬜ 225+" if server == "108-224" else
                  f"✅ 1-107\n⬜ 108-224\n⬜ 225+",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(f"🌐 Selected server: **{server}**", ephemeral=True)
    
    # --- SUBMIT BUTTON (Row 3) ---
    @discord.ui.button(label="Submit Setup", style=discord.ButtonStyle.primary, emoji="✅", row=3, custom_id="submit_btn")
    async def submit_btn(self, interaction: discord.Interaction, button: Button):
        # Validate selections
        if not self.selected_troop:
            await interaction.response.send_message("❌ Please select a troop type!", ephemeral=True)
            return
        
        if not self.selected_server:
            await interaction.response.send_message("❌ Please select a server range!", ephemeral=True)
            return
        
        # Store user data
        user_id = str(interaction.user.id)
        user_selections[user_id] = {
            'troop': self.selected_troop,
            'languages': self.selected_languages,
            'server': self.selected_server
        }
        
        # Create confirmation embed
        embed = discord.Embed(
            title="✅ Setup Complete!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Your Selections:",
            value=f"**Troop:** {self.selected_troop}\n"
                  f"**Languages:** {', '.join(self.selected_languages) if self.selected_languages else 'None'}\n"
                  f"**Server:** {self.selected_server}",
            inline=False
        )
        
        embed.set_footer(text="Your roles have been assigned!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Log
        print(f"[SETUP] {interaction.user} completed setup")

# --- PREFIX COMMANDS ---
@bot.command(name="createsetup")
@commands.has_permissions(administrator=True)
async def createsetup(ctx):
    """Create interactive setup message"""
    embed = discord.Embed(
        title="Channels & Roles",
        description="### Customize\nAnswer questions to get access to more channels and roles.",
        color=0x5865F2
    )
    
    # Initial state (like your photo)
    embed.add_field(
        name="Please select your main troop type *",
        value="✅ Horde\n⬜ League\n⬜ Nature",
        inline=False
    )
    
    embed.add_field(
        name="Please select any languages you speak",
        value="⬜ Chinese\n✅ English\n⬜ Japanese\n✅ Korean",
        inline=False
    )
    
    embed.add_field(
        name="Please select the server range of your main account *",
        value="⬜ Server 1 - 107\n⬜ Server 108 - 224\n✅ Server 225+",
        inline=False
    )
    
    embed.set_footer(text="Click buttons to select, then click Submit")
    
    await ctx.send(embed=embed, view=RoleSetupView())
    await ctx.message.delete()

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command(name="mydata")
async def mydata(ctx):
    """Check your stored data"""
    user_id = str(ctx.author.id)
    if user_id in user_selections:
        data = user_selections[user_id]
        embed = discord.Embed(
            title="Your Setup Data",
            color=discord.Color.blue()
        )
        embed.add_field(name="Troop", value=data['troop'])
        embed.add_field(name="Languages", value=', '.join(data['languages']) if data['languages'] else "None")
        embed.add_field(name="Server", value=data['server'])
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ You haven't completed the setup!")

@bot.command(name="help")
async def help_command(ctx):
    """Show help"""
    embed = discord.Embed(
        title="Bot Commands",
        description="Prefix: `!`",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="General",
        value="• `!ping` - Check bot status\n• `!help` - Show this message",
        inline=False
    )
    
    embed.add_field(
        name="Setup (Admin Only)",
        value="• `!createsetup` - Create role setup message",
        inline=False
    )
    
    embed.add_field(
        name="User Commands",
        value="• `!mydata` - Check your setup data",
        inline=False
    )
    
    await ctx.send(embed=embed)

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    # Make view persistent
    bot.add_view(RoleSetupView())
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="for !createsetup"
        )
    )
    print("✅ Button setup bot ready!")
    print("✅ Commands: !ping, !createsetup, !mydata, !help")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need administrator permissions to use this command!")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore unknown commands
    else:
        await ctx.send(f"❌ Error: {str(error)[:100]}")

# --- RUN ---
if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ ERROR: No TOKEN environment variable")