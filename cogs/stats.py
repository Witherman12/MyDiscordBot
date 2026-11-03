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
# ΛΙΣΤΑ ΓΙΑ ΤΙΣ ΠΡΟΤΑΣΕΙΣ (AUTOCOMPLETE)
# ==========================================
FACTION_CHOICES = [
    app_commands.Choice(name="Adepta Sororitas", value="⚜️"),
    app_commands.Choice(name="Adeptus Custodes", value="<:Custode:1439332561468920132>"),
    app_commands.Choice(name="Adeptus Mechanicus", value="<:AdeptusMechanicus:1455895386530254993>"),
    app_commands.Choice(name="Aeldari", value="<:Aeldari:1501193876487274506>"),
    app_commands.Choice(name="Astra Militarum", value="🪖"),
    app_commands.Choice(name="Chaos Daemons", value="<:Daemons:1563572127314223225>"),
    app_commands.Choice(name="Chaos Space Marines", value="<:BlackLegion:1495073025660420212>"),
    app_commands.Choice(name="Dark Angels", value="🗡️"),
    app_commands.Choice(name="Death Guard", value="<:DeathGuard:1439330955079717150>"),
    app_commands.Choice(name="Drukhari", value="<:Drukhari:1543897513201901579>"),
    app_commands.Choice(name="Emperor's Children", value="<:Mogrim:1465674684690337927>"),
    app_commands.Choice(name="Imperial Knights", value="<:Knight:1439331932109279468>"),
    app_commands.Choice(name="Leagues of Votann", value="<:Votann:1567263378626322574>"),
    app_commands.Choice(name="Necrons", value="<:Necron:1439333592802005174>"),
    app_commands.Choice(name="Orks", value="<:Ork:1416864462798983228>"),
    app_commands.Choice(name="Salamanders", value="<:Salamander:1458223866634571907>"),
    app_commands.Choice(name="Space Marines", value="<:SpaceMarine:1520706897332670537>"),
    app_commands.Choice(name="T'au Empire", value="<:Tau:1520707105105907753>"),
    app_commands.Choice(name="Thousand Sons", value="<:ThousandSons:1505870183666028574>"),
    app_commands.Choice(name="Tyranids", value="<:Tyranid:1545493790318661662>"),
    app_commands.Choice(name="Ultramarines", value="<:Ultramarine:1432413619567460522>"),
    app_commands.Choice(name="White Scars", value="🇲🇳")
]

# Αυτό εξασφαλίζει ότι το input του χρήστη 
# (αν δεν κάνει κλικ σε πρόταση και απλά γράψει κείμενο)
# θα μετατραπεί σε emoji ID, εφόσον υπάρχει στη λίστα.
VALID_VALUES = {choice.value for choice in FACTION_CHOICES}

async def faction_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    # Φιλτράρει τη λίστα στρατών καθώς πληκτρολογεί ο χρήστης
    return [
        choice for choice in FACTION_CHOICES
        if current.lower() in choice.name.lower()
    ][:25]


class MatchTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    # ----------------------------------------------------
    # /report
    # ----------------------------------------------------
    @app_commands.command(name="report", description="Κατάγραψε το αποτέλεσμα ενός αγώνα 40k")
    @app_commands.describe(
        faction_a="WINNER (Επίλεξε από τη λίστα)",
        faction_b="LOSER (Επίλεξε από τη λίστα)",
        is_tie="Επίλεξε True αν ο αγώνας έληξε ισοπαλία"
    )
    @app_commands.autocomplete(faction_a=faction_autocomplete, faction_b=faction_autocomplete)
    async def report_match(self, interaction: discord.Interaction, faction_a: str, faction_b: str, is_tie: bool = False):
        
        # Αν κάποιος έγραψε χειροκίνητα άκυρο κείμενο (π.χ. asdads) και δεν διάλεξε από τη λίστα
        if faction_a not in VALID_VALUES:
            await interaction.response.send_message(f"❌ Παρακαλώ επίλεξε τον 1ο στρατό **από τη λίστα** που εμφανίζεται όταν πληκτρολογείς.", ephemeral=True)
            return
        if faction_b not in VALID_VALUES:
            await interaction.response.send_message(f"❌ Παρακαλώ επίλεξε τον 2ο στρατό **από τη λίστα** που εμφανίζεται όταν πληκτρολογείς.", ephemeral=True)
            return

        if is_tie:
            factions_col.update_one({"name": faction_a}, {"$inc": {"ties": 1, "wins": 0, "losses": 0}}, upsert=True)
            factions_col.update_one({"name": faction_b}, {"$inc": {"ties": 1, "wins": 0, "losses": 0}}, upsert=True)
            await interaction.response.send_message(f"⚔️ Καταγράφηκε Ισοπαλία ανάμεσα σε {faction_a} και {faction_b}!", ephemeral=False)
        else:
            factions_col.update_one({"name": faction_a}, {"$inc": {"wins": 1, "losses": 0, "ties": 0}}, upsert=True)
            factions_col.update_one({"name": faction_b}, {"$inc": {"losses": 1, "wins": 0, "ties": 0}}, upsert=True)
            await interaction.response.send_message(f"🏆 Καταγράφηκε Νίκη για {faction_a} εναντίον {faction_b}!", ephemeral=False)

    # ----------------------------------------------------
    # /stats
    # ----------------------------------------------------
    @app_commands.command(name="stats", description="Δες τα στατιστικά νικών ενός στρατού")
    @app_commands.describe(faction="Επίλεξε τον στρατό από τη λίστα")
    @app_commands.autocomplete(faction=faction_autocomplete)
    async def faction_stats(self, interaction: discord.Interaction, faction: str):
        
        if faction not in VALID_VALUES:
            await interaction.response.send_message("⚠️ Παρακαλώ επίλεξε έναν έγκυρο στρατό **από τη λίστα**.", ephemeral=True)
            return
        
        data = factions_col.find_one({"name": faction})
        if not data:
            await interaction.response.send_message(f"⚠️ Δεν βρέθηκαν αγώνες για {faction}.", ephemeral=True)
            return

        wins = data.get("wins", 0)
        losses = data.get("losses", 0)
        ties = data.get("ties", 0)
        total_games = wins + losses + ties
        win_rate = 0 if total_games == 0 else (wins / total_games) * 100

        await interaction.response.send_message(
            f"📊 **Στατιστικά:** {faction}\n"
            f"Win Rate: **{win_rate:.1f}%**\n"
            f"Wins: **{wins}** | Losses: **{losses}** | Ties: **{ties}**",
            ephemeral=False
        )

    # ----------------------------------------------------
    # /top
    # ----------------------------------------------------
    @app_commands.command(name="top", description="Το Top 5 των Factions με βάση τις νίκες")
    async def top_factions(self, interaction: discord.Interaction):
        if factions_col.count_documents({}) == 0:
            await interaction.response.send_message("⚠️ Δεν υπάρχουν ακόμα αγώνες στην ΒΔ!", ephemeral=True)
            return

        top_data = factions_col.find().sort("wins", -1).limit(5)
        message = "🏆 **Top 5 Factions** 🏆\n\n"
        
        for index, data in enumerate(top_data, 1):
            name = data.get("name", "Άγνωστο") 
            wins = data.get("wins", 0)
            losses = data.get("losses", 0)
            ties = data.get("ties", 0)
            
            total_games = wins + losses + ties
            win_rate = (wins / total_games * 100) if total_games > 0 else 0
            
            message += f"**{index}.** {name} - Wins: **{wins}** | WR: **{win_rate:.1f}%**\n"

        await interaction.response.send_message(message, ephemeral=False)
        
    # ----------------------------------------------------
    # /undo_report
    # ----------------------------------------------------
    @app_commands.command(name="undo_report", description="ΔΙΟΡΘΩΣΗ: Αφαίρεσε έναν αγώνα που καταγράφηκε κατά λάθος")
    @app_commands.describe(
        faction_a="Ο 1ος στρατός (από τη λίστα)",
        faction_b="Ο 2ος στρατός (από τη λίστα)",
        is_tie="Ήταν ισοπαλία;"
    )
    @app_commands.autocomplete(faction_a=faction_autocomplete, faction_b=faction_autocomplete)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def undo_report(self, interaction: discord.Interaction, faction_a: str, faction_b: str, is_tie: bool = False):
        
        if faction_a not in VALID_VALUES or faction_b not in VALID_VALUES:
            await interaction.response.send_message("❌ Πρέπει να επιλέξεις τους στρατούς από τη λίστα για να γίνει σωστά η αναίρεση.", ephemeral=True)
            return

        if is_tie:
            factions_col.update_one({"name": faction_a}, {"$inc": {"ties": -1}})
            factions_col.update_one({"name": faction_b}, {"$inc": {"ties": -1}})
            await interaction.response.send_message(f"⏪ Έγινε αναίρεση της Ισοπαλίας ανάμεσα σε {faction_a} και {faction_b}.", ephemeral=False)
        else:
            factions_col.update_one({"name": faction_a}, {"$inc": {"wins": -1}})
            factions_col.update_one({"name": faction_b}, {"$inc": {"losses": -1}})
            await interaction.response.send_message(f"⏪ Έγινε αναίρεση της Νίκης του {faction_a} εναντίον του {faction_b}.", ephemeral=False)

    # ----------------------------------------------------
    # /backup : Λήψη αντιγράφου ασφαλείας
    # ----------------------------------------------------
    @app_commands.command(name="backup", description="Κατεβάζει όλη τη βάση σε αρχείο (Μόνο Admins)")
    @app_commands.checks.has_permissions(administrator=True)
    async def backup_database(self, interaction: discord.Interaction):
        # Βάζουμε defer() γιατί το bot χρειαστεί λίγο χρόνο να διαβάσει τη βάση
        await interaction.response.defer(ephemeral=True)
        
        # Τραβάμε τα δεδομένα αφαιρώντας το "_id" γιατί δημιουργεί πρόβλημα στο JSON
        factions_data = list(factions_col.find({}, {"_id": 0}))
        
        # Μετατροπή σε όμορφο JSON κείμενο
        json_data = json.dumps({"Factions": factions_data}, indent=4, ensure_ascii=False)
        
        # Δημιουργία αρχείου στη μνήμη και αποστολή
        file = discord.File(fp=io.BytesIO(json_data.encode('utf-8')), filename="glorious_factions_backup.json")
        await interaction.followup.send("✅ Το αντίγραφο ασφαλείας είναι έτοιμο:", file=file)
        
async def setup(bot):
    await bot.add_cog(MatchTracker(bot))