import discord
from discord.ext import commands
from discord import app_commands
import os
import pymongo
import certifi

# Σύνδεση με τη βάση
MONGO_URI = os.environ.get("MONGODB_URI")
client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True)
db = client["GloriousDatabase"]
factions_col = db["Factions"]

# ==========================================
# ΣΥΣΤΗΜΑ ΠΡΟΣΤΑΣΙΑΣ & ΑΝΤΙΣΤΟΙΧΙΣΗΣ EMOJIS
# ==========================================
# Αριστερά: Τι μπορεί να πληκτρολογήσει ο χρήστης
# Δεξιά: Το επίσημο Emoji όπως είναι αποθηκευμένο στην MongoDB
FACTION_ALIASES = {
    # Space Marines (Γενικά)
    "space marines": "<:SpaceMarine:1520706897332670537>", "sm": "<:SpaceMarine:1520706897332670537>", 
    "<:SpaceMarine:1520706897332670537>": "<:SpaceMarine:1520706897332670537>",
    
    # Ultramarines
    "ultramarines": "<:Ultramarine:1432413619567460522>", "um": "<:Ultramarine:1432413619567460522>",
    "<:Ultramarine:1432413619567460522>": "<:Ultramarine:1432413619567460522>",
    
    # Dark Angels
    "dark angels": "🗡️", "da": "🗡️", "🗡️": "🗡️",
    
    # Salamanders
    "salamanders": "<:Salamander:1458223866634571907>", "sallies": "<:Salamander:1458223866634571907>",
    "<:Salamander:1458223866634571907>": "<:Salamander:1458223866634571907>",
    
    # White Scars
    "white scars": "🇲🇳", "ws": "🇲🇳", "🇲🇳": "🇲🇳",
    
    # Chaos / Black Legion
    "black legion": "<:BlackLegion:1495073025660420212>", "bl": "<:BlackLegion:1495073025660420212>",
    "chaos space marines": "<:BlackLegion:1495073025660420212>", "csm": "<:BlackLegion:1495073025660420212>",
    "<:BlackLegion:1495073025660420212>": "<:BlackLegion:1495073025660420212>",
    
    # Death Guard
    "death guard": "<:DeathGuard:1439330955079717150>", "dg": "<:DeathGuard:1439330955079717150>",
    "<:DeathGuard:1439330955079717150>": "<:DeathGuard:1439330955079717150>",
    
    # Thousand Sons
    "thousand sons": "<:ThousandSons:1505870183666028574>", "ts": "<:ThousandSons:1505870183666028574>", "tsons": "<:ThousandSons:1505870183666028574>",
    "<:ThousandSons:1505870183666028574>": "<:ThousandSons:1505870183666028574>",
    
    # Emperor's Children
    "emperor's children": "<:Mogrim:1465674684690337927>", "ec": "<:Mogrim:1465674684690337927>",
    "<:Mogrim:1465674684690337927>": "<:Mogrim:1465674684690337927>",
    
    # Daemons
    "chaos daemons": "<:Daemons:1563572127314223225>", "daemons": "<:Daemons:1563572127314223225>",
    "<:Daemons:1563572127314223225>": "<:Daemons:1563572127314223225>",
    
    # Xenos
    "orks": "<:Ork:1416864462798983228>", "ork": "<:Ork:1416864462798983228>",
    "<:Ork:1416864462798983228>": "<:Ork:1416864462798983228>",
    
    "tyranids": "<:Tyranid:1545493790318661662>", "nids": "<:Tyranid:1545493790318661662>",
    "<:Tyranid:1545493790318661662>": "<:Tyranid:1545493790318661662>",
    
    "necrons": "<:Necron:1439333592802005174>", "necron": "<:Necron:1439333592802005174>",
    "<:Necron:1439333592802005174>": "<:Necron:1439333592802005174>",
    
    "tau": "<:Tau:1520707105105907753>", "t'au": "<:Tau:1520707105105907753>", "t'au empire": "<:Tau:1520707105105907753>",
    "<:Tau:1520707105105907753>": "<:Tau:1520707105105907753>",
    
    "aeldari": "<:Aeldari:1501193876487274506>", "eldar": "<:Aeldari:1501193876487274506>",
    "<:Aeldari:1501193876487274506>": "<:Aeldari:1501193876487274506>",
    
    "drukhari": "<:Drukhari:1543897513201901579>", "dark eldar": "<:Drukhari:1543897513201901579>", "de": "<:Drukhari:1543897513201901579>",
    "<:Drukhari:1543897513201901579>": "<:Drukhari:1543897513201901579>",
    
    # Imperium
    "astra militarum": "<:AstraMilitarum:1435349542768869578>", "guard": "<:AstraMilitarum:1435349542768869578>", "imperial guard": "<:AstraMilitarum:1435349542768869578>",
    "<:AstraMilitarum:1435349542768869578>": "<:AstraMilitarum:1435349542768869578>",
    
    "adepta sororitas": "⚜️", "sisters of battle": "⚜️", "sob": "⚜️", "⚜️": "⚜️",
    
    "adeptus mechanicus": "<:AdeptusMechanicus:1455895386530254993>", "admech": "<:AdeptusMechanicus:1455895386530254993>",
    "<:AdeptusMechanicus:1455895386530254993>": "<:AdeptusMechanicus:1455895386530254993>",
    
    "adeptus custodes": "<:Custode:1439332561468920132>", "custodes": "<:Custode:1439332561468920132>",
    "<:Custode:1439332561468920132>": "<:Custode:1439332561468920132>",
    
    "imperial knights": "<:Knight:1439331932109279468>", "knights": "<:Knight:1439331932109279468>", "ik": "<:Knight:1439331932109279468>",
    "<:Knight:1439331932109279468>": "<:Knight:1439331932109279468>"
}

