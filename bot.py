import discord
import os
from discord.ui import Modal, Select, View, Button

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Bot(intents=intents)

class SetupModal(Modal, title="Role Setup"):
    def __init__(self):
        super().__init__()
        
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
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"✅ Setup complete!\nTroop: {self.troop.values[0]}\nLanguages: {', '.join(self.languages.values) or 'None'}",
            ephemeral=True
        )

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")

@bot.command(description="Send setup message")
async def setup(ctx):
    view = View()
    button = Button(label="Start Setup", style=discord.ButtonStyle.primary, emoji="⚙️")
    
    async def button_callback(interaction):
        await interaction.response.send_modal(SetupModal())
    
    button.callback = button_callback
    view.add_item(button)
    
    embed = discord.Embed(
        title="Channels & Roles",
        description="Click button to setup roles",
        color=discord.Color.blue()
    )
    
    await ctx.respond(embed=embed, view=view)

if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Error: Set DISCORD_BOT_TOKEN environment variable")