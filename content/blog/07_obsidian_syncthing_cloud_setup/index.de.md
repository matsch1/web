---
ShowToc: true
TocOpen: true
base_hash: 4252314707314461c48d7b7f94726a78110eb90d7f17fd1dad28c8b874683615
cover:
  alt: obsidian-syncthing
  caption: ''
  image: img1.png
  relative: true
date: 2025-09-22
description: Verwende Syncthing auf einem Server, um einen plattformübergreifenden
  Dateiaustausch für Obsidian-Notizen und mehr einzurichten.
draft: false
slug: obsidian-cloud-sync-setup
tags:
- obsdian
- syncthing
title: 'Mein Obsidian- und Syncthing-Setup: Eine selbst gehostete Cloud für Notizen,
  Backups und mehr'
---

Es gibt zwei Arten von Notizern: diejenigen, die ihre wertvollen Gedanken der Cloud anvertrauen (Hallo, Notion-/Google Drive-/OneNote-Nutzer), und diejenigen, die in den Abgrund starren und sich fragen: *„Was wäre, wenn ich dafür meine eigene Infrastruktur aufbauen würde?“*  

Ich gehöre zur zweiten Gruppe.  
Hier erfährst du, wie ich aus **Syncthing + Obsidian + einem Webserver** ein Monster geschaffen habe, das Notizen synchronisiert, fleißig Backups erstellt und die Cloud ersetzt.  

---

## Die Kernidee  

- **Server:** Ein VPS, der als mein „Syncthing-Master“ fungiert  
- **Clients:** Linux-, Windows- und Android-Geräte, die alle problemlos mit dem Server synchronisieren.  
- **Speicherort:** Obsidian-Notizen befinden sich in einem einzigen Ordner. Dieser Ordner ist die zentrale Quelle.  

Die Magie steckt in Syncthing: Jedes Gerät kommuniziert mit dem Server und synchronisiert Notizen **bidirektional**. Das bedeutet, dass ich Notizen überall bearbeiten kann (auf meinem Smartphone während der Fahrt zur Arbeit, an meinem Desktop-PC beim Programmieren oder auf meinem Laptop, während ich so tue, als würde ich mich auf der Couch entspannen). Innerhalb von Sekunden werden die Änderungen auf allen Geräten übernommen.  

Der Server ist sowohl **Synchronisierungszentrale** als auch **Backup-Speicher**. Selbst wenn also ein Laptop den Geist aufgibt oder mein Handy beschließt, ein Bad zu nehmen, bleiben die Notizen sicher.  

---

## Warum Syncthing?  

Weil es im Grunde die **Anti-Cloud-Cloud** ist.  

- Keine Konten, keine Abonnements, keine Anbieterabhängigkeit.  
- Läuft auf allem (Linux, Windows, macOS, Android, sogar auf Routern, falls man darauf steht).  
- Peer-to-Peer-Magie: Geräte kommunizieren direkt miteinander, wenn möglich, und greifen andernfalls auf einen Relay-Server zurück.  
- Einmal eingerichtet, „funktioniert es einfach“.  
- Einfach einzurichten mit **Coolify**

Es ist wie Dropbox, nur nerdiger und ohne die unheimlichen Nutzungsbedingungen.  

---

## Obsidian-Ebene  

Obsidian behandelt seine **Vault-Einstellungen** (Themes, Plugins, Arbeitsbereichskonfiguration) einfach als weitere Dateien. Das bedeutet: Sobald du deinen Vault-Ordner in Syncthing einbindest, **wird auch die gesamte Konfiguration synchronisiert**.  

Genau: Ich kann ein Plugin auf meinem Linux-Rechner installieren, und Sekunden später ist es wie von Zauberhand auch unter Windows und Android verfügbar. Meine Tastenkombinationen, mein Farbschema, meine verrückten Plugin-Kombinationen – sie alle folgen mir überallhin.  

---

## Zusätzliche Funktionen  

Jetzt wird es erst richtig spannend. Ich habe mich nicht mit „nur dem Synchronisieren von Notizen“ begnügt.  

### GitHub-Backup  

Ich führe einen Cron-Job aus, der den gesamten „Vault“ in ein privates GitHub-Repo hochlädt.  

Warum? Weil:  
1. **Zusätzliches Sicherheitsnetz** (man kann nie genug Backups haben).  
2. **Versionskontrolle**: Im Grunde ist es die Git-Historie meines Gehirns.  

### Automatisierte Dateiverwaltung  

Manchmal wird es in den Notizen unordentlich. Anhänge stapeln sich, Screenshots landen an beliebigen Stellen.  

Lösung: ein kleines Python-Skript (das ebenfalls über Cron läuft), das aufräumt und die Dinge neu ordnet.  
Stellt es euch wie einen Roomba für meinen „Vault“ vor.  

---

## Über Notizen hinaus: Syncthing als persönliche Cloud  

Hier kommt der Clou: Sobald Syncthing auf einem VPS läuft, hast du im Grunde dein eigenes **Cloud-Framework** aufgebaut. Notizen sind nur der Anfang.  

- **Ersatz für Google Drive**: Füge einfach jeden Ordner hinzu, den du geräteübergreifend synchronisieren möchtest. Fertig.  
- **DCIM-Backup für das Smartphone**: Mein Android-Gerät speichert neue Fotos direkt auf dem Server, selbst wenn ich im Ausland bin. Sie sind sofort sicher, ohne dass ich jemals „Google Fotos“ anfassen muss. 
  Achte auf den Speicherplatz deines Servers. Bilder benötigen viel mehr Platz als Notizen.

Ich stelle mir das gerne so vor: **Syncthing ist mein Cloud-Betriebssystem, der VPS ist das Rechenzentrum und meine Geräte sind lediglich Clients.**  

---

## TL;DR-Einrichtung  

- VPS mit installiertem Syncthing → fungiert als Master und Backup-Hub.  
- Clients: Linux, Windows, Android mit Syncthing.  
- „Vault“-Ordner = wird überall synchronisiert.  
- Obsidian-Konfiguration = wird ebenfalls synchronisiert.  
- Das gewisse Extra: GitHub-Backup, Python-Skripte, Cron-Jobs.  
- Bonus: Syncthing dient gleichzeitig als Ersatz für Google Drive und als Foto-Backup.  

---

## Abschließende Gedanken  

Die meisten Leute zahlen für Cloud-Speicher. Ich ziehe es vor, für einen VPS zu zahlen und meine eigene Lösung zu basteln.  
Mit Syncthing + Obsidian erhalte ich **Echtzeit-Synchronisierung, vollständige Kontrolle, keine Anbieterabhängigkeit** und ein paar Extrapunkte bei den Nerds.  

Wenn du dich für Selbsthosting und Dateneigentum interessierst oder einfach gerne an der Infrastruktur bastelst, kann ich dir diese Kombination nur wärmstens empfehlen. Es geht nicht nur um Notizen – es ist ein selbst gehostetes Cloud-Ökosystem.