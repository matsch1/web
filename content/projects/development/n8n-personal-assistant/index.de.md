---
ShowToc: true
TocOpen: true
base_hash: be42d23e906da803939775ed35666f37a1c87280e2dcc22c5f827e8decaed235
cover:
  alt: n8n-ai-assistant
  caption: Personal AI assistant build with n8n
  image: header.png
  relative: true
date: 2025-10-11
description: Erstelle deinen eigenen persönlichen Telegram-Assistenten mit n8n
draft: false
slug: n8n-ai-assistant
tags:
- n8n
- AI
title: Mein persönlicher n8n-KI-Assistent
homepage:
  section: engineering
  state: archive
  featured: false
project:
  status: discontinued
---

{{< alert type="info" title="" >}}
Der n8n-KI-Agent ist inzwischen obsolet und nicht mehr im Einsatz.
Ich habe ihn durch den Hermes Agent ersetzt, da dieser eine deutlich angenehmere Nutzung ermöglicht.
{{< /alert >}}

## Einleitung
{{< figure src="./ai-assistang.webp" width="400" alt="AI agent" class="right" >}}
Wer würde sich nicht einen persönlichen Assistenten wünschen – jemanden, der Termine, Aufgaben, E-Mails und andere administrative Aufgaben erledigt? Mit den heutigen KI-Fähigkeiten ist dies sogar für Personen möglich geworden, die sich keinen menschlichen Assistenten leisten können.
In diesem Beitrag zeige ich euch, wie ihr mit n8n einen persönlichen KI-Assistenten erstellen könnt, der auf Telegram-Nachrichten (einschließlich Sprachnotizen) reagiert und euch bei der Verwaltung von Terminen und Aufgaben unterstützt.

## n8n einrichten
Bevor wir den Assistenten erstellen, müssen wir n8n einrichten. n8n ist eine No-Code-Plattform zur Workflow-Automatisierung, die eine Vielzahl von Integrationen und Automatisierungen koordinieren kann (vielleicht werde ich in zukünftigen Beiträgen noch weitere Beispiele vorstellen).

{{< figure src="https://www.webmaster-vitaliy.de/wp-content/uploads/2025/05/n8n.png" width="300" alt="n8n" link="https://n8n.io/" target="_blank">}}

