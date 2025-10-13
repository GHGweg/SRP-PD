#!/usr/bin/env python3
import os
import re
import datetime
import threading
import discord
from discord import app_commands, ui
from discord.ext import commands
from flask import Flask

# ----------------------------
# Logging (Dateibasierte Logs)
# ----------------------------
LOG_DIR = "/home/hodenkobold/bot-Logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log(msg: str):
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    fname = os.path.join(LOG_DIR, f"bot-{date_str}.log")
    line = f"[{timestamp}] {msg}\n"
    try:
        with open(fname, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print("Fehler beim Schreiben der Logdatei:", e)
    # auch auf stdout
    print(line, end="")

# ----------------------------
# Kleine Hilfsfunktionen
# ----------------------------
def sanitize_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^a-z0-9\-]", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    if not name:
        return "user"
    return name[:90]  # limit length

# ----------------------------
# Flask-Statusseite (optional)
# ----------------------------
app = Flask(__name__)
@app.route("/")
def home():
    return "✅ Bot läuft!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

# ----------------------------
# Discord Bot Setup
# ----------------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = False
bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------------------
# Rollen-Konstanten (anpassen falls nötig)
# ----------------------------
ROLLE_ABTEILUNG = "✴ ⊶▬⊶▬ 𝐀𝐛𝐭𝐞𝐢𝐥𝐮𝐧𝐠𝐞𝐧 ▬⊷▬⊷ ✴"
ROLLE_TEAMVERWALTUNG = "Teamverwaltung"
ROLLE_STAFF = "staff"
ROLLE_HIGH_TEAM = "┏―――――:gem:High Team:gem:――――┛"
ROLLE_BW_AUSSTEHEND = "Bewerbungs Gespräch ausstehend"

ROLLE_BESUCHER = "🧳 | Besucher"
ROLLE_TEAMSCHLUSS = "❌ | Ausbildungssperre"
ROLLE_VERIFIZIERT = "Verifiziert"
ROLLE_MITGLIED = "» Mitglied"

ROLLE_WARN_1 = "❌ | 1.Abmahnung"
ROLLE_WARN_2 = "❌ | 2.Abmahnung"
ROLLE_TEAMWARN_1 = "Team Warn 1"
ROLLE_TEAMWARN_2 = "Team Warn 2"
ROLLE_TEAMWARN_1_DAUER = "Team Warn 1 (Dauerhaft)"
ROLLE_TEAMWARN_2_DAUER = "Team Warn 2 (Dauerhaft)"

# ----------------------------
# Hilfsfunktionen Rollen & Rechte
# ----------------------------
def get_role_by_name(guild: discord.Guild, name: str):
    if not name:
        return None
    return discord.utils.get(guild.roles, name=name)

def has_admin_permission(member: discord.Member) -> bool:
    names = [r.name for r in member.roles]
    return (ROLLE_ABTEILUNG in names) or (ROLLE_TEAMVERWALTUNG in names)

# ----------------------------
# On ready
# ----------------------------
@bot.event
async def on_ready():
    log(f"Bot ist online als {bot.user} (id: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        log(f"Slash-Commands synchronisiert: {len(synced)}")
    except Exception as e:
        log(f"Fehler beim Sync: {e}")

# ----------------------------
# /ping
# ----------------------------
@bot.tree.command(name="ping", description="Testet, ob der Bot antwortet.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")
    log(f"/ping von {interaction.user} in {interaction.guild.name}")

# ----------------------------
# /cop-kick
# ----------------------------
@bot.tree.command(name="cop-kick", description="Mitglied aus dem Cop-Team entfernen.")
@app_commands.describe(member="Mitglied auswählen", grund="Grund angeben", teamsperre="Teamsperre hinzufügen? (true/false)")
async def cop_kick(interaction: discord.Interaction, member: discord.Member, grund: str, teamsperre: bool = False):
    if not has_admin_permission(interaction.user):
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return
    # remove all roles except @everyone
    roles_to_remove = [r for r in member.roles if r != interaction.guild.default_role]
    if roles_to_remove:
        try:
            await member.remove_roles(*roles_to_remove, reason=f"cop-kick by {interaction.user}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Bot hat nicht die nötigen Rechte, Rollen zu entfernen.", ephemeral=True)
            return

    besucher = get_role_by_name(interaction.guild, ROLLE_BESUCHER)
    if besucher:
        try:
            await member.add_roles(besucher, reason=f"cop-kick by {interaction.user}")
        except discord.Forbidden:
            pass

    if teamsperre:
        ts = get_role_by_name(interaction.guild, ROLLE_TEAMSCHLUSS)
        if ts:
            try:
                await member.add_roles(ts, reason=f"cop-kick by {interaction.user}")
            except discord.Forbidden:
                pass

    embed = discord.Embed(title="❌ Cop-Kick", color=discord.Color.red())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="🚫 Teamsperre", value="✅ Ja" if teamsperre else "❌ Nein", inline=False)
    embed.add_field(name="📅 Datum", value=datetime.datetime.utcnow().strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)
    log(f"cop-kick: {member} by {interaction.user} | teamsperre={teamsperre} | grund={grund}")

