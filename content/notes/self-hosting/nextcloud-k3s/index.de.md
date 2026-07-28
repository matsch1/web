---
ShowToc: true
TocOpen: true
base_hash: d88cb6653205b991d20c0a79824e3d397670cb9e1f1a79ebd043d63fc6d58317
cover:
  alt: nextcloud-k3s-helm-deployment
  caption: The way I deployed nextcloud on my k3s cluster using helm chart
  image: nextcloud-k3s-helm-deployment.webp
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
Nextcloud ist eine selbst gehostete Kollaborationsplattform, die Dateisynchronisierung und -freigabe, Kalender, Kontakte sowie ein wachsendes Ökosystem von Apps bietet. Sie gewährleistet ein hohes Maß an Dateneigentum und deckt dennoch viele Anwendungsfälle ab, die normalerweise von verwalteten Cloud-Diensten abgedeckt werden.
Mein Ziel ist es daher, Google Drive, Kontakte und Kalender durch eine selbst gehostete Nextcloud-Instanz zu ersetzen.

In meinem Homelab betreibe ich eine leichtgewichtige Kubernetes-Distribution auf Basis von k3s. 
Um die Bereitstellung reproduzierbar und wartbar zu halten und sie an cloud-native Best Practices anzupassen, habe ich mich entschieden, Nextcloud mithilfe des Helm-Charts bereitzustellen, anstatt auf Ad-hoc-Manifeste oder manuelle Container-Einrichtungen zurückzugreifen. 
Mit Helm kann ich den gewünschten Zustand deklarativ beschreiben, Upgrades sicherer verwalten und Konfigurationsänderungen versionsverwaltet halten.
Dies ist der erste Schritt, um meinen k3s-Cluster mit Argo CD zu verwalten.

Während des Bereitstellungsprozesses stieß ich auf mehrere nicht offensichtliche Herausforderungen und anwendungsspezifische Konfigurationsdetails, die beim Betrieb von Nextcloud auf Kubernetes leicht übersehen werden können. 
Dieser Artikel dokumentiert meinen Vorgehensweg, die aufgetretenen Probleme und die Lösungen, die in meiner K3S-Umgebung funktioniert haben, mit dem Ziel, anderen, die eine ähnliche Einrichtung versuchen, eine praktische Referenz zu bieten.

## Einrichtung des Helm-Charts
### Herunterladen des Helm-Charts
Der erste Schritt bestand darin, das offizielle Nextcloud-Helm-Chart zu beschaffen. Anstatt es bei jeder Bereitstellung direkt aus dem Repository zu installieren, ziehe ich es vor, das Chart lokal herunterzuladen und als „Vendor“ zu speichern. Dies verschafft mir vollständigen Einblick in die Standardeinstellungen, ermöglicht es mir, Änderungen im Laufe der Zeit nachzuverfolgen, und vermeidet Überraschungen, wenn sich die Upstream-Standardeinstellungen ändern.

``` sh
helm repo add nextcloud https://nextcloud.github.io/helm/
helm repo update
```

Indem ich das Chart zusammen mit meiner Cluster-Konfiguration aufbewahre, kann ich Updates sorgfältig prüfen und testen, bevor ich sie in meinem Homelab einsetze.

### Struktur der Werte-Datei
Die mit dem Chart gelieferte Standard-`values.yaml` ist umfassend, aber umfangreich. Eine direkte Bearbeitung wird schnell unübersichtlich, insbesondere beim Vergleich von Änderungen während Upgrades.

Um dies zu beheben, habe ich die Konfiguration in zwei Dateien aufgeteilt:

- `values-default.yaml`  
  Dies ist die ursprüngliche Datei `values.yaml`. Sie wird nicht manuell bearbeitet und dient als Referenz für Änderungen im Upstream.

- `values.yaml`  
  Diese Datei enthält ausschließlich meine Überschreibungen und umgebungsspezifische Konfigurationen.

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
- Weniger bewegliche Teile bei der Validierung der Bereitstellung  

Diese Entscheidung wurde mit der ausdrücklichen Absicht getroffen, später zu migrieren. Sobald sich die Bereitstellung als stabil erwiesen hätte und die Nutzung zunahm, wäre der Wechsel zu MariaDB mithilfe der Datenbankkonfigurationsoptionen des Helm-Charts unkompliziert gewesen.

Dieser schrittweise Ansatz ermöglichte es mir, mich zunächst auf Kubernetes-spezifische Aspekte zu konzentrieren und mich mit Nextcloud vertraut zu machen, bevor ich Datenbankvorgänge und Backups in den Prozess einbezog.

