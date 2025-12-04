---
ShowToc: true
TocOpen: true
base_hash: 373d284b4fc5f2c6b8599bfec2b5d89ac325ba58d5f5b22d0ce9faa02880a5d0
cover:
  alt: n8n-ai-assistant
  caption: Personal AI assistant build with n8n
  image: header.png
  relative: true
date: 2025-10-11
description: Build your own personal telegram assistant using n8n
draft: false
slug: n8n-ai-assistant
tags:
- n8n
- AI
title: Mein persönlicher n8n AI-Assistent
---

{{< alert type="info" title="Ongoing" >}}
Der Assistent macht einen guten Job und ist immer noch im täglichen Einsatz.
{{< /alert >}}

## Einleitung
{{< figure src="./ai-assistang.png" width="400" alt="AI agent" class="right" >}}
Wer wünscht sich nicht einen persönlichen Assistenten - jemanden, der Termine, Aufgaben, E-Mails und andere Verwaltungsarbeiten erledigt? Mit den heutigen KI-Fähigkeiten ist dies sogar für Personen möglich geworden, die sich keinen menschlichen Assistenten leisten können.
In diesem Beitrag zeige ich, wie man mit n8n einen persönlichen KI-Assistenten erstellen kann, der auf Telegram-Nachrichten (einschließlich Sprachnotizen) antwortet und Ihnen bei der Verwaltung von Terminen und Aufgaben hilft.