# ----------------------------
# /cop-warn
# ----------------------------
@bot.tree.command(name="cop-warn", description="Mitglied verwarnen (Cop).")
@app_commands.describe(member="Mitglied auswählen", grund="Grund angeben", stufe="Warnstufe (1 oder 2)")
async def cop_warn(interaction: discord.Interaction, member: discord.Member, grund: str, stufe: int):
    if not has_admin_permission(interaction.user):
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return
    if stufe not in (1,2):
        await interaction.response.send_message("⚠️ Stufe muss 1 oder 2 sein.", ephemeral=True)
        return
    role_name = ROLLE_WARN_1 if stufe == 1 else ROLLE_WARN_2
    role = get_role_by_name(interaction.guild, role_name)
    if role:
        try:
            await member.add_roles(role, reason=f"cop-warn by {interaction.user}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Bot hat keine Rechte, die Rolle zu vergeben.", ephemeral=True)
            return
    embed = discord.Embed(title=f"⚠️ Verwarnung (Cop) Stufe {stufe}", color=discord.Color.orange())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="📅 Datum", value=datetime.datetime.utcnow().strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)
    log(f"cop-warn: {member} by {interaction.user} | stufe={stufe} | grund={grund}")

# ----------------------------
# /team-kick
# ----------------------------
@bot.tree.command(name="team-kick", description="Mitglied aus dem Team entfernen.")
@app_commands.describe(member="Mitglied auswählen", grund="Grund angeben", teamsperre="Teamsperre hinzufügen? (true/false)")
async def team_kick(interaction: discord.Interaction, member: discord.Member, grund: str, teamsperre: bool = False):
    if not has_admin_permission(interaction.user):
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return
    # remove all roles
    roles_to_remove = [r for r in member.roles if r != interaction.guild.default_role]
    if roles_to_remove:
        try:
            await member.remove_roles(*roles_to_remove, reason=f"team-kick by {interaction.user}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Bot hat nicht die nötigen Rechte, Rollen zu entfernen.", ephemeral=True)
            return

    # add Verifiziert + » Mitglied
    verifiziert = get_role_by_name(interaction.guild, ROLLE_VERIFIZIERT)
    mitglied = get_role_by_name(interaction.guild, ROLLE_MITGLIED)
    added = []
    if verifiziert:
        try:
            await member.add_roles(verifiziert, reason=f"team-kick by {interaction.user}")
            added.append(verifiziert.name)
        except discord.Forbidden:
            pass
    if mitglied:
        try:
            await member.add_roles(mitglied, reason=f"team-kick by {interaction.user}")
            added.append(mitglied.name)
        except discord.Forbidden:
            pass

    if teamsperre:
        ts = get_role_by_name(interaction.guild, ROLLE_TEAMSCHLUSS)
        if ts:
            try:
                await member.add_roles(ts, reason=f"team-kick by {interaction.user}")
                added.append(ts.name)
            except discord.Forbidden:
                pass

    embed = discord.Embed(title="❌ Team-Kick", color=discord.Color.red())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="📋 Neue Rollen", value=", ".join(added) if added else "Keine", inline=False)
    embed.add_field(name="📅 Datum", value=datetime.datetime.utcnow().strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)
    log(f"team-kick: {member} by {interaction.user} | teamsperre={teamsperre} | added={added} | grund={grund}")

