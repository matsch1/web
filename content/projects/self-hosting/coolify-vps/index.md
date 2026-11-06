---
title: "Setup Coolify platform on your VPS"
slug: "coolify-vps-setup"
date: 2025-05-10
description: "Server hardening and deploy first app with Coolify."
ShowToc: true
TocOpen: true
draft: false
cover:
  image: "editorial-cover.webp"
  alt: "coolify-vps-setup"
  caption: ""
  relative: true
tags:
  - server
  - syncthing
  - coolify
  - tailscale
source_lang: en
translation_lock: true
homepage:
  title: "Coolify on my own VPS"
  teaser: "Hardening a VPS and deploying a first app with Coolify: practical lessons from my setup."
  section: engineering
project:
  status: active
---

{{< alert type="info" title="" >}}
The VPS is still running, although most of its services have changed since the initial setup.
{{< /alert >}}

## UPDATE NOV 2026
The VPS is still running, although it now hosts different services than those initially set up.
Coolify has proven reliable, requiring little to no maintenance.
The server currently serves three main purposes:
- Hosting Syncthing, the only service that has remained unchanged.
- Hosting my Hermes Agent.
- Acting as a reverse proxy for my homelab via Tailscale.

## Introduction
Self-hosting has become an excellent way to gain hands-on experience with server administration, DevOps tooling, and modern deployment platforms. My goal was to provision a virtual private server (VPS), secure it properly, and use it as a small but flexible platform for deploying backend components that support my app development workflow.

Typical workloads include lightweight services such as PocketBase for backend storage, Unleash for feature flags, and automation tools like n8n. I also planned to use the server for file synchronization via Syncthing and other experiments over time.

To streamline deployment and app lifecycle management, I chose Coolify, an open-source PaaS that abstracts container orchestration into a friendly dashboard. This post documents the initial VPS setup, basic hardening steps, Tailscale integration, and deploying the first application.

This is a personal experience report, not a complete or maintained security-hardening guide. The commands illustrate the setup; details may vary with the operating system and Coolify version.

## Server hosting
Choosing the right hosting provider depends on budget, proximity, bandwidth, and support. Coolify lists minimum requirements of 2 CPU cores, 2 GB RAM, and 10 GB of free disk space on a supported Linux distribution. Applications and builds need additional resources. After provisioning the instance, note the following:

- Server location and plan  
- Operating system image (e.g., Ubuntu 22.04 LTS)  
- Basic credentials provided by the host  
- Public IP address  

{{< figure src="./netcup_vps.png" width="700" alt="" class="right" >}}

