---
title: " Building Shellmaster: A Fun Way to Learn Linux Shell Commands "
slug: "building-shellmaster"
date: 2025-04-06
description: "My path of building a quiz app using flutter, pocketbase and unleash"
ShowToc: true
TocOpen: true
draft: false
cover:
  image: "img1.webp"
  alt: "shellmaster"
  caption: ""
  relative: true
params:
  ShowPostNavLinks: true
---
Learning Linux shell commands can be daunting, but what if it could be fun? That’s the idea behind **Shellmaster**, a quiz game app that helps users master shell and bash commands through engaging quizzes. 
Check it out on Google Play Store: [Shellmaster - Apps on Google Play](https://play.google.com/store/apps/details?id=com.matschcode.shellmaster)
While building Shellmaster, I encountered several interesting technical challenges and learned a lot about **Flutter**, **PocketBase**, **Unleash feature flags**, and **Google Play Console deployment**. In this article, I’ll share some key takeaways from the development journey.
## Table of Contents

1. [App Features](#app-features)
2. [App Development](#app-development)
	1. [Choosing Flutter for a Cross-Platform Quiz App](#choosing-flutter-for-a-cross-platform-quiz-app)
	2. [PocketBase as a Lightweight Backend](#pocketbase-as-a-lightweight-backend)
	3. [Using Unleash for Feature Flags](#using-unleash-for-feature-flags)
	4. [Deploying via Google Play Console](#deploying-via-google-play-console)
3. [Conclusion](#conclusion)


---

## App Features

Shellmaster is designed to make learning Linux commands fun and interactive. Here are some of its key features:

- **Multiple Quiz Modes**: Test your knowledge with different game modes, including timed quizzes and practice sessions.
- **Difficulty Levels & Categories**: Questions are categorized into easy, medium, and hard levels, covering essential shell commands, scripting, and system administration.
- **Progress Tracking**: Keep track of your performance and improve over time.
- **Custom Challenges**: Users can set their own challenges and compete with friends.
- **Offline Support**: Play quizzes without requiring an internet connection.
- **Dark Mode**: Enjoy a sleek dark mode for better readability.

---

## APP Development

The next chapters are about my learning during the development process.
If you are interested in some nice Flutter stuff keep reading. If you are only here for Linux and Bash check the app out on Google Play Store [Shellmaster - Apps on Google Play](https://play.google.com/store/apps/details?id=com.matschcode.shellmaster).
### Choosing Flutter for a Cross-Platform Quiz App

I chose **Flutter** because of its **fast development cycle, beautiful UI capabilities, and cross-platform support**. With a single codebase, I could target both Android and (potentially) iOS in the future. Some of the key Flutter features I leveraged include:

- **Custom UI components**: I built a custom AppBar (`CSAppBar`) for a consistent look.
- **State management**: I used `provider` to handle quiz state and user preferences efficiently.
- **Smooth animations**: Animated background color changes in the quiz questions enhance the user experience.

---

### PocketBase as a Lightweight Backend

For managing quiz data, user progress, and authentication, I opted for **PocketBase**, an open-source backend written in Go. It provides a **SQLite database, real-time subscriptions, and an API with minimal setup**. Here’s why it worked well for Shellmaster:

- **Self-hosted control**: Running PocketBase on my VPS gives me full data ownership.
- **Easy integration**: PocketBase exposes a REST API that Flutter’s `http` package can easily consume.
- **User authentication**: Built-in authentication allowed me to manage user progress across devices. I will add the possibility for user login in the future.

### Example: Fetching Quiz Data from PocketBase

```dart
Future<List<Question>> fetchQuestions() async {
  final response = await http.get(Uri.parse('https://your-pocketbase-url/api/collections/questions/records'));
  final data = jsonDecode(response.body);
  return data['items'].map<Question>((json) => Question.fromJson(json)).toList();
}
```

---

### Using Unleash for Feature Flags

To enable **progressive feature rollouts and A/B testing**, I integrated **Unleash**, an open-source feature flag system. This allowed me to **toggle features dynamically** without releasing a new app update.

#### Why Use Feature Flags?

- **Experiment with new features** (e.g., a “hardcore mode” for experienced users)
- **Enable/disable features remotely** without requiring an app update
- **Gradual rollouts** for testing on a subset of users

#### Implementing Feature Flags in Flutter

```dart
final unleash = UnleashClient(appName: 'shellmaster', instanceId: 'your-instance-id', url: 'https://your-unleash-server');
await unleash.start();
bool isHardcoreModeEnabled = unleash.isEnabled('hardcore-mode');
```

---

### Deploying via Google Play Console

Publishing Shellmaster on the **Google Play Store** involved several key steps:

1. **App Signing & Bundling**: Flutter’s `flutter build appbundle` made generating an **AAB** package easy.
2. **Play Console Setup**: Setting up **store listings, screenshots, and descriptions** took more time than expected.
3. **Testing & Release Tracks**: Using **internal, closed, and open testing** helped catch bugs before full deployment.
4. **Review Process**: Google’s review process required proper compliance with data policies, especially for user authentication.


---

## Conclusion

Building Shellmaster has been an exciting journey, combining **Flutter’s UI capabilities, PocketBase’s lightweight backend, Unleash’s feature flags, and Google Play Console deployment**. The result is a fun and educational quiz app that helps users improve their Linux shell skills interactively.

If you're interested, check out **Shellmaster** on the [Shellmaster - Apps on Google Play](https://play.google.com/store/apps/details?id=com.matschcode.shellmaster) and let me know your thoughts!

What are some interesting tech stacks you've used in your apps? Let’s discuss in the comments!

