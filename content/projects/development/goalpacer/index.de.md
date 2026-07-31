---
ShowToc: true
TocOpen: true
base_hash: 2a99bc6590744e456b5ff1fe20314c27d83752b1872c8c2bbcb801c17eac7797
cover:
  alt: goalpacer
  caption: ''
  image: img1.webp
  relative: true
date: 2024-11-16
description: Erläuterung, wie ich meine erste App für das Marathontraining mit Flutter
  entwickle
draft: false
gallery_translation_version: 1
homepage:
  featured: false
  section: engineering
  state: archive
project:
  status: discontinued
slug: goalpacer-pace-estimator
tags:
- flutter
- sports
- application
title: Erste Flutter-App für das Marathontraining
---

{{< alert type="warning" title="" >}}
Leider ist die App nicht mehr verfügbar. 
Die Wartung war zu zeitaufwendig, und ich möchte keinen weiteren Aufwand mehr in dieses Projekt stecken.
{{< /alert >}}

Ich bin stolz darauf, dass ich meine erste Flutter-App in etwa vier Tagen mehr oder weniger produktionsreif entwickeln konnte.

Vor diesen Tagen hatte ich keinerlei Erfahrung mit Flutter. Aber mir hat schon immer die Idee gefallen, auf einfache Weise Apps für den persönlichen Gebrauch zu entwickeln. 
Nach einigen gescheiterten Versuchen in den letzten zwei Jahren, mit Python nützliche persönliche Apps zu entwickeln, hörte ich von Flutter.
Da ich diesen Monat etwas Freizeit hatte, stellte ich mir die Herausforderung, Flutter zu lernen, eine Android-App zu entwickeln und sie IN 4 TAGEN im Google Play Store zu veröffentlichen.

Die App, für die ich mich entschieden habe, ist eine Art Temporechner, den ich für mein Lauf- und Triathlontraining nutzen kann. Bislang habe ich für diesen Zweck ein Google Doc verwendet. Ich brauche nur ein paar einfache Zeichenfolgen- und Rechenoperationen auf einigen Seiten, ein Backend ist nicht erforderlich. Das scheint perfekt für meine erste App zu sein – nicht zu komplex und ich würde sie nutzen, um mein Training in Zukunft zu optimieren.

Der Entwicklungsprozess beginnt eigentlich einen Tag zu früh. Bei meinem Plan konnte ich es kaum erwarten, loszulegen, und habe am Abend von Tag 0 mithilfe des [Flutter Crash Course](https://youtu.be/j_rCDc_X-k8?si=OqmFujJvhpzCYK5O) von Net Ninja auf YouTube eine Kaffee-Karten-App erstellt.
Mit den Erkenntnissen aus diesem Tutorial beginne ich am Morgen von Tag 1 mit meiner eigenen Flutter-App namens „Goalpacer“.

In den folgenden drei Tagen gelang es mir, diese App mit VSCO auf meinem Linux-Rechner zu entwickeln. Ich habe vier Funktionen implementiert: 

- Zielzeitrechner: Berechnet die Zielzeit basierend auf deinem Tempo beim Laufen, Schwimmen und Radfahren.
- Temporechner: Berechnet das erforderliche Tempo für Ihre gewünschte Zielzeit
- Herzfrequenzzonen-Rechner: Schätzt Ihre Herzfrequenzzonen anhand Ihrer maximalen Herzfrequenz
- Tempo-Umrechner: Rechnet Tempi von min/Meile in min/km um

Auch wenn das Design recht einfach und bei weitem nicht perfekt ist, bin ich mit dem Ergebnis sehr zufrieden.

Der letzte Schritt ist die Veröffentlichung der App im Google Play Store. Letztendlich ist das komplizierter, als ich erwartet hatte. Momentan bin ich auf der Suche nach Testern für den Closed-Loop-Test. Als privater Erstentwickler ist es erforderlich, einen Closed-Loop-Test mit 20 Personen durchzuführen, bevor man die App im Play Store veröffentlichen kann.

{{< galleries >}}
{{< gallery src="https://play-lh.googleusercontent.com/_gqr1RR1sYASzLR5yPkzHaX3hp704e63VvNj1iWg1COAGxZYk2aUxu0MyK3GN33Mww=w2560-h1440" title="Startseite">}}
{{< gallery src="https://play-lh.googleusercontent.com/BLCCMgKAVVZb880iBsN1-7dztMIvxrEfwzJ5fWRwx_8_4LglkeUhW91XsuHpOyR5WA=w2560-h1440" title="Zeitrechner" >}}
{{< gallery src="https://play-lh.googleusercontent.com/Qq14Cvd2ZVo0jwOdaeQYBXq9QLC04kuvgzH4MiZjDCOenBtGX2bTve_a9ltRuX0hWQQ=w2560-h1440" title="Tempo-Rechner" >}}
{{< gallery src="https://play-lh.googleusercontent.com/I0a0iCv3VMvLLK9TpGksVQeNOknJGyFZs14RMOT32l4hU6TLOfKlijU5WzKf8deLXw=w2560-h1440" title="Herzfrequenzzonen" >}}
{{< gallery src="https://play-lh.googleusercontent.com/L0XSeuoHSrN_Wc6hBoizI4Mx9QojKRFLEwAGzeKMkmu2Ro9jflzqYuoFnDEC_bwCyyc=w2560-h1440" title="Einheitenrechner" >}}
{{< gallery src="https://play-lh.googleusercontent.com/xoah8BMs4Z-KymeAH-HoezaqG-cIUWQrhMDQzex3H57MffhljxDa9LLM7d8ezU2_Xw=w2560-h1440" title="Zwischenzeiten" >}}
{{< /galleries >}}