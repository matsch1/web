---
ShowToc: true
TocOpen: true
base_hash: e4d8d9a1cc6b34cbba80f279da0ac7c69a2c8335daaf30581c842fbfc36894f9
date: 2025-01-07
description: My learnings during flutter refactoring
draft: false
img: img1.webp
title: 7 Wege zur Refaktorierung Ihrer Flutter-Anwendung
---

![header-image](img1.webp)
Refactoring ist ein wichtiger Teil der Wartung und Verbesserung Ihrer Flutter-Anwendung.
Es stellt sicher, dass Ihre Codebasis sauber, konsistent und effizient bleibt, während Ihre Anwendung wächst.
In diesem Artikel werden wir sieben praktische Möglichkeiten zum Refactoring Ihrer Flutter-Anwendung untersuchen.

## 1. Parameter in Widgets für Konsistenz verwenden

Beim Erstellen von Widgets kann das Festcodieren von Werten wie padding oder fontSize zu Inkonsistenzen führen. Übergeben Sie diese Werte stattdessen als Parameter, um Widgets wiederverwendbar und konsistent zu machen.

### Beispiel: Verwendung von Parametern anstelle von fest kodierten Werten
```dart
class GreetingWidget extends StatelessWidget {
  final String name;
  final double _fontSize = 20;
  final double _paddingVal = 10;

  const GreetingWidget({
    required this.name,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final String greeting = 'Hello, $name!'; // Internal parameter

    return Padding(
      padding: EdgeInsets.all(_paddingVal),
      child: Column(children: [
        Text(
          greeting,
          style: TextStyle(fontSize: _fontSize),
        ),
        Text(
          "nice to see you!",
          style: TextStyle(fontSize: _fontSize),
        ),
      ]),
    );
  }
}
```
Indem man `paddingVal` und `fontSize` als interne Parameter definiert, kann das GreetingWidget leicht gewartet werden.

---

## 2. Erstellen einer globalen Parameterdatei

Der nächste Schritt nach der Erstellung interner Parameter für die Konsistenz ist die Erstellung globaler Parameter für die Konsistenz.
Alle Werte, die in Ihrer Anwendung konsistent bleiben sollen, wie Farben, Skalierungsfaktoren oder Schaltflächengrößen, speichern Sie in einer globalen Datei.
Diese Datei braucht keine besondere Formatierung. Sie können sie einfach so erstellen.

### Beispiel: Globale Parameterdatei
```dart
// wrapperBox
double boxWidthFactor = 0.9;
double paddingVal = 10;
double borderWidth = 3;
double borderRadius = 10;
double boxHeaderTextSize = 16;
```
Um diese globalen Parameter in verschiedenen Dateien zu verwenden. Importieren Sie einfach die globale Parameterdatei zu Beginn.
### Verwendung:
```dart
import 'package:<appName>/common/src/globals.dart';

Text(
  'Hello, World!',
  style: TextStyle(fontSize: boxHeaderTextSize),
);
```
Dieser Ansatz gewährleistet Konsistenz in der gesamten Anwendung und vereinfacht Aktualisierungen.

---

## 3. Organisieren Sie Ihre Dart-Dateien effektiv

Ein gut strukturiertes `lib`-Verzeichnis verbessert die Lesbarkeit und Wartbarkeit des Codes. Eine gängige Struktur ist die Feature-basierte Organisation:

### Beispiel Dateistruktur
```
lib/
|-- features/
|   |-- home/
|   |   |-- home_screen.dart
|   |   |-- home_controller.dart
|-- shared/
|   |-- classes/
|   |-- funcs/
|   |-- widgets/
|   |-- utils/
|   |-- themes.dart
```

