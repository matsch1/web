---
ShowToc: true
TocOpen: true
base_hash: 256154078431f47b0ee08842528bc3575a732995d64e9185d294be3d8305496e
cover:
  alt: nextcloud-k3s-helm-deployment
  caption: The way I deployed nextcloud on my k3s cluster using helm chart
  image: nextcloud-k3s-helm-deployment.png
  relative: true
date: 2025-12-19
description: The way I deployed nextcloud on my k3s cluster using helm chart
draft: false
slug: nextcloud-k3s-helm-deployment
tags:
- kubernetes
- k3s
- nextcloud
title: Nextcloud K3S-Bereitstellung mit Helmdiagramm
---

## Einleitung
Nextcloud ist eine selbst gehostete Plattform für die Zusammenarbeit, die Dateisynchronisierung und -freigabe, Kalender, Kontakte und ein wachsendes Ökosystem von Anwendungen bietet. Sie bietet starke Garantien für das Dateneigentum und deckt gleichzeitig viele Anwendungsfälle ab, die üblicherweise von verwalteten Cloud-Diensten abgedeckt werden.
Mein Ziel ist es also, Google Drive, Contacs und Calendar durch eine selbst gehostete Nextcloud-Instanz zu ersetzen.

In meinem Homelab betreibe ich eine leichtgewichtige Kubernetes-Distribution, die auf k3s basiert.
Um das Deployment reproduzierbar und wartbar zu halten und den Best Practices für Cloud-Native zu entsprechen, habe ich mich entschieden, Nextcloud mit Hilfe des Helm-Diagramms zu implementieren, anstatt mich auf Ad-hoc-Manifeste oder manuelle Container-Setups zu verlassen.
Helm ermöglicht es mir, den gewünschten Zustand deklarativ zu beschreiben, Upgrades sicherer zu verwalten und Konfigurationsänderungen versionskontrolliert zu halten.
Dies ist der erste Schritt, um meinen K3S-Cluster mit Argo CD zu verwalten.

Während des Deployment-Prozesses stieß ich auf mehrere nicht offensichtliche Herausforderungen und anwendungsspezifische Konfigurationsdetails, die beim Betrieb von Nextcloud auf Kubernetes leicht übersehen werden können.
Dieser Artikel dokumentiert meinen Ansatz, die Probleme, auf die ich gestoßen bin, und die Lösungen, die für meine K3S-Umgebung funktionierten, mit dem Ziel, eine praktische Referenz für andere zu bieten, die eine ähnliche Einrichtung versuchen.

## Helm Chart Setup
### Herunterladen des Helm-Charts
Der erste Schritt bestand darin, das offizielle Nextcloud Helm Chart zu beschaffen. Anstatt es bei jedem Einsatz direkt aus dem Repository zu installieren, ziehe ich es vor, das Diagramm lokal herunterzuladen und anzubieten. Auf diese Weise habe ich vollen Einblick in die Standardeinstellungen, kann Änderungen im Laufe der Zeit verfolgen und vermeide Überraschungen, wenn sich die Upstream-Standardeinstellungen ändern.

``` sh
helm repo add nextcloud https://nextcloud.github.io/helm/
helm repo update
```

Indem ich das Diagramm neben meiner Clusterkonfiguration aufbewahre, kann ich Aktualisierungen gezielt überprüfen und testen, bevor ich sie in meinem Homelab einführe.

### Struktur der Wertedatei
Die Standard-`values.yaml`, die mit dem Diagramm geliefert wird, ist umfassend, aber groß. Wenn man sie direkt ändert, wird sie schnell unwartbar, insbesondere wenn man Änderungen bei Upgrades vergleicht.

Um dieses Problem zu lösen, habe ich die Konfiguration in zwei Dateien aufgeteilt:

- `values-default.yaml`
  Dies ist die ursprüngliche `values.yaml`. Sie wird nicht manuell bearbeitet und dient als Referenz für vorgelagerte Änderungen.

- `values.yaml`
  Diese Datei enthält nur meine Überschreibungen und umgebungsspezifische Konfigurationen.

Dieser Ansatz hat mehrere Vorteile:

