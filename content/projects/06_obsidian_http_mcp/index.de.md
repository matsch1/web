---
ShowToc: true
TocOpen: true
base_hash: fec459eee2138418a2f56d28acb30568e8f942b3dafff9336f6504797fd2f525
cover:
  alt: obsidian-http-mcp
  caption: ''
  image: img1.png
  relative: true
date: 2025-09-28
description: Kommuniziere mit deinem Remote-Obsidian-Vault über den HTTP-MCP-Server.
draft: false
slug: obsidian-http-mcp
tags:
- obsidian
- mcp
title: 'Mit Ihren Obsidian-Notizen chatten: Vorstellung des HTTP-MCP-Servers'
---

{{< alert type="warning" title="" >}}
Leider wird der MCP-Server nicht mehr benötigt, da der gesamte n8n-Agent durch den Hermes-Agenten ersetzt wurde. 
{{< /alert >}}

## Einleitung
Wenn ihr meine Obsidian-Konfiguration verfolgt habt, wisst ihr, dass ich es liebe, meine Notizen mit Syncthing ([My Obsidian + Syncthing Setup: A Self-Hosted Cloud for Notes, Backups, and More](https://matsch1.github.io/web/en/coding/07_obsidian_syncthing_cloud_setup/)) geräteübergreifend zu synchronisieren. Aber ich wollte mehr als nur Synchronisierung – ich wollte **intelligent mit meinen Notizen interagieren, überall und jederzeit**.

## Warum Obsidian HTTP MCP?
Deshalb habe ich **Obsidian HTTP MCP** entwickelt, einen auf [FastMCP](https://gofastmcp.com/getting-started/welcome) basierenden, ressourcenschonenden Server, der deinen Obsidian-Vault über HTTP mithilfe des MCP-Protokolls bereitstellt.

Mit diesem Server kannst du:
- **KI-Clients** wie Cursor direkt mit deinem Vault verbinden und so die Suche in natürlicher Sprache, Analysen und sogar automatisierte Notizänderungen ermöglichen.
- **Ihre Notizen bei Bedarf abfragen** – über Skripte, Dashboards oder jedes Gerät, das HTTP unterstützt.
- **Den Server schlank und schnell halten** dank der FastMCP-Basis.

Im Grunde ist Ihr Vault nicht mehr nur ein Speicherort – er wird zu einer interaktiven Wissensmaschine.

## So funktioniert es
Jede Notiz in Ihrem Vault wird als MCP-„Paket“ behandelt. Der Server stellt Endpunkte zum Lesen, Aktualisieren oder Analysieren dieser Pakete bereit. Die Verwendung des HTTP-Protokolls sorgt für Einfachheit, Sicherheit und Zugriffsmöglichkeiten hinter Standard-Firewalls.

Der eigentliche Spaß beginnt mit der **KI-Integration**. Du kannst deinen Desktop-KI-Assistenten bitten, Notizen zusammenzufassen, relevante Informationen zu finden oder sogar Inhalte auf Basis deines Vaults zu generieren – und das alles durch ganz normales Chatten. Es ist, als würdest du deinen Notizen ein eigenes Gehirn geben.

## Was es zu einem „Nerdy-Perks“-Würdigen macht
- **KI-gestützte Workflows:** Chatten Sie mit Ihrem Archiv, analysieren Sie Inhalte oder bearbeiten Sie Notizen programmgesteuert.
- **Geräteübergreifender Zugriff:** Kommunizieren Sie mit Ihrem Archiv über Skripte, mobile Apps oder Web-Tools.
- **Minimaler Aufwand:** Zustandslos und effizient, perfekt für schlanke Setups.
- **Hackbar:** Erstelle Bots, Dashboards oder Automatisierungen rund um deine Notizen.
- **Sicher:** Läuft hinter deiner bestehenden Sicherheitsinfrastruktur, ohne dass Cloud-Dienste erforderlich sind.

### Beispiele für coole KI-Interaktionen
- **Suche und Zusammenfassungen in natürlicher Sprache:** Bitten Sie Ihre KI, Notizen in einfachem Englisch zu finden oder zusammenzufassen.
- **Automatisierte Aktualisierung und Erstellung von Notizen:** Lassen Sie die KI Notizen erstellen oder bearbeiten, Besprechungsprotokolle entwerfen oder Lernkarten generieren.
- **Vault-Analysen & Erkenntnisse:** Verfolgen Sie Trends, Lücken und wiederkehrende Themen in Ihren Notizen.
- **Persönlicher Wissensassistent:** Chatten Sie mit Ihrem Vault, um Fragen zu beantworten, Zusammenhänge vorzuschlagen oder Themen zu empfehlen.
- **Code- und Workflow-Automatisierung:** Nutzen Sie die KI, um Skripte zu generieren, Notizen zu organisieren oder automatisierte Workflows auszulösen.

## Einrichtung
- Starten Sie den MCP-Server auf Ihrem Remote-Server in einem Docker-Container mit einem einzigen Befehl.
- Fügen Sie die Client-Konfiguration zu Ihrem Desktop-KI-Client (z. B. Cursor) hinzu:
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
- Beginnen Sie, mit Ihren Notizen zu interagieren.

Eine ausführlichere Beschreibung finden Sie im GitHub-Repository: [obsidian-http-mcp](https://github.com/matsch1/obsidian-http-mcp) – und schon heute können Sie mit Ihren Notizen chatten!
	
## TL;DR
Obsidian HTTP MCP ist ein schlanker Server, der Ihren Obsidian-Vault über HTTP mithilfe des MCP-Protokolls verfügbar macht. Damit können Sie KI-Clients wie Cursor mit Ihren Notizen verbinden, um Suchanfragen in natürlicher Sprache, Zusammenfassungen, Analysen und automatisierte Änderungen durchzuführen. Führen Sie ihn auf einem Remote-Server aus, verbinden Sie Ihren KI-Client und verwandeln Sie Ihren Vault im Handumdrehen in eine interaktive, KI-gestützte Wissensmaschine. Schauen Sie sich das Ganze auf GitHub an [obsidian-http-mcp](https://github.com/matsch1/obsidian-http-mcp)!