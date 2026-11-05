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
Die Infrastruktur meines Heimservers wurde als produktionsnahes Single-Node-Homelab umgesetzt. Für mich bedeutet das, einen Kompromiss aus einem möglichst produktionsnahen Setup, wenig Wartungsaufwand und geringen Kosten einzugehen.
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
Der Hypervisor ist die Virtualisierungsschicht im Cluster. Sie ist dazu da die Grundsysteme logisch sauber voneinander zu trennne. Da beide VMs auf einem einzigen physischen Host laufen, führt dessen Ausfall zum Ausfall aller darauf betriebenen Dienste. Eine Hochverfügbarkeit des Gesamtsystems ist daher nicht gegeben. Im Rahmen eines Homelabs nehme ich das vorerst in Kauf.

Als Virtualisierungsplattform nutze ich Proxmox VE, das auf Debian basiert und direkt auf dem Host installiert ist. Die virtuellen Maschinen werden mit KVM/QEMU betrieben.

Mittels Ansible und Terraform beschreibe ich die Infrastruktur und dessen Setup in Konfigurationsdateien, was es mir erlaubt nach Infrastructure-As-Code Prinzipien die Cluster Infrastruktur zu managen.


## Kubernetes
Um meine Services zu deployen habe ich mich für ein K3s cluster entschieden, welches im Single-Node-Betrieb auf einer VM läuft.
Das erlaubt mir mein Setup flexibel zu konfigurieren und dabei verschiedene Kubernetes Themen zu lernen und auszuprobieren.

Die Services selbst werden mit Argo CD nach dem GitOps-Prinzip bereitgestellt. Der gewünschte Zustand meiner Anwendungen liegt dabei in Git; Argo CD gleicht ihn mit dem Zustand im Cluster ab. Für die Konfiguration meiner Anwendungen nutze ich Helm-Charts, die Argo CD ebenfalls unterstützt.

## NAS
Die zweite VM ist eine reine NAS-VM. Mit TrueNAS als Betriebssystem verwalte ich einen ZFS-Storage-Pool, der aus einem RAIDZ1-VDEV mit vier HDDs besteht. Die einfache Parität ermöglicht es, den Ausfall einer einzelnen HDD ohne Datenverlust zu überstehen. Diese Redundanz ersetzt jedoch kein separates Backup: Sie schützt beispielsweise nicht vor versehentlichem Löschen, Schadsoftware oder dem Verlust des gesamten Servers.

Bei TrueNAS als VM ist auch die Anbindung der Festplatten wichtig. Ein per PCI-Passthrough durchgereichter SATA- oder HBA-Controller ermöglicht TrueNAS direkten Zugriff auf die angeschlossenen HDDs und ist die bevorzugte Variante, sofern Hardware und IOMMU-Gruppen dies erlauben. Virtuelle Datenträger sind damit nicht gleichzusetzen.

Das NAS beinhaltet allerdings nicht nur meine Dateibackups. Über NFS stelle ich dem Kubernetes-Cluster persistenten Speicher für Anwendungsdaten bereit. Damit liegen diese getrennt von den Systemdatenträgern der Kubernetes-VM auf dem RAIDZ1-Pool. Diese Speicherung ist für sich genommen kein Backup; dafür sind zusätzliche Sicherungen erforderlich.

## Fazit
Für einen privaten Heimserver bietet mein System eine ordentliche Grundlage. 

### Was mir sehr gut gefällt:
Es ermöglicht mir mehrere Services selbst zu hosten und viele Sachen auszuprobieren. Dabei behalte ich auch immer die Hoheit über meine Daten und bin nicht angewiesen auf Techkonzerne. Die vorhandenen Ressourcen bieten ausreichend Kapazität für alles, was ich zu Hause brauche. Ein möglichst geringer Energieverbrauch ist dabei ein Ziel. Das NAS-System bietet ausreichend Platz für meine Dateien und toleriert durch RAIDZ1 den Ausfall einer einzelnen HDD.

### Was man optimieren könnte:
Ein Cluster über mehrere physische Hosts könnte mehr Spielraum bei der Verteilung der Anwendungen bieten und die Verfügbarkeit erhöhen. Für eine höhere Verfügbarkeit müssten auch Control Plane, Speicher und Anwendungen entsprechend redundant ausgelegt sein. Die einzelne TrueNAS-VM bleibt andernfalls ein zentraler Ausfallpunkt für NFS-abhängige Anwendungen. Mehrere Kubernetes-VMs auf demselben Host schützen dagegen nicht vor dessen Ausfall. Zusätzliche Hosts würden auch den Energieverbrauch und den Wartungsaufwand erhöhen.

Mehr CPU-Leistung und RAM könnten Engpässe entschärfen, sofern diese Ressourcen die jeweilige Anwendung begrenzen. Die Skalierbarkeit meines einzelnen Heimservers bleibt jedoch beschränkt. Insbesondere Nextcloud und das NAS können je nach Nutzung relevante CPU-, RAM- und I/O-Ressourcen benötigen.

Zusätzlich wäre ein Offsite-Backup interessant, welches meine Daten selbst bei Brand oder Diebstahl an einem physisch anderen Ort sichert.
