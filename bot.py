import discord
from discord.ext import commands
from discord.ui import View, Button
import os
import datetime

TOKEN = os.getenv('TOKEN')

# --- 1. FIRST: Create the bot instance ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!!', intents=intents, help_command=None)

# --- 2. Store user selections ---
user_selections = {}

# --- 3. ANNOUNCEMENT SYSTEM CLASS ---
class AnnouncementSystem:
    def __init__(self):
        self.announcement_channels = {}
        self.announcement_images = {}
    
    def create_announcement_embed(self, message, author, title="ANNOUNCEMENT", color=0xFF5500, image_url=None):
        """Create a beautiful announcement embed"""
        embed = discord.Embed(
            title=f"📢 **{title}**",
            description=message,
            color=color,
            timestamp=datetime.datetime.utcnow()
        )
        
        embed.set_author(
            name=f"Posted by {author.display_name}",
            icon_url=author.display_avatar.url
        )
        
        if author.guild.icon:
            embed.set_thumbnail(url=author.guild.icon.url)
        
        if image_url:
            embed.set_image(url=image_url)
        
        # YOUR CUSTOM FOOTER
        embed.set_footer(
            text="©️ 558 Discord Server • Official Announcement",
            icon_url="https://cdn.discordapp.com/emojis/1065149931136663624.png"
        )
        
        return embed
    
    async def get_announcement_channel(self, guild):
        """Get or find announcement channel"""
        server_id = str(guild.id)
        
        if server_id in self.announcement_channels:
            channel = guild.get_channel(self.announcement_channels[server_id])
            if channel:
                return channel
        
        for channel in guild.text_channels:
            if any(keyword in channel.name.lower() for keyword in ["announce", "📢", "news"]):
                self.announcement_channels[server_id] = channel.id
                return channel
        
        for channel in guild.text_channels:
            if isinstance(channel, discord.TextChannel):
                return channel
        
        return None

# --- 4. Create announcement system AFTER bot is defined ---
announcements = AnnouncementSystem()

# --- 5. ANNOUNCEMENT COMMANDS ---
@bot.group(name="announce", invoke_without_command=True)
@commands.has_permissions(manage_messages=True)
async def announce_group(ctx):
    """Announcement management system"""
    embed = discord.Embed(
        title="📢 **Announcement System**",
        description=(
            "**Commands:**\n"
            "• `!!announce send <message>` - Send announcement\n"
            "• `!!announce channel #channel` - Set announcement channel\n"
            "• `!!announce preview <message>` - Preview announcement\n"
            "• `!!announce image <url>` - Add image to announcement\n"
            "• `!!announce urgent <message>` - Red urgent announcement\n"
        ),
        color=0x5865F2
    )
    await ctx.send(embed=embed)

@announce_group.command(name="send")
@commands.has_permissions(manage_messages=True)
async def announce_send(ctx, *, message: str):
    """Send an announcement"""
    channel = await announcements.get_announcement_channel(ctx.guild)
    if not channel:
        await ctx.send("❌ No announcement channel found! Use `!!announce channel #channel`")
        return
    
    server_id = str(ctx.guild.id)
    image_url = announcements.announcement_images.get(server_id)
    
    embed = announcements.create_announcement_embed(
        message=message,
        author=ctx.author,
        image_url=image_url
    )
    
    try:
        sent_message = await channel.send("@here", embed=embed)
        
        await sent_message.add_reaction("📢")
        await sent_message.add_reaction("✅")
        
        if server_id in announcements.announcement_images:
            del announcements.announcement_images[server_id]
        
        confirm_embed = discord.Embed(
            description=f"✅ **Announcement Sent!**\n**Channel:** {channel.mention}\n**Link:** [Jump to Message]({sent_message.jump_url})",
            color=discord.Color.green()
        )
        await ctx.send(embed=confirm_embed, delete_after=10)
        await ctx.message.delete(delay=5)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)[:100]}")

