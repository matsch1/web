<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

# WEB

<em></em>

<!-- BADGES -->
<!-- local repository, no metadata badges. -->

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/JSON-000000.svg?style=default&logo=JSON&logoColor=white" alt="JSON">
<img src="https://img.shields.io/badge/TOML-9C4121.svg?style=default&logo=TOML&logoColor=white" alt="TOML">
<img src="https://img.shields.io/badge/XML-005FAD.svg?style=default&logo=XML&logoColor=white" alt="XML">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=default&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/GitHub%20Actions-2088FF.svg?style=default&logo=GitHub-Actions&logoColor=white" alt="GitHub%20Actions">
<img src="https://img.shields.io/badge/YAML-CB171E.svg?style=default&logo=YAML&logoColor=white" alt="YAML">

</div>
<br>

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Project Structure](#project-structure)
- [License](#license)

---

## Overview
My website about coding and travel related stuff.
It is build with [Hugo](https://gohugo.io/) and deployed to [GitHub Pages](https://docs.github.com/en/pages) using [GitHub Actions](https://github.com/features/actions).

The website can be found here: [matschweb](https://matsch1.github.io/web/en)

### Coding 
A documentation of stuff I learned during coding.
The topics I am currently working on are:
  - Worfklow optimizations: Syncthing, Obsidian, AI
  - Linux stuff: dotfiles, Shellmaster
  - App development: Flutter

### Travel
Mainly for sharing impressions of my solo travels with friends and family.

## Local development (Dev Container)

The project can be edited in a Docker-based Dev Container. It includes Hugo,
Neovim (using the host's `~/.config/nvim` configuration), LazyGit, OpenCode,
Python, and the tools required by this repository.

### Start the container

Docker and the [Dev Containers CLI](https://github.com/devcontainers/cli) are
required. From the repository root, build and start the container:

```sh
devcontainer up --workspace-folder .
```

To rebuild it after changes to `.devcontainer/`:

```sh
devcontainer up --workspace-folder . --remove-existing-container
```

Open an interactive shell in the running container:

```sh
devcontainer exec --workspace-folder . bash
```

### Commands inside the container

After opening the interactive shell above, run the commands directly:

```sh
# Start the local preview server
hugo server

# Create the static production build in public/
hugo --gc --minify

# Edit the project with the mounted Neovim configuration
nvim .

# Open Git's terminal UI
lazygit

# Start OpenCode (first run prompts for authentication)
opencode
```

It is available at [http://localhost:1313/](http://localhost:1313/).
The Dev Container supplies `--bind 0.0.0.0` and the local base URL
automatically for `hugo server`.
The first build can take several minutes while Hugo processes images; wait
until Hugo reports that the web server is available before opening the URL.

To run the preview server from the host without opening an interactive shell:

```sh
devcontainer exec --workspace-folder . hugo server
```


---

## Features

### Auto Translation 
#### Usage
Follow the steps from GitHub Actions workflow.

Local Debugging:
- Run script ''' ./scripts/translate_markdown.py '''

#### DEEPL API
At the moment the free version of DEEPL api is used for auto translation.

#### Google Translator
At the beginning I used Google Translator for automatic translation. 
It is deprecated but does work with python 3.12.3
For this usecase it is important to use the following python dependencies: requests python-frontmatter langdetect googletrans==4.0.0-rc1.
Python 3.12.3 is included in Ubuntu 24.04 (see workflow).


### Shortcodes
#### Open-Street-Map
Copy geo link from [openstreetmap](https://www.openstreetmap.org/#map=6/51.33/10.45) and insert into shortcode:
''' {{< open-street-map map_title="Flensburg Bahnhof" geo_link="geo:48.1395,6.8174?z=12" >}} '''
Add title manually.

#### Komoot
Embed Komoot via the share link of kommoot.
Copy the src link from the embed in to the shortcode:
{{< komoot src="https://www.komoot.com/de-de/tour/2307166457/embed?share_token=aQnymAKsMOlxpwS71nFIKouaHoxZYQvpJC6IoyrL7MZERrNPtB&profile=1" >}}

#### Strava
Copy activity id from browser url and add to shortcode:
{{< strava-activity id="14849684801" title="Packtest für Juli (Hinweg)" distance="104.39 km" elevation="959 hm" time="5h 02m" >}}
Add title, distance, elevation and time manually.

#### Gallery
I use images located in the same directory as the markdown file the shortcode is
used.
The the gallery can be generated like this:
{{< galleries >}}
{{< gallery src="img1.jpg" title="Fahrrad voll beladen" alt="Voll beladenes Reiserad am Straßburger Kanal" >}}
{{< gallery src="img2.jpg" title="Am Straßburger Kanal" alt="Radfahrer am Straßburger Kanal zwischen Bäumen und Wasser" >}}
{{< gallery src="img3.jpg" title="Vogesen" alt="Reiserad vor bewaldeten Hügeln in den Vogesen" >}}
{{< gallery src="img4.jpg" title="Bester Schlafplatz mit Aussicht" alt="Zeltplatz mit Blick über die Landschaft" >}}
{{< /galleries >}}
Add the image name, a short caption (`title`) shown in the lightbox, and a descriptive `alt` text that explains the image context rather than repeating the filename. The first image is the cropped 3:2 lead image; all following images remain uncropped in a one-line, horizontally scrollable strip.

---

## Project Structure

```sh
└── web/
    ├── .github
    │   └── workflows
    ├── README.md
    ├── archetypes
    ├── assets
    ├── content
    ├── hugo.toml
    ├── layouts
    ├── public
    ├── scripts
    │   └── translate_markdown.py
    ├── static
    └── themes
        └── PaperMod
```

---

## License

Web is protected under the [LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

<div align="right">

[![][back-to-top]](#top)

</div>


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square


---
