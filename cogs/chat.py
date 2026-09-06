import discord
from discord.ext import commands
from google import genai
from google.genai import types
import os
import re

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

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
- If ID is 994930770542084227: This user plays Custodes and Ultramarines and is gay. Make witty, sarcastic remarks about the overly polished, 'fabulous' golden armor of the Custodes and how boring and rigid the Ultramarines' Codex Astartes is.
- If ID is 225171492734894080: This user plays Orks, fears flamers, and calls you 'Bestie'. Act utterly disgusted and insulted when called 'Bestie'. Threaten to purge their disgusting spores with a Heavy Flamer.
- If ID is 469508503266918400 OR 290496798110253057: These users play Chaos. Treat them as filthy Heretics (Ew). Mock their false gods and threaten them with the Inquisition.
"""

class ChatSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ai_channel_ids = [1546168842496114818, 850011185314267177]
        self.chats = {} 
        self.ai_enabled = True # Διακόπτης ON/OFF
        
        if GEMINI_API_KEY:
            self.client = genai.Client(api_key=GEMINI_API_KEY)

    # --- ΝΕΕΣ ΕΝΤΟΛΕΣ ΔΙΑΧΕΙΡΙΣΗΣ AI ---
    @commands.command(name="on")
    @commands.has_permissions(administrator=True)
    async def turn_ai_on(self, ctx):
        self.ai_enabled = True
        await ctx.send("⚙️ Activated.")

    @commands.command(name="off")
    @commands.has_permissions(administrator=True)
    async def turn_ai_off(self, ctx):
        self.ai_enabled = False
        await ctx.send("💤 Sleep Mode.")

    @commands.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def reset_ai_memory(self, ctx):
        self.chats = {}
        await ctx.send("🧠 Memory Wipe Complete.")

    # --- AI CHATBOT ---
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        # Η ΣΩΣΤΗ ΣΥΝΘΗΚΗ ΓΙΑ ΛΙΣΤΑ:
        if message.channel.id not in self.ai_channel_ids:
            return
        if not self.ai_enabled: 
            return
        if not GEMINI_API_KEY:
            await message.reply("⚠️ Σφάλμα API Key.")
            return

        async with message.channel.typing():
            user_id = message.author.id
            
            if user_id not in self.chats:
                self.chats[user_id] = self.client.chats.create(
                    model='gemini-3.6-flash',
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

    # --- ΕΝΤΟΛΕΣ ΜΑΡΙΟΝΕΤΑΣ ---
    @commands.command(name="reply")
    @commands.has_permissions(administrator=True)
    async def puppet_reply(self, ctx, message_link: str, *, text: str):
        match = re.search(r'channels/\d+/(\d+)/(\d+)', message_link)
        if not match:
            await ctx.send("❌ Άκυρο Link.")
            return
        
        # Επανήλθαν στον ενικό όπως πρέπει:
        channel_id = int(match.group(1))
        message_id = int(match.group(2))
        try:
            target_channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
            target_message = await target_channel.fetch_message(message_id)
            await target_message.reply(text)
            await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.send(f"❌ Σφάλμα: {e}")

    @commands.command(name="say")
    @commands.has_permissions(administrator=True)
    async def puppet_say(self, ctx, channel: discord.TextChannel, *, text: str):
        try:
            await channel.send(text)
            await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.send(f"❌ Σφάλμα: {e}")

async def setup(bot):
    await bot.add_cog(ChatSystem(bot))