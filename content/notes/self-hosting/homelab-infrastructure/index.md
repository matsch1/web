---
title: "Homelab Infrastruktur"
slug: "homelab-infrastructure"
date: 2026-11-03
description: "Eine Übersicht meiner Homelab Infrastruktur"
ShowToc: true
TocOpen: true
draft: true
cover:
  image: 
  alt: "homelab-infrastructure"
  caption: "Meine Homelab Infrastruktur"
  relative: true
tags:
  - proxmox
  - kubernetes
  - k3s
source_lang: de
homepage:
  teaser: "Hypervisor, Kubernetes und NAS in meinem Homelab sauber aufgesetzt."
  title: Meine Homelab Infrastruktur
translation_lock: true
---

## Einführung
Mein Homelab besteht aktuell aus zwei separaten Servern, einem angemieteten VPS und einem eigenen Heimserver.
In diesem Artikel geht es nur um meinen Heimserver.

Den Heimserver habe ich zu Beginn des Jahres umgebaut und erfüllt für mich mehrere Zwecke:
- Datenspeicher: Ich brauche ein NAS für ein besseres Backup System.
- Lernen: Ich möchte spezifische Kubernetes Themen ausprobieren.
- Degoogle: Ich möchte mit meinen Daten unabhängig von Google sein.

Hier geht es darum, wie ich den Heimserver dazu vorbereitet habe.

## Welchen Heimserver habe ich?

{{< figure src="./homeserver.webp" width="400" alt="" class="right" >}}

Mein Heimserer ist ein HPE Proliant Microsverer Gen10.
Er hat ein AMD Opteron(tm) X3421 APU mit aktuell 24 GB RAM.

Zusätzlich dazu bietet das Gehäuse Platz für 4 SATA Platten, welche bei mir in einem RAIDZ1 laufen.

## Infrastrukturübersicht
Die Infrastruktur meines Heimserver wurde als "Production-Singlenode-Cluster" umgesetzt. Für mich bedeutet das ein Kompromiss aus einem möglichst produktionsnahen Setup mit wenig Wartungsaufwand und geringen Kosten einzugehen.
Konrket bedeutet das in erster Instanz eine Virtualisierungsebene einzuführen, welche es ermöglicht mehrere VMs auf einem Server zu hosten.
Das hat den Vorteil, dass ich die Grundsysteme zumindest thematisch sauber trennen kann. Da sich alles auf einer Node befindet, ist allerdings keine technische Ausfallsicherheit gegeben.

Die folgende Übersicht zeigt die Ebenen von der Hardware bis zu den Anwendungen schematisch:

```text
HPE ProLiant MicroServer Gen10
└── Proxmox VE · Hypervisor
    ├── VM · Kubernetes mit k3s
    │   └── Single-Node-Cluster
    │       └── Pods und Container · Anwendungen
    └── VM · TrueNAS
        ├── Datenspeicher · 4 SATA-Platten im RAIDZ1
        └── NFS-Freigaben
```

Die VMs trennen Kubernetes und NAS logisch voneinander. Beide laufen jedoch auf demselben physischen Server und teilen sich damit dessen Ausfallrisiko.

## Hypervisor
- Bisschen was über proxmox (Warum proxmox?)

## Kuberenetes
- Bisschen was über platform
- Bisschenwas über k3s
- Ausug aus apps

## NAS
- Ziel: NAS, RAID, NFS
- truenas

## Fazit
- Infrastruktur so zufrieden?
- Was nochmal so machen und was anders machen?
