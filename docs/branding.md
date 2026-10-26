# matschcode identity

The header mark is `static/branding/matschcode-jutland.svg`: a real-route signet
beside Manrope **500** (`matsch`) / **800** (`code`), with a 0.13 em word gap.
Letterforms are vector outlines, not browser text; there are no font downloads.
The accessible home link is named `matschcode`; the SVG itself is decorative.

## Route provenance

The signet derives from the 13 recorded stages of the Jutland trip in 2023,
retrieved from the owner's Intervals.icu activity streams. North-up orientation
and proportions are retained. Each stage was simplified independently using
Douglas–Peucker with a 10 km tolerance, matching the approved silhouette.
Day boundaries remain separate; no missing sections have been invented.
The final adjustment rounds each interior corner with a quadratic segment,
cutting at most 12% of the shorter adjacent edge. Straight runs and the overall
angular silhouette remain. The stroke width is 8 on a 156-unit-high canvas.
Only normalized drawing geometry is included here, never original GPS data.

## Usage

- Header: inline SVG, `currentColor`, 232 px wide (196 / 164 px on narrow screens).
- Standalone signet: `branding/jutland-route.svg`.
- Favicons / touch icon: route on a warm light tile for contrast in either theme.
- Social fallback: `branding/matschcode-jutland-social.webp`, 1200 × 630.
- Existing illustration files are preserved, but no longer configured as branding.

## Font license

Manrope: Copyright 2018 The Manrope Project Authors,
licensed under SIL Open Font License 1.1. A copy is distributed at
`static/branding/Manrope-OFL.txt`.
Upstream: https://github.com/googlefonts/manrope
License source: https://github.com/google/fonts/blob/main/ofl/manrope/OFL.txt

## Reproduction

The SVG exports themselves are the editable production masters. They contain
no raster images, executable elements, external resources, or coordinate data.
Keep the 500/800 lettering, word gap, stage boundaries and route orientation
when making future exports. The compact header inherits the existing masthead
text color in both themes; do not replace it with an external SVG image if it
needs to keep inheriting `currentColor`.
