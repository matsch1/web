---
title: "7 Ways to Refactor Your Flutter Application"
date: 2025-01-07
description: "My learnings during flutter refactoring"
ShowToc: true
TocOpen: true
draft: false
cover:
  image: "img1.webp"
  alt: "flutter-refactoring"
  caption: ""
  relative: true
params:
  ShowPostNavLinks: true
---
Refactoring is a vital part of maintaining and improving your Flutter application. 
It ensures your codebase remains clean, consistent, and efficient as your app grows. 
In this article, we’ll explore seven practical ways to refactor your Flutter application.

## 1. Use Parameters in Widgets for Consistency

When building widgets, hardcoding values like padding or fontSize can lead to inconsistencies. Instead, pass these values as parameters to make widgets reusable and consistent.

### Example: Use parameters instead of hardcoded values
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
By defining `paddingVal` and `fontSize` as internal parameters, the GreetingWidget can easily maintained.

---

## 2. Create a Global Parameter File

The next step to creating internal parameters for consistency, is creating global parameters for consistency.
All values that should remain consistent throughout your app, such as colors, scaling factors, or button sizes, store them in a global file.
This file doesn't need a special formatting. You can easily make it like this.

### Example: Global Parameters File
```dart
// wrapperBox
double boxWidthFactor = 0.9;
double paddingVal = 10;
double borderWidth = 3;
double borderRadius = 10;
double boxHeaderTextSize = 16;
```
To use this global parameters in different files. Just import the global parameter file at the beginnging.
### Usage:
```dart
import 'package:<appName>/common/src/globals.dart';

Text(
  'Hello, World!',
  style: TextStyle(fontSize: boxHeaderTextSize),
);
```
This approach ensures consistency across the entire app and simplifies updates.

---

## 3. Organize Your Dart Files Effectively

A well-structured `lib` directory improves code readability and maintainability. A common structure is feature-based organization:

### Example File Structure
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

Refer to [Flutter Professional Folder Structure: Feature-first or Layer-first?](https://codingwitht.com/flutter-folder-structure/) for an in-depth guide to file organization.

---

## 4. Create Custom Widgets for Reusability

If you find yourself duplicating similar widgets, extract them into custom widgets. This reduces code duplication and improves maintainability.

### Example: Extracting a Custom Widget
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

### Usage:
```dart
CustomCard(title: 'Flutter', subtitle: 'Custom Widgets');
```

---

## 5. Differentiate Internal and External Parameters/Methods

When working with Flutter, distinguishing between internal and external parameters or methods is essential. 
**Internal parameters or methods** are private to the widget and typically have an underscore (`_`) prefix, 
while **external parameters or methods** are exposed to other widgets or parts of the app and lack this prefix.

### When to Use an Underscore

- Use an underscore (`_`) for **private** properties or methods that should not be accessed outside the widget.
- Internal parameters or methods are intended for use within the widget's implementation only.

### Example: Internal Parameter with Underscore

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

In this example, `_count` and `_increment` are internal and should not be accessed outside `_CounterWidgetState`.

### When to Avoid an Underscore

- Avoid underscores for **public** properties or methods that are meant to be used by parent widgets or other components.
- External parameters or methods define the API of your widget and should be accessible.

### Example: External Parameters

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

Here, `name` is an external parameter passed by the parent widget, defining the widget's behavior.

### Best Practices

- Use underscores (`_`) for private/internal properties or methods to encapsulate implementation details.
- Keep external parameters clean and intuitive to create a clear API for your widgets.

---

## 6. Scale Widgets Using Screen Size

To make your app responsive, scale widgets based on screen size using the `MediaQuery` class.

### Example: Responsive Padding

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

This ensures your UI adapts gracefully to different screen sizes and prevents your app from overflow.

---

## 7. Usage of Providers: Managing State Effectively

The `provider` package simplifies state management by allowing widgets to listen to changes and rebuild accordingly. 
This is necessary if you need the same data in different widgets (read or write).
Here are two popular provider type I already used:

### **ChangeNotifierProvider**

Use `ChangeNotifierProvider` for managing mutable state.
For example a quiz game app with a QuizProvider. 
If some widget modifies the quiz data with the help of the QuizProvider, every Consumer of the quizd data will be notfied.

#### Example: Quiz Game App

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
The QuizProvider data can be accessed using ``context.watch<QuizProvider>()`` or manipulated using ``context.read<QuizProvider>().submitAnswer()``

### **FutureProvider**

Use `FutureProvider` for widgets that depend on asynchronous data.

#### Example: Fetching User Data

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

Refactoring doesn’t have to be overwhelming. By applying these seven techniques, you can improve your Flutter application’s maintainability, scalability, and overall quality.


