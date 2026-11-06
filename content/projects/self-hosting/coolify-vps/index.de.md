---
ShowToc: true
TocOpen: true
base_hash: 8b1284c3df8e304a606a17d05c19b4256e06866341ca2cdf0d9f0e7125ef2f30
cover:
  alt: coolify-vps-setup
  caption: ''
  image: editorial-cover.webp
  relative: true
cover_translation_version: 1
date: 2025-05-10
description: Server-Absicherung und Bereitstellung der ersten App mit Coolify.
draft: false
homepage:
  section: engineering
  teaser: 'Hardening a VPS and deploying a first app with Coolify: practical lessons
    from my setup.'
  title: Coolify on my own VPS
project:
  status: active
slug: coolify-vps-setup
tags:
- server
- syncthing
- coolify
- tailscale
title: Richten Sie die Coolify-Plattform auf Ihrem VPS ein
translation_lock: false
---

{{< alert type="info" title="" >}}
Der VPS läuft immer noch, obwohl sich die meisten seiner Dienste seit der Ersteinrichtung geändert haben.
{{< /alert >}}

## UPDATE NOVEMBER 2026
Der VPS läuft immer noch, obwohl er mittlerweile andere Dienste hostet als ursprünglich eingerichtet.
Coolify hat sich als zuverlässig erwiesen und erfordert kaum bis gar keinen Wartungsaufwand.
Der Server dient derzeit drei Hauptzwecken:
- Hosting von Syncthing, dem einzigen Dienst, der unverändert geblieben ist. Mein Synchronisationssetup beschreibe ich im Beitrag zur [Obsidian-Cloud-Synchronisation]({{< relref "/notes/self-hosting/obsidian-syncthing" >}}).
- Hosting meines [persönlichen Assistenten mit Hermes Agent]({{< relref "/projects/development/hermes-agent" >}}).
- Reverse-Proxy für mein Homelab über Tailscale. Der Beitrag [K3s-Dienste über VPS und Tailscale veröffentlichen]({{< relref "/notes/self-hosting/tailscale-public-domain" >}}) erklärt diese Verbindung; [meine Homelab-Infrastruktur]({{< relref "/notes/self-hosting/homelab-infrastructure" >}}) liefert den Gesamtüberblick.

## Einleitung
Selbsthosting hat sich als hervorragende Möglichkeit erwiesen, praktische Erfahrungen mit Serveradministration, DevOps-Tools und modernen Bereitstellungsplattformen zu sammeln. Mein Ziel war es, einen Virtual Private Server (VPS) einzurichten, ihn ordnungsgemäß abzusichern und als kleine, aber flexible Plattform für die Bereitstellung von Backend-Komponenten zu nutzen, die meinen App-Entwicklungs-Workflow unterstützen.

Zu den typischen Workloads gehören leichtgewichtige Dienste wie PocketBase für den Backend-Speicher, Unleash für Feature-Flags und Automatisierungstools wie n8n. Außerdem plante ich, den Server im Laufe der Zeit für die Dateisynchronisation über Syncthing und andere Experimente zu nutzen.

Um das Deployment und das Management des Anwendungslebenszyklus zu optimieren, entschied ich mich für Coolify, eine Open-Source-PaaS, die die Container-Orchestrierung in einem benutzerfreundlichen Dashboard abstrahiert. Dieser Beitrag dokumentiert die anfängliche VPS-Einrichtung, grundlegende Maßnahmen zur Absicherung, die Tailscale-Integration sowie das Deployment der ersten Anwendung.

Dies ist ein persönlicher Erfahrungsbericht und kein vollständiger oder gepflegter Leitfaden zur Sicherheitshärtung. Die Befehle veranschaulichen die Einrichtung; Details können je nach Betriebssystem und Coolify-Version variieren.