In my case I decided to go with a VPS hosted by [netcup](https://www.netcup.com/de/server/vps).
I started the project using the smallest VPS option `VPS 250 G11s` but later on upgrade to the second option `VPS 500 G11s`.
This costs me about 5€ per month (including private domain) and provides enough ressources for everything I need.

## Server access
### SCP
For the first access it is possible to connect to the server using the server control panel provided by netcup.
The first time you are logged in to the VPS as root user, so the first thing to do is setting up a different user.

### Setup user
``` shell
# Debian systems
adduser <username>
usermod -aG sudo <username>
```

This creates the user, prompt for password, creates the home directory of the user and set basic defaults. The second command is to add the user to the sudo group. With that it is possible to execute commands with elevated user rights using `sudo`.

```
# Switch to new user
sudo su - <server-user>
```

### Get ssh access
For that a ssh key has to be generated on the client machine.

```
ssh-keygen -t ed25519 -C "your_email@example.com"
```

This prompts for name of the key, location and passphrase.
The key can be saved to `~/.ssh/<ssh-key>`. A passphrase is recommended for a personal admin key.
This will create 2 files: `<ssh-key>` and `<ssh-key.pub>`.

To get SSH access to the VPS, create the SSH directory on the server if needed:
```
sudo install -d -m 700 -o <server-user> -g <server-user> /home/<server-user>/.ssh
```

Copy the content of `<ssh-key.pub>` to `/home/<server-user>/.ssh/authorized_keys`. If the file does not exist, create it; otherwise append the key without overwriting existing entries.
You can use `nano` or `vi` as command line text editor to do that.

Pay attention to the user rights of that file.
```
sudo chmod 600 /home/<server-user>/.ssh/authorized_keys
sudo chown <server-user>:<server-user> /home/<server-user>/.ssh/authorized_keys
```

After doing this ssh setup the VPS can be accessed from the client using:
```
ssh -i ~/.ssh/<ssh-key> <server-user>@<server-ip>
```

### Server hardening
To reduce unauthorized access, I focused on SSH authentication and firewall rules.

#### Login restrictions
{{< alert type="warning" title="Danger" >}}
Pay attention! The following settings can break you server access!
{{< /alert >}}

##### SSH only access
Login with password will be forbidden 
{{< alert type="warning" title="Danger" >}}
Pay attention that the ssh login works fine!
{{< /alert >}}
Disable password authentication (edit `/etc/ssh/sshd_config`):

    PasswordAuthentication no
    KbdInteractiveAuthentication no

##### Root access and Coolify
Disabling root SSH login entirely is a common hardening step, but it conflicts with Coolify's standard setup: Coolify uses SSH as `root` to manage the local server. For that setup, allow key-based root login while disabling password-based root login:

    PermitRootLogin prohibit-password

An alternative is a supported non-root Coolify configuration, which needs additional setup and is not covered here. Root key access should be restricted to the required management paths.

{{< alert type="warning" title="Danger" >}}
Keep the current session open and ensure console access is available before changing SSH settings.
{{< /alert >}}

Check any included configuration files in `/etc/ssh/sshd_config.d/` for conflicting settings. Validate and reload the configuration on Debian/Ubuntu:

```sh
sudo sshd -t
# Only reload if validation succeeds:
sudo systemctl reload ssh
```

Test a new key-based connection in a second terminal before closing the original session.

#### Firewall
For better security we want to block all ports we do not need.
For this purpose we use the uncomplicated firewall ([UFW](https://wiki.ubuntu.com/UncomplicatedFirewall)).

{{< alert type="warning" title="Danger" >}}
Before enabling the firewall, check ssh login works fine!
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
The next step was adding a virtual private network (VPN) for private management access. Tailscale provides that network, but installing it does not disable public access: the firewall rules above still allow SSH, HTTP, and HTTPS from the internet.

A very easy to setup, and easy to use VPN is [Tailscale](https://tailscale.com/). It uses WireGuard under the hood to create encrypted point-to-point connections between your devices.

{{< figure src="https://cdn.sanity.io/images/w77i7m8x/production/fab2bfd901de3d58f7f62d35fe9a5107fedc43c1-1360x725.svg?w=3840&q=75&fit=clip&auto=format" width="700" alt="Tailscale">}}


#### Setup
The initial setup included temporarily disabling UFW. This is not normally necessary for Tailscale and leaves host services without UFW protection while it is disabled. Keep a working SSH session and provider console access available:
```
sudo ufw disable
```

For Debian systems easily execute this command on your VPS to install Tailscale:
```
curl -fsSL https://tailscale.com/install.sh | sh
```

#### Starting Tailscale
```
sudo tailscale up --ssh
tailscale ip
```

After starting Tailscale and login to the Tailnet. The second command will print your servers Tailscale-IP.

The `--ssh` flag enables Tailscale SSH, which authenticates through Tailnet identities and SSH policies rather than the personal SSH key configured above. Its access rules are separate from OpenSSH's `sshd_config`, including root-login restrictions. For traditional key-based OpenSSH over Tailscale instead, omit `--ssh` (or disable it with `sudo tailscale set --ssh=false` if already enabled).

The following rule allows incoming host traffic on the Tailscale interface, subject to Tailnet access policies; it does not open a specific Tailscale port:
```
sudo ufw allow in on tailscale0
```

Before reenabling the firewall try to login to your VPS using:
```
ssh <server-user>@<tailscale-ip>
```
For traditional OpenSSH, add `-i ~/.ssh/<ssh-key>` to that command if using a custom key filename.

If this login works, re-enable UFW and check its status. `ufw reload` alone does not re-enable a disabled firewall:
```
sudo ufw enable
sudo ufw status verbose
```

This provides a private management path, not a guarantee that the VPS is accessible only through the Tailnet. To make SSH Tailnet-only, first verify a new connection after enabling UFW, then remove the public SSH rule with `sudo ufw delete allow 22/tcp` and check for other public SSH allowances, including IPv6. Keep Coolify's required container-to-host SSH access in place. Public HTTP/HTTPS access can remain available for deliberately published services.

## Installing Coolify
The next step is to install our platform [Coolify](https://coolify.io/) using the official script:
```
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | sudo bash
```

Coolify also needs to reach the host's SSH service from its container. Inspect the Docker networks to identify the relevant subnets and host gateway address:
```
sudo docker network inspect bridge
sudo docker network inspect coolify
```

The output should result in something like this:
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
Note the `Subnet` of the `IPAM -> Config` of the bridge and Coolify.
Note the `Gateway` of the `IPAM -> Config` of the bridge.
For the container-to-host SSH connection, rules can be restricted to TCP port 22 rather than allowing every port on the host gateway. Adapt these examples to the actual source networks and host address used by Coolify:
``` shell
sudo ufw allow proto tcp from <subnet-bridge> to <gateway-bridge> port 22
sudo ufw allow proto tcp from <subnet-coolify> to <gateway-bridge> port 22
```

{{< alert type="warning" title="Docker ports and UFW" >}}
Docker-published ports can bypass UFW's normal incoming rules. These gateway rules allow container-to-host SSH; they do not protect the Coolify dashboard or other published container ports from public access. Before exposing the installation, restrict management ports using a provider firewall, verified private-only Docker port bindings, or Docker-aware firewall rules. Check both IPv4 and IPv6 reachability from outside the Tailnet. See [Docker's firewall documentation](https://docs.docker.com/engine/network/packet-filtering-firewalls/#docker-and-ufw).
{{< /alert >}}

Once dashboard access is restricted, finish the installation by accessing the Coolify web UI on `http://<tailscale-ip>:8000` from inside the Tailnet. Create the admin account immediately: whoever reaches the initial registration page first can claim the instance. Then validate Coolify's localhost server connection.


## Syncthing Deployment in Coolify

1. In Coolify, create a new project (e.g. `VPS production`).
2. Add resources (e.g. `Syncthing`) 
{{< figure src="./coolify_new_resource.png" width="900" alt="Add Coolify resource" >}}
3. Configuration > General > define service name and service url.
{{< figure src="./coolify_syncthing_configuration.png" width="900" alt="Syncthing configuration" >}}
4. Deploy the container.  
5. Access Syncthing via service url.

These steps describe deploying and accessing the web UI, not the complete synchronization setup. The HTTP service URL does not carry Syncthing's sync protocol. Direct synchronization typically uses `22000/TCP` and `22000/UDP`, with suitable Docker port mappings and firewall rules for the intended network, or relies on relay connectivity. Persistent volumes are needed for configuration and synchronized data; protect the admin UI with authentication and restricted access.

## Later: using the VPS as a controlled public ingress

I later used this VPS and Tailscale foundation to publish selected services from a private k3s homelab without opening my home network: [Expose K3s Services from a Tailscale-Protected Homelab via a VPS](https://blog.matschcode.de/en/notes/self-hosting/expose-k3s-services-via-vps/).
