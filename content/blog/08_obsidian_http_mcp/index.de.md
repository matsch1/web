---
slug: "obsidian-http-mcp"
ShowToc: true
TocOpen: true
base_hash: 2a2fff609143c7d99ed791049e4646eb78e6ef1c9598cab6dbd1f850e9a6d4ff
cover:
  alt: obsidian-http-mcp
  caption: ''
  image: img1.png
  relative: true
date: 2025-09-28
description: Chat with your remote Obsidian vault using http mcp server.
draft: false
title: 'Chatten Sie mit Ihren Obsidian Notes: Einführung von HTTP MCP Server'
tags:
  - obsidian
  - mcp
---

## Einleitung
Wenn Sie mein Obsidian-Setup verfolgt haben, wissen Sie, dass ich meine Notizen gerne mit Syncthing ([My Obsidian + Syncthing Setup: A Self-Hosted Cloud for Notes, Backups, and More](https://matsch1.github.io/web/en/coding/07_obsidian_syncthing_cloud_setup/)) geräteübergreifend synchronisiere. Aber ich wollte mehr als nur synchronisieren - ich wollte **interact with my notes intelligently, anywhere, anytime**.

## Warum Obsidian HTTP MCP?
Deshalb habe ich **Obsidian HTTP MCP** entwickelt, einen leichtgewichtigen Server, der auf [FastMCP](https://gofastmcp.com/getting-started/welcome) aufbaut und Ihren Obsidian-Tresor über HTTP mit dem MCP-Protokoll zugänglich macht.

Mit diesem Server können Sie:
- **Connect AI clients** wie Cursor direkt auf Ihren Tresor zugreifen, was eine Suche in natürlicher Sprache, Analysen und sogar automatische Änderungen von Notizen ermöglicht.
- **Query your notes on demand** von Skripten, Dashboards oder jedem Gerät, das HTTP beherrscht.
- **Keep it lightweight and fast** dank der FastMCP-Stiftung.

Im Grunde ist Ihr Tresor nicht mehr nur ein Speicher - er wird zu einer interaktiven Wissensmaschine.

## Wie funktioniert es?
Jede Notiz in Ihrem Tresor wird als ein MCP-"Paket" behandelt. Der Server stellt Endpunkte zum Lesen, Aktualisieren oder Analysieren dieser Pakete bereit. Durch die Verwendung des HTTP-Transports sind die Dinge einfach, sicher und hinter Standard-Firewalls zugänglich.

Der eigentliche Spaß kommt mit **AI integration**. Sie können Ihren Desktop-KI-Assistenten bitten, Notizen zusammenzufassen, relevante Informationen zu finden oder sogar Inhalte auf der Grundlage Ihres Tresors zu generieren - und das alles in einem natürlichen Chat. Es ist, als würden Sie Ihren Notizen ein eigenes Gehirn geben.

## Was es Nerdy-Perks-würdig macht
- **AI-powered workflows:** Chatten Sie mit Ihrem Tresor, analysieren Sie Inhalte oder ändern Sie Notizen programmatisch.
- **Cross-device access:** Sprechen Sie mit Ihrem Tresor über Skripte, mobile Anwendungen oder Webtools.
- **Minimal overhead:** Zustandslos und effizient, perfekt für leichtgewichtige Setups.
- **Hackable:** Erstellen Sie Bots, Dashboards oder Automatisierungen rund um Ihre Notizen.
- **Secure:** Läuft hinter Ihrer bestehenden Sicherheit, ohne Cloud-Dienste zu benötigen.

### Beispiele für coole KI-Interaktionen
- **Natural-language search & summaries:** Bitten Sie Ihre KI, Notizen in einfachem Englisch zu finden oder zusammenzufassen.
- **Automated note updates & generation:** Lassen Sie die KI Notizen erstellen oder ändern, Sitzungsprotokolle entwerfen oder Karteikarten erstellen.
- **Vault analytics & insights:** Verfolgen Sie Trends, Lücken und wiederkehrende Themen in Ihren Notizen.
- **Personal knowledge assistant:** Chatten Sie mit Ihrem Tresor, um Fragen zu beantworten, Verbindungen vorzuschlagen oder Themen zu empfehlen.
- **Code & workflow automation:** Nutzen Sie KI, um Skripte zu erstellen, Notizen zu organisieren oder automatische Workflows auszulösen.

## Einrichtung
- Starten Sie den MCP-Server auf Ihrem Remote-Server in einem Docker-Container mit einem einzigen Befehl.
- Fügen Sie die Client-Konfiguration zu Ihrem Desktop-AI-Client (z. B. Cursor) hinzu:
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
- Beginnen Sie mit der Interaktion mit Ihren Notizen.

Eine ausführlichere Beschreibung finden Sie im GitHub-Repository: [obsidian-http-mcp](https://github.com/matsch1/obsidian-http-mcp) und beginnen Sie noch heute mit Ihren Notizen zu chatten!
	
## TL;DR
Obsidian HTTP MCP ist ein leichtgewichtiger Server, der Ihren Obsidian-Tresor über HTTP mit dem MCP-Protokoll zugänglich macht. Damit können Sie KI-Clients wie Cursor mit Ihren Notizen verbinden, um in natürlicher Sprache zu suchen, Zusammenfassungen zu erstellen, Analysen durchzuführen und automatische Änderungen vorzunehmen. Führen Sie es auf einem Remote-Server aus, verbinden Sie Ihren KI-Client und verwandeln Sie Ihren Tresor sofort in eine interaktive, KI-gestützte Wissensmaschine. Probieren Sie es auf GitHub [obsidian-http-mcp](https://github.com/matsch1/obsidian-http-mcp) aus!
