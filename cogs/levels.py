"""
========================================
ΑΡΧΕΙΟ: levels.py (Cogs)
ΠΕΡΙΓΡΑΦΗ: Σύστημα Leveling και XP.
========================================
"""

import discord
from discord.ext import commands
import pymongo
import certifi
import os
import time
import random

# Σύνδεση με τη MongoDB
MONGO_URI = os.environ.get("MONGODB_URI")
client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True)
db = client["GloriousDatabase"]
levels_col = db["Levels"]

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}
        
        self.announce_channel_id = 801814186434756610 

    def get_xp_for_level(self, level):
        # Βασική RPG φόρμουλα για το πόσο XP χρειάζεται το επόμενο level
        return 5 * (level ** 2) + 50 * level + 100

    @commands.Cog.listener()
    async def on_message(self, message):
        # Αγνοούμε bots και μηνύματα εκτός server
        if message.author.bot or not message.guild:
            return

        user_id = str(message.author.id)
        current_time = time.time()

        # 1. Έλεγχος Cooldown (Δίνει XP μόνο 1 φορά κάθε 59 δευτερόλεπτα)
        if user_id in self.cooldowns and current_time - self.cooldowns[user_id] < 59:
            return

        self.cooldowns[user_id] = current_time

        # 2. Υπολογισμός XP (Από 20 έως 30 XP ανά μήνυμα)
        xp_gained = random.randint(20, 30)

        # 3. Φόρτωση δεδομένων από MongoDB
        user_data = levels_col.find_one({"_id": user_id})
        if not user_data:
            user_data = {"_id": user_id, "xp": 0, "level": 0}

        new_xp = user_data["xp"] + xp_gained
        current_level = user_data["level"]

        # 4. Έλεγχος για Level Up!
        xp_needed = self.get_xp_for_level(current_level)
        leveled_up = False

        while new_xp >= xp_needed:
            current_level += 1
            new_xp -= xp_needed  # Κρατάει XP για το επόμενο level
            xp_needed = self.get_xp_for_level(current_level)
            leveled_up = True

        # 5. Αποθήκευση στη Βάση
        levels_col.update_one(
            {"_id": user_id}, 
            {"$set": {"xp": new_xp, "level": current_level}}, 
            upsert=True
        )

        # 6. Ανακοίνωση Level Up
        if leveled_up:
            channel = self.bot.get_channel(self.announce_channel_id)
            if channel:
                await channel.send(
                    f"<:Upvote:1461299234656616581> **Glorious news!** <@{user_id}> has fought bravely and reached **Level {current_level}**! The Emperor smiles upon them. <:Warhammer_1:1416864475520438302>"
                )

    # --- ΕΝΤΟΛΗ: RANK ---
    @commands.command(name="rank")
    async def check_rank(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_data = levels_col.find_one({"_id": str(member.id)})
        
        if not user_data:
            await ctx.send(f"⚠️ **{member.display_name}** is a fresh recruit and has no combat experience yet (0 XP).")
            return

        level = user_data["level"]
        xp = user_data["xp"]
        xp_needed = self.get_xp_for_level(level)

        embed = discord.Embed(title=f"📜 Service Record: {member.display_name}", color=discord.Color.gold())
        embed.add_field(name="Level", value=f"**{level}**", inline=True)
        embed.add_field(name="Combat XP", value=f"**{xp} / {xp_needed}**", inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await ctx.send(embed=embed)

    # --- ΕΝΤΟΛΗ: SETLEVEL (MIGRATION ΑΠΟ MEE6 - ΜΟΝΟ ΓΙΑ ADMINS) ---
    @commands.command(name="setlevel")
    @commands.has_permissions(administrator=True)
    async def set_level(self, ctx, member: discord.Member, level: int):
        levels_col.update_one(
            {"_id": str(member.id)}, 
            {"$set": {"level": level, "xp": 0}}, 
            upsert=True
        )
        await ctx.send(f"✅ Administratum Override: Το level του **{member.display_name}** ρυθμίστηκε χειροκίνητα στο **{level}**.")

    # --- ΕΝΤΟΛΗ: LEADERBOARD ---
    @commands.command(name="toprank", aliases=["leaderboard", "levels"])
    async def top_ranks(self, ctx):
        # Ζητάμε από τη MongoDB τους top 9, ταξινομημένους κατά Level και μετά κατά XP (φθίνουσα σειρά)
        top_users = levels_col.find().sort([("level", -1), ("xp", -1)]).limit(9)
        
        embed = discord.Embed(
            title="🏆 **Sector Command: Elite Operatives**",
            description="Οι πιο ενεργοί του server:",
            color=discord.Color.dark_red()
        )
        
        message = ""
        for index, user_data in enumerate(top_users, 1):
            user_id = user_data.get("_id")
            level = user_data.get("level", 0)
            xp = user_data.get("xp", 0)
            
            # Προσπάθεια να βρούμε το όνομα του μέλους από τον server
            member = ctx.guild.get_member(int(user_id))
            
            # Αν το μέλος είναι ακόμα στον server δείχνουμε το όνομά του, αλλιώς κάνουμε ping το ID
            if member:
                display_name = member.display_name
            else:
                display_name = f"<@{user_id}>"
            
            message += f"**{index}.** {display_name} - Level: **{level}** *(XP: {xp})*\n"
            
        if not message:
            message = "Το αρχείο είναι άδειο. Κανείς δεν έχει αποδείξει την αξία του ακόμα."
            
        embed.add_field(name="Leaderboard", value=message, inline=False)
        embed.set_footer(text="The Emperor knows your name.")
        
        await ctx.send(embed=embed)
async def setup(bot):
    await bot.add_cog(LevelSystem(bot))