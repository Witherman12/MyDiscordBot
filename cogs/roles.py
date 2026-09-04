"""
========================================
ΑΡΧΕΙΟ: roles.py (Cogs)
ΠΕΡΙΓΡΑΦΗ: Live Panel Καταμέτρησης Ρόλων (Αυτόματο Update)
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

# CUSTOM EMOJIS (Μορφή: <:onoma:ID>)
EMOJIS = {
    "Warhammer": "<:Warhammer_1:1416864475520438302>",
    
    # --- IMPERIUM ---
    "Admech": "<:AdeptusMechanicus:1455895386530254993>", 
    "Astra Militarum": "<:AstraMilitarum:1435349542768869578>", 
    "Custodes": "<:Custode:1439332561468920132>", 
    "Knights": "<:Knight:1439331932109279468>", 
    "Salamanders": "<:Salamander:1458223866634571907>", 
    "Space Marines (All)": "<:SpaceMarine:1520706897332670537>", 
    "White Scars": "🇲🇳", 
    "Dark Angels": "🗡️", #custom: "<:DarkAngels:ΒΑΛΕ_ID>"
    "Ultramarines": "<:Ultramarine:1432413619567460522>",
    
    # --- CHAOS ---
    "Black Legion": "<:BlackLegion:1495073025660420212>", 
    "Death Guard": "<:DeathGuard:1439330955079717150>", 
    "Thousand Sons": "<:ThousandSons:1505870183666028574>",
    
    # --- XENOS ---
    "Aeldari": "<:Aeldari:1501193876487274506>", 
    "Drukhari": "<:Drukhari:1543897513201901579>", 
    "Necrons": "<:Necron:1439333592802005174>", 
    "Orks": "<:Ork:1416864462798983228>",
    "Tau": "<:Tau:1520707105105907753>",
    "Tyranids": "<:Tyranid:1545493790318661662>"
}

# ==========================================
# UI COMPONENTS (Dropdowns) - ΣΕ ΣΧΟΛΙΟ ΓΙΑ ΤΩΡΑ
# ==========================================
"""
class FactionDropdown(discord.ui.Select):
    def __init__(self, category: str, options_dict: dict):
        self.category = category
        self.options_dict = options_dict
        
        options = []
        for name, role_id in options_dict.items():
            emoji = EMOJIS.get(name, "📌")
            options.append(discord.SelectOption(label=name, value=str(role_id), emoji=emoji))
            
        super().__init__(
            placeholder=f"Επίλεξε στρατούς: {category}...",
            min_values=0,
            max_values=len(options),
            custom_id=f"dropdown_{category}"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        member = interaction.user
        selected_role_ids = [int(v) for v in self.values]
        roles_to_add = []
        roles_to_remove = []
        
        for name, role_id in self.options_dict.items():
            role = interaction.guild.get_role(role_id)
            if not role: continue
            
            if role_id in selected_role_ids and role not in member.roles:
                roles_to_add.append(role)
            elif role_id not in selected_role_ids and role in member.roles:
                roles_to_remove.append(role)
                
        if roles_to_add:
            await member.add_roles(*roles_to_add)
        if roles_to_remove:
            await member.remove_roles(*roles_to_remove)
            
        await interaction.followup.send(f"✅ Τα αρχεία ενημερώθηκαν για την κατηγορία **{self.category}**!", ephemeral=True)

class RoleSelectionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for category, roles in FACTION_ROLES.items():
            if category == "General":
                continue
            self.add_item(FactionDropdown(category, roles))
"""

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

    # Αυτόματη ενημέρωση του Panel όταν κάποιος παίρνει/χάνει ρόλο
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

    # AUTO-ROLE: Δίνει το Warhammer ρόλο αυτόματα σε όποιον μπαίνει (Προαιρετικό, το αφήνω)
    @commands.Cog.listener()
    async def on_member_join(self, member):
        warhammer_role_id = 1416870277689901109
        role = member.guild.get_role(warhammer_role_id)
        if role:
            await member.add_roles(role)

    # Εντολή Εγκατάστασης (ΜΟΝΟ το Panel)
    @commands.command(name="setup_roles")
    @commands.has_permissions(administrator=True)
    async def setup_roles(self, ctx):
        await ctx.message.delete()
        
        # 1. Στέλνουμε το Live Panel
        panel_embed = self.generate_panel_embed(ctx.guild)
        panel_msg = await ctx.send(embed=panel_embed)
        
        settings_col.update_one(
            {"_id": "live_panel"},
            {"$set": {"message_id": panel_msg.id, "channel_id": ctx.channel.id}},
            upsert=True
        )
        
        # (Το κομμάτι των Dropdowns αφαιρέθηκε από εδώ)

async def setup(bot):
    await bot.add_cog(RolesSystem(bot))
    # bot.add_view(RoleSelectionView())  # Απενεργοποιημένο μαζί με την κλάση