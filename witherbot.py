import discord
from discord.ext import commands
import pymongo
import certifi
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import re
import random

# ==========================================
# 1. ΨΕΥΤΙΚΟΣ ΔΙΑΚΟΜΙΣΤΗΣ (KEEP-ALIVE RENDER)
# ==========================================
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")
        
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# ==========================================
# 2. ΡΥΘΜΙΣΕΙΣ & ΠΑΡΑΜΕΤΡΟΙ DISCORD
# ==========================================
TOKEN = os.environ.get("DISCORD_TOKEN")
MONGO_URI = os.environ.get("MONGODB_URI")
TARGET_USER_ID = 994930770542084227
TARGET_GUILD_ID = 801753238662676500
TARGET_PHRASE = "glorious melee combat"

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

# --- Ο ΕΠΙΣΗΜΟΣ ΤΡΟΠΟΣ ΦΟΡΤΩΣΗΣ (Discord.py v2.0+) ---
class WitherBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self):
        print("⏳ Ξεκινάει η φόρτωση των Cogs...", flush=True)
        try:
            await self.load_extension("cogs.fun")
            print("✅ Το cogs.fun φορτώθηκε!", flush=True)
        except Exception as e:
            print(f"❌ Σφάλμα στο fun: {e}", flush=True)
            
        try:
            await self.load_extension("cogs.news")
            print("✅ Το cogs.news φορτώθηκε!", flush=True)
        except Exception as e:
            print(f"❌ Σφάλμα στο news: {e}", flush=True)

bot = WitherBot()

# ==========================================
# 3. ΣΥΝΔΕΣΗ ΜΕ ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ (MONGODB)
# ==========================================
print("Σύνδεση με τη βάση δεδομένων...", flush=True)
client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True)
db = client["GloriousDatabase"]
collection = db["Counters"]
factions_col = db["Factions"]

def save_count(count):
    collection.update_one({"_id": "glorious_score"}, {"$set": {"count": count}}, upsert=True)

def load_count():
    doc = collection.find_one({"_id": "glorious_score"})
    if doc:
        return doc.get("count", 0)
    return None

# ==========================================
# 4. EVENTS (ON READY & ON MESSAGE)
# ==========================================
@bot.event
async def on_ready():
    global glorious_count
    print(f'Logged in as {bot.user.name}', flush=True)
    
    guild = bot.get_guild(TARGET_GUILD_ID)
    if guild is None:
        print("ΣΦΑΛΜΑ: Δεν βρήκα τον Server! Έλεγξε το TARGET_GUILD_ID.", flush=True)
        return

    saved_count = load_count()
    
    if saved_count is not None:
        glorious_count = saved_count
        print(f"Το σκορ βρέθηκε στο MongoDB! Ο μετρητής φορτώθηκε: {glorious_count}", flush=True)
    else:
        print("Δεν βρέθηκε σκορ στη βάση. Ρύθμιση αρχικού σκορ σε 19...", flush=True)
        glorious_count = 19
        save_count(glorious_count)

@bot.event
async def on_message(message):
    global glorious_count
    
    if message.author == bot.user:
        return

    if message.author.bot or message.guild.id != TARGET_GUILD_ID:
        return

    msg_lower = message.content.lower()

    if message.author.id == TARGET_USER_ID and TARGET_PHRASE.lower().strip() in msg_lower:
        glorious_count += 1
        save_count(glorious_count)
        print(f"Το είπε ξανά! Νέο σύνολο: {glorious_count} (Σώθηκε στο MongoDB)", flush=True)

    if bot.user in message.mentions:
        greetings = ["hi", "hello", "γεια", "γειά", "hello there"]
        if any(word in msg_lower for word in greetings):
            await message.channel.send("Imperial greetings! The Emperor protects.") 
            
    if re.search(r'wa+gh', msg_lower):
        a_count = random.randint(7, 21)
        waaagh_text = f"# W{'A' * a_count}GH! <:Waaagh:1432414641123885257>"
        await message.channel.send(waaagh_text) 
        
    if "nurgle" in msg_lower:
        try:
            await message.add_reaction("🧼")
        except:
            pass
            
    if re.search(r'\b(mod|mods)\b', msg_lower):
        MOD_ROLE_ID = 802082482320703489  
        await message.reply(f"🚨 <@&{MOD_ROLE_ID}>!")

    if re.search(r'\b(heresy|heretic|heretics)\b', msg_lower):
        try:
            await message.add_reaction("👁️")
        except:
            pass

    if re.search(r'\b(charge|charges|charged)\b', msg_lower):
        if random.randint(1, 2) == 1:
            await message.reply("https://tenor.com/view/orc-boyz-total-war-warhammer-greenskins-charge-warhammer-total-war-gif-19312099")
        else:
            try:
                await message.add_reaction("🏇")
            except:
                pass

    if re.search(r'\b(femboy|femboys)\b', msg_lower):
        try:
            await message.add_reaction("<:scream:829005859727212547>")
            if random.randint(1, 2) == 1:
                await message.reply("https://tenor.com/view/the-office-no-angry-steve-carell-michael-scott-gif-5606969")
        except:
            pass
            
    if re.search(r'\bcruel sun\b', msg_lower):
        await message.reply("https://klipy.com/gifs/seven-deadly-sins-escanor")
            
    await bot.process_commands(message)
 
