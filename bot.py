import os
import discord
from discord import app_commands
from discord.ext import commands

# ----------------------------
# Discord-Bot Setup
# ----------------------------
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------------------
# Rollen-Namen
# ----------------------------
ROLLE_BESUCHER = "🧳 | Besucher"
ROLLE_TEAMSCHLUSS = "❌ | Ausbildungssperre"
ROLLE_1_WARN = "❌ | 1.Abmahnung"
ROLLE_2_WARN = "❌ | 2.Abmahnung"

# Team-spezifische Rollen
ROLLE_VERIFIZIERT = "Verifiziert"
ROLLE_MITGLIED = "» Mitglied"
ROLLE_TEAMSPEER = "Teamsperre"

ROLLE_TEAM_WARN_1 = "Team Warn 1"
ROLLE_TEAM_WARN_2 = "Team Warn 2"
ROLLE_TEAM_WARN_1_DAUER = "Team Warn 1 (Dauerhaft)"
ROLLE_TEAM_WARN_2_DAUER = "Team Warn 2 (Dauerhaft)"

ROLLE_STAFF = "staff"

# ----------------------------
# Zugriff erlaubte Rollen
# ----------------------------
ERLAUBTE_ROLLEN = [
    "✴ ⊶▬⊶▬ 𝐀𝐛𝐭𝐞𝐢𝐥𝐮𝐧𝐠𝐞𝐧 ▬⊷▬⊷ ✴",
    "Teamverwaltung"
]

# ----------------------------
# Hilfsfunktionen
# ----------------------------
def has_role(member: discord.Member, role_names: list):
    """Prüft, ob ein Mitglied eine der erlaubten Rollen hat."""
    return any(role.name in role_names for role in member.roles)


def get_role_by_name(guild, name):
    """Hilfsfunktion, um eine Rolle nach Namen zu finden."""
    return discord.utils.get(guild.roles, name=name)


# ----------------------------
# Event: Bot online
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
# /ping
# ----------------------------
@bot.tree.command(name="ping", description="Überprüft, ob der Bot reagiert")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")


# ----------------------------
# Kick-Befehle (Cop + Team)
# ----------------------------
async def handle_kick(interaction, member, grund, teamsperre, is_team=False):
    if not has_role(interaction.user, ERLAUBTE_ROLLEN):
        await interaction.response.send_message("❌ Du hast keine Berechtigung für diesen Befehl!", ephemeral=True)
        return

    roles_to_remove = [r for r in member.roles if r != interaction.guild.default_role]
    if roles_to_remove:
        await member.remove_roles(*roles_to_remove)

    added_roles = []

    if is_team:
        verifiziert = get_role_by_name(interaction.guild, ROLLE_VERIFIZIERT)
        mitglied = get_role_by_name(interaction.guild, ROLLE_MITGLIED)
        if verifiziert:
            await member.add_roles(verifiziert)
            added_roles.append(verifiziert.name)
        if mitglied:
            await member.add_roles(mitglied)
            added_roles.append(mitglied.name)
        if teamsperre:
            sperre = get_role_by_name(interaction.guild, ROLLE_TEAMSPEER)
            if sperre:
                await member.add_roles(sperre)
                added_roles.append(sperre.name)
    else:
        besucher = get_role_by_name(interaction.guild, ROLLE_BESUCHER)
        if besucher:
            await member.add_roles(besucher)
            added_roles.append(besucher.name)
        if teamsperre:
            sperre = get_role_by_name(interaction.guild, ROLLE_TEAMSCHLUSS)
            if sperre:
                await member.add_roles(sperre)
                added_roles.append(sperre.name)

    embed = discord.Embed(title="❌ Kündigung", color=discord.Color.red())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="⏱️ Teamsperre", value="✅ Ja" if teamsperre else "❌ Nein", inline=False)
    embed.add_field(name="📋 Neue Rollen", value=", ".join(added_roles) if added_roles else "Keine", inline=False)
    embed.add_field(name="📅 Datum", value=interaction.created_at.strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="cop-kick", description="Mitglied kündigen (Cop-Version)")
@app_commands.describe(member="Mitglied auswählen", grund="Grund angeben", teamsperre="Teamsperre hinzufügen? (true/false)")
async def cop_kick(interaction: discord.Interaction, member: discord.Member, grund: str, teamsperre: bool = False):
    await handle_kick(interaction, member, grund, teamsperre, is_team=False)


@bot.tree.command(name="team-kick", description="Mitglied kündigen (Team-Version)")
@app_commands.describe(member="Mitglied auswählen", grund="Grund angeben", teamsperre="Teamsperre hinzufügen? (true/false)")
async def team_kick(interaction: discord.Interaction, member: discord.Member, grund: str, teamsperre: bool = False):
    await handle_kick(interaction, member, grund, teamsperre, is_team=True)


