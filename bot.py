import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button

# ----------------------------
# Bot Setup
# ----------------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------------------
# Rollen
# ----------------------------
ROLLE_ABTEILUNG = "✴ ⊶▬⊶▬ 𝐀𝐛𝐭𝐞𝐢𝐥𝐮𝐧𝐠𝐞𝐧 ▬⊷▬⊷ ✴"
ROLLE_TEAMVERWALTUNG = "Teamverwaltung"
ROLLE_STAFF = "staff"
ROLLE_VERIFIZIERT = "Verifiziert"
ROLLE_MITGLIED = "» Mitglied"
ROLLE_TEAMSCHLUSS = "Teamsperre"
ROLLE_WARN_1 = "Team Warn 1"
ROLLE_WARN_2 = "Team Warn 2"
ROLLE_WARN_1_DAUER = "Team Warn 1 (Dauerhaft)"
ROLLE_WARN_2_DAUER = "Team Warn 2 (Dauerhaft)"
ROLLE_BW_AUSSTEHEND = "Bewerbungs Gespräch ausstehend"
ROLLE_HIGH_TEAM = "┏―――――:gem:High Team:gem:――――┛"

# ----------------------------
# Check Berechtigungen
# ----------------------------
def has_permission(interaction: discord.Interaction):
    return any(r.name in [ROLLE_ABTEILUNG, ROLLE_TEAMVERWALTUNG] for r in interaction.user.roles)

def get_role_by_name(guild, name):
    return discord.utils.get(guild.roles, name=name)

# ----------------------------
# On Ready
# ----------------------------
@bot.event
async def on_ready():
    print(f"✅ Bot ist online als {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔄 {len(synced)} Slash Commands synchronisiert")
    except Exception as e:
        print(f"❌ Fehler beim Sync: {e}")

# ----------------------------
# Ping
# ----------------------------
@bot.tree.command(name="ping", description="Teste, ob der Bot antwortet.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# ----------------------------
# Beispiel: /cop-kick
# ----------------------------
@bot.tree.command(name="cop-kick", description="Mitglied aus dem Team entfernen.")
@app_commands.describe(member="Mitglied auswählen", grund="Grund für die Kündigung", teamsperre="Teamsperre hinzufügen (true/false)")
async def cop_kick(interaction: discord.Interaction, member: discord.Member, grund: str, teamsperre: bool = False):
    if not has_permission(interaction):
        return await interaction.response.send_message("🚫 Keine Berechtigung.", ephemeral=True)

    roles_to_remove = [r for r in member.roles if r != interaction.guild.default_role]
    if roles_to_remove:
        await member.remove_roles(*roles_to_remove)

    add_roles = []
    verifiziert = get_role_by_name(interaction.guild, ROLLE_VERIFIZIERT)
    mitglied = get_role_by_name(interaction.guild, ROLLE_MITGLIED)
    if verifiziert: add_roles.append(verifiziert)
    if mitglied: add_roles.append(mitglied)
    if teamsperre:
        sperre = get_role_by_name(interaction.guild, ROLLE_TEAMSCHLUSS)
        if sperre: add_roles.append(sperre)

    if add_roles:
        await member.add_roles(*add_roles)

    embed = discord.Embed(title="❌ Team-Kick", color=discord.Color.red())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="🚫 Teamsperre", value="✅ Ja" if teamsperre else "❌ Nein", inline=False)
    await interaction.response.send_message(embed=embed)

# ----------------------------
# Warn Befehle
# ----------------------------
@bot.tree.command(name="cop-warn", description="Verwarnung für ein Mitglied.")
@app_commands.describe(member="Mitglied auswählen", grund="Grund", stufe="1 oder 2", dauer="Dauerhaft? (true/false)", zeit="Nur bei temporär: Zeit")
async def cop_warn(interaction: discord.Interaction, member: discord.Member, grund: str, stufe: int, dauer: bool = False, zeit: str = None):
    if not has_permission(interaction):
        return await interaction.response.send_message("🚫 Keine Berechtigung.", ephemeral=True)
    if stufe not in [1,2]:
        return await interaction.response.send_message("⚠️ Stufe muss 1 oder 2 sein.", ephemeral=True)
    role = None
    if stufe == 1:
        role = get_role_by_name(interaction.guild, ROLLE_WARN_1_DAUER if dauer else ROLLE_WARN_1)
    else:
        role = get_role_by_name(interaction.guild, ROLLE_WARN_2_DAUER if dauer else ROLLE_WARN_2)
    if role: await member.add_roles(role)

    embed = discord.Embed(title="⚠️ Verwarnung", color=discord.Color.orange())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="📊 Stufe", value=str(stufe), inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="⏱️ Dauerhaft", value="✅ Ja" if dauer else "❌ Nein", inline=False)
    if zeit:
        embed.add_field(name="⏳ Zeit", value=zeit, inline=False)
    await interaction.response.send_message(embed=embed)

# ----------------------------
# Team-Rank Befehle (up/down)
# ----------------------------
@bot.tree.command(name="up-rank", description="Mitglied befördern.")
@app_commands.describe(member="Mitglied auswählen", neue_rolle="Neue Rolle", grund="Grund")
async def up_rank(interaction: discord.Interaction, member: discord.Member, neue_rolle: discord.Role, grund: str):
    if not has_permission(interaction):
        return await interaction.response.send_message("🚫 Keine Berechtigung.", ephemeral=True)
    await member.add_roles(neue_rolle)
    embed = discord.Embed(title="⬆️ Beförderung", color=discord.Color.green())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="🎖️ Neue Rolle", value=neue_rolle.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="down-rank", description="Mitglied degradieren.")
