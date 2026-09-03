"""
========================================
ΑΡΧΕΙΟ: chat.py (Cogs)
ΠΕΡΙΓΡΑΦΗ: Σύστημα Μαριονέτας & (Μελλοντικά) AI Chatbot
========================================
"""

import discord
from discord.ext import commands
import re

class ChatSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- ΕΝΤΟΛΗ ΜΑΡΙΟΝΕΤΑΣ (!reply) ---
    @commands.command(name="reply")
    @commands.has_permissions(administrator=True)  # Μόνο Admins μπορούν να το κάνουν
    async def puppet_reply(self, ctx, message_link: str, *, text: str):
        """
        Απαντάει σε ένα συγκεκριμένο μήνυμα χρησιμοποιώντας το link του.
        Χρήση: !reply [LINK_ΜΗΝΥΜΑΤΟΣ] [ΚΕΙΜΕΝΟ]
        """
        
        # 1. Διαβάζουμε το link για να βρούμε σε ποιο κανάλι και σε ποιο μήνυμα ανήκει
        match = re.search(r'channels/\d+/(\d+)/(\d+)', message_link)
        
        if not match:
            await ctx.send("❌ Άκυρο Link. Βεβαιώσου ότι έκανες δεξί κλικ στο μήνυμα -> **Αντιγραφή συνδέσμου μηνύματος** (Copy Message Link).")
            return
            
        channel_id = int(match.group(1))
        message_id = int(match.group(2))
        
        try:
            # 2. Βρίσκουμε το κανάλι και το μήνυμα
            target_channel = self.bot.get_channel(channel_id)
            if not target_channel:
                target_channel = await self.bot.fetch_channel(channel_id)
                
            target_message = await target_channel.fetch_message(message_id)
            
            # 3. Το bot κάνει Reply στο μήνυμα-στόχο
            await target_message.reply(text)
            
            # 4. Βάζουμε ένα τικ στο αρχικό (κρυφό) μήνυμα του admin για επιβεβαίωση
            await ctx.message.add_reaction("✅")
            
        except discord.NotFound:
            await ctx.send("❌ Το μήνυμα δεν βρέθηκε. Μήπως διαγράφηκε;")
        except discord.Forbidden:
            await ctx.send("❌ Δεν έχω δικαίωμα να γράψω σε εκείνο το κανάλι!")
        except Exception as e:
            await ctx.send(f"❌ Προέκυψε σφάλμα: {e}")

async def setup(bot):
    await bot.add_cog(ChatSystem(bot))