import discord
from discord.ext import commands, tasks
import feedparser
import asyncio
import pymongo
import certifi
import os
import time
import aiohttp
from bs4 import BeautifulSoup

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
        # Προστέθηκε το πεδίο "type" για να ξεχωρίζει τα RSS από το Web Scraping
        self.news_sources = [
            {
                "name": "Tabletop Battles",
                "type": "rss",
                "url": "https://www.tabletopbattles.com/feed/",
                "footer_icon": "https://cdn.discordapp.com/attachments/1523030976782143645/1542469989955801139/goonhammer.png?ex=6a91589f&is=6a90071f&hm=33eaa3c1ba01686404b0da4d7049112a8ba334c579028bb68ce4221b27a3812b&",
                "thumbnail": "https://cdn.discordapp.com/attachments/850011185314267177/1523030976622493716/ttb_logo_text_white.png?ex=6a8be2e1&is=6a8a9161&hm=ae5b615894c7933e70d45aec0efee1aaa087dc59d0fbfcf40cbe10fa0fffebef&"
            },
            {
                "name": "Auspex Tactics", 
                "type": "rss",
                "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC6Gco9PWxmJmJ5CqfbChuiQ",
                "footer_icon": "https://cdn.discordapp.com/attachments/1523030976782143645/1541033367854780547/vecteezy_youtube-logo-png-youtube-logo-transparent-png-youtube-icon_23986704.png?ex=6a8c1ea9&is=6a8acd29&hm=e6a39cc27508389afbbdea1c5ce244bb4381f540d3f7bbfc6c3cb5b4b3417078&",
                "thumbnail": "https://cdn.discordapp.com/attachments/1523030976782143645/1541033577574174740/channels4_banner.jpg?ex=6a8c1edb&is=6a8acd5b&hm=6c614472d8507c18d3d4ff5527c2ee2829ce3c70630558cc37bf22376489d840&"
            },
            {
                "name": "Warhammer Community", 
                "type": "warcom",
                "url": "https://www.warhammer-community.com/en-gb/all-news-and-features/news/",
                "footer_icon": "https://cdn.discordapp.com/attachments/1523030976782143645/1541029988965289994/Warhammer_1.PNG?ex=6a90b8c4&is=6a8f6744&hm=c107b83a21a15af4e4c79c35917a2cfe7cc53f9751bfa56c7029516c23e45f48&",
                "thumbnail": "https://cdn.discordapp.com/attachments/1523030976782143645/1542466665361707098/Warhammer-logo.png?ex=6a915586&is=6a900406&hm=8620ff726f1c14357e52c51d5d897b8349080539c0a36e414e2d68870464140b&"
            }
        ]
        
        # --- ΛΙΣΤΑ ΕΓΚΡΙΣΗΣ (Πρέπει να έχει τουλάχιστον ένα από αυτά) ---
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

        # --- ΜΑΥΡΗ ΛΙΣΤΑ (Αν βρει αυτά, το άρθρο απορρίπτεται ΑΚΑΡΙΑΙΑ) ---
        self.blocked_keywords = [
            "marvel", "crisis protocol", "mcp", "shatterpoint", "star wars", 
            "armada", "x-wing", "d&d", "dungeons and dragons", 
            "mtg", "magic the gathering", "lorcana"
        ]
        
    async def cog_load(self):
        self.check_news.start()

    def cog_unload(self):
        self.check_news.cancel()

    @tasks.loop(minutes=90)
    async def check_news(self):
        print("\n--- 📡 ΞΕΚΙΝΑΕΙ ΣΑΡΩΣΗ ΑΡΘΡΩΝ ---")
        
        for source in self.news_sources:
            try:
                print(f"🔄 Ανάγνωση πηγής: {source['name']}")
                parsed_entries = [] # Εδώ θα μαζεύουμε τα άρθρα ανεξάρτητα από τον τρόπο που τα διαβάσαμε
                
                # ==========================================
                # 1. ΑΝΑΓΝΩΣΗ ΜΕΣΩ RSS FEED (Goonhammer, YT)
                # ==========================================
                if source.get("type", "rss") == "rss":
                    if "?" in source['url']:
                        busted_url = f"{source['url']}&nocache={int(time.time())}"
                    else:
                        busted_url = f"{source['url']}?nocache={int(time.time())}"
                        
                    feed = await asyncio.to_thread(feedparser.parse, busted_url, agent=self.browser_agent)
                    print(f"   ┣ HTTP Status: {getattr(feed, 'status', 'Άγνωστο')}")
                    
                    if not feed.entries:
                        print(f"⚠️ Δεν βρέθηκαν άρθρα στο feed: {source['name']}")
                        continue

                    # Μετατρέπουμε τα RSS entries σε ενιαία μορφή
                    for entry in feed.entries[:15]:
                        summary = getattr(entry, 'summary', getattr(entry, 'description', ""))
                        video_id = None
                        if hasattr(entry, 'yt_videoid'):
                            video_id = entry.yt_videoid
                        elif "youtube.com/watch?v=" in entry.link:
                            video_id = entry.link.split("v=")[1].split("&")[0]

                        parsed_entries.append({
                            "title": entry.title,
                            "link": entry.link,
                            "summary": summary,
                            "video_id": video_id,
                            "image_url": None
                        })
                
                # ==========================================
                # 2. ΑΝΑΓΝΩΣΗ ΜΕΣΩ WEB SCRAPING (Warhammer Com)
                # ==========================================
                elif source.get("type") == "warcom":
                    async with aiohttp.ClientSession() as session:
                        async with session.get(source['url'], headers={"User-Agent": self.browser_agent}) as response:
                            print(f"   ┣ HTTP Status (WarCom): {response.status}")
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                found_links = set()
                                
                                # Όπως είδαμε στο HTML, τα άρθρα είναι όλα κλεισμένα σε <article> tags!
                                articles = soup.find_all('article')
                                
                                for article in articles:
                                    # Το link είναι μέσα στο article
                                    a_tag = article.find('a', href=True)
                                    if not a_tag:
                                        continue
                                        
                                    href = a_tag['href']
                                    
                                    # Σιγουρευόμαστε ότι είναι άρθρο
                                    if '/articles/' not in href and '/news/' not in href:
                                        continue
                                        
                                    if href.startswith('/'):
                                        href = "https://www.warhammer-community.com" + href
                                        
                                    if href in found_links:
                                        continue
                                        
                                    # Ο τίτλος κρύβεται στο 'title' attribute, αλλιώς παίρνουμε το κείμενο
                                    title = a_tag.get('title')
                                    if not title:
                                        title = a_tag.text.strip()
                                        
                                    if not title or len(title) < 5:
                                        continue
                                        
                                    # Βρίσκουμε την εικόνα του άρθρου
                                    img_tag = article.find('img')
                                    img_url = img_tag.get('src') if img_tag else None
                                    
                                    parsed_entries.append({
                                        "title": title,
                                        "link": href,
                                        "summary": "",
                                        "video_id": None,
                                        "image_url": img_url
                                    })
                                    found_links.add(href)
                                    
                                    if len(parsed_entries) >= 15:
                                        break
                            else:
                                print(f"⚠️ Αποτυχία σύνδεσης στο WarCom (Status {response.status})")
                                continue

                # ==========================================
                # ΦΙΛΤΡΑΡΙΣΜΑ & ΑΠΟΣΤΟΛΗ ΣΤΟ DISCORD
                # ==========================================
                if not parsed_entries:
                    continue

                recent_entries = reversed(parsed_entries)
                
                for entry in recent_entries:
                    title = entry['title']
                    title_lower = title.lower()
                    current_link = entry['link']
                    summary_lower = entry['summary'].lower()
                    
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
                        
                    # --- ΝΕΟ ΑΡΘΡΟ/ΒΙΝΤΕΟ ΒΡΕΘΗΚΕ ---
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
                        
                        # Ρύθμιση Εικόνας (YouTube, WarCom ή κλασικό Thumbnail)
                        if entry['video_id']:
                            yt_thumbnail = f"https://img.youtube.com/vi/{entry['video_id']}/hqdefault.jpg"
                            embed.set_image(url=yt_thumbnail)
                            embed.set_thumbnail(url=source["thumbnail"])
                        elif entry['image_url']:
                            embed.set_image(url=entry['image_url']) # Η εικόνα του WarCom!
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