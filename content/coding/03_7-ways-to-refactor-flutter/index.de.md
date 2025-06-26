---
ShowToc: true
TocOpen: true
base_hash: e4d8d9a1cc6b34cbba80f279da0ac7c69a2c8335daaf30581c842fbfc36894f9
date: 2025-01-07
description: My learnings during flutter refactoring
draft: false
img: img1.webp
title: 7 Möglichkeiten, Ihre Flatter -Anwendung neu zu gestalten
---

![header-image](img1.webp)
Refactoring ist ein wesentlicher Bestandteil der Aufrechterhaltung und Verbesserung Ihrer Flutteranwendung.
Es stellt sicher, dass Ihre Codebasis mit zunehmendem Wachstum Ihrer App sauber, konsistent und effizient bleibt.
In diesem Artikel werden wir sieben praktische Möglichkeiten untersuchen, um Ihre Flutter -Anwendung neu zu gestalten.

## 1. Verwenden Sie Parameter in Widgets zur Konsistenz

Beim Erstellen von Widgets können Hardcoding -Werte wie Polsterung oder Fontsize zu Inkonsistenzen führen.Geben Sie diese Werte stattdessen als Parameter über, um Widgets wiederverwendbar und konsistent zu machen.

### Beispiel: Verwenden Sie Parameter anstelle von hartcodierten Werten
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
Durch Definieren von `paddingVal` und `fontSize` als interne Parameter kann das Grußwidget leicht verwaltet werden.

---

## 2. Erstellen Sie eine globale Parameterdatei

Der nächste Schritt, um interne Parameter für die Konsistenz zu erstellen, besteht darin, globale Parameter für die Konsistenz zu erstellen.
Alle Werte, die in Ihrer App konsistent bleiben sollten, wie z. B. Farben, Skalierungsfaktoren oder Schaltflächengrößen, speichern sie in einer globalen Datei.
Diese Datei benötigt keine spezielle Formatierung.Sie können es leicht so machen.

### Beispiel: Globale Parameterdatei
```dart
// wrapperBox
double boxWidthFactor = 0.9;
double paddingVal = 10;
double borderWidth = 3;
double borderRadius = 10;
double boxHeaderTextSize = 16;
```
Verwenden dieser globalen Parameter in verschiedenen Dateien.Importieren Sie einfach die globale Parameterdatei zu Beginn.
### Verwendung:
```dart
import 'package:<appName>/common/src/globals.dart';

Text(
  'Hello, World!',
  style: TextStyle(fontSize: boxHeaderTextSize),
);
```
Dieser Ansatz gewährleistet die Konsistenz in der gesamten App und vereinfacht Aktualisierungen.

---

## 3. organisieren Sie Ihre DART -Dateien effektiv

Ein gut strukturiertes Verzeichnis `lib` verbessert die Lesbarkeit und die Wartbarkeit der Code.Eine gemeinsame Struktur ist eine featurebasierte Organisation:

### Beispieldateistruktur
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

Eine eingehende Anleitung zur Dateiorganisation finden Sie in [Flutter Professional Folder Structure: Feature-first or Layer-first?](https://codingwitht.com/flutter-folder-structure/).

---

## 4. Erstellen Sie benutzerdefinierte Widgets für die Wiederverwendbarkeit

Wenn Sie ähnliche Widgets duplizieren, extrahieren Sie sie in benutzerdefinierte Widgets.Dies reduziert die Code -Duplikation und verbessert die Wartbarkeit.

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

## 5. Differenzieren Sie interne und externe Parameter/Methoden

Bei der Arbeit mit Flattern ist die Unterscheidung zwischen internen und externen Parametern oder Methoden unerlässlich.
**Internal parameters or methods** sind privat für das Widget und haben normalerweise ein Unterstrich (`_`) Präfix,
Während **external parameters or methods** anderen Widgets oder Teilen der App ausgesetzt sind und dieses Präfix fehlt.

### Wann kann ein Unterstrich verwendet werden

- Verwenden Sie einen Unterstrich (`_`) für **private** Eigenschaften oder Methoden, auf die nicht außerhalb des Widgets zugegriffen werden sollten.
- Interne Parameter oder Methoden dienen nur zur Verwendung in der Implementierung des Widgets.

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

In diesem Beispiel sind `_count` und `_increment` intern und sollten nicht außerhalb `_CounterWidgetState` zugegriffen werden.

### Wann meiden Sie einen Unterstrich?

- Vermeiden Sie Unterstriche für **public** Eigenschaften oder Methoden, die von übergeordneten Widgets oder anderen Komponenten verwendet werden sollen.
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

- Verwenden Sie Unterstriche (`_`) für private/interne Eigenschaften oder Methoden, um die Implementierungsdetails zu verkörpern.
- Halten Sie externe Parameter sauber und intuitiv, um eine klare API für Ihre Widgets zu erstellen.

---

## 6. Skalieren Widgets mithilfe der Bildschirmgröße

Um Ihre App reaktionsschnell zu machen, skalieren Sie Widgets basierend auf der Bildschirmgröße mit der Klasse `MediaQuery`.

### Beispiel: Reaktionsschnelle Polsterung

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

Dies stellt sicher, dass sich Ihre Benutzeroberfläche anmutig an verschiedene Bildschirmgrößen anpasst und Ihre App über Überlauf hindert.

---

## 7. Nutzung von Anbietern: Staat effektiv verwalten

Das Paket `provider` vereinfacht das staatliche Management, indem Widgets Änderungen anhören und entsprechend wieder aufbauen können.
Dies ist erforderlich, wenn Sie dieselben Daten in verschiedenen Widgets benötigen (lesen oder schreiben).
Hier sind zwei beliebte Anbietertypen, die ich bereits verwendet habe:

### **ChangeNotifierProvider**

Verwenden Sie `ChangeNotifierProvider` für die Verwaltung des mutablen Zustands.
Zum Beispiel eine Quizspiel -App mit einem QuizProvider.
Wenn ein Widget die Quizdaten mithilfe des QuizProviders ändert, wird jeder Verbraucher der Quizd -Daten nicht fixiert.

#### Beispiel: Quiz Game App

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
Auf die QuizProvider -Daten können mit `[[00000110000024] [[00000110000025] [[00000110000026] [00000110000025] [[00000110000026] `

### **FutureProvider**

Use ` FutureProvider` für Widgets, die von asynchronen Daten abhängen, zugegriffen werden.

#### Beispiel: Benutzerdaten abrufen

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

Refactoring muss nicht überwältigend sein.Durch die Anwendung dieser sieben Techniken können Sie die Wartbarkeit, Skalierbarkeit und Gesamtqualität Ihrer Flutteranwendung verbessern.