---
ShowToc: true
TocOpen: true
base_hash: 8da4d4d37fabc9f798b83868c113d003dc1250f0e329c419dcd3aa769efa6196
cover:
  alt: Traffic flow from VPS to Tailscale-protected K3s cluster
  caption: Public traffic routed through a VPS into a private K3s homelab via Tailscale
  image: expose-k3s-services-via-vps.png
  relative: true
date: 2025-12-21
description: Leitung des öffentlichen Web-Traffics über einen VPS in einen durch Tailscale
  gesicherten K3s-Cluster, der in einem privaten Homelab läuft.
draft: false
slug: expose-k3s-services-via-vps
tags:
- kubernetes
- k3s
- tailscale
- vps
title: K3s-Dienste aus einem durch Tailscale geschützten Homelab über einen VPS bereitstellen
---

Bei meiner letzten Homelab-Sitzung stieß ich auf ein Problem, das mir zunächst lästig erschien, sich aber schließlich in eine überraschend elegante Lösung verwandelte – eine, die es wert ist, geteilt zu werden.

## Das Problem
Ich betreibe in meiner Wohnung einen privaten Server, auf dem verschiedene Homelab-Dienste gehostet werden. Dieser Server ist bewusst nicht direkt über das öffentliche Internet erreichbar. Ich möchte meine internen Dienste privat halten und unter meiner Kontrolle behalten.

Für den Fernzugriff auf Reisen nutze ich [Tailscale](https://tailscale.com/). Dadurch kann ich von meinem Smartphone oder Laptop aus sicher auf Dienste wie [paperless-ngx](https://github.com/paperless-ngx/paperless-ngx) zugreifen, ohne etwas öffentlich preiszugeben. Bislang hat diese Konfiguration einwandfrei funktioniert.

Die Situation änderte sich, als ich [Nextcloud](https://nextcloud.com/de/) einrichtete. Im Gegensatz zu meinen anderen Diensten musste [Nextcloud](https://nextcloud.com/de/) öffentlich zugänglich sein, damit ich Dateien mit Freunden und Familie teilen konnte.

Die naheliegende Lösung wäre gewesen:
- Portweiterleitung auf meiner Fritz!Box konfigurieren
- Eine Domain auf meine Heim-IP verweisen
- DynDNS hinzufügen, um IP-Änderungen zu handhaben

Dieser Ansatz scheiterte jedoch schnell:
- Ich wollte mein Heimnetzwerk nicht über die Portweiterleitung offenlegen
- Mein DNS-Anbieter unterstützt keine DynDNS-Updates

Nachdem ich Alternativen geprüft hatte, wurde mir klar, dass ich das fehlende Puzzleteil bereits hatte:
einen VPS mit einer statischen öffentlichen IP-Adresse.

Daraus entstand die Idee:
Warum nicht den VPS als öffentlichen Einstiegspunkt nutzen und den Datenverkehr sicher in mein [Tailscale](https://tailscale.com/)-Netzwerk weiterleiten, direkt zu meinem K3s-Cluster zu Hause?

## Die Lösung
Die endgültige Architektur ist einfach, sicher und überraschend robust.

### Was ich bereits hatte
- Einen VPS mit einer statischen öffentlichen IP-Adresse (siehe meinen anderen Beitrag über meinen VPS ([Setup Coolify platform on your VPS](https://blog.matschcode.de/en/projects/self-hosting/coolify-vps-setup/))
- [Coolify](https://coolify.io/) läuft auf dem VPS als PaaS
- Traefik als Reverse-Proxy, verwaltet von Coolify
- Eine private Domain, die über A-Einträge auf die IP-Adresse des VPS verweist
- Tailscale, installiert auf beiden:
  - dem VPS
  - dem K3s-Cluster meines Homelabs

Zu diesem Zeitpunkt waren der VPS und mein Homelab bereits Teil desselben Tailnets, was bedeutete, dass sie sicher miteinander kommunizieren konnten, als befänden sie sich im selben lokalen Netzwerk.

### Was noch fehlte
Damit dies durchgängig funktionierte, waren zwei Anpassungen erforderlich:

#### 1. Reverse-Proxy-Routing auf dem VPS
[Traefik](https://traefik.io/traefik) (verwaltet von [Coolify](https://coolify.io/)) musste Anfragen für eine bestimmte Domain über [Tailscale](https://tailscale.com/) an einen Dienst weiterleiten, der in meinem privaten K3s-Cluster läuft.
Dazu muss die Datei `/data/coolify/proxy/dynamic/coolify.yaml` geändert werden:
``` yaml
# add routes
    nextcloud-http:
      middlewares:
        - redirect-to-https
      entryPoints:
        - http
      service: nextcloud-service
      rule: Host(`<yourdomain.com>`)
    nextcloud-https:
      entryPoints:
        - https
      service: nextcloud-service
      rule: 'Host(`<yourdomain.com>`)'
      tls:
        certresolver: letsencrypt
        
# add service
    nextcloud-service:
      loadBalancer:
        servers:
          -
            url: "http://<tailscale-ip>:<nodePort>" # node Port of LoadBalancer service (see step 2)
```

#### 2. Bereitstellung des Dienstes innerhalb von Kubernetes
Anstatt einen Standard-Ingress für Nextcloud zu verwenden, bin ich auf einen LoadBalancer-Dienst umgestiegen. Dadurch konnte Traefik auf dem VPS den Datenverkehr über die Tailscale-IP direkt an den Nextcloud-Pod weiterleiten.

```yaml
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
          nodePort: <nodePort> # must be greater than 30000
```


### Das Ergebnis
Nach diesen Änderungen sieht der Datenfluss wie folgt aus:**
{{< figure src="./routing.png" width="700" alt="VPS K3S routing" >}}
Das Smartphone kann über das Internet auf Nextcloud unter meiner privaten Domain zugreifen, jedoch nicht auf paperless-ngx.
Von innerhalb des Tailnets ist „paperless-ngx“ weiterhin verfügbar.

{{< alert type="info" title="" >}}
Keine Portweiterleitung – kein DynDNS – keine öffentliche Offenlegung meiner privaten IP-Adresse.
{{< /alert >}}

## Zusammenfassung
Durch die Nutzung eines VPS als öffentlichen Eingangs-Knotenpunkt und die Kombination mit Tailscale konnte ich einen einzelnen Dienst aus meinem privaten Homelab nach außen verfügbar machen, ohne die Sicherheit oder die Sauberkeit der Architektur zu beeinträchtigen.

**Diese Konfiguration bietet:**
- Eine stabile öffentliche IP-Adresse
- Sichere private Vernetzung über Tailscale
- Volle Kontrolle darüber, welche Dienste nach außen zugänglich sind
- Keine eingehenden Verbindungen zu meinem Heimnetzwerk