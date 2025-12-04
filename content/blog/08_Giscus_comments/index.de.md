---
ShowToc: true
TocOpen: true
base_hash: 07ee3e4f4132288c5e163d471935267d91c64e2ba19ef742992750c126d305e9
cover:
  alt: giscus-hugo-comments
  caption: Giscus the Git Discussion based commenting system for Hugo blogs
  image: giscus.png
  relative: true
date: 2025-12-04
description: Giscus the Git Discussion based commenting system for Hugo blogs
draft: false
slug: giscus-hugo-comments
tags:
- hugo
title: Giscus-Kommentare für Hugo-Blog einrichten
---

## Einleitung: Warum Kommentare hinzufügen?

Ich wollte den Lesern die Möglichkeit geben, auf einfache Weise Kommentare zu meinen Hugo-Blog-Beiträgen abzugeben, und suchte nach einer Lösung, die sowohl **simple for users** als auch **lightweight/easy to maintain** für mich ist.

Hugo bietet offizielle Unterstützung für die Integration verschiedener kommerzieller und Open-Source-Kommentarsysteme.

## Auswahl eines Kommentarsystems
### Kommerziell vs. Open-Source

Obwohl es mehrere kommerzielle Optionen wie **Disqus** gibt (kostenlos für nicht-kommerzielle Nutzung, aber oft mit Werbung), habe ich mich für eine **open-source**-Lösung entschieden, um die Kontrolle zu behalten und Werbung von Dritten zu vermeiden.

Hier sind einige beliebte Optionen in jeder Kategorie:

| Kommerzielle Systeme | Open-Source-Systeme |
| :--- | :--- |
| Emote | Kaktus Kommentare |
| Graph Comment | Comentario |
| Hyvor Talk | **Giscus** |
| IntenseDebate | Isso |
| ReplyBox | Remark42 |

### Wartungsfreies Open-Source: Giscus vs. Utterances

Meine ursprüngliche Anforderung war es, einen selbst gehosteten Server zu vermeiden, was mich dazu brachte, mich auf Systeme zu konzentrieren, die ein bestehendes Backend eines Drittanbieters nutzen. Die beiden wichtigsten Open-Source-Optionen, die kein Self-Hosting erfordern, sind:

* **Utterances:** Verwendet **GitHub Issues** als Backend.
* **Giscus:** Verwendet **GitHub Discussions** als Backend.

Ich habe mich für **Giscus** entschieden, weil **GitHub Discussions** von Natur aus besser für Unterhaltungen mit Threads geeignet ist und verschachtelte Antworten erlaubt, verglichen mit der flachen Liste von Kommentaren in GitHub Issues. Giscus bietet auch moderne Funktionen wie:

* Reaktionen auf den Hauptbeitrag.
* Strenger Seitenabgleich, um Verwechslungen von Kommentaren zu vermeiden.
* Aktivere Wartung.

{{< alert type="warning" title="" >}}
Dieses System basiert auf GitHub-Diskussionen, was bedeutet, dass Leser ein GitHub-Konto benötigen, um Kommentare zu schreiben.  
{{< /alert >}}

## Giscus Einrichtungsanleitung
Die Integration von Giscus in Ihren Hugo-Blog erfordert drei einfache Schritte: Vorbereitung Ihres GitHub-Repositorys, Generierung des Einbettungscodes und Erstellung eines Hugo-Shortcodes.

### 1. Vorbereitung des Repositorys

Giscus verbindet sich direkt mit dem Quellcode-Repository deines Blogs auf GitHub. Stellen Sie sicher, dass die folgenden Bedingungen erfüllt sind:

- Das Repository muss öffentlich sein
- Die [Giscus app](https://github.com/apps/giscus) muss installiert sein.
- Die Diskussionsfunktion muss aktiviert sein ([enabling Discussion feature](https://docs.github.com/en/github/administering-a-repository/managing-repository-settings/enabling-or-disabling-github-discussions-for-a-repository)).

### 2. Erzeugen Sie den Giscus Embed Code

Navigieren Sie zum offiziellen [Giscus app website](https://giscus.app/), um Ihren Einbettungscode zu konfigurieren und zu generieren. Sie müssen ein paar Parameter angeben:

* **Repository:** Der Name Ihres öffentlichen Repositorys (z.B. `username/blog-repo`).
* **Discussion Category:** Die Kategorie in Ihren GitHub-Diskussionen, in der neue Beitragskommentare erstellt werden sollen (z. B. "Blog-Kommentare").
* **Mapping Strategy:** Wie Giscus einen Blogbeitrag mit einer bestimmten Diskussion verknüpft. Die Verwendung von `pathname` ist die Standardwahl.
* **Theme:** Das visuelle Thema (hell/dunkel/angepasst) für den Kommentarbereich.

Die Website generiert automatisch ein HTML-Snippet (`<script>...</script>`), das auf den von Ihnen gewählten Einstellungen basiert. **Copy this code.**

### 3. Hugo-Integration (mit PaperMod als Beispiel)

Ich verwende das populäre [PaperMod Hugo theme](https://github.com/adityatelange/hugo-PaperMod/wiki/Features#comments), das bereits so eingerichtet ist, dass Kommentare problemlos verarbeitet werden können.

#### A. Aktivieren Sie Kommentare in `hugo.toml`
Fügen Sie den folgenden Parameter zu Ihrer Hauptkonfigurationsdatei hinzu, um Ihrem Theme mitzuteilen, dass es einen Kommentarbereich anzeigen soll:

```toml
[params]
  comments = true
```

#### B. Erstellen Sie den Giscus Shortcode

Erstellen Sie eine neue Datei unter `layouts/partials/comments.html`` und fügen Sie den generierten Giscus <script> Tag darin ein.
Das war's! Giscus kümmert sich automatisch um die Zuordnung der Diskussionen, speichert alle Daten auf GitHub und erfordert keine Servereinrichtung auf Ihrer Seite.


## Überlegung: Selbst-Hosting Optionen

Wenn ein GitHub-Konto für Sie nicht in Frage kommt, sollten Sie eine vollständig selbst gehostete Lösung bevorzugen, die Ihnen die vollständige Kontrolle über Ihre Daten und Ihre Privatsphäre gibt.

Zu den starken Optionen in dieser Kategorie gehören:

- Commento
- Isso
- Bemerkung42

Remark42 ist eine außergewöhnlich funktionsreiche und robuste Wahl. Es bietet moderne Kommentarfunktionen, unterstützt verschiedene Anmeldemethoden (nicht nur GitHub) und wird aktiv gepflegt.

Während das Selbsthosten die Zuweisung von Serverressourcen und die Wartung erfordert, bieten Systeme wie Remark42 die ultimative Unabhängigkeit und Anpassungsfähigkeit. Für diejenigen, die Wert auf eine serverlose, problemlose Einrichtung legen, ist Giscus jedoch der perfekte Ausgangspunkt.

## Fazit

Giscus ist eine ausgezeichnete, moderne und quelloffene Lösung für das Hinzufügen von Kommentaren zu einem statischen Hugo-Blog. Es umgeht die Komplexität des Selbst-Hostings, nutzt das überlegene Threading von GitHub Discussions und bietet eine nahtlose Integration.

Es ist der ideale Ausgangspunkt für jeden, der die Beteiligung der Leser ohne den Aufwand der Serververwaltung ermöglichen möchte.