@announce_group.command(name="channel")
@commands.has_permissions(administrator=True)
async def announce_channel(ctx, channel: discord.TextChannel):
    """Set the announcement channel"""
    server_id = str(ctx.guild.id)
    announcements.announcement_channels[server_id] = channel.id
    
    embed = discord.Embed(
        description=f"✅ **Announcement channel set to {channel.mention}**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@announce_group.command(name="preview")
@commands.has_permissions(manage_messages=True)
async def announce_preview(ctx, *, message: str):
    """Preview announcement"""
    server_id = str(ctx.guild.id)
    image_url = announcements.announcement_images.get(server_id)
    
    embed = announcements.create_announcement_embed(
        message=message,
        author=ctx.author,
        title="ANNOUNCEMENT PREVIEW",
        color=0x5865F2,
        image_url=image_url
    )
    
    await ctx.send("**📝 Preview:**", embed=embed)
    await ctx.send("*Use `!!announce send` to post.*")

@announce_group.command(name="image")
@commands.has_permissions(manage_messages=True)
async def announce_image(ctx, image_url: str):
    """Set image for next announcement"""
    if not (image_url.startswith("http://") or image_url.startswith("https://")):
        await ctx.send("❌ Please provide a valid image URL")
        return
    
    server_id = str(ctx.guild.id)
    announcements.announcement_images[server_id] = image_url
    
    embed = discord.Embed(
        title="✅ Image Set for Next Announcement",
        color=discord.Color.green()
    )
    embed.set_image(url=image_url)
    await ctx.send(embed=embed)

@announce_group.command(name="urgent")
@commands.has_permissions(manage_messages=True)
async def announce_urgent(ctx, *, message: str):
    """Send urgent announcement (red)"""
    channel = await announcements.get_announcement_channel(ctx.guild)
    if not channel:
        await ctx.send("❌ No announcement channel set!")
        return
    
    embed = announcements.create_announcement_embed(
        message=message,
        author=ctx.author,
        title="🚨 URGENT ANNOUNCEMENT",
        color=0xFF0000,
        image_url=announcements.announcement_images.get(str(ctx.guild.id))
    )
    
    sent_message = await channel.send("@everyone", embed=embed)
    await sent_message.add_reaction("🚨")
    await sent_message.add_reaction("⚠️")
    
    await ctx.send(f"✅ Urgent announcement sent!", delete_after=5)
    await ctx.message.delete(delay=3)

# Quick alias
@bot.command(name="a")
@commands.has_permissions(manage_messages=True)
async def quick_announce(ctx, *, message: str):
    """Quick announcement"""
    await announce_send.invoke(ctx, message=message)


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("🏓 Pong!")

# --- MESSAGE SENDING SYSTEM ---
@bot.group(name="say", invoke_without_command=True)
@commands.has_permissions(manage_messages=True)
async def say_group(ctx):
    """Send messages through the bot"""
    embed = discord.Embed(
        title="💬 Message Sending System",
        description=(
            "**Commands:**\n"
            "• `!!say <message>` - Send message in current channel\n"
            "• `!!say #channel <message>` - Send to specific channel\n"
            "• `!!say embed #channel <title> | <description>` - Send embed\n"
            "• `!!say reply <message_id> <message>` - Reply to a message\n"
            "• `!!say dm @user <message>` - Send DM to user\n"
        ),
        color=0x5865F2
    )
    await ctx.send(embed=embed)

# --- FIXED: Use converter for optional channel ---
@say_group.command(name="send")
@commands.has_permissions(manage_messages=True)
async def say_send(ctx, target: str = None, *, message: str = None):
    """
    Send a message to any channel
    Usage: !!say #channel Hello everyone!
           !!say Hello (sends in current channel)
    """
    # Handle the case where no target is provided
    if message is None:
        # If no target, the entire content is the message
        message = target
        target_channel = ctx.channel
        target = None
    else:
        # Try to parse target as a channel
        try:
            # Try to convert target to a channel
            converter = commands.TextChannelConverter()
            target_channel = await converter.convert(ctx, target)
        except:
            # If conversion fails, treat target as part of message
            message = f"{target} {message}"
            target_channel = ctx.channel
    
    try:
        # Send the message
        sent_message = await target_channel.send(message)
        
        # Send confirmation
        if target_channel != ctx.channel:
            confirm_embed = discord.Embed(
                description=f"✅ **Message sent to {target_channel.mention}**\n[Jump to message]({sent_message.jump_url})",
                color=discord.Color.green()
            )
            await ctx.send(embed=confirm_embed, delete_after=10)
        else:
            # If sending in same channel, just delete command
            await ctx.message.delete(delay=2)
        
        # Log
        print(f"[SAY] {ctx.author} sent message to #{target_channel.name}: {message[:50]}...")
        
    except Exception as e:
        await ctx.send(f"❌ Failed to send message: {str(e)[:100]}")

# Alternative simpler version:
@bot.command(name="sendto")
@commands.has_permissions(manage_messages=True)
async def send_to(ctx, channel: discord.TextChannel, *, message: str):
    """
    Send message to specific channel
    Usage: !!sendto #channel Your message here
    """
    try:
        sent_message = await channel.send(message)
        
        confirm_embed = discord.Embed(
            description=f"✅ **Message sent to {channel.mention}**\n[Jump to message]({sent_message.jump_url})",
            color=discord.Color.green()
        )
        await ctx.send(embed=confirm_embed, delete_after=10)
        await ctx.message.delete(delay=2)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)[:100]}")

