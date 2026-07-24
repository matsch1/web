---
ShowToc: true
TocOpen: true
base_hash: ead31e0053daeaed284740a3fe5a45ae95fd8f8f6761f2d02cf42318fb13a2e3
cover:
  alt: flutter-refactoring
  caption: ''
  image: img1.webp
  relative: true
date: 2025-01-07
description: Meine Erkenntnisse beim Refactoring mit Flutter
draft: false
slug: flutter-refactoring
tags:
- flutter
title: 7 Möglichkeiten, Ihre Flutter-Anwendung zu refaktorisieren
---

Refactoring ist ein wesentlicher Bestandteil der Wartung und Verbesserung Ihrer Flutter-Anwendung. 
Es sorgt dafür, dass Ihr Code auch bei wachsender App übersichtlich, konsistent und effizient bleibt. 
In diesem Artikel stellen wir Ihnen sieben praktische Methoden zum Refactoring Ihrer Flutter-Anwendung vor.

## 1. Verwenden Sie Parameter in Widgets, um Konsistenz zu gewährleisten

Beim Erstellen von Widgets kann die Festcodierung von Werten wie „padding“ oder „fontSize“ zu Inkonsistenzen führen. Übergeben Sie diese Werte stattdessen als Parameter, um Widgets wiederverwendbar und konsistent zu machen.

### Beispiel: Verwenden Sie Parameter anstelle von festcodierten Werten
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

## 2. Erstellen Sie eine globale Parameterdatei

Der nächste Schritt nach der Erstellung interner Parameter zur Gewährleistung der Konsistenz ist die Erstellung globaler Parameter.
Alle Werte, die in Ihrer gesamten App konsistent bleiben sollen, wie Farben, Skalierungsfaktoren oder Schaltflächengrößen, speichern Sie in einer globalen Datei.
Diese Datei erfordert keine spezielle Formatierung. Sie können sie ganz einfach wie folgt erstellen.

### Beispiel: Globale Parameterdatei
```dart
// wrapperBox
double boxWidthFactor = 0.9;
double paddingVal = 10;
double borderWidth = 3;
double borderRadius = 10;
double boxHeaderTextSize = 16;
```
Um diese globalen Parameter in verschiedenen Dateien zu verwenden, importieren Sie einfach die globale Parameterdatei am Anfang.
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

## 3. Organisieren Sie Ihre Dart-Dateien effektiv

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

## 4. Erstellen Sie benutzerdefinierte Widgets zur Wiederverwendbarkeit

Wenn Sie feststellen, dass Sie ähnliche Widgets duplizieren, extrahieren Sie diese in benutzerdefinierte Widgets. Dies reduziert Code-Duplikate und verbessert die Wartbarkeit.

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

## 5. Unterscheiden Sie zwischen internen und externen Parametern/Methoden

Bei der Arbeit mit Flutter ist es unerlässlich, zwischen internen und externen Parametern oder Methoden zu unterscheiden. 
**Interne Parameter oder Methoden** sind privat für das Widget und haben in der Regel ein Unterstrich-Präfix (`_`), 
während **externe Parameter oder Methoden** für andere Widgets oder Teile der App zugänglich sind und dieses Präfix nicht aufweisen.

### Wann wird ein Unterstrich verwendet?

- Verwenden Sie einen Unterstrich (`_`) für **private** Eigenschaften oder Methoden, auf die außerhalb des Widgets nicht zugegriffen werden soll.
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

- Vermeiden Sie Unterstriche bei **öffentlichen** Eigenschaften oder Methoden, die von übergeordneten Widgets oder anderen Komponenten verwendet werden sollen.
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

### Best Practices

- Verwenden Sie Unterstriche (`_`) für private/interne Eigenschaften oder Methoden, um Implementierungsdetails zu kapseln.
- Halten Sie externe Parameter übersichtlich und intuitiv, um eine klare API für Ihre Widgets zu schaffen.

---

## 6. Widgets anhand der Bildschirmgröße skalieren

Um Ihre App responsiv zu gestalten, skalieren Sie Widgets anhand der Bildschirmgröße mithilfe der Klasse `MediaQuery`.

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

Dadurch wird sichergestellt, dass sich Ihre Benutzeroberfläche nahtlos an verschiedene Bildschirmgrößen anpasst und ein Überlaufen Ihrer App verhindert wird.

---

## 7. Verwendung von Providern: Effektives Statusmanagement

Das `provider`-Paket vereinfacht die Zustandsverwaltung, indem es Widgets ermöglicht, auf Änderungen zu reagieren und sich entsprechend neu aufzubauen. 
Dies ist notwendig, wenn Sie dieselben Daten in verschiedenen Widgets benötigen (zum Lesen oder Schreiben).
Hier sind zwei beliebte Provider-Typen, die ich bereits verwendet habe:

### **ChangeNotifierProvider**

Verwenden Sie `ChangeNotifierProvider` zur Verwaltung veränderbarer Zustände.
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
Auf die Daten des QuizProviders kann über ``context.watch<QuizProvider>()`` or manipulated using ``context.read<QuizProvider>().submitAnswer()``

### **FutureProvider**

Use `FutureProvider` auf die Daten des QuizProviders zugegriffen werden.

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

Refactoring muss nicht unbedingt eine überwältigende Aufgabe sein. Durch die Anwendung dieser sieben Techniken können Sie die Wartbarkeit, Skalierbarkeit und Gesamtqualität Ihrer Flutter-Anwendung verbessern.