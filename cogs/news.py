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
        self.browser_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        
        # --- ΠΗΓΕΣ ΕΙΔΗΣΕΩΝ ---
        self.news_sources = [
            {
                "name": "Tabletop Battles",
                "url": "https://www.tabletopbattles.com/feed/",
                "footer_icon": "https://cdn.discordapp.com/attachments/1523030976782143645/1542469989955801139/goonhammer.png?ex=6a91589f&is=6a90071f&hm=33eaa3c1ba01686404b0da4d7049112a8ba334c579028bb68ce4221b27a3812b&",
                "thumbnail": "https://cdn.discordapp.com/attachments/850011185314267177/1523030976622493716/ttb_logo_text_white.png?ex=6a8be2e1&is=6a8a9161&hm=ae5b615894c7933e70d45aec0efee1aaa087dc59d0fbfcf40cbe10fa0fffebef&"
            },
            {
                "name": "Auspex Tactics", 
                "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC6Gco9PWxmJmJ5CqfbChuiQ",
                "footer_icon": "https://cdn.discordapp.com/attachments/1523030976782143645/1541033367854780547/vecteezy_youtube-logo-png-youtube-logo-transparent-png-youtube-icon_23986704.png?ex=6a8c1ea9&is=6a8acd29&hm=e6a39cc27508389afbbdea1c5ce244bb4381f540d3f7bbfc6c3cb5b4b3417078&",
                "thumbnail": "https://cdn.discordapp.com/attachments/1523030976782143645/1541033577574174740/channels4_banner.jpg?ex=6a8c1edb&is=6a8acd5b&hm=6c614472d8507c18d3d4ff5527c2ee2829ce3c70630558cc37bf22376489d840&"
            },
            {
                "name": "Wargamer", 
                "url": "https://www.wargamer.com/warhammer-40k/feed",
                "footer_icon": "https://cdn.discordapp.com/attachments/1523030976782143645/1542484519192625242/Wargamer_logo.jpg?ex=6a916627&is=6a9014a7&hm=639efbc0381ad4c6da379645deb4e365bac0586056d386c4bee3a60b96f64d41&",
                "thumbnail": "https://cdn.discordapp.com/attachments/1523030976782143645/1542466665361707098/Warhammer-logo.png?ex=6a915586&is=6a900406&hm=8620ff726f1c14357e52c51d5d897b8349080539c0a36e414e2d68870464140b&"
            }
        ]
        
        # --- ΛΙΣΤΑ ΕΓΚΡΙΣΗΣ ---
        self.valid_keywords = [
            "40k", "warhammer 40k", "warhammer 40000", "warhammer 40,000",
            "aos", "age of sigmar", "kill team", "warhammer", "old world", "horus heresy",
            "competitive intel", "competitive innovations", "hammer of math", 
            "ruleshammer", "how to paint everything", "detachment focus",
            "black library", "that 6+++ show", "lunchtime show",
            "11th edition", "11th ed", "in 11th", "launch tier list",
            "space marines", "genestealer cults", "ork", "orks", "chaos", 
            "tyranids", "necron", "necrons", "tau empire", "aeldari", 
            "drukhari", "adeptus mechanicus", "imperium", "blood axes", "goffs"
        ]

        # --- ΜΑΥΡΗ ΛΙΣΤΑ ---
        self.blocked_keywords = [
            "marvel", "crisis protocol", "mcp", "shatterpoint", "star wars", 
            "armada", "x-wing", "d&d", "dungeons and dragons", 
            "mtg", "magic the gathering", "lorcana"
        ]
        
    async def cog_load(self):
        self.check_news.start()

    def cog_unload(self):
        self.check_news.cancel()

    @tasks.loop(minutes=60)
    async def check_news(self):
        print("\n--- 📡 ΞΕΚΙΝΑΕΙ ΣΑΡΩΣΗ ΑΡΘΡΩΝ ---")
        
        for source in self.news_sources:
            try:
                print(f"🔄 Ανάγνωση πηγής: {source['name']}")
                
                # Cache busting logic
                if "?" in source['url']:
                    busted_url = f"{source['url']}&nocache={int(time.time())}"
                else:
                    busted_url = f"{source['url']}?nocache={int(time.time())}"
                    
                feed = await asyncio.to_thread(feedparser.parse, busted_url, agent=self.browser_agent)
                print(f"   ┣ HTTP Status: {getattr(feed, 'status', 'Άγνωστο')}")
                
                if not feed.entries:
                    print(f"⚠️ Δεν βρέθηκαν άρθρα στο feed: {source['name']}")
                    continue

                recent_entries = reversed(feed.entries[:15])
                
                for entry in recent_entries:
                    title = entry.title
                    title_lower = title.lower()
                    current_link = entry.link
                    
                    summary_lower = ""
                    if hasattr(entry, 'summary'):
                        summary_lower = entry.summary.lower()
                    elif hasattr(entry, 'description'):
                        summary_lower = entry.description.lower()
                        
                    print(f"🔎 Ελέγχω: '{title}'")
                        
                    # 1. ΕΛΕΓΧΟΣ ΜΑΥΡΗΣ ΛΙΣΤΑΣ (ΜΟΝΟ ΣΤΟΝ ΤΙΤΛΟ)
                    is_blocked = any(b_kw in title_lower for b_kw in self.blocked_keywords)
                    if is_blocked:
                        print("   ┗ 🚫 Απορρίφθηκε (Μαύρη Λίστα)")
                        continue
                        
                    # 2. ΕΛΕΓΧΟΣ ΛΕΞΕΩΝ-ΚΛΕΙΔΙΩΝ
                    is_relevant = any(kw in title_lower or kw in summary_lower for kw in self.valid_keywords)
                    if not is_relevant:
                        print("   ┗ ❌ Απορρίφθηκε (Χωρίς keywords 40k)")
                        continue 
                        
                    # 3. ΕΛΕΓΧΟΣ ΒΑΣΗΣ ΔΕΔΟΜΕΝΩΝ
                    article_exists = news_col.find_one({"_id": current_link})
                    if article_exists:
                        print("   ┗ ⏭️ Προσπεράστηκε (Υπάρχει ήδη)")
                        continue 
                        
                    # --- ΝΕΟ ΑΡΘΡΟ ΒΡΕΘΗΚΕ! ---
                    print("   ┗ ✅ ΕΓΚΡΙΘΗΚΕ! Αποθήκευση και αποστολή...")
                    news_col.insert_one({"_id": current_link, "title": title, "source": source['name']})
                    
                    channel = self.bot.get_channel(self.news_channel_id)
                    if channel:
                        embed = discord.Embed(
                            title=f"📜 {title}",
                            url=current_link,
                            color=discord.Color.from_rgb(255, 255, 255),
                            description="Νέο περιεχόμενο δημοσιεύτηκε!\nΠατήστε τον τίτλο για να το δείτε."
                        )
                        
                        # --- YOUTUBE DYNAMIC THUMBNAILS ---
                        if hasattr(entry, 'yt_videoid') or "youtube.com/watch?v=" in current_link:
                            if hasattr(entry, 'yt_videoid'):
                                video_id = entry.yt_videoid
                            else:
                                video_id = current_link.split("v=")[1].split("&")[0]
                                
                            yt_thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                            embed.set_image(url=yt_thumbnail) 
                            embed.set_thumbnail(url=source["thumbnail"]) 
                        else:
                            embed.set_thumbnail(url=source["thumbnail"])
                            
                        embed.set_footer(text=f"{source['name']} Updates", icon_url=source["footer_icon"])
                        
                        await channel.send(
                            content="<:Warhammer_1:1416864475520438302> **Incoming Transmission!**", 
                            embed=embed
                        )
                        await asyncio.sleep(2)
                        
            except Exception as e:
                print(f"❌ [News Radar] Σφάλμα κατά τον έλεγχο της πηγής {source['name']}: {e}")

    @check_news.before_loop
    async def before_check_news(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(NewsFeed(bot))