---
ShowToc: true
TocOpen: true
base_hash: dc726962890305bc4a7d330e6784baa9041d76f65dce92171d29d21a48882343
cover:
  alt: split-keyboard-ianmaclarty
  caption: ''
  image: header.png
  relative: true
date: 2025-08-04
description: Modeling, soldering, 3D printing, assembling, flashing
draft: false
slug: split-keyboard-ianmaclarty
tags:
- 3D printing
- keyboard
title: Meine erste geteilte Tastatur - Ian's Keyboard
---

{{< alert type="info" title="" >}}
Die Tastatur funktioniert hervorragend und ist immer noch im täglichen Einsatz.
Die QMK-Software wächst mit der Zeit.
{{< /alert >}}

## Einleitung

{{< figure src="./split-keyboard-guy.png" width="700" alt="Guy typing on split keyboard" class="right" >}}

Wer möchte nicht mühelos cool aussehen, wenn er auf einer Tastatur tippt, die sonst niemand versteht? Ich weiß, dass ich es will.  

Neben dem reinen Style-Faktor habe ich einige echte Vorteile einer geteilten Tastatur entdeckt. Für mich sind das die wichtigsten Vorteile:

- **Reduced hand motion:** Das Bewegen meiner Hand, um die Pfeiltasten oder Zahlen zu erreichen, hat mich schon immer genervt. Und von der Gymnastik mit Daumen und kleinem Finger, die erforderlich ist, um Alt, Esc oder Strg zu drücken, will ich gar nicht erst anfangen. Mit einer geteilten Tastatur werden diese Bewegungen auf ein Minimum reduziert.  

- **Better ergonomics:** Bei einem geteilten Layout geht es nicht nur um den Komfort der Finger. Es ermöglicht mir, die Tastaturhälften natürlicher zu positionieren, was meine allgemeine Haltung am Schreibtisch verbessert und verhindert, dass ich wie eine Krabbe sitze.  

- **Increased typing speed:** Weniger Handbewegungen bedeuten weniger Zeitverschwendung, was natürlich zu schnellerem Tippen führt, sobald man sich an das Layout gewöhnt hat.  

Der Wechsel zu einer geteilten Tastatur ist nicht nur eine stilistische Entscheidung, sondern auch eine Verbesserung für Ihre Hände, Ihre Haltung und Ihre Produktivität.

## Ian's Keyboard

Für meinen ersten Bau stieß ich auf das GitHub-Projekt von Ian Maclarty, die [IK Keyboard](https://github.com/ianmaclarty/ik).
Das Konzept ist einfach: Bauen Sie Ihre eigene geteilte Tastatur mit Teilen, die Sie leicht von AliExpress beziehen können.  

Die einzigen schwierigen Teile sind die Leiterplatten und die 3D-gedruckten Gehäuse.  
Glücklicherweise hatte ein Kollege zwei Ersatzplatinen für mich, und ich kann die Gehäuse selbst mit meinem 3D-Drucker drucken.

Für alles andere können Sie einfach der Anleitung im [README](https://github.com/ianmaclarty/ik/blob/main/README.md) des Projekts folgen.

## PCB Redesign

Im ursprünglichen Entwurf gibt es zwei separate Gerber-Dateien - eine für die linke und eine für die rechte Leiterplatte.

Die Leiterplatten, die ich erhalten habe, wurden leicht modifiziert, so dass die gleiche Leiterplatte für beide Seiten verwendet werden kann.  
Dies ist eine erhebliche Verbesserung, da die Leiterplattenhersteller in der Regel eine Mindestmenge von fünf Stück pro Gerberdatei verlangen.  
Mit dem neuen Design müssen Sie nur noch einen Typ bestellen, was die Kosten niedrig hält.  
Bei Anbietern wie [pcbway.com](https://www.pcbway.com/) können Sie beispielsweise fünf identische Leiterplatten für etwa 30 € bestellen.
Leider habe ich die modifizierten Versionen der Gerberdateien nicht.

## 3D-Modellierung und Druck des Rahmens

Die ursprünglichen STL-Dateien sind auf Kompaktheit optimiert, was den Zusammenbau und insbesondere die Fehlersuche erschweren kann.  
Um den Arbeitsablauf zu verbessern, habe ich die Gehäuse so umgestaltet, dass alles nach dem Löten montiert werden kann.

Sie können meine modifizierten STL-Dateien in meinem GitHub-Repository [Ian Maclarty Mods](https://github.com/matsch1/ianmaclarty_ik1.2_keyboard/tree/main/STLs) finden.

## Zusammenbau

Der Zusammenbauprozess besteht aus zwei Hauptaufgaben:

- Löten aller Komponenten auf der Platine
- Montage des Gehäuses und der Tastenkappen

### Löten

Um die beiden Hälften zu verbinden, habe ich PJ328-Kopfhörerbuchsen verwendet, weil ich noch einige zur Hand hatte.  
Das Gehäuse unterscheidet sich leicht, um diese unterzubringen, aber solange man sauber lötet, funktioniert es gut.

Für die MCUs empfehle ich, nahe gelegene Bauteile mit Nagellack abzudecken, um Kurzschlüsse beim Löten zu vermeiden.

Für alles andere sollten Sie sich auf die Anweisungen im Original
[README](https://github.com/ianmaclarty/ik/blob/main/README.md).

{{< alert type="warning" title="" >}}
Wenn Sie die Originalgehäuse verwenden, müssen Sie das Frontgehäuse **before** anbringen und die Schalter anlöten.
{{< /alert >}}

{{< galleries >}}
{{< gallery src="./pcb_soldering_top.jpg" title="PCB Top" >}}
{{< gallery src="./pcb_soldering_bottom.jpg" title="PCB Bottom" >}}
{{< /galleries >}}

### Alles zusammenfügen

Sobald das Löten abgeschlossen ist, ist der Rest einfach und angenehm.  
Befolgen Sie einfach die Montageschritte aus dem Original von [README](https://github.com/ianmaclarty/ik/blob/main/README.md).
{{< figure src="./keyboard_assembled.jpg" width="700" alt="Assembled Keyboard" >}}

## Software

Die Firmware für diese Tastatur basiert auf der [QMK firmware](https://qmk.fm/).
Glücklicherweise bietet Ian alles, was Sie brauchen, um loszulegen.

### Änderungen

Das Tastaturlayout ist eine sehr persönliche Angelegenheit.  
Ich habe meine so konfiguriert, dass sie nahtlos mit dem `US International – Alt Gr dead keys`-Layout auf meinem PC funktioniert.

Unter Windows müssen Sie dieses Layout manuell installieren. Eine zuverlässige Implementierung wird von [thomasfaingnaert](https://github.com/thomasfaingnaert/win-us-intl-altgr) bereitgestellt.
Dieses Layout behält QWERTY bei und unterstützt zusätzlich die deutschen Zeichen ä, ö, ü und ß.

### Blinken

Um die Firmware zu flashen, folgen Sie einfach den Anweisungen in Ian's [README](https://github.com/ianmaclarty/ik/blob/main/README.md).

Meine persönlichen Tastaturbelegungen sind hier verfügbar: [keymaps matsch](https://github.com/matsch1/ianmaclarty_ik1.2_keyboard/tree/main/keymaps/ik1_2)