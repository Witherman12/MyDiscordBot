import discord
from discord.ext import commands
from datetime import datetime
from zoneinfo import ZoneInfo

class AuditLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1557048607478251561  
        self.tz = ZoneInfo("Europe/Athens")

    def get_time(self):
        return datetime.now(self.tz).strftime("%d/%m/%Y %H:%M:%S")

    # --- 1. ΔΙΑΓΡΑΦΗ ΜΗΝΥΜΑΤΟΣ ---
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        channel = self.bot.get_channel(self.log_channel_id)
        if channel:
            embed = discord.Embed(
                title="🗑️ [DELETED] Μήνυμα Διαγράφηκε",
                description=f"**Χρήστης:** {message.author.mention} ({message.author.name})\n**Κανάλι:** {message.channel.mention}",
                color=discord.Color.red()
            )
            embed.add_field(name="Περιεχόμενο:", value=message.content[:1000] or "*[Χωρίς κείμενο/Εικόνα]*", inline=False)
            embed.set_footer(text=f"Time: {self.get_time()} | ID: {message.author.id}")
            await channel.send(embed=embed)

    # --- 2. ΕΠΕΞΕΡΓΑΣΙΑ ΜΗΝΥΜΑΤΟΣ ---
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return

        channel = self.bot.get_channel(self.log_channel_id)
        if channel:
            embed = discord.Embed(
                title="✏️ [EDITED] Μήνυμα Επεξεργάστηκε",
                description=f"**Χρήστης:** {before.author.mention} ({before.author.name})\n**Κανάλι:** {before.channel.mention}\n[🔗 Μετάβαση στο μήνυμα]({after.jump_url})",
                color=discord.Color.orange()
            )
            embed.add_field(name="Πριν:", value=before.content[:1000] or "*[Κενό]*", inline=False)
            embed.add_field(name="Μετά:", value=after.content[:1000] or "*[Κενό]*", inline=False)
            embed.set_footer(text=f"Time: {self.get_time()} | ID: {before.author.id}")
            await channel.send(embed=embed)

    # --- 3. ΑΠΟΧΩΡΗΣΗ ΜΕΛΟΥΣ (LEAVE/KICK) ---
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(self.log_channel_id)
        if channel:
            embed = discord.Embed(
                title="🚪 [LEFT] Αποχώρηση Χρήστη",
                description=f"Ο/Η {member.mention} (`{member.name}`) εγκατέλειψε τον server.",
                color=discord.Color.dark_gray()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"Time: {self.get_time()} | ID: {member.id}")
            await channel.send(embed=embed)

    # --- 4. MOD ACTIONS: BANS & UNBANS ---
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        channel = self.bot.get_channel(self.log_channel_id)
        if channel:
            embed = discord.Embed(
                title="🔨 [BANNED] Χρήστης Αποκλείστηκε",
                description=f"Ο/Η {user.mention} (`{user.name}`) έφαγε Ban από τον server.",
                color=discord.Color.dark_red()
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"Time: {self.get_time()} | ID: {user.id}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        channel = self.bot.get_channel(self.log_channel_id)
        if channel:
            embed = discord.Embed(
                title="🕊️ [UNBANNED] Το Ban Αφαιρέθηκε",
                description=f"Ο/Η {user.mention} (`{user.name}`) έγινε Unban.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Time: {self.get_time()} | ID: {user.id}")
            await channel.send(embed=embed)

    # --- 5. MOD ACTIONS: TIMEOUTS & ROLE CHANGES ---
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        channel = self.bot.get_channel(self.log_channel_id)
        if not channel:
            return
        
        # Έλεγχος για αλλαγή Nickname στον Server
        if before.nick != after.nick:
            embed = discord.Embed(
                title="🏷️ [NICKNAME CHANGED] Αλλαγή Ψευδωνύμου",
                color=discord.Color.teal()
            )
            embed.add_field(name="Παλιό:", value=before.nick if before.nick else before.name, inline=True)
            embed.add_field(name="Νέο:", value=after.nick if after.nick else after.name, inline=True)
            embed.set_thumbnail(url=after.display_avatar.url)
            embed.set_footer(text=f"Time: {self.get_time()} | User ID: {after.id}")
            await channel.send(embed=embed)
        
        # Έλεγχος για Timeouts
        if before.timed_out_until != after.timed_out_until:
            if after.timed_out_until:
                timeout_end = after.timed_out_until.astimezone(self.tz).strftime("%d/%m/%Y %H:%M:%S")
                embed = discord.Embed(
                    title="🔇 [TIMEOUT] Επιβολή Mute",
                    description=f"Ο/Η {after.mention} τέθηκε σε Timeout μέχρι: **{timeout_end}**",
                    color=discord.Color.brand_red()
                )
            else:
                embed = discord.Embed(
                    title="🔊 [TIMEOUT REMOVED] Λήξη Mute",
                    description=f"Το Timeout του/της {after.mention} λύθηκε ή αφαιρέθηκε.",
                    color=discord.Color.blue()
                )
            embed.set_thumbnail(url=after.display_avatar.url)
            embed.set_footer(text=f"Time: {self.get_time()} | ID: {after.id}")
            await channel.send(embed=embed)

        # Έλεγχος για αλλαγή Ρόλων
        added_roles = [role for role in after.roles if role not in before.roles]
        removed_roles = [role for role in before.roles if role not in after.roles]
        
        if added_roles or removed_roles:
            actor = None
            try:
                # Ψάχνουμε στο Audit Log του Discord για να δούμε ποιος άλλαξε τον ρόλο
                async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update):
                    if entry.target.id == after.id:
                        actor = entry.user
                        break
            except discord.Forbidden:
                pass # Αν το bot δεν έχει άδεια να διαβάζει τα Audit Logs

            # Αν αυτός που έδωσε/αφαίρεσε τον ρόλο είναι Bot το αγνοούμε εντελώς
            if actor and actor.bot:
                return

            # Αν φτάσαμε εδώ, σημαίνει ότι κάποιος άνθρωπος (Admin/Mod) έκανε την αλλαγή
            actor_text = actor.mention if actor else "Άγνωστο (Δεν βρέθηκε στο Audit Log)"
            
            embed = discord.Embed(
                title="🎭 [ROLE UPDATE] Ενημέρωση Ρόλων",
                description=f"**Χρήστης:** {after.mention}\n**Τροποποιήθηκε από:** {actor_text}",
                color=discord.Color.gold()
            )
            
            if added_roles:
                embed.add_field(name="Προστέθηκαν:", value=", ".join([r.mention for r in added_roles]), inline=False)
            if removed_roles:
                embed.add_field(name="Αφαιρέθηκαν:", value=", ".join([r.mention for r in removed_roles]), inline=False)
            
            embed.set_footer(text=f"Time: {self.get_time()} | Target ID: {after.id}")
            await channel.send(embed=embed)
            
    # --- 6. VOICE CHANNEL ACTIVITY ---
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        channel = self.bot.get_channel(self.log_channel_id)
        if not channel:
            return

        # Μπήκε σε κανάλι (δεν ήταν σε κανένα πριν)
        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                title="🎙️ [VOICE JOIN] Σύνδεση σε Κανάλι",
                description=f"Ο/Η {member.mention} μπήκε στο κανάλι **{after.channel.mention}**",
                color=discord.Color.brand_green()
            )
            embed.set_footer(text=f"Time: {self.get_time()} | ID: {member.id}")
            await channel.send(embed=embed)

        # Βγήκε από κανάλι (δεν είναι σε κανένα τώρα)
        elif before.channel is not None and after.channel is None:
            embed = discord.Embed(
                title="🔇 [VOICE LEAVE] Αποσύνδεση από Κανάλι",
                description=f"Ο/Η {member.mention} βγήκε από το κανάλι **{before.channel.mention}**",
                color=discord.Color.dark_gray()
            )
            embed.set_footer(text=f"Time: {self.get_time()} | ID: {member.id}")
            await channel.send(embed=embed)

        # Άλλαξε κανάλι (Μετακίνηση)
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            embed = discord.Embed(
                title="🔄 [VOICE MOVE] Μετακίνηση σε άλλο Κανάλι",
                description=f"Ο/Η {member.mention} μετακινήθηκε από το **{before.channel.mention}** στο **{after.channel.mention}**",
                color=discord.Color.blurple()
            )
            embed.set_footer(text=f"Time: {self.get_time()} | ID: {member.id}")
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AuditLogs(bot))