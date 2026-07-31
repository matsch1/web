---
ShowToc: true
TocOpen: true
base_hash: 8cb7d60e55facfcd6f1b558ba454eb11240f86d02abb686f52cab5d9aeddbfdf
cover:
  alt: shellmaster
  caption: ''
  image: img1.webp
  relative: true
date: 2025-04-06
description: Mein Weg zur Entwicklung einer Quiz-App mit Flutter, Pocketbase und Unleash
draft: false
homepage:
  featured: false
  section: engineering
  state: archive
project:
  status: discontinued
slug: building-shellmaster
tags:
- flutter
- application
- linux
title: ' Shellmaster erstellen: Eine unterhaltsame Art, Linux-Shell-Befehle zu lernen '
---

{{< alert type="warning" title="" >}}
Leider ist die App nicht mehr verfügbar. 
Die Pflege war zu zeitaufwendig, und ich möchte keinen weiteren Aufwand mehr in dieses Projekt stecken.
{{< /alert >}}

Das Erlernen von Linux-Shell-Befehlen kann einschüchternd sein, aber was wäre, wenn es Spaß machen könnte? Das ist die Idee hinter **Shellmaster**, einer Quiz-App, die Nutzern hilft, Shell- und Bash-Befehle durch spannende Quizfragen zu meistern. 
Schaut euch die App im Google Play Store an: „Shellmaster“
Bei der Entwicklung von Shellmaster stieß ich auf einige interessante technische Herausforderungen und lernte viel über **Flutter**, **PocketBase**, **Unleash-Feature-Flags** und die **Bereitstellung über die Google Play Console**. In diesem Artikel teile ich einige wichtige Erkenntnisse aus dem Entwicklungsprozess.
## Inhaltsverzeichnis