## n8n einrichten
{{< figure src="https://www.webmaster-vitaliy.de/wp-content/uploads/2025/05/n8n.png" width="400" alt="n8n" class="right" link="https://n8n.io/" target="_blank">}}
Bevor wir den Assistenten erstellen, müssen wir n8n einrichten. n8n ist eine No-Code-Workflow-Automatisierungsplattform, die eine breite Palette von Integrationen und Automatisierungen orchestrieren kann (ich werde in zukünftigen Beiträgen einige zusätzliche Beispiele behandeln).
n8n muss selbst auf einem Server gehostet werden. Ich empfehle, den Ansatz aus meinem [Coolify VPS setup](https://blog.matschcode.de/en/projects/coolify-vps-setup/) zu verfolgen. Wenn Sie bereits eine Coolify-Instanz betreiben, können Sie einfach mit ein paar Klicks eine neue n8n-Ressource hinzufügen.

## Workflow erstellen
Mein persönlicher Assistent-Workflow ist nicht komplett selbst erstellt. Ich habe eine der vielen vorhandenen Vorlagen aus der n8n-Bibliothek als Grundlage verwendet:
[Voice & Text Assistant with Telegram, Gemini AI, Calendar, Gmail & Notion](https://n8n.io/workflows/8648-voice-and-text-assistant-with-telegram-gemini-ai-calendar-gmail-and-notion/).

In den folgenden Kapiteln werde ich die wichtigsten Komponenten dieses Workflows beschreiben und die von mir vorgenommenen Änderungen hervorheben.

### Auslöser
Der Workflow wird durch eine eingehende Telegram-Nachricht ausgelöst.  
Um dies zu aktivieren, müssen Sie zunächst einen Telegram-Bot mit BotFather erstellen und die Chat-ID in Ihrem n8n Telegram-Knoten konfigurieren.

Für die Einrichtung des Bots können Sie diesem Tutorial folgen:  
{{< youtube RIrIXLAj8bE >}}

Sobald Sie das API-Token haben, erstellen Sie Telegram-Anmeldedaten in n8n, und die Verbindung zu Ihrem Bot wird hergestellt.

Wenn Sie den Zugriff einschränken möchten, können Sie die vorhandene Kontoprüfung beibehalten, mit der überprüft wird, ob die eingehende Nachricht von der richtigen Chat-ID stammt. Dies ist optional, kann aber eine zusätzliche Kontrollebene darstellen.

#### Kategorisierung von Text, Sprache oder Bild
Ich habe den ursprünglichen Schalterblock ersetzt und eine Logik zur Unterscheidung zwischen Text-, Audio- und Bildnachrichten eingeführt.  
Dadurch kann mein Assistent nicht nur Text, sondern auch Sprachnotizen und Bilder verarbeiten.

Die folgenden Bildschirmfotos zeigen, wie die verschiedenen Nachrichtentypen behandelt werden:
{{< galleries >}}
{{< gallery src="./settings_telegram_switch.png" title="telegram_switch_settings" >}}
{{< gallery src="telegram_message_voice_image.png" title="telegram_message_voice_image" >}}
{{< /galleries >}}

Um den Inhalt der Nachricht zu extrahieren, verwende ich `Get File`-Knoten mit den folgenden Datei-IDs:

| Nachrichtentyp | Datei-ID |
|--------------|---------|
| Bild | {{ $json.message.voice.file_id }} |
| Stimme | {{ $json.message.voice.file_id }} |
| Text | - |

Nachdem ich den Inhalt extrahiert habe, übergebe ich ihn in Eingabeaufforderungen ähnlich der folgenden:

```
The user provided the following text as an audio prompt
{{ $json.content.parts[0].text }}
Hint: It is possible that it has some transcription errors.
```


Auf diese Weise kann der KI-Agent den bereitgestellten Inhalt zuverlässig interpretieren, unabhängig davon, ob es sich um Text, Sprache oder ein Bild handelt.

### KI-Agent
Das Herzstück des Assistenten ist der KI-Agent, der die eingehende Nachricht interpretiert und entscheidet, wie zu handeln ist.  
Der ursprüngliche Workflow verwendet Google Gemini als Modell-Backend, aber Sie können dies durch jedes von n8n unterstützte LLM ersetzen (OpenAI, Anthropic, lokale Modelle über Ollama usw.).
Ich empfehle, ein OpenAI-Chatmodell wie `gpt-5-mini` zu verwenden. Damit habe ich die besten Ergebnisse erzielt und es kostet nur etwa 1$ pro Monat (je nach Nutzung).

Mein Assistent folgt einer einfachen Kette:

1. Eingabe empfangen (Text, Bild oder transkribiertes Audio)
2. Interpretation der Benutzerabsicht
3. Entscheiden, welches Tool aufgerufen werden soll (eine Aufgabe erstellen, einen Termin hinzufügen, eine Notiz schreiben usw.)
4. Ausführen des Tools über n8n-Knoten
5. Senden Sie eine menschenfreundliche Zusammenfassung zurück an Telegram

Dies macht das System vorhersehbar, modular und einfach zu erweitern.

#### Speicher
Der Speicher legt im Grunde fest, wie viel Geschichte Ihr Assistent verarbeiten kann.
In meinem Fall habe ich mich für `Simple Memory` entschieden, das auf `{{ $json.message.chat.id }}` basiert und eine Kontextfensterlänge von 20 hat. Das bedeutet, dass sich der KI-Agent immer an Ihre letzten 20 Nachrichten erinnert.

#### MCP-Werkzeuge
Der Assistent verlässt sich auf die **MCP tools** (Model Context Protocol tools), die von n8n zur Verfügung gestellt werden, um die eigentlichen Aktionen durchzuführen.  
Jedes Tool kapselt ein bestimmtes Verhalten, zum Beispiel:

- `calendar.addEvent`
- `notion.createPage`
- `todo.createTask`
- `email.send`
- `notes.append`

Diese Werkzeuge stellen strukturierte Schnittstellen zur Verfügung, die die KI aufrufen kann.  
Das bedeutet, dass der Agent keinen willkürlichen Text erstellt, sondern stattdessen präzise Befehle im JSON-Format zurückgibt, die n8n dann ausführt.

Um zusätzliche Funktionen zu integrieren (z. B. Einkaufslisten, Fitnessprotokolle, Gewohnheitsverfolgung), müssen Sie nur neue Tools hinzufügen und sie in der Eingabeaufforderung des Agenten beschreiben.
In meinem Fall verwende ich beispielsweise Obsidian anstelle von Notion für Notizen und habe dafür einen extra MCP-Server ([HTTP Obsidian MCP server](https://blog.matschcode.de/en/projects/obsidian-http-mcp/)) eingerichtet, der von meinem KI-Agenten verwendet wird.

Ich empfehle außerdem, die folgenden von n8n bereitgestellten MCP-Tools hinzuzufügen:
- SerpAPI, damit der KI-Agent in der Lage ist, das Web zu durchsuchen
- Datum und Uhrzeit, damit der KI-Agent nicht auf die Systemzeit angewiesen ist
- Taschenrechner, da KIs schlecht mit Zahlen umgehen können

{{< figure src="./mcp_tools.png" width="800" alt="MCP tools" >}}

#### Eingabeaufforderung
Klare Aufforderungen verbessern die Zuverlässigkeit des Agenten erheblich.  
Ich verwende einen strukturierten Prompt, der der KI klare Anweisungen gibt:

- ihre Rolle (persönlicher Produktivitätsassistent)
- erlaubte Aktionen (Termin erstellen, Aufgabe hinzufügen, Notiz speichern usw.)
- erforderliches Ausgabeformat (JSON-Befehlsobjekte)

Dies geschieht im Feld `System Message` des KI-Agenten.
Je mehr Aufwand Sie für die Eingabeaufforderung betreiben, desto mehr verhält er sich so, wie Sie es erwarten.

### Rückmeldung
Nachdem der Agent eine Aktion ausgeführt hat, generiert der Workflow eine kurze Bestätigungsnachricht und sendet sie zurück an Telegram.  
So ist sichergestellt, dass der Benutzer immer weiß, was der Assistent getan hat.

Beispiele:

- "Ihr Termin wurde für Dienstag um 14:00 Uhr hinzugefügt."
- "Ich habe eine neue Aufgabe für morgen erstellt."

Diese Feedbackschleife verbessert die Benutzerfreundlichkeit und vermeidet Verwirrung, insbesondere bei sprachgesteuerten Interaktionen, bei denen der Benutzer die Eingabe nicht sehen kann.

## Beispiele für die Verwendung
Im Folgenden finden Sie einige praktische Beispiele, die zeigen, was der Assistent alles kann.

### Termin zum Kalender hinzufügen
Sie können Nachrichten oder sogar Sprachnotizen senden wie:

- "Vereinbaren Sie morgen um 10 Uhr einen Termin mit John."
- "Vereinbaren Sie einen Termin beim Zahnarzt am 5. April um 8:30 Uhr".

Der Assistent analysiert das Datum, erstellt mit dem Kalendertool ein Ereignis und sendet eine Bestätigungsnachricht.

### Aufgabe für zukünftige To-Dos erstellen
In meinem Setup verfolge ich Aufgaben mit Obsidian. Mein Obsidian MCP-Server stellt Tools zur Verfügung, mit denen der KI-Agent Aufgaben direkt in meinem Tresor erstellen, aktualisieren oder abfragen kann.  
Das bedeutet, dass ich meinem Assistenten einfach sagen kann:

- "Erinnere mich daran, dass ich morgen früh um 7 Uhr den Müll rausbringe."
- Habe ich irgendwelche Aufgaben in meinen Notizen, die mit meinem n8n-Projekt zu tun haben?"

Der Agent interpretiert die Anfrage, wählt das entsprechende MCP-Tool aus, und die Aufgabe wird automatisch hinzugefügt oder abgerufen.

### Hinzufügen von Kochrezepten zu Notizen
Ein Anwendungsfall, der mir besonders gefällt, ist die Erstellung und Speicherung persönlicher Kochrezepte, einschließlich einer strukturierten Zutatenliste.  
Ich kann meinen Assistenten z. B. fragen:

- "Ich möchte eine fettarme Version von Chicken Masala kochen. Bitte geben Sie mir ein Rezept für vier Personen."
- "Dieses Rezept sieht perfekt aus. Skalieren Sie es auf sechs Personen und speichern Sie es in meinem Obsidian-Tresor."

In der Systemabfrage habe ich genau festgelegt, wie meine Rezepte formatiert werden sollen und dass der Agent vorhandene Rezepte als Vorlagen verwenden kann.  
Das Ergebnis ist ein sauber strukturiertes Rezept, das direkt in meinen Notizen gespeichert ist, komplett mit Zutatenliste - ideal für die Planung von Mahlzeiten und den Einkauf von Lebensmitteln.