# dcbot_full.py
import os
import re
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

# ----------------------------
# Basic Bot Setup
# ----------------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = False  # nicht nötig, wir arbeiten mit Slash-Commands
bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------------------
# Rollen-Namen (anpassbar)
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
def has_role(member: discord.Member, role_names: list) -> bool:
    """Prüft, ob ein Mitglied eine der erlaubten Rollen hat."""
    return any(role.name in role_names for role in member.roles)

def get_role_by_name(guild: discord.Guild, name: str):
    """Get role by exact name or return None."""
    return discord.utils.get(guild.roles, name=name)

def sanitize_channel_name(name: str) -> str:
    """Sanitize username to a valid channel name (lowercase, alnum + hyphen)."""
    name = name.lower()
    # replace spaces and invalid chars with hyphen
    name = re.sub(r'[^a-z0-9\-]', '-', name)
    name = re.sub(r'-+', '-', name).strip('-')
    if not name:
        name = "user"
    return name

# ----------------------------
# On ready: sync commands
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
# Gemeinsame Kick-Logik
# ----------------------------
async def handle_kick(interaction: discord.Interaction, member: discord.Member, grund: str, teamsperre: bool, is_team: bool):
    if not has_role(interaction.user, ERLAUBTE_ROLLEN):
        await interaction.response.send_message("❌ Du hast keine Berechtigung für diesen Befehl!", ephemeral=True)
        return

    # Remove all roles except @everyone
    roles_to_remove = [r for r in member.roles if r != interaction.guild.default_role]
    if roles_to_remove:
        try:
            await member.remove_roles(*roles_to_remove, reason=f"Kündigung durch {interaction.user}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Der Bot hat keine Berechtigung, Rollen zu entfernen.", ephemeral=True)
            return

    added_roles = []

    if is_team:
        # always add Verifiziert and » Mitglied
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

    embed = discord.Embed(
        title="❌ Kündigung",
        color=discord.Color.red()
    )
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="⏱️ Teamsperre", value="✅ Ja" if teamsperre else "❌ Nein", inline=False)
    embed.add_field(name="📋 Neue Rollen", value=", ".join(added_roles) if added_roles else "Keine", inline=False)
    embed.add_field(name="📅 Datum", value=interaction.created_at.strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)

# ----------------------------
# /cop-kick & /team-kick
# ----------------------------
@bot.tree.command(name="cop-kick", description="Mitglied kündigen (Cop-Version)")
@app_commands.describe(member="Mitglied auswählen", grund="Grund angeben", teamsperre="Teamsperre hinzufügen? (true/false)")
async def cop_kick(interaction: discord.Interaction, member: discord.Member, grund: str, teamsperre: bool = False):
    await handle_kick(interaction, member, grund, teamsperre, is_team=False)

@bot.tree.command(name="team-kick", description="Mitglied kündigen (Team-Version)")
@app_commands.describe(member="Mitglied auswählen", grund="Grund angeben", teamsperre="Teamsperre hinzufügen? (true/false)")
async def team_kick(interaction: discord.Interaction, member: discord.Member, grund: str, teamsperre: bool = False):
    await handle_kick(interaction, member, grund, teamsperre, is_team=True)

# ----------------------------
# /cop-warn
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
        try:
            await member.add_roles(role, reason=f"Verwarnung Stufe {stufe} durch {interaction.user}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Der Bot hat keine Berechtigung, Rollen zu vergeben.", ephemeral=True)
            return

    embed = discord.Embed(
        title=f"⚠️ Verwarnung (Stufe {stufe})",
        color=discord.Color.orange()
    )
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="📅 Datum", value=interaction.created_at.strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)

# ----------------------------
# /team-warn
# ----------------------------
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
        try:
            await member.add_roles(role, reason=f"Team Verwarnung Stufe {stufe} durch {interaction.user}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Der Bot hat keine Berechtigung, Rollen zu vergeben.", ephemeral=True)
            return

    embed = discord.Embed(
        title=f"⚠️ Team Verwarnung (Stufe {stufe})",
        color=discord.Color.yellow() if stufe == 1 else discord.Color.orange()
    )
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="⏱️ Dauerhaft", value="✅ Ja" if dauerhaft else "❌ Nein", inline=True)
    if not dauerhaft:
        embed.add_field(name="⌛ Zeit", value=zeit, inline=True)
    embed.add_field(name="📅 Datum", value=interaction.created_at.strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)