@app_commands.describe(member="Mitglied auswählen", neue_rolle="Neue Rolle", grund="Grund")
async def down_rank(interaction: discord.Interaction, member: discord.Member, neue_rolle: discord.Role, grund: str):
    if not has_permission(interaction):
        return await interaction.response.send_message("🚫 Keine Berechtigung.", ephemeral=True)
    await member.add_roles(neue_rolle)
    embed = discord.Embed(title="⬇️ Degradierung", color=discord.Color.orange())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="➡️ Neue Rolle", value=neue_rolle.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    await interaction.response.send_message(embed=embed)

# ----------------------------
# Neuer Teamler
# ----------------------------
@bot.tree.command(name="neuer-teamler", description="Neues Teammitglied hinzufügen.")
@app_commands.describe(member="Mitglied auswählen", rolle="Rolle geben", grund="Optionaler Grund")
async def neuer_teamler(interaction: discord.Interaction, member: discord.Member, rolle: discord.Role, grund: str = None):
    if not has_permission(interaction):
        return await interaction.response.send_message("🚫 Keine Berechtigung.", ephemeral=True)
    staff_role = get_role_by_name(interaction.guild, ROLLE_STAFF)
    await member.add_roles(rolle)
    if staff_role:
        await member.add_roles(staff_role)
    embed = discord.Embed(title="👥 Neuer Teamler", color=discord.Color.blue())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="🎖️ Rolle", value=rolle.mention, inline=False)
    if grund:
        embed.add_field(name="📝 Grund", value=grund, inline=False)
    await interaction.response.send_message(embed=embed)

# ----------------------------
# Ticket Panel
# ----------------------------
class TicketButtonView(View):
    def __init__(self, category: discord.CategoryChannel):
        super().__init__(timeout=None)
        self.category = category

        # Button: Allgemeine Fragen
        self.add_item(Button(label="Allgemeine Fragen", style=discord.ButtonStyle.primary, custom_id="ticket_allgemein"))
        # Button: Teambeschwerde
        self.add_item(Button(label="Teambeschwerde", style=discord.ButtonStyle.danger, custom_id="ticket_teambeschwerde"))
        # Button: Bewerbungsgespräch
        self.add_item(Button(label="Bewerbungsgespräch", style=discord.ButtonStyle.success, custom_id="ticket_bewerbung"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Bewerbungsgespräch darf nur Rolle Bewerbungs Gespräch ausstehend
        if interaction.data["custom_id"] == "ticket_bewerbung":
            return any(r.name == ROLLE_BW_AUSSTEHEND for r in interaction.user.roles)
        return True

@bot.tree.command(name="ticket-setup", description="Ticket Panel in Kanal senden.")
@app_commands.describe(channel="Kanal, wo das Ticket Panel erscheinen soll")
async def ticket_setup(interaction: discord.Interaction, channel: discord.TextChannel):
    if not has_permission(interaction):
        return await interaction.response.send_message("🚫 Keine Berechtigung.", ephemeral=True)
    category = discord.utils.get(interaction.guild.categories, name="Bewerbungsgespräch")
    if not category:
        category = await interaction.guild.create_category("Bewerbungsgespräch")
    embed = discord.Embed(title="🎟️ Ticket System", description="Klicke auf einen Button, um ein Ticket zu erstellen.", color=discord.Color.green())
    await channel.send(embed=embed, view=TicketButtonView(category))
    await interaction.response.send_message("✅ Ticket-Panel wurde erstellt.", ephemeral=True)

# ----------------------------
# Events Ticket Button Click
# ----------------------------
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if not interaction.type == discord.InteractionType.component:
        return

    user = interaction.user
    guild = interaction.guild
    staff_role = get_role_by_name(guild, ROLLE_STAFF)
    high_team_role = get_role_by_name(guild, ROLLE_HIGH_TEAM)
    category = discord.utils.get(guild.categories, name="Bewerbungsgespräch")
    if not category:
        category = await guild.create_category("Bewerbungsgespräch")

    # Button: Allgemeine Fragen
    if interaction.data["custom_id"] == "ticket_allgemein":
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        channel = await guild.create_text_channel(f"Frage-von-{user.name}", category=category, overwrites=overwrites)
        await interaction.response.send_message(f"🎫 Dein Ticket wurde erstellt: {channel.mention}", ephemeral=True)

    # Button: Teambeschwerde
    if interaction.data["custom_id"] == "ticket_teambeschwerde":
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        channel = await guild.create_text_channel(f"Teambeschwerde-von-{user.name}", category=category, overwrites=overwrites)
        await interaction.response.send_message(f"🎫 Dein Ticket wurde erstellt: {channel.mention}", ephemeral=True)

    # Button: Bewerbungsgespräch
    if interaction.data["custom_id"] == "ticket_bewerbung":
        if not any(r.name == ROLLE_BW_AUSSTEHEND for r in user.roles):
            return await interaction.response.send_message("🚫 Du darfst keine Bewerbungsgespräch-Tickets erstellen.", ephemeral=True)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        if high_team_role:
            overwrites[high_team_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        channel = await guild.create_text_channel(f"Bewerbung-von-{user.name}", category=category, overwrites=overwrites)
        await interaction.response.send_message(f"🎫 Dein Bewerbungsgespräch-Ticket wurde erstellt: {channel.mention}", ephemeral=True)

# ----------------------------
# Bot Token starten
# ----------------------------
bot.run("DEIN_BOT_TOKEN_HIER")
