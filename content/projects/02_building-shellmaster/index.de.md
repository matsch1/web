---
ShowToc: true
TocOpen: true
base_hash: 6a73eb43bd818d03f39d2a3a4544b8856f7e4b60ef931f765b60d675808aa244
cover:
  alt: shellmaster
  caption: ''
  image: img1.webp
  relative: true
date: 2025-04-06
description: Mein Weg zur Entwicklung einer Quiz-App mit Flutter, Pocketbase und Unleash
draft: false
slug: building-shellmaster
tags:
- flutter
- application
- linux
title: ' Shellmaster erstellen: Eine unterhaltsame Art, Linux-Shell-Befehle zu lernen '
---

{{< alert type="error" title="Deprecated" >}}
Die App wurde erneut aus dem Play Store entfernt, da ich das Projekt nicht mehr weiterführen kann.
{{< /alert >}}

Das Erlernen von Linux-Shell-Befehlen kann einschüchternd sein, aber was wäre, wenn es Spaß machen könnte? Das ist die Idee hinter **Shellmaster**, einer Quiz-App, die Nutzern hilft, Shell- und Bash-Befehle durch spannende Quizfragen zu meistern. 
Schaut sie euch im Google Play Store an: [Shellmaster - Apps on Google Play](https://play.google.com/store/apps/details?id=com.matschcode.shellmaster)
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

- **Verschiedene Quiz-Modi**: Teste dein Wissen in verschiedenen Spielmodi, darunter zeitlich begrenzte Quizze und Übungsrunden.
- **Schwierigkeitsstufen und Kategorien**: Die Fragen sind in die Stufen „leicht“, „mittel“ und „schwer“ unterteilt und decken wichtige Shell-Befehle, Skripting und Systemadministration ab.
- **Fortschrittsverfolgung**: Behalte deine Leistung im Blick und verbessere dich im Laufe der Zeit.
- **Individuelle Herausforderungen**: Nutzer können sich eigene Herausforderungen stellen und sich mit Freunden messen.
- **Offline-Unterstützung**: Spiele Quizze, ohne dass eine Internetverbindung erforderlich ist.
- **Dunkelmodus**: Genieße einen eleganten Dunkelmodus für bessere Lesbarkeit.

---

## App-Entwicklung

In den nächsten Kapiteln geht es um meine Erfahrungen während des Entwicklungsprozesses.
Wenn du an interessanten Flutter-Inhalten interessiert bist, lies weiter. Wenn du nur wegen Linux und Bash hier bist, schau dir die App im Google Play Store [Shellmaster - Apps on Google Play](https://play.google.com/store/apps/details?id=com.matschcode.shellmaster) an.
### Die Wahl von Flutter für eine plattformübergreifende Quiz-App

Ich habe mich für **Flutter** entschieden, weil es einen **schnellen Entwicklungszyklus, ansprechende UI-Funktionen und plattformübergreifende Unterstützung** bietet. Mit einer einzigen Codebasis konnte ich sowohl Android als auch (möglicherweise) iOS in Zukunft ansprechen. Zu den wichtigsten Flutter-Funktionen, die ich genutzt habe, gehören:

- **Benutzerdefinierte UI-Komponenten**: Ich habe eine benutzerdefinierte AppBar (`CSAppBar`) erstellt, um ein einheitliches Erscheinungsbild zu gewährleisten.
- **Zustandsverwaltung**: Ich habe `provider` verwendet, um den Quizstatus und die Benutzereinstellungen effizient zu verwalten.
- **Flüssige Animationen**: Animierte Hintergrundfarbenwechsel bei den Quizfragen verbessern das Benutzererlebnis.

---

### PocketBase als leichtgewichtiges Backend

Für die Verwaltung von Quizdaten, Benutzerfortschritten und der Authentifizierung habe ich mich für **PocketBase** entschieden, ein in Go geschriebenes Open-Source-Backend. Es bietet eine **SQLite-Datenbank, Echtzeit-Abonnements und eine API mit minimalem Einrichtungsaufwand**. Hier sind die Gründe, warum es sich gut für Shellmaster bewährt hat:

- **Selbstgehostete Kontrolle**: Durch den Betrieb von PocketBase auf meinem VPS habe ich die volle Kontrolle über meine Daten.
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
- **Schrittweise Einführungen** zum Testen bei einer Teilgruppe von Nutzern

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
4. **Prüfungsverfahren**: Das Prüfungsverfahren von Google erforderte die ordnungsgemäße Einhaltung der Datenschutzrichtlinien, insbesondere hinsichtlich der Benutzerauthentifizierung.


---

## Fazit

Die Entwicklung von Shellmaster war eine spannende Reise, bei der **die UI-Fähigkeiten von Flutter, das leichtgewichtige Backend von PocketBase, die Feature-Flags von Unleash und die Bereitstellung über die Google Play Console** kombiniert wurden. Das Ergebnis ist eine unterhaltsame und lehrreiche Quiz-App, die Nutzern hilft, ihre Linux-Shell-Kenntnisse interaktiv zu verbessern.

Wenn ihr interessiert seid, schaut euch **Shellmaster** auf der [Shellmaster - Apps on Google Play](https://play.google.com/store/apps/details?id=com.matschcode.shellmaster) an und teilt mir eure Meinung mit!

Welche interessanten Tech-Stacks habt ihr in euren Apps verwendet? Lasst uns in den Kommentaren darüber diskutieren!