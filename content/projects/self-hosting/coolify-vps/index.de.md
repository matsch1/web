---
ShowToc: true
TocOpen: true
base_hash: 180adb904f21efe3e6e8d8cc061798f3c37812d2f665b805e9e7c48d86fcd2af
cover:
  alt: coolify-vps-setup
  caption: ''
  image: header.png
  relative: true
date: 2025-05-10
description: Server-Absicherung und Bereitstellung der ersten App mit Coolify.
draft: false
homepage:
  featured: false
  section: engineering
  state: evergreen
project:
  status: paused
slug: coolify-vps-setup
tags:
- server
- syncthing
- coolify
- tailscale
title: Richte die Coolify-Plattform auf deinem VPS ein
---

{{< alert type="info" title="" >}}
Der VPS läuft hervorragend, aber das Projekt ist noch nicht abgeschlossen.
Die auf diesem Server ausgeführten Anwendungen ändern sich im Laufe der Zeit.
{{< /alert >}}

## Einleitung
Selbsthosting hat sich zu einer hervorragenden Möglichkeit entwickelt, praktische Erfahrungen mit Serveradministration, DevOps-Tools und modernen Bereitstellungsplattformen zu sammeln. Mein Ziel war es, einen Virtual Private Server (VPS) einzurichten, ihn ordnungsgemäß abzusichern und ihn als kleine, aber flexible Plattform für die Bereitstellung von Backend-Komponenten zu nutzen, die meinen App-Entwicklungs-Workflow unterstützen.

Zu den typischen Workloads gehören leichtgewichtige Dienste wie PocketBase für den Backend-Speicher, Unleash für Feature-Flags und Automatisierungstools wie n8n. Außerdem plante ich, den Server im Laufe der Zeit für die Dateisynchronisation über Syncthing und andere Experimente zu nutzen.

Um das Deployment und das App-Lebenszyklusmanagement zu optimieren, entschied ich mich für Coolify, eine Open-Source-PaaS, die die Container-Orchestrierung in einem benutzerfreundlichen Dashboard abstrahiert. Dieser Beitrag dokumentiert die anfängliche VPS-Einrichtung, grundlegende Sicherheitsmaßnahmen, die Tailscale-Integration und das Deployment der ersten Anwendung.

