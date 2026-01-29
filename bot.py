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

# --- QUIZ SYSTEM ---
class QuizSystem:
    def __init__(self):
        self.active_quiz = None
        self.quiz_questions = []
        self.current_question = 0
        self.participants = {}  # {user_id: {"score": 0, "answers": []}}
        self.question_timer = None
        self.quiz_channel = None
        self.quiz_logs_channel = None
        self.quiz_running = False
        self.question_start_time = None
        
        # Load questions (you can expand this)
        self.load_questions()
    
    def load_questions(self):
        """Load quiz questions"""
        self.quiz_questions = [
            {
                "question": "What is the capital of France?",
                "options": ["A) London", "B) Berlin", "C) Paris", "D) Madrid"],
                "correct": "C",
                "points": 300,
                "time_limit": 60  # seconds
            },
            {
                "question": "Which planet is known as the Red Planet?",
                "options": ["A) Venus", "B) Mars", "C) Jupiter", "D) Saturn"],
                "correct": "B",
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "What is 2 + 2?",
                "options": ["A) 3", "B) 4", "C) 5", "D) 6"],
                "correct": "B",
                "points": 100,
                "time_limit": 30
            },
            {
                "question": "Who painted the Mona Lisa?",
                "options": ["A) Van Gogh", "B) Picasso", "C) Da Vinci", "D) Rembrandt"],
                "correct": "C",
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "What is the largest ocean on Earth?",
                "options": ["A) Atlantic", "B) Indian", "C) Arctic", "D) Pacific"],
                "correct": "D",
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "How many continents are there?",
                "options": ["A) 5", "B) 6", "C) 7", "D) 8"],
                "correct": "C",
                "points": 200,
                "time_limit": 45
            },
            {
                "question": "What is H2O?",
                "options": ["A) Oxygen", "B) Hydrogen", "C) Water", "D) Carbon Dioxide"],
                "correct": "C",
                "points": 200,
                "time_limit": 45
            },
            {
                "question": "Who wrote 'Romeo and Juliet'?",
                "options": ["A) Shakespeare", "B) Dickens", "C) Twain", "D) Hemingway"],
                "correct": "A",
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "What is the fastest land animal?",
                "options": ["A) Lion", "B) Cheetah", "C) Horse", "D) Leopard"],
                "correct": "B",
                "points": 300,
                "time_limit": 60
            },
            {
                "question": "What is the chemical symbol for gold?",
                "options": ["A) Go", "B) Gd", "C) Au", "D) Ag"],
                "correct": "C",
                "points": 300,
                "time_limit": 60
            }
        ]
        # Add more questions to reach 20...
    
    def calculate_points(self, answer_time, total_time, max_points):
        """Calculate points based on answer speed"""
        time_left = total_time - answer_time
        percentage = time_left / total_time
        return int(max_points * percentage)
    
    async def start_quiz(self, channel, logs_channel):
        """Start a new quiz"""
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
            description="Get ready for 20 questions!\n\n"
                       "**How to play:**\n"
                       "• Answer with A, B, C, or D\n"
                       "• Faster answers = more points!\n"
                       "• Max points: 300 per question\n\n"
                       f"First question starts in **10 seconds**!",
            color=discord.Color.gold()
        )
        embed.set_footer(text="Type your answer in this channel!")
        await channel.send(embed=embed)
        
        # Start countdown
        for i in range(5, 0, -1):
            await channel.send(f"⏰ **{i}...**")
            await asyncio.sleep(1)
        
        # Start first question
        await self.send_question()
    
    async def send_question(self):
        """Send current question"""
        if self.current_question >= len(self.quiz_questions):
            await self.end_quiz()
            return
        
        question = self.quiz_questions[self.current_question]
        self.question_start_time = datetime.utcnow()
        
        # Create question embed
        embed = discord.Embed(
            title=f"❓ **Question {self.current_question + 1}/20**",
            description=question["question"],
            color=discord.Color.blue()
        )
        
        for option in question["options"]:
            embed.add_field(name="​", value=option, inline=False)
        
        embed.add_field(
            name="⏰ Time Limit",
            value=f"**{question['time_limit']} seconds**\nMax points: **{question['points']}**",
            inline=False
        )
        
        embed.set_footer(text="Answer with A, B, C, or D!")
        
        # Send question
        message = await self.quiz_channel.send(embed=embed)
        
        # Start timer
        self.start_question_timer(question["time_limit"], message)
        
        # Start countdown updates
        self.update_countdown.start(message, question["time_limit"])
    
    def start_question_timer(self, time_limit, message):
        """Start timer for current question"""
        async def timer():
            await asyncio.sleep(time_limit)
            await self.end_question(message)
        
        self.question_timer = asyncio.create_task(timer())
    
    @tasks.loop(seconds=5)
    async def update_countdown(self, message, total_time):
        """Update countdown in embed"""
        if not self.quiz_running:
            self.update_countdown.stop()
            return
        
        elapsed = (datetime.utcnow() - self.question_start_time).seconds
        time_left = total_time - elapsed
        
        if time_left <= 0:
            self.update_countdown.stop()
            return
        
        # Update embed with time left
        try:
            embed = message.embeds[0]
            
            # Find and update time field
            for i, field in enumerate(embed.fields):
                if field.name == "⏰ Time Limit":
                    embed.set_field_at(
                        i,
                        name="⏰ Time Remaining",
                        value=f"**{time_left} seconds**\nMax points: **{self.quiz_questions[self.current_question]['points']}**",
                        inline=False
                    )
                    break
            
            await message.edit(embed=embed)
            
        except:
            pass
    
    async def process_answer(self, user, answer):
        """Process user's answer"""
        if not self.quiz_running:
            return False
        
        question = self.quiz_questions[self.current_question]
        answer_time = (datetime.utcnow() - self.question_start_time).seconds
        
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
        
        # Check answer
        is_correct = (answer.upper() == question["correct"])
        
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
            "answer": answer.upper(),
            "correct": is_correct,
            "points": points,
            "time": answer_time
        })
        
        # Log to quiz logs
        await self.log_answer(user, question["question"], answer.upper(), 
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
        embed.add_field(name="✏️ Answer", value=answer, inline=True)
        embed.add_field(name="✅ Correct", value="Yes" if correct else "No", inline=True)
        embed.add_field(name="⭐ Points", value=str(points), inline=True)
        embed.add_field(name="⏱️ Time", value=f"{time}s", inline=True)
        
        await self.quiz_logs_channel.send(embed=embed)
    
    async def end_question(self, message):
        """End current question"""
        self.update_countdown.stop()
        
        question = self.quiz_questions[self.current_question]
        
        # Send results
        embed = discord.Embed(
            title=f"⏰ **TIME'S UP!**",
            description=f"**Correct answer: {question['correct']}**\n\n"
                       f"**Question:** {question['question']}\n"
                       f"**Options:**\n" + "\n".join(question["options"]),
            color=discord.Color.orange()
        )
        
        # Show top 3 quickest correct answers
        correct_answers = []
        for user_id, data in self.participants.items():
            for answer in data["answers"]:
                if answer["question"] == self.current_question and answer["correct"]:
                    correct_answers.append({
                        "user": data["name"],
                        "time": answer["time"],
                        "points": answer["points"]
                    })
        
        correct_answers.sort(key=lambda x: x["time"])
        
        if correct_answers:
            embed.add_field(
                name="🏆 Fastest Correct Answers",
                value="\n".join([
                    f"**{i+1}. {ans['user']}** - {ans['time']}s ({ans['points']} pts)"
                    for i, ans in enumerate(correct_answers[:3])
                ]),
                inline=False
            )
        
        await self.quiz_channel.send(embed=embed)
        
        # Wait 5 seconds before next question
        await asyncio.sleep(5)
        
        # Move to next question
        self.current_question += 1
        await self.send_question()
    
    async def end_quiz(self):
        """End the entire quiz"""
        self.quiz_running = False
        self.update_countdown.stop()
        
        if self.question_timer:
            self.question_timer.cancel()
        
        # Sort participants by score
        sorted_participants = sorted(
            self.participants.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        # Create results embed
        embed = discord.Embed(
            title="🎉 **QUIZ FINISHED!**",
            description="Here are the final results:",
            color=discord.Color.gold()
        )
        
        # Top 10 leaderboard
        leaderboard = []
        for i, (user_id, data) in enumerate(sorted_participants[:10]):
            leaderboard.append(f"**{i+1}. {data['name']}** - {data['score']} points")
        
        if leaderboard:
            embed.add_field(
                name="🏆 **TOP 10 LEADERBOARD**",
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
        
        # Save results to file
        await self.save_results(sorted_participants)
    
    async def save_results(self, participants):
        """Save quiz results to file"""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "participants": {}
        }
        
        for user_id, data in participants:
            results["participants"][user_id] = data
        
        # Save to JSON file
        filename = f"quiz_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Send file to logs channel
        if self.quiz_logs_channel:
            await self.quiz_logs_channel.send(
                f"📊 **Quiz Results File**",
                file=discord.File(filename)
            )
        
        # Clean up
        try:
            os.remove(filename)
        except:
            pass

# --- ADD TO YOUR BOT ---
quiz_system = QuizSystem()

# --- QUIZ COMMANDS ---
@bot.group(name="quiz", invoke_without_command=True)
@commands.has_permissions(manage_messages=True)
async def quiz_group(ctx):
    """Quiz system commands"""
    embed = discord.Embed(
        title="🎯 **Quiz System**",
        description="**Commands:**\n"
                   "• `!!quiz start` - Start a new quiz\n"
                   "• `!!quiz stop` - Stop current quiz\n"
                   "• `!!quiz leaderboard` - Show current scores\n"
                   "• `!!quiz addq` - Add a new question\n"
                   "• `!!quiz questions` - List all questions",
        color=0x5865F2
    )
    await ctx.send(embed=embed)

@quiz_group.command(name="start")
@commands.has_permissions(manage_messages=True)
async def quiz_start(ctx):
    """Start a quiz in this channel"""
    if quiz_system.quiz_running:
        await ctx.send("❌ Quiz is already running!", delete_after=5)
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
    
    await ctx.send(f"✅ **Quiz starting in this channel!**\nLogs will go to {logs_channel.mention}")
    await quiz_system.start_quiz(ctx.channel, logs_channel)

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
    
    sorted_participants = sorted(
        quiz_system.participants.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )
    
    embed = discord.Embed(
        title="🏆 **Current Leaderboard**",
        color=discord.Color.gold()
    )
    
    for i, (user_id, data) in enumerate(sorted_participants[:10]):
        embed.add_field(
            name=f"{i+1}. {data['name']}",
            value=f"**Score:** {data['score']}\n"
                  f"**Correct:** {sum(1 for a in data['answers'] if a['correct'])}/{len(data['answers'])}",
            inline=True
        )
    
    await ctx.send(embed=embed)

@quiz_group.command(name="addquestion")
@commands.has_permissions(administrator=True)
async def quiz_addq(ctx, points: int, time_limit: int, *, question_data: str):
    """
    Add a new quiz question
    Format: !!quiz addq 300 60 Question? | A) Option1 | B) Option2 | C) Option3 | D) Option4 | C
    """
    try:
        parts = question_data.split(" | ")
        if len(parts) != 6:
            await ctx.send("❌ Wrong format! Use: `Question? | A) opt1 | B) opt2 | C) opt3 | D) opt4 | C`")
            return
        
        new_question = {
            "question": parts[0],
            "options": [parts[1], parts[2], parts[3], parts[4]],
            "correct": parts[5].upper(),
            "points": points,
            "time_limit": time_limit
        }
        
        quiz_system.quiz_questions.append(new_question)
        
        embed = discord.Embed(
            title="✅ **Question Added!**",
            description=new_question["question"],
            color=discord.Color.green()
        )
        
        for option in new_question["options"]:
            embed.add_field(name="​", value=option, inline=False)
        
        embed.add_field(name="✅ Correct Answer", value=new_question["correct"])
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
    
    # Check for quiz answers (A, B, C, D)
    if (quiz_system.quiz_running and 
        message.channel == quiz_system.quiz_channel and
        message.content.upper() in ["A", "B", "C", "D"]):
        
        await quiz_system.process_answer(message.author, message.content)
        
        # Add reaction to show answer received
        await message.add_reaction("✅")
    
    await bot.process_commands(message)

# --- UPDATE HELP COMMAND ---
# Add to your existing help command:
"""
**🎯 Quiz Commands (Mods)**
• `!!quiz start` - Start quiz
• `!!quiz stop` - Stop quiz  
• `!!quiz leaderboard` - Show scores
• `!!quiz addq` - Add question
• `!!quiz questions` - List questions
"""

# Add this line to on_ready():
print("✅ Quiz system loaded! Commands: !!quiz")



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