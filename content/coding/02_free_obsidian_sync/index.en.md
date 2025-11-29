---
title: "Free Obsidian PC Android sync"
date: 2025-01-02
img: img1.webp
description: "Explanation of how I use Syncthing as a free Obsidian Sync"
ShowToc: true
TocOpen: true
draft: false
cover:
  image: "img1.webp"
  alt: "obsidian-sync"
  caption: ""
  relative: true
params:
  ShowPostNavLinks: true
---
![header-image](img1.webp)
Obsidian is a great tool for collecting ideas.

I use it mainly for the following reasons:
- Research
- Collecting information
- Saving some spontaneous ideas

Depending on my actual situation I prefer to use my laptop or my phone.
To always have access to my vaults, regardless of the device I am using, I need to sync the data between my devices. For that purpose Obsidian provides the Sync Plugin. But for this plugin they charge you 4$ a month, which I don't want to spend, if there is another option.

## I found a solution which meets my requirements:
- Crossplatform availability: Linux, Windows and Android
- No manual work: no downloads, no copies, no nothing
- free to use

## What I use now:
- [Syncthing-fork](https://play.google.com/store/apps/details?id=com.github.catfriend1.syncthingandroid) on my android phone
- [Syncthing](https://github.com/syncthing/syncthing) on my windows and linux machine
- Shell script to backup the data in a git repository

## Setup:
- Install syncthing on the devices you want to use Obsidian
- Create folders on every device to store the Obsidian files locally
- Linking the devices using the QR code
- Share the folders (also using QR code)
- Copy your vault into the new directory and open it in Obsidian
- *optional:*
  - create a git repository in your Obsidian directory and backup the files to your github account


## Obsidian Git autobackup

``` bash
#!/bin/bash

git-autopush() {
  REPO_DIR = $1
  cd "$REPO_DIR" || {
    echo "Repository not found: $REPO_DIR"
    exit 1
  }

  # Check if the repository has changes
  if [[ -n $(git status --porcelain) ]]; then
    git add .
    git status

    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    git commit -m "Auto-commit: $TIMESTAMP"

    git push origin "$(git rev-parse --abbrev-ref HEAD)" || {
      echo "Failed to push changes."
      exit 1
    }

    echo "Changes pushed successfully."
  else
    # Check if there are committed changes to push
    LOCAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    if [[ -n $(git rev-list origin/"$LOCAL_BRANCH"..HEAD) ]]; then

      # Push changes
      git push origin "$LOCAL_BRANCH" || {
        echo "Failed to push changes."
        exit 1
      }
      echo "Changes pushed successfully."
    fi

  fi
}

git-autopush $1
```

