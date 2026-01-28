import discord
from discord.ui import Modal, Select, Button, View
import os

TOKEN = os.getenv('TOKEN')

print(f"Using Py-cord version: {discord.__version__}")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Bot(intents=intents)

class RoleSetupModal(Modal, title="Role Setup"):
    def __init__(self):
        super().__init__()
        
        self.troop = Select(
            placeholder="Select main troop type",
            options=[
                discord.SelectOption(label="Horde", emoji="👹"),
                discord.SelectOption(label="League", emoji="🛡️"),
                discord.SelectOption(label="Nature", emoji="🌿")
            ]
        )
        self.add_item(self.troop)
        
        self.languages = Select(
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
        self.add_item(self.languages)
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"✅ Setup Complete!\n"
            f"Troop: {self.troop.values[0]}\n"
            f"Languages: {', '.join(self.languages.values) if self.languages.values else 'None'}",
            ephemeral=True
        )

class SetupView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Start Setup", style=discord.ButtonStyle.primary, emoji="⚙️")
    async def button_callback(self, interaction, button):
        await interaction.response.send_modal(RoleSetupModal())

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    bot.add_view(SetupView())

@bot.slash_command(name="setup", description="Send role setup form")
async def setup(ctx):
    await ctx.respond("Click below to setup roles:", view=SetupView())

if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Error: No TOKEN")