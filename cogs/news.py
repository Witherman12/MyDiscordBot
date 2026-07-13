import discord
from discord.ext import commands, tasks
import feedparser
import asyncio
import pymongo
import certifi
import os
import time

# Σύνδεση με τη βάση
MONGO_URI = os.environ.get("MONGODB_URI")
client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True)
db = client["GloriousDatabase"]
news_col = db["News"] 

class NewsFeed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.news_channel_id = 1416856517231116510  
        self.feed_url = "https://www.tabletopbattles.com/feed/"
        self.browser_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        
        self.valid_keywords = [
            # Βασικά (Ονόματα Παιχνιδιών)
            "40k", "warhammer 40k", "warhammer 40000", "warhammer 40,000",
            "aos", "age of sigmar", "kill team", "warhammer", "old world", "horus heresy",
            
            # Στήλες Άρθρων
            "competitive intel", "competitive innovations", "hammer of math", 
            "ruleshammer", "how to paint everything", "detachment focus",
            "black library", "that 6+++ show", "lunchtime show",
            
            # Εκδόσεις & Λέξεις-Κλειδιά
            "11th edition", "11th ed", "in 11th", "launch tier list",
            
            # Factions
            "space marines", "genestealer cults", "ork", "orks", "chaos", 
            "tyranids", "necron", "necrons", "tau empire", "aeldari", 
            "drukhari", "adeptus mechanicus", "imperium", "blood axes", "goffs"
        ]
        
    async def cog_load(self):
        self.check_news.start()

    def cog_unload(self):
        self.check_news.cancel()

    @tasks.loop(minutes=90)
    async def check_news(self):
        try:
            # CACHE BUSTING
            busted_url = f"{self.feed_url}?nocache={int(time.time())}"
            
            feed = await asyncio.to_thread(feedparser.parse, busted_url, agent=self.browser_agent)
            
            if not feed.entries:
                print("⚠️ [News Radar] Δεν βρέθηκαν άρθρα στο feed αυτή τη στιγμή. Ίσως το site μπλόκαρε το request.")
                return

            recent_entries = reversed(feed.entries[:20])
            
            print("\n--- 📡 ΞΕΚΙΝΑΕΙ ΣΑΡΩΣΗ ΑΡΘΡΩΝ ---")
            
            for entry in recent_entries:
                title = entry.title
                title_lower = title.lower()
                current_link = entry.link
                
                # 1. Παίρνουμε τα tags
                tags_lower = []
                if hasattr(entry, 'tags'):
                    tags_lower = [tag.term.lower() for tag in entry.tags]
                
                # 2. Παίρνουμε την περίληψη (summary/description)
                summary_lower = ""
                if hasattr(entry, 'summary'):
                    summary_lower = entry.summary.lower()
                elif hasattr(entry, 'description'):
                    summary_lower = entry.description.lower()
                    
                # 🛠️ DEBUG PRINT: Για να βλέπεις στα Logs του Render τι διαβάζει το bot!
                print(f"🔎 Ελέγχω: '{title}'")
                print(f"   ┣ Tags: {tags_lower}")
                    
                # 3. Έλεγχος Λέξεων-Κλειδιών σε ΤΙΤΛΟ, TAGS ΚΑΙ ΠΕΡΙΛΗΨΗ
                is_relevant = False
                for kw in self.valid_keywords:
                    if kw in title_lower or kw in summary_lower or any(kw in tag for tag in tags_lower):
                        is_relevant = True
                        break 
                
                if not is_relevant:
                    print("   ┗ ❌ Απορρίφθηκε (Άσχετο παιχνίδι/Χωρίς keywords)")
                    continue 
                    
                # 4. Έλεγχος Βάσης Δεδομένων
                article_exists = news_col.find_one({"_id": current_link})
                
                if article_exists:
                    print("   ┗ ⏭️ Προσπεράστηκε (Υπάρχει ήδη στη MongoDB)")
                    continue 
                    
                # --- ΝΕΟ ΑΡΘΡΟ ΒΡΕΘΗΚΕ! ---
                print("   ┗ ✅ ΕΓΚΡΙΘΗΚΕ! Αποθήκευση και αποστολή...")
                news_col.insert_one({"_id": current_link, "title": title})
                
                channel = self.bot.get_channel(self.news_channel_id)
                if channel:
                    embed = discord.Embed(
                        title=f"📜 {title}",
                        url=current_link,
                        color=discord.Color.from_rgb(255, 255, 255),
                        description="Νέο άρθρο δημοσιεύτηκε!\nΠατήστε τον τίτλο για να το διαβάσετε."
                    )
                    
                    main_logo = "https://cdn.discordapp.com/attachments/850011185314267177/1523030976622493716/ttb_logo_text_white.png?ex=6a4aa0a1&is=6a494f21&hm=728378f8686a35b19fbf57b82d4ef32bab760aaf1d841ff2acce3e9c96348af9&"
                    sec_logo = "https://cdn.discordapp.com/attachments/850011185314267177/1523063566675218534/sec_logo.png?ex=6a4abefb&is=6a496d7b&hm=409512ed10459af4c6bc65504c1aa38d3f5d0564ce6786e52c61fd5fdefc197f&"
                    embed.set_thumbnail(url=main_logo)
                    embed.set_footer(text="Tabletop Battles Updates", icon_url=sec_logo)
                    
                    await channel.send(
                        content="<:Warhammer_1:1416864475520438302> **Incoming Transmission!**", 
                        embed=embed
                    )
                    print(f"✅ [News Radar] Νέο άρθρο στάλθηκε: {title}")
                    
                    await asyncio.sleep(2)
                    
        except Exception as e:
            print(f"❌ [News Radar] Σφάλμα κατά τον έλεγχο (Η λούπα επέζησε): {e}")

    @check_news.before_loop
    async def before_check_news(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(NewsFeed(bot))