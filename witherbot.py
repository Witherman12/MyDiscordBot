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
TARGET_GUILD_ID = 801753238662676500  # Βάλε εδώ το ID του Server σου (χωρίς εισαγωγικά)
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
        
        # Το any() ελέγχει αν ΟΠΟΙΑΔΗΠΟΤΕ από τις λέξεις της λίστας υπάρχει στο μήνυμα
        if any(word in msg_lower for word in greetings):
            await message.channel.send("Imperial greetings! The Emperor protects.") 
            # (Μπορείς να αλλάξεις το μήνυμα ανάμεσα στα αυτάκια σε ό,τι θέλεις!)
            
    # --- 3. Έλεγχος για το WAAAGH ---
    # Το μοτίβο r'wa+gh' σημαίνει: 'w', ακολουθούμενο από ένα ή περισσότερα 'a', και τέλος 'gh'.
    if re.search(r'wa+gh', message.content.lower()):
        await message.channel.send("# WAAAAAAGH! <:Waaagh:1432414641123885257>") 
        # Μπορείς να αλλάξεις το τι θα απαντάει (και τα emojis) σε ό,τι θέλεις!
        
    # --- 4. Έλεγχος για τον Nurgle (Reaction με σαπούνι) ---
    if "nurgle" in message.content.lower():
        try:
            # Το "🧼" είναι το default Unicode emoji για το σαπούνι. 
            await message.add_reaction("🧼")
        except discord.errors.Forbidden:
            # Αυτό τυπώνεται στα logs του Render αν το bot δεν έχει δικαίωμα να κάνει reacts
            print("Δεν έχω άδεια για να βάλω reaction (add_reactions permission).")
        except discord.errors.NotFound:
            print("Δεν βρέθηκε το emoji (απίθανο για τα βασικά unicode).")

    # Απαραίτητο για να συνεχίσουν να δουλεύουν οι εντολές (όπως το !glorious)
    await bot.process_commands(message)
    
@bot.command()
async def glorious(ctx):
    await ctx.send(f"Ο <@{TARGET_USER_ID}> έχει πει τη φράση '{TARGET_PHRASE}' {glorious_count} φορές! <:Custode:1439332561468920132>")

bot.run(TOKEN)