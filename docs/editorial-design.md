# Editorial design

The blog remains Hugo + PaperMod. No theme update, URL migration, external font request, new plugin or production deployment is part of this change.

## Components and content

- Homepage: authentic photographic masthead, one concise introduction, active lifecycle projects first, a single feature card, compact engineering/outdoor recommendations, recent articles and a small archive.
- Interior pages: compact masthead; existing reading width, galleries, maps and original article bodies remain unchanged.
- Explicit `Projekt` / `Beitrag` (`Project` / `Article`) labels. A page is a project when it is a project section overview or has canonical project metadata; being stored below `/projects/` alone does not make a travel chapter a project.
- `project.status` remains the lifecycle source. `homepage.state` remains editorial curation, not a lifecycle status. Article cards and article headers do not display project statuses.
- Navigation and the existing `/notes/` landing page say `Beiträge` / `Articles`. Paths remain unchanged; no new Notes content type is introduced.
- Optional `homepage.title` and `homepage.teaser` provide localized card copy without rewriting article titles or bodies. Manually reviewed localized editorial copy uses the repository's existing `translation_lock` support.
- Headings use locally hosted Manrope; the font license is shipped under `static/fonts/OFL.txt`. Warm light surfaces, forest/charcoal dark surfaces, restrained green accents, reduced-motion handling and visible focus styles are in `assets/css/extended/z-editorial.css`.
- Feature and compact covers pass distinct `sizes` hints to the existing responsive-image pipeline. Technical covers retain their entire artwork rather than cropping diagram labels. Outdoor photos retain photographic crops. Text-only cards have a single-column fallback.

## Verification

Use the Hugo version pinned in the workflows, install `requirements.txt`, then:

```sh
export HUGO_BIN=/path/to/hugo
"$HUGO_BIN" --gc --minify
python3 scripts/prepare_root_artifacts.py public
python3 scripts/verify_site.py public
python3 -m unittest discover -s tests -v
```

The ordinary test suite includes rendered Hugo regression tests when Hugo is discoverable through `HUGO_BIN` or `PATH`. The optional real-browser tests require Playwright and a Chromium executable. Serve a freshly built `public` directory locally, then run in a separate shell:

```sh
python3 -m http.server 8876 --bind 127.0.0.1 --directory public
```

```sh
export EDITORIAL_BASE_URL=http://localhost:8876
export BROWSER_EXECUTABLE=/path/to/chromium
python3 -m unittest discover -s tests -v
```

Browser coverage: German/English homepage, project listing, article listing and travel article; 320/390/768/1280 pixel viewports; light/dark schemes; no horizontal page overflow; compact interior masthead; loaded Manrope; exactly one homepage lead. A cover-removal fixture protects the text-only card fallback at mobile and desktop widths.

Publishing remains a separate, explicitly authorized operation. A successful local build does not publish the site.
