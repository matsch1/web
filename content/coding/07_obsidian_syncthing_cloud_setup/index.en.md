---
title: "My Obsidian + Syncthing Setup: A Self-Hosted Cloud for Notes, Backups, and More"
date: 2025-09-22
img: img1.png
description: "Use syncthing on a server to create a cross-plattform file exchange for Obsidian notes and more"
ShowToc: true
TocOpen: true
draft: false
---
![header-image](img1.png)
  

There are two kinds of note-takers: those who trust their precious thoughts to the cloud (hello Notion/Google Drive/OneNote people), and those who stare into the abyss and think: *“what if I built my own infrastructure for this?”*  

I belong to the second group.  
Here’s how I turned **Syncthing + Obsidian + a webserver** into a note-syncing, backup-happy, cloud-replacing monster.  

---

## The Core Idea  

- **Server:** a VPS that acts as my “Syncthing master”  
- **Clients:** Linux, Windows, and Android devices, all happily syncing to the server.  
- **Vault:** Obsidian notes live in a single folder. That folder is the source of truth.  

The magic is in Syncthing: every device talks to the server, syncing notes **bi-directionally**. That means I can edit notes anywhere (on my phone while commuting, at my desktop during coding sessions, or on my laptop while pretending to relax on the couch). Within seconds, the changes ripple across all devices.  

The server is both **sync hub** and **backup repository**. So even if a laptop dies or my phone decides to go for a swim, the notes remain safe.  

---

## Why Syncthing?  

Because it’s basically the **anti-cloud cloud**.  

- No accounts, no subscriptions, no vendor lock-in.  
- Runs on everything (Linux, Windows, macOS, Android, even routers if you’re into that).  
- Peer-to-peer magic: devices talk directly if they can, fallback via relay if they can’t.  
- Once set up, it’s “just working.”  
- Easy to setup with **Coolify**

It’s like Dropbox, but nerdier and without the creepy terms of service.  

---

## Obsidian Layer  

Obsidian treats its **vault setup** (themes, plugins, workspace config) as just more files. Which means: once you throw your vault folder into Syncthing, **the entire setup syncs too**.  

That’s right: I can install a plugin on my Linux machine, and seconds later it’s magically available on Windows and Android. My hotkeys, my color scheme, my crazy plugin combos — they all follow me around.  

---

## Extra Features  

This is where it gets fun. I didn’t stop at “just syncing notes.”  

### GitHub Backup  

I run a cron job that pushes the entire vault into a private GitHub repo.  

Why? Because:  
1. **Extra safety net** (never enough backups).  
2. **Version control**: it’s basically git history of my brain.  

### Automated File Handling  

Sometimes, notes get messy. Attachments pile up, screenshots end up in random places.  

Solution: a small Python script (also running via cron) that cleans up and reorganizes things.  
Think of it as a Roomba for my vault.  

---

## Beyond Notes: Syncthing as a Personal Cloud  

Here’s the twist: once you’ve got Syncthing humming along on a VPS, you’ve basically built your own **cloud framework**. Notes are just the start.  

- **Google Drive replacement**: throw in any folder you want synced across devices. Done.  
- **Phone DCIM backup**: my Android dumps new photos straight to the server, even when I’m abroad. They’re instantly safe, without me ever touching “Google Photos”. 
  Pay attention to the disk space of your server. Images take much space then notes.

I like to think of it as: **Syncthing is my cloud OS, the VPS is the data center, and my devices are just clients.**  

---

## TL;DR Setup  

- VPS with Syncthing installed → acts as master and backup hub.  
- Clients: Linux, Windows, Android with Syncthing.  
- Vault folder = synced everywhere.  
- Obsidian config = synced too.  
- Extra spice: GitHub backup, Python scripts, cron jobs.  
- Bonus: Syncthing doubles as Google Drive + photo backup replacement.  

---

## Closing Thoughts  

Most people pay for cloud storage. I prefer paying for a VPS and hacking my own.  
With Syncthing + Obsidian, I get **real-time sync, complete control, no vendor lock-in**, and some extra nerd cred.  

If you’re into self-hosting, data ownership, or just like to tinker with infrastructure, I can’t recommend this combo enough. It’s not just notes — it’s a self-hosted cloud ecosystem.  

