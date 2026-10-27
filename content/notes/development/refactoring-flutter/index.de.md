---
ShowToc: true
TocOpen: true
base_hash: a91ee7eaee91272b9d19fb91243ccde513800e460f1c07fd9b24950d9951223a
cover:
  alt: flutter-refactoring
  caption: ''
  image: editorial-cover.webp
  relative: true
date: 2025-01-07
description: Meine Erkenntnisse beim Refactoring mit Flutter
draft: false
slug: flutter-refactoring
tags:
- flutter
title: 7 Möglichkeiten, deine Flutter-App zu refaktorisieren
homepage:
  teaser: 'Widgets vereinfachen, Werte wiederverwenden und Code strukturieren: praktische
    Beispiele aus meinem Flutter-Refactoring.'
  title: Sieben Ansätze fürs Flutter-Refactoring
translation_lock: true
---

Refactoring ist ein wesentlicher Bestandteil der Wartung und Verbesserung deiner Flutter-App.
Es sorgt dafür, dass dein Code auch bei wachsender App übersichtlich, konsistent und effizient bleibt.
In diesem Artikel zeige ich dir sieben praktische Methoden zum Refactoring deiner Flutter-App.

## 1. Verwende Parameter in Widgets, um Konsistenz zu gewährleisten

Beim Erstellen von Widgets kann das Festschreiben von Werten wie „padding“ oder „fontSize“ zu Inkonsistenzen führen. Übergib diese Werte stattdessen als Parameter, um Widgets wiederverwendbar und konsistent zu machen.

### Beispiel: Verwende Parameter anstelle von festgeschriebenen Werten
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
Durch die Definition von `paddingVal` und `fontSize` als interne Parameter lässt sich das GreetingWidget leicht warten.

---

## 2. Erstelle eine globale Parameterdatei

Der nächste Schritt nach der Erstellung interner Parameter zur Gewährleistung der Konsistenz ist die Erstellung globaler Parameter.
Alle Werte, die in deiner gesamten App konsistent bleiben sollen, wie Farben, Skalierungsfaktoren oder Schaltflächengrößen, speicherst du in einer globalen Datei.
Diese Datei benötigt keine spezielle Formatierung. Du kannst sie ganz einfach wie folgt erstellen.

### Beispiel: Globale Parameterdatei
```dart
// wrapperBox
double boxWidthFactor = 0.9;
double paddingVal = 10;
double borderWidth = 3;
double borderRadius = 10;
double boxHeaderTextSize = 16;
```
Um diese globalen Parameter in verschiedenen Dateien zu verwenden, importiere einfach die globale Parameterdatei am Anfang.
### Verwendung:
```dart
import 'package:<appName>/common/src/globals.dart';

Text(
  'Hello, World!',
  style: TextStyle(fontSize: boxHeaderTextSize),
);
```
Dieser Ansatz gewährleistet Konsistenz in der gesamten App und vereinfacht Aktualisierungen.

---

## 3. Organisiere deine Dart-Dateien effektiv

Ein gut strukturiertes `lib`-Verzeichnis verbessert die Lesbarkeit und Wartbarkeit des Codes. Eine gängige Struktur ist die funktionsbasierte Organisation:

### Beispiel für eine Dateistruktur
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

Eine ausführliche Anleitung zur Dateiorganisation findest du unter [Flutter Professional Folder Structure: Feature-first or Layer-first?](https://codingwitht.com/flutter-folder-structure/).

---

## 4. Erstelle benutzerdefinierte Widgets zur Wiederverwendbarkeit

Wenn du feststellst, dass du ähnliche Widgets duplizierst, extrahiere diese in benutzerdefinierte Widgets. Dies reduziert Code-Duplikate und verbessert die Wartbarkeit.

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

## 5. Unterscheide zwischen internen und externen Parametern/Methoden

Bei der Arbeit mit Flutter ist es unerlässlich, zwischen internen und externen Parametern oder Methoden zu unterscheiden. 
**Interne Parameter oder Methoden** sind privat für das Widget und haben in der Regel ein Unterstrich-Präfix (`_`), 
während **externe Parameter oder Methoden** für andere Widgets oder Teile der App zugänglich sind und dieses Präfix nicht aufweisen.

### Wann wird ein Unterstrich verwendet?

- Verwende einen Unterstrich (`_`) für **private** Eigenschaften oder Methoden, auf die außerhalb des Widgets nicht zugegriffen werden soll.
- Interne Parameter oder Methoden sind ausschließlich für die Verwendung innerhalb der Implementierung des Widgets vorgesehen.

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

In diesem Beispiel sind `_count` und `_increment` intern und sollten außerhalb von `_CounterWidgetState` nicht aufgerufen werden.

### Wann man Unterstriche vermeiden sollte

- Vermeide Unterstriche bei **öffentlichen** Eigenschaften oder Methoden, die von übergeordneten Widgets oder anderen Komponenten verwendet werden sollen.
- Externe Parameter oder Methoden definieren die API deines Widgets und sollten zugänglich sein.

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

### Best Practices

- Verwende Unterstriche (`_`) für private/interne Eigenschaften oder Methoden, um Implementierungsdetails zu kapseln.
- Halte externe Parameter übersichtlich und intuitiv, um eine klare API für deine Widgets zu schaffen.

---

## 6. Widgets anhand der Bildschirmgröße skalieren

Um deine App responsiv zu gestalten, skaliere Widgets anhand der Bildschirmgröße mithilfe der Klasse `MediaQuery`.

### Beispiel: Responsives Padding

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

Dadurch wird sichergestellt, dass sich deine Benutzeroberfläche nahtlos an verschiedene Bildschirmgrößen anpasst und ein Überlaufen deiner App verhindert wird.

---

## 7. Verwendung von Providern: Effektives Statusmanagement

Das `provider`-Paket vereinfacht die Zustandsverwaltung, indem es Widgets ermöglicht, auf Änderungen zu reagieren und sich entsprechend neu aufzubauen. 
Dies ist notwendig, wenn du dieselben Daten in verschiedenen Widgets benötigst (zum Lesen oder Schreiben).
Hier sind zwei beliebte Provider-Typen, die ich bereits verwendet habe:

### **ChangeNotifierProvider**

Verwende `ChangeNotifierProvider` zur Verwaltung veränderbarer Zustände.
Beispielsweise eine Quiz-App mit einem QuizProvider. 
Wenn ein Widget die Quizdaten mithilfe des QuizProviders ändert, werden alle Verbraucher der Quizdaten benachrichtigt.

#### Beispiel: Quiz-Spiel-App

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
Auf die Daten des QuizProviders kannst du über ``context.watch<QuizProvider>()`` zugreifen und sie mit ``context.read<QuizProvider>().submitAnswer()`` verändern.

### **FutureProvider**

Verwende `FutureProvider` für Widgets, die von asynchronen Daten abhängen.

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

Refactoring muss nicht unbedingt eine überwältigende Aufgabe sein. Mit diesen sieben Techniken kannst du die Wartbarkeit, Skalierbarkeit und Gesamtqualität deiner Flutter-App verbessern.