n8n muss auf einem eigenen Server gehostet werden. Ich empfehle, den Ansatz aus meinem [Coolify VPS setup](https://blog.matschcode.de/de/projects/self-hosting/coolify-vps-setup/) zu befolgen. Wenn bei dir bereits eine Coolify-Instanz läuft, kannst du mit wenigen Klicks einfach eine neue n8n-Ressource hinzufügen.

## Workflow erstellen
Der Workflow für meinen persönlichen Assistenten ist nicht vollständig selbst erstellt. Ich habe eine der vielen vorhandenen Vorlagen aus der n8n-Bibliothek als Grundlage verwendet:
[Voice & Text Assistant with Telegram, Gemini AI, Calendar, Gmail & Notion](https://n8n.io/workflows/8648-voice-and-text-assistant-with-telegram-gemini-ai-calendar-gmail-and-notion/).

In den folgenden Kapiteln werde ich die wichtigsten Komponenten dieses Workflows beschreiben und die von mir vorgenommenen Änderungen hervorheben.

### Auslöser
Der Workflow wird durch eine eingehende Telegram-Nachricht ausgelöst.
Um dies zu ermöglichen, musst du zunächst mithilfe von BotFather einen Telegram-Bot erstellen und die Chat-ID in deinem n8n-Telegram-Knoten konfigurieren.

Für die Einrichtung des Bots kannst du dieser Anleitung folgen. Das ursprüngliche Video ist leider nicht mehr verfügbar; dieses Video bietet eine ähnliche Alternative:
{{< youtube K7aFsGOMayc >}}

Sobald du den API-Token hast, erstelle in n8n die Telegram-Anmeldedaten, und die Verbindung zu deinem Bot wird hergestellt.

Wenn du den Zugriff einschränken möchtest, kannst du die vorhandene Kontoüberprüfung beibehalten, die prüft, ob die eingehende Nachricht von der richtigen Chat-ID stammt. Dies ist optional, kann aber eine zusätzliche Kontrollstufe bieten.

#### Kategorisierung von Text, Sprache oder Bild
Ich habe den ursprünglichen Switch-Block ersetzt und eine Logik eingeführt, um zwischen Text-, Audio- und Bildnachrichten zu unterscheiden.
Dadurch kann mein Assistent nicht nur Text, sondern auch Sprachnotizen und Bilder verarbeiten.

Die folgenden Screenshots zeigen, wie die Nachrichtentypen verarbeitet werden:
{{< galleries >}}
{{< gallery src="./settings_telegram_switch.png" title="Nachrichtentypen im n8n-Switch" alt="n8n-Switch im Rules-Modus mit Regeln für voice.file_id, photo[3].file_id und message.text; die Ausgänge heißen Audio, Image und Text" >}}
{{< gallery src="telegram_message_voice_image.png" title="n8n-Workflow für Text, Sprache und Bilder" alt="n8n-Workflow: Telegram Trigger, Account Check und Switch verzweigen Nachrichten in Audio-, Bild- und Textverarbeitung mit Transkription, Bildanalyse und Prompts" >}}
{{< /galleries >}}

Um den Inhalt der Nachricht zu extrahieren, verwende ich `Get File`-Knoten mit den folgenden Datei-IDs:

| Nachrichtentyp | Datei-ID |
|--------------|---------|
| Bild | {{ $json.message.voice.file_id }} |
| Sprache | {{ $json.message.voice.file_id }} |
| Text | — |

Nach dem Extrahieren des Inhalts übergebe ich ihn an Prompts, die dem unten stehenden ähneln:

```
The user provided the following text as an audio prompt
{{ $json.content.parts[0].text }}
Hint: It is possible that it has some transcription errors.
```


Mit dieser Konfiguration kann der KI-Agent den bereitgestellten Inhalt zuverlässig interpretieren, unabhängig davon, ob er ursprünglich als Text, Sprache oder Bild vorlag.

### KI-Agent
Das Herzstück des Assistenten ist der KI-Agent, der die eingehende Nachricht interpretiert und entscheidet, wie zu handeln ist.
Der ursprüngliche Workflow nutzt Google Gemini als Modell-Backend, aber Sie können dieses durch jedes von n8n unterstützte LLM ersetzen (OpenAI, Anthropic, lokale Modelle über Ollama usw.).
Ich empfehle ein OpenAI-Chat-Modell wie `gpt-5-mini`. Damit habe ich die besten Ergebnisse erzielt, und es kostet nur etwa 1 $ pro Monat (abhängig von Ihrer Nutzung).

Mein Assistent folgt einer einfachen Abfolge:

1. Eingabe empfangen (Text, Bild oder transkribiertes Audio)
2. Absicht des Nutzers interpretieren
3. Entscheiden, welches Tool aufgerufen werden soll (Aufgabe erstellen, Termin hinzufügen, Notiz schreiben usw.)
4. Das Tool über n8n-Knoten ausführen
5. Eine für Menschen verständliche Zusammenfassung zurück an Telegram senden

Dadurch ist das System vorhersehbar, modular und leicht zu erweitern.

#### Speicher
Der Speicher legt im Wesentlichen fest, wie viel Verlauf dein Assistent verarbeiten kann.
In meinem Fall verwende ich `Simple Memory` basierend auf `{{ $json.message.chat.id }}` mit einer Kontextfensterlänge von 20. Das bedeutet, dass sich der KI-Agent immer an deine letzten 20 Nachrichten erinnert.

#### MCP-Tools
Der Assistent nutzt **MCP-Tools** (Model Context Protocol-Tools), die von n8n bereitgestellt werden, um die eigentlichen Aktionen auszuführen.
Jedes Tool kapselt ein bestimmtes Verhalten, zum Beispiel:

- `calendar.addEvent`
- `notion.createPage`
- `todo.createTask`
- `email.send`
- `notes.append`

Diese Tools stellen strukturierte Schnittstellen bereit, die die KI aufrufen kann.
Das bedeutet, dass der Agent keinen beliebigen Text erstellt, sondern präzise Befehle im JSON-Format zurückgibt, die n8n ausführt.

Um zusätzliche Funktionen zu integrieren (zum Beispiel Einkaufslisten, Fitnessprotokolle, Gewohnheitsaufzeichnung), musst du lediglich neue Tools hinzufügen und diese in der Agenten-Eingabeaufforderung beschreiben.
In meinem Fall verwende ich beispielsweise Obsidian anstelle von Notion für Notizen und richte dafür einen zusätzlichen MCP-Server ein ([HTTP Obsidian MCP server](https://blog.matschcode.de/de/projects/development/obsidian-http-mcp/)), der von meinem KI-Agenten genutzt wird.

Außerdem empfehle ich, die folgenden von n8n bereitgestellten MCP-Tools hinzuzufügen:
- SerpAPI, damit der KI-Agent im Internet suchen kann
- „Date & Time“, damit der KI-Agent nicht auf die Systemzeit angewiesen ist
- „Calculator“, da KIs schlecht mit Zahlen umgehen können

{{< figure src="./mcp_tools.png" width="800" alt="MCP tools" >}}

#### Promptgestaltung
Eine klare Promptgestaltung verbessert die Zuverlässigkeit des Agenten erheblich.
Ich verwende einen strukturierten Prompt, der der KI klare Anweisungen zu folgenden Punkten gibt:

- ihre Rolle (persönlicher Produktivitätsassistent)
- zulässige Aktionen (Termin erstellen, Aufgabe hinzufügen, Notiz speichern usw.)
- erforderliches Ausgabeformat (JSON-Befehlsobjekte)

Dies erfolgt im Feld `System Message` des KI-Agenten.
Je mehr Aufwand Sie in die Eingabeanweisungen stecken, desto besser verhält sich der Agent gemäß Ihren Erwartungen.

### Feedback
Nachdem der Agent eine Aktion abgeschlossen hat, generiert der Workflow eine kurze Bestätigungsmeldung und sendet diese zurück an Telegram.
Dadurch wird sichergestellt, dass der Nutzer stets weiß, was der Assistent getan hat.

Beispiele:

- „Dein Termin wurde für Dienstag um 14:00 Uhr hinzugefügt.“
- „Ich habe eine neue Aufgabe für morgen angelegt.“

Diese Rückkopplungsschleife verbessert die Benutzerfreundlichkeit und vermeidet Verwirrung, insbesondere bei sprachgesteuerten Interaktionen, bei denen der Nutzer die Eingabe nicht sehen kann.

## Anwendungsbeispiele
Im Folgenden finden Sie einige praktische Beispiele, die veranschaulichen, was der Assistent leisten kann.

### Termin in den Kalender eintragen
Sie können Nachrichten oder sogar Sprachnotizen senden wie:

- „Plane morgen um 10 Uhr ein Treffen mit John ein.“
- „Erstelle einen Termin beim Zahnarzt am 5. April um 8:30 Uhr.“

Der Assistent analysiert das Datum, erstellt mithilfe des Kalender-Tools einen Termin und sendet eine Bestätigungsnachricht zurück.

### Aufgabe für zukünftige To-Dos erstellen
In meiner Konfiguration verwalte ich Aufgaben mit Obsidian. Mein Obsidian-MCP-Server stellt Tools bereit, mit denen der KI-Agent Aufgaben direkt in meinem Vault erstellen, aktualisieren oder abfragen kann.
Das bedeutet, ich kann meinem Assistenten einfach sagen:

- „Erinnere mich daran, morgen früh um 7 Uhr den Müll rauszubringen.“
- „Habe ich in meinen Notizen irgendwelche Aufgaben, die mit meinem n8n-Projekt zu tun haben?“

Der Agent interpretiert die Anfrage, wählt das entsprechende MCP-Tool aus, und die Aufgabe wird automatisch hinzugefügt oder abgerufen.

### Kochrezepte zu Notizen hinzufügen
Ein Anwendungsfall, der mir besonders gut gefällt, ist das Erstellen und Speichern persönlicher Kochrezepte, einschließlich einer strukturierten Zutatenliste.
Ich kann meinen Assistenten beispielsweise fragen:

- „Ich möchte eine fettarme Version von Chicken Masala kochen. Bitte gib mir ein Rezept für vier Personen.“
- „Dieses Rezept sieht perfekt aus. Passe es für sechs Personen an und speichere es in meinem Obsidian-Vault.“

In der Systemaufforderung habe ich genau definiert, wie meine Rezepte formatiert sein sollen und dass der Agent vorhandene Rezepte als Vorlagen verwenden darf.
Das Ergebnis ist ein übersichtlich strukturiertes Rezept, das direkt in meinen Notizen gespeichert wird – komplett mit Zutatenliste – ideal für die Mahlzeitenplanung und den Einkauf.
