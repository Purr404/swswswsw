import discord
from discord.ext import commands
import datetime

# --- ANNOUNCEMENT SYSTEM ---
class AnnouncementSystem:
    def __init__(self, bot):
        self.bot = bot
        self.announcement_channels = {}  # {server_id: channel_id}
        self.announcement_images = {}    # {server_id: image_url}
    
    def create_announcement_embed(self, message, author, title="ANNOUNCEMENT", color=0xFF5500, image_url=None):
        """Create a beautiful announcement embed"""
        embed = discord.Embed(
            title=f"📢 **{title}**",
            description=message,
            color=color,
            timestamp=datetime.datetime.utcnow()
        )
        
        # Add author info
        embed.set_author(
            name=f"Posted by {author.display_name}",
            icon_url=author.display_avatar.url
        )
        
        # Add server icon as thumbnail
        if author.guild.icon:
            embed.set_thumbnail(url=author.guild.icon.url)
        
        # Add image if provided
        if image_url:
            embed.set_image(url=image_url)
        
        # Custom footer with copyright (this is what you wanted!)
        embed.set_footer(
            text="TH 558 Discord Server • Official Announcement",
            icon_url="https://cdn.discordapp.com/emojis/1065149931136663624.png"  # Copyright emoji
        )
        
        return embed
    
    async def get_announcement_channel(self, guild):
        """Get or find announcement channel"""
        server_id = str(guild.id)
        
        # Check if channel is set
        if server_id in self.announcement_channels:
            channel = guild.get_channel(self.announcement_channels[server_id])
            if channel:
                return channel
        
        # Try to find announcement channel
        for channel in guild.text_channels:
            if any(keyword in channel.name.lower() for keyword in ["announce", "📢", "news", "bulletin"]):
                self.announcement_channels[server_id] = channel.id
                return channel
        
        # Return first text channel as fallback
        for channel in guild.text_channels:
            if isinstance(channel, discord.TextChannel):
                return channel
        
        return None

# Add to your bot setup
bot.announcements = AnnouncementSystem(bot)

# --- ANNOUNCEMENT COMMANDS GROUP ---
@bot.group(name="announce", invoke_without_command=True)
@commands.has_permissions(manage_messages=True)
async def announce_group(ctx):
    """Announcement management system"""
    embed = discord.Embed(
        title="📢 **Announcement System**",
        description=(
            "**Commands:**\n"
            "▸ `!announce send <message>` - Send announcement\n"
            "▸ `!announce channel #channel` - Set announcement channel\n"
            "▸ `!announce preview <message>` - Preview before sending\n"
            "▸ `!announce image <url>` - Add image to next announcement\n"
            "▸ `!announce urgent <message>` - Red urgent announcement\n"
            "▸ `!announce update <message>` - Blue update announcement\n"
            "▸ `!announce event <message>` - Green event announcement\n"
        ),
        color=0x5865F2
    )
    embed.set_footer(text="TH 558 Moderator Tools")
    await ctx.send(embed=embed)

# --- SEND ANNOUNCEMENT ---
@announce_group.command(name="send")
@commands.has_permissions(manage_messages=True)
async def announce_send(ctx, *, message: str):
    """Send an announcement to the announcement channel"""
    
    # Get announcement channel
    channel = await bot.announcements.get_announcement_channel(ctx.guild)
    if not channel:
        await ctx.send("❌ No announcement channel found! Set one with `!announce channel #channel`")
        return
    
    # Check for image
    server_id = str(ctx.guild.id)
    image_url = bot.announcements.announcement_images.get(server_id)
    
    # Create embed
    embed = bot.announcements.create_announcement_embed(
        message=message,
        author=ctx.author,
        title="ANNOUNCEMENT",
        color=0xFF5500,  # Orange
        image_url=image_url
    )
    
    # Send announcement
    try:
        sent_message = await channel.send("@here" if channel != ctx.channel else "", embed=embed)
        
        # Add engagement reactions
        await sent_message.add_reaction("📢")  # Announcement
        await sent_message.add_reaction("✅")  # Confirm
        await sent_message.add_reaction("💬")  # Discuss
        await sent_message.add_reaction("📌")  # Pin
        
        # Clear stored image
        if server_id in bot.announcements.announcement_images:
            del bot.announcements.announcement_images[server_id]
        
        # Send confirmation to moderator
        confirm_embed = discord.Embed(
            description=(
                f"✅ **Announcement Sent!**\n"
                f"**Channel:** {channel.mention}\n"
                f"**Link:** [Jump to Message]({sent_message.jump_url})"
            ),
            color=discord.Color.green()
        )
        confirm_embed.set_footer(text="Announcement delivered successfully")
        
        await ctx.send(embed=confirm_embed, delete_after=10)
        
        # Delete command message
        await ctx.message.delete(delay=5)
        
    except Exception as e:
        await ctx.send(f"❌ Failed to send announcement: {str(e)[:100]}")

