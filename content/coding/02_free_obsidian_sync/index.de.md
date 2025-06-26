---
ShowToc: true
TocOpen: true
base_hash: 35974ea88c45f4863f863cee2e7ca263ca5498eb9d68728d1b279c08b14db7cd
date: 2025-01-02
description: Explanation of how I use Syncthing as a free Obsidian Sync
draft: false
img: img1.webp
title: Kostenlose Obsidian PC Android Sync
---

![header-image](img1.webp)
Obsidian ist ein großartiges Werkzeug zum Sammeln von Ideen.

Ich benutze es hauptsächlich aus den folgenden Gründen:
- Forschung
- Informationen sammeln
- Spontane Ideen retten

Abhängig von meiner tatsächlichen Situation bevorzuge ich es, meinen Laptop oder mein Telefon zu verwenden.
Um immer Zugriff auf meine Gewölbe zu haben, unabhängig von dem Gerät, das ich verwende, muss ich die Daten zwischen meinen Geräten synchronisieren.Zu diesem Zweck stellt Obsidian das Sync -Plugin zur Verfügung.Aber für dieses Plugin berechnen sie Ihnen 4 $ pro Monat, was ich nicht ausgeben möchte, wenn es eine andere Option gibt.

## Ich habe eine Lösung gefunden, die meine Anforderungen entspricht:
- Verfügbarkeit von CrossPlatform: Linux, Windows und Android
- Keine manuellen Arbeit: Keine Downloads, keine Kopien, kein nichts
- frei zu bedienen

## Was ich jetzt benutze:
- [Syncthing-fork](https://play.google.com/store/apps/details?id=com.github.catfriend1.syncthingandroid) auf meinem Android -Telefon
- [Syncthing](https://github.com/syncthing/syncthing) auf meinem Windows and Linux -Computer
- Shell -Skript, um die Daten in einem Git -Repository zu sichern

## Aufstellen:
- Synchronisierung auf den Geräten, die Sie für Obsidian verwenden möchten
- Erstellen Sie Ordner auf jedem Gerät, um die Obsidian -Dateien lokal zu speichern
- Verknüpfung der Geräte mit dem QR -Code
- Teilen Sie die Ordner (auch mit QR -Code) teilen)
- Kopieren Sie Ihr Gewölbe in das neue Verzeichnis und öffnen Sie es in Obsidian
- *Optional: *
- Erstellen Sie ein Git -Repository in Ihrem Obsidian -Verzeichnis und sichern Sie die Dateien in Ihrem GitHub -Konto


## Obsidian Git Autobackup

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