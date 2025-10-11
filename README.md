⚙️ Übersicht

Dieser Bot ist speziell für RP- oder Verwaltungsserver entwickelt und bietet:
	•	👮 Cop- & Team-Befehle
	•	⚠️ Verwarnsystem
	•	⬆️ Up- & Down-Rank Funktionen
	•	👥 Team-Aufnahme via /neuer-teamler
	•	🔒 Zugriff nur für autorisierte Rollen

	👑 Befehle & Erklärungen

🏓 /ping

Testbefehl
Antwortet mit „🏓 Pong!“, um zu prüfen, ob der Bot aktiv ist.

Keine Berechtigungen nötig.

⸻

❌ /cop-kick

Ein Mitglied aus dem Polizeiteam entfernen.
Parameter:
	•	member → Das betroffene Mitglied
	•	grund → Warum es gekündigt wird
	•	teamsperre → true/false, ob eine Teamsperre vergeben wird

Aktionen:
	•	Entfernt alle Rollen außer @everyone
	•	Fügt 🧳 | Besucher hinzu
	•	Wenn teamsperre=True: fügt ❌ | Ausbildungssperre hinzu
	•	Sendet ein Embed mit Name, Grund, Teamsperre und Datum

⸻

⚠️ /cop-warn

Verwarnung für Polizeimitglieder.
Parameter:
	•	member → Das betroffene Mitglied
	•	grund → Grund der Verwarnung
	•	stufe → 1 oder 2

Aktionen:
	•	Stufe 1 → fügt Rolle ❌ | 1.Abmahnung hinzu
	•	Stufe 2 → fügt Rolle ❌ | 2.Abmahnung hinzu
	•	Sendet ein Embed mit Name, Grund, Stufe und Datum

⸻

🧳 /team-kick

Ein Mitglied aus dem Team entfernen.
Parameter:
	•	member → Das betroffene Mitglied
	•	grund → Grund für den Kick
	•	teamsperre → true/false

Aktionen:
	•	Entfernt alle Rollen außer @everyone
	•	Fügt folgende Rollen immer hinzu:
	•	Verifiziert
	•	» Mitglied
	•	Falls teamsperre=True: fügt zusätzlich Teamsperre hinzu
	•	Sendet ein Embed mit Name, Grund, Teamsperre und Datum

⸻

⚠️ /team-warn

Teammitglied verwarnen.
Parameter:
	•	member → Mitglied
	•	grund → Verwarnungsgrund
	•	stufe → 1 oder 2
	•	dauerhaft → true/false
	•	zeit → Freitext für Dauer (z. B. „7 Tage“ oder „24 Stunden“)

Aktionen:
	•	Temporäre Warnung:
	•	Stufe 1 → Team Warn 1
	•	Stufe 2 → Team Warn 2
	•	Dauerhafte Warnung:
	•	Stufe 1 → Team Warn 1 (Dauerhaft)
	•	Stufe 2 → Team Warn 2 (Dauerhaft)
	•	Sendet Embed mit:
	•	Mitglied
	•	Grund
	•	Stufe
	•	Dauerhaft Ja/Nein
	•	Zeit (wenn angegeben)
	•	Datum

Der Bot entfernt temporäre Verwarnungen nicht automatisch — sie sind rein informativ.

⸻

⬆️ /up-rank

Ein Mitglied befördern.
Parameter:
	•	member → Mitglied
	•	neue_rolle → Neue, höhere Rolle
	•	grund → Begründung

Aktionen:
	•	Fügt die neue Rolle hinzu
	•	Sendet Embed mit Mitglied, neuer Rolle, Grund und Datum

⸻

⬇️ /down-rank

Ein Mitglied degradieren.
Parameter:
	•	member → Mitglied
	•	neue_rolle → Neue, niedrigere Rolle
	•	grund → Begründung

Aktionen:
	•	Fügt die neue Rolle hinzu
	•	Sendet Embed mit Mitglied, neuer Rolle, Grund und Datum

⸻

👥 /neuer-teamler

Ein neues Teammitglied aufnehmen.
Parameter:
	•	member → Das neue Mitglied
	•	rolle → Die Teamrolle (z. B. „Support“, „Ausbilder“ etc.)
	•	grund → optional

Aktionen:
	•	Fügt die ausgewählte Rolle hinzu
	•	Fügt zusätzlich automatisch die Rolle staff hinzu
	•	Sendet Embed mit:
	•	Mitglied
	•	Neue Rolle
	•	Zusatzrolle „staff“
	•	Grund (falls angegeben)
	•	Datum

⸻

🔒 Zugriffsrechte

Nur Mitglieder mit mindestens einer dieser Rollen dürfen Befehle ausführen:
	•	✴ ⊶▬⊶▬ 𝐀𝐛𝐭𝐞𝐢𝐥𝐮𝐧𝐠𝐞𝐧 ▬⊷▬⊷ ✴
	•	Teamverwaltung

Alle anderen Nutzer bekommen eine Fehlermeldung wie:

❌ Du hast keine Berechtigung, diesen Befehl zu verwenden.
