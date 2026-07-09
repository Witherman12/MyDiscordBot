"""
========================================
ΑΡΧΕΙΟ: witherbot.py (Main)
ΠΕΡΙΓΡΑΦΗ: Το κεντρικό αρχείο του bot. Διαχειρίζεται τη σύνδεση με το Discord, 
           τη ΒΔ (MongoDB), τα events μηνυμάτων και τα στατιστικά.
           
ΠΕΡΙΕΧΟΜΕΝΑ / ΕΝΤΟΛΕΣ:
 - on_message : Ακούει για auto-replies (glorious phrase, tags, Waaagh, Nurgle, Mods, Heresy, Charge, Femboy, Sun).
 - !glorious  : Δείχνει πόσες φορές έχει ειπωθεί η μυστική φράση.
 - !report    : Καταγράφει το αποτέλεσμα μιας μάχης στη βάση (Νίκη/Ήττα ή Ισοπαλία).
 - !stats     : Εμφανίζει το Win Rate και το ιστορικό ενός Faction.
 - !top       : Εμφανίζει το Leaderboard με τα 5 καλύτερα Factions.
========================================
"""

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

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Φόρτωση των εξωτερικών αρχείων (Cogs)
@bot.event
async def setup_hook():
    await bot.load_extension("cogs.fun")
    print("✅ Το αρχείο Fun φορτώθηκε με επιτυχία!")
    
    await bot.load_extension("cogs.news")
    print("✅ Το αρχείο News (RSS) φορτώθηκε με επιτυχία!")

glorious_count = 0


# ==========================================
# 3. ΣΥΝΔΕΣΗ ΜΕ ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ (MONGODB)
# ==========================================
print("Σύνδεση με τη βάση δεδομένων...")
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
    print(f'Logged in as {bot.user.name}')
    
    guild = bot.get_guild(TARGET_GUILD_ID)
    if guild is None:
        print("ΣΦΑΛΜΑ: Δεν βρήκα τον Server! Έλεγξε το TARGET_GUILD_ID.")
        return

    saved_count = load_count()
    
    if saved_count is not None:
        glorious_count = saved_count
        print(f"Το σκορ βρέθηκε στο MongoDB! Ο μετρητής φορτώθηκε: {glorious_count}")
    else:
        print("Δεν βρέθηκε σκορ στη βάση. Ρύθμιση αρχικού σκορ σε 19...")
        glorious_count = 19
        save_count(glorious_count)
        print("Το 19 αποθηκεύτηκε στο MongoDB με επιτυχία!")

@bot.event
async def on_message(message):
    global glorious_count
    
    # [Ασπίδα] Αγνοούμε τα μηνύματα του ίδιου του bot για να αποφύγουμε λούπες (spam)!
    if message.author == bot.user:
        return

    # Αγνοούμε μηνύματα από άλλα bots ή από λάθος server
    if message.author.bot or message.guild.id != TARGET_GUILD_ID:
        return

    # Ορίζουμε το μήνυμα σε πεζά μια φορά στην αρχή για να το χρησιμοποιούν όλοι οι έλεγχοι
    msg_lower = message.content.lower()

    # [Α] - Έλεγχος για την φράση
    if message.author.id == TARGET_USER_ID and TARGET_PHRASE.lower().strip() in msg_lower:
        glorious_count += 1
        save_count(glorious_count)
        print(f"Το είπε ξανά! Νέο σύνολο: {glorious_count} (Σώθηκε στο MongoDB)")

    # [Β] - Έλεγχος για Tag και Χαιρετισμό
    if bot.user in message.mentions:
        greetings = ["hi", "hello", "γεια", "γειά", "hello there"]
        if any(word in msg_lower for word in greetings):
            await message.channel.send("Imperial greetings! The Emperor protects.") 
            
    # [Γ] - Έλεγχος για το WAAAGH (Δυναμικό μέγεθος)
    if re.search(r'wa+gh', msg_lower):
        # Δημιουργεί τυχαίο αριθμό από Α (από 7 έως 21)
        a_count = random.randint(7, 21)
        waaagh_text = f"# W{'A' * a_count}GH! <:Waaagh:1432414641123885257>"
        await message.channel.send(waaagh_text) 
        
    # [Δ] - Έλεγχος για τον Nurgle (Reaction με σαπούνι)
    if "nurgle" in msg_lower:
        try:
            await message.add_reaction("🧼")
        except discord.errors.Forbidden:
            print("Δεν έχω άδεια για να βάλω reaction (add_reactions permission).")
        except discord.errors.NotFound:
            print("Δεν βρέθηκε το emoji.")
            
    # [Ε] - Έλεγχος για Mod/Mods
    if re.search(r'\b(mod|mods)\b', msg_lower):
        MOD_ROLE_ID = 802082482320703489  
        await message.reply(f"🚨 <@&{MOD_ROLE_ID}>!")

    # [Ζ] - Έλεγχος για Heresy (Reaction με μάτι)
    if re.search(r'\b(heresy|heretic|heretics)\b', msg_lower):
        try:
            await message.add_reaction("👁️")
        except:
            pass

    # [Η] - Charge (50% GIF, 50% Emoji)
    if re.search(r'\b(charge|charges|charged)\b', msg_lower):
        if random.randint(1, 2) == 1:
            await message.reply("https://tenor.com/view/orc-boyz-total-war-warhammer-greenskins-charge-warhammer-total-war-gif-19312099")
        else:
            try:
                await message.add_reaction("🏇")
            except:
                pass

    # [Θ] - Femboy
    if re.search(r'\b(femboy|femboys)\b', msg_lower):
        try:
            # Emoji React πάντα
            await message.add_reaction("<:scream:829005859727212547>")
            
            # 50% πιθανότητα (1 στις 2) να απαντήσει με GIF
            if random.randint(1, 2) == 1:
                await message.reply("https://tenor.com/view/the-office-no-angry-steve-carell-michael-scott-gif-5606969")
        except:
            pass
            
    # [Ι] - Cruel Sun (Escanor)
    if re.search(r'\bcruel sun\b', msg_lower):
        await message.reply("https://klipy.com/gifs/seven-deadly-sins-escanor")
            
    # Απαραίτητο για να συνεχίσουν να δουλεύουν οι !εντολές
    await bot.process_commands(message)
 
 
# ==========================================
# 5. ΕΝΤΟΛΕΣ ΒΑΣΗΣ ΔΕΔΟΜΕΝΩΝ (COMMANDS)
# ==========================================

# --- ΕΝΤΟΛΗ: glorious ---
@bot.command()
async def glorious(ctx):
    await ctx.send(f"Ο <@{TARGET_USER_ID}> έχει πει τη φράση '{TARGET_PHRASE}' {glorious_count} φορές! <:Custode:1439332561468920132>")

# --- ΕΝΤΟΛΗ: report ---
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

# --- ΕΝΤΟΛΗ: stats ---
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
    
# --- ΕΝΤΟΛΗ: top ---
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


# Εκκίνηση του Bot
bot.run(TOKEN)