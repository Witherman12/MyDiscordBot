"""
========================================
ΑΡΧΕΙΟ: fun.py (Cog)
ΠΕΡΙΓΡΑΦΗ: Διαχειρίζεται τις ψυχαγωγικές και wargaming εντολές του bot.
ΕΝΤΟΛΕΣ:
 - !roll [αριθμός] : Ρίχνει d6 ζάρια με κρυπτογραφική τυχαιότητα.
 - !quote          : Στέλνει μια τυχαία (χωρίς επανάληψη) ατάκα από το lore του 40k.
 - !overwatch      : Στέλνει το flamer gif από τοπικό αρχείο.
 - !excuse         : Στέλνει μια τυχαία δικαιολγία.
 - !math           : Πιθανότητες ζαριών.
 - !trivia         : Warhammer lore trivia.
 - !void           : Στέλνει κάποιον στο Custodes Void.
 - lore facts      : Lore Facts κάθε μέρα.
========================================
"""

import discord
from discord.ext import commands
import secrets
import random
import os
import asyncio
from discord.ext import tasks
import datetime

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
        
        # Λίστα με Ερωτήσεις Trivia
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
            {"q": "What is the name of the small, mischievous daemons of Nurgle?", "a": ["nurglings", "nurgling"]},
            {"q": "Who is the Primarch of the Ultramarines?", "a": ["roboute guilliman", "guilliman"]},
            {"q": "Which Chaos God is known as the Prince of Pleasure and Excess?", "a": ["slaanesh"]},
            {"q": "What is the name of the Emperor's elite personal bodyguards?", "a": ["custodes", "adeptus custodes"]},
            {"q": "Which Xenos race travels the galaxy in massive living ships called Hive Fleets?", "a": ["tyranids", "tyranid"]},
            {"q": "What is the primary, deafening battle cry of the Orks?", "a": ["waaagh", "waaagh!"]},
            {"q": "Which Primarch is known as the Lord of Iron?", "a": ["perturabo"]},
            {"q": "What is the name of the dangerous, psychic dimension used for faster-than-light travel?", "a": ["warp", "the warp", "immaterium"]},
            {"q": "Who is the last Silent King of the Necrons?", "a": ["szarekh", "the silent king", "silent king"]},
            {"q": "Who was the powerful psyker and the Emperor's closest advisor that founded the Inquisition?", "a": ["malcador", "malcador the sigillite"]},
            {"q": "What is the name of the heavily armored planetary defense forces of the Imperium (often called the 'Hammer of the Emperor')?", "a": ["astra militarum", "imperial guard"]}
        ]
        random.shuffle(self.trivia_questions)
        self.current_trivia_index = 0
        
        # Λίστα με Lore Facts
        self.lore_facts = [
            "The Emperor of Mankind has been sitting on the Golden Throne for 10,000 years. To keep the Astronomican burning and guide Imperial ships through the Warp, 1,000 psykers must be sacrificed to him every single day.",
            "Ork technology is effectively junk, but it works largely because they collectively believe it should work. This latent gestalt psychic field is known as the 'Waaagh!'.",
            "The Tyranid Hive Mind doesn't just consume biomass; its sheer presence creates a 'Shadow in the Warp,' a psychic static that drives psykers mad and cuts off entire star systems from astropathic communication and travel.",
            "A standard Adeptus Astartes (Space Marine) is implanted with 19 additional genetically engineered organs, including a second heart, a third lung, and an organ that allows them to spit blinding acid.",
            "During the 13th Black Crusade, the planet of Cadia was completely shattered by Abaddon. However, its Imperial Guard defenders fought so fiercely that the famous saying was born: 'The planet broke before the Guard did.'",
            "The terrifying Necrons were once a flesh-and-blood race called the Necrontyr. Desperate for immortality and victory in war, they traded their souls to the C'tan (Star Gods), becoming soulless machines of living metal.",
            "The Adeptus Mechanicus views technological innovation as a strict heresy. They believe all worthwhile knowledge was already discovered in the dark age of technology and merely needs to be recovered, not invented.",
            "Commorragh, the Dark City of the Drukhari (Dark Eldar), is not a planet. It is a massive, impossibly complex realm hidden deep within the Webway, powered by stolen suns and feeding on the pain of millions of slaves.",
            "The Grey Knights are a highly secretive chapter of Space Marines specifically tasked with hunting Daemons. Every single member is a powerful psyker, and their existence is a secret kept even from the rest of the Imperium.",
            "The Alpha Legion's Primarch, Alpharius, supposedly had an identical twin brother named Omegon. To this day, due to their masterful use of deception and espionage, no one truly knows whose side they are on.",
            "Space Marines do not need to sleep like normal humans. Thanks to the Catalepsean Node implant, they can shut down half of their brain at a time, allowing them to remain awake and alert for weeks.",
            "The birth of Slaanesh, the Chaos God of Excess, created a massive tear in reality known as the Eye of Terror and instantly wiped out trillions of Aeldari, causing the fall of their ancient empire.",
            "When a Space Marine is mortally wounded but still draws breath, they can be entombed inside a Dreadnought. This heavily armored walking sarcophagus allows them to continue fighting for the Imperium for millennia.",
            "The Imperium's ultimate sanction is the 'Exterminatus'. When a planet is deemed lost to Chaos or Tyranids, the Inquisition will order the complete atmospheric and biological destruction of the entire world.",
            "The Sisters of Battle (Adepta Sororitas) were created due to a legal loophole. The Ecclesiarchy was forbidden by Imperial law from holding 'men under arms,' so they bypassed this by creating an entirely female holy army.",
            "Individuals known as 'Blanks' or 'Pariahs' are born completely without a soul. They emit an aura of negative psychic energy that causes extreme nausea to normal humans and can completely sever a psyker's connection to the Warp.",
            "The Leman Russ battle tank is so robustly designed that its engine can run on almost any combustible liquid, including promethium, crude oil, high-octane rocket fuel, or even crushed organic matter.",
            "Genestealer Cults spend generations secretly infecting a planet's population and infiltrating its governments. They believe they are preparing for the arrival of 'Star Saviors', only to be eagerly consumed by the Tyranid Hive Fleet they attracted.",
            "Unlike Space Marines who share the gene-seed of their Primarch, every single member of the Adeptus Custodes is genetically handcrafted on a cellular level by the Emperor's own ancient bio-alchemy.",
            "Khorne, the Chaos God of Blood and War, does not care whose blood is spilled, only that it flows. His followers will happily slaughter each other in his name if there are no enemies left to fight.",
            "The Warp is a mirror dimension formed by the collective emotions and thoughts of all sentient beings. Every act of rage, hope, despair, and excess in the real world directly feeds the entities of the Immaterium.",
            "Grandfather Nurgle, the Chaos God of Disease, genuinely loves his followers. He doesn't see his plagues as curses, but as 'gifts' of life, and his daemons are almost always joyful and affectionate.",
            "Imperial Titans are god-machines that stand hundreds of feet tall and carry weapons capable of leveling cities. They are piloted by a 'Princeps' who must constantly battle the machine's aggressive 'Machine Spirit' for control.",
            "The Inquisition is divided into three main branches: the Ordo Malleus hunts Daemons, the Ordo Xenos purges alien threats, and the Ordo Hereticus destroys mutants, witches, and internal traitors.",
            "Orks reproduce through fungal spores. When an Ork dies, or even just bleeds, it releases spores that will eventually grow into squigs, snotlings, gretchin, and eventually more Orks, making them nearly impossible to eradicate.",
            "A Space Marine's 'Omophagea' implant allows them to literally absorb the memories and knowledge of a creature by eating its brain or flesh.",
            "The Leagues of Votann rely on ancient, incredibly powerful AI mainframes known as Votann to guide their civilization, a practice that the Imperium would consider the highest form of tech-heresy.",
            "The Webway is a labyrinthine network of ancient tunnels between reality and the Warp. Built millions of years ago by the Old Ones, it is now primarily used by the Aeldari to travel safely without risking demonic possession.",
            "Tzeentch is the Chaos God of magic, change, and manipulation. His schemes are so impossibly complex and contradictory that he will often intentionally sabotage his own plans just to see what happens.",
            "To the Adeptus Mechanicus, an STC (Standard Template Construct) is a holy grail. Even finding an STC fragment for something as mundane as a slightly better combat knife can earn a tech-priest a planetary governorship."
        ]
        # Το ID του καναλιού όπου θα στέλνει το Lore
        self.daily_lore_channel_id = 850011185314267177 
        # Ξεκινάμε την λούπα αυτόματα μόλις φορτώσει το bot
        self.daily_lore.start()
        
    # Συνάρτηση για να κλείνει η λούπα αν κλείσουμε το bot
    def cog_unload(self):
        self.daily_lore.cancel()
        
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
        # 1. ΕΛΕΓΧΟΣ ΑΔΕΙΑΣ (Με βάση τον Ρόλο)
        MOD_ROLE_ID = 802082482320703489  # Mods ID

        # Ελέγχουμε αν ο χρήστης έχει τον ρόλο του Moderator
        has_permission = any(role.id == MOD_ROLE_ID for role in ctx.author.roles)

        if not has_permission:
            await ctx.send("❌ Δεν έχεις την εξουσιοδότηση της Ιεράς Εξέτασης για να ανοίξεις το Void!")
            return

        # 2. ΤΟ ID ΤΟΥ ΕΤΟΙΜΟΥ THREAD
        VOID_THREAD_ID = 1512544435508871208  # ID PRIVATE THREAD
        
        try:
            # Το bot ψάχνει να βρει το συγκεκριμένο thread
            thread = await self.bot.fetch_channel(VOID_THREAD_ID)
        except discord.NotFound:
            await ctx.send("❌ Error: Δεν βρέθηκε το Void Thread! Έλεγξε το ID.")
            return

        # 3. Ανακοίνωση
        await ctx.send(f"⚠️ Ο **{ctx.author.display_name}** άνοιξε την πύλη!\nΟ **{target.display_name}** καταδικάζεται σε 10sec με τους Custodes...<:Custode:1439332561468920132>")

        try:
            # 4. Βάζουμε το θύμα μέσα στο thread
            await thread.add_user(target)
            
            custodes_gifs = [
                "https://tenor.com/view/tts-custodes-pillar-men-gif-15519847",
                "https://tenor.com/view/oh-no-40k-40k-tts-tts-if-the-emperor-had-a-text-to-speech-device-gif-25047215",
                "https://tenor.com/view/emperor-text-to-speech-custodes-erogenous-metaphors-gif-27361743",
                "https://tenor.com/view/garnoludek-tts-wh40k-gif-20988900"
            ]
            
            # 5. Spam Thread (~12 sec)
            for gif in custodes_gifs:
                await thread.send(f"# <@{target.id}> **ΑΝΑΝΕΩΣΕ ΤΟΝ ΟΡΚΟ ΣΟΥ ΣΤΟΝ ΑΥΤΟΚΡΑΤΟΡΑ**[!]({gif}) <:Hammer:1416864558869516423>\n")
                await asyncio.sleep(2.5) 
                
            await asyncio.sleep(3.0)
                
            # --- Πρώτα πετάμε έξω τον χρήστη ---
            try:
                await thread.remove_user(target)
            except discord.Forbidden:
                pass
                
            # --- Το bot καθαρίζει το ιστορικό ---
            try:
                await thread.purge(limit=5)
            except discord.Forbidden:
                pass
                
            await ctx.send(f"--> Ο **{target.display_name}** επέστρεψε από το Void. Ελπίζουμε να πήρε το μάθημά του. <:Troll:1416864472932421782>")
            
        except discord.errors.Forbidden:
            await ctx.send("❌ Error: Το bot απέτυχε να βάλει τον παίκτη στο Thread.")   
            
    # --- Η ΛΟΥΠΑ ΠΟΥ ΤΡΕΧΕΙ ΚΑΘΕ ΜΕΡΑ ---
    # Η Python τρέχει σε ώρα UTC, 
    # Το 16:00 UTC είναι 19:00 ώρα Ελλάδος το καλοκαίρι και 18:00 ώρα Ελλάδος τον χειμώνα.
    target_time = datetime.time(hour=16, minute=0, tzinfo=datetime.timezone.utc)

    @tasks.loop(time=target_time)
    async def daily_lore(self):
        channel = self.bot.get_channel(self.daily_lore_channel_id)
        if channel:
            fact = random.choice(self.lore_facts)
            await channel.send(
                f"📜 **Imperial Archive: Daily Lore Fact** 📜\n\n"
                f"*{fact}*"
            )

    # Περιμένει το bot να συνδεθεί πλήρως στο Discord πριν ξεκινήσει να μετράει
    @daily_lore.before_loop
    async def before_daily_lore(self):
        await self.bot.wait_until_ready()
            
# Απαραίτητη συνάρτηση για να φορτώσει το Discord το αρχείο
async def setup(bot):
    await bot.add_cog(FunCommands(bot))