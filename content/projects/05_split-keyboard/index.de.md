---
ShowToc: true
TocOpen: true
base_hash: 372824345bbb078514e354b8931de8cd12b6a3b6e2a2dd9694bc6cb03da7d6de
cover:
  alt: split-keyboard-ianmaclarty
  caption: ''
  image: header.png
  relative: true
date: 2025-08-04
description: Modellbau, Löten, 3D-Druck, Zusammenbau, Flashen
draft: false
slug: split-keyboard-ianmaclarty
tags:
- 3D printing
- keyboard
title: Mein erster Selbstbau einer geteilten Tastatur – Ians Tastatur
---

{{< alert type="info" title="" >}}
Die Tastatur funktioniert hervorragend und ist nach wie vor im täglichen Einsatz.
Die QMK-Software entwickelt sich mit der Zeit weiter.
{{< /alert >}}

## Einleitung

{{< figure src="./split-keyboard-guy.png" width="700" alt="Guy typing on split keyboard" class="right" >}}

Wer möchte nicht mühelos cool wirken, während er auf einer Tastatur tippt, die sonst niemand versteht? Ich auf jeden Fall.  

Abgesehen vom reinen Stilfaktor habe ich einige echte Vorteile der Verwendung einer geteilten Tastatur entdeckt. Für mich sind die wichtigsten Vorteile:

- **Weniger Handbewegungen:** Es hat mich immer genervt, meine Hand bewegen zu müssen, um die Pfeiltasten oder Ziffern zu erreichen. Und von den Akrobatikübungen mit Daumen und kleinem Finger, die nötig sind, um Alt, Esc oder Strg zu drücken, will ich gar nicht erst anfangen. Mit einer geteilten Tastatur werden diese Bewegungen auf ein Minimum reduziert.  

- **Bessere Ergonomie:** Bei einem geteilten Layout geht es nicht nur um den Komfort für die Finger. Es ermöglicht mir, die beiden Tastaturhälften natürlicher zu positionieren, was meine gesamte Sitzhaltung am Schreibtisch verbessert und verhindert, dass ich wie eine Garnele dasitze.  

- **Höhere Tippgeschwindigkeit:** Weniger Handbewegungen bedeuten weniger Zeitverlust, was natürlich zu schnellerem Tippen führt, sobald man sich an das Layout gewöhnt hat.  

Der Umstieg auf eine geteilte Tastatur ist nicht nur eine Stilfrage – es ist eine Verbesserung für deine Hände, deine Körperhaltung und deine Produktivität.

## Ians Tastatur

Für meinen ersten Selbstbau bin ich auf Ian Maclartys GitHub-Projekt gestoßen, das [IK Keyboard](https://github.com/ianmaclarty/ik).  
Das Konzept ist einfach: Baue dir deine eigene geteilte Tastatur aus Teilen, die du problemlos bei AliExpress besorgen kannst.  

Die einzigen anspruchsvollen Teile sind die Leiterplatten und die 3D-gedruckten Gehäuse.  
Glücklicherweise hatte ein Kollege zwei übrig gebliebene Leiterplatten für mich, und die Gehäuse kann ich mit meinem 3D-Drucker selbst drucken.

Für alles andere kannst du einfach der Anleitung im [README](https://github.com/ianmaclarty/ik/blob/main/README.md) des Projekts folgen.

## Neugestaltung der Leiterplatte

Im ursprünglichen Entwurf gibt es zwei separate Gerber-Dateien – eine für die linke Leiterplatte und eine für die rechte.

Die Leiterplatten, die ich erhalten habe, wurden leicht modifiziert, sodass dieselbe Leiterplatte für beide Seiten verwendet werden kann.  
Dies ist eine erhebliche Verbesserung, da Leiterplattenhersteller in der Regel eine Mindestbestellmenge von fünf Stück pro Gerber-Datei verlangen.  
Durch die Neugestaltung muss nur noch ein Typ bestellt werden, was die Kosten senkt.  
Beispielsweise lassen sich fünf identische Leiterplatten bei Anbietern wie [pcbway.com](https://www.pcbway.com/) für etwa 30 € herstellen.
Leider verfüge ich nicht über die modifizierten Versionen der Gerber-Dateien.

## 3D-Modellierung und Druck des Rahmens

Die ursprünglichen STL-Dateien sind auf Kompaktheit optimiert, was die Montage und insbesondere die Fehlersuche erschweren kann.  
Um den Arbeitsablauf zu verbessern, habe ich die Gehäuse neu gestaltet, sodass alles nach dem Löten zusammengebaut werden kann.

Meine modifizierten STL-Dateien findest du in meinem GitHub-Repository [Ian Maclarty Mods](https://github.com/matsch1/ianmaclarty_ik1.2_keyboard/tree/main/STLs)

## Zusammenbau

Der Zusammenbau besteht aus zwei Kernaufgaben:

- Das Auflöten aller Bauteile auf die Leiterplatte  
- Die Montage des Gehäuses und der Tastenkappen

### Löten

Um die beiden Hälften miteinander zu verbinden, habe ich PJ328-Kopfhörerbuchsen verwendet, da ich noch einige davon vorrätig hatte.  
Das Gehäuse weicht geringfügig ab, um diese aufzunehmen, aber solange man sauber lötet, funktioniert es gut.

Für die Mikrocontroller empfehle ich, benachbarte Bauteile mit Nagellack abzudecken, um Kurzschlüsse beim Löten zu vermeiden.

Für alles andere halte dich an die Anleitung im Original  
[README](https://github.com/ianmaclarty/ik/blob/main/README.md).

{{< alert type="warning" title="" >}}
Wenn du die Originalgehäuse verwendest, musst du das vordere Gehäuse **vor** dem Löten der Schalter anbringen.
{{< /alert >}}

{{< galleries >}}
{{< gallery src="./pcb_soldering_top.jpg" title="PCB Top" >}}
{{< gallery src="./pcb_soldering_bottom.jpg" title="PCB Bottom" >}}
{{< /galleries >}}

### Alles zusammenbauen

Sobald das Löten abgeschlossen ist, ist der Rest unkompliziert und macht Spaß.  
Befolgen Sie einfach die Montageschritte aus dem Original [README](https://github.com/ianmaclarty/ik/blob/main/README.md).
{{< figure src="./keyboard_assembled.jpg" width="700" alt="Assembled Keyboard" >}}

## Software

Die Firmware für diese Tastatur basiert auf der [QMK firmware](https://qmk.fm/).  
Glücklicherweise stellt Ian alles zur Verfügung, was man für den Einstieg benötigt.

### Anpassungen

Die Vorlieben für Tastaturlayouts sind sehr individuell.  
Ich habe meine Tastatur so konfiguriert, dass sie nahtlos mit dem `US International – Alt Gr dead keys`-Layout auf meinem PC zusammenarbeitet.

Unter Windows musst du dieses Layout manuell installieren. Eine zuverlässige Implementierung bietet [thomasfaingnaert](https://github.com/thomasfaingnaert/win-us-intl-altgr).
Dieses Layout behält die QWERTY-Anordnung bei und bietet zusätzlich Unterstützung für deutsche Zeichen: ä, ö, ü und ß.

### Flashen

Um die Firmware zu flashen, befolge einfach die Anweisungen in Ians [README](https://github.com/ianmaclarty/ik/blob/main/README.md).

Meine persönlichen Tastenbelegungen sind hier verfügbar: [keymaps matsch](https://github.com/matsch1/ianmaclarty_ik1.2_keyboard/tree/main/keymaps/ik1_2)