import discord
from discord.ext import commands
import re

class ChatSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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