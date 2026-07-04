"""
========================================
ΑΡΧΕΙΟ: news.py (Cogs)
ΠΕΡΙΓΡΑΦΗ: Ελέγχει το RSS Feed του Goonhammer κάθε 30 λεπτά
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
        
        # Το RSS Feed του Goonhammer (αφού το WarCom δεν έχει)
        self.feed_url = "https://www.goonhammer.com/feed/"
        
        # Ο Agent για να μην μας μπλοκάρει το site
        self.browser_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        
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

        # Παίρνουμε το πιο πρόσφατο άρθρο
        latest_entry = feed.entries[0]
        current_link = latest_entry.link
        title = latest_entry.title

        # Ζητάμε από το MongoDB να μας πει ποιο ήταν το τελευταίο άρθρο
        last_news = news_col.find_one({"_id": "latest_article"})

        # Αν η βάση είναι άδεια (πρώτη φορά που τρέχει) ή το άρθρο υπάρχει ήδη
        if last_news and last_news.get("link") == current_link:
            print("💤[News Radar] Δεν υπάρχει νέο άρθρο.") # Προαιρετικό print
            return
            
        # --- ΑΝ ΦΤΑΣΕΙ ΕΔΩ, ΣΗΜΑΙΝΕΙ ΟΤΙ ΒΡΗΚΕ ΝΕΟ ΑΡΘΡΟ! ---
        
        # Αποθηκεύουμε το νέο link στη Βάση για την επόμενη φορά
        news_col.update_one({"_id": "latest_article"}, {"$set": {"link": current_link, "title": title}}, upsert=True)
            
        channel = self.bot.get_channel(self.news_channel_id)
        if channel:
            # Φτιάχνουμε το Embed
            embed = discord.Embed(
                title=f"📜 {title}",
                url=current_link,
                color=discord.Color.from_rgb(255, 0, 0), # Κόκκινο χρώμα
                description="Νέο άρθρο δημοσιεύτηκε!\nΠατήστε τον τίτλο για να το διαβάσετε."
            )
            
            # Βάζουμε το logo 
            warcom_logo = "https://cdn.discordapp.com/attachments/850011185314267177/1523021068497846363/WarhammerComunityLogo.png?ex=6a4a9767&is=6a4945e7&hm=e65745367cae5fd9b7d5c3c335764b7df20ef06796cc7fce3c55a9b7442ecacc&"
            embed.set_thumbnail(url=warcom_logo)
            embed.set_footer(text="Warhammer Community Updates", icon_url=warcom_logo)
            
            # Στέλνει το μήνυμα και το Embed
            await channel.send(
                content="🚨 **Εισερχόμενη Μετάδοση!** 🚨", 
                embed=embed
            )
            print(f"✅ [News Radar] Νέο άρθρο στάλθηκε: {title}")

    @check_news.before_loop
    async def before_check_news(self):
        # Περιμένει να φορτώσει πλήρως το bot πριν ξεκινήσει το ψάξιμο
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(NewsFeed(bot))