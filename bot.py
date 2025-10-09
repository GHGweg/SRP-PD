import os
import threading
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask

# ----------------------------
# Flask-Statusseite
# ----------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot läuft!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Flask in einem Thread starten
threading.Thread(target=run_flask).start()

# ----------------------------
# Discord-Bot
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

# ----------------------------
# Hilfsfunktion für Rollen
# ----------------------------
def get_role_by_name(guild, name):
    for role in guild.roles:
        if role.name == name:
            return role
    return None

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
# /cop-kick Befehl
# ----------------------------
@bot.tree.command(name="cop-kick", description="Mitglied kündigen")
@app_commands.describe(member="Mitglied auswählen", grund="Grund angeben", teamsperre="Teamsperre hinzufügen? (true/false)")
async def cop_kick(interaction: discord.Interaction, member: discord.Member, grund: str, teamsperre: bool = False):
    roles_to_remove = [role for role in member.roles if role != interaction.guild.default_role]
    if roles_to_remove:
        await member.remove_roles(*roles_to_remove)

    besucher_role = get_role_by_name(interaction.guild, ROLLE_BESUCHER)
    if besucher_role:
        await member.add_roles(besucher_role)

    if teamsperre:
        ts_role = get_role_by_name(interaction.guild, ROLLE_TEAMSCHLUSS)
        if ts_role:
            await member.add_roles(ts_role)

    embed = discord.Embed(title="❌ Kündigung", color=discord.Color.red())
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="⏱️ Teamsperre", value="✅ Ja" if teamsperre else "❌ Nein", inline=False)
    embed.add_field(name="📅 Datum", value=interaction.created_at.strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)

# ----------------------------
# /up-rank Befehl
# ----------------------------
@bot.tree.command(name="up-rank", description="Mitglied befördern")
@app_commands.describe(member="Mitglied auswählen", neue_rolle="Neue Rolle geben", grund="Grund angeben")
async def up_rank(interaction: discord.Interaction, member: discord.Member, neue_rolle: discord.Role, grund: str):
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

# ----------------------------
# /down-rank Befehl
# ----------------------------
@bot.tree.command(name="down-rank", description="Mitglied degradieren")
@app_commands.describe(member="Mitglied auswählen", neue_rolle="Neue Rolle geben", grund="Grund angeben")
async def down_rank(interaction: discord.Interaction, member: discord.Member, neue_rolle: discord.Role, grund: str):
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
# /cop-warn Befehl
# ----------------------------
@bot.tree.command(name="cop-warn", description="Mitglied verwarnen")
@app_commands.describe(member="Mitglied auswählen", grund="Grund angeben", stufe="Warnstufe (1 oder 2)")
async def cop_warn(interaction: discord.Interaction, member: discord.Member, grund: str, stufe: int):
    colors = {1: discord.Color.yellow(), 2: discord.Color.orange()}
    emojis = {1: "⚠️", 2: "⚠️⚠️"}

    if stufe == 1:
        role = get_role_by_name(interaction.guild, ROLLE_1_WARN)
        if role:
            await member.add_roles(role)
    elif stufe == 2:
        role = get_role_by_name(interaction.guild, ROLLE_2_WARN)
        if role:
            await member.add_roles(role)

    embed = discord.Embed(
        title=f"{emojis.get(stufe,'⚠️')} Verwarnung (Stufe {stufe})",
        color=colors.get(stufe, discord.Color.greyple())
    )
    embed.add_field(name="👤 Mitglied", value=member.mention, inline=False)
    embed.add_field(name="📝 Grund", value=grund, inline=False)
    embed.add_field(name="📅 Datum", value=interaction.created_at.strftime("%d.%m.%Y"), inline=False)
    await interaction.response.send_message(embed=embed)

# ----------------------------
# Bot starten
# ----------------------------
if __name__ == "__main__":
    token = os.getenv("TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ Kein TOKEN gefunden. Bitte als Environment Variable setzen.")
