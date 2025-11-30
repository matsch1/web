---
ShowToc: true
TocOpen: true
base_hash: 9c89e19e3828eb3da11e53671bbea800cde586cf64bec685e4149115bc398e27
cover:
  alt: goalpacer
  caption: ''
  image: img1.webp
  relative: true
date: 2024-11-16
description: Explanation of how I build my first app for martathon training using
  Flutter
draft: false
slug: goalpacer-pace-estimator
title: Erste Flutter-App für das Marathontraining
---

Ich bin stolz zu sagen, dass ich meine erste Flutter-App in 4 Tagen mehr oder weniger produktionsreif bauen konnte.

Vor dieser Zeit hatte ich noch keine Erfahrung mit Flutter. Aber ich mochte schon immer die Idee, einfach Apps für den persönlichen Gebrauch zu erstellen.
Nach einigen fehlgeschlagenen Versuchen, in den letzten zwei Jahren einige nützliche persönliche Apps mit Python zu erstellen, hörte ich von Flutter.
Diesen Monat hatte ich also etwas freie Zeit und stellte mich der Herausforderung, Flutter zu lernen, eine Android-App zu erstellen und sie innerhalb von 4 Tagen im Google Play Store zu veröffentlichen.

Die App, die ich mir ausgesucht habe, ist eine Art Pacing-Rechner, den ich für das Lauf- und Triathlon-Training verwenden kann. Zu diesem Zweck habe ich bisher ein Google Doc verwendet. Ich brauche nur ein paar einfache Zeichenfolgen und mathematische Operationen auf ein paar Seiten, kein Backend erforderlich. Das scheint mir perfekt für meine erste App zu sein, nicht zu komplex und ich würde es nutzen, um mein Training in Zukunft zu optimieren.

Der Entwicklungsprozess beginnt eigentlich einen Tag zu früh. Mit meinem Plan konnte ich es nicht abwarten und habe am Abend von Tag 0 mit Hilfe der [Flutter Crash Course](https://youtu.be/j_rCDc_X-k8?si=OqmFujJvhpzCYK5O) von Net Ninja auf Youtube eine Kaffeekarten-App gebaut.
Mit den Erkenntnissen aus diesem Tutorial beginne ich am Morgen von Tag 1 mit meiner eigenen Flutter-App namens "GOALPACER".

In den nächsten 3 Tagen konnte ich diese App mit VSCO auf meinem Linux-Rechner erstellen. Ich habe es geschafft, 4 Funktionalitäten bereitzustellen:

- Zielzeit-Rechner: Berechnet die Zielzeit basierend auf der eigenen Geschwindigkeit beim Laufen, Schwimmen und Radfahren.
- Pace-Rechner: Berechnet die notwendige Pace für Ihre gewünschte Zielzeit
- Herzfrequenz-Zonen-Rechner: Schätzen Sie Ihre Herzfrequenzbereiche auf der Grundlage Ihrer maximalen Herzfrequenz
- Pace Converter: Konvertiert die Pace von min/mile in min/km

Auch wenn das Design ziemlich einfach und alles andere als perfekt ist, bin ich mit dem Ergebnis sehr zufrieden.

Der letzte Schritt ist die Veröffentlichung der App im Google Play Store. Am Ende ist das komplizierter als ich erwartet habe. Im Moment befinde ich mich in einem Zustand, in dem ich nach Testern für den geschlossenen Kreislauf suche. Als privater Erstentwickler ist es notwendig, einen Closed-Loop-Test mit 20 Personen durchzuführen, bevor man die App im Play Store veröffentlichen kann.

Wenn Sie also Interesse an der App haben oder sich mit mir unterhalten wollen, können Sie mich gerne kontaktieren. Ich würde gerne einige Tester aus der Community gewinnen, um unabhängige Meinungen von verschiedenen Leuten zu erhalten.


![Home Screen](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/1wxmur6qdkg6rch09i0e.png)
![Finish Time Calculator](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/06ixfkec9wzsxvg1xvbb.png)