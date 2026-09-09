"""
========================================
ΑΡΧΕΙΟ: roles.py (Cogs)
ΠΕΡΙΓΡΑΦΗ: Live Panel & Persistent Auto-Updating Buttons
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
        "Warhammer": 1416870277689901109 # Μόνο για το Live Panel - Δεν βγάζει κουμπί
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
    },
    "Other Games": {
        "Campaign": 1477668128237420615,       
        "Age Of Sigmar": 1491162031880015945,  
        "Kill Team": 1491372593616392192,      
        "Old World": 1491372847711391774,      
        "Gaming": 1520072097295106219       
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
    "Tyranids": "<:Tyranid:1545493790318661662>",
    # Άλλα παιχ΄ίδια
    "Campaign": "<:Warhammer_1:1416864475520438302>", 
    "Age Of Sigmar": "<:Age_of_Sigmar:1439331241693286600>",
    "Kill Team": "<:Kill_Team:1491372232243675236>",
    "Old World": "<:Old_World:1491371903665963098>",
    "Gaming": "🎮"
}

def get_style_for_category(category: str):
    if category == "Imperium": return discord.ButtonStyle.primary
    elif category == "Chaos": return discord.ButtonStyle.danger
    elif category == "Xenos": return discord.ButtonStyle.success
    return discord.ButtonStyle.secondary

class RoleButton(discord.ui.Button):
    def __init__(self, label: str, role_id: int, style: discord.ButtonStyle, emoji: str = None):
        super().__init__(
            label=label,
            style=style,
            custom_id=f"role_btn_{role_id}",
            emoji=emoji
        )
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("❌ Error: This role was deleted or not found", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"➖ Role has been removed: **{role.name}**", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"➕ You got the role: **{role.name}**", ephemeral=True)

class RoleCategoryView(discord.ui.View):
    def __init__(self, category: str, roles_dict: dict):
        super().__init__(timeout=None)
        style = get_style_for_category(category)
        
        for name, role_id in roles_dict.items():
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
                
            is_inline = False if category in ["General", "Other Games"] else True
            embed.add_field(name=f"**{category}**", value=text, inline=is_inline)
            
        embed.set_footer(text="To Departmento Munitorum παρακολουθεί.")
        return embed

    # AUTO-UPDATE: Τρέχει κάθε φορά που ανοίγει το bot και κάνει edit τα υπάρχοντα μηνύματα
    @commands.Cog.listener()
    async def on_ready(self):
        menu_data = settings_col.find_one({"_id": "role_menus"})
        if not menu_data: return
        
        channel = self.bot.get_channel(menu_data["channel_id"])
        if not channel: return
        
        # 1. Update το Live Panel
        try:
            panel_msg = await channel.fetch_message(menu_data["panel_msg_id"])
            await panel_msg.edit(embed=self.generate_panel_embed(channel.guild))
        except: pass
        
        # 2. Update τα Buttons
        messages_dict = menu_data.get("messages", {})
        for category, msg_id in messages_dict.items():
            # Αγνοούμε το "General" γιατί δεν έχει κουμπιά
            if category not in FACTION_ROLES or category == "General": continue 
            
            try:
                msg = await channel.fetch_message(msg_id)
                view = RoleCategoryView(category, FACTION_ROLES[category])
                
                color = discord.Color.blue() if category == "Imperium" else (discord.Color.red() if category == "Chaos" else (discord.Color.green() if category == "Xenos" else discord.Color.dark_grey()))
                icon = "🎲" if category == "Other Games" else "🛡️"
                
                embed = discord.Embed(title=f"{icon} {category} Roles", color=color)
                await msg.edit(embed=embed, view=view)
                
                # Κολλάμε το View στο Bot για να είναι Persistent
                self.bot.add_view(view)
            except Exception as e:
                print(f"Αποτυχία ενημέρωσης {category}: {e}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles == after.roles: return
            
        menu_data = settings_col.find_one({"_id": "role_menus"})
        if not menu_data: return
        
        channel = self.bot.get_channel(menu_data["channel_id"])
        if not channel: return
        
        try:
            msg = await channel.fetch_message(menu_data["panel_msg_id"])
            await msg.edit(embed=self.generate_panel_embed(after.guild))
        except: pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        warhammer_role_id = 1416870277689901109
        role = member.guild.get_role(warhammer_role_id)
        if role:
            await member.add_roles(role)

    # ----------------------------------------------------
    # Η ΕΝΤΟΛΗ ΠΟΥ ΣΤΗΝΕΙ ΤΟ ΣΥΣΤΗΜΑ
    # ----------------------------------------------------
    @commands.command(name="setup_roles")
    @commands.has_permissions(administrator=True)
    async def setup_roles(self, ctx):
        await ctx.message.delete()
        
        # Στέλνουμε το Panel
        panel_embed = self.generate_panel_embed(ctx.guild)
        panel_msg = await ctx.send(embed=panel_embed)
        
        await ctx.send("https://cdn.discordapp.com/attachments/1523030976782143645/1547174668350263346/CITYPNG.COMHorizontal_White_Line_-_2000x2000.png?ex=6aa27632&is=6aa124b2&hm=e74aa9659e8399a93a0ed792beba8ff29873a7466fc8e9b54be560ba9c173e1a&")
        await ctx.send("## 📜 ARMY SELECTION\n*Press the buttons below to get or remove your roles.*")

        saved_messages = {}

        # Φτιάχνουμε τα μηνύματα με τα κουμπιά ένα-ένα
        for category, roles in FACTION_ROLES.items():
            if not roles or category == "General": continue # Το General (Warhammer) εξαιρείται από τα κουμπιά
            
            view = RoleCategoryView(category, roles)
            color = discord.Color.blue() if category == "Imperium" else (discord.Color.red() if category == "Chaos" else (discord.Color.green() if category == "Xenos" else discord.Color.dark_grey()))
            icon = "🎲" if category == "Other Games" else "🛡️"
            
            menu_embed = discord.Embed(title=f"{icon} {category} Roles", color=color)
            msg = await ctx.send(embed=menu_embed, view=view)
            
            saved_messages[category] = msg.id

        # Αποθήκευση στη Βάση για να τα βρίσκει το Auto-Update
        settings_col.update_one(
            {"_id": "role_menus"},
            {
                "$set": {
                    "channel_id": ctx.channel.id,
                    "panel_msg_id": panel_msg.id,
                    "messages": saved_messages
                }
            },
            upsert=True
        )
        
        # Καθαρίζουμε το παλιό ID format από τη βάση αν υπάρχει
        settings_col.delete_one({"_id": "live_panel"})

async def setup(bot):
    await bot.add_cog(RolesSystem(bot))
    # Τα Views πλέον γίνονται attach μέσα από την on_ready