---
ShowToc: true
TocOpen: true
base_hash: e6aade8529b6ff2ad89511cb046472700476bf5d42f86ee2a8b6113a017309f6
cover:
  alt: coolify-vps-setup
  caption: ''
  image: header.png
  relative: true
date: 2025-05-10
description: Server hardening and deploy first app with Coolify.
draft: false
slug: coolify-vps-setup
tags:
- server
- syncthing
- coolify
- tailscale
title: Coolify Plattform auf deinem VPS einrichten
---

Der VPS funktioniert hervorragend, aber das Projekt ist noch nicht abgeschlossen.
    Die Anwendungen, die auf diesem Server laufen, ändern sich mit der Zeit.

## Einleitung
Self-Hosting hat sich zu einer hervorragenden Möglichkeit entwickelt, praktische Erfahrungen mit Serveradministration, DevOps-Tools und modernen Bereitstellungsplattformen zu sammeln. Mein Ziel war es, einen Virtual Private Server (VPS) einzurichten, ihn richtig abzusichern und ihn als kleine, aber flexible Plattform für die Bereitstellung von Backend-Komponenten zu nutzen, die meinen Workflow bei der Anwendungsentwicklung unterstützen.

Zu den typischen Arbeitslasten gehören leichtgewichtige Dienste wie PocketBase für Backend-Storage, Unleash für Feature-Flags und Automatisierungstools wie n8n. Im Laufe der Zeit wollte ich den Server auch für die Dateisynchronisierung über Syncthing und andere Experimente nutzen.

Um die Bereitstellung und die Verwaltung des Lebenszyklus von Anwendungen zu optimieren, entschied ich mich für Coolify, eine Open-Source-PaaS, die die Container-Orchestrierung in einem benutzerfreundlichen Dashboard zusammenfasst. Dieser Beitrag dokumentiert die anfängliche VPS-Einrichtung, grundlegende Härtungsschritte, die Tailscale-Integration und die Bereitstellung der ersten Anwendung.

## Server-Hosting
Die Wahl des richtigen Hosting-Anbieters hängt vom Budget, der Nähe, der Bandbreite und dem Support ab. Jeder Anbieter, der eine moderne Linux-Distribution und mindestens 2 GB RAM anbietet, wird Coolify bequem betreiben können. Beachten Sie nach der Einrichtung der Instanz die folgenden Punkte:

- Serverstandort und -plan
- Betriebssystem-Image (z. B. Ubuntu 22.04 LTS)
- Grundlegende Anmeldeinformationen des Hosts
- Öffentliche IP-Adresse

{{< figure src="./netcup_vps.png" width="700" alt="" class="right" >}}