- Klare Trennung zwischen den Standardeinstellungen der Originalhersteller und meinen Anpassungen
- Einfachere Diffs bei der Aktualisierung des Diagramms
- Geringeres Risiko einer versehentlichen Abweichung von den beabsichtigten Standardeinstellungen

Beim Deployment werden beide Dateien angewendet, wobei `values.yaml` die Standardeinstellungen überschreibt.


## Design-Entscheidungen
### Auswahl der Datenbank: Zuerst SQLite, später MariaDB
Für den ersten Einsatz habe ich mich bewusst für SQLite als Datenbank-Backend entschieden. In einem Homelab-Kontext reduziert dies die Komplexität erheblich:

- Es muss kein zusätzlicher Datenbankdienst betrieben werden
- Schnellere Ersteinrichtung
- Weniger bewegliche Teile bei der Validierung des Einsatzes

Diese Entscheidung wurde mit der ausdrücklichen Absicht getroffen, später zu migrieren. Sobald sich der Einsatz als stabil erwiesen hatte und die Nutzung zunahm, wäre ein Wechsel zu MariaDB mit Hilfe der Datenbankkonfigurationsoptionen des Helm-Diagramms problemlos möglich gewesen.

Dieser schrittweise Ansatz ermöglichte es mir, mich zunächst auf Kubernetes-spezifische Belange zu konzentrieren und mich mit Nextcloud vertraut zu machen, bevor ich Datenbankoperationen und Backups in den Mix einführte.

