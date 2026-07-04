"""
========================================
ΑΡΧΕΙΟ: news.py (Cogs)
ΠΕΡΙΓΡΑΦΗ: Ελέγχει το RSS Feed του Warhammer Community κάθε 30 λεπτά
           και στέλνει τα νέα άρθρα σε συγκεκριμένο κανάλι με Embed.
========================================
"""

import discord
from discord.ext import commands, tasks
import feedparser
import asyncio

class NewsFeed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Το ID του καναλιού #new-updates
        self.news_channel_id = 850011185314267177  
        
        # Το επίσημο RSS Feed του Warhammer Community
        self.feed_url = "https://www.goonhammer.com/feed/"
        
        # Αποθηκεύει το τελευταίο άρθρο για να μην κάνει spam τα παλιά
        self.last_post_link = None
        
        # Ξεκινάει την λούπα αυτόματα
        self.check_news.start()

    def cog_unload(self):
        self.check_news.cancel()

    # Ελέγχει κάθε 30 λεπτά
    @tasks.loop(minutes=30)
    async def check_news(self):
        # Διαβάζει το RSS Feed χωρίς να παγώνει το υπόλοιπο bot με χρήση thread
        feed = await asyncio.to_thread(feedparser.parse, self.feed_url)
        
        if not feed.entries:
            return

        # Παίρνουμε το πιο πρόσφατο άρθρο
        latest_entry = feed.entries[0]
        current_link = latest_entry.link

        # Αν το bot μόλις άνοιξε, κρατάμε το τελευταίο άρθρο σαν βάση και δεν στέλνουμε τίποτα
        if self.last_post_link is None:
            self.last_post_link = current_link
            print(f"📡 [News Radar] Κλείδωσε στο τελευταίο άρθρο: {current_link}")
            return

        # Αν βρήκε καινούριο άρθρο
        if current_link != self.last_post_link:
            self.last_post_link = current_link
            
            channel = self.bot.get_channel(self.news_channel_id)
            if channel:
                title = latest_entry.title
                
                # Φτιάχνουμε το Embed
                embed = discord.Embed(
                    title=f"📜 {title}",
                    url=current_link,
                    color=discord.Color.from_rgb(255, 0, 0), # Κόκκινο χρώμα (Inquisition/WarCom)
                    description="Νέο άρθρο δημοσιεύτηκε!\nΠατήστε τον τίτλο για να το διαβάσετε."
                )
                
                # Βάζουμε το logo του Warhammer Community
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