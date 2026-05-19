import discord
from discord.ext import commands
import pymongo
import certifi

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

import re

# --- 1. ΨΕΥΤΙΚΟΣ ΔΙΑΚΟΜΙΣΤΗΣ (ΓΙΑ ΝΑ ΜΕΙΝΕΙ ΞΥΠΝΙΟ ΤΟ RENDER) ---
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
# ----------------------------------------------------------------

# --- ΡΥΘΜΙΣΕΙΣ ---
TOKEN = os.environ.get("DISCORD_TOKEN")
MONGO_URI = os.environ.get("MONGODB_URI")
# TOKEN = 'ΧΧΧ'
# MONGO_URI = 'ΧΧΧ'
TARGET_USER_ID = 994930770542084227
TARGET_GUILD_ID = 801753238662676500
TARGET_PHRASE = "glorious melee combat"

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)
glorious_count = 0

# --- 3. ΣΥΝΔΕΣΗ ΜΕ ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ ---
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
    
    # Αν το μήνυμα είναι από το ίδιο το bot ή από λάθος server, το αγνοούμε
    if message.author.bot or message.guild.id != TARGET_GUILD_ID:
        return

    # --- 1. Έλεγχος για το "glorious melee combat" ---
    if message.author.id == TARGET_USER_ID and TARGET_PHRASE.lower().strip() in message.content.lower():
        glorious_count += 1
        save_count(glorious_count)
        print(f"Το είπε ξανά! Νέο σύνολο: {glorious_count} (Σώθηκε στο MongoDB)")

    # --- 2. Έλεγχος για Tag και Χαιρετισμό ---
    # Ελέγχουμε αν το bot έγινε Mention (tag)
    if bot.user in message.mentions:
        # Φτιάχνουμε μια λίστα με λέξεις-κλειδιά
        greetings = ["hi", "hello", "γεια", "γειά", "hello there"]
        # Ελέγχουμε αν το μήνυμα (σε πεζά) περιέχει κάποιον χαιρετισμό
        msg_lower = message.content.lower()
        
        # Το any() ελέγχει αν οποιαδήποτε από τις λέξεις της λίστας υπάρχει στο μήνυμα
        if any(word in msg_lower for word in greetings):
            await message.channel.send("Imperial greetings! The Emperor protects.") 
            
    # --- 3. Έλεγχος για το WAAAGH ---
    # Το μοτίβο r'wa+gh' σημαίνει: 'w', ακολουθούμενο από ένα ή περισσότερα 'a', και τέλος 'gh'.
    if re.search(r'wa+gh', message.content.lower()):
        await message.channel.send("# WAAAAAAGH! <:Waaagh:1432414641123885257>") 
        
    # --- 4. Έλεγχος για τον Nurgle (Reaction με σαπούνι) ---
    if "nurgle" in message.content.lower():
        try:
            await message.add_reaction("🧼")
        except discord.errors.Forbidden:
            # Αυτό τυπώνεται στα logs του Render αν το bot δεν έχει δικαίωμα να κάνει reacts
            print("Δεν έχω άδεια για να βάλω reaction (add_reactions permission).")
        except discord.errors.NotFound:
            print("Δεν βρέθηκε το emoji (απίθανο για τα βασικά unicode).")

    # Απαραίτητο για να συνεχίσουν να δουλεύουν οι εντολές
    await bot.process_commands(message)
   
# --- ΕΝΤΟΛΗ report - ΚΑΤΑΓΡΑΦΗ ΑΠΟΤΕΛΕΣΜΑΤΟΣ ---
@bot.command(name="report")
async def report_match(ctx, *, match_data: str):
    # Ελέγχουμε αν είναι ισοπαλία
    is_tie = False
    if match_data.lower().startswith("tie "):
        is_tie = True
        match_data = match_data[4:] # Κόβουμε τη λέξη "tie " από την αρχή

    # Ελέγχουμε αν υπάρχει το "vs"
    if " vs " not in match_data.lower():
        await ctx.send("❌ Λάθος μορφή! Χρησιμοποίησε: `!report FactionA vs FactionB` ή `!report tie FactionA vs FactionB`")
        return

    # Χωρίζουμε τα factions με βάση το "vs" (αγνοώντας κεφαλαία/πεζά)
    parts = re.split(r'\s+vs\s+', match_data, flags=re.IGNORECASE)
    if len(parts) != 2:
        await ctx.send("❌ Λάθος μορφή! Παρακαλώ γράψε μόνο δύο Factions.")
        return

    # 
    faction1 = parts[0].strip()
    if not faction1.startswith("<"): faction1 = faction1.title()

    faction2 = parts[1].strip()
    if not faction2.startswith("<"): faction2 = faction2.title()

    if is_tie:
        # Ενημερώνουμε και τα δύο ως ισοπαλία (Αν δεν υπάρχουν στη βάση, τα δημιουργεί αυτόματα)
        factions_col.update_one({"name": faction1}, {"$inc": {"ties": 1, "wins": 0, "losses": 0}}, upsert=True)
        factions_col.update_one({"name": faction2}, {"$inc": {"ties": 1, "wins": 0, "losses": 0}}, upsert=True)
        await ctx.send(f"⚔️ Καταγράφηκε Ισοπαλία ανάμεσα σε **{faction1}** και **{faction2}**!")
    else:
        # Το faction1 είναι ο νικητής, το faction2 ο ηττημένος
        factions_col.update_one({"name": faction1}, {"$inc": {"wins": 1, "losses": 0, "ties": 0}}, upsert=True)
        factions_col.update_one({"name": faction2}, {"$inc": {"losses": 1, "wins": 0, "ties": 0}}, upsert=True)
        await ctx.send(f"🏆 Καταγράφηκε Νίκη για τους **{faction1}** εναντίον των **{faction2}**!")

# --- ΕΝΤΟΛΗ stats - ΕΜΦΑΝΙΣΗ ΣΤΑΤΙΣΤΙΚΩΝ ---
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

    if total_games == 0:
        win_rate = 0
    else:
        win_rate = (wins / total_games) * 100

    # Φτιάχνουμε το τελικό μήνυμα
    await ctx.send(
        f"📊 **Στατιστικά: {faction_name}**\n"
        f"Win Rate: **{win_rate:.1f}%**\n"
        f"Wins: **{wins}** | Losses: **{losses}** | Ties: **{ties}**"
    )
    
@bot.command()
async def glorious(ctx):
    await ctx.send(f"Ο <@{TARGET_USER_ID}> έχει πει τη φράση '{TARGET_PHRASE}' {glorious_count} φορές! <:Custode:1439332561468920132>")

bot.run(TOKEN)