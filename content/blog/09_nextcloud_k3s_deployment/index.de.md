---
ShowToc: true
TocOpen: true
base_hash: 68c92dfcdc3bf658f38cd233b69ea215fada4ba57fcc5b64224dabae68edeca7
cover:
  alt: nextcloud-k3s-helm-deployment
  caption: The way I deployed nextcloud on my k3s cluster using helm chart
  image: nextcloud-k3s-helm-deployment.png
  relative: true
date: 2025-12-19
description: So habe ich Nextcloud mithilfe eines Helm-Charts auf meinem k3s-Cluster
  bereitgestellt
draft: false
slug: nextcloud-k3s-helm-deployment
tags:
- kubernetes
- k3s
- nextcloud
title: Nextcloud-K3S-Bereitstellung mit Helm-Chart
---

## Einleitung
Nextcloud ist eine selbst gehostete Kollaborationsplattform, die Dateisynchronisierung und -freigabe, Kalender, Kontakte sowie ein wachsendes Ökosystem an Apps bietet. Sie gewährleistet ein hohes Maß an Dateneigentum und deckt dennoch viele Anwendungsfälle ab, die normalerweise von verwalteten Cloud-Diensten abgedeckt werden.
Mein Ziel ist es daher, Google Drive, Kontakte und Kalender durch eine selbst gehostete Nextcloud-Instanz zu ersetzen.

In meinem Homelab betreibe ich eine leichtgewichtige Kubernetes-Distribution auf Basis von k3s. 
Um die Bereitstellung reproduzierbar und wartbar zu halten und sie an cloud-native Best Practices anzupassen, habe ich mich entschieden, Nextcloud mithilfe des Helm-Charts bereitzustellen, anstatt auf Ad-hoc-Manifeste oder manuelle Container-Einrichtungen zurückzugreifen. 
Mit Helm kann ich den gewünschten Zustand deklarativ beschreiben, Upgrades sicherer verwalten und Konfigurationsänderungen versionsverwaltet halten.
Dies ist der erste Schritt, um meinen K3S-Cluster mit Argo CD zu verwalten.

Während des Bereitstellungsprozesses stieß ich auf mehrere nicht offensichtliche Herausforderungen und anwendungsspezifische Konfigurationsdetails, die beim Betrieb von Nextcloud auf Kubernetes leicht übersehen werden können. 
Dieser Artikel dokumentiert meinen Vorgehensweg, die aufgetretenen Probleme und die Lösungen, die in meiner K3S-Umgebung funktioniert haben, mit dem Ziel, anderen, die eine ähnliche Einrichtung versuchen, eine praktische Referenz zu bieten.

## Einrichtung des Helm-Charts
### Herunterladen des Helm-Charts
Der erste Schritt bestand darin, das offizielle Nextcloud-Helm-Chart zu beschaffen. Anstatt es bei jeder Bereitstellung direkt aus dem Repository zu installieren, ziehe ich es vor, das Chart lokal herunterzuladen und als Vendor-Chart zu verwalten. Dies verschafft mir vollständigen Einblick in die Standardeinstellungen, ermöglicht es mir, Änderungen im Laufe der Zeit nachzuverfolgen, und vermeidet Überraschungen, wenn sich die Upstream-Standardeinstellungen ändern.

``` sh
helm repo add nextcloud https://nextcloud.github.io/helm/
helm repo update
```

Indem ich das Chart zusammen mit meiner Cluster-Konfiguration aufbewahre, kann ich Updates sorgfältig prüfen und testen, bevor ich sie in meinem Homelab einsetze.

### Struktur der Werte-Datei
Die mit dem Chart gelieferte Standarddatei `values.yaml` ist umfassend, aber umfangreich. Eine direkte Bearbeitung wird schnell unübersichtlich, insbesondere beim Vergleich von Änderungen während Upgrades.

Um dies zu beheben, habe ich die Konfiguration in zwei Dateien aufgeteilt:

- `values-default.yaml`  
  Dies ist die ursprüngliche `values.yaml`. Sie wird nicht manuell bearbeitet und dient als Referenz für Änderungen im Upstream.

