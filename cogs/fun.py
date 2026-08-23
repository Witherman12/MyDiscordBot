"""
========================================
ΑΡΧΕΙΟ: fun.py (Cogs)
ΠΕΡΙΓΡΑΦΗ: Διαχειρίζεται τις ψυχαγωγικές και wargaming εντολές του bot.
ΕΝΤΟΛΕΣ:
 - !help           : Εμφανίζει την λίστα με όλες τις εντολές (Μενού Βοήθειας).
 - !adminhelp      : Εντολές αποκλειστικά για τους Inquisitors (Admins/Mods).
 - !glorious       : Στέλνει το ηχητικό της Glorious Melee Combat (mp3).
 - !counter        : Δείχνει το σκορ του Glorious Melee Combat.
 - !roll [αριθμός] : Ρίχνει d6 ζάρια με κρυπτογραφική τυχαιότητα.
 - !quote          : Στέλνει μια τυχαία (χωρίς επανάληψη) ατάκα από το lore του 40k.
 - !overwatch      : Στέλνει το flamer gif από τοπικό αρχείο.
 - !excuse         : Στέλνει μια τυχαία δικαιολογία.
 - !math           : Πιθανότητες ζαριών (Mathhammer).
 - !trivia         : Warhammer lore trivia.
 - !void           : Στέλνει κάποιον στο Custodes Void.
 - !sus [reply/@]  : Δικάζει δημόσια όποιον στέλνει sus περιεχόμενο.
 - lore facts      : Lore Facts κάθε μέρα (Αυτοματοποιημένο).
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
        
        # Λίστα με Ερωτήσεις Trivia (50 Ερωτήσεις)
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
            {"q": "What is the name of the heavily armored planetary defense forces of the Imperium (often called the 'Hammer of the Emperor')?", "a": ["astra militarum", "imperial guard"]},
            {"q": "Which Primarch is known as the 'Night Haunter'?", "a": ["konrad curze", "curze"]},
            {"q": "What is the icy homeworld of the Space Wolves chapter?", "a": ["fenris"]},
            {"q": "What is the homeworld of the Ultramarines?", "a": ["macragge"]},
            {"q": "Who is the current Chapter Master of the Blood Angels, one of the oldest living Space Marines?", "a": ["dante", "commander dante"]},
            {"q": "What is the name of the all-female order of warriors who are completely psychic blanks (soulless)?", "a": ["sisters of silence"]},
            {"q": "Which Officio Assassinorum temple specializes in long-range sniper assassinations?", "a": ["vindicare", "vindicare temple"]},
            {"q": "Which Primarch forged the legendary hammer known as the Dawnbringer?", "a": ["vulkan"]},
            {"q": "What is the name of the heavily augmented cyborg infantry of the Adeptus Mechanicus?", "a": ["skitarii"]},
            {"q": "Which Space Marine Legion is proudly known as the '1st Legion'?", "a": ["dark angels"]},
            {"q": "Who is the Supreme Grand Master of the Grey Knights, trapped wandering the Warp?", "a": ["kaldor draigo", "draigo"]},
            {"q": "What is the ultimate Imperial sanction that completely destroys the biosphere of a corrupted planet?", "a": ["exterminatus"]},
            {"q": "What is the name of the ancient, walking robotic sarcophagi used by mortally wounded Space Marines?", "a": ["dreadnought", "dreadnoughts"]},
            {"q": "Which Chaos God is known as the Architect of Fate and Lord of Sorcery?", "a": ["tzeentch"]},
            {"q": "Which Chaos Space Marine Legion specializes in siege warfare, trenches, and heavy artillery?", "a": ["iron warriors"]},
            {"q": "Which Primarch is famously known as the 'Red Angel'?", "a": ["angron"]},
            {"q": "What is the name of Abaddon the Despoiler's massive flagship, formerly commanded by Horus?", "a": ["vengeful spirit", "the vengeful spirit"]},
            {"q": "What is the name of Nurgle's most famous, soul-corrupting plague?", "a": ["nurgle's rot", "nurgles rot"]},
            {"q": "Which Primarch of the Emperor's Children fell to Slaanesh in his pursuit of perfection?", "a": ["fulgrim"]},
            {"q": "Who is the Khârn the Betrayer's favored Chaos God?", "a": ["khorne"]},
            {"q": "Who are the twin gods worshipped by the Orks?", "a": ["gork and mork", "mork and gork"]},
            {"q": "Who is the biggest, most dangerous Ork Warboss currently leading the largest Waaagh! in the galaxy?", "a": ["ghazghkull", "ghazghkull thraka", "ghazghkull mag uruk thraka"]},
            {"q": "What living metal forms the bodies of the Necrons?", "a": ["necrodermis"]},
            {"q": "Who is the arrogant Necron Overlord known as the 'Stormlord'?", "a": ["imotekh", "imotekh the stormlord"]},
            {"q": "Which Aeldari (Eldar) God of War's avatar can be summoned into battle?", "a": ["khaine", "kaela mensha khaine"]},
            {"q": "What do Genestealer Cults commonly call the Tyranid Hive Fleet they worship?", "a": ["four armed emperor", "the four-armed emperor", "star children"]},
            {"q": "Which ruling caste of the T'au Empire leads their entire society?", "a": ["ethereal", "ethereals", "ethereal caste"]},
            {"q": "What is the name of the massive, labyrinthine dimension the Aeldari use to travel safely avoiding the Warp?", "a": ["webway", "the webway"]},
            {"q": "Which Drukhari (Dark Eldar) Supreme Overlord rules the dark city of Commorragh?", "a": ["asdrubael vect", "vect"]},
            {"q": "What is the name of the massive Tyranid bio-titans that tower over the battlefield?", "a": ["hierophant", "hierophant bio-titan"]},
            {"q": "Which Tyranid Hive Fleet was responsible for the devastation of the Ultramarines' homeworld in the First Tyrannic War?", "a": ["behemoth", "hive fleet behemoth"]}
        ]
        random.shuffle(self.trivia_questions)
        self.current_trivia_index = 0
        
        # --- LORE CATEGORIES ---
        self.lore_categories = {
            "Imperium of Man": [
                "The Emperor of Mankind has been sitting on the Golden Throne for 10,000 years. To keep the Astronomican burning and guide Imperial ships through the Warp, 1,000 psykers must be sacrificed to him every single day.",
                "During the 13th Black Crusade, the planet of Cadia was completely shattered by Abaddon. However, its Imperial Guard defenders fought so fiercely that the famous saying was born: 'The planet broke before the Guard did.'",
                "The Imperium's ultimate sanction is the 'Exterminatus'. When a planet is deemed lost to Chaos or Tyranids, the Inquisition will order the complete atmospheric and biological destruction of the entire world.",
                "The Sisters of Battle (Adepta Sororitas) were created due to a legal loophole. The Ecclesiarchy was forbidden by Imperial law from holding 'men under arms,' so they bypassed this by creating an entirely female holy army.",
                "Individuals known as 'Blanks' or 'Pariahs' are born completely without a soul. They emit an aura of negative psychic energy that causes extreme nausea to normal humans and can completely sever a psyker's connection to the Warp.",
                "The Inquisition is divided into three main branches: the Ordo Malleus hunts Daemons, the Ordo Xenos purges alien threats, and the Ordo Hereticus destroys mutants, witches, and internal traitors.",
                "The Golden Throne is slowly failing, and nobody in the Imperium knows how to fix it. If it fully breaks, the Emperor will die, the Astronomican will go out, and Terra will likely be consumed by a massive Warp rift.",
                "The Eversor Assassins of the Officio Assassinorum are kept in cryo-sleep until needed. They are pumped full of so many combat drugs that if they are ever killed, their bodies violently detonate in a biological explosion.",
                "The Geller Field, which protects Imperial ships from daemons while traveling through the Warp, is actually generated by the dreams of a comatose, mathematically-lobotomized psyker suspended in a pod.",
                "The Adepta Sororitas use a tank called the 'Exorcist' which is literally a mobile pipe organ. The 'Sister' plays hymns on the organ's keys, which triggers the launch of devastating armor-piercing missiles.",
                "The Culexus Assassins are blanks (soulless). They wear massive animus speculums on their heads that weaponize their negative psychic aura, allowing them to shoot blasts of anti-warp energy that instantly incinerates psykers.",
                "The Imperium uses 'Servitors' for menial labor. These are lobotomized humans, often criminals, whose brains and nervous systems have been heavily augmented with cybernetics to perform a single, repetitive task forever.",
            ],
            "Adeptus Astartes & Primarchs": [
                "A standard Adeptus Astartes (Space Marine) is implanted with 19 additional genetically engineered organs, including a second heart, a third lung, and an organ that allows them to spit blinding acid.",
                "The Grey Knights are a highly secretive chapter of Space Marines specifically tasked with hunting Daemons. Every single member is a powerful psyker, and their existence is a secret kept even from the rest of the Imperium.",
                "Space Marines do not need to sleep like normal humans. Thanks to the Catalepsean Node implant, they can shut down half of their brain at a time, allowing them to remain awake and alert for weeks.",
                "When a Space Marine is mortally wounded but still draws breath, they can be entombed inside a Dreadnought. This heavily armored walking sarcophagus allows them to continue fighting for the Imperium for millennia.",
                "Unlike Space Marines who share the gene-seed of their Primarch, every single member of the Adeptus Custodes is genetically handcrafted on a cellular level by the Emperor's own ancient bio-alchemy.",
                "A Space Marine's 'Omophagea' implant allows them to literally absorb the memories and knowledge of a creature by eating its brain or flesh.",
                "Vulkan, the Primarch of the Salamanders, is a 'Perpetual'. This means he is functionally immortal and has died multiple times, including being dropped into a planetary atmosphere, only to regenerate completely.",
                "A Custodian's name grows longer with every heroic deed they perform. Some veteran Custodes have names that take several hours to recite and are engraved on the inside of their armor.",
                "Corvus Corax, the Primarch of the Raven Guard, spent thousands of years in the Warp hunting traitors. The Warp mutated him not into a daemon, but into a terrifying entity made of shadows and ravens that haunts Word Bearers.",
                "Space Marines have a specialized organ called the 'Betcher's Gland' which allows them to spit blinding, highly corrosive acid strong enough to eat through metal bars.",
                "Lion El'Jonson, Primarch of the Dark Angels, has finally awakened after 10,000 years. He has aged into a wise, tired old man and now uses a mysterious Warp ability called 'Forestwalking' to teleport across the galaxy.",
            ],
            "Astra Militarum": [
                "The Leman Russ battle tank is so robustly designed that its engine can run on almost any combustible liquid, including promethium, crude oil, high-octane rocket fuel, or even crushed organic matter.",
                "Sly Marbo is a legendary Imperial Guard soldier of the Catachan Jungle Fighters. He is essentially the Imperium's version of Rambo, known for taking down entire enemy encampments and even a Tyranid bio-titan single-handedly.",
                "The Death Korps of Krieg are so fanatically devoted to dying for the Emperor that their Commissars are actually stationed with them to hold them back from suicidal charges, rather than to force them forward.",
            ],
            "Adeptus Mechanicus": [
                "The Adeptus Mechanicus views technological innovation as a strict heresy. They believe all worthwhile knowledge was already discovered in the dark age of technology and merely needs to be recovered, not invented.",
                "Imperial Titans are god-machines that stand hundreds of feet tall and carry weapons capable of leveling cities. They are piloted by a 'Princeps' who must constantly battle the machine's aggressive 'Machine Spirit' for control.",
                "To the Adeptus Mechanicus, an STC (Standard Template Construct) is a holy grail. Even finding an STC fragment for something as mundane as a slightly better combat knife can earn a tech-priest a planetary governorship.",
            ],
            "Orks": [
                "Ork technology is effectively junk, but it works largely because they collectively believe it should work. This latent gestalt psychic field is known as the 'Waaagh!'.",
                "Orks reproduce through fungal spores. When an Ork dies, or even just bleeds, it releases spores that will eventually grow into squigs, snotlings, gretchin, and eventually more Orks, making them nearly impossible to eradicate.",
                "Ork 'Squigs' come in countless bio-engineered varieties for every situation. There are Bomb-Squigs, Eating-Squigs, Medical-Squigs (used to sew wounds shut with their teeth), and even Hair-Squigs that Orks use as toupees.",
                "Ghazghkull Mag Uruk Thraka, the greatest living Ork Warboss, once had half his head blown off by a bolter round. A 'Painboy' replaced it with adamantium, accidentally jumpstarting his psychic connection to the Ork gods.",
                "To an Ork, colors have physical power. Red vehicles go faster, blue is lucky, yellow makes explosions bigger, and purple makes them invisible—after all, have you ever seen a purple Ork?",
                "An Ork Warboss named Tuska Daemon-Killa intentionally flew his Waaagh! into the Eye of Terror just to fight Daemons. Khorne was so entertained by this that he resurrects Tuska and his boyz every day to fight an eternal, glorious battle.",
                "The Ork economy is entirely based on 'Teef' (teeth). Because Ork teeth naturally decay over time, it is impossible to hoard wealth, completely eliminating inflation and creating a perfectly stable, if violent, economic system.",
                "During the War of the Beast, an Ork Warboss grew so massive and intelligent that his Waaagh! possessed 'Attack Moons' with gravity weapons, and his Ork diplomats actually spoke perfect High Gothic to threaten Terra.",
            ],
            "Chaos & The Warp": [
                "The Alpha Legion's Primarch, Alpharius, supposedly had an identical twin brother named Omegon. To this day, due to their masterful use of deception and espionage, no one truly knows whose side they are on.",
                "The birth of Slaanesh, the Chaos God of Excess, created a massive tear in reality known as the Eye of Terror and instantly wiped out trillions of Aeldari, causing the fall of their ancient empire.",
                "Khorne, the Chaos God of Blood and War, does not care whose blood is spilled, only that it flows. His followers will happily slaughter each other in his name if there are no enemies left to fight.",
                "The Warp is a mirror dimension formed by the collective emotions and thoughts of all sentient beings. Every act of rage, hope, despair, and excess in the real world directly feeds the entities of the Immaterium.",
                "Grandfather Nurgle, the Chaos God of Disease, genuinely loves his followers. He doesn't see his plagues as curses, but as 'gifts' of life, and his daemons are almost always joyful and affectionate.",
                "Tzeentch is the Chaos God of magic, change, and manipulation. His schemes are so impossibly complex and contradictory that he will often intentionally sabotage his own plans just to see what happens.",
                "Slaanesh's Noise Marines use weapons called Sonic Blasters that fire weaponized sound. The screeching noise is so loud and discordant that it causes enemies' internal organs to rupture and their bones to shatter.",
                "Before they were mindless berserkers, the World Eaters Legion implanted themselves with the 'Butcher's Nails', archeotech brain implants that cause agonizing pain unless the host is actively killing someone.",
                "Vashtorr the Arkifane is a newly risen entity of the Warp, a demigod of chaotic invention and corrupted technology. He seeks to become a fifth Chaos God by gathering ancient artifacts to forge terrifying superweapons.",
            ],
            "Tyranids & Genestealers": [
                "The Tyranid Hive Mind doesn't just consume biomass; its sheer presence creates a 'Shadow in the Warp,' a psychic static that drives psykers mad and cuts off entire star systems from astropathic communication and travel.",
                "Genestealer Cults spend generations secretly infecting a planet's population and infiltrating its governments. They believe they are preparing for the arrival of 'Star Saviors', only to be eagerly consumed by the Tyranid Hive Fleet they attracted.",
                "When the Tyranids conquer a world, they don't just eat the people. They consume all flora, fauna, oceans, and even the atmosphere itself, leaving nothing but a dead, barren rock floating in space.",
                "The galaxy is currently facing the Fourth Tyrannic War. Hive Fleet Leviathan has launched an unprecedented assault from the Galactic West, attacking from beneath the galactic plane and pushing directly towards Terra.",
            ],
            "Necrons": [
                "The terrifying Necrons were once a flesh-and-blood race called the Necrontyr. Desperate for immortality and victory in war, they traded their souls to the C'tan (Star Gods), becoming soulless machines of living metal.",
                "Trazyn the Infinite, the kleptomaniac Necron Overlord, has a massive museum on Solemnace. Among his exhibits, he secretly possesses a perfect, uncorrupted clone of the Primarch Fulgrim.",
                "The Necrons are currently building the 'Pariah Nexus', a vast region of space where their Blackstone pylons completely sever the Warp from realspace. Any humans entering it suffer the 'Stilling', becoming mindless, soulless husks.",
            ],
            "Aeldari, T'au & Other Xenos": [
                "Commorragh, the Dark City of the Drukhari (Dark Eldar), is not a planet. It is a massive, impossibly complex realm hidden deep within the Webway, powered by stolen suns and feeding on the pain of millions of slaves.",
                "The Leagues of Votann rely on ancient, incredibly powerful AI mainframes known as Votann to guide their civilization, a practice that the Imperium would consider the highest form of tech-heresy.",
                "The Webway is a labyrinthine network of ancient tunnels between reality and the Warp. Built millions of years ago by the Old Ones, it is now primarily used by the Aeldari to travel safely without risking demonic possession.",
                "The T'au Empire utilizes the 'Kroot', a carnivorous mercenary race. The Kroot are biologically capable of absorbing the DNA of whatever they eat, directing their own evolution based on their diet.",
                "The Supreme Ethereal of the T'au Empire, Aun'Va, was assassinated by an Imperial Culexus Assassin years ago. To prevent mass panic, the T'au leadership replaced him with an AI hologram, keeping his death a complete secret.",
            ],
            "Ancient Lore": [
                "Long before the Imperium, humanity had a golden age relying on advanced AI called the 'Men of Iron'. These machines eventually rebelled, causing a galaxy-wide war so devastating that it made the Horus Heresy look like a skirmish.",
                "The 'War in Heaven' was a conflict fought 60 million years ago between the Old Ones and the Necrontyr. The weapons used were so cataclysmic that they permanently broke the calm dimension of the Immaterium, creating the chaotic Warp we know today.",
            ]
        }
        
        # Μετατρέπουμε το dictionary σε μία ενιαία λίστα για να τρέχει στο Loop
        self.flat_lore = []
        for category, facts in self.lore_categories.items():
            for fact in facts:
                self.flat_lore.append((category, fact))
                
        # Ταξινομούμε την λίστα. 
        # Έτσι εξασφαλίζουμε ότι, όσες φορές κι αν γίνει επανεκκίνηση το bot, η σειρά των facts θα είναι η ίδια.
        self.flat_lore.sort(key=lambda x: x[1])

        # Το ID του καναλιού όπου θα στέλνει το Lore
        self.daily_lore_channel_id = 1416479181860110436
        # Ξεκινάμε την λούπα αυτόματα μόλις φορτώσει το bot
        self.daily_lore.start()

    # Συνάρτηση για να κλείνει η λούπα αν κλείσουμε το bot
    def cog_unload(self):
        self.daily_lore.cancel()

# --- ΕΝΤΟΛΗ: HELP ---
    @commands.command(name="help")
    async def custom_help(self, ctx):
        embed = discord.Embed(
            title="📜 **Αρχείο Εντολών (Help)**",
            description="Όλες οι διαθέσιμες εντολές του συστήματος και η λειτουργία τους:",
            color=discord.Color.from_rgb(0, 102, 204)
        )

        # Κατηγορία 1: Leveling & XP
        embed.add_field(
            name="📊 **Στατιστικά & Εμπειρία**",
            value=(
                "**`!rank [@user]`** - Εμφανίζει το Level & XP σου ή ενός άλλου παίκτη.\n"
                "**`!toprank`** - Το Leaderboard με τους 9 καλύτερους βετεράνους.\n"
                "**`!pray`** - Ημερήσια προσευχή για bonus XP."
            ),
            inline=False
        )

        # Κατηγορία 2: Tabletop & Match Tracking
        embed.add_field(
            name="⚔️ **Καταγραφή Μαχών & Factions**",
            value=(
                "**`!stats [Faction]`** - Win Rate & ιστορικό αγώνων ενός Faction.\n"
                "**`!top`** - Leaderboard με τα 5 καλύτερα Factions του server."
            ),
            inline=False
        )

        # Κατηγορία 3: Βοηθήματα 40k
        embed.add_field(
            name="🎲 **Warhammer 40k Εργαλεία**",
            value=(
                "**`!math [A] [BS] [S] [T]`** - Υπολογίζει τις πιθανότητες στο Mathhammer.\n"
                "**`!quote`** - Στέλνει μια τυχαία ατάκα από το lore του 40k.\n"
                "**`!trivia`** - Ξεκινάει ένα γρήγορο παιχνίδι 40k lore trivia."
            ),
            inline=False
        )

        # Κατηγορία 4: Fun & Memes
        embed.add_field(
            name="🤡 **Fun & Διάφορα**",
            value=(
                "**`!glorious`** - Στέλνει το Glorious MP3.\n"
                "**`!counter`** - Δείχνει πόσες φορές έχει ειπωθεί Η Φράση.\n"
                "**`!roll [αριθμός]`** - Ρίχνει ζάρια. Ιδανικό για να λύνετε διαφορές.\n"
                "**`!overwatch`** - Όταν τα λόγια δεν αρκούν, το bot φέρνει Flamers.\n"
                "**`!excuse`** - Το bot σου δίνει την τέλεια δικαιολογία.\n"
                "**`!sus [reply ή @user]`** - Δικάζει δημόσια όποιον στέλνει περίεργο περιεχόμενο."
            ),
            inline=False
        )

        embed.set_footer(text=f"Αίτημα από τον {ctx.author.display_name} - The Emperor Protects.")
        await ctx.send(embed=embed)

    # --- ΕΝΤΟΛΗ: ADMIN HELP ---
    @commands.command(name="adminhelp")
    @commands.check_any(
        commands.has_permissions(administrator=True),
        commands.has_any_role("E.K.D.")
    )
    async def admin_help(self, ctx):
        embed = discord.Embed(
            title="🛑 **Inquisitorial Vault (Admin Commands)**",
            description="Εντολές αυστηρά περιορισμένες για το High Command του Server.",
            color=discord.Color.dark_red()
        )

        embed.add_field(
            name="⚙️ **Σύστημα & Δεδομένα**",
            value=(
                "**`!setlevel [@user] [level]`** - Ορίζει χειροκίνητα το Level κάποιου παίκτη.\n"
                "**`!report [FactionA] vs [FactionB]`** - Καταγράφει το αποτέλεσμα μιας μάχης στη ΒΔ."
            ),
            inline=False
        )

        embed.add_field(
            name="🔨 **Moderation & Ποινές**",
            value=(
                "**`!void [@user]`** - Στέλνει τον χρήστη στο Void.\n"
                "*Soon*"
            ),
            inline=False
        )

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/850011185314267177/1528866771438931968/ilviymd6q1xe1.jpg?ex=6a5fdba3&is=6a5e8a23&hm=a746ff54b008d6871af13ad636f1dd3f99cdd2e5ecd2ce77b2761b7c2e8f6e91&")
        embed.set_footer(text=f"Inquisitor {ctx.author.display_name}, authorization accepted.")
        
        await ctx.send(embed=embed)

    # --- ERROR HANDLER ΓΙΑ ΤΟ ADMIN HELP ---
    @admin_help.error
    async def admin_help_error(self, ctx, error):
        if isinstance(error, commands.CheckAnyFailure) or isinstance(error, commands.MissingPermissions):
            await ctx.send("⛔ **HERESY DETECTED!** Δεν έχεις το Inquisitorial Clearance για αυτή την εντολή.")

    # --- ΕΝΤΟΛΗ: GLORIOUS (MP3) ---
    @commands.command(name="glorious")
    async def send_glorious_mp3(self, ctx):
        try:
            audio_file = discord.File("glorious.mp3")
            await ctx.send("🎶 **GLORIOUS MELEE COMBAT!**", file=audio_file)
        except FileNotFoundError:
            await ctx.send("❌ Error: Το αρχείο `glorious.mp3` δεν βρέθηκε στα αρχεία του bot!")
        
    # --- ΕΝΤΟΛΗ: ΖΑΡΙΑ ---
    @commands.command(name="roll")
    async def roll_dice(self, ctx, amount: int = 1):  
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
    async def send_quote(self, ctx):  
        if self.current_index >= len(self.quotes):
            random.shuffle(self.quotes)
            self.current_index = 0

        await ctx.send(f"📜 {self.quotes[self.current_index]}")
        self.current_index += 1

    # --- ΕΝΤΟΛΗ: OVERWATCH ---
    @commands.command(name="overwatch")
    async def overwatch_gif(self, ctx):  
        if os.path.exists("flamer.gif"):
            with open("flamer.gif", "rb") as f:
                picture = discord.File(f)
            await ctx.send(f"🔥 **OVERWATCH!** Ο **{ctx.author.display_name}** ανάβει τα Flamers!", file=picture)
        else:
            await ctx.send("❌ Σφάλμα: Δεν βρέθηκε το αρχείο `flamer.gif`!")

    # --- ΕΝΤΟΛΗ: EXCUSE ---
    @commands.command(name="excuse")
    async def defeat_excuse(self, ctx):
        if self.current_excuse_index >= len(self.excuses):
            random.shuffle(self.excuses)
            self.current_excuse_index = 0
            
        chosen_excuse = self.excuses[self.current_excuse_index]
        self.current_excuse_index += 1
        
        await ctx.send(f"«*{chosen_excuse}*»")
        
    # --- ΕΝΤΟΛΗ: MATHHAMMER ---
    @commands.command(name="math")
    async def mathhammer(self, ctx, attacks: int = 0, skill: int = 0, strength: int = 0, toughness: int = 0):
        if attacks <= 0 or skill < 2 or skill > 6 or strength <= 0 or toughness <= 0:
            await ctx.send("❌ Λάθος! Δοκίμασε: `!math [A] [BS/WS] [S] [T]`")
            return

        hit_chance = (7 - skill) / 6.0
        expected_hits = attacks * hit_chance
        
        if strength >= toughness * 2:
            wound_target = 2
        elif strength > toughness:
            wound_target = 3
        elif strength == toughness:
            wound_target = 4
        elif strength * 2 <= toughness:
            wound_target = 6
        else: 
            wound_target = 5
            
        wound_chance = (7 - wound_target) / 6.0
        expected_wounds = expected_hits * wound_chance

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
        if self.current_trivia_index >= len(self.trivia_questions):
            random.shuffle(self.trivia_questions)
            self.current_trivia_index = 0
            
        q_data = self.trivia_questions[self.current_trivia_index]
        self.current_trivia_index += 1
        
        await ctx.send(
            f"🧠 **Warhammer 40k Trivia!** 🧠\n"
            f"Έχετε **30 sec** να γράψετε τη σωστή απάντηση!\n\n"
            f"**Question:** {q_data['q']}"
        )
        
        def check(m):
            if m.channel != ctx.channel or m.author.bot:
                return False
            user_ans = m.content.lower().strip()
            return any(correct_ans in user_ans for correct_ans in q_data['a'])
            
        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            correct_answers = " / ".join(q_data['a']).title()
            await ctx.send(f"⏳ Τέλος χρόνου! Κανείς δεν βρήκε την απάντηση.\nΤο σωστό ήταν: **{correct_answers}**.")
        else:
            await ctx.send(f"🎉 Ο **{msg.author.display_name}**! Έδωσε τη σωστή απάντηση!")

    # --- ΕΝΤΟΛΗ: SUS (ANTI-WEIRD CONTENT) ---
    @commands.command(name="sus")
    async def call_out_sus(self, ctx, target: discord.Member = None):
        
        # 1. Ελέγχουμε αν η εντολή γράφτηκε ως "Reply" σε κάποιο μήνυμα
        replied_msg = None
        if ctx.message.reference and ctx.message.reference.message_id:
            try:
                replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                target = replied_msg.author # Ο στόχος γίνεται αυτόματα αυτός που έγραψε το περίεργο μήνυμα!
            except discord.NotFound:
                pass

        # 2. Αν δεν υπάρχει ούτε reply ούτε @tag, βγάζουμε σφάλμα
        if not target:
            await ctx.send("❌ Πρέπει να κάνεις **reply** ή tag κάποιον")
            return

        # 3. Λίστα με μηνύματα
        sus_messages = [
            f"🚨 Alert! The content posted by **{target.display_name}** has exceeded acceptable Cringe levels.",
            f"📸 Caught in 4K, **{target.display_name}**! Your digital footprint is ruined.",
            f"🛑 Someone take the keyboard away from **{target.display_name}**, please.",
            f"🤨 **{target.display_name}**, what exactly are our eyes witnessing right now?",
            f"🚓 Internet Police? Yes, **{target.display_name}** struck again."
        ]
        
        chosen_message = random.choice(sus_messages)
        sus_gif = "https://tenor.com/view/rock-one-eyebrow-raised-rock-staring-the-rock-gif-22113367"
        
        # 4. Στέλνουμε πρώτα το κείμενο (σαν reply αν υπάρχει)
        if replied_msg:
            await ctx.send(chosen_message, reference=replied_msg)
        else:
            await ctx.send(chosen_message)
            
        # 5. Στέλνουμε το GIF σε 2ο μήνυμα για να είναι καθαρό
        await ctx.send(sus_gif)
            
    # --- ΕΝΤΟΛΗ: VOID (ENHANCED TORTURE EDITION + ANTI-SPAM) ---
    @commands.command(name="void")
    async def send_to_void(self, ctx, target: discord.Member):
        
        # --- ANTI-SPAM LOCK ---
        # Ελέγχουμε αν το Void λειτουργεί ήδη
        if getattr(self, 'void_active', False):
            await ctx.send("⏳ **The Void is currently occupied!**")
            return
            
        # Κλειδώνουμε την εντολή για να μην μπει άλλος
        self.void_active = True 

        try:
            # IDs των ΡΟΛΩΝ
            ALLOWED_ROLE_IDS = [802082482320703489]
            
            # IDs συγκεκριμένων ΧΡΗΣΤΩΝ
            ALLOWED_USER_IDS = [994930770542084227, 225171492734894080]

            # Ελέγχει αν ο χρήστης έχει τον Ρόλο ή αν το User ID του είναι στη λίστα
            has_role_perm = any(role.id in ALLOWED_ROLE_IDS for role in ctx.author.roles)
            has_user_perm = ctx.author.id in ALLOWED_USER_IDS

            # Αν δεν έχει τίποτα από τα δύο τρώει πόρτα
            if not (has_role_perm or has_user_perm):
                await ctx.send("❌ Δεν έχεις την εξουσιοδότηση της Ιεράς Εξέτασης για να ανοίξεις το Void!")
                return

            # Έλεγχος στόχου (Ασυλία)
            if target.id in [522869870178729985, 1503484130560839772]: 
                await ctx.reply("https://tenor.com/view/nuh-uh-nuh-uh-scout-tf2-gif-12750436057634665505")
                return

            VOID_THREAD_ID = 1512544435508871208  
            
            try:
                thread = await self.bot.fetch_channel(VOID_THREAD_ID)
            except discord.NotFound:
                await ctx.send("❌ Error: Δεν βρέθηκε το Void Thread! Έλεγξε το ID.")
                return

            await ctx.send(f"⚠️ Ο **{ctx.author.display_name}** άνοιξε την πύλη!\nΟ **{target.display_name}** ρίχνεται στο Void για να μείνει μόνος με τους Custodes...<:Custode:1439332561468920132>\n-# 17.5 Seconds")

            try:
                # 1. Προσθήκη στο Thread
                await thread.add_user(target)
                
                # 2. Το Προσωπικό Μήνυμα (DM) της Ιεράς Εξέτασης
                #try:
                #await target.send(f"👁️ **THE INQUISITION SEES YOU.**\nΕξορίστηκες στο Void από τον {ctx.author.display_name}. Μετάνιωσε για τις αμαρτίες σου!")
                #except discord.Forbidden:
                #pass # Αν έχει κλειστά τα DMs το αγνοούμε
                
                # 3. Τα GIFs
                custodes_gifs = [
                    "https://tenor.com/view/40k-warhammer-tasty-rainbow-sons-gaming-gif-17304578",
                    "https://tenor.com/view/tts-custodes-pillar-men-gif-15519847",
                    "https://tenor.com/view/oh-no-40k-40k-tts-tts-if-the-emperor-had-a-text-to-speech-device-gif-25047215",
                    "https://tenor.com/view/emperor-text-to-speech-custodes-erogenous-metaphors-gif-27361743",
                    "https://tenor.com/view/garnoludek-tts-wh40k-gif-20988900"
                ]
                
                # 4. Τα διαφορετικά μηνύματα
                annoying_phrases = [
                    "**RENEW YOUR OATH TO THE EMPEROR!**",
                    "**DO NOT HIDE, HERETIC!**",
                    "**HEAR THE HYMNS OF THE CUSTODES!**",
                    "**REPENT! REPENT! REPENT!**",
                    "**YOU CANNOT ESCAPE THEIR WRATH!**"
                ]
                
                # 5. Η Λούπα
                for i in range(len(custodes_gifs)):
                    # Κύριο μήνυμα με ping και GIF
                    await thread.send(f"# <@{target.id}> {annoying_phrases[i]}\n[!]({custodes_gifs[i]}) <:Hammer:1416864558869516423>")
                    await asyncio.sleep(2.5)
                    
                    # Γρήγορο ping ενδιάμεσα για έξτρα notification sound!
                    await thread.send(f"Wake up <@{target.id}>!")
                    await asyncio.sleep(0.5) 
                    
                await asyncio.sleep(2.5)
                    
                # 6. Αφαίρεση του Χρήστη
                try:
                    await thread.remove_user(target)
                except discord.Forbidden:
                    pass
                    
                # 7. Εκκαθάριση - Όριο 15 μηνύματα
                try:
                    await thread.purge(limit=15)
                except discord.Forbidden:
                    pass
                    
                await ctx.send(f"--> Ο **{target.display_name}** επέστρεψε από το Void. Ελπίζουμε να πήρε το μάθημά του. <:Troll:1416864472932421782>")
                
            except discord.errors.Forbidden:
                await ctx.send("❌ Error: Το bot απέτυχε να βάλει τον παίκτη στο Thread.")
                
        finally:
            # RELEASE LOCK
            self.void_active = False
            
    # --- Η ΛΟΥΠΑ ΠΟΥ ΤΡΕΧΕΙ ΚΑΘΕ ΜΕΡΑ ---
    target_time = datetime.time(hour=14, minute=0, tzinfo=datetime.timezone.utc)

    @tasks.loop(time=target_time)
    async def daily_lore(self):
        channel = self.bot.get_channel(self.daily_lore_channel_id)
        if channel:
            # Υπολογισμός του απόλυτου αριθμού της σημερινής ημερομηνίας
            today_number = datetime.date.today().toordinal()

            # Διαιρούμε τη σημερινή μέρα με το σύνολο των facts.
            # Το υπόλοιπο είναι ο δείκτης του σημερινού μας Fact!
            current_index = today_number % len(self.flat_lore)
            
            category, fact = self.flat_lore[current_index]

            next_run = self.daily_lore.next_iteration
            if next_run:
                timestamp = int(next_run.timestamp())
                next_timer_str = f"\n\n-# ⏳ Next archive unlocks: <t:{timestamp}:R>"
            else:
                next_timer_str = ""

            await channel.send(
                f"📜 **Imperial Archive: Daily Lore Fact** 📜\n"
                f"-# Category: **{category}**\n\n"
                f"*{fact}*{next_timer_str}"
            )

    @daily_lore.before_loop
    async def before_daily_lore(self):
        await self.bot.wait_until_ready()
            
async def setup(bot):
    await bot.add_cog(FunCommands(bot))