@bot.command(name="sendhere")
@commands.has_permissions(manage_messages=True)
async def send_here(ctx, *, message: str):
    """
    Send message in current channel
    Usage: !!sendhere Your message here
    """
    try:
        await ctx.send(message)
        await ctx.message.delete(delay=2)
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)[:100]}")

# --- SIMPLER EMBED COMMAND ---
@bot.command(name="embed")
@commands.has_permissions(manage_messages=True)
async def send_embed(ctx, channel: discord.TextChannel = None, *, content: str):
    """
    Send embed message
    Usage: !!embed #channel Title | Description
           !!embed Title | Description (sends in current channel)
    """
    target_channel = channel or ctx.channel
    
    # Parse title and description
    if "|" in content:
        title, description = content.split("|", 1)
        title = title.strip()
        description = description.strip()
    else:
        title = "Announcement"
        description = content
    
    try:
        embed = discord.Embed(
            title=title,
            description=description,
            color=0x5865F2,
            timestamp=datetime.datetime.utcnow()
        )
        
        embed.set_author(
            name=f"From {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        embed.set_footer(text="©️ 558 Discord Server")
        
        sent_message = await target_channel.send(embed=embed)
        
        if target_channel != ctx.channel:
            await ctx.send(f"✅ Embed sent to {target_channel.mention}", delete_after=5)
        
        await ctx.message.delete(delay=2)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)[:100]}")

# --- DM COMMAND ---
@bot.command(name="dm")
@commands.has_permissions(manage_messages=True)
async def send_dm(ctx, user: discord.Member, *, message: str):
    """
    Send DM to a user
    Usage: !!dm @user Your message here
    """
    try:
        embed = discord.Embed(
            title=f"Message from {ctx.guild.name} Staff",
            description=message,
            color=0x5865F2,
            timestamp=datetime.datetime.utcnow()
        )
        
        embed.set_author(
            name=f"From {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        embed.set_footer(text="©️ 558 Discord Server")
        
        await user.send(embed=embed)
        
        await ctx.send(f"✅ DM sent to {user.mention}", delete_after=5)
        await ctx.message.delete(delay=2)
        
    except discord.Forbidden:
        await ctx.send(f"❌ Cannot DM {user.mention} (DMs disabled)", delete_after=5)
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)[:100]}")

# --- REPLY COMMAND ---
@bot.command(name="smartreply")
@commands.has_permissions(manage_messages=True)
async def smart_reply(ctx, message_id: int, *, reply_message: str):
    """
    Try to find and reply to message in any channel
    Usage: !!smartreply 123456789012345678 Your reply
    """
    message_found = False
    
    # Search through all text channels
    for channel in ctx.guild.text_channels:
        try:
            # Check if bot has permission to read this channel
            if channel.permissions_for(ctx.guild.me).read_messages:
                try:
                    # Try to fetch the message
                    message_to_reply = await channel.fetch_message(message_id)
                    
                    # Found it! Reply and stop searching
                    await message_to_reply.reply(reply_message)
                    await ctx.send(f"✅ Replied in {channel.mention}", delete_after=5)
                    await ctx.message.delete()
                    message_found = True
                    break
                    
                except discord.NotFound:
                    continue  # Message not in this channel, try next
        except:
            continue
    
    if not message_found:
        await ctx.send(
            "❌ **Could not find message!**\n"
            "The message might be:\n"
            "• In a channel I can't access\n"
            "• Deleted\n"
            "• Wrong ID\n\n"
            "Try: `!!replyto #channel message_id your_message`",
            delete_after=10
        )

# --- 8. EVENTS ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    
    # Make your view persistent
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="for!!help"
        )
    )
    print("✅ Bot ready with announcements!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission!")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"❌ Error: {str(error)[:100]}")

# --- 9. RUN BOT ---
if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ ERROR: No TOKEN")