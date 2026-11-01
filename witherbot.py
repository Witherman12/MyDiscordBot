import discord
from discord.ext import commands
import pymongo
import certifi
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import re
import random
import secrets

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
TARGET_PHRASE = "glorious melee"

# ID του συγκεκριμένου χρήστη για το 5% emoji reaction
SPECIFIC_USER_ID = 469508503266918400

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

# --- Ο ΕΠΙΣΗΜΟΣ ΤΡΟΠΟΣ ΦΟΡΤΩΣΗΣ (Discord.py v2.0+) ---
class WitherBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self):
        print("⏳ Ξεκινάει η φόρτωση των Cogs...", flush=True)
        try:
            await self.load_extension("cogs.fun")
            print("✅ [1] Το cogs.fun φορτώθηκε!", flush=True)
        except Exception as e:
            print(f"❌ Σφάλμα στο fun: {e}", flush=True)
            
        try:
            await self.load_extension("cogs.news")
            print("✅ [2] Το cogs.news φορτώθηκε!", flush=True)
        except Exception as e:
            print(f"❌ Σφάλμα στο news: {e}", flush=True)
            
        try:
            await self.load_extension("cogs.levels")
            print("✅ [3] Το cogs.levels φορτώθηκε!", flush=True)
        except Exception as e:
            print(f"❌ Σφάλμα στο levels: {e}", flush=True)

        try:
            await self.load_extension("cogs.daily")
            print("✅ [4] Το cogs.daily φορτώθηκε!", flush=True)
        except Exception as e:
            print(f"❌ Σφάλμα στο daily: {e}", flush=True)
            
        try:
            await self.load_extension("cogs.roles")
            print("✅ [5] Το cogs.roles φορτώθηκε!", flush=True)
        except Exception as e:
            print(f"❌ Σφάλμα στο roles: {e}", flush=True)
            
        try:
            await self.load_extension("cogs.chat")
            print("✅ [6] Το cogs.chat φορτώθηκε!", flush=True)
        except Exception as e:
            print(f"❌ Σφάλμα στο chat: {e}", flush=True)
        
        try:
            await self.load_extension("cogs.logs")
            print("✅ [7] Το cogs.logs φορτώθηκε!", flush=True)
        except Exception as e:
            print(f"❌ Σφάλμα στο logs: {e}", flush=True)
            
        try:
            await self.load_extension("cogs.stats")
            print("✅ [8] Το cogs.stats φορτώθηκε!", flush=True)
        except Exception as e:
            print(f"❌ Σφάλμα στο matches: {e}", flush=True)

        # Συγχρονισμός των Slash Commands
        try:
            synced = await self.tree.sync()
            print(f"✅ Συγχρονίστηκαν {len(synced)} Slash Commands με το Discord!", flush=True)
        except Exception as e:
            print(f"❌ Αποτυχία συγχρονισμού Slash Commands: {e}", flush=True)

bot = WitherBot()

# ==========================================
# 3. ΣΥΝΔΕΣΗ ΜΕ ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ (MONGODB)
# ==========================================
print("Σύνδεση με τη βάση δεδομένων...", flush=True)
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

# ==========================================
# 4. EVENTS (ON READY & ON MESSAGE)
# ==========================================

# ID του καναλιού που μιλάμε με τον Servitor
AI_CHANNEL_ID = 1546168842496114818

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
        print("Δεν βρέθηκε σκορ στη βάση. Ρύθμιση αρχικού σκορ σε 50...", flush=True)
        glorious_count = 50
        save_count(glorious_count)

@bot.event
async def on_message(message):
    global glorious_count
    
    if message.author == bot.user:
        return

    if message.author.bot or message.guild.id != TARGET_GUILD_ID:
        return

    msg_lower = message.content.lower()

    # Ελέγχουμε αν βρισκόμαστε στο κανάλι που μιλάμε με το AI
    is_ai_channel = (message.channel.id == AI_CHANNEL_ID)

    # --- 5% User React ---
    if message.author.id == SPECIFIC_USER_ID:
        
        magic_numbers = [13, 69]
        
        roll = secrets.randbelow(100)
        
        if roll in magic_numbers:
            try:
                await message.add_reaction("🫃") 
            except:
                pass

    # --- GLORIOUS COUNTER ---
    if message.author.id == TARGET_USER_ID and TARGET_PHRASE.lower().strip() in msg_lower:
        glorious_count += 1
        save_count(glorious_count)
        print(f"Το είπε ξανά! Νέο σύνολο: {glorious_count} (Σώθηκε στο MongoDB)", flush=True)

    # ==========================================
    # MEMES & TRIGGERS (Μπλοκαρισμένα στο AI channel / Reactions επιτρέπονται)

    # --- Hello World ---
    if bot.user in message.mentions and not is_ai_channel:
        if re.search(r'\b(hi|hello|γεια|γειά|hello there)\b', msg_lower):
            await message.channel.send("Imperial greetings! The Emperor protects.") 

    if re.search(r'\b(gay|gays)\b', msg_lower) and not is_ai_channel:
        await message.reply("https://tenor.com/view/abster-abstract-abstractchain-green-pudgy-gif-5688303286939671857")
            
    if re.search(r'wa+gh', msg_lower) and not is_ai_channel:
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
            await message.add_reaction("👁️") # Το reaction μπαίνει κανονικά παντού
        except:
            pass

    if re.search(r'\b(charge|charges|charged)\b', msg_lower):
        if random.randint(1, 2) == 1:
            if not is_ai_channel: # Το GIF στέλνεται ΜΟΝΟ αν δεν είμαστε στο AI channel
                await message.reply("https://tenor.com/view/orc-boyz-total-war-warhammer-greenskins-charge-warhammer-total-war-gif-19312099")
        else:
            try:
                await message.add_reaction("🏇")
            except:
                pass

    if re.search(r'\b(femboy|femboys)\b', msg_lower):
        try:
            await message.add_reaction("<:scream:829005859727212547>")
            # Το GIF στέλνεται ΜΟΝΟ αν δεν είμαστε στο AI channel
            if random.randint(1, 100) <= 75 and not is_ai_channel:
                await message.reply("https://tenor.com/view/the-office-no-angry-steve-carell-michael-scott-gif-5606969")
        except:
            pass
            
    if re.search(r'\bcruel sun\b', msg_lower) and not is_ai_channel:
        await message.reply("https://klipy.com/gifs/seven-deadly-sins-escanor")
            
    await bot.process_commands(message)
 
# ==========================================
# 5. ΕΝΤΟΛΕΣ ΒΑΣΗΣ ΔΕΔΟΜΕΝΩΝ (COMMANDS)
# ==========================================
@bot.command(name="counter")
async def show_counter(ctx):
    await ctx.send(f"Ο <@{TARGET_USER_ID}> έχει πει τη φράση '{TARGET_PHRASE}' {glorious_count} φορές! <:Custode:1439332561468920132>")

bot.run(TOKEN)