Unter [Flutter Professional Folder Structure: Feature-first or Layer-first?](https://codingwitht.com/flutter-folder-structure/) finden Sie eine ausführliche Anleitung zur Dateiorganisation.

---

## 4. Benutzerdefinierte Widgets für Wiederverwendbarkeit erstellen

Wenn Sie feststellen, dass Sie ähnliche Widgets duplizieren, extrahieren Sie sie in benutzerdefinierte Widgets. Dies reduziert die Codeduplizierung und verbessert die Wartbarkeit.

### Beispiel: Extrahieren eines benutzerdefinierten Widgets
```dart
class CustomCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final double _fontSize = 12;

  const CustomCard({
    required this.title,
    required this.subtitle,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(paddingVal),
        child: Column(children: [
          ListTile(
            title: Text(title),
            subtitle: Text(subtitle),
          ),
          Text(
            "Hello hacker",
            style: TextStyle(fontSize: _fontSize),
          ),
          Text(
            "nice to see you!",
            style: TextStyle(fontSize: _fontSize),
          ),
        ]),
      ),
    );
  }
}
```

### Verwendung:
```dart
CustomCard(title: 'Flutter', subtitle: 'Custom Widgets');
```

---

## 5. Unterscheidung von internen und externen Parametern/Methoden

Bei der Arbeit mit Flutter ist es wichtig, zwischen internen und externen Parametern oder Methoden zu unterscheiden.
**Internal parameters or methods** sind privat für das Widget und haben typischerweise einen Unterstrich (`_`) als Präfix,
während **external parameters or methods** für andere Widgets oder Teile der App zugänglich sind und dieses Präfix fehlt.

### Wann wird ein Unterstrich verwendet?

- Verwenden Sie einen Unterstrich (`_`) für **private** Eigenschaften oder Methoden, auf die außerhalb des Widgets nicht zugegriffen werden soll.
- Interne Parameter oder Methoden sind nur für die Verwendung innerhalb der Implementierung des Widgets gedacht.

### Beispiel: Interner Parameter mit Unterstrich

```dart
class CounterWidget extends StatefulWidget {
  @override
  _CounterWidgetState createState() => _CounterWidgetState();
}

class _CounterWidgetState extends State<CounterWidget> {
  int _count = 0; // Internal parameter

  void _increment() { // Internal method
    setState(() {
      _count++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Count: $_count'),
        ElevatedButton(onPressed: _increment, child: Text('Increment')),
      ],
    );
  }
}
```

In diesem Beispiel sind `_count` und `_increment` intern und sollten nicht außerhalb von `_CounterWidgetState` aufgerufen werden.

### Wann sollte ein Unterstrich vermieden werden?

- Vermeiden Sie Unterstriche für **public**-Eigenschaften oder -Methoden, die von übergeordneten Widgets oder anderen Komponenten verwendet werden sollen.
- Externe Parameter oder Methoden definieren die API Ihres Widgets und sollten zugänglich sein.

### Beispiel: Externe Parameter

```dart
class GreetingWidget extends StatelessWidget {
  final String name; // External parameter

  GreetingWidget({required this.name});

  @override
  Widget build(BuildContext context) {
    return Text('Hello, $name!');
  }
}
```

Hier ist `name` ein externer Parameter, der vom übergeordneten Widget übergeben wird und das Verhalten des Widgets definiert.

### Bewährte Praktiken

- Verwenden Sie Unterstriche (`_`) für private/interne Eigenschaften oder Methoden, um Implementierungsdetails zu kapseln.
- Halten Sie externe Parameter sauber und intuitiv, um eine klare API für Ihre Widgets zu schaffen.

---

## 6. Widgets anhand der Bildschirmgröße skalieren

Um Ihre Anwendung reaktionsfähig zu machen, skalieren Sie Widgets je nach Bildschirmgröße mit der Klasse `MediaQuery`.

### Beispiel: Reaktionsfähiges Padding

```dart
class ResponsiveBox extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    double screenWidth = MediaQuery.of(context).size.width;

    return SizedBox(
      width: screenWidth*0.8;
      child: Text('Responsive Box'),
    );
  }
}
```

Dies stellt sicher, dass sich Ihre Benutzeroberfläche an verschiedene Bildschirmgrößen anpasst und verhindert, dass Ihre Anwendung überläuft.

---

## 7. Verwendung von Providern: Staat effektiv verwalten

Das `provider`-Paket vereinfacht die Zustandsverwaltung, indem es den Widgets erlaubt, auf Änderungen zu hören und sie entsprechend neu zu erstellen.
Dies ist notwendig, wenn Sie die gleichen Daten in verschiedenen Widgets benötigen (lesen oder schreiben).
Hier sind zwei beliebte Providertypen, die ich bereits verwendet habe:

### **ChangeNotifierProvider**

Verwenden Sie `ChangeNotifierProvider` für die Verwaltung veränderlicher Zustände.
Zum Beispiel eine Quizspiel-App mit einem QuizProvider.
Wenn ein Widget die Quizdaten mit Hilfe des QuizProviders ändert, wird jeder Verbraucher der Quizdaten nicht berücksichtigt.

#### Beispiel: Quizspiel-App

```dart
import 'package:provider/provider.dart';

const GameUI({
  super.key,
});

@override
Widget build(BuildContext context) {

  return MultiProvider(
    providers: [
      ChangeNotifierProvider(
        create: (context) => QuizProvider(),
      ),
    ],
    child: const Scaffold(
      appBar: CustomAppBar(),
      body: Body(),
    ),
  );
}
class QuizProvider with ChangeNotifier {
  late QuizGame _quizGame;
  QuizProvider({});

  void loadGame() async {
    var questions = await fetchAllQuestions();
    _quizGame =
        QuizGame();
    _quizGame.init();
    notifyListeners();
  }

  void selectAnswer(int selectedAnswers) {
    _quizGame.currentQuestion.selectedAnswer = selectedAnswers;
    notifyListeners();
  }

  void submitAnswer() async {
    _quizGame.submitAnswer();
    notifyListeners();
  }

  void nextQuestion() async {
    // await Future.delayed(const Duration(milliseconds: 200));
    _quizGame.nextQuestion();
    notifyListeners();
  }
}
```
Auf die QuizProvider-Daten kann mit ``context.watch<QuizProvider>()`` or manipulated using ``context.read<QuizProvider>().submitAnswer()``

### **FutureProvider**

Use `FutureProvider` für Widgets zugegriffen werden, die von asynchronen Daten abhängen.

#### Beispiel: Abrufen von Benutzerdaten

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

void main() {
  runApp(
    FutureProvider<User>(
      create: (context) => fetchUser(),
      initialData: User(name: 'Loading...', email: 'Loading...'),
      child: MyApp(),
    ),
  );
}

class User {
  final String name;
  final String email;

  User({required this.name, required this.email});
}

Future<User> fetchUser() async {
  await Future.delayed(Duration(seconds: 2)); // Simulate network delay
  return User(name: 'John Doe', email: 'john.doe@example.com');
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: UserScreen(),
    );
  }
}

class UserScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final user = Provider.of<User>(context);

    return Scaffold(
      appBar: AppBar(title: Text('User Info')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('Name: ${user.name}', style: TextStyle(fontSize: 24)),
            SizedBox(height: 10),
            Text('Email: ${user.email}', style: TextStyle(fontSize: 18)),
          ],
        ),
      ),
    );
  }
}
```

---

Refactoring muss nicht überwältigend sein. Durch die Anwendung dieser sieben Techniken können Sie die Wartbarkeit, Skalierbarkeit und Gesamtqualität Ihrer Flutter-Anwendung verbessern.