import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta, timezone
import random

class CullingGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mining_channel = None  # will be set via command
        self.energy_regen.start()

    def cog_unload(self):
        self.energy_regen.cancel()

    # ------------------------------------------------------------------
    # Energy Regen Task (every hour)
    # ------------------------------------------------------------------
    @tasks.loop(hours=1)
    async def energy_regen(self):
        """Give 1 energy every hour to all players (up to max)."""
        await self.bot.wait_until_ready()
        async with self.bot.db_pool.acquire() as conn:
            # Get all users who have less than max energy and last regen > 1 hour ago
            rows = await conn.fetch("""
                SELECT user_id, energy, max_energy, last_energy_regen
                FROM player_stats
                WHERE energy < max_energy
            """)
            now = datetime.now(timezone.utc)
            for row in rows:
                last = row['last_energy_regen']
                if last.tzinfo is None:
                    last = last.replace(tzinfo=timezone.utc)
                if (now - last) >= timedelta(hours=1):
                    new_energy = min(row['energy'] + 1, row['max_energy'])
                    await conn.execute("""
                        UPDATE player_stats
                        SET energy = $1, last_energy_regen = $2
                        WHERE user_id = $3
                    """, new_energy, now, row['user_id'])

    @energy_regen.before_loop
    async def before_energy_regen(self):
        await self.bot.wait_until_ready()

    # ------------------------------------------------------------------
    # Helper: Ensure player stats exist (called when buying weapon)
    # ------------------------------------------------------------------
    async def ensure_player_stats(self, user_id: str):
        """Create player stats with default HP/energy if not exists."""
        async with self.bot.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO player_stats (user_id, hp, max_hp, energy, max_energy, last_energy_regen)
                VALUES ($1, 1000, 1000, 3, 3, NOW())
                ON CONFLICT (user_id) DO NOTHING
            """, user_id)

    # ------------------------------------------------------------------
    # Admin: Set mining channel
    # ------------------------------------------------------------------
    @commands.command(name='setminingchannel')
    @commands.has_permissions(administrator=True)
    async def set_mining_channel(self, ctx, channel: discord.TextChannel):
        self.mining_channel = channel.id
        await ctx.send(f"✅ Mining channel set to {channel.mention}")

    # ------------------------------------------------------------------
    # Mining: Start
    # ------------------------------------------------------------------
    @commands.command(name='minestart')
    async def mine_start(self, ctx):
        """Start mining in the designated mining channel."""
        if self.mining_channel is None or ctx.channel.id != self.mining_channel:
            await ctx.send("❌ You can only mine in the designated mining channel.")
            return

        user_id = str(ctx.author.id)
        await self.ensure_player_stats(user_id)

        async with self.bot.db_pool.acquire() as conn:
            # Check if already mining
            existing = await conn.fetchval("SELECT mining_start FROM player_stats WHERE user_id = $1", user_id)
            if existing:
                await ctx.send("❌ You are already mining! Use `!!minestop` to finish.")
                return

            # Start mining
            now = datetime.now(timezone.utc)
            await conn.execute("""
                UPDATE player_stats
                SET mining_start = $1, pending_reward = 0
                WHERE user_id = $2
            """, now, user_id)

        embed = discord.Embed(
            title="⛏️ Mining Started",
            description=f"{ctx.author.mention} has started mining!\n"
                        "You will earn gems over time. Use `!!minestop` to claim.\n"
                        "**Note:** You can be plundered while mining!",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    # ------------------------------------------------------------------
    # Mining: Stop
    # ------------------------------------------------------------------
    @commands.command(name='minestop')
    async def mine_stop(self, ctx):
        """Stop mining and claim gems."""
        user_id = str(ctx.author.id)
        async with self.bot.db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT mining_start FROM player_stats WHERE user_id = $1", user_id)
            if not row or not row['mining_start']:
                await ctx.send("❌ You are not mining.")
                return

            start = row['mining_start']
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            hours_mined = (now - start).total_seconds() / 3600
            hours_mined = min(hours_mined, 12)  # max 12 hours

            # Calculate gems: 1% of a pool per 2 hours (base pool maybe 1000?)
            # We'll define a pool that grows over time; for simplicity, pool = 1000 per 2 hours? 
            # Let's use a fixed pool of 5000 gems total, and each 2 hours gives 1% = 50 gems.
            # So reward = (hours_mined // 2) * 50  (rounded down)
            intervals = int(hours_mined // 2)
            gems_earned = intervals * 50  # 50 gems per 2 hours

            # Update user gems
            if gems_earned > 0:
                await currency_system.add_gems(user_id, gems_earned, "Mining reward")

            # Reset mining
            await conn.execute("""
                UPDATE player_stats
                SET mining_start = NULL, pending_reward = 0
                WHERE user_id = $1
            """, user_id)

        embed = discord.Embed(
            title="⛏️ Mining Finished",
            description=f"You mined for **{hours_mined:.1f} hours** and earned **{gems_earned} gems**.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    # ------------------------------------------------------------------
    # Plunder
    # ------------------------------------------------------------------
    @commands.command(name='plunder')
    async def plunder(self, ctx, target: discord.Member):
        """Use 1 energy to plunder a miner and steal 30% of their pending reward."""
        attacker_id = str(ctx.author.id)
        defender_id = str(target.id)

        if attacker_id == defender_id:
            await ctx.send("❌ You cannot plunder yourself.")
            return

        await self.ensure_player_stats(attacker_id)
        await self.ensure_player_stats(defender_id)

        async with self.bot.db_pool.acquire() as conn:
            # Check plunder limits (2 per day)
            today = datetime.now(timezone.utc).date()
            stats = await conn.fetchrow("""
                SELECT energy, plunder_count, last_plunder_reset
                FROM player_stats WHERE user_id = $1
            """, attacker_id)
            if not stats or stats['energy'] < 1:
                await ctx.send("❌ You need at least 1 energy to plunder.")
                return
            if stats['last_plunder_reset'] != today:
                # Reset count
                await conn.execute("UPDATE player_stats SET plunder_count = 0, last_plunder_reset = $1 WHERE user_id = $2", today, attacker_id)
                plunder_count = 0
            else:
                plunder_count = stats['plunder_count']
            if plunder_count >= 2:
                await ctx.send("❌ You have already used your 2 plunders today.")
                return

            # Check defender is mining
            defender = await conn.fetchrow("SELECT mining_start, pending_reward FROM player_stats WHERE user_id = $1", defender_id)
            if not defender or not defender['mining_start']:
                await ctx.send("❌ That user is not mining.")
                return

            # Calculate pending reward (same as mining stop)
            start = defender['mining_start']
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            hours_mined = (now - start).total_seconds() / 3600
            intervals = int(hours_mined // 2)
            pending = intervals * 50  # 50 per 2h

            if pending == 0:
                await ctx.send("❌ That user hasn't mined enough yet (need at least 2 hours).")
                return

            steal = int(pending * 0.3)  # 30%
            # Give stolen gems to attacker
            await currency_system.add_gems(attacker_id, steal, f"Plundered from {target.name}")

            # Deduct from defender? Actually plunder doesn't remove defender's gems; they still get their mining reward? The description says plunder rewards are based on miner's earned, so perhaps defender loses that amount? Usually plunder steals from the pending reward, so defender gets less. Let's implement that: defender's pending reward is reduced by the stolen amount, and they get the rest when they stop mining.
            # We'll store pending_reward in player_stats and update it.
            await conn.execute("""
                UPDATE player_stats
                SET pending_reward = pending_reward + $1
                WHERE user_id = $2
            """, -steal, defender_id)  # negative to reduce

            # Deduct energy from attacker
            await conn.execute("""
                UPDATE player_stats
                SET energy = energy - 1, plunder_count = plunder_count + 1
                WHERE user_id = $1
            """, attacker_id)

        embed = discord.Embed(
            title="💰 Plunder Successful!",
            description=f"{ctx.author.mention} plundered **{steal} gems** from {target.mention}!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    # ------------------------------------------------------------------
    # Attack
    # ------------------------------------------------------------------
    @commands.command(name='attack')
    async def attack(self, ctx, target: discord.Member):
        """Attack another player using your weapon. Uses 1 energy."""
        attacker_id = str(ctx.author.id)
        defender_id = str(target.id)

        if attacker_id == defender_id:
            await ctx.send("❌ You cannot attack yourself.")
            return

        await self.ensure_player_stats(attacker_id)
        await self.ensure_player_stats(defender_id)

        async with self.bot.db_pool.acquire() as conn:
            # Check energy
            energy = await conn.fetchval("SELECT energy FROM player_stats WHERE user_id = $1", attacker_id)
            if not energy or energy < 1:
                await ctx.send("❌ You need at least 1 energy to attack.")
                return

            # Get attacker's weapon (latest)
            weapon = await conn.fetchrow("""
                SELECT uw.attack, COALESCE(si.name, uw.generated_name) as name, uw.image_url
                FROM user_weapons uw
                LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                WHERE uw.user_id = $1
                ORDER BY uw.purchased_at DESC
                LIMIT 1
            """, attacker_id)
            if not weapon:
                await ctx.send("❌ You don't have a weapon to attack with!")
                return

            # Get defender's HP and weapon (for display)
            defender_stats = await conn.fetchrow("SELECT hp FROM player_stats WHERE user_id = $1", defender_id)
            defender_weapon = await conn.fetchrow("""
                SELECT uw.attack, COALESCE(si.name, uw.generated_name) as name
                FROM user_weapons uw
                LEFT JOIN shop_items si ON uw.weapon_item_id = si.item_id
                WHERE uw.user_id = $1
                ORDER BY uw.purchased_at DESC
                LIMIT 1
            """, defender_id)

            # Deduct energy
            await conn.execute("UPDATE player_stats SET energy = energy - 1 WHERE user_id = $1", attacker_id)

        # Build attack embed
        embed = discord.Embed(
            title="⚔️ Attack Initiated!",
            description=f"{ctx.author.mention} is attacking {target.mention}!",
            color=discord.Color.orange()
        )
        embed.add_field(name="Attacker's Weapon", value=f"{weapon['name']} (+{weapon['attack']} ATK)", inline=True)
        if defender_weapon:
            embed.add_field(name="Defender's Weapon", value=f"{defender_weapon['name']} (+{defender_weapon['attack']} ATK)", inline=True)
        embed.add_field(name="Defender's HP", value=f"{defender_stats['hp']} / 1000", inline=False)
        if weapon['image_url']:
            embed.set_thumbnail(url=weapon['image_url'])

        # Create a view with a button to resolve the attack
        view = AttackView(attacker_id, defender_id, weapon['attack'], self.bot)
        await ctx.send(embed=embed, view=view)

class AttackView(discord.ui.View):
    def __init__(self, attacker_id, defender_id, attack_power, bot):
        super().__init__(timeout=60)
        self.attacker_id = attacker_id
        self.defender_id = defender_id
        self.attack_power = attack_power
        self.bot = bot

    @discord.ui.button(label="Resolve Attack", style=discord.ButtonStyle.danger)
    async def resolve(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Only the defender can resolve? Or anyone? Let's allow defender to click.
        if str(interaction.user.id) != self.defender_id:
            await interaction.response.send_message("Only the defender can resolve this attack.", ephemeral=True)
            return

        await interaction.response.defer()
        # Calculate damage (simple: attack_power)
        damage = self.attack_power
        async with self.bot.db_pool.acquire() as conn:
            # Get defender's current HP
            defender = await conn.fetchrow("SELECT hp FROM player_stats WHERE user_id = $1", self.defender_id)
            if not defender:
                await interaction.followup.send("Defender stats not found.")
                return
            new_hp = defender['hp'] - damage
            if new_hp < 0:
                new_hp = 0
            await conn.execute("UPDATE player_stats SET hp = $1 WHERE user_id = $2", new_hp, self.defender_id)

            # Log attack
            await conn.execute("""
                INSERT INTO attack_logs (attacker_id, defender_id, damage)
                VALUES ($1, $2, $3)
            """, self.attacker_id, self.defender_id, damage)

        # Disable buttons
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

        # Send result
        embed = discord.Embed(
            title="⚔️ Attack Result",
            description=f"{interaction.user.mention} took **{damage} damage**!",
            color=discord.Color.red()
        )
        embed.add_field(name="HP Remaining", value=f"{new_hp} / 1000")
        await interaction.followup.send(embed=embed)

        if new_hp == 0:
            # Optionally, handle death (e.g., reset HP, drop items, etc.)
            await interaction.followup.send(f"{interaction.user.mention} has been defeated! They will respawn with 1000 HP.")
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("UPDATE player_stats SET hp = 1000 WHERE user_id = $1", self.defender_id)

bot.add_cog(CullingGame(bot))