### Nun auf PostgreSQL migriert
Die Migration zu MariaDB verlief nicht so reibungslos wie erwartet, da der Datenbank-Pod instabil war.

Da dies frustrierend war, bin ich stattdessen auf PostgreSQL umgestiegen.
Mit Hilfe meines hermes-agents verlief die Migration von SQLite zu PostgreSQL sehr reibungslos.

## Erforderliche Anpassungen
### Vertrauenswürdige Domänen für den Zugriff über benutzerdefinierte Domänen
{{< figure src="https://help.nextcloud.com/uploads/default/original/3X/d/b/dbdf5a0e3ed2d78800f42f3612ef88c623e9ad8d.png" width="600" alt="Nextcloud untrusted domain error" >}}

Nextcloud legt streng fest, von welchen Hostnamen es Anfragen akzeptiert. Wenn Nextcloud hinter einem Ingress-Controller oder einem LoadBalancer läuft, ist dies besonders wichtig.

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

Dies lässt sich durch Bearbeiten der CoreDNS-ConfigMap beheben:
``` sh
kubectl edit configMap coredns -nkube-system
```

Ersetze 
``` sh
forward . /etc/resolv.conf
``` 
durch 
``` sh
forward . 1.1.1.1 8.8.8.8
```
.
Diese Änderung spiegelt die tatsächlich auf dem Knoten konfigurierten Resolver wider. Nach der Anwendung wurde der App Store korrekt geladen und die App-Installation funktionierte wie erwartet.


### DAV-Konfiguration für den Zugriff auf Android-Kontakte und -Kalender
Um Kalender und Kontakte auf Ihrem Smartphone zu integrieren, muss Nextcloud DAV-Zugriff bereitstellen.

Ich habe die Anleitung von Robin befolgt, um meine Google-Kontakte und meinen Google-Kalender zu Nextcloud zu migrieren:
„Google-Kontakte und -Kalender zu NextCloud verschieben.“ Leider ist der Blog nicht mehr online.
Für die Datenmigration würde ich nun die von Nextcloud bereitgestellte [migration tool](https://nextcloud.com/blog/easy-migration-to-nextcloud-from-insecure-and-privacy-unfriendly-platforms-now-available/) verwenden.

Um [synchronize with Android](https://docs.nextcloud.com/server/19/user_manual/pim/sync_android.html) durchzuführen, befolgen Sie die Anweisungen von Nextcloud.
Während des [DAVx⁵](https://www.davx5.com/download/) Einrichtungsprozesses bin ich beim Schritt `Grant Access` hängen geblieben.

{{< figure src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRmZPWsy7ripvR1b7OIfdfyon23ykeLuhSVHA&s" width="300" alt="Nextcloud DAV Grant Access issue" link="https://itcamefromtheinternet.com/blog/nextcloud-android-sync/" >}}

Um DAV-Clients wie [DAVx⁵](https://www.davx5.com/download/) zu unterstützen, ist eine zusätzliche Konfiguration erforderlich. Dies lässt sich beheben, indem man über Helm-Werte eine benutzerdefinierte Konfigurationsdatei einfügt und den HTTPS-Client-Fix aktiviert.

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
Nicht alles lässt sich nahtlos in Helm-Werte integrieren. Für Komponenten, die zwar mit dem Nextcloud-Chart in Zusammenhang stehen, aber nicht streng genommen Teil davon sind, habe ich auf zusätzliche Manifeste zurückgegriffen.

Diese Manifestdateien befinden sich neben dem Helm-Deployment und werden im Rahmen desselben Workflows angewendet. Dadurch bleibt das gesamte Deployment zusammenhängend, während die Grenzen des Upstream-Charts weiterhin gewahrt bleiben.

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
Die Bereitstellung von Nextcloud auf einem k3s-Cluster mit Helm hat gut funktioniert, erforderte jedoch mehr Überlegung als eine einfache „helm install“-Anweisung. Durch eine übersichtliche Strukturierung der Konfiguration, bewusste Designentscheidungen und die Nutzung von Helm-Funktionen wie benutzerdefinierten Konfigurationsdateien und zusätzlichen Manifesten habe ich letztendlich eine Konfiguration erhalten, die sowohl flexibel als auch wartungsfreundlich ist.

Die dazugehörige Netzwerkarchitektur, die diesen Nextcloud-Dienst über einen VPS öffentlich erreichbar macht, ohne das Heimnetzwerk zu öffnen, finden Sie unter [Expose K3s Services from a Tailscale-Protected Homelab via a VPS](https://blog.matschcode.de/en/notes/self-hosting/expose-k3s-services-via-vps/).

Ich bin mit der aktuellen Konfiguration sehr zufrieden, daher sind keine weiteren Änderungen geplant.