In meinem Fall habe ich mich für einen VPS entschieden, der von [netcup](https://www.netcup.com/de/server/vps) gehostet wird.
Ich habe das Projekt mit der kleinsten VPS-Option `VPS 250 G11s` begonnen, bin aber später auf die zweite Option `VPS 500 G11s` aufgestiegen.
Das kostet mich etwa 5€ pro Monat (inklusive privater Domain) und bietet genug Ressourcen für alles, was ich brauche.

## Server-Zugang
## SCP
Für den ersten Zugang ist es möglich, sich über das Server Control Panel von netcup mit dem Server zu verbinden.
Beim ersten Mal ist man auf dem VPS als Root-Benutzer eingeloggt, also muss man als erstes einen anderen Benutzer einrichten.

### Benutzer einrichten
``` shell
# Debian systems
adduser <username>
usermod -aG sudo <username>
```

Damit wird der Benutzer angelegt, das Passwort abgefragt, das Home-Verzeichnis des Benutzers erstellt und die grundlegenden Standardeinstellungen festgelegt. Mit dem zweiten Befehl wird der Benutzer zur Gruppe sudo hinzugefügt. Damit ist es möglich, mit `sudo` Befehle mit erweiterten Benutzerrechten auszuführen.

```
# Switch to new user
sudo su - <server-user>
```

### ssh-Zugang erhalten
Dazu muss auf dem Client-Rechner ein ssh-Schlüssel erzeugt werden.

```
ssh-keygen -t ed25519 -b 4096 -C "your_email@example.com"
```

Es wird nach dem Namen des Schlüssels, dem Speicherort und der Passphrase gefragt.
Der Schlüssel sollte auf `/home/$USER/.ssh/<ssh-key>` gespeichert werden. Die Passphrase kann leer bleiben.
Es werden 2 Dateien erstellt: <ssh-key> und <ssh-key.pub>.

Um ssh-Zugang zum VPS zu erhalten, muss der Inhalt von <ssh-key.pub> nach `/home/<server-user>/.ssh/autorized_keys` kopiert werden. Wenn die Datei nicht vorhanden ist, muss sie erstellt werden.
Dazu können Sie `nano` oder `vi` als Kommandozeilen-Editor verwenden.

Achten Sie auf die Benutzerrechte für diese Datei.
```
sudo chmod 600 /home/<server-user>/.ssh/authorized_keys
sudo chown <server-user>:<server-user> /home/<server-user>/.ssh/authorized_keys
```

Nach dieser ssh-Einrichtung kann vom Client aus auf den VPS zugegriffen werden:
```
ssh <server-user>@<server-ip>
```

### Server-Härtung
Um sicherzustellen, dass sich in Zukunft nur Sie auf dem Server einloggen können, härten wir den Server mit zwei Dingen.

#### Login-Beschränkungen
{{< alert type="warning" title="Danger" >}}
Bitte beachten Sie! Die folgenden Einstellungen können Ihren Serverzugang unterbrechen!
{{< /alert >}}

##### Nur SSH-Zugang
Login mit Passwort wird verboten
{{< alert type="warning" title="Danger" >}}
Achten Sie darauf, dass der ssh-Login funktioniert!
{{< /alert >}}
Deaktivieren Sie die Passwort-Authentifizierung (bearbeiten Sie `/etc/ssh/sshd_config`):

    PasswordAuthentication no

##### Kein Root-Login
Keine Anmeldung als root-Benutzer möglich.
{{< alert type="warning" title="Danger" >}}
Achten Sie darauf, dass die Anmeldung mit Ihrem Server-Benutzer funktioniert!
{{< /alert >}}
Deaktivieren Sie den Root-Login (bearbeiten Sie `/etc/ssh/sshd_config`):

    PermitRootLogin no


#### Firewall
Für eine bessere Sicherheit wollen wir alle Ports blockieren, die wir nicht benötigen.
Zu diesem Zweck verwenden wir die unkomplizierte Firewall ([UFW](https://wiki.ubuntu.com/UncomplicatedFirewall)).

{{< alert type="warning" title="Danger" >}}
Bevor Sie die Firewall aktivieren, überprüfen Sie, ob der ssh-Login funktioniert!
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
Der nächste Schritt auf unserem Weg zu einem kugelsicheren VPS-Server ist die Einrichtung eines virtuellen privaten Netzwerks (VPN). Dadurch wird sichergestellt, dass nur Personen in diesem Netzwerk auf den VPS zugreifen können.

Ein sehr einfach einzurichtendes und einfach zu benutzendes VPN ist [Tailscale](https://tailscale.com/). Es verwendet WireGuard unter der Haube, um verschlüsselte Punkt-zu-Punkt-Verbindungen zwischen Ihren Geräten herzustellen.

{{< figure src="https://cdn.sanity.io/images/w77i7m8x/production/fab2bfd901de3d58f7f62d35fe9a5107fedc43c1-1360x725.svg?w=3840&q=75&fit=clip&auto=format" width="700" alt="Tailscale">}}


#### Einrichtung
Vor der Einrichtung von Tailscale ist es empfehlenswert, die Firewall zu deaktivieren, um nicht vom VPS ausgesperrt zu werden.
```
sudo ufw disable
```

Für Debian-Systeme führen Sie einfach diesen Befehl auf Ihrem VPS aus, um Tailscale zu installieren:
```
curl -fsSL https://tailscale.com/install.sh | sh
```

#### Tailscale starten
```
sudo tailscale up --ssh
tailscale ip
```

Nach dem Start von Tailscale und der Anmeldung im Tailnet. Der zweite Befehl gibt die Tailscale-IP Ihres Servers aus.

Nun müssen die Tailscale-Ports zum UFW hinzugefügt werden:
```
sudo ufw allow in on tailscale0
```

Bevor Sie die Firewall wieder aktivieren, versuchen Sie, sich auf Ihrem VPS einzuloggen mit:
```
ssh <server-user>@<tailscale-ip>
```
Wenn dieser Login funktioniert, kann die Firewall neu gestartet werden.
```
sudo ufw reload
sudo service ssh restart
```

Damit haben Sie nun einen VPS, der ziemlich sicher ist.
Der Login funktioniert nur von einem Client im Tailnet mit dem <server-key> und dem <server-user>.

## Coolify installieren
Der nächste Schritt ist die Installation unserer Plattform [Coolify](https://coolify.io/) mit Hilfe des offiziellen Skripts:
```
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

Bevor wir weitermachen, müssen wir die Netzwerkkommunikation von Coolify mit der Firewall erlauben.
Dazu müssen wir die Netzwerke der Docker Bridge und von Coolify überprüfen, indem wir diese Befehle ausführen:
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
Beachten Sie die `Subnet` der `IPAM -> Config` der Bridge und von Coolify.
Beachten Sie die `Gateway` der `IPAM -> Config` der Brücke.
Mit diesen drei Werten können die neuen Firewall-Regeln hinzugefügt werden:
``` shell
sudo ufw allow from <subnet-bridge> to <gateway-bridge>
sudo ufw allow from <subnet-coolify> to <gateway-bridge>
sudo ufw reload
sudo service ssh restart
```

Schließen Sie die Installation ab, indem Sie vom Tailnet aus auf die Coolify-Web-UI auf `http://<tailscale-ip>:8000` zugreifen und den Anweisungen folgen.


## Syncthing-Bereitstellung in Coolify

1. Erstellen Sie in Coolify ein neues Projekt (z. B. `VPS production`).
2. Fügen Sie Ressourcen hinzu (z. B. `Syncthing`).
{{< figure src="./coolify_new_resource.png" width="900" alt="Add Coolify resource" >}}
3. Konfiguration > Allgemein > Dienstname und Dienst-URL festlegen.
{{< figure src="./coolify_syncthing_configuration.png" width="900" alt="Syncthing configuration" >}}
4. Stellen Sie den Container bereit.  
5. Zugriff auf Syncthing über den Dienst url.