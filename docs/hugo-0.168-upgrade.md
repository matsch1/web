# Reviewed Hugo / PaperMod upgrade

## Scope and rollback

- Hugo Extended: 0.164.0 → 0.168.0 in both workflows.
- PaperMod: `154d006e0182dfc7da38008323976b02e6bfab4a` → `26523e0fd837f965d08e320c9dde83700ad15649`.
- No content, translations, local layout overrides, publish triggers or deployment settings changed.
- Roll back by reverting this upgrade commit (generator and theme together).

## Intervening release audit

Sources: upstream release notes for [0.165.0](https://github.com/gohugoio/hugo/releases/tag/v0.165.0), [0.166.0](https://github.com/gohugoio/hugo/releases/tag/v0.166.0), [0.167.0](https://github.com/gohugoio/hugo/releases/tag/v0.167.0), [0.168.0](https://github.com/gohugoio/hugo/releases/tag/v0.168.0), plus the complete PaperMod commit-range diff.

- **0.165:** Tailwind removed from default exec allowlist; old deprecations removed; parent-directory symlink handling tightened; resource transformation chaining and minifier/image dependencies changed. This site does not invoke Tailwind. The production build resolves all current template calls and resources without warnings.
- **0.166:** Glob engine rewritten (malformed patterns now fail; `**/` still requires a slash); symlinked theme mount roots dropped; Node tool symlinks constrained; remote fetches reject private resolved addresses and ignore environment proxies by default; Org content denied by default. No custom glob mounts, Org input, Node asset processing or GetRemote calls were found in the site's configuration/layouts. Existing builds require no security-policy relaxation. Return semantics changed (valued return only in partials), auto-derived titles containing `/` now form one slug segment, and PNG/filter cache versions changed. Local valued return is inside a partial; exact output-route comparison detects slug changes. KaTeX CSS must be >=0.18.4 for ToMath HTML output; this site has no ToMath/KaTeX integration.
- **0.167:** Branch-page slugs now cascade; numeric comparisons are exact; summaries balance open lists/quotes and can grow; user table render hooks take priority. Explicit baseURL remains configured, no root cleanDestinationDir migration is needed, no local table hook exists. Sass/ESBuild fallback reads and theme symlinks are confined; no policy relaxation needed. All generated HTML/XML/JSON routes are compared, not just counts. Summary content can legitimately differ; byte-identical HTML is not claimed.
- **0.168:** Theme module replacements ignored; animated image decoding/first-frame behavior changes and memory checks; generator-tag ordering, JS/HTML minifier escaping and Go security fixes. No theme replacements are configured; responsive-image tests and a complete production build exercise current images. Inline scripts also receive browser smoke checks.
- **PaperMod:** minimum Hugo 0.158; language APIs migrate to Label/Locale/Direction/Name; Scratch state becomes local variables; cover resolution is lazy; WebP no longer gated on Extended; header page URL is hoisted; TOC regex and code/table CSS change. Local base/header/head/cover overrides already use current APIs and remain intentionally untouched. Existing navigation, responsive-image, gallery and deferred-provider tests remain active. Full-output canonical/hreflang/OG/Twitter/robots comparison is unchanged across all 204 HTML routes.

## CI correction and regression protection

PR CI previously ran rendering tests before installing Hugo; some tests used a machine-local fallback binary and others could skip. The Hugo setup now precedes the suite and `HUGO_BIN=$(command -v hugo)` selects the reviewed binary. Tests lock both workflow pins, the theme commit and this ordering; rendered regression tests protect the DE/EN custom masthead/menu and unique social tags. Version and CI-order tests were observed failing before the associated changes.

## Local verification

Evidence directory for this run: `/tmp/web-upgrade-Ez7Nx6/evidence/` (not committed).

- Original baseline suite rerun independently: 79 tests pass; the prior baseline log contained a missing-venv error and is not treated as a pass.
- Candidate: complete unittest suite, production `hugo --gc --minify --environment production`, root-artifact assembly and `scripts/verify_site.py`.
- Baseline/candidate: 204 HTML, 67 XML, 2 JSON routes each, no additions/removals; canonical/hreflang/OG/Twitter/robots tags unchanged on every HTML file. Hugo reports 103 pages per language.
- Existing Chromium headless shell reused; prior `browser-install.log` was empty, not evidence of an installation failure. No browser reinstall.
- 16 browser cases: DE/EN home, search, article and gallery, at 1440px and 390px. Navigation/masthead, no horizontal overflow, theme toggle, search results and localized OG URLs pass; no uncaught page errors. Screenshots and JSON results are in evidence.
- Browser requests for the canonical host were served from the local candidate; Giscus/Komoot requests were blocked. This does not certify external-provider availability, all browser engines, all content interactions, or live performance. No translation API calls, merge or deployment performed.

Reproduce: install requirements, initialize submodules, set `HUGO_BIN` to Hugo Extended 0.168.0, then run `HUGO_BIN="$HUGO_BIN" python -m unittest discover -s tests -v`; run the production build and root/SEO scripts shown in PR CI.
