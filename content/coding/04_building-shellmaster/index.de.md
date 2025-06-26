---
ShowToc: true
TocOpen: true
base_hash: 555c0c80d560c1c8fd7703c2c49a03387d6ca9dd03b99e41131e242bdd4a0f64
date: 2025-04-06
description: My path of building a quiz app using flutter, pocketbase and unleash
draft: false
img: img1.webp
title: 'Bauen von Shellmaster: Eine unterhaltsame Möglichkeit, Linux -Shell -Befehle
  zu lernen'
---

![header-image](img1.webp)
Das Erlernen von Linux -Shell -Befehlen kann entmutigend sein, aber was ist, wenn es Spaß machen könnte?Das ist die Idee hinter **Shellmaster**, einer Quiz -Spiel -App, mit der Benutzer die Befehle von Shell und Bash durch ansprechende Quizs beherrschen können.
Schauen Sie sich es im Google Play Store an: [Shellmaster - Apps on Google Play](https://play.google.com/store/apps/details?id=com.matschcode.shellmaster)
Während ich Shellmaster baute, stieß ich auf einige interessante technische Herausforderungen und lernte viel über [[00000110000018], **PocketBase**, **Unleash feature flags** und **Google Play Console deployment**.In diesem Artikel werde ich einige wichtige Imbissbuden aus der Entwicklungsreise teilen.
## Inhaltsverzeichnis

1. [App Features](#app-features)
2. [App Development](#app-development)
1. [Choosing Flutter for a Cross-Platform Quiz App](#choosing-flutter-for-a-cross-platform-quiz-app)
2. [PocketBase as a Lightweight Backend](#pocketbase-as-a-lightweight-backend)
3. [Using Unleash for Feature Flags](#using-unleash-for-feature-flags)
4. [Deploying via Google Play Console](#deploying-via-google-play-console)
3. [Conclusion](#conclusion)


---

## App -Funktionen

Shellmaster ist so konzipiert, dass Lernlinux -Befehle Spaß und interaktiv machen.Hier sind einige seiner Schlüsselmerkmale:

- **Multiple Quiz Modes**: Testen Sie Ihr Wissen mit unterschiedlichen Spielmodi, einschließlich zeitgesteuerter Quiz und Übungssitzungen.
.
- **Progress Tracking**: Verfolgen Sie Ihre Leistung und verbessern Sie sich im Laufe der Zeit.
- **Custom Challenges**: Benutzer können ihre eigenen Herausforderungen stellen und mit Freunden konkurrieren.
- **Offline Support**: Spielen Sie Quiz, ohne eine Internetverbindung zu erfordern.
- **Dark Mode**: Genießen Sie einen schlanken dunklen Modus, um eine bessere Lesbarkeit zu erhalten.

---

## App -Entwicklung

In den nächsten Kapiteln geht es um mein Lernen während des Entwicklungsprozesses.
Wenn Sie sich für ein schönes Flattern interessieren, lesen Sie weiter.Wenn Sie nur hier für Linux und Bash sind, überprüfen Sie die App im Google Play Store [Shellmaster - Apps on Google Play](https://play.google.com/store/apps/details?id=com.matschcode.shellmaster).
### Auswahl von Flutter für eine plattformübergreifende Quiz-App

Ich habe **Flutter** wegen seiner **fast development cycle, beautiful UI capabilities, and cross-platform support** gewählt.Mit einer einzelnen Codebasis könnte ich in Zukunft sowohl Android als auch (potenziell) iOS ansprechen.Einige der wichtigsten Flutterfunktionen, die ich nutzte, sind:

- **Custom UI components**: Ich habe eine benutzerdefinierte Appbar (`CSAppBar`) für einen konsistenten Look erstellt.
- **State management**: Ich habe `provider` verwendet, um den Quizzustand und die Benutzereinstellungen effizient zu bewältigen.
- **Smooth animations**: Animierte Hintergrundfarbe -Änderungen in den Quizfragen verbessern die Benutzererfahrung.

---

### PocketBase als leichtes Backend

Für die Verwaltung von Quizdaten, Benutzerfortschritt und Authentifizierung habe ich mich für **PocketBase** entschieden, ein Open-Source-Backend in Go.Es bietet eine **SQLite database, real-time subscriptions, and an API with minimal setup**.Hier ist, warum es für Shellmaster gut funktioniert hat:

.
.
.Ich werde in Zukunft die Möglichkeit für die Benutzeranmeldung hinzufügen.

### Beispiel: Quizdaten aus PocketBase abrufen

```dart
Future<List<Question>> fetchQuestions() async {
  final response = await http.get(Uri.parse('https://your-pocketbase-url/api/collections/questions/records'));
  final data = jsonDecode(response.body);
  return data['items'].map<Question>((json) => Question.fromJson(json)).toList();
}
```

---

### Verwenden Sie die Entfessel für Feature -Flags

Um **progressive feature rollouts and A/B testing** zu aktivieren, integrierte ich **Unleash** ein Open-Source-Feature-Flag-System.Dies ermöglichte mir, **toggle features dynamically** zu [00000110000040]], ohne ein neues App -Update zu veröffentlichen.

#### Warum Feature Flags verwenden?

- **Experiment with new features** (z. B. ein „Hardcore -Modus“ für erfahrene Benutzer)
- **Enable/disable features remotely** ohne eine App -Update erforderlich
- **Gradual rollouts** zum Testen auf einer Teilmenge von Benutzern

#### Implementierung von Feature -Flags in Flutter

```dart
final unleash = UnleashClient(appName: 'shellmaster', instanceId: 'your-instance-id', url: 'https://your-unleash-server');
await unleash.start();
bool isHardcoreModeEnabled = unleash.isEnabled('hardcore-mode');
```

---

### Bereitstellung über Google Play Console

Das Veröffentlichen von Shellmaster am **Google Play Store** umfasste mehrere wichtige Schritte:

1. **App Signing & Bundling**: Flutters `flutter build appbundle` erzeugte ein **AAB** Paket Easy.
2. **Play Console Setup**: Einrichten **store listings, screenshots, and descriptions** hat mehr Zeit als erwartet in Anspruch genommen.
3.. **Testing & Release Tracks**: Verwenden **internal, closed, and open testing** Hilft bei der vollständigen Bereitstellung Fehlern.
4. **Review Process**: Der Überprüfungsprozess von Google erforderte eine ordnungsgemäße Einhaltung der Datenrichtlinien, insbesondere für die Benutzerauthentifizierung.


---

## Abschluss

Der Bau von Shellmaster war eine aufregende Reise, die **Flutter’s UI capabilities, PocketBase’s lightweight backend, Unleash’s feature flags, and Google Play Console deployment** kombiniert.Das Ergebnis ist eine unterhaltsame und pädagogische Quiz -App, mit der Benutzer ihre Linux -Shell -Fähigkeiten interaktiv verbessern können.

Wenn Sie interessiert sind, schauen Sie sich **Shellmaster** in der [Shellmaster - Apps on Google Play](https://play.google.com/store/apps/details?id=com.matschcode.shellmaster) an und lassen Sie mich Ihre Gedanken wissen!

Was sind einige interessante Tech -Stapel, die Sie in Ihren Apps verwendet haben?Lassen Sie uns in den Kommentaren diskutieren!