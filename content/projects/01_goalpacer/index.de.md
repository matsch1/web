---
ShowToc: true
TocOpen: true
base_hash: 493bf4a837f2c4ff15fd8e74524f2682116fde7e67287cda0e598e41cf5e4899
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
tags:
- flutter
- sports
- application
title: Erste Flutter-App für das Marathontraining
---

Ich bin stolz zu sagen, dass ich meine erste Flutter-App in 4 Tagen mehr oder weniger produktionsreif bauen konnte.

Vor dieser Zeit hatte ich noch keine Erfahrung mit Flutter. Aber ich mochte schon immer die Idee, einfach Apps für den persönlichen Gebrauch zu erstellen.
Nach einigen fehlgeschlagenen Versuchen, in den letzten zwei Jahren einige nützliche persönliche Apps mit Python zu erstellen, hörte ich von Flutter.
Diesen Monat hatte ich also etwas freie Zeit und stellte mich der Herausforderung, Flutter zu lernen, eine Android-App zu erstellen und sie innerhalb von 4 Tagen im Google Play Store zu veröffentlichen.

Die App, die ich mir ausgesucht habe, ist eine Art Pacing-Rechner, den ich für das Lauf- und Triathlon-Training verwenden kann. Zu diesem Zweck habe ich bisher ein Google Doc verwendet. Ich brauche nur ein paar einfache Zeichenfolgen und mathematische Operationen auf ein paar Seiten, kein Backend erforderlich. Das scheint mir perfekt für meine erste App zu sein, nicht zu komplex und ich würde es nutzen, um mein Training in Zukunft zu optimieren.

Der Entwicklungsprozess beginnt eigentlich einen Tag zu früh. Mit meinem Plan konnte ich es nicht abwarten und habe am Abend von Tag 0 mit Hilfe der [Flutter Crash Course](https://youtu.be/j_rCDc_X-k8?si=OqmFujJvhpzCYK5O) von Net Ninja auf Youtube eine Kaffeekarten-App gebaut.
Mit den Erkenntnissen aus diesem Tutorial beginne ich am Morgen von Tag 1 mit meiner eigenen Flutter-App namens [Goalpacer - Google Play Store](https://play.google.com/store/apps/details?id=com.matschcode.goalpacer).

In den nächsten 3 Tagen konnte ich diese App mit VSCO auf meinem Linux-Rechner erstellen. Ich habe es geschafft, 4 Funktionalitäten bereitzustellen:

- Finish Time Calculator: Berechnet die Zielzeit basierend auf der eigenen Geschwindigkeit beim Laufen, Schwimmen und Radfahren.
- Pace-Rechner: Berechnet die notwendige Pace für Ihre gewünschte Zielzeit
- Herzfrequenz-Zonen-Rechner: Schätzen Sie Ihre Herzfrequenzbereiche auf der Grundlage Ihrer maximalen Herzfrequenz
- Pace Converter: Konvertiert die Pace von min/mile in min/km

Auch wenn das Design ziemlich einfach und alles andere als perfekt ist, bin ich mit dem Ergebnis sehr zufrieden.

Der letzte Schritt ist die Veröffentlichung der App im Google Play Store. Am Ende ist das komplizierter als ich erwartet habe. Im Moment befinde ich mich in einem Zustand, in dem ich nach Testern für den geschlossenen Kreislauf suche. Als privater Erstentwickler ist es notwendig, einen Closed-Loop-Test mit 20 Personen durchzuführen, bevor man die App im Play Store veröffentlichen kann.

{{< galleries >}}
{{< gallery src="https://play-lh.googleusercontent.com/_gqr1RR1sYASzLR5yPkzHaX3hp704e63VvNj1iWg1COAGxZYk2aUxu0MyK3GN33Mww=w2560-h1440" title="Home Screen">}}
{{< gallery src="https://play-lh.googleusercontent.com/BLCCMgKAVVZb880iBsN1-7dztMIvxrEfwzJ5fWRwx_8_4LglkeUhW91XsuHpOyR5WA=w2560-h1440" title="Time Calculator" >}}
{{< gallery src="https://play-lh.googleusercontent.com/Qq14Cvd2ZVo0jwOdaeQYBXq9QLC04kuvgzH4MiZjDCOenBtGX2bTve_a9ltRuX0hWQQ=w2560-h1440" title="Pace Calculator" >}}
{{< gallery src="https://play-lh.googleusercontent.com/I0a0iCv3VMvLLK9TpGksVQeNOknJGyFZs14RMOT32l4hU6TLOfKlijU5WzKf8deLXw=w2560-h1440" title="Heartrate zones" >}}
{{< gallery src="https://play-lh.googleusercontent.com/L0XSeuoHSrN_Wc6hBoizI4Mx9QojKRFLEwAGzeKMkmu2Ro9jflzqYuoFnDEC_bwCyyc=w2560-h1440" title="Unit Converter" >}}
{{< gallery src="https://play-lh.googleusercontent.com/xoah8BMs4Z-KymeAH-HoezaqG-cIUWQrhMDQzex3H57MffhljxDa9LLM7d8ezU2_Xw=w2560-h1440" title="Split times" >}}
{{< /galleries >}}