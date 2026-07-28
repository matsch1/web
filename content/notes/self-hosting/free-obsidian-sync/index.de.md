---
ShowToc: true
TocOpen: true
base_hash: 0930fddd6d28777e3e2647cc7707662be1ce6e3494c29970c7eee1785b0f2343
cover:
  alt: obsidian-sync
  caption: ''
  image: img1.webp
  relative: true
date: 2025-01-02
description: Erklärung, wie ich Syncthing als kostenlose Obsidian-Synchronisierung
  nutze
draft: false
img: img1.webp
slug: free-obsidian-sync-solution
tags:
- obsidian
- syncthing
title: Kostenlose Obsidian-Synchronisierung zwischen PC und Android
---

Obsidian ist ein großartiges Tool zum Sammeln von Ideen.

Ich nutze es hauptsächlich aus folgenden Gründen:
- Recherche
- Sammeln von Informationen
- Festhalten spontaner Ideen

Je nach Situation nutze ich lieber meinen Laptop oder mein Smartphone.
Um unabhängig vom verwendeten Gerät immer Zugriff auf meine „Vaults“ zu haben, muss ich die Daten zwischen meinen Geräten synchronisieren. Zu diesem Zweck bietet Obsidian das Sync-Plugin an. Für dieses Plugin werden jedoch 4 $ pro Monat berechnet, die ich nicht ausgeben möchte, wenn es eine andere Möglichkeit gibt.

## Ich habe eine Lösung gefunden, die meinen Anforderungen entspricht:
- Plattformübergreifende Verfügbarkeit: Linux, Windows und Android
- Kein manueller Aufwand: keine Downloads, keine Kopien, gar nichts
- Kostenlos nutzbar

## Was ich derzeit nutze:
- [Syncthing-fork](https://play.google.com/store/apps/details?id=com.github.catfriend1.syncthingandroid) auf meinem Android-Smartphone
- [Syncthing](https://github.com/syncthing/syncthing) auf meinem Windows- und Linux-Rechner
- Ein Shell-Skript, um die Daten in einem Git-Repository zu sichern

## Einrichtung:
- Installiere Syncthing auf den Geräten, auf denen du Obsidian nutzen möchtest
- Erstelle auf jedem Gerät Ordner, um die Obsidian-Dateien lokal zu speichern
- Verbinde die Geräte über den QR-Code
- Teile die Ordner (ebenfalls über den QR-Code)
- Kopiere deinen „Vault“ in das neue Verzeichnis und öffne ihn in Obsidian
- *optional:*
  - Erstellen Sie ein Git-Repository in Ihrem Obsidian-Verzeichnis und sichern Sie die Dateien auf Ihrem GitHub-Konto


## Obsidian Git-Autosicherung

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

## Über die reine Gerätesynchronisierung hinaus

Das ist der einfache, kostenlose Einstieg zum Synchronisieren eines Obsidian-Vaults. Später habe ich das Setup um einen serverzentrierten Syncthing-Hub, Backups und weitere selbst gehostete Dienste erweitert: [Mein Obsidian- und Syncthing-Setup](https://blog.matschcode.de/de/notes/self-hosting/obsidian-cloud-sync-setup/).