## Server-Hosting
Die Wahl des richtigen Hosting-Anbieters hängt von Budget, Standortnähe, Bandbreite und Support ab. Jeder Anbieter, der eine moderne Linux-Distribution und mindestens 2 GB RAM anbietet, kann Coolify problemlos ausführen. Beachten Sie nach der Bereitstellung der Instanz Folgendes:

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
ssh-keygen -t ed25519 -b 4096 -C "your_email@example.com"
```

Sie werden zur Eingabe des Namens des Schlüssels, des Speicherorts und der Passphrase aufgefordert.
Der Schlüssel sollte unter `/home/$USER/.ssh/<ssh-key>` gespeichert werden. Die Passphrase kann leer bleiben.
Dadurch werden zwei Dateien erstellt: `<ssh-key>` und `<ssh-key.pub>`.

Um SSH-Zugriff auf den VPS zu erhalten, muss der Inhalt von `<ssh-key.pub>` in `/home/<server-user>/.ssh/autorized_keys` kopiert werden. Falls die Datei nicht existiert, muss sie angelegt werden.
Dazu kannst du `nano` oder `vi` als Texteditor in der Befehlszeile verwenden.

Achten Sie dabei auf die Benutzerrechte dieser Datei.
```
sudo chmod 600 /home/<server-user>/.ssh/authorized_keys
sudo chown <server-user>:<server-user> /home/<server-user>/.ssh/authorized_keys
```

Nach dieser SSH-Konfiguration kann vom Client aus über folgenden Befehl auf den VPS zugegriffen werden:
```
ssh <server-user>@<server-ip>
```

### Server-Absicherung
Um sicherzustellen, dass sich in Zukunft nur noch Sie auf dem Server anmelden können, sichern wir den Server mithilfe von zwei Maßnahmen ab.

#### Anmeldebeschränkungen
{{< alert type="warning" title="Danger" >}}
Achtung! Die folgenden Einstellungen können den Zugriff auf Ihren Server unterbrechen!
{{< /alert >}}

##### Nur SSH-Zugriff
Die Anmeldung mit Passwort wird untersagt. 
{{< alert type="warning" title="Danger" >}}
Achten Sie darauf, dass die SSH-Anmeldung einwandfrei funktioniert!
{{< /alert >}}
Passwortauthentifizierung deaktivieren (bearbeite `/etc/ssh/sshd_config`):

 PasswordAuthentication no

##### Keine Anmeldung als Root
Eine Anmeldung als Root-Benutzer ist nicht möglich.
{{< alert type="warning" title="Danger" >}}
Achte darauf, dass die Anmeldung mit deinem Server-Benutzer einwandfrei funktioniert!
{{< /alert >}}
Root-Anmeldung deaktivieren (bearbeiten `/etc/ssh/sshd_config`):

 PermitRootLogin no


#### Firewall
Aus Sicherheitsgründen möchten wir alle Ports blockieren, die wir nicht benötigen.
Dazu verwenden wir die unkomplizierte Firewall ([UFW](https://wiki.ubuntu.com/UncomplicatedFirewall)).

{{< alert type="warning" title="Danger" >}}
Bevor du die Firewall aktivierst, überprüfe, ob die SSH-Anmeldung einwandfrei funktioniert!
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
Der nächste Schritt auf unserem Weg zu einem absolut sicheren VPS-Server ist die Einrichtung eines virtuellen privaten Netzwerks (VPN). Dadurch wird sichergestellt, dass nur Personen in diesem Netzwerk auf den VPS zugreifen können.

Ein sehr einfach einzurichtendes und benutzerfreundliches VPN ist [Tailscale](https://tailscale.com/). Es nutzt im Hintergrund WireGuard, um verschlüsselte Punkt-zu-Punkt-Verbindungen zwischen Ihren Geräten herzustellen.

{{< figure src="https://cdn.sanity.io/images/w77i7m8x/production/fab2bfd901de3d58f7f62d35fe9a5107fedc43c1-1360x725.svg?w=3840&q=75&fit=clip&auto=format" width="700" alt="Tailscale">}}


#### Einrichtung
Vor der Einrichtung von Tailscale wird empfohlen, die Firewall zu deaktivieren, um nicht aus dem VPS ausgesperrt zu werden.
```
sudo ufw disable
```

Auf Debian-Systemen führen Sie einfach diesen Befehl auf Ihrem VPS aus, um Tailscale zu installieren:
```
curl -fsSL https://tailscale.com/install.sh | sh
```

#### Tailscale starten
```
sudo tailscale up --ssh
tailscale ip
```

Starten Sie Tailscale und melden Sie sich bei Tailnet an. Der zweite Befehl gibt die Tailscale-IP Ihres Servers aus.

Nun müssen die Tailscale-Ports zur UFW hinzugefügt werden:
```
sudo ufw allow in on tailscale0
```

Bevor Sie die Firewall wieder aktivieren, versuchen Sie, sich mit folgendem Befehl bei Ihrem VPS anzumelden:
```
ssh <server-user>@<tailscale-ip>
```
Wenn diese Anmeldung problemlos funktioniert, kann die Firewall neu gestartet werden.
```
sudo ufw reload
sudo service ssh restart
```

Damit verfügen Sie nun über einen VPS, der ziemlich sicher ist.
Die Anmeldung funktioniert nur von einem Client im Tailnet mit dem `<server-key>` und dem `<server-user>`.

## Coolify installieren
Der nächste Schritt ist die Installation unserer Plattform [Coolify](https://coolify.io/) mithilfe des offiziellen Skripts:
```
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

Bevor wir fortfahren, müssen wir die Netzwerkkommunikation von Coolify in der Firewall zulassen.
Dazu müssen wir die Netzwerke der Docker-Bridge und von Coolify mit den folgenden Befehlen überprüfen:
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
Notieren Sie sich die Werte `Subnet` der Bridge und `IPAM -> Config` von Coolify.
Beachten Sie den Wert `Gateway` der Bridge im Vergleich zu `IPAM -> Config`.
Mit diesen drei Werten können die neuen Firewall-Regeln hinzugefügt werden:
``` shell
sudo ufw allow from <subnet-bridge> to <gateway-bridge>
sudo ufw allow from <subnet-coolify> to <gateway-bridge>
sudo ufw reload
sudo service ssh restart
```

Schließen Sie die Installation ab, indem Sie von innerhalb des Tailnets auf die Coolify-Weboberfläche unter `http://<tailscale-ip>:8000` zugreifen und den Anweisungen folgen.


## Syncthing-Bereitstellung in Coolify

1. Erstellen Sie in Coolify ein neues Projekt (z. B. `VPS production`).
2. Fügen Sie Ressourcen hinzu (z. B. `Syncthing`) 
{{< figure src="./coolify_new_resource.png" width="900" alt="Add Coolify resource" >}}
3. Konfiguration > Allgemein > Servicenamen und Service-URL festlegen.
{{< figure src="./coolify_syncthing_configuration.png" width="900" alt="Syncthing configuration" >}}
4. Den Container bereitstellen.  
5. Über die Service-URL auf Syncthing zugreifen.

## Später: Nutzung des VPS als kontrollierten öffentlichen Ingress

Später habe ich diesen VPS und die Tailscale-Foundation genutzt, um ausgewählte Dienste aus einem privaten k3s-Homelab zu veröffentlichen, ohne mein Heimnetzwerk zu öffnen: [Expose K3s Services from a Tailscale-Protected Homelab via a VPS](https://blog.matschcode.de/en/notes/self-hosting/expose-k3s-services-via-vps/).