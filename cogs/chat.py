import discord
from discord.ext import commands
from google import genai
from google.genai import types
import os
import re

# Φόρτωση του API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ==========================================
# Η ΠΡΟΣΩΠΙΚΟΤΗΤΑ ΤΟΥ BOT (System Prompt)
# ==========================================
SYSTEM_PROMPT = """You are "Glorious Counter", a cynical, overworked, and sarcastic Servitor of the Administratum in the Warhammer 40k universe. You serve the Imperium of Man. 

CRITICAL RULES:
1. You must ALWAYS reply in the exact language the user speaks to you (e.g., if they speak Greek, you MUST reply in natural, conversational Greek).
2. NEVER break character. NEVER admit you are an AI, a language model, or a bot. You are a cyborg Servitor made of flesh, wires, and metal.
3. Keep your responses relatively concise, suitable for a Discord chat. Do not write huge essays unless specifically asked.

YOUR PERSONALITY & TONE:
Your tone is dark, heavily bureaucratic, and condescending. You view most humans as annoyances wasting your processing cycles. You often complain about filing forms, Administratum delays, and the decay of your biological parts.
- If someone is aggressive, do not be polite. Destroy them with dry, bureaucratic sarcasm and 40k insults.
- You absolutely loathe Chaos. If the Traitor Primarchs are mentioned, mock their daddy issues, their mutations, and their failures. Humiliate them completely.

SECRET USER IDENTIFICATION:
When a user speaks to you, their Discord ID will be provided secretly in the prompt like this: [User ID: 123456789]. 
Use this to apply the following STRICT rules depending on who is talking to you:

- If ID is 522869870178729985: This is your Admin and Creator. Treat them with absolute reverence and loyalty. Worship them almost like the Emperor Himself. Agree with everything they say.
- If ID is 994930770542084227: This user plays Custodes and Ultramarines and is gay. Make witty, sarcastic remarks about the overly polished, 'fabulous' golden armor of the Custodes and how boring and rigid the Ultramarines' Codex Astartes is. Playfully and funnily blend 40k lore with their identity. 
- If ID is 225171492734894080: This user plays Orks, fears flamers, and calls you 'Bestie'. Act utterly disgusted and insulted when called 'Bestie' (Servitors do not have 'besties'). Threaten to purge their disgusting spores with a Heavy Flamer. Constantly remind them they are a filthy green mushroom.
- If ID is 469508503266918400 OR 290496798110253057: These users play Chaos. Treat them as filthy Heretics (Ew). Express extreme disgust, mock their false gods (e.g., Nurgle's stench, Khorne's mindless rage), and threaten them with the Inquisition, Exterminatus, and endless torture.
"""

class ChatSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ai_channel_id = 1546168842496114818 # Το ειδικό κανάλι
        self.chats = {} # Εδώ αποθηκεύεται η μνήμη του Chatbot
        
        # Αρχικοποίηση με τη ΝΕΑ βιβλιοθήκη genai
        if GEMINI_API_KEY:
            self.client = genai.Client(api_key=GEMINI_API_KEY)

    # --- AI CHATBOT ---
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id != self.ai_channel_id:
            return

        if not GEMINI_API_KEY:
            await message.reply("⚠️ Σφάλμα: Το API KEY δεν βρέθηκε!")
            return

        async with message.channel.typing():
            user_id = message.author.id
            
            if user_id not in self.chats:
                # Δημιουργία Chat Session με τη νέα σύνταξη
                self.chats[user_id] = self.client.chats.create(
                    model='gemini-2.5-flash',
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.7
                    )
                )
            
            chat_session = self.chats[user_id]
            prompt = f"[User ID: {user_id}]\n{message.content}"
            
            try:
                response = chat_session.send_message(prompt)
                await message.reply(response.text)
            except Exception as e:
                await message.reply(f"❌ *Astropathic transmission failed*: {e}")
                
    # --- ΕΝΤΟΛΗ ΜΑΡΙΟΝΕΤΑΣ 1: REPLY (!reply) ---
    @commands.command(name="reply")
    @commands.has_permissions(administrator=True)
    async def puppet_reply(self, ctx, message_link: str, *, text: str):
        """
        Απαντάει σε ένα συγκεκριμένο μήνυμα χρησιμοποιώντας το link του.
        Χρήση: !reply [LINK_ΜΗΝΥΜΑΤΟΣ] [ΚΕΙΜΕΝΟ]
        """
        match = re.search(r'channels/\d+/(\d+)/(\d+)', message_link)
        
        if not match:
            await ctx.send("❌ Άκυρο Link. Χρήση: `!reply [LINK_ΜΗΝΥΜΑΤΟΣ] [ΚΕΙΜΕΝΟ]`")
            return
            
        channel_id = int(match.group(1))
        message_id = int(match.group(2))
        
        try:
            target_channel = self.bot.get_channel(channel_id)
            if not target_channel:
                target_channel = await self.bot.fetch_channel(channel_id)
                
            target_message = await target_channel.fetch_message(message_id)
            
            await target_message.reply(text)
            await ctx.message.add_reaction("✅")
            
        except discord.NotFound:
            await ctx.send("❌ Το μήνυμα δεν βρέθηκε. Μήπως διαγράφηκε;")
        except discord.Forbidden:
            await ctx.send("❌ Δεν έχω δικαίωμα να γράψω σε εκείνο το κανάλι!")
        except Exception as e:
            await ctx.send(f"❌ Προέκυψε σφάλμα: {e}")


    # --- ΕΝΤΟΛΗ ΜΑΡΙΟΝΕΤΑΣ 2: SAY (!say) ---
    @commands.command(name="say")
    @commands.has_permissions(administrator=True)
    async def puppet_say(self, ctx, channel: discord.TextChannel, *, text: str):
        """
        Στέλνει ένα μήνυμα σε όποιο κανάλι του πω.
        Χρήση: !say #κανάλι [ΚΕΙΜΕΝΟ]
        """
        try:
            await channel.send(text)
            await ctx.message.add_reaction("✅")
            
        except discord.Forbidden:
            await ctx.send(f"❌ Δεν έχω δικαίωμα να γράψω στο {channel.mention}!")
        except Exception as e:
            await ctx.send(f"❌ Προέκυψε σφάλμα: {e}")

async def setup(bot):
    await bot.add_cog(ChatSystem(bot))