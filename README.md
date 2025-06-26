My website build with hugo.

Content is split in coding and travel related stuff.
Published to: [https://matsch1.github.io/web/](https://matsch1.github.io/web/)

# Coding 
Main source of stuff I post to [dev.to](https://dev.to).

# Travel
Mainly for sharing impressions of my solo travels with friends and family.

# Setup / Background
## Auto Translation
Google Translator is used for translation with python. It is deprecated but
does work with python 3.12.3
For this usecase it is important to use the following python dependencies: requests python-frontmatter langdetect googletrans==4.0.0-rc1.
Python 3.12.3 is included in Ubuntu 24.04 (see workflow).

- Local debugging with Python 3.12.3 installed via pyenv
- Install required packages
- Run script ''' ./scripts/translate_markdown.py '''

## Shortcodes
### Open-Street-Map
Copy geo link from [openstreetmap](https://www.openstreetmap.org/#map=6/51.33/10.45) and insert into shortcode:
''' {{< open-street-map map_title="Flensburg Bahnhof" geo_link="geo:48.1395,6.8174?z=12" >}} '''
Add title manually.

### Komoot
Embed Komoot via the share link of kommoot.
Copy the src link from the embed in to the shortcode:
{{< komoot src="https://www.komoot.com/de-de/tour/2307166457/embed?share_token=aQnymAKsMOlxpwS71nFIKouaHoxZYQvpJC6IoyrL7MZERrNPtB&profile=1" >}}

### Strava
Copy activity id from browser url and add to shortcode:
{{< strava-activity id="14849684801" title="Packtest für Juli (Hinweg)" distance="104.39 km" elevation="959 hm" time="5h 02m" >}}
Add title, distance, elevation and time manually.

### Gallery
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
