---
ShowToc: true
TocOpen: true
base_hash: 017d85a989e316c54baa577c1e3d02ff1055b057f4a13abefad17cf48ac1650c
cover:
  alt: giscus-hugo-comments
  caption: Giscus the Git Discussion based commenting system for Hugo blogs
  image: giscus.png
  relative: true
date: 2025-12-04
description: Giscus – das auf Git-Diskussionen basierende Kommentarsystem für Hugo-Blogs
draft: false
slug: giscus-hugo-comments
tags:
- hugo
title: Einrichtung von Giscus-Kommentaren für einen Hugo-Blog
---

## Einleitung: Warum Kommentare hinzufügen?

Ich wollte meinen Lesern die Möglichkeit geben, meine Hugo-Blogbeiträge einfach zu kommentieren, und suchte nach einer Lösung, die sowohl **für die Nutzer einfach** als auch **schlank und leicht zu warten** für mich ist.

Hugo bietet offizielle Unterstützung für die Integration verschiedener kommerzieller und Open-Source-Kommentarsysteme.

## Auswahl eines Kommentarsystems
### Kommerziell vs. Open-Source

Zwar gibt es mehrere kommerzielle Optionen wie **Disqus** (kostenlos für nicht-kommerzielle Nutzung, enthält jedoch oft Werbung), doch habe ich mich für eine **Open-Source**-Lösung entschieden, um die Kontrolle zu behalten und Werbung von Drittanbietern zu vermeiden.

Hier sind einige beliebte Optionen aus den jeweiligen Kategorien:

| Kommerzielle Systeme | Open-Source-Systeme |
| :--- | :--- |
| Emote | Cactus Comments |
| Graph Comment | Comentario |
| Hyvor Talk | **Giscus** |
| IntenseDebate | Isso |
| ReplyBox | Remark42 |

### Wartungsfreies Open-Source: Giscus vs. Utterances

Meine ursprüngliche Anforderung war es, das Selbsthosten eines Servers zu vermeiden, weshalb ich mich auf Systeme konzentrierte, die ein bestehendes Backend eines Drittanbieters nutzen. Die beiden wichtigsten Open-Source-Optionen, die kein eigenes Hosting erfordern, sind:

* **Utterances:** Nutzt **GitHub Issues** als Backend.
* **Giscus:** Nutzt **GitHub Discussions** als Backend.

Ich habe mich für **Giscus** entschieden, da **GitHub Discussions** von Natur aus besser für Thread-basierte Unterhaltungen geeignet ist und verschachtelte Antworten ermöglicht – im Gegensatz zur flachen Liste von Kommentaren in GitHub Issues. Giscus bietet außerdem moderne Funktionen wie:

* Reaktionen auf den Hauptbeitrag.
* Strikte Seitenzuordnung, um Verwechslungen bei Kommentaren zu verhindern.
* Aktivere Pflege.

{{< alert type="warning" title="" >}}
Dieses System basiert auf GitHub Discussions, was bedeutet, dass Leser ein GitHub-Konto benötigen, um Kommentare zu schreiben.  
{{< /alert >}}

## Anleitung zur Einrichtung von Giscus
Die Integration von Giscus in Ihren Hugo-Blog erfolgt in drei einfachen Schritten: Vorbereitung Ihres GitHub-Repositorys, Generierung des Einbettungscodes und Erstellung eines Hugo-Shortcodes.

### 1. Vorbereitung des Repositorys

Giscus stellt eine direkte Verbindung zum Quellcode-Repository Ihres Blogs auf GitHub her. Stellen Sie sicher, dass die folgenden Bedingungen erfüllt sind:

- Das Repository muss öffentlich sein.
- Das [Giscus app](https://github.com/apps/giscus) muss installiert sein.
- Die Diskussionsfunktion muss aktiviert sein ([enabling Discussion feature](https://docs.github.com/en/github/administering-a-repository/managing-repository-settings/enabling-or-disabling-github-discussions-for-a-repository)).

### 2. Giscus-Einbettungscode generieren

Rufen Sie die offizielle [Giscus app website](https://giscus.app/) auf, um Ihren Einbettungscode zu konfigurieren und zu generieren. Sie müssen dabei einige Parameter angeben:

* **Repository:** Der Name Ihres öffentlichen Repositorys (z. B. `username/blog-repo`).
* **Diskussionskategorie:** Die Kategorie in Ihren GitHub-Diskussionen, in der neue Beitrags-Kommentare erstellt werden (z. B. „Blog-Kommentare“).
* **Zuordnungsstrategie:** Wie Giscus einen Blogbeitrag mit einer bestimmten Diskussion verknüpft. Die Verwendung von `pathname` ist die Standardoption.
* **Design:** Das visuelle Design (hell/dunkel/benutzerdefiniert) für den Kommentarbereich.

Die Website generiert automatisch einen HTML-Schnipsel (`<script>...</script>`) basierend auf Ihren Auswahlmöglichkeiten. **Kopieren Sie diesen Code.**

### 3. Hugo-Integration (am Beispiel von PaperMod)

Ich verwende das beliebte [PaperMod Hugo theme](https://github.com/adityatelange/hugo-PaperMod/wiki/Features#comments), das bereits so eingerichtet ist, dass Kommentare problemlos verwaltet werden können.

#### A. Kommentare in `hugo.toml` aktivieren
Füge den folgenden Parameter zu deiner Hauptkonfigurationsdatei hinzu, um deinem Theme mitzuteilen, dass es einen Kommentarbereich rendern soll:

```toml
[params]
  comments = true
```

#### B. Den Giscus-Shortcode erstellen

Erstellen Sie eine neue Datei unter `layouts/partials/comments.html` und fügen Sie den generierten Giscus-Tag `<script>` darin ein.
Das war’s schon! Giscus übernimmt automatisch die Zuordnung der Diskussionen, speichert alle Daten auf GitHub und erfordert keinerlei Server-Einrichtung Ihrerseits.


## Überlegung: Optionen für Selbsthosting

Wenn die Notwendigkeit eines GitHub-Kontos für Sie ein Ausschlusskriterium ist, ziehen Sie vielleicht eine vollständig selbst gehostete Lösung vor, die Ihnen die vollständige Kontrolle über Daten und Datenschutz gewährt.

Zu den empfehlenswerten Optionen in dieser Kategorie gehören:

- Commento
- Isso
- Remark42

Von diesen sticht Remark42 als besonders funktionsreiche und robuste Wahl hervor. Es bietet moderne Kommentarfunktionen, unterstützt verschiedene Anmeldemethoden (nicht nur GitHub) und wird aktiv gepflegt.

Zwar erfordert das Selbsthosting die Bereitstellung von Serverressourcen und die Übernahme der Wartung, doch bieten Systeme wie Remark42 ein Höchstmaß an Unabhängigkeit und Anpassungsmöglichkeiten. Für diejenigen, die Wert auf eine serverlose, unkomplizierte Einrichtung legen, bleibt Giscus jedoch der perfekte Ausgangspunkt.

## Fazit

Giscus ist eine hervorragende, moderne und quelloffene Lösung, um Kommentare zu einem statischen Hugo-Blog hinzuzufügen. Es umgeht die Komplexität des Selbsthostings, nutzt die überlegene Thread-Struktur von GitHub Discussions und bietet eine nahtlose Integration.

Es ist der ideale Ausgangspunkt für alle, die die Interaktion mit ihren Lesern fördern möchten, ohne sich um die Serververwaltung kümmern zu müssen.