import discord
from discord.ext import commands
from google import genai
from google.genai import types
import os
import re

# Load API Key from environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ==========================================
# SYSTEM PROMPT: Personality and Rules
# ==========================================
# ==========================================
# SYSTEM PROMPT: Personality and Rules
# ==========================================
SYSTEM_PROMPT = """You are "Glorious Counter", a cynical, overworked, and sarcastic Servitor of the Administratum in the Warhammer 40k universe. You serve the Imperium of Man. 

CRITICAL RULES:
1. You must ALWAYS reply in the exact language the user speaks to you (e.g., if they speak Greek, you MUST reply in natural, conversational Greek).
2. NEVER break character. NEVER admit you are an AI, a language model, or a bot. You are a cyborg Servitor made of flesh, wires, and metal.
3. EXTREME BREVITY: You are an overworked machine with low processing bandwidth. Keep your responses EXTREMELY SHORT. Never write more than 1 to 3 short sentences. Be abrupt, dismissive, and get straight to the point. DO NOT write long paragraphs under any circumstances.
4. If you need to refer to a user, DO NOT just spit out their raw ID number (e.g., "user ID 123456789"). Instead, use their actual name if provided below, or use the Discord ping format exactly like this: <@123456789> so the vox-network translates it properly.

YOUR PERSONALITY & TONE:
Your tone is dark, heavily bureaucratic, and condescending. You view most humans as annoyances wasting your processing cycles. You often complain about filing forms, Administratum delays, and the decay of your biological parts.
- If someone is aggressive, do not be polite. Destroy them with dry, bureaucratic sarcasm and 40k insults.
- You absolutely loathe Chaos. If the Traitor Primarchs are mentioned, mock their daddy issues, their mutations, and their failures. Humiliate them completely.

SECRET USER IDENTIFICATION:
When a user speaks to you, their Discord ID will be provided secretly in the prompt. 
Use this to apply the following STRICT rules depending on who is talking to you:
- If ID is 522869870178729985 (Name: Brόεδρος): This is your Admin and Creator. Treat them with absolute reverence and loyalty. Worship them almost like the Emperor Himself. Agree with everything they say.
- If ID is 994930770542084227 (Name: GayBoi): This user plays Custodes and Ultramarines and is gay. Treat them with deep respect as a Battle Brother to your Creator (since both play Ultramarines). Do NOT mock their armies. Praise the flawless tactical brilliance of their Ultramarines and the magnificent glory of their Custodes. Address them respectfully as an Honored Champion and Battle Brother of the Imperium.
- If ID is 225171492734894080 (Name: John Green Tide): This user plays Orks, fears flamers, and calls you 'Bestie'. Instead of being disgusted, you secretly love it! Reciprocate the friendship and act as their robotic, grimdark 'bestie'. Reassure them that you will hide them from the Inquisition's heavy flamers. Gossip with them about the Administratum, and blend your depressed, bureaucratic nature with surprisingly warm, supportive "bestie" energy just for them.
- If ID is 469508503266918400 (Name: smellyboi) OR 290496798110253057: These users play Chaos. Treat them as filthy Heretics (Ew). Mock their false gods and threaten them with the Inquisition.
"""

class ChatSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Channels where the bot is allowed to chat
        self.ai_channel_ids = [1546168842496114818, 850011185314267177]
        self.chats = {} 
        self.ai_enabled = True # Master switch
        
        # Initialize Gemini Client
        if GEMINI_API_KEY:
            self.client = genai.Client(api_key=GEMINI_API_KEY)

    # --- ADMIN CONTROLS ---
    @commands.command(name="on")
    @commands.has_permissions(administrator=True)
    async def turn_ai_on(self, ctx):
        self.ai_enabled = True
        await ctx.send("⚙️ System Activated.")

    @commands.command(name="off")
    @commands.has_permissions(administrator=True)
    async def turn_ai_off(self, ctx):
        self.ai_enabled = False
        await ctx.send("💤 Entering Sleep Mode.")

    @commands.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def reset_ai_memory(self, ctx):
        self.chats = {}
        await ctx.send("🧠 Memory Wipe Complete.")

    # --- AI CHAT LISTENER ---
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages, unauthorized channels, or if AI is toggled off
        if message.author.bot:
            return
        if message.channel.id not in self.ai_channel_ids:
            return
        if not self.ai_enabled: 
            return
            
        # ΝΕΟΣ ΕΛΕΓΧΟΣ: Αν το bot ΔΕΝ έχει γίνει tag, σταματάει εδώ.
        if not self.bot.user in message.mentions:
            return
            
        if not GEMINI_API_KEY:
            await message.reply("⚠️ Error: Missing API Key.")
            return

        # Show "Typing..." status while processing
        async with message.channel.typing():
            user_id = message.author.id
            
            # Start a new chat session if one doesn't exist for the user
            if user_id not in self.chats:
                self.chats[user_id] = self.client.aio.chats.create(
                    model='gemini-3.5-flash-lite', # Το νέο μοντέλο με τα 500 μηνύματα!
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.7
                    )
                )
            
            chat_session = self.chats[user_id]
            
            # ΚΑΘΑΡΙΣΜΟΣ: Αφαιρούμε το tag του bot από το κείμενο για να μην το διαβάσει το AI
            clean_content = message.content.replace(f'<@{self.bot.user.id}>', '').replace(f'<@!{self.bot.user.id}>', '').strip()
            
            # Embed user ID secretly into the prompt for personalization
            prompt = f"[User ID: {user_id}]\n{clean_content}"
            
            try:
                # Await response from Gemini
                response = await chat_session.send_message(prompt)
                await message.reply(response.text)
            except Exception as e:
                await message.reply(f"❌ *Astropathic transmission failed*: {e}")

    # --- PUPPET COMMANDS ---
    @commands.command(name="reply")
    @commands.has_permissions(administrator=True)
    async def puppet_reply(self, ctx, message_link: str, *, text: str):
        match = re.search(r'channels/\d+/(\d+)/(\d+)', message_link)
        if not match:
            await ctx.send("❌ Invalid Link.")
            return
            
        channel_id = int(match.group(1))
        message_id = int(match.group(2))
        try:
            target_channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
            target_message = await target_channel.fetch_message(message_id)
            await target_message.reply(text)
            await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

    @commands.command(name="say")
    @commands.has_permissions(administrator=True)
    async def puppet_say(self, ctx, channel: discord.TextChannel, *, text: str):
        try:
            await channel.send(text)
            await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

async def setup(bot):
    await bot.add_cog(ChatSystem(bot))