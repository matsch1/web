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

# Coding 
A documentation of stuff I learned during coding.
The topics I am currently working on are:
  - Worfklow optimizations: Syncthing, Obsidian, AI
  - Linux stuff: dotfiles, Shellmaster
  - App development: Flutter

# Travel
Mainly for sharing impressions of my solo travels with friends and family.


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
{{< gallery src="img1.jpg" title="Fahrrad voll beladen" >}}
{{< gallery src="img2.jpg" title="Am Strassbourger Kanal" >}}
{{< gallery src="img3.jpg" title="Vogesen" >}}
{{< gallery src="img4.jpg" title="Bester Schlafplatz mit Aussicht" >}}
{{< /galleries >}}
Add image name and title manually.

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
