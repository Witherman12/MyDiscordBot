"""
========================================
ΑΡΧΕΙΟ: roles.py (Cogs)
ΠΕΡΙΓΡΑΦΗ: Live Panel & Persistent Button Role Assignment
========================================
"""

import discord
from discord.ext import commands
import os
import pymongo
import certifi

MONGO_URI = os.environ.get("MONGODB_URI")
client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True)
db = client["GloriousDatabase"]
settings_col = db["Settings"]

# ==========================================
# ΔΕΔΟΜΕΝΑ ΡΟΛΩΝ
# Εδώ προσθέτεις νέους ρόλους πανεύκολα! 
# Δεν χρειάζεται καν να βάλεις emoji αν δεν θες.
# ==========================================
FACTION_ROLES = {
    "General": {
        "Warhammer": 1416870277689901109
    },
    "Imperium": {
        "Admech": 1455895430524043355,
        "Astra Militarum": 1439285439780487310,
        "Custodes": 1439280511309713489,
        "Dark Angels": 1510258331992985751,
        "Knights": 1439281880573939712,
        "Salamanders": 1458223310247563345,
        "Sisters of Battle": 1545809435354730547,
        "Space Marines (All)": 1520707256662888488,
        "Ultramarines": 1439255972970233939,
        "White Scars": 1492131141166301265
    },
    "Chaos": {
        "Black Legion": 1495072660634210518,
        "Death Guard": 1439256956081799210,
        "Thousand Sons": 1505870287923843092
    },
    "Xenos": {
        "Aeldari": 1501194059052744855,
        "Drukhari": 1450233943357001801,
        "Necrons": 1439280799017992354,
        "Orks": 1439256437317570590,
        "Tau": 1450231929705332837,
        "Tyranids": 1545479655992328333
    }
}

EMOJIS = {
    "Warhammer": "<:Warhammer_1:1416864475520438302>",
    "Admech": "<:AdeptusMechanicus:1455895386530254993>", 
    "Astra Militarum": "<:AstraMilitarum:1435349542768869578>", 
    "Custodes": "<:Custode:1439332561468920132>", 
    "Knights": "<:Knight:1439331932109279468>", 
    "Salamanders": "<:Salamander:1458223866634571907>", 
    "Sisters of Battle": "⚜️",
    "Space Marines (All)": "<:SpaceMarine:1520706897332670537>", 
    "White Scars": "🇲🇳", 
    "Dark Angels": "🗡️",
    "Ultramarines": "<:Ultramarine:1432413619567460522>",
    "Black Legion": "<:BlackLegion:1495073025660420212>", 
    "Death Guard": "<:DeathGuard:1439330955079717150>", 
    "Thousand Sons": "<:ThousandSons:1505870183666028574>",
    "Aeldari": "<:Aeldari:1501193876487274506>", 
    "Drukhari": "<:Drukhari:1543897513201901579>", 
    "Necrons": "<:Necron:1439333592802005174>", 
    "Orks": "<:Ork:1416864462798983228>",
    "Tau": "<:Tau:1520707105105907753>",
    "Tyranids": "<:Tyranid:1545493790318661662>"
}

# ==========================================
# UI COMPONENTS (Buttons)
# ==========================================
def get_style_for_category(category: str):
    """Αντιστοιχεί χρώματα ανάλογα το Lore."""
    if category == "Imperium":
        return discord.ButtonStyle.primary  # Μπλε
    elif category == "Chaos":
        return discord.ButtonStyle.danger   # Κόκκινο
    elif category == "Xenos":
        return discord.ButtonStyle.success  # Πράσινο
    return discord.ButtonStyle.secondary    # Γκρι

class RoleButton(discord.ui.Button):
    def __init__(self, label: str, role_id: int, style: discord.ButtonStyle, emoji: str = None):
        super().__init__(
            label=label,
            style=style,
            custom_id=f"role_btn_{role_id}", # Το custom_id κάνει τα κουμπιά persistent (δεν χαλάνε στο restart)
            emoji=emoji
        )
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("❌ Error: Αυτός ο ρόλος διεγράφη ή δεν βρέθηκε.", ephemeral=True)
            return

        # Toggle Logic: Αν το έχει, του το βγάζουμε. Αν δεν το έχει, του το δίνουμε.
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"➖ Σου αφαιρέθηκε ο ρόλος: **{role.name}**", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"➕ Πήρες τον ρόλο: **{role.name}**", ephemeral=True)

