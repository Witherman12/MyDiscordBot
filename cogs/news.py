"""
========================================
ΑΡΧΕΙΟ: news.py (Cogs)
ΠΕΡΙΓΡΑΦΗ: Ελέγχει το RSS Feed του Tabletop Battles κάθε 30 λεπτά
           και στέλνει τα νέα άρθρα σε συγκεκριμένο κανάλι με Embed.
           Συνδέεται με MongoDB για να θυμάται το τελευταίο άρθρο!
========================================
"""

import discord
from discord.ext import commands, tasks
import feedparser
import asyncio
import pymongo
import certifi
import os

# Σύνδεση με τη βάση
MONGO_URI = os.environ.get("MONGODB_URI")
client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True)
db = client["GloriousDatabase"]
news_col = db["News"] # Το collection που θα κρατάει τα άρθρα

class NewsFeed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Το ID του καναλιού #new-updates
        self.news_channel_id = 850011185314267177  
        
        # Το RSS Feed του Tabletop Battles
        self.feed_url = "https://www.tabletopbattles.com/feed/"
        
        # Ο Agent για να μην μας μπλοκάρει το site
        self.browser_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        
        # Λέξεις κλειδιά/Κατηγορίες που μας ενδιαφέρουν
        self.valid_keywords = [
            "40k", "warhammer 40k", "warhammer 40000", "warhammer 40,000",
            "aos", "age of sigmar", "kill team", "warhammer", "old world", "horus heresy"
        ]
        
        # Ξεκινάει την λούπα αυτόματα
        self.check_news.start()

    def cog_unload(self):
        self.check_news.cancel()

    # Ελέγχει κάθε 30 λεπτά
    @tasks.loop(minutes=30)
    async def check_news(self):
        # Διαβάζει το RSS Feed (βάζουμε kwargs για τον Agent στο asyncio)
        feed = await asyncio.to_thread(feedparser.parse, self.feed_url, agent=self.browser_agent)
        
        if not feed.entries:
            print("⚠️ [News Radar] Δεν βρέθηκαν άρθρα. Πιθανό μπλοκάρισμα.")
            return

        # ΨΑΧΝΟΥΜΕ ΤΟ ΠΙΟ ΠΡΟΣΦΑΤΟ ΑΡΘΡΟ ΠΟΥ ΤΑΙΡΙΑΖΕΙ ΣΤΑ ΦΙΛΤΡΑ
        target_entry = None
        
        for entry in feed.entries:
            title_lower = entry.title.lower()
            
            # Μαζεύουμε όλα τα tags/κατηγορίες του άρθρου αν υπάρχουν
            tags_lower = []
            if hasattr(entry, 'tags'):
                tags_lower = [tag.term.lower() for tag in entry.tags]
                
            # Ελέγχουμε αν κάποια από τις λέξεις-κλειδιά υπάρχει στον Τίτλο Ή στα Tags
            is_relevant = False
            for kw in self.valid_keywords:
                if kw in title_lower or any(kw in tag for tag in tags_lower):
                    is_relevant = True
                    break # Βρήκαμε λέξη-κλειδί, σταματάμε τον έλεγχο για αυτό το άρθρο
            
            if is_relevant:
                target_entry = entry
                break # Βρήκαμε το πιο πρόσφατο σχετικό άρθρο, σταματάμε το ψάξιμο
                
        # Αν δεν βρέθηκε απολύτως κανένα σχετικό άρθρο στο Feed
        if not target_entry:
            # print("💤 [News Radar] Δεν υπάρχει κανένα άρθρο για 40k/AoS στο feed αυτή τη στιγμή.")
            return

        # Πήραμε το σωστό άρθρο
        current_link = target_entry.link
        title = target_entry.title

        # Ζητάμε από το MongoDB να μας πει ποιο ήταν το τελευταίο άρθρο που στείλαμε
        last_news = news_col.find_one({"_id": "latest_article"})

        # Αν η βάση έχει ήδη αυτό το άρθρο, δεν κάνουμε τίποτα
        if last_news and last_news.get("link") == current_link:
            # print("💤 [News Radar] Το τελευταίο 40k/AoS άρθρο έχει ήδη σταλεί.")
            return
            
        # --- ΑΝ ΦΤΑΣΕΙ ΕΔΩ, ΣΗΜΑΙΝΕΙ ΟΤΙ ΒΡΗΚΕ ΝΕΟ, ΣΧΕΤΙΚΟ ΑΡΘΡΟ! ---
        
        # Αποθηκεύουμε το νέο link στη Βάση για την επόμενη φορά
        news_col.update_one({"_id": "latest_article"}, {"$set": {"link": current_link, "title": title}}, upsert=True)
            
        channel = self.bot.get_channel(self.news_channel_id)
        if channel:
            # Φτιάχνουμε το Embed
            embed = discord.Embed(
                title=f"📜 {title}",
                url=current_link,
                color=discord.Color.from_rgb(255, 255, 255),
                description="Νέο άρθρο δημοσιεύτηκε!\nΠατήστε τον τίτλο για να το διαβάσετε."
            )
            
            # Βάζουμε το logo 
            main_logo = "https://cdn.discordapp.com/attachments/850011185314267177/1523030976622493716/ttb_logo_text_white.png?ex=6a4aa0a1&is=6a494f21&hm=728378f8686a35b19fbf57b82d4ef32bab760aaf1d841ff2acce3e9c96348af9&"
            sec_logo = "https://cdn.discordapp.com/attachments/850011185314267177/1523063566675218534/sec_logo.png?ex=6a4abefb&is=6a496d7b&hm=409512ed10459af4c6bc65504c1aa38d3f5d0564ce6786e52c61fd5fdefc197f&"
            embed.set_thumbnail(url=main_logo)
            embed.set_footer(text="Warhammer Community Updates", icon_url=sec_logo)
            
            # Στέλνει το μήνυμα και το Embed
            await channel.send(
                content="<:Warhammer_1:1416864475520438302> **Incoming Transmission!**", 
                embed=embed
            )
            print(f"✅ [News Radar] Νέο άρθρο στάλθηκε: {title}")

    @check_news.before_loop
    async def before_check_news(self):
        # Περιμένει να φορτώσει πλήρως το bot πριν ξεκινήσει το ψάξιμο
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(NewsFeed(bot))