⚙️ Übersicht
Dieser Bot ist speziell für RP- oder Verwaltungsserver entwickelt und bietet: 
• 👮 Cop- & Team-Befehle 
• ⚠️ Verwarnsystem 
• ⬆️ Up- & Down-Rank Funktionen 
• 👥 Team-Aufnahme via /neuer-teamler 
• 🔒 Zugriff nur für autorisierte Rollen
• 🎫 Ticket-System mit Buttons für Allgemeine Fragen, Teambeschwerden und Bewerbungsgespräche

👑 Befehle & Erklärungen

🏓 /ping
Testbefehl. Antwortet mit „🏓 Pong!“, um zu prüfen, ob der Bot aktiv ist.
Keine Berechtigungen nötig.

❌ /cop-kick
Ein Mitglied aus dem Polizeiteam entfernen.
Parameter: 
• member → Das betroffene Mitglied 
• grund → Warum es gekündigt wird 
• teamsperre → true/false, ob eine Teamsperre vergeben wird
Aktionen: 
• Entfernt alle Rollen außer @everyone 
• Fügt 🧳 | Besucher hinzu 
• Wenn teamsperre=True: fügt ❌ | Ausbildungssperre hinzu 
• Sendet ein Embed mit Name, Grund, Teamsperre und Datum

⚠️ /cop-warn
Verwarnung für Polizeimitglieder.
Parameter: 
• member → Das betroffene Mitglied 
• grund → Grund der Verwarnung 
• stufe → 1 oder 2
Aktionen: 
• Stufe 1 → fügt Rolle ❌ | 1.Abmahnung hinzu 
• Stufe 2 → fügt Rolle ❌ | 2.Abmahnung hinzu 
• Sendet ein Embed mit Name, Grund, Stufe und Datum

🧳 /team-kick
Ein Mitglied aus dem Team entfernen.
Parameter: 
• member → Das betroffene Mitglied 
• grund → Grund für den Kick 
• teamsperre → true/false
Aktionen: 
• Entfernt alle Rollen außer @everyone 
• Fügt folgende Rollen immer hinzu: Verifiziert, » Mitglied 
• Falls teamsperre=True: fügt zusätzlich Teamsperre hinzu 
• Sendet ein Embed mit Name, Grund, Teamsperre und Datum

⚠️ /team-warn
Teammitglied verwarnen.
Parameter: 
• member → Mitglied 
• grund → Verwarnungsgrund 
• stufe → 1 oder 2 
• dauerhaft → true/false 
• zeit → Freitext für Dauer (z. B. „7 Tage“ oder „24 Stunden“)
Aktionen: 
• Temporäre Warnung: 
  - Stufe 1 → Team Warn 1 
  - Stufe 2 → Team Warn 2 
• Dauerhafte Warnung: 
  - Stufe 1 → Team Warn 1 (Dauerhaft) 
  - Stufe 2 → Team Warn 2 (Dauerhaft) 
• Sendet Embed mit: Mitglied, Grund, Stufe, Dauerhaft Ja/Nein, Zeit (wenn angegeben), Datum
Der Bot entfernt temporäre Verwarnungen nicht automatisch — sie sind rein informativ.

⬆️ /up-rank
Ein Mitglied befördern.
Parameter: 
• member → Mitglied 
• neue_rolle → Neue, höhere Rolle 
• grund → Begründung
Aktionen: 
• Fügt die neue Rolle hinzu 
• Sendet Embed mit Mitglied, neuer Rolle, Grund und Datum

⬇️ /down-rank
Ein Mitglied degradieren.
Parameter: 
• member → Mitglied 
• neue_rolle → Neue, niedrigere Rolle 
• grund → Begründung
Aktionen: 
• Fügt die neue Rolle hinzu 
• Sendet Embed mit Mitglied, neue Rolle, Grund und Datum

👥 /neuer-teamler
Ein neues Teammitglied aufnehmen.
Parameter: 
• member → Das neue Mitglied 
• rolle → Die Teamrolle (z. B. „Support“, „Ausbilder“ etc.) 
• grund → optional
Aktionen: 
• Fügt die ausgewählte Rolle hinzu 
• Fügt automatisch die Rolle staff hinzu 
• Sendet Embed mit: Mitglied, Neue Rolle, Zusatzrolle „staff“, Grund (falls angegeben), Datum

🔒 Zugriffsrechte
Nur Mitglieder mit mindestens einer dieser Rollen dürfen Befehle ausführen: 
• ✴ ⊶▬⊶▬ 𝐀𝐛𝐭𝐞𝐢𝐥𝐮𝐧𝐠𝐞𝐧 ▬⊷▬⊷ ✴ 
• Teamverwaltung
Alle anderen Nutzer bekommen eine Fehlermeldung:
❌ Du hast keine Berechtigung, diesen Befehl zu verwenden.

🎫 /ticket-setup
Mit diesem Befehl kann ein Administrator oder jemand mit der Rolle Teamverwaltung oder ✴ ⊶▬⊶▬ 𝐀𝐛𝐭𝐞𝐢𝐥𝐮𝐧𝐠𝐞𝐧 ▬⊷▬⊷ ✴ ein Ticket-Panel in einen gewünschten Kanal senden. Das Panel besteht aus einer Embed-Nachricht mit **drei Buttons**:

1. **Allgemeine Fragen** → Ticketname: `Frage-von-<username>`  
   - Kann von jedem erstellt werden  
   - Zugriff für Ticket-Ersteller + staff  
   - Ticket schließen nur durch staff

2. **Teambeschwerde** → Ticketname: `Teambeschwerde-von-<username>`  
   - Kann von jedem erstellt werden  
   - Zugriff für Ticket-Ersteller + staff  
   - Ticket schließen nur durch staff

3. **Bewerbungsgespräch** → Ticketname: `Bewerbung-von-<username>`  
   - **Nur** Nutzer mit Rolle `Bewerbungs Gespräch ausstehend` dürfen erstellen  
   - Zugriff für Ticket-Ersteller + staff  
   - Bearbeitung/Schließen nur durch Rolle `┏―――――:gem:High Team:gem:――――┛`

Alle Tickets werden in der Kategorie `Bewerbungsgespräch` erstellt. Das Ticket-Panel wird als Embed mit Buttons angezeigt.

💡 Hinweise
- Nutzt Discord Embeds und Buttons (`discord.ui`)  
- Bot benötigt Berechtigungen: Kanäle verwalten, Nachrichten senden, Nachrichten lesen  
- Ticket-Name wird automatisch aus dem Discord-Namen erstellt
- 


EINLADUNGS LINK:

https://discord.com/oauth2/authorize?client_id=1425967124903624746