# ----------------------------
# Up-Rank & Down-Rank
# ----------------------------
@bot.tree.command(name="up-rank", description="Mitglied befördern")
@app_commands.describe(member="Mitglied auswählen", neue_rolle="Neue Rolle geben", grund="Grund angeben")
async def up_rank(interaction: discord.Interaction, member: discord.Member, neue_rolle: discord.Role, grund: str):
    if not has_role(interaction.user, ERLAUBTE_ROLLEN):
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return
    try:
        await member.add_roles(neue_rolle, reason=f"Beförderung durch {interaction.user}")
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
        await member.add_roles(neue_rolle, reason=f"Degradierung durch {interaction.user}")
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
    try:
        await member.add_roles(rolle, reason=f"Neuer Teamler durch {interaction.user}")
        if staff_role:
            await member.add_roles(staff_role, reason=f"Neuer Teamler (staff) durch {interaction.user}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ Fehler: Bot hat keine Berechtigung, Rollen zu vergeben.", ephemeral=True)
        return

    embed = discord.Embed(title="👥 Neues Teammitglied", color=discord.Color.blue())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="🏷️ Neue Rolle", value=rolle.mention, inline=False)
    if staff_role:
        embed.add_field(name="🧩 Zusatzrolle", value=staff_role.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="📅 Datum", value=interaction.created_at.strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)

# ----------------------------
# Ticket System (View + Handlers)
# ----------------------------
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="❌ Ticket schließen", style=discord.ButtonStyle.red, custom_id="ticket_close")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_role = get_role_by_name(interaction.guild, ROLLE_STAFF)
        # nur staff darf schließen
        if not staff_role or staff_role not in interaction.user.roles:
            await interaction.response.send_message("🚫 Du darfst dieses Ticket nicht schließen.", ephemeral=True)
            return

        await interaction.response.send_message("🕐 Ticket wird geschlossen...", ephemeral=True)
        # kurze Verzögerung, damit die Nachricht dem User angezeigt wird
        await asyncio.sleep(1.5)
        try:
            await interaction.channel.delete(reason=f"Ticket geschlossen von {interaction.user}")
        except Exception:
            # falls nicht löschbar
            await interaction.followup.send("❌ Konnte Ticket-Kanal nicht löschen.", ephemeral=True)

class TicketCreateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Ticket erstellen", style=discord.ButtonStyle.green, custom_id="ticket_create")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        staff_role = get_role_by_name(guild, ROLLE_STAFF)

        # Check existing ticket
        channel_name = f"ticket-{sanitize_channel_name(user.name)}"
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if existing_channel:
            await interaction.response.send_message(f"❗ Du hast bereits ein offenes Ticket: {existing_channel.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            bot.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        # Create channel in same category as the message if possible, else no category
        category = None
        try:
            # try to place under the category of the channel where the button was clicked
            if interaction.channel and isinstance(interaction.channel, discord.TextChannel):
                category = interaction.channel.category
        except Exception:
            category = None

        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            overwrites=overwrites,
            reason=f"Ticket erstellt von {user}",
            category=category
        )

        # send welcome embed + close button
        embed = discord.Embed(
            title="🎟️ Neues Ticket",
            description=f"👋 Willkommen {user.mention}!\n\nBitte beschreibe dein Anliegen kurz. Ein Teammitglied wird dir bald antworten.",
            color=discord.Color.blue()
        )
        view = CloseTicketView()
        # Mention staff if exists
        content = staff_role.mention if staff_role else None
        await ticket_channel.send(content=content, embed=embed, view=view)

        await interaction.response.send_message(f"✅ Dein Ticket wurde erstellt: {ticket_channel.mention}", ephemeral=True)

# Slash command to set up ticket panel
@bot.tree.command(name="ticket-setup", description="Sendet das Ticket-Erstell-Panel in den angegebenen Channel")
@app_commands.describe(channel="Channel, in den das Ticket-Panel gesendet werden soll")
async def ticket_setup(interaction: discord.Interaction, channel: discord.TextChannel):
    # Only allowed roles can setup the panel
    if not has_role(interaction.user, ERLAUBTE_ROLLEN):
        await interaction.response.send_message("❌ Du hast keine Berechtigung dafür.", ephemeral=True)
        return

    embed = discord.Embed(
        title="🎟️ Support-Tickets",
        description="Wenn du Hilfe benötigst, klicke unten auf den Button, um ein privates Ticket zu eröffnen.\nUnser Team hilft dir so schnell wie möglich.",
        color=discord.Color.green()
    )
    embed.set_footer(text="Ticket-System")

    view = TicketCreateView()
    await channel.send(embed=embed, view=view)
    await interaction.response.send_message(f"✅ Ticket-Panel wurde in {channel.mention} erstellt!", ephemeral=True)

# ----------------------------
# Start Bot
# ----------------------------
if __name__ == "__main__":
    # Ersetze hier lokal mit deinem Token (NICHT öffentlich teilen)
    TOKEN = "DEIN_TOKEN_HIER"
    if TOKEN == "DEIN_TOKEN_HIER" or not TOKEN:
        print("❌ Bitte setze deinen Bot-Token in der Variable TOKEN im Script.")
    else:
        bot.run(TOKEN)
