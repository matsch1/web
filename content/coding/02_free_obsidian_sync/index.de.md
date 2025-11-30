---
slug: "free-obsidian-sync-solution"
ShowToc: true
TocOpen: true
base_hash: ae103845a1a6ccdd19702b010d1fb9234d4e96905e2a4c416bed88c017935e28
cover:
  alt: obsidian-sync
  caption: ''
  image: img1.webp
  relative: true
date: 2025-01-02
description: Explanation of how I use Syncthing as a free Obsidian Sync
draft: false
img: img1.webp
params:
  ShowPostNavLinks: true
title: Kostenlose Obsidian PC Android-Synchronisation
---

Obsidian ist ein großartiges Werkzeug zum Sammeln von Ideen.

Ich benutze es hauptsächlich aus den folgenden Gründen:
- Recherche
- Sammeln von Informationen
- Abspeichern spontaner Ideen

Je nach Situation verwende ich lieber meinen Laptop oder mein Handy.
Um immer Zugriff auf meine Daten zu haben, egal welches Gerät ich gerade benutze, muss ich die Daten zwischen meinen Geräten synchronisieren. Zu diesem Zweck bietet Obsidian das Sync Plugin an. Aber für dieses Plugin werden 4$ pro Monat berechnet, die ich nicht ausgeben möchte, wenn es eine andere Möglichkeit gibt.

## Ich habe eine Lösung gefunden, die meine Anforderungen erfüllt:
- Plattformübergreifende Verfügbarkeit: Linux, Windows und Android
- Keine manuelle Arbeit: keine Downloads, keine Kopien, kein gar nichts
- kostenlos zu verwenden

## Was ich jetzt benutze:
- [Syncthing-fork](https://play.google.com/store/apps/details?id=com.github.catfriend1.syncthingandroid) auf meinem Androiden-Handy
- [Syncthing](https://github.com/syncthing/syncthing) auf meinem Windows- und Linux-Rechner
- Shell-Skript zum Sichern der Daten in einem Git-Repository

## Einrichten:
- Installieren Sie Syncthing auf den Geräten, auf denen Sie Obsidian verwenden wollen
- Erstellen von Ordnern auf jedem Gerät, um die Obsidian-Dateien lokal zu speichern
- Verknüpfen der Geräte mit dem QR-Code
- Teilen Sie die Ordner (auch mit QR-Code)
- Kopieren Sie Ihren Tresor in das neue Verzeichnis und öffnen Sie ihn in Obsidian
- *optional:*
  - Erstellen Sie ein Git-Repository in Ihrem Obsidian-Verzeichnis und sichern Sie die Dateien in Ihrem Github-Konto


## Obsidian Git autobackup

``` bash
#!/bin/bash

git-autopush() {
  REPO_DIR = $1
  cd "$REPO_DIR" || {
    echo "Repository not found: $REPO_DIR"
    exit 1
  }

  # Check if the repository has changes
  if [[ -n $(git status --porcelain) ]]; then
    git add .
    git status

    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    git commit -m "Auto-commit: $TIMESTAMP"

    git push origin "$(git rev-parse --abbrev-ref HEAD)" || {
      echo "Failed to push changes."
      exit 1
    }

    echo "Changes pushed successfully."
  else
    # Check if there are committed changes to push
    LOCAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    if [[ -n $(git rev-list origin/"$LOCAL_BRANCH"..HEAD) ]]; then

      # Push changes
      git push origin "$LOCAL_BRANCH" || {
        echo "Failed to push changes."
        exit 1
      }
      echo "Changes pushed successfully."
    fi

  fi
}

git-autopush $1
```