# ----------------------------
# /team-warn
# ----------------------------
@bot.tree.command(name="team-warn", description="Teammitglied verwarnen.")
@app_commands.describe(member="Mitglied auswählen", grund="Grund", stufe="1 oder 2", dauerhaft="Dauerhaft? (true/false)", zeit="Optional: Zeit (z. B. 7 Tage)")
async def team_warn(interaction: discord.Interaction, member: discord.Member, grund: str, stufe: int, dauerhaft: bool = False, zeit: str = None):
    if not has_admin_permission(interaction.user):
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return
    if stufe not in (1,2):
        await interaction.response.send_message("⚠️ Stufe muss 1 oder 2 sein.", ephemeral=True)
        return

    role_name = None
    if stufe == 1:
        role_name = ROLLE_TEAMWARN_1_DAUER if dauerhaft else ROLLE_TEAMWARN_1
    else:
        role_name = ROLLE_TEAMWARN_2_DAUER if dauerhaft else ROLLE_TEAMWARN_2

    role = get_role_by_name(interaction.guild, role_name)
    if role:
        try:
            await member.add_roles(role, reason=f"team-warn by {interaction.user}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Bot hat keine Rechte, die Rolle zu vergeben.", ephemeral=True)
            return

    embed = discord.Embed(title=f"⚠️ Team-Warn Stufe {stufe}", color=discord.Color.orange())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="⏱️ Dauerhaft", value="✅ Ja" if dauerhaft else "❌ Nein", inline=True)
    if not dauerhaft and zeit:
        embed.add_field(name="⌛ Zeit (Info)", value=zeit, inline=True)
    embed.add_field(name="📅 Datum", value=datetime.datetime.utcnow().strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)
    log(f"team-warn: {member} by {interaction.user} | stufe={stufe} | dauerhaft={dauerhaft} | zeit={zeit} | grund={grund}")

# ----------------------------
# /neuer-teamler
# ----------------------------
@bot.tree.command(name="neuer-teamler", description="Neues Teammitglied aufnehmen (vergibt Rolle + staff)")
@app_commands.describe(member="Mitglied auswählen", rolle="Rolle wählen", grund="Optionaler Grund")
async def neuer_teamler(interaction: discord.Interaction, member: discord.Member, rolle: discord.Role, grund: str = None):
    if not has_admin_permission(interaction.user):
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return

    staff = get_role_by_name(interaction.guild, ROLLE_STAFF)
    added = []
    try:
        await member.add_roles(rolle, reason=f"neuer-teamler by {interaction.user}")
        added.append(rolle.name)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Bot hat keine Rechte, die Rolle zu vergeben.", ephemeral=True)
        return
    if staff:
        try:
            await member.add_roles(staff, reason=f"neuer-teamler by {interaction.user}")
            added.append(staff.name)
        except discord.Forbidden:
            pass

    embed = discord.Embed(title="👥 Neuer Teamler", color=discord.Color.blue())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="🏷️ Neue Rolle", value=rolle.mention, inline=False)
    if staff:
        embed.add_field(name="🧩 Zusatzrolle", value=staff.mention, inline=False)
    if grund:
        embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="📅 Datum", value=datetime.datetime.utcnow().strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)
    log(f"neuer-teamler: {member} by {interaction.user} | added={added} | grund={grund}")

# ----------------------------
# /up-rank & /down-rank (nur Ankündigung)
# ----------------------------
@bot.tree.command(name="up-rank", description="Beförderung ankündigen (keine automatische Rollenzuweisung)")
@app_commands.describe(member="Mitglied auswählen", neue_rolle="Neue Rolle (wird nicht automatisch vergeben)", grund="Grund")
async def up_rank(interaction: discord.Interaction, member: discord.Member, neue_rolle: discord.Role, grund: str):
    if not has_admin_permission(interaction.user):
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return
    embed = discord.Embed(title="⬆️ Beförderung", color=discord.Color.green())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="➡️ Neue Rolle (Ankündigung)", value=neue_rolle.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="📅 Datum", value=datetime.datetime.utcnow().strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)
    log(f"up-rank (announce): {member} by {interaction.user} | neue_rolle={neue_rolle.name} | grund={grund}")