1. [App Features](#app-features)
2. [App Development](#app-development)
  1. [Choosing Flutter for a Cross-Platform Quiz App](#choosing-flutter-for-a-cross-platform-quiz-app)
	2. [PocketBase as a Lightweight Backend](#pocketbase-as-a-lightweight-backend)
  3. [Using Unleash for Feature Flags](#using-unleash-for-feature-flags)
  4. [Deploying via Google Play Console](#deploying-via-google-play-console)
3. [Conclusion](#conclusion)


---

## App-Funktionen

Shellmaster wurde entwickelt, um das Erlernen von Linux-Befehlen unterhaltsam und interaktiv zu gestalten. Hier sind einige der wichtigsten Funktionen:

- **Verschiedene Quizmodi**: Teste dein Wissen in verschiedenen Spielmodi, darunter zeitlich begrenzte Quizze und Übungsrunden.
- **Schwierigkeitsstufen & Kategorien**: Die Fragen sind in die Stufen „leicht“, „mittel“ und „schwer“ unterteilt und decken wichtige Shell-Befehle, Skripting und Systemadministration ab.
- **Fortschrittsverfolgung**: Behalte deine Leistung im Blick und verbessere dich im Laufe der Zeit.
- **Individuelle Herausforderungen**: Nutzer können sich eigene Herausforderungen stellen und sich mit Freunden messen.
- **Offline-Unterstützung**: Spiele Quizze, ohne dass eine Internetverbindung erforderlich ist.
- **Dunkelmodus**: Genieße einen eleganten Dunkelmodus für bessere Lesbarkeit.

---

## App-Entwicklung

In den nächsten Kapiteln geht es um meine Erfahrungen während des Entwicklungsprozesses.
Wenn du an interessanten Flutter-Inhalten interessiert bist, lies weiter. Wenn du nur wegen Linux und Bash hier bist, schau dir die App im Google Play Store an: „Shellmaster – Apps auf Google Play“.
### Die Wahl von Flutter für eine plattformübergreifende Quiz-App

Ich habe mich für **Flutter** entschieden, weil es einen **schnellen Entwicklungszyklus, ansprechende UI-Funktionen und plattformübergreifende Unterstützung** bietet. Mit einer einzigen Codebasis konnte ich sowohl Android als auch (möglicherweise) iOS in Zukunft ansprechen. Zu den wichtigsten Flutter-Funktionen, die ich genutzt habe, gehören:

- **Benutzerdefinierte UI-Komponenten**: Ich habe eine benutzerdefinierte AppBar (`CSAppBar`) erstellt, um ein einheitliches Erscheinungsbild zu gewährleisten.
- **Zustandsverwaltung**: Ich habe `provider` verwendet, um den Quiz-Zustand und die Benutzereinstellungen effizient zu verwalten.
- **Flüssige Animationen**: Animierte Hintergrundfarbenwechsel bei den Quizfragen verbessern das Nutzererlebnis.

---

### PocketBase als schlankes Backend

Zur Verwaltung von Quizdaten, Benutzerfortschritten und der Authentifizierung habe ich mich für **PocketBase** entschieden, ein in Go geschriebenes Open-Source-Backend. Es bietet eine **SQLite-Datenbank, Echtzeit-Abonnements und eine API mit minimalem Einrichtungsaufwand**. Hier sind die Gründe, warum es sich gut für Shellmaster geeignet hat:

- **Selbstgehostete Kontrolle**: Durch den Betrieb von PocketBase auf meinem VPS habe ich die volle Kontrolle über die Daten.
- **Einfache Integration**: PocketBase stellt eine REST-API bereit, die das `http`-Paket von Flutter problemlos nutzen kann.
- **Benutzerauthentifizierung**: Dank der integrierten Authentifizierung konnte ich den Fortschritt der Benutzer geräteübergreifend verwalten. Ich werde in Zukunft die Möglichkeit zur Benutzeranmeldung hinzufügen.

### Beispiel: Abrufen von Quizdaten aus PocketBase

```dart
Future<List<Question>> fetchQuestions() async {
  final response = await http.get(Uri.parse('https://your-pocketbase-url/api/collections/questions/records'));
  final data = jsonDecode(response.body);
  return data['items'].map<Question>((json) => Question.fromJson(json)).toList();
}
```

---

### Einsatz von Unleash für Feature-Flags

Um **schrittweise Feature-Einführungen und A/B-Tests** zu ermöglichen, habe ich **Unleash** integriert, ein Open-Source-Feature-Flag-System. Dadurch konnte ich **Features dynamisch aktivieren und deaktivieren**, ohne ein neues App-Update veröffentlichen zu müssen.

#### Warum Feature-Flags verwenden?

- **Mit neuen Funktionen experimentieren** (z. B. ein „Hardcore-Modus“ für erfahrene Nutzer)
- **Funktionen aus der Ferne aktivieren/deaktivieren**, ohne dass ein App-Update erforderlich ist
- **Schrittweise Einführung** zum Testen bei einer Teilgruppe von Nutzern

#### Implementierung von Feature-Flags in Flutter

```dart
final unleash = UnleashClient(appName: 'shellmaster', instanceId: 'your-instance-id', url: 'https://your-unleash-server');
await unleash.start();
bool isHardcoreModeEnabled = unleash.isEnabled('hardcore-mode');
```

---

### Veröffentlichung über die Google Play Console

Die Veröffentlichung von Shellmaster im **Google Play Store** umfasste mehrere wichtige Schritte:

1. **App-Signierung und -Bündelung**: Dank Flutters `flutter build appbundle` war die Erstellung eines **AAB**-Pakets ganz einfach.
2. **Einrichtung der Play Console**: Die Einrichtung von **Store-Einträgen, Screenshots und Beschreibungen** nahm mehr Zeit in Anspruch als erwartet.
3. **Tests und Release-Tracks**: Durch **interne, geschlossene und offene Tests** konnten Fehler vor der vollständigen Bereitstellung erkannt werden.
4. **Prüfungsverfahren**: Googles Überprüfungsprozess erforderte die ordnungsgemäße Einhaltung der Datenrichtlinien, insbesondere bei der Benutzerauthentifizierung.


---

## Fazit

Die Entwicklung von Shellmaster war eine spannende Reise, bei der **die UI-Fähigkeiten von Flutter, das leichtgewichtige Backend von PocketBase, die Feature-Flags von Unleash und die Bereitstellung über die Google Play Console** kombiniert wurden. Das Ergebnis ist eine unterhaltsame und lehrreiche Quiz-App, die Nutzern hilft, ihre Linux-Shell-Kenntnisse interaktiv zu verbessern.

Welche interessanten Tech-Stacks habt ihr in euren Apps verwendet? Lasst uns das in den Kommentaren diskutieren!