## Erforderliche Modifikationen
### Vertrauenswürdige Domänen für benutzerdefinierten Domänenzugriff
{{< figure src="https://help.nextcloud.com/uploads/default/original/3X/d/b/dbdf5a0e3ed2d78800f42f3612ef88c623e9ad8d.png
" width="600" alt="Nextcloud untrusted domain error" >}}

Nextcloud achtet streng darauf, von welchen Hostnamen es Anfragen annimmt. Dies ist besonders wichtig, wenn es hinter einem Ingress Controller oder einem LoadBalancer läuft.

Ich habe die vertrauenswürdigen Domänen explizit so konfiguriert, dass sie enthalten sind:

Die externe Domäne, die über Ingress zugänglich ist

Alle internen Dienstnamen, die zum Testen oder Debuggen verwendet werden

Ohne diese Konfiguration kann Nextcloud Verbindungen verweigern oder Benutzer unerwartet umleiten. Die Verwaltung vertrauenswürdiger Domänen durch Helm-Werte stellt sicher, dass die Konfiguration über Pod-Neustarts und Upgrades hinweg bestehen bleibt.

Fügen Sie den folgenden Abschnitt zu Ihrer `values.yaml`-Datei hinzu:
``` yaml
nextcloud:
  trustedDomains: [localhost, <yourdomain.com>]
```

### Reparieren der NextCloud App Store-Verbindung
Um die Apps Kontakte und Kalender zu installieren, muss Nextcloud eine Verbindung mit dem Nextcloud App Store herstellen. In meinem Fall war die App Store-Ansicht leer und konnte den Inhalt nicht laden.

{{< figure src="https://forum.yunohost.org/uploads/default/original/2X/6/6c1ca5c9b3e6c1f5c36a7d64e700b0f8078f208e.png
" width="600" alt="Nextcloud App Store connection error" link="https://forum.yunohost.org/t/nextcloud-appstore-does-not-work/30804
" >}}

Um das Problem zu identifizieren, habe ich die Konnektivität zum App Store sowohl vom k3s-Knoten als auch vom Nextcloud-Container aus getestet:
``` sh
curl https://apps.nextcloud.com
```

Die Anfrage funktionierte auf dem Knoten, schlug aber innerhalb des Containers fehl. Nach einiger Fehlersuche konnte ich das Problem auf CoreDNS im kube-system-Namensraum zurückführen.

Dies kann durch Bearbeiten der CoreDNS ConfigMap behoben werden:
``` sh
kubectl edit configMap coredns -nkube-system
```

Ersetzen Sie
``` sh
forward . /etc/resolv.conf
```
durch
``` sh
forward . 1.1.1.1 8.8.8.8
```
.
Diese Änderung spiegelt die auf dem Knoten konfigurierten effektiven Auflöser wider. Nach Anwendung dieser Änderung wurde der App Store korrekt geladen und die Installation der App funktionierte wie erwartet.

### DAV-Konfiguration für den Zugriff auf Kontakte und Kalender
Ich habe die Anleitung von Robin befolgt, um meine Google-Kontakte und den Kalender zu Nextcloud zu migrieren:
[Moving Google Contacts and Calendar to NextCloud](https://selfhostedheaven.com/posts/20220116-moving-google-contacts-and-calendar-to-nextcloud/)
Während des DAVx⁵-Einrichtungsprozesses blieb ich beim Schritt `Grant Access` hängen.

{{< figure src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRmZPWsy7ripvR1b7OIfdfyon23ykeLuhSVHA&s
" width="400" alt="Nextcloud DAV Grant Access issue" link="https://itcamefromtheinternet.com/blog/nextcloud-android-sync/
" >}}

Um DAV-Clients wie DAVx⁵ zu unterstützen, ist eine zusätzliche Konfiguration erforderlich. Dies wird gelöst, indem eine benutzerdefinierte Konfigurationsdatei über Helm-Werte injiziert und der HTTPS-Client-Fix aktiviert wird.

``` yaml
nextcloud:
  configs:
    davx.config.php: |-
      <?php
      $CONFIG = array(
        'csrf.optout' => array(
          '/^WebDAVFS/',
          '/^Microsoft-WebDAV-MiniRedir/',
          '/RaiDrive/',
          '/CrKey/',
          '/Nextcloud-android/',
          '/Nextcloud-iOS/',
      ),
    );
  
│ phpClientHttpsFix:
│   enabled: true
│   protocol: https
```

Nach Anwendung dieser Konfiguration funktionierte der Schritt `Grant Access` auf meinem Android-Gerät ohne Probleme.

### Extra Manifeste
Nicht alles passt sauber in die Helm-Werte. Für Komponenten, die an das Nextcloud-Diagramm angrenzen, aber nicht unbedingt Teil davon sind, habe ich mich auf zusätzliche Manifeste verlassen.

Diese Manifeste laufen neben dem Helm-Einsatz und werden im Rahmen desselben Workflows angewendet. Auf diese Weise bleibt der Gesamteinsatz kohärent und respektiert gleichzeitig die Grenzen des vorgelagerten Diagramms.

In meinem Fall habe ich einen externen `LoadBalancer``-Dienst definiert:
``` yaml
│ extraManifests:
│   externalService:
│     apiVersion: v1
│     kind: Service
│     metadata:
│       name: nextcloud-external-service
│       namespace: nextcloud
│     spec:
│       type: LoadBalancer
│       selector:
│         app.kubernetes.io/component: app
│         app.kubernetes.io/instance: nextcloud
│         app.kubernetes.io/name: nextcloud
│       ports:
│         - protocol: TCP
│           port: 8080
│           targetPort: 80
│           nodePort: <nodePort>
```


## Bereitstellung
Wenn alles eingerichtet ist, ist die Bereitstellung von Nextcloud ganz einfach:
``` sh
helm install nextcloud ./nextcloud \
  -n nextcloud \
  --create-namespace \
  -f ./nextcloud/values-default.yaml \
  -f ./nextcloud/values.yaml
```

## Zusammenfassung
Die Bereitstellung von Nextcloud auf einem k3s-Cluster mit Helm hat gut funktioniert, aber sie erforderte mehr Überlegungen als eine einfache Helm-Installation. Durch eine saubere Strukturierung der Konfiguration, bewusste Designentscheidungen und die Nutzung von Helm-Funktionen wie benutzerdefinierten Konfigurationsdateien und zusätzlichen Manifesten habe ich eine Einrichtung erhalten, die sowohl flexibel als auch wartbar ist.

Zu den nächsten Schritten für diesen Einsatz gehören die Migration auf MariaDB, die Verschärfung der Sicherheitseinstellungen und das Hinzufügen geeigneter Backup- und Überwachungsworkflows. Aber selbst in seiner jetzigen Form bietet dieser Ansatz eine solide Grundlage für den zuverlässigen Betrieb von Nextcloud in einer Kubernetes-Umgebung für den Heimgebrauch.