@bot.tree.command(name="down-rank", description="Degradierung ankündigen (keine automatische Rollenzuweisung)")
@app_commands.describe(member="Mitglied auswählen", neue_rolle="Neue Rolle (wird nicht automatisch vergeben)", grund="Grund")
async def down_rank(interaction: discord.Interaction, member: discord.Member, neue_rolle: discord.Role, grund: str):
    if not has_admin_permission(interaction.user):
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return
    embed = discord.Embed(title="⬇️ Degradierung", color=discord.Color.orange())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="➡️ Neue Rolle (Ankündigung)", value=neue_rolle.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="📅 Datum", value=datetime.datetime.utcnow().strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)
    log(f"down-rank (announce): {member} by {interaction.user} | neue_rolle={neue_rolle.name} | grund={grund}")

# ----------------------------
# Ticket System (Panel, Ticket-Erstellung, Close)
# ----------------------------
class TicketPanelView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # Buttons
        self.add_item(ui.Button(label="💬 Allgemeine Fragen", style=discord.ButtonStyle.green, custom_id="ticket_allgemein"))
        self.add_item(ui.Button(label="📝 Teambeschwerde", style=discord.ButtonStyle.red, custom_id="ticket_beschwerde"))
        self.add_item(ui.Button(label="🎓 Bewerbungsgespräch", style=discord.ButtonStyle.blurple, custom_id="ticket_bewerbung"))

class TicketCloseView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label="❌ Ticket schließen", style=discord.ButtonStyle.red, custom_id="ticket_close"))