# --- SET ANNOUNCEMENT CHANNEL ---
@announce_group.command(name="channel")
@commands.has_permissions(administrator=True)
async def announce_channel(ctx, channel: discord.TextChannel):
    """Set the announcement channel"""
    server_id = str(ctx.guild.id)
    bot.announcements.announcement_channels[server_id] = channel.id
    
    embed = discord.Embed(
        description=f"✅ **Announcement channel set to {channel.mention}**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

# --- PREVIEW ANNOUNCEMENT ---
@announce_group.command(name="preview")
@commands.has_permissions(manage_messages=True)
async def announce_preview(ctx, *, message: str):
    """Preview how the announcement will look"""
    server_id = str(ctx.guild.id)
    image_url = bot.announcements.announcement_images.get(server_id)
    
    embed = bot.announcements.create_announcement_embed(
        message=message,
        author=ctx.author,
        title="ANNOUNCEMENT PREVIEW",
        color=0x5865F2,  # Preview color
        image_url=image_url
    )
    
    await ctx.send("**📝 Preview:**", embed=embed)
    
    # Show which image will be included
    if image_url:
        await ctx.send(f"*Includes image: {image_url[:50]}...*")
    
    await ctx.send("*Use `!announce send` to post this announcement.*")

# --- SET IMAGE FOR NEXT ANNOUNCEMENT ---
@announce_group.command(name="image")
@commands.has_permissions(manage_messages=True)
async def announce_image(ctx, image_url: str):
    """Set an image to include in the next announcement"""
    # Validate URL
    if not (image_url.startswith("http://") or image_url.startswith("https://")):
        await ctx.send("❌ Please provide a valid image URL (http:// or https://)")
        return
    
    server_id = str(ctx.guild.id)
    bot.announcements.announcement_images[server_id] = image_url
    
    # Show preview
    embed = discord.Embed(
        title="✅ Image Set for Next Announcement",
        description=f"URL: {image_url[:100]}...",
        color=discord.Color.green()
    )
    embed.set_image(url=image_url)
    embed.set_footer(text="This image will be included in your next !announce send command")
    
    await ctx.send(embed=embed)

# --- URGENT ANNOUNCEMENT (Red) ---
@announce_group.command(name="urgent")
@commands.has_permissions(manage_messages=True)
async def announce_urgent(ctx, *, message: str):
    """Send an urgent announcement (red color)"""
    channel = await bot.announcements.get_announcement_channel(ctx.guild)
    if not channel:
        await ctx.send("❌ No announcement channel set!")
        return
    
    embed = bot.announcements.create_announcement_embed(
        message=message,
        author=ctx.author,
        title="🚨 URGENT ANNOUNCEMENT",
        color=0xFF0000,  # Red
        image_url=bot.announcements.announcement_images.get(str(ctx.guild.id))
    )
    
    sent_message = await channel.send("@everyone", embed=embed)
    
    # Add urgent reactions
    await sent_message.add_reaction("🚨")
    await sent_message.add_reaction("⚠️")
    
    await ctx.send(f"✅ Urgent announcement sent to {channel.mention}", delete_after=5)
    await ctx.message.delete(delay=3)

# --- UPDATE ANNOUNCEMENT (Blue) ---
@announce_group.command(name="update")
@commands.has_permissions(manage_messages=True)
async def announce_update(ctx, *, message: str):
    """Send an update announcement (blue color)"""
    channel = await bot.announcements.get_announcement_channel(ctx.guild)
    if not channel:
        await ctx.send("❌ No announcement channel set!")
        return
    
    embed = bot.announcements.create_announcement_embed(
        message=message,
        author=ctx.author,
        title="🔄 SERVER UPDATE",
        color=0x0080FF,  # Blue
        image_url=bot.announcements.announcement_images.get(str(ctx.guild.id))
    )
    
    sent_message = await channel.send("@here", embed=embed)
    await sent_message.add_reaction("🔄")
    await sent_message.add_reaction("📝")
    
    await ctx.send(f"✅ Update announcement sent to {channel.mention}", delete_after=5)
    await ctx.message.delete(delay=3)

# --- EVENT ANNOUNCEMENT (Green) ---
@announce_group.command(name="event")
@commands.has_permissions(manage_messages=True)
async def announce_event(ctx, *, message: str):
    """Send an event announcement (green color)"""
    channel = await bot.announcements.get_announcement_channel(ctx.guild)
    if not channel:
        await ctx.send("❌ No announcement channel set!")
        return
    
    embed = bot.announcements.create_announcement_embed(
        message=message,
        author=ctx.author,
        title="🎉 UPCOMING EVENT",
        color=0x00FF00,  # Green
        image_url=bot.announcements.announcement_images.get(str(ctx.guild.id))
    )
    
    sent_message = await channel.send("@here", embed=embed)
    await sent_message.add_reaction("🎉")
    await sent_message.add_reaction("📅")
    
    await ctx.send(f"✅ Event announcement sent to {channel.mention}", delete_after=5)
    await ctx.message.delete(delay=3)

# --- QUICK ANNOUNCE ALIAS ---
@bot.command(name="a")
@commands.has_permissions(manage_messages=True)
async def quick_announce(ctx, *, message: str):
    """Quick announcement alias"""
    # This calls the send command
    await announce_send.invoke(ctx, message=message)