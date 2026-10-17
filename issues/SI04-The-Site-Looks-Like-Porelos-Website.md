# SI04 — The Site Looks Like Porelo's Website

**Status:** Estimated.
**Size:** S - one stylesheet and the logo copied in by `build/assemble.py`, the theme's palette, fonts and logo in its
configuration, one check of the built pages in the site workflow, and tests of what it writes; no contract another
repository reads.

**What must be true.** The documentation site looks like Porelo's website (porelo.ai), so that a reader moving from
the website to the documentation sees one product: the same dark colours, accents, fonts, logo and surfaces.

- **Dark only.** The light scheme and its toggle are gone.
- **The theme's own navigation stays**: tabs, sidebar, search, the top button. The website's one-page parts - the
  thumb bar at the bottom on phones, the scroll reveal, the typing terminal - are not carried over.
- **Nothing is loaded from another origin.** The theme's web fonts are switched off, as the website loads none.

## The website's design

As the website's stylesheet defines it:

    --bg: #05050c;        --bg-2: #0b0b1a;
    --text: #e8ecff;      --muted: #9aa3c7;
    --cyan: #00f0ff;      --magenta: #ff2bd6;   --lime: #b6ff3b;   --amber: #ffb020;
    --glass: rgba(18, 20, 40, 0.55);   --glass-strong: rgba(14, 16, 34, 0.78);
    --glass-border: rgba(140, 160, 255, 0.14);
    --glow-cyan: 0 0 0 1px rgba(0, 240, 255, 0.35), 0 0 24px rgba(0, 240, 255, 0.25);
    --radius: 18px;  --radius-sm: 12px;
    --font: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --mono: ui-monospace, "JetBrains Mono", "SFMono-Regular", Menlo, Consolas, "Liberation Mono", monospace;

- **Links** are cyan, underlined on hover with `text-underline-offset: 3px`. **Inline `code`** is lime, in the mono
  font. **Focus** is `2px solid` cyan with a 3px offset.
- **Glass surfaces** are `--glass` behind `backdrop-filter: blur(18px) saturate(160%)`, with a 1px `--glass-border`
  and `box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 10px 40px rgba(0,0,0,0.35)`. Where `backdrop-filter` is not
  supported, they use `--glass-strong`.
- **Code blocks** look like the code in the website's cards: `background: rgba(0,0,0,0.35)`,
  `border: 1px dashed rgba(182,255,59,0.25)`, radius 10px.
- **The small heading above a section** ("eyebrow") is `600 0.8rem` mono, magenta, with `letter-spacing: 0.08em`.
- **The background** is a faint cyan grid, in perspective:
  `linear-gradient(rgba(0,240,255,0.07) 1px, transparent 1px)` both ways at `44px`. It is optional, and never at the
  cost of reading.
- **The logo** is the website's `logo.svg` (sha256 `7261bf0b946329210eded9d4af3f2f7b02a09a740653120ad8af12fa14153491`),
  used as the header logo and the favicon. It is one inline SVG, a gradient from cyan to magenta on `#07070f`, and it
  references nothing outside itself.

## Plan

Read in today's code (2026-10-17): `assemble.py` writes the site's `mkdocs.yml` from `THEME` (`build/assemble.py:121`),
in `assemble()` (`:295`). `THEME` holds Material with two palettes, light (`default`) and dark (`slate`), and a toggle
between them. It carries no stylesheet of its own and no
logo. Every page requests `fonts.googleapis.com` today (Roboto and Roboto Mono): they are the theme's default
fonts, which it loads unless told not to.

- **The theme in `THEME`:**
  - one palette, `scheme: slate`, without a toggle;
  - `font: false`, which ends the request to `fonts.googleapis.com`: the stacks above come from the stylesheet,
    and nothing is fetched;
  - `logo` and `favicon` naming the copied `logo.svg`.
- **One stylesheet in this repository**, `build/porelo.css`, copied by `assemble.py` into the site's `docs/` and named
  under `extra_css`. It maps the website's variables onto Material's own (`--md-default-bg-color`,
  `--md-default-fg-color` and its lighter steps, `--md-primary-fg-color`, `--md-accent-fg-color`,
  `--md-typeset-a-color`, `--md-code-bg-color`, `--md-code-fg-color`, `--md-text-font`, `--md-code-font`). It then
  styles the header, tabs, sidebar and search as glass, code blocks as dashed cards, and focus, links and the grid as
  above.
- **The logo** in this repository as `build/logo.svg`, copied beside the stylesheet: the site takes it from no other
  repository. Both are copied in `assemble()` as `EARLY_BIRD` is today (`:245`).
- **The check of the built pages**, `build/same_origin.py`: reads every `.html` under the built site and fails naming
  each `src` or `href` that leaves the site, except `<a href>`. It runs in `.github/workflows/site.yml` right after the
  strict build (`:109`).
- If [SI01](README.md#si01) (Zensical) comes first, the same stylesheet carries over: it reads the same variables.

**Contrast, computed from the values above** (WCAG ratio, against `--bg` / `--bg-2`): text 17.3 / 16.6, muted
8.2 / 7.8, cyan 14.4 / 13.8, magenta 6.4 / 6.1, lime 16.8 / 16.1, amber 11.1 / 10.7. Every one passes AA for body
text (4.5).

## How it is tested

- **Red first:** `test_the_site_is_built_with_material_tabs_search_and_both_schemes` (`tests/test_assemble.py:134`)
  asserts two schemes today; it is changed to assert one `slate` palette with no toggle, `font: false` and
  `extra_css`, and seen red before `THEME` changes.
- **Tests of what `assemble.py` writes:**
  - one palette and no toggle;
  - `font: false`;
  - `extra_css` naming the stylesheet;
  - the stylesheet and the logo present in `docs/`, the logo at the sha256 above.
- **A test of the stylesheet:** every colour pair it sets for text on a background, computed against the background,
  passes WCAG AA.
- **No other origin:** `build/same_origin.py`, run in the site workflow after the strict build, refuses any `src` or
  `href` in the built pages that leaves the site, except links a reader follows (`<a href>`). Its own test reads two
  small pages, one with a stylesheet from another origin (red) and one with only an outside `<a href>` (green).
- **By eye:** the built site at a phone width and a desktop width, every tab.
- The existing tests and the strict build stay green.

## Acceptance

- The published site is dark only, in the website's colours, fonts and logo, with its navigation as today.
- No built page loads anything from another origin; every text colour passes WCAG AA against its background.