@bot.tree.command(name="ticket-setup", description="Sendet das Ticket-Panel (Embed mit Buttons) in einen Kanal.")
@app_commands.describe(channel="Channel für das Ticket-Panel")
async def ticket_setup(interaction: discord.Interaction, channel: discord.TextChannel):
    if not has_admin_permission(interaction.user):
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return
    # ensure category exists
    cat = discord.utils.get(interaction.guild.categories, name="Bewerbungsgespräch")
    if not cat:
        cat = await interaction.guild.create_category("Bewerbungsgespräch", reason="Ticket-Kategorie anlegen")

    embed = discord.Embed(
        title="🎫 Support & Tickets",
        description="Klicke auf einen Button, um ein privates Ticket zu öffnen:\n\n"
                    "💬 Allgemeine Fragen\n"
                    "📝 Teambeschwerde\n"
                    "🎓 Bewerbungsgespräch (nur mit passender Rolle)",
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Ein Ticket ist privat: nur du und Staff sehen es.")
    await channel.send(embed=embed, view=TicketPanelView())
    await interaction.response.send_message(f"✅ Ticket-Panel wurde in {channel.mention} gesendet.", ephemeral=True)
    log(f"ticket-setup by {interaction.user} in {channel.name}")

@bot.event
async def on_interaction(interaction: discord.Interaction):
    # only handle component interactions here
    try:
        if interaction.type != discord.InteractionType.component:
            return
    except Exception:
        return

    custom_id = interaction.data.get("custom_id")
    user = interaction.user
    guild = interaction.guild

    # Ticket panel buttons
    if custom_id in ("ticket_allgemein", "ticket_beschwerde", "ticket_bewerbung"):
        # check role for Bewerbung
        if custom_id == "ticket_bewerbung":
            role = get_role_by_name(guild, ROLLE_BW_AUSSTEHEND)
            if not role or role not in user.roles:
                await interaction.response.send_message("🚫 Du darfst keine Bewerbungsgespräch-Tickets erstellen.", ephemeral=True)
                return

        # make sure category exists
        category = discord.utils.get(guild.categories, name="Bewerbungsgespräch")
        if not category:
            category = await guild.create_category("Bewerbungsgespräch", reason="Ticket-Kategorie anlegen")

        if custom_id == "ticket_allgemein":
            cname = f"frage-von-{sanitize_name(user.name)}"
            title = "Frage"
            desc = f"Ticket von {user.mention} — Allgemeine Frage"
            is_bewerbung = False
        elif custom_id == "ticket_beschwerde":
            cname = f"teambeschwerde-von-{sanitize_name(user.name)}"
            title = "Teambeschwerde"
            desc = f"Ticket von {user.mention} — Teambeschwerde"
            is_bewerbung = False
        else:  # ticket_bewerbung
            cname = f"bewerbung-von-{sanitize_name(user.name)}"
            title = "Bewerbungsgespräch"
            desc = f"Bewerbungsgespräch von {user.mention}"
            is_bewerbung = True

        # Avoid duplicate ticket channel
        existing = discord.utils.get(guild.text_channels, name=cname)
        if existing:
            await interaction.response.send_message(f"❗ Du hast bereits ein Ticket: {existing.mention}", ephemeral=True)
            return

        # permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            bot.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        staff_role = get_role_by_name(guild, ROLLE_STAFF)
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        if is_bewerbung:
            high_role = get_role_by_name(guild, ROLLE_HIGH_TEAM)
            if high_role:
                overwrites[high_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        # create channel
        ticket_channel = await guild.create_text_channel(cname, overwrites=overwrites, category=category, reason=f"Ticket erstellt von {user}")
        log(f"Ticket erstellt: {cname} by {user} | type={'bewerbung' if is_bewerbung else 'normal'}")

        # send ticket embed + close button
        ticket_embed = discord.Embed(title=f"🎫 {title}: {user.display_name}", description=desc + "\n\nBitte beschreibe dein Anliegen.", color=discord.Color.blue())
        ticket_embed.add_field(name="Erstellt von", value=user.mention, inline=True)
        ticket_embed.add_field(name="Typ", value=title, inline=True)
        ticket_embed.add_field(name="Datum", value=datetime.datetime.utcnow().strftime("%d.%m.%Y"), inline=False)

        # close button behavior differs for bewerbung (require HIGH_TEAM) vs others (require STAFF)
        view = TicketCloseView()
        await ticket_channel.send(content=(staff_role.mention if staff_role else None), embed=ticket_embed, view=view)
        await interaction.response.send_message(f"✅ Ticket erstellt: {ticket_channel.mention}", ephemeral=True)
        return

    # Ticket close button
    if custom_id == "ticket_close":
        # check permissions based on channel name
        channel = interaction.channel
        user_roles = [r.name for r in interaction.user.roles]
        name = channel.name if channel else ""
        if name.startswith("bewerbung"):
            # require high team
            if ROLLE_HIGH_TEAM not in user_roles:
                await interaction.response.send_message("🚫 Nur High Team darf Bewerbungstickets schließen.", ephemeral=True)
                return
        else:
            # require staff
            if ROLLE_STAFF not in user_roles:
                await interaction.response.send_message("🚫 Nur Staff darf Tickets schließen.", ephemeral=True)
                return
        await interaction.response.send_message("🗑️ Ticket wird geschlossen...", ephemeral=True)
        try:
            await channel.delete(reason=f"Ticket geschlossen von {interaction.user}")
            log(f"Ticket geschlossen: {name} by {interaction.user}")
        except Exception as e:
            log(f"Fehler beim Löschen Ticket {name}: {e}")
        return

# ----------------------------
# Abmeldung Panel & Modal
# ----------------------------
class AbmeldungModal(ui.Modal, title="Abmeldung einreichen"):
    von = ui.TextInput(label="Von (Datum oder Datum+Uhrzeit)", placeholder="z. B. 2025-10-20 oder 2025-10-20 08:00", required=True, max_length=50)
    bis = ui.TextInput(label="Bis (Datum oder Datum+Uhrzeit)", placeholder="z. B. 2025-10-22 oder 2025-10-22 18:00", required=True, max_length=50)
    grund = ui.TextInput(label="Grund", style=discord.TextStyle.long, placeholder="Kurz den Grund beschreiben", required=True, max_length=1000)

    def __init__(self, announce_channel_id: int):
        super().__init__()
        self.announce_channel_id = announce_channel_id

    async def on_submit(self, interaction: discord.Interaction):
        # post the announcement
        guild = interaction.guild
        channel = guild.get_channel(self.announce_channel_id)
        if channel is None:
            await interaction.response.send_message("❌ Zielkanal für Abmeldung nicht gefunden.", ephemeral=True)
            return

        embed = discord.Embed(title="📢 Abmeldung", color=discord.Color.gold())
        embed.add_field(name="👤 Benutzer", value=interaction.user.mention, inline=False)
        embed.add_field(name="📅 Von", value=self.von.value, inline=True)
        embed.add_field(name="📅 Bis", value=self.bis.value, inline=True)
        embed.add_field(name="📝 Grund", value=self.grund.value, inline=False)
        embed.add_field(name="📅 Datum (Einreichung)", value=datetime.datetime.utcnow().strftime("%d.%m.%Y %H:%M UTC"), inline=False)
        try:
            await channel.send(embed=embed)
            await interaction.response.send_message("✅ Abmeldung gesendet!", ephemeral=True)
            log(f"Abmeldung: {interaction.user} | von={self.von.value} | bis={self.bis.value} | grund={self.grund.value} | announce_channel={channel.name}")
        except Exception as e:
            await interaction.response.send_message("❌ Konnte die Abmeldung nicht senden.", ephemeral=True)
            log(f"Fehler Abmeldung senden: {e}")

@ui.button(label="📅 Abmeldung einreichen", style=discord.ButtonStyle.primary, custom_id="abmeldung_button")
async def _dummy_button_callback(interaction: discord.Interaction, button: ui.Button):
    # dummy placeholder — actual buttons created in view class below
    await interaction.response.send_message("This is a placeholder.", ephemeral=True)

class AbmeldungPanelView(ui.View):
    def __init__(self, announce_channel_id: int):
        super().__init__(timeout=None)
        self.announce_channel_id = announce_channel_id
        # create button that opens modal
        self.add_item(AbmeldungButton(announce_channel_id))

class AbmeldungButton(ui.Button):
    def __init__(self, announce_channel_id: int):
        super().__init__(label="📅 Abmeldung einreichen", style=discord.ButtonStyle.primary, custom_id=f"abmeldung_button:{announce_channel_id}")
        self.announce_channel_id = announce_channel_id

    async def callback(self, interaction: discord.Interaction):
        modal = AbmeldungModal(announce_channel_id=self.announce_channel_id)
        await interaction.response.send_modal(modal)

@bot.tree.command(name="abmeldung", description="Erstellt ein Abmelde-Panel (Embed + Button) in einem Kanal.")
@app_commands.describe(panel_channel="Kanal, in dem das Abmelde-Panel gesendet wird", announce_channel="Kanal, in dem die Abmelde-Ankündigungen gepostet werden")
async def abmeldung(interaction: discord.Interaction, panel_channel: discord.TextChannel, announce_channel: discord.TextChannel):
    if not has_admin_permission(interaction.user):
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return

    view = AbmeldungPanelView(announce_channel_id=announce_channel.id)
    embed = discord.Embed(title="📅 Abmeldung", description="Klicke auf den Button und fülle das Formular (Von / Bis / Grund) aus. Die Abmeldung wird im Ankündigungs-Kanal gepostet.", color=discord.Color.green())
    embed.add_field(name="📢 Ankündigungskanal", value=announce_channel.mention, inline=False)
    await panel_channel.send(embed=embed, view=view)
    await interaction.response.send_message(f"✅ Abmelde-Panel gesendet nach {panel_channel.mention}. Ankündigungen gehen an {announce_channel.mention}.", ephemeral=True)
    log(f"abmeldung-panel erstellt by {interaction.user} | panel_channel={panel_channel.name} | announce_channel={announce_channel.name}")

# ----------------------------
# Start Bot (TOKEN Platzhalter)
# ----------------------------
if __name__ == "__main__":
    TOKEN = "DEIN_BOT_TOKEN_HIER"
    if TOKEN == "DEIN_BOT_TOKEN_HIER" or not TOKEN:
        print("❌ Bitte setze deinen Discord-Bot TOKEN in der Variable TOKEN (nur lokal).")
    else:
        log("Starte Bot...")
        bot.run(TOKEN)
