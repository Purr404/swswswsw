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



import discord
from discord.ext import commands, tasks
import asyncio
import json
import random
from datetime import datetime, timedelta
import os

# --- QUIZ SYSTEM CLASS (Complete) ---
class QuizSystem:
    def __init__(self, bot):
        self.bot = bot
        self.quiz_questions = []
        self.current_question = 0
        self.participants = {}
        self.question_timer = None
        self.quiz_channel = None
        self.quiz_logs_channel = None
        self.quiz_running = False
        self.question_start_time = None
        
        # Load 20 questions
        self.load_questions()
    
    def load_questions(self):
        """Load 20 quiz questions with open-ended answers"""
        self.quiz_questions = [
            {
                "question": "What is the capital city of France?",
                "correct_answers": ["paris"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "Which planet is known as the Red Planet?",
                "correct_answers": ["mars", "planet mars"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "What is the chemical symbol for gold?",
                "correct_answers": ["au"],
                "points": 200,
                "time_limit": 45
            },
            {
                "question": "Who painted the Mona Lisa?",
                "correct_answers": ["leonardo da vinci", "da vinci", "leonardo"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "What is the largest mammal in the world?",
                "correct_answers": ["blue whale", "whale"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "How many continents are there on Earth?",
                "correct_answers": ["7", "seven"],
                "points": 200,
                "time_limit": 45
            },
            {
                "question": "What is H2O commonly known as?",
                "correct_answers": ["water", "h2o"],
                "points": 200,
                "time_limit": 45
            },
            {
                "question": "Who wrote the play 'Romeo and Juliet'?",
                "correct_answers": ["william shakespeare", "shakespeare"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "What is the fastest land animal?",
                "correct_answers": ["cheetah"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "Which country gifted the Statue of Liberty to the USA?",
                "correct_answers": ["france"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "How many sides does a hexagon have?",
                "correct_answers": ["6", "six"],
                "points": 200,
                "time_limit": 45
            },
            {
                "question": "What is the hardest natural substance on Earth?",
                "correct_answers": ["diamond"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "Which gas do plants absorb from the atmosphere?",
                "correct_answers": ["carbon dioxide", "co2"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "What is the smallest country in the world?",
                "correct_answers": ["vatican city", "vatican"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "Which planet has the most moons?",
                "correct_answers": ["saturn"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "What is the capital of Japan?",
                "correct_answers": ["tokyo"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "How many players are on a basketball team?",
                "correct_answers": ["5", "five"],
                "points": 200,
                "time_limit": 45
            },
            {
                "question": "What is the main ingredient in guacamole?",
                "correct_answers": ["avocado"],
                "points": 200,
                "time_limit": 45
            },
            {
                "question": "Which year did World War II end?",
                "correct_answers": ["1945"],
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "What is the currency of Japan?",
                "correct_answers": ["yen"],
                "points": 300,
                "time_limit": 60
            }
        ]
    
    def calculate_points(self, answer_time, total_time, max_points):
        """Calculate points based on answer speed"""
        time_left = total_time - answer_time
        if time_left <= 0:
            return 0
        percentage = time_left / total_time
        return int(max_points * percentage)
    
    async def start_quiz(self, channel, logs_channel):
        """Start a new quiz in specified channel"""
        self.quiz_channel = channel
        self.quiz_logs_channel = logs_channel
        self.quiz_running = True
        self.current_question = 0
        self.participants = {}
        
        # Shuffle questions
        random.shuffle(self.quiz_questions)
        
        # Send quiz start message
        embed = discord.Embed(
            title="🎯 **QUIZ STARTING!**",
            description=(
                "**Open-Ended Quiz**\n"
                "Think carefully and type your answers!\n\n"
                "**Rules:**\n"
                "• Type your answer exactly\n"
                "• Spelling matters!\n"
                "• Faster answers = more points!\n"
                "• Max points: 300 per question\n\n"
                f"First question starts in **5 seconds**!"
            ),
            color=discord.Color.gold()
        )
        start_msg = await channel.send(embed=embed)
        
        # Start countdown
        for i in range(5, 0, -1):
            await start_msg.edit(content=f"⏰ **{i}...**")
            await asyncio.sleep(1)
        
        await start_msg.delete()
        
        # Start first question
        await self.send_question()
    
    async def send_question(self):
        """Send current question with countdown bar"""
        if self.current_question >= len(self.quiz_questions):
            await self.end_quiz()
            return
        
        question = self.quiz_questions[self.current_question]
        self.question_start_time = datetime.utcnow()
        
        # Initial progress bar (full)
        progress_bar = "🟩" * 20
        
        # Create question embed
        embed = discord.Embed(
            title=f"❓ **Question {self.current_question + 1}/{len(self.quiz_questions)}**",
            description=question["question"],
            color=discord.Color.blue()
        )
        
        # Add countdown bar field
        embed.add_field(
            name=f"⏰ **{question['time_limit']:02d} SECONDS LEFT**",
            value=f"```\n{progress_bar}\n{question['time_limit']:02d} seconds\n```\n"
                  f"**Max Points:** {question['points']} ⭐",
            inline=False
        )
        
        embed.set_footer(text="Type your answer in the chat")
        
        # Send question
        self.question_message = await self.quiz_channel.send(embed=embed)
        
        # Start the live countdown
        self.countdown_task.start(question["time_limit"])
        
        # Start question timer (for auto-ending)
        self.start_question_timer(question["time_limit"])
    
    @tasks.loop(seconds=1)
    async def countdown_task(self, total_time):
        """Update live countdown bar every second"""
        if not self.quiz_running:
            self.countdown_task.stop()
            return
        
        try:
            elapsed = (datetime.utcnow() - self.question_start_time).seconds
            time_left = total_time - elapsed
            
            if time_left <= 0:
                self.countdown_task.stop()
                return
            
            # Create progress bar
            progress = int((time_left / total_time) * 20)
            progress_bar = "🟩" * progress + "⬜" * (20 - progress)
            
            # Update embed
            embed = self.question_message.embeds[0]
            
            # Find and update the time field
            for i, field in enumerate(embed.fields):
                if "⏰" in field.name:
                    embed.set_field_at(
                        i,
                        name=f"⏰ **{time_left:02d} SECONDS LEFT**",
                        value=f"```\n{progress_bar}\n{time_left:02d} seconds\n```\n"
                              f"**Max Points:** {self.quiz_questions[self.current_question]['points']} ⭐",
                        inline=False
                    )
                    break
            
            # Change embed color based on time
            if time_left <= 10:
                embed.color = discord.Color.red()
            elif time_left <= 30:
                embed.color = discord.Color.orange()
            else:
                embed.color = discord.Color.blue()
            
            await self.question_message.edit(embed=embed)
            
        except Exception as e:
            print(f"Countdown error: {e}")
            self.countdown_task.stop()
    
    def start_question_timer(self, time_limit):
        """Start timer for current question"""
        async def timer():
            await asyncio.sleep(time_limit)
            await self.end_question()
        
        if self.question_timer:
            self.question_timer.cancel()
        
        self.question_timer = asyncio.create_task(timer())
    
    async def process_answer(self, user, answer_text):
        """Process user's answer silently (no reactions)"""
        if not self.quiz_running:
            return False
        
        question = self.quiz_questions[self.current_question]
        answer_time = (datetime.utcnow() - self.question_start_time).seconds
        
        # Check if time's up
        if answer_time > question["time_limit"]:
            return False
        
        # Initialize user in participants
        user_id = str(user.id)
        if user_id not in self.participants:
            self.participants[user_id] = {
                "name": user.display_name,
                "score": 0,
                "answers": [],
                "total_time": 0
            }
        
        # Check if already answered this question
        for a in self.participants[user_id]["answers"]:
            if a["question"] == self.current_question:
                return False  # Already answered
        
        # Check if answer is correct (case-insensitive, trim spaces)
        user_answer = answer_text.lower().strip()
        is_correct = any(correct_answer == user_answer 
                        for correct_answer in question["correct_answers"])
        
        # Calculate points
        points = 0
        if is_correct:
            points = self.calculate_points(
                answer_time,
                question["time_limit"],
                question["points"]
            )
            self.participants[user_id]["score"] += points
        
        # Record answer
        self.participants[user_id]["answers"].append({
            "question": self.current_question,
            "answer": answer_text,
            "correct": is_correct,
            "points": points,
            "time": answer_time
        })
        
        # Log to quiz logs (silently)
        await self.log_answer(user, question["question"], answer_text, 
                             is_correct, points, answer_time)
        
        return True
    
    async def log_answer(self, user, question, answer, correct, points, time):
        """Log answer to quiz logs channel"""
        if not self.quiz_logs_channel:
            return
        
        embed = discord.Embed(
            title="📝 **Quiz Answer Log**",
            color=discord.Color.green() if correct else discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="👤 User", value=user.mention, inline=True)
        embed.add_field(name="📋 Question", value=question[:100] + "...", inline=True)
        embed.add_field(name="✏️ Answer", value=answer[:50], inline=True)
        embed.add_field(name="✅ Correct", value="Yes" if correct else "No", inline=True)
        embed.add_field(name="⭐ Points", value=str(points), inline=True)
        embed.add_field(name="⏱️ Time", value=f"{time}s", inline=True)
        
        await self.quiz_logs_channel.send(embed=embed)
    
    async def end_question(self):
        """End current question and show live leaderboard"""
        self.countdown_task.stop()
        
        question = self.quiz_questions[self.current_question]
        
        # Show correct answer(s)
        correct_answers = ", ".join([a.capitalize() for a in question["correct_answers"]])
        
        embed = discord.Embed(
            title=f"✅ **Question {self.current_question + 1} Complete**",
            description=f"**Correct answer(s):** {correct_answers}",
            color=discord.Color.green()
        )
        
        # Show top 3 fastest for THIS question
        question_answers = []
        for user_id, data in self.participants.items():
            for answer in data["answers"]:
                if answer["question"] == self.current_question and answer["correct"]:
                    question_answers.append({
                        "user": data["name"],
                        "time": answer["time"],
                        "points": answer["points"]
                    })
        
        question_answers.sort(key=lambda x: x["time"])
        
        if question_answers:
            embed.add_field(
                name="🏆 **Fastest This Question**",
                value="\n".join([
                    f"**{i+1}. {ans['user']}** - {ans['time']}s ({ans['points']} pts)"
                    for i, ans in enumerate(question_answers[:3])
                ]),
                inline=False
            )
        
        await self.quiz_channel.send(embed=embed)
        
        # Wait 2 seconds
        await asyncio.sleep(2)
        
        # SHOW LIVE LEADERBOARD WITH ALL USERS
        leaderboard_embed = await self.create_live_leaderboard()
        leaderboard_message = await self.quiz_channel.send(embed=leaderboard_embed)
        
        # Countdown to next question with leaderboard showing
        countdown_seconds = 5
        for i in range(countdown_seconds, 0, -1):
            # Update leaderboard countdown
            updated_embed = await self.create_live_leaderboard(countdown=i)
            await leaderboard_message.edit(embed=updated_embed)
            await asyncio.sleep(1)
        
        await leaderboard_message.delete()
        
        # Move to next question
        self.current_question += 1
        await self.send_question()
    
    async def create_live_leaderboard(self, countdown=None):
        """Create a live leaderboard embed showing all participants"""
        if not self.participants:
            embed = discord.Embed(
                title="📊 **Current Leaderboard**",
                description="No participants yet!",
                color=discord.Color.blue()
            )
            return embed
        
        # Sort by score (highest first)
        sorted_participants = sorted(
            self.participants.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        # Calculate statistics
        total_questions = self.current_question + 1
        max_possible = total_questions * 300
        
        embed = discord.Embed(
            title="📊 **LIVE LEADERBOARD**",
            color=discord.Color.gold()
        )
        
        # Add countdown if provided
        if countdown:
            embed.description = f"**Next question in:** {countdown} seconds\n"
        
        # Show question progress
        embed.add_field(
            name="📈 **Progress**",
            value=f"**Question:** {self.current_question + 1}/{len(self.quiz_questions)}\n"
                  f"**Max Possible:** {max_possible} points",
            inline=False
        )
        
        # Create leaderboard entries
        leaderboard_lines = []
        for i, (user_id, data) in enumerate(sorted_participants):
            # Get user's performance on current question
            current_q_answer = None
            for answer in data["answers"]:
                if answer["question"] == self.current_question:
                    current_q_answer = answer
                    break
            
            # Format line with emoji based on rank
            rank_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            emoji = rank_emoji[i] if i < len(rank_emoji) else f"{i+1}."
            
            # Format current question performance
            if current_q_answer:
                if current_q_answer["correct"]:
                    q_perf = f"✅ +{current_q_answer['points']}"
                else:
                    q_perf = "❌ +0"
            else:
                q_perf = "⏳ No answer"
            
            leaderboard_lines.append(
                f"{emoji} **{data['name']}**\n"
                f"   Total: **{data['score']}** pts | This Q: {q_perf}"
            )
        
        # Split leaderboard into chunks (10 per field)
        for i in range(0, len(leaderboard_lines), 10):
            chunk = leaderboard_lines[i:i + 10]
            embed.add_field(
                name=f"**Rank {i+1}-{i+len(chunk)}**" if i > 0 else "**🏆 TOP 10**",
                value="\n".join(chunk),
                inline=False
            )
        
        # Add statistics
        total_participants = len(self.participants)
        answered_this_q = len([a for data in self.participants.values() 
                              for a in data["answers"] if a["question"] == self.current_question])
        
        embed.add_field(
            name="📊 **Statistics**",
            value=f"**Participants:** {total_participants}\n"
                  f"**Answered Q{self.current_question + 1}:** {answered_this_q}/{total_participants}",
            inline=True
        )
        
        embed.set_footer(text=f"Question {self.current_question + 1} of {len(self.quiz_questions)}")
        
        return embed
    
    async def end_quiz(self):
        """End the entire quiz"""
        self.quiz_running = False
        self.countdown_task.stop()
        
        if self.question_timer:
            self.question_timer.cancel()
        
        # Sort participants by score
        sorted_participants = sorted(
            self.participants.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        # Create final results embed
        embed = discord.Embed(
            title="🎉 **QUIZ FINISHED!**",
            description="**Final Results:**",
            color=discord.Color.gold()
        )
        
        # Top 10 leaderboard
        leaderboard = []
        for i, (user_id, data) in enumerate(sorted_participants[:10]):
            leaderboard.append(f"**{i+1}. {data['name']}** - {data['score']} points")
        
        if leaderboard:
            embed.add_field(
                name="🏆 **FINAL TOP 10**",
                value="\n".join(leaderboard),
                inline=False
            )
        
        # Participant stats
        total_questions = len(self.quiz_questions)
        embed.add_field(
            name="📊 **Statistics**",
            value=f"**Total Participants:** {len(self.participants)}\n"
                  f"**Total Questions:** {total_questions}\n"
                  f"**Max Possible Points:** {total_questions * 300}",
            inline=False
        )
        
        await self.quiz_channel.send(embed=embed)
        
        # Reset for next quiz
        self.quiz_channel = None
        self.quiz_logs_channel = None
        self.current_question = 0
        self.participants = {}

# Create quiz system instance
quiz_system = QuizSystem(bot)

# --- QUIZ COMMANDS ---
@bot.group(name="quiz", invoke_without_command=True)
@commands.has_permissions(manage_messages=True)
async def quiz_group(ctx):
    """Quiz system commands"""
    embed = discord.Embed(
        title="🎯 **Quiz System**",
        description="**Commands:**\n"
                   "• `!!quiz start` - Start quiz in THIS channel\n"
                   "• `!!quiz start #channel` - Start quiz in specific channel\n"
                   "• `!!quiz stop` - Stop current quiz\n"
                   "• `!!quiz leaderboard` - Show current scores\n"
                   "• `!!quiz addq` - Add a new question",
        color=0x5865F2
    )
    await ctx.send(embed=embed)

@quiz_group.command(name="start")
@commands.has_permissions(manage_messages=True)
async def quiz_start(ctx, channel: discord.TextChannel = None):
    """
    Start a quiz in specific channel
    Usage: !!quiz start #channel  (starts in mentioned channel)
           !!quiz start           (starts in current channel)
    """
    if quiz_system.quiz_running:
        await ctx.send("❌ Quiz is already running!", delete_after=5)
        return
    
    # Determine which channel to use
    quiz_channel = channel or ctx.channel
    
    # Check permissions
    if not quiz_channel.permissions_for(ctx.guild.me).send_messages:
        await ctx.send(f"❌ I don't have permission to send messages in {quiz_channel.mention}!")
        return
    
    # Find or create quiz-logs channel
    logs_channel = discord.utils.get(ctx.guild.channels, name="quiz-logs")
    if not logs_channel:
        try:
            logs_channel = await ctx.guild.create_text_channel(
                "quiz-logs",
                reason="Auto-created quiz logs channel"
            )
        except:
            logs_channel = ctx.channel
    
    # Confirm
    embed = discord.Embed(
        description=f"✅ **Quiz starting in {quiz_channel.mention}!**\n"
                   f"Logs will go to {logs_channel.mention}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, delete_after=10)
    
    # Start quiz
    await quiz_system.start_quiz(quiz_channel, logs_channel)

@quiz_group.command(name="stop")
@commands.has_permissions(manage_messages=True)
async def quiz_stop(ctx):
    """Stop current quiz"""
    if not quiz_system.quiz_running:
        await ctx.send("❌ No quiz is running!", delete_after=5)
        return
    
    quiz_system.quiz_running = False
    if quiz_system.question_timer:
        quiz_system.question_timer.cancel()
    
    await ctx.send("✅ Quiz stopped!")

@quiz_group.command(name="leaderboard")
async def quiz_leaderboard(ctx):
    """Show current quiz leaderboard"""
    if not quiz_system.participants:
        await ctx.send("❌ No quiz data available!", delete_after=5)
        return
    
    # Create leaderboard embed
    embed = await quiz_system.create_live_leaderboard()
    await ctx.send(embed=embed)

@quiz_group.command(name="addq")
@commands.has_permissions(administrator=True)
async def quiz_addq(ctx, points: int, time_limit: int, *, question_data: str):
    """
    Add a new quiz question
    Format: !!quiz addq 300 60 Question? | correct answer 1 | correct answer 2
    Example: !!quiz addq 300 60 Capital of France? | paris
    """
    try:
        parts = question_data.split(" | ")
        if len(parts) < 2:
            await ctx.send("❌ Format: `Question? | correct answer 1 | correct answer 2`")
            return
        
        new_question = {
            "question": parts[0],
            "correct_answers": [ans.lower().strip() for ans in parts[1:]],
            "points": points,
            "time_limit": time_limit
        }
        
        quiz_system.quiz_questions.append(new_question)
        
        embed = discord.Embed(
            title="✅ **Question Added!**",
            description=new_question["question"],
            color=discord.Color.green()
        )
        
        embed.add_field(name="✅ Correct Answers", 
                       value=", ".join(new_question["correct_answers"]))
        embed.add_field(name="⭐ Points", value=str(points))
        embed.add_field(name="⏱️ Time Limit", value=f"{time_limit}s")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)[:100]}")

# --- ANSWER DETECTION ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Check for quiz answers (any text answer)
    if (quiz_system.quiz_running and 
        message.channel == quiz_system.quiz_channel):
        
        # Process the answer silently (NO REACTIONS)
        await quiz_system.process_answer(message.author, message.content)
    
    await bot.process_commands(message)

# Add to your help command:
"""
**🎯 Quiz System (Mods)**
• `!!quiz` - Quiz commands
• `!!quiz start` - Start quiz in current channel
• `!!quiz start #channel` - Start in specific channel
• `!!quiz stop` - Stop quiz
• `!!quiz leaderboard` - Show scores
• `!!quiz addq` - Add question
"""



# --- 8. EVENTS ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    
    # Make your view persistent
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=""
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