- `values.yaml`  
  Diese Datei enthält ausschließlich meine Überschreibungen und umgebungsspezifischen Konfigurationen.

Dieser Ansatz hat mehrere Vorteile:

- Klare Trennung zwischen den Standardwerten aus dem Upstream und meinen Anpassungen  
- Einfachere Diffs beim Upgrade des Charts  
- Geringeres Risiko, versehentlich von den beabsichtigten Standardwerten abzuweichen  

Bei der Bereitstellung werden beide Dateien angewendet, wobei `values.yaml` die Standardwerte überschreibt.


## Designentscheidungen
### Wahl der Datenbank: Zunächst SQLite, später MariaDB
Für die Erstbereitstellung habe ich mich bewusst für SQLite als Datenbank-Backend entschieden. Im Homelab-Kontext reduziert dies die Komplexität erheblich:

- Kein zusätzlicher Datenbankdienst, der betrieben werden muss  
- Schnellere Ersteinrichtung  
- Weniger Komponenten, die bei der Validierung der Bereitstellung berücksichtigt werden müssen  

Diese Entscheidung wurde mit der ausdrücklichen Absicht getroffen, später zu migrieren. Sobald sich die Bereitstellung als stabil erwiesen hat und die Nutzung zunimmt, wäre der Wechsel zu MariaDB mithilfe der Datenbankkonfigurationsoptionen des Helm-Charts unkompliziert.

Dieser schrittweise Ansatz ermöglichte es mir, mich zunächst auf Kubernetes-spezifische Aspekte zu konzentrieren und mich mit Nextcloud vertraut zu machen, bevor ich Datenbankoperationen und Backups in den Prozess einbezog.

## Erforderliche Anpassungen
### Vertrauenswürdige Domains für den Zugriff über benutzerdefinierte Domains
{{< figure src="https://help.nextcloud.com/uploads/default/original/3X/d/b/dbdf5a0e3ed2d78800f42f3612ef88c623e9ad8d.png" width="600" alt="Nextcloud untrusted domain error" >}}

Nextcloud legt streng fest, von welchen Hostnamen es Anfragen akzeptiert. Wenn Nextcloud hinter einem Ingress-Controller oder einem LoadBalancer betrieben wird, ist dies besonders wichtig.

Ich habe die vertrauenswürdigen Domänen explizit so konfiguriert, dass sie Folgendes umfassen:

Die über Ingress exponierte externe Domäne

Alle internen Dienstnamen, die zum Testen oder Debuggen verwendet werden

Ohne diese Konfiguration kann Nextcloud Verbindungen ablehnen oder Nutzer unerwartet umleiten. Die Verwaltung vertrauenswürdiger Domänen über Helm-Werte stellt sicher, dass die Konfiguration auch bei Pod-Neustarts und Upgrades erhalten bleibt.

Fügen Sie den folgenden Abschnitt zu Ihrer `values.yaml`-Datei hinzu:
``` yaml
nextcloud:
  trustedDomains: [localhost, <yourdomain.com>]
```

### Behebung des Verbindungsproblems zum NextCloud-App-Store
Um die Apps „Kontakte“ und „Kalender“ zu installieren, muss Nextcloud eine Verbindung zum NextCloud-App-Store herstellen. In meinem Fall war die Ansicht des App-Stores leer und es konnten keine Inhalte geladen werden.

{{< figure src="https://forum.yunohost.org/uploads/default/original/2X/6/6c1ca5c9b3e6c1f5c36a7d64e700b0f8078f208e.png" width="600" alt="Nextcloud App Store connection error" link="https://forum.yunohost.org/t/nextcloud-appstore-does-not-work/30804" >}}

Um das Problem zu identifizieren, habe ich die Verbindung zum App Store sowohl vom k3s-Knoten als auch aus dem NextCloud-Container heraus getestet:
``` sh
curl https://apps.nextcloud.com
```

Die Anfrage funktionierte auf dem Knoten, schlug jedoch innerhalb des Containers fehl. Nach einigen Debugging-Schritten konnte ich das Problem auf CoreDNS im Namespace „kube-system“ zurückführen.