# ----------------------------
# Verwarnungen
# ----------------------------
@bot.tree.command(name="cop-warn", description="Mitglied verwarnen (Cop-Version)")
@app_commands.describe(member="Mitglied auswählen", grund="Grund angeben", stufe="Warnstufe (1 oder 2)")
async def cop_warn(interaction: discord.Interaction, member: discord.Member, grund: str, stufe: int):
    if not has_role(interaction.user, ERLAUBTE_ROLLEN):
        await interaction.response.send_message("❌ Du hast keine Berechtigung für diesen Befehl!", ephemeral=True)
        return

    if stufe == 1:
        role = get_role_by_name(interaction.guild, ROLLE_1_WARN)
    elif stufe == 2:
        role = get_role_by_name(interaction.guild, ROLLE_2_WARN)
    else:
        await interaction.response.send_message("❌ Ungültige Stufe! Nur 1 oder 2 erlaubt.", ephemeral=True)
        return

    if role:
        await member.add_roles(role)

    embed = discord.Embed(title=f"⚠️ Verwarnung (Stufe {stufe})", color=discord.Color.orange())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="📅 Datum", value=interaction.created_at.strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="team-warn", description="Mitglied verwarnen (Team-Version)")
@app_commands.describe(
    member="Mitglied auswählen",
    grund="Grund angeben",
    stufe="Warnstufe (1 oder 2)",
    dauerhaft="Dauerhafte Verwarnung?",
    zeit="Dauer der Verwarnung (nur Info, z. B. 24h, 2d)"
)
async def team_warn(interaction: discord.Interaction, member: discord.Member, grund: str, stufe: int, dauerhaft: bool = False, zeit: str = "Keine"):
    if not has_role(interaction.user, ERLAUBTE_ROLLEN):
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return

    role = None
    if stufe == 1:
        role = get_role_by_name(interaction.guild, ROLLE_TEAM_WARN_1_DAUER if dauerhaft else ROLLE_TEAM_WARN_1)
    elif stufe == 2:
        role = get_role_by_name(interaction.guild, ROLLE_TEAM_WARN_2_DAUER if dauerhaft else ROLLE_TEAM_WARN_2)
    else:
        await interaction.response.send_message("❌ Ungültige Stufe! Nur 1 oder 2 erlaubt.", ephemeral=True)
        return

    if role:
        await member.add_roles(role)

    embed = discord.Embed(title=f"⚠️ Team Verwarnung (Stufe {stufe})", color=discord.Color.yellow() if stufe == 1 else discord.Color.orange())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="⏱️ Dauerhaft", value="✅ Ja" if dauerhaft else "❌ Nein", inline=True)
    if not dauerhaft:
        embed.add_field(name="⌛ Zeit", value=zeit, inline=True)
    embed.add_field(name="📅 Datum", value=interaction.created_at.strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)


# ----------------------------
# Up- und Down-Rank
# ----------------------------
@bot.tree.command(name="up-rank", description="Mitglied befördern")
@app_commands.describe(member="Mitglied auswählen", neue_rolle="Neue Rolle geben", grund="Grund angeben")
async def up_rank(interaction: discord.Interaction, member: discord.Member, neue_rolle: discord.Role, grund: str):
    if not has_role(interaction.user, ERLAUBTE_ROLLEN):
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return
    try:
        await member.add_roles(neue_rolle)
        embed = discord.Embed(title="⬆️ Beförderung", color=discord.Color.green())
        embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
        embed.add_field(name="➡️ Neue Rolle", value=neue_rolle.mention, inline=False)
        embed.add_field(name="📝 Grund", value=grund, inline=False)
        embed.add_field(name="📅 Datum", value=interaction.created_at.strftime("%d.%m.%Y"), inline=False)
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Fehler: Bot hat keine Berechtigung, die Rolle zu vergeben.", ephemeral=True)


@bot.tree.command(name="down-rank", description="Mitglied degradieren")
@app_commands.describe(member="Mitglied auswählen", neue_rolle="Neue Rolle geben", grund="Grund angeben")
async def down_rank(interaction: discord.Interaction, member: discord.Member, neue_rolle: discord.Role, grund: str):
    if not has_role(interaction.user, ERLAUBTE_ROLLEN):
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return
    try:
        await member.add_roles(neue_rolle)
        embed = discord.Embed(title="⬇️ Degradierung", color=discord.Color.orange())
        embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
        embed.add_field(name="➡️ Neue Rolle", value=neue_rolle.mention, inline=False)
        embed.add_field(name="📝 Grund", value=grund, inline=False)
        embed.add_field(name="📅 Datum", value=interaction.created_at.strftime("%d.%m.%Y"), inline=False)
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Fehler: Bot hat keine Berechtigung, die Rolle zu vergeben.", ephemeral=True)


# ----------------------------
# Neuer-Teamler
# ----------------------------
@bot.tree.command(name="neuer-teamler", description="Neues Teammitglied hinzufügen")
@app_commands.describe(member="Mitglied auswählen", rolle="Rolle auswählen", grund="Optionaler Grund")
async def neuer_teamler(interaction: discord.Interaction, member: discord.Member, rolle: discord.Role, grund: str = "Kein Grund angegeben"):
    if not has_role(interaction.user, ERLAUBTE_ROLLEN):
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return

    staff_role = get_role_by_name(interaction.guild, ROLLE_STAFF)
    await member.add_roles(rolle)
    if staff_role:
        await member.add_roles(staff_role)

    embed = discord.Embed(title="👥 Neues Teammitglied", color=discord.Color.blue())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="🏷️ Neue Rolle", value=rolle.mention, inline=False)
    if staff_role:
        embed.add_field(name="🧩 Zusatzrolle", value=staff_role.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="📅 Datum", value=interaction.created_at.strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)


# ----------------------------
# Bot starten
# ----------------------------
if __name__ == "__main__":
    bot.run("DEIN_TOKEN_HIER")