# ==========================================
# 5. ΕΝΤΟΛΕΣ ΒΑΣΗΣ ΔΕΔΟΜΕΝΩΝ (COMMANDS)
# ==========================================
@bot.command(name="counter")
async def show_counter(ctx):
    await ctx.send(f"Ο <@{TARGET_USER_ID}> έχει πει τη φράση '{TARGET_PHRASE}' {glorious_count} φορές! <:Custode:1439332561468920132>")

@bot.command(name="report")
async def report_match(ctx, *, match_data: str):
    is_tie = False
    if match_data.lower().startswith("tie "):
        is_tie = True
        match_data = match_data[4:]

    if " vs " not in match_data.lower():
        await ctx.send("❌ Λάθος μορφή! Χρησιμοποίησε: `!report FactionA vs FactionB` ή `!report tie FactionA vs FactionB`")
        return

    parts = re.split(r'\s+vs\s+', match_data, flags=re.IGNORECASE)
    if len(parts) != 2:
        await ctx.send("❌ Λάθος μορφή! Παρακαλώ γράψε μόνο δύο Factions.")
        return

    faction1 = parts[0].strip()
    if not faction1.startswith("<"): faction1 = faction1.title()

    faction2 = parts[1].strip()
    if not faction2.startswith("<"): faction2 = faction2.title()

    if is_tie:
        factions_col.update_one({"name": faction1}, {"$inc": {"ties": 1, "wins": 0, "losses": 0}}, upsert=True)
        factions_col.update_one({"name": faction2}, {"$inc": {"ties": 1, "wins": 0, "losses": 0}}, upsert=True)
        await ctx.send(f"⚔️ Καταγράφηκε Ισοπαλία ανάμεσα σε **{faction1}** και **{faction2}**!")
    else:
        factions_col.update_one({"name": faction1}, {"$inc": {"wins": 1, "losses": 0, "ties": 0}}, upsert=True)
        factions_col.update_one({"name": faction2}, {"$inc": {"losses": 1, "wins": 0, "ties": 0}}, upsert=True)
        await ctx.send(f"🏆 Καταγράφηκε Νίκη για τους **{faction1}** εναντίον των **{faction2}**!")

@bot.command(name="stats")
async def faction_stats(ctx, *, faction_name: str):
    faction_name = faction_name.strip()
    if not faction_name.startswith("<"): faction_name = faction_name.title()
    
    data = factions_col.find_one({"name": faction_name})
    if not data:
        await ctx.send(f"⚠️ Δεν βρέθηκαν στατιστικά για το Faction: **{faction_name}**.")
        return

    wins = data.get("wins", 0)
    losses = data.get("losses", 0)
    ties = data.get("ties", 0)
    total_games = wins + losses + ties

    win_rate = 0 if total_games == 0 else (wins / total_games) * 100

    await ctx.send(
        f"📊 **Στατιστικά: {faction_name}**\n"
        f"Win Rate: **{win_rate:.1f}%**\n"
        f"Wins: **{wins}** | Losses: **{losses}** | Ties: **{ties}**"
    )
    
@bot.command(name="top")
async def top_factions(ctx):
    if factions_col.count_documents({}) == 0:
        await ctx.send("⚠️ Δεν υπάρχουν ακόμα καταγεγραμμένοι αγώνες στην ΒΔ!")
        return

    top_data = factions_col.find().sort("wins", -1).limit(5)
    message = "🏆 **Top 5 Factions (Με βάση τις Νίκες)** 🏆\n\n"
    
    for index, data in enumerate(top_data, 1):
        name = data.get("name", "Άγνωστο")
        wins = data.get("wins", 0)
        losses = data.get("losses", 0)
        ties = data.get("ties", 0)
        
        total_games = wins + losses + ties
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        
        message += f"**{index}.** {name} - Wins: **{wins}** | WR: **{win_rate:.1f}%**\n"

    await ctx.send(message)

bot.run(TOKEN)