Dies lässt sich beheben, indem man die CoreDNS-ConfigMap bearbeitet:
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
Diese Änderung spiegelt die tatsächlich auf dem Knoten konfigurierten Resolver wider. Nach der Anwendung wurde der App Store korrekt geladen und die App-Installation funktionierte wie erwartet.

### DAV-Konfiguration für den Zugriff auf Kontakte und Kalender
Ich habe die Anleitung von Robin befolgt, um meine Google-Kontakte und meinen Google-Kalender zu Nextcloud zu migrieren:
[Moving Google Contacts and Calendar to NextCloud](https://selfhostedheaven.com/posts/20220116-moving-google-contacts-and-calendar-to-nextcloud/)
Während des DAVx⁵-Einrichtungsprozesses blieb ich bei Schritt `Grant Access` hängen.

{{< figure src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRmZPWsy7ripvR1b7OIfdfyon23ykeLuhSVHA&s" width="300" alt="Nextcloud DAV Grant Access issue" link="https://itcamefromtheinternet.com/blog/nextcloud-android-sync/" >}}

Um DAV-Clients wie DAVx⁵ zu unterstützen, ist eine zusätzliche Konfiguration erforderlich. Dies lässt sich beheben, indem man über Helm-Werte eine benutzerdefinierte Konfigurationsdatei einbindet und den HTTPS-Client-Fix aktiviert.

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

phpClientHttpsFix:
  enabled: true
  protocol: https
```

Nach dem Anwenden dieser Konfiguration funktionierte der Schritt `Grant Access` auf meinem Android-Gerät ohne Probleme.

### Zusätzliche Manifeste
Nicht alles lässt sich nahtlos in Helm-Werte integrieren. Für Komponenten, die mit dem Nextcloud-Chart in Zusammenhang stehen, aber nicht streng genommen Teil davon sind, habe ich auf zusätzliche Manifeste zurückgegriffen.

Diese Manifeste befinden sich neben dem Helm-Deployment und werden im Rahmen desselben Workflows angewendet. Dadurch bleibt das gesamte Deployment zusammenhängend, während gleichzeitig die Grenzen des Upstream-Charts gewahrt bleiben.

In meinem Fall habe ich einen externen `LoadBalancer``-Dienst definiert:
``` yaml
extraManifests:
  externalService:
    apiVersion: v1
    kind: Service
    metadata:
      name: nextcloud-external-service
      namespace: nextcloud
    spec:
      type: LoadBalancer
      selector:
        app.kubernetes.io/component: app
        app.kubernetes.io/instance: nextcloud
        app.kubernetes.io/name: nextcloud
      ports:
        - protocol: TCP
          port: 8080
          targetPort: 80
          nodePort: <nodePort>
```


## Bereitstellung
Da nun alles vorbereitet ist, ist die Bereitstellung von Nextcloud unkompliziert:
``` sh
helm install nextcloud ./nextcloud \
  -n nextcloud \
  --create-namespace \
  -f ./nextcloud/values-default.yaml \
  -f ./nextcloud/values.yaml
```

## Zusammenfassung
Die Bereitstellung von Nextcloud auf einem k3s-Cluster mit Helm funktionierte gut, erforderte jedoch mehr Überlegung als eine einfache „helm install“-Anweisung. Durch eine übersichtliche Strukturierung der Konfiguration, bewusste Designentscheidungen und die Nutzung von Helm-Funktionen wie benutzerdefinierten Konfigurationsdateien und zusätzlichen Manifesten habe ich letztendlich eine Konfiguration erhalten, die sowohl flexibel als auch wartbar ist.

Die nächsten Schritte für diese Bereitstellung umfassen die Migration zu MariaDB, die Verschärfung der Sicherheitseinstellungen sowie die Einrichtung geeigneter Backup- und Überwachungsworkflows. Doch selbst in seiner aktuellen Form bietet dieser Ansatz eine solide Grundlage für den zuverlässigen Betrieb von Nextcloud in einer Kubernetes-Umgebung im Heimlabor.