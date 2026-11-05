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
Konrket bedeutet das in erster Instanz eine Virtualisierungsebene einzuführen, welche es ermöglicht mehrere VMs auf einem Server zu hosten. Darauf aufbauend kommt dann die Platform Ebene, welche die Grundlage der Services darstellt.

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

Die VMs trennen Kubernetes und NAS logisch voneinander.

## Hypervisor
Der Hypervisor ist die Virtualisierungsschicht im Cluster. Sie ist dazu da die Grundsysteme logisch sauber voneinander zu trennne. Da sich alles auf einer Node befindet, ist allerdings keine technische Ausfallsicherheit gegeben. Im Rahmen eines Homelabs nehme ich das vorerst in Kauf.

Beim Hypervisor meiner Wahl handelt es sich um Proxmox, welcher auf Debian basiert und direkt auf dem Host installiert ist.

Mittels Ansible und Terraform beschreibe ich die Infrastruktur und dessen Setup in Konfigurationsdateien, was es mir erlaubt nach Infrastructure-As-Code Prinzipien die Cluster Infrastruktur zu managen.


## Kubernetes
Um meine Services zu deployen habe ich mich für ein K3s cluster entschieden, welches im Single-Node-Betrieb auf einer VM läuft.
Das erlaubt mir mein Setup flexibel zu konfigurieren und dabei verschiedene Kubernetes Themen zu lernen und auszuprobieren.

Die Services selbst sind dann mit ArgoCD in eim GitOps pattern deployed. So habe ich immer den Überblick über den aktuellen Stand meiner Apps und gleichzeitig die Möglichkeit alles per Helm Chart zu konfigurieren und maintainen.

## NAS
Die zweite VM ist eine reine NAS VM. Mit TrueNAS als Betriebssystem verwalte ich meine HDDs in einem storage pool als RAIDZ1. Dadurch erhalte ich eine Parität von 1, was meine Datensicherheit sogar beim Ausfall einer HDD garantiert.

Das NAS beinhaltet allerdings nicht nur meine Dateibackups. Per NFS share teile ich den Speicherplatz direkt mit der Kubernetes-VM, was es mir ermöglicht die Daten meiner Kubernetes Apps direkt im RAID zu sichern. Das sorgt für eine zusätzliche Trennung der User-Daten von den Service-Daten.

## Fazit
Für einen privaten Heimserver bietet mein System eine ordentliche Grundlage. 

### Was mir sehr gut gefällt:
Es ermöglicht mir mehrere Services selbst zu hosten und viele Sachen auszuprobieren. Dabei behalte ich auch immer die Hoheit über meine Daten und bin nicht angewiesen auf Techkonzerne. Die relativ moderaten Ressourcen sorgen für einen geringen Energieverbrauch und dabei trotzdem ausreichend Kapazität für alles was ich Zuhause brauche. Das NAS System bietet ausreichend Platz für meine Dateien und sorgt für eine grundlegende Ausfallsicherheit.

### Was man optimieren könnte:
Ein Multinode-Cluster würde nochmal mehr Freiheitsgrade und Ausfallsicherheit ins System bringen, erhöht zeitgleich aber auch den Energieverbrauch und den Wartungsaufwand. Generell mehr CPU und RAM würden das ganze System performanter machen. So kann ich das System nicht beliebig skalieren. Vor allem Nextcloud und NAS fressen viel Ressourcen. 
