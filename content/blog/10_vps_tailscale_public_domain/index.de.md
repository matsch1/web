---
ShowToc: true
TocOpen: true
base_hash: 1bd74db1fcd4763bfe84f32101c5a9bc641480c4a126dd7cafc796a5d4edbc4f
cover:
  alt: Traffic flow from VPS to Tailscale-protected K3s cluster
  caption: Public traffic routed through a VPS into a private K3s homelab via Tailscale
  image: expose-k3s-services-via-vps.png
  relative: true
date: 2025-12-21
description: Route public web traffic through a VPS into a Tailscale-secured K3s cluster
  running in a private homelab.
draft: false
slug: expose-k3s-services-via-vps
tags:
- kubernetes
- k3s
- tailscale
- vps
title: K3s Dienste aus einem Tailscale-geschützten Homelab über einen VPS bereitstellen
---

Während meiner letzten Homelabbing-Sitzung stieß ich auf ein Problem, das sich zunächst als lästig erwies, sich aber schließlich in eine überraschend elegante Lösung verwandelte - eine, die es wert ist, geteilt zu werden.

## Das Problem
Ich betreibe einen privaten Server in meiner Wohnung, auf dem verschiedene Homelab-Dienste gehostet werden. Dieser Server ist vom öffentlichen Internet aus nicht direkt zugänglich. Ich möchte meine internen Dienste privat und unter meiner Kontrolle halten.

Für den Fernzugriff von unterwegs verwende ich [Tailscale](https://tailscale.com/). Damit kann ich von meinem Telefon oder Laptop aus sicher auf Dienste wie [paperless-ngx](https://github.com/paperless-ngx/paperless-ngx) zugreifen, ohne etwas öffentlich preiszugeben. Bislang hat diese Einrichtung einwandfrei funktioniert.

Die Situation änderte sich, als ich [Nextcloud](https://nextcloud.com/de/) einrichtete. Im Gegensatz zu meinen anderen Diensten musste [Nextcloud](https://nextcloud.com/de/) öffentlich zugänglich sein, damit ich Dateien mit Freunden und Familie teilen konnte.

Die offensichtliche Lösung wäre gewesen:
- Konfigurieren Sie eine Portweiterleitung auf meiner Fritz!Box
- Eine Domain auf meine Heim-IP verweisen
- DynDNS hinzufügen, um IP-Änderungen zu verwalten

Dieser Ansatz scheiterte jedoch schnell:
- Ich wollte mein Heimnetzwerk nicht über Portweiterleitung preisgeben
- Mein DNS-Anbieter unterstützt keine DynDNS-Aktualisierungen

Nachdem ich mich nach Alternativen umgesehen hatte, stellte ich fest, dass ich das fehlende Puzzlestück bereits hatte:
einen VPS mit einer statischen öffentlichen IP.

Das brachte mich auf die Idee:
Warum nicht den VPS als öffentlichen Einstiegspunkt nutzen und den Datenverkehr sicher in mein [Tailscale](https://tailscale.com/)-Netzwerk weiterleiten, direkt zu meinem K3s-Cluster zu Hause?

## Die Lösung
Die endgültige Architektur ist einfach, sicher und erstaunlich robust.

### Was ich bereits hatte
- Einen VPS mit einer statischen öffentlichen IP (siehe meinen anderen Beitrag über meinen VPS ([Setup Coolify platform on your VPS](https://blog.matschcode.de/en/projects/coolify-vps-setup/))
- [Coolify](https://coolify.io/), das auf dem VPS als PaaS läuft
- Traefik als Reverse-Proxy, der von Coolify verwaltet wird
- Eine private Domain, die über A-Records auf die VPS-IP zeigt
- Tailscale ist auf beiden installiert:
  - dem VPS
  - dem Homelab K3s-Cluster

Zu diesem Zeitpunkt waren der VPS und mein Homelab bereits Teil desselben Tailnets, d.h. sie konnten sicher kommunizieren, als ob sie sich im selben lokalen Netzwerk befänden.

## Was noch fehlte
Damit dies durchgängig funktioniert, musste ich zwei Anpassungen vornehmen:

### 1. Reverse-Proxy-Routing auf dem VPS
[Traefik](https://traefik.io/traefik) (verwaltet von [Coolify](https://coolify.io/)) musste Anfragen für eine bestimmte Domain an einen Dienst weiterleiten, der innerhalb meines privaten K3S-Clusters über [Tailscale](https://tailscale.com/) läuft.
Hierfür muss die Datei `/data/coolify/proxy/dynamic/coolify.yaml` modifiziert werden:
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

### 2. Dienst-Exposition innerhalb von Kubernetes
Anstatt einen Standard-Ingress für Nextcloud zu verwenden, habe ich auf einen LoadBalancer-Dienst umgestellt. Dies ermöglichte es Traefik auf dem VPS, den Datenverkehr über seine Tailscale-IP direkt an den Nextcloud-Pod weiterzuleiten.

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


**With these changes in place, traffic flow looks like this:**

{{< figure src="./routing.png" width="700" alt="VPS K3S routing" >}}

{{< alert type="info" title="" >}}
Keine Portweiterleitung.
Kein DynDNS.
Keine öffentliche Bekanntgabe meiner Heimat-IP.
{{< /alert >}}

## Zusammenfassung
Durch die Verwendung eines VPS als öffentlichen Zugangspunkt und die Kombination mit Tailscale war ich in der Lage, einen einzigen Dienst von meinem privaten Heimlabor aus zu veröffentlichen, ohne die Sicherheit oder die Sauberkeit der Architektur zu beeinträchtigen.

**This setup provides:**
- Eine stabile öffentliche IP
- Sicheres privates Netzwerk über Tailscale
- Volle Kontrolle darüber, welche Dienste offengelegt werden
- Keine eingehenden Verbindungen zu meinem Heimnetzwerk