# Δημιουργεί αυτόματα ένα κρυφό λεξικό όπου όλα τα αριστερά κλειδιά είναι με μικρά γράμματα
FACTION_ALIASES_LOWER = {k.lower(): v for k, v in FACTION_ALIASES.items()}

def get_standard_faction(user_input):
    cleaned = user_input.strip().lower()
    return FACTION_ALIASES_LOWER.get(cleaned, None)

# ==========================================
# ΛΙΣΤΑ ΓΙΑ ΤΙΣ ΠΡΟΤΑΣΕΙΣ (AUTOCOMPLETE)
# ==========================================
FACTION_CHOICES = [
    app_commands.Choice(name="Space Marines", value="<:SpaceMarine:1520706897332670537>"),
    app_commands.Choice(name="Ultramarines", value="<:Ultramarine:1432413619567460522>"),
    app_commands.Choice(name="Dark Angels", value="🗡️"),
    app_commands.Choice(name="Salamanders", value="<:Salamander:1458223866634571907>"),
    app_commands.Choice(name="White Scars", value="🇲🇳"),
    app_commands.Choice(name="Chaos Space Marines", value="<:BlackLegion:1495073025660420212>"),
    app_commands.Choice(name="Death Guard", value="<:DeathGuard:1439330955079717150>"),
    app_commands.Choice(name="Thousand Sons", value="<:ThousandSons:1505870183666028574>"),
    app_commands.Choice(name="Emperor's Children", value="<:Mogrim:1465674684690337927>"),
    app_commands.Choice(name="Chaos Daemons", value="<:Daemons:1563572127314223225>"),
    app_commands.Choice(name="Orks", value="<:Ork:1416864462798983228>"),
    app_commands.Choice(name="Tyranids", value="<:Tyranid:1545493790318661662>"),
    app_commands.Choice(name="Necrons", value="<:Necron:1439333592802005174>"),
    app_commands.Choice(name="T'au Empire", value="<:Tau:1520707105105907753>"),
    app_commands.Choice(name="Aeldari", value="<:Aeldari:1501193876487274506>"),
    app_commands.Choice(name="Drukhari", value="<:Drukhari:1543897513201901579>"),
    app_commands.Choice(name="Astra Militarum", value="<:AstraMilitarum:1435349542768869578>"),
    app_commands.Choice(name="Adepta Sororitas", value="⚜️"),
    app_commands.Choice(name="Adeptus Mechanicus", value="<:AdeptusMechanicus:1455895386530254993>"),
    app_commands.Choice(name="Adeptus Custodes", value="<:Custode:1439332561468920132>"),
    app_commands.Choice(name="Imperial Knights", value="<:Knight:1439331932109279468>")
]

