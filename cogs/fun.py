"""
========================================
ΑΡΧΕΙΟ: fun.py (Cog)
ΠΕΡΙΓΡΑΦΗ: Διαχειρίζεται τις ψυχαγωγικές και wargaming εντολές του bot.
ΕΝΤΟΛΕΣ:
 - !roll [αριθμός] : Ρίχνει d6 ζάρια με κρυπτογραφική τυχαιότητα.
 - !quote          : Στέλνει μια τυχαία (χωρίς επανάληψη) ατάκα από το lore του 40k.
 - !overwatch      : Στέλνει το flamer gif από τοπικό αρχείο.
 - !excuse         : Στέλνει μια τυχαία δικαιολγία.
========================================
"""

import discord
from discord.ext import commands
import secrets
import random
import os

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Λίστα με Quotes 
        self.quotes = [
            "«In the grim darkness of the far future, there is only war.»",
            "«The Emperor protects.»",
            "«Blood for the Blood God! Skulls for the Skull Throne!»",
            "«Hope is the first step on the road to disappointment.»",
            "«Knowledge is power, guard it well.»",
            "«An open mind is like a fortress with its gates unbarred and unguarded.»",
            "«Even in death, I still serve.»",
            "«Innocence proves nothing.»",
            "«Walk softly, and carry a big gun.»",
            "«Success is measured in blood; yours or your enemy's.»",
            "«To clean a component with a stained rag is a sin against the Machine God.»",
            "«Blessed is the mind too small for doubt.»",
            "«There is no such thing as innocence, only degrees of guilt.»",
            "«The Orks are the pinnacle of creation. For them, the great struggle is won.»",
            "«By the Emperor's decree, let heresy be met with fire.»",
            "«Fear denies faith.»",
            "«A coward dies a thousand deaths. A hero dies but once.»",
            "«For those who seek perfection there can be no rest on this side of the grave.»",
            "«Only the awkward questions are ever asked. The smooth ones answer themselves.»",
            "«Burn the heretic. Kill the mutant. Purge the unclean.»"
        ]
        random.shuffle(self.quotes)
        self.current_index = 0
        
        # Λίστα με Δικαιολογίες
        self.excuses = [
            "Τα ζάρια μου είχαν διαφθαρεί από το Warp! 🌀",
            "Είναι ξεκάθαρο... Ο Alpharius είχε παρεισφρήσει στα στρατεύματά μου! 🐍",
            "Το τραπέζι έγερνε προς την πλευρά του αντιπάλου! 📐",
            "Απλά έκανα tactical retreat για να τον παρασύρω σε παγίδα... στο επόμενο παιχνίδι! 🏃‍♂️",
            "Τα Machine Spirits των ζαριών μου με εγκατέλειψαν. Ξέχασα το ιερό λάδι. ⚙️",
            "Δεν έχασα, απλά ο Tzeentch άλλαξε το σχέδιο την τελευταία στιγμή! 🦅",
            "Όλος μου ο στρατός ήταν απλά ένα ολόγραμμα του Trazyn the Infinite! 💀",
            "Σκοπίμως έφερα άσσους, είναι όλα μέρος του Greater Good. 🐟",
            "Ο ήλιος χτυπούσε το τραπέζι και τύφλωνε τα μοντέλα μου! ☀️",
            "Η Ιερά Εξέταση μου απαγόρευσε να χρησιμοποιήσω την πραγματική μου στρατηγική. 👁️",
            "Το codex μου είναι ξεπερασμένο, περιμένω το dataslate για να δείξω την πραγματική μου δύναμη! 📖",
            "Ο Nurgle είχε αρρωστήσει τα ζάρια μου και δεν μπορούσαν να ρολάρουν πάνω από 2... 🤢"
        ]
        random.shuffle(self.excuses)
        self.current_excuse_index = 0

    # --- ΕΝΤΟΛΗ: ΖΑΡΙΑ ---
    @commands.command(name="roll")
    async def roll_dice(self, ctx, amount: int = 1):  # Προστέθηκε το self
        if amount <= 0:
            await ctx.send("❌ Πρέπει να ρίξεις τουλάχιστον 1 ζάρι!")
            return
        if amount > 100:
            await ctx.send("❌ Πολλά ζάρια! Το όριο είναι 100 τη φορά.")
            return

        rolls = [secrets.choice(range(1, 7)) for _ in range(amount)]
        total = sum(rolls)
        rolls_str = ", ".join(map(str, rolls))

        await ctx.send(
            f"🎲 Ο **{ctx.author.display_name}** έριξε **{amount}** ζάρια!\n"
            f"Αποτελέσματα: **{rolls_str}**\n"
            f"Σύνολο: **{total}**"
        )

    # --- ΕΝΤΟΛΗ: QUOTE ---
    @commands.command(name="quote")
    async def send_quote(self, ctx):  # Προστέθηκε το self
        # Χρησιμοποιούμε παντού το self για να καλέσουμε τις μεταβλητές μας
        if self.current_index >= len(self.quotes):
            random.shuffle(self.quotes)
            self.current_index = 0

        await ctx.send(f"📜 {self.quotes[self.current_index]}")
        self.current_index += 1

    # --- ΕΝΤΟΛΗ: OVERWATCH ---
    @commands.command(name="overwatch")
    async def overwatch_gif(self, ctx):  # Προστέθηκε το self
        if os.path.exists("flamer.gif"):
            with open("flamer.gif", "rb") as f:
                picture = discord.File(f)
            await ctx.send(f"🔥 **OVERWATCH!** Ο **{ctx.author.display_name}** ανάβει τα Flamers!", file=picture)
        else:
            await ctx.send("❌ Σφάλμα: Δεν βρέθηκε το αρχείο `flamer.gif`!")

    # --- ΕΝΤΟΛΗ: EXCUSE ---
    @commands.command(name="excuse")
    async def defeat_excuse(self, ctx):
        # Αν τελείωσαν οι δικαιολογίες ανακατεύουμε ξανά.
        if self.current_excuse_index >= len(self.excuses):
            random.shuffle(self.excuses)
            self.current_excuse_index = 0
            
        # Διαλέγουμε την σημερινή δικαιολογία
        chosen_excuse = self.excuses[self.current_excuse_index]
        self.current_excuse_index += 1
        
        # Στέλνουμε το τελικό μήνυμα
        await ctx.send(f"Ο **{ctx.author.display_name}** δηλώνει υπεύθυνα ότι:\n«*{chosen_excuse}*»")
        
# Απαραίτητη συνάρτηση για να φορτώσει το Discord το αρχείο
async def setup(bot):
    await bot.add_cog(FunCommands(bot))