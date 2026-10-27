---
ShowToc: true
TocOpen: true
base_hash: 1d8110e16aa57ebd7e50254006d0e09af59d7db67ae562e33a70c427db95f608
cover:
  alt: obsidian-http-mcp
  caption: ''
  image: "editorial-cover.webp"
  relative: true
date: 2025-09-28
description: Kommuniziere mit deinem Remote-Obsidian-Vault über den HTTP-MCP-Server.
draft: false
homepage:
  featured: false
  section: engineering
  state: archive
  teaser: Ein HTTP-MCP-Server macht den Obsidian-Vault für KI-Clients zugänglich.
    Ein Rückblick auf das inzwischen eingestellte Projekt.
  title: Obsidian-Notizen per MCP nutzen
project:
  status: discontinued
slug: obsidian-http-mcp
tags:
- obsidian
- mcp
title: 'Mit deinen Obsidian-Notizen chatten: mein HTTP-MCP-Server'
translation_lock: true
---

{{< alert type="warning" title="" >}}
Leider wird der MCP-Server nicht mehr benötigt, da das gesamte [n8n AI agent](https://blog.matschcode.de/en/projects/development/n8n-ai-assistant/) durch den Hermes-Agenten ersetzt wurde.
{{< /alert >}}

## Einleitung
Wenn du meine Obsidian-Konfiguration verfolgt hast, weißt du, dass ich es liebe, meine Notizen mit Syncthing ([My Obsidian + Syncthing Setup: A Self-Hosted Cloud for Notes, Backups, and More](https://blog.matschcode.de/en/notes/self-hosting/obsidian-cloud-sync-setup/)) geräteübergreifend zu synchronisieren. Aber ich wollte mehr als nur Synchronisierung – ich wollte **intelligent mit meinen Notizen interagieren, überall und jederzeit**.

## Warum Obsidian HTTP MCP?
Deshalb habe ich **Obsidian HTTP MCP** entwickelt, einen auf [FastMCP](https://gofastmcp.com/getting-started/welcome) basierenden, ressourcenschonenden Server, der deinen Obsidian-Vault über HTTP mithilfe des MCP-Protokolls zugänglich macht.

Mit diesem Server kannst du:
- **KI-Clients** wie Cursor direkt mit deinem Vault verbinden und so die Suche in natürlicher Sprache, Analysen und sogar automatisierte Notizänderungen ermöglichen.
- **Deine Notizen bei Bedarf abfragen** – über Skripte, Dashboards oder jedes Gerät, das HTTP unterstützt.
- **Den Server schlank und schnell halten** dank der FastMCP-Basis.

Im Grunde ist dein Vault nicht mehr nur ein Speicherort – er wird zu einer interaktiven Wissensmaschine.

## So funktioniert es
Jede Notiz in deinem Vault wird als MCP-„Paket“ behandelt. Der Server stellt Endpunkte zum Lesen, Aktualisieren oder Analysieren dieser Pakete bereit. Die Verwendung des HTTP-Protokolls sorgt für Einfachheit, Sicherheit und Zugriffsmöglichkeiten hinter Standard-Firewalls.

Der eigentliche Spaß beginnt mit der **KI-Integration**. Du kannst deinen Desktop-KI-Assistenten bitten, Notizen zusammenzufassen, relevante Informationen zu finden oder sogar Inhalte auf Basis deines Vaults zu generieren – und das alles durch ganz normales Chatten. Es ist, als würdest du deinen Notizen ein eigenes Gehirn geben.

## Was es für „Nerdy Perks“ wert macht
- **KI-gestützte Workflows:** Chatte mit deinem Archiv, analysiere Inhalte oder bearbeite Notizen programmgesteuert.
- **Geräteübergreifender Zugriff:** Kommuniziere mit deinem Archiv über Skripte, mobile Apps oder Web-Tools.
- **Minimaler Aufwand:** Zustandslos und effizient, perfekt für schlanke Setups.
- **Hackbar:** Erstelle Bots, Dashboards oder Automatisierungen rund um deine Notizen.
- **Sicher:** Läuft hinter deiner bestehenden Sicherheitsinfrastruktur, ohne Cloud-Dienste zu benötigen.

### Beispiele für coole KI-Interaktionen
- **Suche und Zusammenfassungen in natürlicher Sprache:** Bitte deine KI, Notizen in einfachem Englisch zu finden oder zusammenzufassen.
- **Automatisierte Aktualisierung und Erstellung von Notizen:** Lass die KI Notizen erstellen oder bearbeiten, Sitzungsprotokolle entwerfen oder Lernkarten generieren.
- **Vault-Analysen & Erkenntnisse:** Verfolge Trends, Lücken und wiederkehrende Themen in deinen Notizen.
- **Persönlicher Wissensassistent:** Chatte mit deinem Vault, um Fragen zu beantworten, Zusammenhänge vorzuschlagen oder Themen zu empfehlen.
- **Code- und Workflow-Automatisierung:** Nutze die KI, um Skripte zu generieren, Notizen zu organisieren oder automatisierte Workflows auszulösen.

## Einrichtung
- Starte den MCP-Server auf deinem Remote-Server in einem Docker-Container mit einem einzigen Befehl.
- Füge die Client-Konfiguration zu deinem Desktop-KI-Client hinzu (z. B. Cursor):
```json
{
 "mcpServers": {
   "obsidian-http-mcp": {
     "transport": "http",
     "url": "http://localhost:9001/mcp",
     "headers": {
       "Authorization": "Bearer <MCP_API_KEY>"
     }
   }
 }
}
```
- Beginne, mit deinen Notizen zu interagieren.

Eine ausführlichere Beschreibung findest du im GitHub-Repository: [obsidian-http-mcp](https://github.com/matsch1/obsidian-http-mcp) – und fang noch heute an, mit deinen Notizen zu chatten!
	
## TL;DR
Obsidian HTTP MCP ist ein schlanker Server, der deinen Obsidian-Vault über HTTP mithilfe des MCP-Protokolls verfügbar macht. Damit kannst du KI-Clients wie Cursor mit deinen Notizen verbinden, um Suchanfragen in natürlicher Sprache, Zusammenfassungen, Analysen und automatisierte Änderungen durchzuführen. Führe ihn auf einem Remote-Server aus, verbinde deinen KI-Client und verwandle deinen Vault im Handumdrehen in eine interaktive, KI-gestützte Wissensmaschine. Schau dir das Ganze auf GitHub an: [obsidian-http-mcp](https://github.com/matsch1/obsidian-http-mcp)!