async def faction_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    """Φιλτράρει τη λίστα στρατών καθώς πληκτρολογεί ο χρήστης"""
    return [
        choice for choice in FACTION_CHOICES
        if current.lower() in choice.name.lower()
    ][:25]


class MatchTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ----------------------------------------------------
    # /report : Slash Command με κουτάκια
    # ----------------------------------------------------
    @app_commands.command(name="report", description="Κατάγραψε το αποτέλεσμα ενός αγώνα 40k")
    @app_commands.describe(
        faction_a="WINNER (π.χ. sm, orks, ή το ίδιο το emoji)",
        faction_b="LOSER",
        is_tie="Επίλεξε True αν ο αγώνας έληξε ισοπαλία"
    )
    @app_commands.autocomplete(faction_a=faction_autocomplete, faction_b=faction_autocomplete)
    async def report_match(self, interaction: discord.Interaction, faction_a: str, faction_b: str, is_tie: bool = False):
        fac1 = get_standard_faction(faction_a)
        fac2 = get_standard_faction(faction_b)

        # Μηνύματα σφάλματος ορατά ΜΟΝΟ σε αυτόν που έκανε το λάθος (ephemeral=True)
        if not fac1:
            await interaction.response.send_message(f"❌ Το `{faction_a}` δεν αναγνωρίστηκε. Βάλε σωστό ακρωνύμιο (π.χ. um, dg) ή το emoji.", ephemeral=True)
            return
        if not fac2:
            await interaction.response.send_message(f"❌ Το `{faction_b}` δεν αναγνωρίστηκε. Βάλε σωστό ακρωνύμιο (π.χ. ork) ή το emoji.", ephemeral=True)
            return

        # Καταγραφή στη Βάση με τα EMOJIS! (Δημόσιο μήνυμα)
        if is_tie:
            factions_col.update_one({"name": fac1}, {"$inc": {"ties": 1, "wins": 0, "losses": 0}}, upsert=True)
            factions_col.update_one({"name": fac2}, {"$inc": {"ties": 1, "wins": 0, "losses": 0}}, upsert=True)
            await interaction.response.send_message(f"⚔️ Καταγράφηκε Ισοπαλία ανάμεσα σε {fac1} και {fac2}!", ephemeral=False)
        else:
            factions_col.update_one({"name": fac1}, {"$inc": {"wins": 1, "losses": 0, "ties": 0}}, upsert=True)
            factions_col.update_one({"name": fac2}, {"$inc": {"losses": 1, "wins": 0, "ties": 0}}, upsert=True)
            await interaction.response.send_message(f"🏆 Καταγράφηκε Νίκη για {fac1} εναντίον {fac2}!", ephemeral=False)

    # ----------------------------------------------------
    # /stats : Δες στατιστικά με το Emoji
    # ----------------------------------------------------
    @app_commands.command(name="stats", description="Δες τα στατιστικά νικών ενός στρατού")
    @app_commands.describe(faction="Το όνομα ή ακρωνύμιο του στρατού (π.χ. custodes, UM)")
    @app_commands.autocomplete(faction=faction_autocomplete)
    async def faction_stats(self, interaction: discord.Interaction, faction: str):
        clean_name = get_standard_faction(faction)
        
        if not clean_name:
            await interaction.response.send_message(f"⚠️ Δεν αναγνωρίζω τον στρατό: `{faction}`.", ephemeral=True)
            return
        
        data = factions_col.find_one({"name": clean_name})
        if not data:
            await interaction.response.send_message(f"⚠️ Δεν βρέθηκαν αγώνες για {clean_name}.", ephemeral=True)
            return

        wins = data.get("wins", 0)
        losses = data.get("losses", 0)
        ties = data.get("ties", 0)
        total_games = wins + losses + ties
        win_rate = 0 if total_games == 0 else (wins / total_games) * 100

        await interaction.response.send_message(
            f"📊 **Στατιστικά:** {clean_name}\n"
            f"Win Rate: **{win_rate:.1f}%**\n"
            f"Wins: **{wins}** | Losses: **{losses}** | Ties: **{ties}**",
            ephemeral=False
        )

    # ----------------------------------------------------
    # /top : Βγάζει τα Top Factions και θα δείχνει απευθείας τα emojis!
    # ----------------------------------------------------
    @app_commands.command(name="top", description="Το Top 5 των Factions με βάση τις νίκες")
    async def top_factions(self, interaction: discord.Interaction):
        if factions_col.count_documents({}) == 0:
            await interaction.response.send_message("⚠️ Δεν υπάρχουν ακόμα αγώνες στην ΒΔ!", ephemeral=True)
            return

        top_data = factions_col.find().sort("wins", -1).limit(5)
        message = "🏆 **Top 5 Factions** 🏆\n\n"
        
        for index, data in enumerate(top_data, 1):
            name = data.get("name", "Άγνωστο") # Εδώ το name είναι ΄ήδη το emoji string!
            wins = data.get("wins", 0)
            losses = data.get("losses", 0)
            ties = data.get("ties", 0)
            
            total_games = wins + losses + ties
            win_rate = (wins / total_games * 100) if total_games > 0 else 0
            
            message += f"**{index}.** {name} - Wins: **{wins}** | WR: **{win_rate:.1f}%**\n"

        await interaction.response.send_message(message, ephemeral=False)
        
    # ----------------------------------------------------
    # /undo_report : Διόρθωση λάθους (Αφαίρεση στατιστικών)
    # ----------------------------------------------------
    @app_commands.command(name="undo_report", description="ΔΙΟΡΘΩΣΗ: Αφαίρεσε έναν αγώνα που καταγράφηκε κατά λάθος")
    @app_commands.describe(
        faction_a="Ο στρατός που είχε δηλωθεί ότι ΝΙΚΗΣΕ (ή 1ος στην ισοπαλία)",
        faction_b="Ο στρατός που είχε δηλωθεί ότι ΕΧΑΣΕ (ή 2ος στην ισοπαλία)",
        is_tie="Ήταν ισοπαλία;"
    )
    @app_commands.autocomplete(faction_a=faction_autocomplete, faction_b=faction_autocomplete)
    @app_commands.checks.has_permissions(manage_messages=True) # Μόνο Admin
    async def undo_report(self, interaction: discord.Interaction, faction_a: str, faction_b: str, is_tie: bool = False):
        fac1 = get_standard_faction(faction_a)
        fac2 = get_standard_faction(faction_b)

        if not fac1 or not fac2:
            await interaction.response.send_message("❌ Δεν αναγνωρίστηκαν οι στρατοί. Έλεγξε τα ονόματα.", ephemeral=True)
            return

        # Αφαιρούμε (-1) από τη βάση αντί να προσθέτουμε
        if is_tie:
            factions_col.update_one({"name": fac1}, {"$inc": {"ties": -1}})
            factions_col.update_one({"name": fac2}, {"$inc": {"ties": -1}})
            await interaction.response.send_message(f"⏪ Έγινε αναίρεση της Ισοπαλίας ανάμεσα σε {fac1} και {fac2}.", ephemeral=False)
        else:
            factions_col.update_one({"name": fac1}, {"$inc": {"wins": -1}})
            factions_col.update_one({"name": fac2}, {"$inc": {"losses": -1}})
            await interaction.response.send_message(f"⏪ Έγινε αναίρεση της Νίκης του {fac1} εναντίον του {fac2}.", ephemeral=False)

async def setup(bot):
    await bot.add_cog(MatchTracker(bot))