class RoleCategoryView(discord.ui.View):
    def __init__(self, category: str, roles_dict: dict):
        super().__init__(timeout=None) # Timeout None σημαίνει ότι δεν λήγει ΠΟΤΕ
        style = get_style_for_category(category)
        
        for name, role_id in roles_dict.items():
            # Αν υπάρχει emoji στο dictionary, το βάζουμε. Αν όχι, μπαίνει μόνο κείμενο αυτόματα!
            emoji_str = EMOJIS.get(name) 
            self.add_item(RoleButton(label=name, role_id=role_id, style=style, emoji=emoji_str))

# ==========================================
# ΚΛΑΣΗ ΣΥΣΤΗΜΑΤΟΣ (COG)
# ==========================================
class RolesSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def generate_panel_embed(self, guild):
        embed = discord.Embed(
            title="📊 **Live Faction Census**",
            description="*Επίσημη καταμέτρηση. Ενημερώνεται σε πραγματικό χρόνο.*",
            color=discord.Color.from_rgb(200, 160, 40)
        )
        
        for category, roles in FACTION_ROLES.items():
            text = ""
            for name, role_id in roles.items():
                role = guild.get_role(role_id)
                count = len(role.members) if role else 0
                emoji = EMOJIS.get(name, "▪️")
                text += f"{emoji} **{name}:** {count}\n"
                
            is_inline = False if category == "General" else True
            embed.add_field(name=f"**{category}**", value=text, inline=is_inline)
            
        embed.set_footer(text="To Departmento Munitorum παρακολουθεί.")
        return embed

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles == after.roles: return
            
        panel_data = settings_col.find_one({"_id": "live_panel"})
        if not panel_data: return
        
        channel = self.bot.get_channel(panel_data["channel_id"])
        if not channel: return
        
        try:
            msg = await channel.fetch_message(panel_data["message_id"])
            await msg.edit(embed=self.generate_panel_embed(after.guild))
        except:
            pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        warhammer_role_id = 1416870277689901109
        role = member.guild.get_role(warhammer_role_id)
        if role:
            await member.add_roles(role)

    # ----------------------------------------------------
    # Η ΕΝΤΟΛΗ ΠΟΥ ΣΤΗΝΕΙ ΟΛΟ ΤΟ ΜΕΝΟΥ
    # ----------------------------------------------------
    @commands.command(name="setup_roles")
    @commands.has_permissions(administrator=True)
    async def setup_roles(self, ctx):
        await ctx.message.delete()
        
        # 1. Στέλνουμε/Ανανεώνουμε το Live Panel καταμέτρησης
        panel_embed = self.generate_panel_embed(ctx.guild)
        panel_msg = await ctx.send(embed=panel_embed)
        
        settings_col.update_one(
            {"_id": "live_panel"},
            {"$set": {"message_id": panel_msg.id, "channel_id": ctx.channel.id}},
            upsert=True
        )
        
        # 2. Στέλνουμε τα μενού με τα κουμπιά (Ένα ξεχωριστό μήνυμα ανά Faction)
        await ctx.send("https://cdn.discordapp.com/attachments/1523030976782143645/1546995182992359424/2026-09-09_002348.png?ex=6aa1cf09&is=6aa07d89&hm=f1eb7a5afb66d3059262aec2b74fb8cac266c041df02e6f59cca745d09fb61b1&")
        await ctx.send("## 📜 ARMY SELECTION\n*Press the buttons below to get or remove your roles.*")

        for category, roles in FACTION_ROLES.items():
            if not roles: continue
            
            view = RoleCategoryView(category, roles)
            
            # Δημιουργία ενός mini embed για το κάθε faction ώστε να φαίνεται καθαρό
            color = discord.Color.blue() if category == "Imperium" else (discord.Color.red() if category == "Chaos" else discord.Color.green())
            if category == "General": color = discord.Color.dark_grey()
                
            menu_embed = discord.Embed(title=f"🛡️ {category} Roles", color=color)
            await ctx.send(embed=menu_embed, view=view)

# Αυτό είναι σημαντικό για να μην "πεθαίνουν" τα κουμπιά στο restart
async def setup(bot):
    await bot.add_cog(RolesSystem(bot))
    
    # Διαβάζει ξανά όλα τα views στο boot για να ξέρει το Discord ότι τα κουμπιά είναι ενεργά
    for category, roles in FACTION_ROLES.items():
        bot.add_view(RoleCategoryView(category, roles))