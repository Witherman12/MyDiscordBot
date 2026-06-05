"""
========================================
ΑΡΧΕΙΟ: fun.py (Cog)
ΠΕΡΙΓΡΑΦΗ: Διαχειρίζεται τις ψυχαγωγικές και wargaming εντολές του bot.
ΕΝΤΟΛΕΣ:
 - !roll [αριθμός] : Ρίχνει d6 ζάρια με κρυπτογραφική τυχαιότητα.
 - !quote          : Στέλνει μια τυχαία (χωρίς επανάληψη) ατάκα από το lore του 40k.
 - !overwatch      : Στέλνει το flamer gif από τοπικό αρχείο.
 - !excuse         : Στέλνει μια τυχαία δικαιολγία.
 - !math           : Πιθανότητες ζαριών
 - !trivia         : Warhammer lore trivia
 - !void           : Στέλνει κάποιον στο Custodes Void
========================================
"""

import discord
from discord.ext import commands
import secrets
import random
import os
import asyncio

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
        
        # --- Λίστα με Ερωτήσεις Trivia ---
        self.trivia_questions = [
            {"q": "Which Primarch broke Leman Russ's back?", "a": ["magnus", "magnus the red"]},
            {"q": "Who was the Warmaster that led the great betrayal against the Emperor?", "a": ["horus", "horus lupercal"]},
            {"q": "Which Chaos God represents disease, decay, and despair?", "a": ["nurgle"]},
            {"q": "Which Xenos race fights for the 'Greater Good'?", "a": ["tau", "t'au"]},
            {"q": "Who is the famous Necron overlord who 'borrows' historical artifacts for his galleries?", "a": ["trazyn", "trazyn the infinite"]},
            {"q": "Which Primarch killed Sanguinius aboard the Vengeful Spirit?", "a": ["horus", "horus lupercal"]},
            {"q": "What is the name of the Chaos God of Blood, War, and Murder?", "a": ["khorne"]},
            {"q": "Which Primarch is the genetic father of the Blood Angels?", "a": ["sanguinius"]},
            {"q": "On which planet is the Emperor's Golden Throne located?", "a": ["terra", "holy terra"]},
            {"q": "What is the name of the small, mischievous daemons of Nurgle?", "a": ["nurglings", "nurgling"]}
        ]
        random.shuffle(self.trivia_questions)
        self.current_trivia_index = 0

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
        await ctx.send(f"«*{chosen_excuse}*»")
        
    # --- ΕΝΤΟΛΗ: MATHHAMMER ---
    @commands.command(name="math")
    async def mathhammer(self, ctx, attacks: int = 0, skill: int = 0, strength: int = 0, toughness: int = 0):
        # 1. Έλεγχος αν ο χρήστης έβαλε σωστά νούμερα
        if attacks <= 0 or skill < 2 or skill > 6 or strength <= 0 or toughness <= 0:
            await ctx.send("❌ Λάθος! Δοκίμασε: `!math [A] [BS/WS] [S] [T]`")
            return

        # 2. Υπολογισμός Hits
        hit_chance = (7 - skill) / 6.0
        expected_hits = attacks * hit_chance
       

        # 3. Υπολογισμός Wounds (Κανόνες 10th Edition)
        if strength >= toughness * 2:
            wound_target = 2
        elif strength > toughness:
            wound_target = 3
        elif strength == toughness:
            wound_target = 4
        elif strength * 2 <= toughness:
            wound_target = 6
        else: # strength < toughness
            wound_target = 5
            
        wound_chance = (7 - wound_target) / 6.0
        expected_wounds = expected_hits * wound_chance

        # 4. Εμφάνιση του τελικού αποτελέσματος στο Discord
        message = (
            f"🧮 **Mathhammer Report** 🧮\n"
            f"**Επιθέσεις:** {attacks} | **Hit σε:** {skill}+ | **S:** {strength} vs **T:** {toughness} (Wound σε: {wound_target}+)\n"
            f"----------\n"
            f"🎯 Αναμενόμενα Hits: **{expected_hits:.2f}**\n"
            f"🩸 Αναμενόμενα Wounds: **{expected_wounds:.2f}**\n"
        )
        await ctx.send(message)
        
    # --- ΕΝΤΟΛΗ: TRIVIA ---
    @commands.command(name="trivia")
    async def trivia_game(self, ctx):
        # Αν τελείωσαν οι ερωτήσεις, ανακατεύουμε ξανά!
        if self.current_trivia_index >= len(self.trivia_questions):
            random.shuffle(self.trivia_questions)
            self.current_trivia_index = 0
            
        # Διαλέγουμε τη σημερινή ερώτηση και προχωράμε τον μετρητή
        q_data = self.trivia_questions[self.current_trivia_index]
        self.current_trivia_index += 1
        
        await ctx.send(
            f"🧠 **Warhammer 40k Trivia!** 🧠\n"
            f"Έχετε **30 sec** να γράψετε τη σωστή απάντηση!\n\n"
            f"**Question:** {q_data['q']}"
        )
        
        # Η συνάρτηση που ελέγχει αν η απάντηση που γράφτηκε είναι η σωστή
        def check(m):
            if m.channel != ctx.channel or m.author.bot:
                return False
            user_ans = m.content.lower().strip()
            return any(correct_ans in user_ans for correct_ans in q_data['a'])
            
        try:
            # Το bot περιμένει την απάντηση
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            correct_answers = " / ".join(q_data['a']).title()
            await ctx.send(f"⏳ Τέλος χρόνου! Κανείς δεν βρήκε την απάντηση.\nΤο σωστό ήταν: **{correct_answers}**.")
        else:
            await ctx.send(f"🎉 Ο **{msg.author.display_name}**! Έδωσε τη σωστή απάντηση!")
            
    # --- ΕΝΤΟΛΗ: VOID ---
    @commands.command(name="void")
    async def send_to_void(self, ctx, target: discord.Member):
        # 1. ΕΛΕΓΧΟΣ ΑΔΕΙΑΣ
        allowed_inquisitors = [802082482320703489] # Mods ID
        
        if ctx.author.id not in allowed_inquisitors:
            await ctx.send("❌ Δεν έχεις την εξουσιοδότηση της Ιεράς Εξέτασης για να ανοίξεις το Void!")
            return
            
        if target.bot:
            await ctx.send("🤖 Δεν μπορείς να στείλεις ένα Bot στο Void!")
            return

        # 2. ΤΟ ID ΤΟΥ ΕΤΟΙΜΟΥ THREAD
        VOID_THREAD_ID = 1512502090667397162  # ID PRIVATE THREAD
        
        try:
            # Το bot ψάχνει να βρει το συγκεκριμένο thread
            thread = await self.bot.fetch_channel(VOID_THREAD_ID)
        except discord.NotFound:
            await ctx.send("❌ Σφάλμα: Δεν βρέθηκε το Void Thread! Έλεγξε το ID.")
            return

        # 3. Ανακοίνωση
        await ctx.send(f"⚠️ Ο **{ctx.author.display_name}** άνοιξε την πύλη!\nΟ **{target.display_name}** καταδικάζεται σε 10 δευτερόλεπτα με τους Custodes...")

        try:
            # 4. Βάζουμε το θύμα μέσα στο thread
            await thread.add_user(target)
            
            custodes_gifs = [
                "https://tenor.com/view/tts-custodes-pillar-men-gif-15519847",
                "https://tenor.com/view/oh-no-40k-40k-tts-tts-if-the-emperor-had-a-text-to-speech-device-gif-25047215",
                "https://tenor.com/view/emperor-text-to-speech-custodes-erogenous-metaphors-gif-27361743",
                "https://tenor.com/view/garnoludek-tts-wh40k-gif-20988900"
            ]
            
            # 5. Spam Thread (~10 δευτερόλεπτα)
            end_time = asyncio.get_event_loop().time() + 10.0
            
            while asyncio.get_event_loop().time() < end_time:
                gif = secrets.choice(custodes_gifs)
                await thread.send(f"<@{target.id}> ΑΝΑΝΕΩΣΕ ΤΟΝ ΟΡΚΟ ΣΟΥ ΣΤΟΝ ΑΥΤΟΚΡΑΤΟΡΑ!\n{gif}")
                # Περιμένουμε 2 sec για να μη φάμε ban για spam
                await asyncio.sleep(2) 
                
            # 6. Τέλος τιμωρίας - Τον βγάζουμε από το thread
            await thread.remove_user(target)
            
            # Ανακοίνωση Επιστροφής
            await ctx.send(f"✅ Ο **{target.display_name}** επέστρεψε από το Void. Ελπίζουμε να πήρε το μάθημά του.")
            
        except discord.errors.Forbidden:
            await ctx.send("❌ Σφάλμα: Το bot δεν έχει δικαίωμα να προσθέτει/αφαιρεί άτομα από αυτό το Thread!")
            
# Απαραίτητη συνάρτηση για να φορτώσει το Discord το αρχείο
async def setup(bot):
    await bot.add_cog(FunCommands(bot))