## Server-Hosting
Die Wahl des richtigen Hosting-Anbieters hängt von Budget, Standort, Bandbreite und Support ab. Coolify gibt Mindestanforderungen von 2 CPU-Kernen, 2 GB RAM und 10 GB freiem Speicherplatz auf einer unterstützten Linux-Distribution an. Anwendungen und Builds benötigen zusätzliche Ressourcen. Beachten Sie nach der Bereitstellung der Instanz Folgendes:

- Serverstandort und Tarif  
- Betriebssystem-Image (z. B. Ubuntu 22.04 LTS)  
- Vom Host bereitgestellte grundlegende Anmeldedaten  
- Öffentliche IP-Adresse  

{{< figure src="./netcup_vps.png" width="700" alt="" class="right" >}}

In meinem Fall habe ich mich für einen VPS entschieden, der von [netcup](https://www.netcup.com/de/server/vps) gehostet wird.
Ich habe das Projekt mit der kleinsten VPS-Option `VPS 250 G11s` begonnen, bin aber später auf die zweite Option `VPS 500 G11s` umgestiegen.
Das kostet mich etwa 5 € pro Monat (einschließlich eigener Domain) und bietet genügend Ressourcen für alles, was ich brauche.

## Zugriff auf den Server
### SCP
Für den ersten Zugriff kann man sich über das von netcup bereitgestellte Server-Control-Panel mit dem Server verbinden.
Beim ersten Mal meldet man sich als Root-Benutzer beim VPS an, daher muss als Erstes ein anderer Benutzer eingerichtet werden.

### Benutzer einrichten
``` shell
# Debian systems
adduser <username>
usermod -aG sudo <username>
```

Dadurch wird der Benutzer angelegt, nach einem Passwort gefragt, das Home-Verzeichnis des Benutzers erstellt und grundlegende Standardeinstellungen festgelegt. Der zweite Befehl dient dazu, den Benutzer zur sudo-Gruppe hinzuzufügen. Damit ist es möglich, Befehle mit erweiterten Benutzerrechten über `sudo` auszuführen.

```
# Switch to new user
sudo su - <server-user>
```

### SSH-Zugriff einrichten
Dazu muss auf dem Client-Rechner ein SSH-Schlüssel generiert werden.

```
ssh-keygen -t ed25519 -C "your_email@example.com"
```

Sie werden zur Eingabe des Schlüsselnamens, des Speicherorts und der Passphrase aufgefordert.
Der Schlüssel kann unter `~/.ssh/<ssh-key>` gespeichert werden. Für einen persönlichen Admin-Schlüssel wird eine Passphrase empfohlen.
Dadurch werden zwei Dateien erstellt: `<ssh-key>` und `<ssh-key.pub>`.

Um SSH-Zugriff auf den VPS zu erhalten, erstellen Sie bei Bedarf das SSH-Verzeichnis auf dem Server:
```
sudo install -d -m 700 -o <server-user> -g <server-user> /home/<server-user>/.ssh
```

Kopieren Sie den Inhalt von `<ssh-key.pub>` in `/home/<server-user>/.ssh/authorized_keys`. Falls die Datei nicht existiert, erstellen Sie sie; andernfalls fügen Sie den Schlüssel an, ohne vorhandene Einträge zu überschreiben.
Sie können dazu `nano` oder `vi` als Texteditor in der Befehlszeile verwenden.

Achten Sie auf die Benutzerrechte dieser Datei.
```
sudo chmod 600 /home/<server-user>/.ssh/authorized_keys
sudo chown <server-user>:<server-user> /home/<server-user>/.ssh/authorized_keys
```

Nach dieser SSH-Konfiguration kann vom Client aus über folgenden Befehl auf den VPS zugegriffen werden:
```
ssh -i ~/.ssh/<ssh-key> <server-user>@<server-ip>
```

### Server-Absicherung
Um unbefugten Zugriff zu reduzieren, habe ich mich auf die SSH-Authentifizierung und die Firewall-Regeln konzentriert.

#### Anmeldebeschränkungen
{{< alert type="warning" title="Danger" >}}
Achtung! Die folgenden Einstellungen können den Zugriff auf Ihren Server unterbrechen!
{{< /alert >}}

##### Ausschließlich SSH-Zugriff
Die Anmeldung per Passwort wird untersagt. 
{{< alert type="warning" title="Danger" >}}
Stellen Sie sicher, dass die SSH-Anmeldung einwandfrei funktioniert!
{{< /alert >}}
Passwortauthentifizierung deaktivieren (bearbeite `/etc/ssh/sshd_config`):

 PasswordAuthentication no
    KbdInteractiveAuthentication no

##### Root-Zugriff und Coolify
Die vollständige Deaktivierung der Root-SSH-Anmeldung ist eine gängige Sicherheitsmaßnahme, steht jedoch im Widerspruch zur Standardkonfiguration von Coolify: Coolify nutzt SSH als `root` zur Verwaltung des lokalen Servers. Erlauben Sie für diese Konfiguration die schlüsselbasierte Root-Anmeldung und deaktivieren Sie gleichzeitig die passwortbasierte Root-Anmeldung:

 PermitRootLogin prohibit-password

Eine Alternative ist eine unterstützte Coolify-Konfiguration ohne Root-Zugriff, die jedoch zusätzliche Einstellungen erfordert und hier nicht behandelt wird. Der Root-Schlüsselzugriff sollte auf die erforderlichen Verwaltungspfade beschränkt werden.

{{< alert type="warning" title="Danger" >}}
Halten Sie die aktuelle Sitzung offen und stellen Sie sicher, dass der Konsolenzugriff verfügbar ist, bevor Sie die SSH-Einstellungen ändern.
{{< /alert >}}

Überprüfen Sie alle enthaltenen Konfigurationsdateien in `/etc/ssh/sshd_config.d/` auf widersprüchliche Einstellungen. Überprüfen Sie die Konfiguration und laden Sie sie unter Debian/Ubuntu neu:

```sh
sudo sshd -t
# Only reload if validation succeeds:
sudo systemctl reload ssh
```

Testen Sie eine neue schlüsselbasierte Verbindung in einem zweiten Terminal, bevor Sie die ursprüngliche Sitzung schließen.

#### Firewall
Aus Sicherheitsgründen möchten wir alle Ports blockieren, die wir nicht benötigen.
Zu diesem Zweck verwenden wir die unkomplizierte Firewall ([UFW](https://wiki.ubuntu.com/UncomplicatedFirewall)).

{{< alert type="warning" title="Danger" >}}
Bevor Sie die Firewall aktivieren, überprüfen Sie, ob die SSH-Anmeldung einwandfrei funktioniert!
{{< /alert >}}

```
# Installation
sudo apt install ufw

# Setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp #ssh
sudo ufw allow 80/tcp #http
sudo ufw allow 443/tcp #https
sudo ufw enable
```

### Tailscale
Der nächste Schritt war das Einrichten eines virtuellen privaten Netzwerks (VPN) für den privaten Verwaltungszugriff. Tailscale stellt dieses Netzwerk bereit, doch durch die Installation wird der öffentliche Zugriff nicht deaktiviert: Die oben genannten Firewall-Regeln lassen weiterhin SSH, HTTP und HTTPS aus dem Internet zu.

Ein sehr einfach einzurichtendes und benutzerfreundliches VPN ist [Tailscale](https://tailscale.com/). Es nutzt im Hintergrund WireGuard, um verschlüsselte Punkt-zu-Punkt-Verbindungen zwischen Ihren Geräten herzustellen.

{{< figure src="https://cdn.sanity.io/images/w77i7m8x/production/fab2bfd901de3d58f7f62d35fe9a5107fedc43c1-1360x725.svg?w=3840&q=75&fit=clip&auto=format" width="700" alt="Tailscale">}}


#### Einrichtung
Die Ersteinrichtung umfasste die vorübergehende Deaktivierung von UFW. Dies ist für Tailscale normalerweise nicht erforderlich und lässt die Host-Dienste während der Deaktivierung ohne UFW-Schutz. Halten Sie eine aktive SSH-Sitzung und den Zugriff auf die Provider-Konsole bereit:
```
sudo ufw disable
```

Auf Debian-Systemen können Sie Tailscale ganz einfach mit diesem Befehl auf Ihrem VPS installieren:
```
curl -fsSL https://tailscale.com/install.sh | sh
```

#### Tailscale starten
```
sudo tailscale up --ssh
tailscale ip
```

Starten Sie Tailscale und melden Sie sich bei Tailnet an. Der zweite Befehl gibt die Tailscale-IP Ihres Servers aus.

Das Flag `--ssh` aktiviert Tailscale-SSH, das die Authentifizierung über Tailnet-Identitäten und SSH-Richtlinien anstelle des oben konfigurierten persönlichen SSH-Schlüssels vornimmt. Die Zugriffsregeln unterscheiden sich von denen von OpenSSH `sshd_config`, einschließlich der Einschränkungen für die Root-Anmeldung. Für herkömmliches schlüsselbasiertes OpenSSH über Tailscale lassen Sie stattdessen `--ssh` weg (oder deaktivieren Sie es mit `sudo tailscale set --ssh=false`, falls es bereits aktiviert ist).

Die folgende Regel erlaubt eingehenden Host-Datenverkehr auf der Tailscale-Schnittstelle, vorbehaltlich der Tailnet-Zugriffsrichtlinien; sie öffnet keinen bestimmten Tailscale-Port:
```
sudo ufw allow in on tailscale0
```

Bevor Sie die Firewall wieder aktivieren, versuchen Sie, sich mit folgendem Befehl bei Ihrem VPS anzumelden:
```
ssh <server-user>@<tailscale-ip>
```
Bei herkömmlichem OpenSSH fügen Sie diesem Befehl `-i ~/.ssh/<ssh-key>` hinzu, wenn Sie einen benutzerdefinierten Schlüssel-Dateinamen verwenden.

Wenn diese Anmeldung funktioniert, aktivieren Sie UFW erneut und überprüfen Sie dessen Status. `ufw reload` allein aktiviert eine deaktivierte Firewall nicht wieder:
```
sudo ufw enable
sudo ufw status verbose
```

Dies stellt einen privaten Verwaltungspfad bereit, ist jedoch keine Garantie dafür, dass der VPS ausschließlich über das Tailnet erreichbar ist. Um SSH ausschließlich über das Tailnet zu ermöglichen, überprüfen Sie zunächst nach der Aktivierung von UFW eine neue Verbindung, entfernen Sie dann die öffentliche SSH-Regel mit `sudo ufw delete allow 22/tcp` und prüfen Sie, ob noch andere öffentliche SSH-Zugriffe bestehen, einschließlich IPv6. Behalten Sie den von Coolify benötigten SSH-Zugriff vom Container zum Host bei. Der öffentliche HTTP/HTTPS-Zugriff kann für bewusst veröffentlichte Dienste weiterhin verfügbar bleiben.

## Installation von Coolify
Der nächste Schritt ist die Installation unserer Plattform [Coolify](https://coolify.io/) mithilfe des offiziellen Skripts:
```
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | sudo bash
```

Coolify muss außerdem vom Container aus auf den SSH-Dienst des Hosts zugreifen können. Überprüfen Sie die Docker-Netzwerke, um die relevanten Subnetze und die Gateway-Adresse des Hosts zu ermitteln:
```
sudo docker network inspect bridge
sudo docker network inspect coolify
```

Die Ausgabe sollte in etwa so aussehen:
```
[
    {
        "Name": "coolify",
        "Id": "6103a5aa95d01b69bba2d662f8b1d66645a8ab909ff45499e905e5b36302cf57",
        "Created": "2025-02-01T18:09:18.815150113+01:00",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv4": true,
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": {},
            "Config": [
                {
                    "Subnet": "10.0.1.0/24",
                    "Gateway": "10.0.1.1"
                }
            ]
        },
.
.
.
```
Notieren Sie sich die `Subnet` der `IPAM -> Config` der Bridge und von Coolify.
Beachten Sie den Wert `Gateway` des `IPAM -> Config` der Bridge.
Für die SSH-Verbindung vom Container zum Host können die Regeln auf den TCP-Port 22 beschränkt werden, anstatt jeden Port am Host-Gateway zuzulassen. Passen Sie diese Beispiele an die tatsächlichen Quellnetzwerke und die von Coolify verwendete Host-Adresse an:
``` shell
sudo ufw allow proto tcp from <subnet-bridge> to <gateway-bridge> port 22
sudo ufw allow proto tcp from <subnet-coolify> to <gateway-bridge> port 22
```

{{< alert type="warning" title="Docker ports and UFW" >}}
Von Docker veröffentlichte Ports können die normalen eingehenden Regeln von UFW umgehen. Diese Gateway-Regeln erlauben SSH-Verbindungen vom Container zum Host; sie schützen das Coolify-Dashboard oder andere veröffentlichte Container-Ports nicht vor öffentlichem Zugriff. Bevor Sie die Installation nach außen freigeben, beschränken Sie die Verwaltungsports mithilfe einer Provider-Firewall, verifizierter, ausschließlich privater Docker-Port-Bindungen oder Docker-kompatibler Firewall-Regeln. Überprüfen Sie sowohl die IPv4- als auch die IPv6-Erreichbarkeit von außerhalb des Tailnets. Siehe [Docker's firewall documentation](https://docs.docker.com/engine/network/packet-filtering-firewalls/#docker-and-ufw).
{{< /alert >}}

Sobald der Zugriff auf das Dashboard eingeschränkt ist, schließen Sie die Installation ab, indem Sie von innerhalb des Tailnets auf die Coolify-Weboberfläche unter `http://<tailscale-ip>:8000` zugreifen. Erstellen Sie umgehend das Admin-Konto: Wer zuerst die erste Registrierungsseite aufruft, kann die Instanz beanspruchen. Überprüfen Sie anschließend die Verbindung zum Localhost-Server von Coolify.


## Syncthing-Bereitstellung in Coolify

1. Erstellen Sie in Coolify ein neues Projekt (z. B. `VPS production`).
2. Fügen Sie Ressourcen hinzu (z. B. `Syncthing`) 
{{< figure src="./coolify_new_resource.png" width="900" alt="Add Coolify resource" >}}
3. Konfiguration > Allgemein > Legen Sie den Servicenamen und die Service-URL fest.
{{< figure src="./coolify_syncthing_configuration.png" width="900" alt="Syncthing configuration" >}}
4. Stellen Sie den Container bereit.  
5. Greifen Sie über die Dienst-URL auf Syncthing zu.

Diese Schritte beschreiben die Bereitstellung und den Zugriff auf die Web-Benutzeroberfläche, nicht die vollständige Synchronisationskonfiguration. Die HTTP-Dienst-URL unterstützt das Syncthing-Synchronisationsprotokoll nicht. Die direkte Synchronisation verwendet in der Regel `22000/TCP` und `22000/UDP` mit geeigneten Docker-Portzuordnungen und Firewall-Regeln für das jeweilige Netzwerk oder stützt sich auf eine Relay-Verbindung. Für die Konfiguration und die synchronisierten Daten werden persistente Volumes benötigt; schützen Sie die Admin-Benutzeroberfläche durch Authentifizierung und Zugriffsbeschränkungen.

## Später: Nutzung des VPS als kontrollierter öffentlicher Ingress

Später nutzte ich diesen VPS und die Tailscale-Foundation, um ausgewählte Dienste aus einem privaten k3s-Homelab zu veröffentlichen, ohne mein Heimnetzwerk zu öffnen: [Expose K3s Services from a Tailscale-Protected Homelab via a VPS](https://blog.matschcode.de/en/notes/self-hosting/expose-k3s-services-via-vps/).