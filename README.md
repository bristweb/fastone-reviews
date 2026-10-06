# FASTONE Pro Paint — reviews widget

A static, database-free collection of every public review of **[FASTONE® Pro Premades](https://www.fastonepro.com/)** (the six-color heavy body acrylic skin tone paint set by Knoxville artist Heather Wolfe), plus an embeddable reviews widget in the style of Elfsight. Everything is plain files served by GitHub Pages: no server, no database, no third-party widget service.

- **Live widget:** https://bristweb.github.io/fastone-reviews/
- **Iframe page:** https://bristweb.github.io/fastone-reviews/embed.html
- **All reviews as JSON:** https://bristweb.github.io/fastone-reviews/data/reviews/index.json
- **schema.org JSON-LD:** https://bristweb.github.io/fastone-reviews/data/reviews/schema.json

The code is generic (it is the widget from [bristweb/heather-wolfe-art-reviews](https://github.com/bristweb/heather-wolfe-art-reviews), plus Amazon/Etsy support in the scripts). Everything specific to FASTONE (reviews, platforms, links, colors, fonts, icons, text) lives in `data/`, so the repo can be [reused for another site](#reuse-for-another-site) by swapping that one folder.

## Contents

1. [Embed on your site](#embed-on-your-site)
   - [JavaScript embed (preferred)](#javascript-embed-preferred)
   - [Iframe embed (alternative)](#iframe-embed-alternative)
   - [Google Sites and other fixed-height boxes](#google-sites-and-other-fixed-height-boxes)
2. [Options and customization](#options-and-customization)
3. [Reuse for another site](#reuse-for-another-site)
4. [Folder layout](#folder-layout)
5. [Review data and schema](#review-data-and-schema)
6. [Adding and updating reviews](#adding-and-updating-reviews)
7. [Weekly pull (monitoring)](#weekly-pull-monitoring)
8. [Card order](#card-order)
9. [AI summary card](#ai-summary-card)
10. [Structured data (JSON-LD)](#structured-data-json-ld)
11. [Header behavior](#header-behavior)
12. [Privacy and presentation](#privacy-and-presentation)
13. [Technical details](#technical-details)
14. [Credits](#credits)

---

## Embed on your site

### JavaScript embed (preferred)

Paste this one tag where the widget should appear:

```html
<script src="https://bristweb.github.io/fastone-reviews/assets/js/reviews-widget.js" defer></script>
```

The widget renders right where the tag is. The script works out the repo address from its own URL. It then loads the stylesheets (`assets/css/reviews-widget.css` and `data/theme/theme.css`), the settings (`data/config.json`) and the reviews (`data/reviews/index.json`), and inserts the widget immediately before the `<script>` element. `defer`, `async`, or neither all work.

Options go on the script tag:

```html
<script src="https://bristweb.github.io/fastone-reviews/assets/js/reviews-widget.js" defer
        data-layout="grid" data-platform="amazon" data-limit="12"></script>
```

- The widget renders directly in your page, so it sizes itself naturally and needs no resize script.
- It stays invisible until its font and first layout are ready, then fades in once, with no font swap or layout jump.
- **Several widgets on one page:** use one script tag per widget, each in its own spot with its own options (for example a grid of Amazon reviews and a carousel of the latest six). The data and CSS are downloaded only once.
- **It fills the width it's given, up to 1200px, inside any page builder.** That includes containers that shrink their content to fit: Framer/Squarespace code blocks, centered flex columns, `text-align:center` blocks, inline-block, `fit-content`, floated, and absolutely positioned parents. It never causes horizontal scrolling.
- The widget's internal classes all start with `rw-`, its font has its own family name, and a small reset keeps common host styles (line height, image borders, text alignment) from leaking in.

**Rendering somewhere other than the script's position** (optional), for example when the script has to go in `<head>` or a site-wide footer:

```html
<!-- a) point the script at an element -->
<script src="https://bristweb.github.io/fastone-reviews/assets/js/reviews-widget.js" defer data-target="#reviews"></script>
<div id="reviews"></div>

<!-- b) or mark one or more elements; each can carry its own options -->
<script src="https://bristweb.github.io/fastone-reviews/assets/js/reviews-widget.js" defer></script>
<div data-reviews-widget data-layout="grid" data-platform="etsy"></div>
<div data-reviews-widget data-limit="6"></div>
```

How the script decides where to render:

1. If it has `data-target`, it renders into that element (any CSS selector). The element's own `data-` options override the script's.
2. Otherwise, if the page has `[data-reviews-widget]` elements that no script has filled yet, it fills all of them. Their own `data-` options override the script's.
3. Otherwise, it renders in place, just before its own tag. A script placed in `<head>` with no target renders at the end of `<body>`.

Mount points are chosen only by position, `data-target`, or the `data-reviews-widget` attribute, never by class name. Don't mix in-place tags and `data-reviews-widget` elements on one page; if you need both, give each script a `data-target`.

If your site builder loads scripts in a way that hides the script's own URL (rare, e.g. as an ES module), add `data-base="https://bristweb.github.io/fastone-reviews/"` to the script tag.

### Iframe embed (alternative)

Use this when your site builder only accepts iframes, or when you want the widget fully isolated from your page's CSS:

```html
<iframe id="reviews-widget" src="https://bristweb.github.io/fastone-reviews/embed.html"
        title="Reviews" loading="lazy" scrolling="no" style="width:100%;border:0;height:420px"></iframe>
<script>
  // auto-resize the iframe to the widget's height
  addEventListener('message', function (e) {
    if (e.data && e.data.type === 'reviews-widget-height')
      document.getElementById('reviews-widget').style.height = e.data.height + 'px';
  });
</script>
```

Options go in the query string: `embed.html?layout=grid&platform=amazon&limit=12`. Without the resize script, set a fixed height (the carousel is about 410px tall at desktop widths), or add `fixed-height=true` so the widget fits whatever height you give the iframe (see [the next section](#google-sites-and-other-fixed-height-boxes)).

`index.html` and `embed.html` are the same bare page, with no page chrome and a transparent background.

### Google Sites and other fixed-height boxes

Some site builders put embedded code in a box whose height you set and the code can't change. Google Sites is the common example: *Insert → Embed → Embed code* places your HTML in a sandboxed iframe on `atari-embeds.googleusercontent.com` (with `sandbox="allow-scripts allow-popups allow-forms allow-same-origin allow-popups-to-escape-sandbox allow-downloads allow-modals allow-storage-access-by-user-activation"`, as seen in fastonepro.com's page source). You set its height by dragging the box in the editor. Nothing inside the box can resize it, and anything taller than the box is cut off.

For boxes like that, the widget has a few independent [fitting options](#per-embed-options). This combination suits Google Sites:

```html
<script src="https://bristweb.github.io/fastone-reviews/assets/js/reviews-widget.js"
        data-fixed-height="true" data-arrows="inside" data-overflow="hidden"
        data-hover-lift="false" data-focus-ring="inside"></script>
```

In Google Sites: *Insert → Embed → Embed code*, paste the snippet, *Next*, *Insert*. Then stretch the box to the full width of the section and drag it to about **420px** tall.

- `data-fixed-height="true"`: the widget fills the box's full height and fits inside it. The header stays on top and the cards take the remaining height. A long review scrolls inside its own card. In short boxes the header compacts further (see [Header behavior](#header-behavior)). The widget never tries to resize the box (it sends no height messages).
- `data-arrows="inside"`: the carousel arrows sit inside the widget's edges instead of overhanging them by 8px.
- `data-overflow="hidden"`: nothing paints outside the widget, horizontally or vertically.
- `data-hover-lift="false"`: cards don't rise 2px on hover, so their top edge can't be cut off.
- `data-focus-ring="inside"`: keyboard focus outlines are drawn inside the tabs, the button, and the arrows.

| Box height | Result |
|---|---|
| above 460px | full header, roomy cards |
| about 420px (recommended) | one-row header without "Excellent" / "Based on"; the whole snippet shows on desktop widths |
| 300-400px | smaller score, stars, and text; longer snippets scroll inside their card |

**Tested** in Chrome with a simulated Google Sites iframe (the sandbox above, and again without `allow-same-origin`, which gives the frame an opaque origin), at heights of 300, 400, 460 and 500px and widths of 400, 800 and 1200px. In every case nothing was cut off and the page inside the box never scrolled. The arrows paged through the cards, the font and data loaded, and clicking a card opened the review in a new tab. The same results held with *Embed → By URL* and `https://bristweb.github.io/fastone-reviews/embed.html?fixed-height=true&arrows=inside&overflow=hidden&hover-lift=false&focus-ring=inside`.

- **New tabs:** cards and "Write a review" are `target="_blank" rel="noopener"` links. Inside a sandboxed iframe, opening them needs `allow-popups`. Google Sites also grants `allow-popups-to-escape-sandbox`, so the review page opens as a normal tab.
- **Fonts and data:** the stylesheet, fonts and JSON come from GitHub Pages, which sends `Access-Control-Allow-Origin: *`. They load even from an opaque-origin sandbox.
- **No auto-resize:** the box keeps the height you set. The widget adapts to that height and to whatever width the box has, including on phones.
- **Structured data:** the JSON-LD goes into the embed's own iframe document, not into the Google Sites page.

The same options work in any fixed-height container: a `<div style="height:400px">` around the script tag, or a fixed-height iframe of `embed.html` without the resize script. With `data-fixed-height`, the widget fills its parent element when the parent has a definite height. Otherwise it fills the window from its own top edge down, minus the page's bottom margin.

---

## Options and customization

### Per-embed options

| Attribute (JS embed: script tag or target element) | Query param (iframe / host page) | Values | Default |
|---|---|---|---|
| `data-layout` | `layout` | `carousel` (one scrolling row with arrows) or `grid` (all cards, wrapping) | `display.layout` in `data/config.json` (`carousel`) |
| `data-platform` | `platform` | `all`, or a platform key from `data/config.json` (`amazon`, `etsy`) | `all` |
| `data-limit` | `limit` | maximum number of cards (`0` = no limit) | `0` |
| `data-base` | n/a | repo root URL, ending in `/` | worked out from the script URL |
| `data-summary` | `summary` | `off` hides the [AI summary card](#ai-summary-card) | shown (`display.show_summary`) |
| `data-schema` | n/a | `off` skips injecting the [JSON-LD](#structured-data-json-ld) into the page | injected (`schema.enabled`) |
| **Fitting options** | | | |
| `data-fixed-height` | `fixed-height` | `true`: fill the full height of the parent element (or, if the parent has no definite height, of the window below the widget) and fit everything inside it: the header stays on top, the cards take the remaining height, long text scrolls inside its card, and the header compacts in short boxes. No height messages are sent to a parent frame. `false`: the widget is as tall as its content | `display.fixed_height` (`false`) |
| `data-overflow` | `overflow` | `clip`: the arrows' 8px overhang is clipped sideways so it can't cause horizontal page scroll. `visible`: the arrows overhang the widget edge (the bare pages use this). `hidden`: nothing paints outside the widget in any direction | `display.overflow` (`clip`) |
| `data-arrows` | `arrows` | `outside` (overhang the edges by 8px), `inside` (within the edges), or `off` (no arrows; swiping and scrolling still work) | `display.arrows` (`outside`) |
| `data-hover-lift` | `hover-lift` | `true`: cards rise 2px on hover and focus. `false`: they stay put (only the border changes) | `display.hover_lift` (`true`) |
| `data-focus-ring` | `focus-ring` | `outside`: focus outlines are drawn 2px outside the tabs, button, and arrows. `inside`: drawn inside them, so a box edge can't cut them off | `display.focus_ring` (`outside`) |
| `data-cards` | `cards` | the most cards shown side by side: carousel `1`-`3` (narrow widths still show fewer, as usual), grid `1`-`4`. `0` = automatic (carousel up to 4; grid as many 270px columns as fit) | `display.cards` (`0`) |
| `data-padding` | `padding` | space around the widget, in px | `display.padding` (`6`) |

Query parameters on the page that hosts the widget override the `data-` attributes (this applies to every widget on that page). For every option that has a `display` key, the order is: query parameter, then `data-` attribute, then `display` in `data/config.json`, then the built-in default. The two on/off options take `true` / `false` (also `1` / `0`, `on` / `off`, `yes` / `no`), and a bare `data-fixed-height` means `true`. Each fitting option works on its own; none depends on another.

The platform tabs still let visitors switch filters. The header's rating and review count always follow the selected tab.

### Site-wide settings: `data/config.json`

| Key | What it controls |
|---|---|
| `business.name`, `business.website` | the business this repo is for (reference) |
| `platforms` | one entry per platform, in tab order: `name`, `icon` (repo path), `write_url` (the "Write a review" link when that tab is active), `page_url`, `card_link` (`"review"` = link each card to its individual review; `"page"` = link to `page_url`), optional `invert_icon_when_active` (makes a dark icon white on the active tab) |
| `default_write_platform` | which platform's `write_url` the button uses on the "All" tab |
| `display.layout` | default layout |
| `display.snippet_chars` | snippet length in characters (`0` = full text) |
| `display.abbreviate_last_names` | `true`: "Isabel W." and surnames in the snippet shown as initials; `false`: full names |
| `display.max_same_platform_run`, `display.diversity_window_days` | card-order diversity (see [Card order](#card-order)) |
| `display.date_locale`, `display.date_options` | date formatting (`Intl.DateTimeFormat` locale and options) |
| `display.font_timeout_ms` | how long to wait for the webfont before showing the fallback face |
| `display.show_rating_only_reviews` | `false` (default): reviews with no text are counted in the header but get no card. `true`: they get a card with no text element |
| `display.show_summary` | `true` (default): show `data/summary.json` as the first card in "All reviews"; `false`: never |
| `display.fixed_height`, `display.overflow`, `display.arrows`, `display.hover_lift`, `display.focus_ring`, `display.cards`, `display.padding` | site-wide defaults for the [fitting options](#per-embed-options): `false`, `"clip"`, `"outside"`, `true`, `"outside"`, `0`, `6`. A `data-` attribute or query parameter overrides them per embed |
| `schema.enabled`, `schema.type`, `schema.max_reviews`, `schema.extra` | JSON-LD built into `data/reviews/schema.json` and injected into the page: on/off, the `@type` (here `Product`, see [Structured data](#structured-data-json-ld); `LocalBusiness` for a service business), how many Review items (`0` = all, the default), and extra properties merged into the entity (here `@id`, a product `name`, `description`, `brand`, `manufacturer`, `gtin12`, `category`, `image`, `sameAs`) |
| `rating_labels` | words shown next to the score (`min` average → label) |
| `strings` | every piece of visible or screen-reader text ("Write a review", its short form "Review" for narrow widths, "Based on", "View on {platform}", aria labels, …), with `{placeholders}` |
| `avatars.initials_palette`, `avatars.initials_text_color` | colors of the generated initials avatars (used by the import script) |

### Look and feel: `data/theme/theme.css`

This file holds the `@font-face` rules (fonts in `data/theme/fonts/`) and CSS custom properties on `.rw-host` (inherited by the widget), which the generic stylesheet reads:

| Variable | Used for | FASTONE |
|---|---|---|
| `--rw-font` | font stack (the first family is the one the widget waits for) | `"FASTONE Open Sans"`, metric-matched Arial fallback, system fonts |
| `--rw-letter-spacing` | body letter spacing | `0` |
| `--rw-ink` / `--rw-body` / `--rw-muted` | names and score / review text / dates and "Based on" | `#1f1f1f` / `#424242` / `#5f6368` |
| `--rw-line` / `--rw-line-strong` | borders / tab hover border | `#e4e4e4` / `#cccccc` |
| `--rw-card` | card, header, tab, and arrow background | `#fff` |
| `--rw-tint` | count chips, avatar placeholder, AI summary card | `#f4f4f4` |
| `--rw-accent` / `--rw-accent-2` | active tab, button, links, focus ring, card hover border / hover shade | `#424242` / `#1f1f1f` |
| `--rw-on-accent` / `--rw-on-accent-soft` | text on the accent / count chip on the active tab | `#fff` / `rgba(255,255,255,.18)` |
| `--rw-star` / `--rw-star-off` | filled / empty stars | `#f5b301` / `#dddddd` |
| `--rw-nav-shadow` | carousel arrow shadow | `0 2px 10px rgba(31,31,31,.12)` |
| `--rw-radius` | card and header corner radius | `8px` |
| `--rw-max-width` | widget max width (centered) | `1200px` |

Where these come from: fastonepro.com is a Google Sites page whose theme CSS uses `#1f1f1f` for headings, `#424242` for buttons and body text, `#212121` for paragraphs, `#5f6368` for secondary UI, `#cccccc` rules, `#f7f7f7` / `#f4f4f4` section tints and white, with headings in uppercase **Oswald** and body text in **Open Sans**. The site is deliberately monochrome, so the only colors in the widget are the star gold (the widget default; stars need a color) and the Amazon and Etsy marks. Besides the variables, `theme.css` sets the score, the rating label ("EXCELLENT") and the AI-summary label in uppercase Oswald to match the site headings, and starts the Oswald download while the widget waits for Open Sans so the header never repaints.

On a page that already uses the JS embed you can also override any of these in your own CSS, e.g. `html .rw-root{--rw-accent:#8a2be2}` (the `html` prefix makes it win over the theme file, which is loaded after your CSS).

---

## Reuse for another site

The widget code (`assets/`, `index.html`, `embed.html`, `scripts/`, the workflow) contains nothing specific to FASTONE. To run it for another business:

1. **Duplicate the repo** (use it as a template or copy it) and enable GitHub Pages (branch `main`, root).
2. **Replace `data/`:**

   | Path | Replace with |
   |---|---|
   | `data/config.json` | the business name and site, each platform's name, icon, write-a-review URL, and page URL, strings (any language), display options, and the initials-avatar palette |
   | `data/theme/theme.css` + `data/theme/fonts/` | the site's fonts (`@font-face`) and colors (`--rw-*` variables). Any family name works; list it first in `--rw-font` |
   | `data/icons/` | one SVG per platform key (current set: Amazon, Etsy, plus Instagram, YouTube and website icons for the linked profiles) |
   | `data/sources.json` | the platforms the business is listed on: `scrape_url` or `scrape_urls` (what the pull script scrapes) and `review_page_url` (fallback link) per review platform, plus optional filters: Amazon `asins`, Etsy `listing_ids` (import only those products), Google `featured_on_website_review_ids` |
   | `data/reviews/` | empty it (keep the folder) |
   | `data/summary.json` | delete it (no summary card) or write one for the new reviews |
   | `data/images/reviewers/` | empty it (keep the folder) |

3. **Collect reviews:** run the [weekly pull](#weekly-pull-monitoring) with the `--all` flag, or add review files by hand. Then commit. The workflow rebuilds `data/reviews/index.json`.
4. **Update the URLs** in this README (embed snippets, links).

The importer understands Google, Yelp, Facebook, Zola, Amazon (`junglee/amazon-reviews-scraper`) and Etsy (`astravalabs/etsy-reviews-scraper`) scraper output; the pull script only touches platforms that `data/sources.json` marks `reviews: true`. Any other platform works in the widget if it has an entry in `config.json`, an icon, and review files (added by hand, or with a small converter added to `scripts/import_reviews.py`).

---

## Folder layout

```
data/                              EVERYTHING SITE-SPECIFIC (swap this folder to reuse the repo)
  config.json                      business, platforms (names, icons, write/page URLs, card links), strings, display options
  theme/theme.css                  @font-face + CSS custom properties (colors, radius, font stack)
  theme/fonts/                     self-hosted Open Sans + Oswald (OFL, see OFL-*.txt)
  icons/                           platform logos: amazon.svg, etsy.svg (+ instagram, youtube, website; see Credits)
  sources.json                     every platform fastonepro.com links to: scrape URLs, ASINs/listing ids, reported counts, non-review links
  reviews/                         one JSON file per review: <platform>-<yyyy-mm-dd>-<first-name>-<last-initial>.json
  reviews/index.json               GENERATED: every review merged + summary (do not edit by hand)
  reviews/schema.json              GENERATED: schema.org JSON-LD (Product + AggregateRating + Review items)
  summary.json                     AI-generated summary shown as the first card in "All reviews"
  images/reviewers/                downloaded reviewer avatars (or generated initials SVGs)
assets/                            GENERIC WIDGET CODE
  js/reviews-widget.js             loads data/config.json + data/reviews/index.json + summary + CSS, renders the widget, injects the JSON-LD
  css/reviews-widget.css           layout and behavior; reads the --rw-* variables from the theme
index.html, embed.html             bare widget pages (no chrome, transparent, noindex): both safe to iframe
scripts/build-index.mjs            validates data/reviews/*.json, writes data/reviews/index.json + schema.json (Node, no dependencies)
scripts/import_reviews.py          raw scraper output -> review files (new only by default) + avatar download
scripts/pull_reviews.py            pull helper: Apify inputs/imports for Amazon + Etsy (and Google/Yelp/Facebook/Zola if listed), build, summary check
.github/workflows/build-index.yml  rebuilds and commits index.json + schema.json when data/reviews/, config.json or the build script change
```

A static site can't list a folder, so the widget reads the generated `data/reviews/index.json` instead.

---

## Review data and schema

| Platform | Reviews stored | Platform-reported | Source page |
|---|---|---|---|
| Amazon | 12 (every written review) | 4.8 ★ · 20 ratings, 12 with text (79% 5★, 21% 4★) | https://www.amazon.com/product-reviews/B0D2LXC354 (ASIN B0D2LXC354) |
| Etsy | 1 | 5.0 ★ · 1 review on the listing | https://www.etsy.com/listing/1872977093#reviews |

fastonepro.com links to exactly one product on each marketplace: Amazon ASIN **B0D2LXC354** ("Buy On Amazon", linked twice, once with an affiliate tag) and Etsy listing **1872977093** in the HeatherWolfeArt shop ("Buy on Etsy"). It also links to Faire (wholesale; the brand has **0** retailer reviews), a "Buy Local" Google Maps link to Jerry's Artarama Knoxville (a store that stocks FASTONE; its reviews are about the store, so they are not collected), Instagram, YouTube, heatherwolfeart.com, a Drive template, and the USPTO trademark record. All of them are listed in [`data/sources.json`](data/sources.json) with what was checked.

**Amazon gap:** Amazon counts 20 ratings, but 8 of them are star-only ratings with no text. Amazon never lists those individually (no name, date or id), so they can't be stored or shown; the widget and JSON-LD use the 12 written reviews (average 4.75, shown as 4.8). Amazon shows a default silhouette for these reviewers (the scraper returns `avatar: null`), so their avatars are generated initials. Amazon has no public seller replies on reviews (`owner_reply` is always `null`). 2 of the 12 are **Amazon Vine** reviews (Daytona S., Joe), flagged `amazon_vine: true`; Amazon gives Vine reviewers the product free and labels their reviews.

**Etsy:** the shop has 3 reviews in total; only Merlyn's (2025-10-21) is for the FASTONE listing. The other two are for Heather Wolfe Art paintings/prints and are skipped by the importer (`listing_ids` in `sources.json`). Etsy has no per-review URL, so `review_url` is the listing's reviews section. Merlyn's avatar and profile link come from the listing page's review markup (the actor doesn't return them).

One file per review in `data/reviews/`:

```jsonc
{
  "id": "amazon-bb1142ef5057",            // stable: <platform>-<sha1(platform_review_id)[:12]>
  "platform": "amazon",                    // a platform key from data/config.json
  "platform_review_id": "R1AS3YUWI1ZYPI",  // the platform's own review id (Etsy: transaction id)
  "reviewer_name": "Hannah Hall",          // full name as shown on the platform (widget shows "Hannah H.")
  "reviewer_profile_url": "https://www.amazon.com/gp/profile/amzn1.account.…",
  "reviewer_image": "data/images/reviewers/amazon-2024-08-07-hannah-h.svg",  // downloaded copy or generated initials (repo path)
  "reviewer_image_source_url": null,       // where the avatar came from (may expire), or null
  "rating": 5,                             // 1-5
  "text": "full review text",              // complete, verbatim
  "date": "2024-08-07T12:00:00Z",          // ISO 8601, UTC. Amazon and Etsy only give a calendar day: stored at 12:00 UTC
  "review_url": "https://www.amazon.com/gp/customer-reviews/R1AS3YUWI1ZYPI",  // individual review (Etsy: listing #reviews)
  "owner_reply": null,                     // the seller's public reply {text, date}, or null
  "collected_at": "2026-10-06T02:30:35Z",
  "updated_at": "…",                       // set when an existing review is refreshed (--update)
  "source": "apify",                       // how it was collected: 'apify' or 'direct'
  // product and purchase details:
  "item_reviewed": {                       // Amazon: title, asin, variant_asin, variant, url; Etsy: title, listing_id, url
    "title": "FASTONE Acrylic Skin Tone Paint Set - 6 Pack Pro Premades",
    "asin": "B0D2LXC354", "variant_asin": "B0D2LXC354", "variant": null,
    "url": "https://www.amazon.com/dp/B0D2LXC354"
  },
  "verified_purchase": true,               // Amazon "Verified Purchase"; Etsy: always true (only buyers can review)
  "verified_purchase_source": "…",         // Etsy: why (the transaction id)
  // optional, platform-specific:
  "title": "Absolute LIFE CHANGER.",       // Amazon review title
  "amazon_vine": true,                     // Amazon Vine review
  "helpful_votes": 2,                      // Amazon "N people found this helpful"
  "reviewed_in": "Reviewed in the United States on August 7, 2024",
  "country": "United States",
  "amazon_user_id": "AGPUTVM3C2PMCD2FPQQW2MFNVKBA",
  "review_image_urls": ["https://m.media-amazon.com/images/I/….jpg"],  // photos attached to the review
  "etsy_shop": "heatherwolfeart", "etsy_shop_id": 5453283
}
```

`data/reviews/index.json` holds every full record plus `file` (source path) and `has_text`, sorted newest first. It also has a `summary` with counts and average ratings per platform.

## Adding and updating reviews

**By hand:**

1. Create `data/reviews/<platform>-<yyyy-mm-dd>-<first>-<initial>.json` following the schema (copy an existing file).
2. Put the avatar in `data/images/reviewers/` with the same stem, and set `reviewer_image` to that path.
3. Commit to `main`.

The *Build reviews index* Action then validates every file, commits a refreshed `data/reviews/index.json` and `schema.json`, and Pages redeploys (about a minute). To check locally, run `node scripts/build-index.mjs`.

**From scraper output:** `python3 scripts/import_reviews.py --amazon .pull/amazon.json --etsy .pull/etsy.json --source apify` writes files for **new** reviews only. Add `--update` to also refresh existing ones; they keep their file names, avatars, and `collected_at`. Avatars are downloaded (never hotlinked). If a platform has no photo, an initials SVG is generated in the `config.json` palette. Reviews of other ASINs / listings are skipped when `sources.json` lists `asins` / `listing_ids`. (`--google`, `--yelp`, `--facebook` and `--zola` also work, for sites that use them.)

## Weekly pull (monitoring)

Free, direct methods are used wherever they work; neither platform has one, so both use Apify. What to scrape comes from `scrape_urls` in `data/sources.json`.

| Platform | Method | Actor | Input (date window added automatically) | Price |
|---|---|---|---|---|
| Amazon | Apify | `junglee/amazon-reviews-scraper` (Apify's own) | `{"productUrls":[{"url":"https://www.amazon.com/dp/B0D2LXC354"}],"maxReviews":100,"includeGdprSensitive":true,"sort":"recent","filterByRatings":["allStars"],"reviewsCutoffDate":"<YYYY-MM-DD>"}` | $0.006/review + $0.0013/review with a date filter |
| Etsy | Apify | `astravalabs/etsy-reviews-scraper` | `{"shops":["heatherwolfeart"],"reviewsSort":"Recency","maxReviews":50,"maxTotalResults":1000}` (shop-wide, no date filter; the importer keeps listing 1872977093 only) | $0.004/review |

Why not direct:

- **Amazon:** the product page shows the rating summary (4.8, 20 ratings) but renders reviews client-side; review pages (`/product-reviews/…`, `/gp/customer-reviews/…`, `/portal/customer-reviews/…`) redirect to Sign in.
- **Etsy:** etsy.com is behind DataDome (403 to plain fetches).

`includeGdprSensitive` is needed for reviewer names and profile links.

**Free-plan limit:** on Apify's free plan `junglee/amazon-reviews-scraper` returns at most **10 reviews per run**. A weekly date-windowed run never gets near that. For a full pull (`--all`) the script runs once per star rating (`fiveStar`, `fourStar`, … each ≤ 10 here), which is how all 12 were collected. Apify's smallest per-run cost cap is **$0.50**, so the script defaults to `--max-usd 0.5`.

**Cost of the initial pull (2026-10-05):** 3 Amazon runs (all stars, 5★, 1-4★) returned 10 + 9 + 3 reviews (12 unique) ≈ 22 × $0.006 ≈ **$0.13**; 1 Etsy run, 3 shop reviews ≈ **$0.01**; 1 `apify/web-fetch` of the Etsy listing page (to check its review count and get Merlyn's avatar) ≈ **$0.002**. Total about **$0.15** (free-tier per-event list prices). A weekly run with no new reviews costs about $0.01.

**Weekly run.** Monitoring isn't a GitHub Actions job. It's a scheduled run on the Bristlecone box that uses the Apify connector:

```bash
cd fastone-reviews && git pull
python3 scripts/pull_reviews.py --print-inputs
#   -> for each platform: actor id + input(s) (Amazon date window = newest stored Amazon review - 30 days) + cost cap
#   run each actor with that input (Apify connector call-actor, callOptions.maxTotalChargeUsd 0.5),
#   save the dataset items as .pull/amazon.json and .pull/etsy.json
python3 scripts/pull_reviews.py --from-raw   # imports NEW reviews only (source "apify"), rebuilds index + schema
#   if it prints "SUMMARY STALE": rewrite data/summary.json from .pull/summary_input.txt (see "AI summary card")
git add data/reviews data/images/reviewers data/summary.json && git commit -m "reviews: add new reviews $(date +%F)" && git push
```

Also check, every few weeks: the Amazon rating count on the product page (if it grew but no new written review arrived, the new ones are star-only), the Faire brand page (retailer reviews would make it a platform), and fastonepro.com for new product links (add the ASIN / listing id to `sources.json`).

Other ways to run it:

- **API token instead of the connector:** `APIFY_TOKEN=… python3 scripts/pull_reviews.py` runs the actors through the Apify REST API itself.
- **Full re-pull:** `--all` drops the date window (Amazon: one run per star rating). It still adds only reviews whose `id` isn't stored yet.
- **Refresh existing reviews:** `scripts/import_reviews.py --update`.
- **Etsy avatars:** the Etsy actor has no avatar field. A new Etsy review gets an initials avatar unless you add `buyer_avatar_url` / `buyer_profile_url` to its item in `.pull/etsy.json` (from the listing page's review markup, e.g. via `apify/web-fetch`) before importing.

`.pull/` holds raw scraper output. It's git-ignored; the imported review files are the record.

**About Elfsight:** fastonepro.com has no Elfsight (or other) reviews widget, so nothing comes from one.

## Card order

The order is deterministic, so it's the same on every load:

- **"All reviews": newest first, with gentle platform diversity.**
  - For each slot, the widget takes the newest remaining review.
  - If that review's platform matches the previous **2** cards, it takes the newest remaining review from a *different* platform instead.
  - It only does that if the other review is at most **~18 months (548 days)** older than the newest candidate. Otherwise it takes the newest review anyway.
  - Today: Amazon, Amazon, Etsy (Merlyn), then the remaining Amazon reviews newest first.
- In "All reviews" the [AI summary card](#ai-summary-card) comes first; it isn't a review and isn't counted (`data-limit` counts review cards only).
- **Single-platform filter** (e.g. Amazon): newest first.
- Ties are broken by `id`.
- Rating-only reviews (empty or whitespace-only text) never become cards, but they still count in the header. All 13 stored reviews have text. With `display.show_rating_only_reviews: true` such reviews get cards with no text element.

Both numbers are settings: `display.max_same_platform_run` and `display.diversity_window_days` in `data/config.json`.

## AI summary card

The first card in "All reviews" (carousel and grid) is a short summary of what reviewers say, written by AI from the stored review texts and labeled as such: a sparkle icon and **AI summary** (`strings.ai_summary`), with `role="note"` and the aria label "AI-generated summary of N reviews". It is not a link, has no stars or platform icon, is not counted in any total or rating, does not count against `data-limit`, and is never part of the JSON-LD. It doesn't appear on single-platform tabs.

It lives in `data/summary.json`:

```jsonc
{
  "text": "2-4 sentences",
  "generated_at": "2026-10-06T02:31:00Z",
  "review_count": 13,          // reviews in index.json when it was written (staleness check)
  "reviews_with_text": 13,
  "generated_by": "…",
  "notes": "…"
}
```

Rules for the text: only themes that actually appear in the reviews, no invented facts, no quotes attributed to anyone, no star claims. The card has the same height as the review cards; if the text is longer than fits, it scrolls inside the card with a fade at the bottom, so keep it to about 300 characters.

**Refresh:** `scripts/pull_reviews.py` compares `review_count` with the current number of reviews after each import. If they differ it prints `SUMMARY STALE` and writes all review texts to `.pull/summary_input.txt`; the weekly run then rewrites `text`, `generated_at`, `review_count` and `reviews_with_text` and commits `data/summary.json` with the new reviews.

**Hide it:** `display.show_summary: false` in `config.json` (everywhere), `data-summary="off"` on one embed, or `?summary=off` on the host page. Deleting `data/summary.json` also removes it.

---

## Structured data (JSON-LD)

`scripts/build-index.mjs` writes `data/reviews/schema.json` (and CI commits it), and the widget injects it once per page as `<script type="application/ld+json" id="reviews-widget-schema">` in `<head>`, however many widgets the page has. Turn it off with `schema.enabled: false` or `data-schema="off"` on the script tag (on any one tag, before it runs). If the page already has a script with that id, nothing is added.

**Why `Product`, not `LocalBusiness`:** every review here is about one physical product (the 6-pack skin tone set), bought on Amazon or Etsy, not about a place or a service, and FASTONE has no storefront, address or opening hours. `Product` (with `brand` FASTONE, `manufacturer` Heather Wolfe Art and the UPC as `gtin12`) describes exactly what was reviewed, and it is the type the marketplaces themselves use (the Etsy listing's own JSON-LD is a `Product` with an `AggregateRating`). `LocalBusiness` would claim the reviews are about a business location, which they aren't.

What's in it:

- One `Product` (`schema.type`) with `@id` `https://www.fastonepro.com/#product`, `name`, `url` (fastonepro.com), and from `schema.extra`: `description` (from the site's label text), `brand`, `manufacturer`, `gtin12` 726872046914, `category`, `image` (the listing photo), `sameAs` (the Amazon and Etsy product pages). No `offers`: prices differ per marketplace and change, and nothing here would keep them current.
- `aggregateRating`: `ratingValue` (one decimal), `bestRating` 5, `worstRating` 1, `ratingCount` and `reviewCount` = every stored review with a 1-5 rating (today 13: 4.8). It does **not** include Amazon's 8 star-only ratings, which aren't available individually.
- `review`: **every** review (`schema.max_reviews: 0`; a number caps it), in the same order as the "All reviews" cards. Each has `author` (`Person`, the displayed name, e.g. "Isabel W."), `datePublished`, `publisher` (`Organization`: Amazon or Etsy), `reviewRating` (`Rating` 1-5) and `reviewBody` (the same snippet the card shows). The AI summary is never included.

**Google caveat (read before expecting stars):** Google's review-snippet guidelines say *"Don't aggregate reviews or ratings from other websites"* (and Elfsight notes Google tends to ignore review snippets on home pages). These reviews come from Amazon and Etsy, so this markup is unlikely to earn star rich results, even as a `Product`. (The self-serving-review rule only covers `LocalBusiness` / `Organization`, so `Product` is at least not against that rule.) The markup still describes the product and its reviews accurately to search engines and AI crawlers. Google also asks that incentivized reviews be disclosed; Amazon labels the 2 Vine reviews on Amazon, but the widget card doesn't show that label (it's stored as `amazon_vine`). If fastonepro.com later adds its own `Product` markup, give it the same `@id` so the two merge, or turn this off.

## Header behavior

One compact row: rating on the left, platform filter tabs in the middle, **Write a review** on the right, all vertically centered. The header responds to the widget's own width through CSS container queries (`container: rw / inline-size` on `.rw-root`), so it follows the embed or iframe width, not the browser window:

| Widget width | Header |
|---|---|
| > 1020px | one row: score, "Excellent", stars, "Based on N reviews" · tabs with icon, name, and count · button |
| ≤ 1020px | tabs collapse to icon and count (the name stays in `title` / `aria-label`) |
| ≤ 720px | compact: "Excellent" and "Based on" hidden (shows score, stars, "N reviews"), tighter tabs and button |
| ≤ 575px | one row: the filter tabs are hidden (the cards show all reviews), the rating (score, stars, "N reviews") on the left, a compact button on the right |
| ≤ 360px | the button reads "Review" (`strings.write_review_short`; its accessible name stays "Write a review"), slightly smaller score |

With [`data-fixed-height`](#google-sites-and-other-fixed-height-boxes) the header also responds to the widget's height (the root becomes a `size` container):

| Widget height | Header and cards |
|---|---|
| ≤ 460px | "Excellent" and "Based on" hidden, tighter header and card padding |
| ≤ 360px | also a smaller score, stars, button, tabs, avatars and review text |
| ≤ 300px | tighter still: smaller score, card padding, avatars, review text and "View on" link |

The carousel shows 4 cards above 1024px, 3 at ≤ 1024px, 2 at ≤ 760px, and one card (88% wide, swipeable, no arrows) at ≤ 575px.

The "Write a review" button goes to the active platform's `write_url`; on the "All" tab it uses `default_write_platform` (Amazon: the product's review form, `/review/create-review?asin=B0D2LXC354`). The Etsy tab goes to Etsy's Purchases page, the only place a buyer can review an Etsy order.

---

## Privacy and presentation

- **Storage is complete.** Each review file stores everything collected:
  - the reviewer's full name, profile URL, and avatar source URL
  - the full review text, title and the seller's reply (none exist today)
  - the individual review URL, date, product (ASIN / listing), verified-purchase and Vine flags, review photos and platform extras

  `data/reviews/index.json` carries the same full records. The repo is public, so all of this is publicly readable.
- **Presentation is abbreviated.** The widget computes everything visible at render time:
  - Names show as **first name + last initial** (e.g. "Isabel W."). Couples like "Ann & Bob C." are kept.
  - Text is clipped to a **~160-character snippet** at a word boundary.
  - The reviewer's own surname inside the snippet is shown as an initial.
  - Screen-reader labels use the abbreviated name too.
  - Each card links to the original review on its platform.
- **Card links:** Amazon cards open the individual review (`/gp/customer-reviews/<id>`; Amazon may ask visitors to sign in to view it). Etsy cards open the listing's reviews section, since Etsy has no per-review URL.
- File names use the abbreviated name: `<platform>-<yyyy-mm-dd>-<first>-<initial>.json`.
- **Search engines:** `index.html` and `embed.html` carry `<meta name="robots" content="noindex, nofollow, noarchive">`. This doesn't affect embedding. The repo itself has no description, topics, or homepage link, but it's still public and findable through GitHub search.

---

## Technical details

- **Mounting:** each copy of the script captures its own `document.currentScript` when it runs, then picks `data-target`, unfilled `[data-reviews-widget]` elements, or a new `<div>` inserted before its own tag (see [the rules above](#javascript-embed-preferred)). A script that runs while the page is still parsing (plain or `async`) waits for `DOMContentLoaded`, so targets further down the page exist. Each element is filled only once.
- **DOM and sizing:** the mount element (the inserted `<div>` or your target) becomes `.rw-host`. It contains a zero-height `.rw-sizer` and the widget itself, `.rw-root`.
  - **Why it collapsed:** `.rw-root` has `container-type: inline-size` so the header and carousel can use container queries. That size containment gives it an intrinsic width of 0.
  - **Where it collapsed:** any parent that sizes children to their content (a Framer Embed or Squarespace code block wrapper, which is a centered flex column; inline-block, `fit-content`, float or absolute parents). There the old widget shrank to its 12px of padding and the container queries picked the narrowest layout.
  - **How the host fixes it:** the host is a full-width block (`width:100%; min-width:0; flex:1 1 100%; align-self:stretch; justify-self:stretch; text-align:left`, with a doubled class so page-builder rules can't override it).
  - **What the sizer adds:** a row of 24 inline blocks gives the host an intrinsic max-content width of `--rw-max-width` and a min-content width of 1/24 of it. Shrink-to-fit parents therefore size the widget to the available width without ever forcing overflow.
  - **Clipping:** `.rw-clip` (`overflow-x: clip`) trims the arrows' overhang. `data-overflow="hidden"` uses `.rw-overflow-hidden` (`overflow: hidden`) instead.
  - **Fixed height:** `data-fixed-height` gives the host a height: `100%` when its parent has a definite height (checked with a probe element), otherwise the window height below the widget's top minus the page's bottom margin, recalculated on resize. `.rw-root.rw-fixed` becomes a flex column with `container-type: size`; the track gets the remaining height (`grid-template-rows: minmax(0,1fr)`), and each card's text gets `overflow-y: auto`.
- **Empty text:** a review whose text is empty or only whitespace / zero-width characters never gets a text element (no empty paragraph, quote, spacer, or placeholder). The card's "View on …" link is pinned to the bottom with `margin-top: auto`, so a card without text still lays out cleanly.
- **Loading:** the script works out the repo root as `new URL('../../', document.currentScript.src)`, or uses `data-base`. In parallel it fetches `data/config.json`, `data/reviews/index.json` and (optional) `data/summary.json` (`cache: no-cache`); `data/reviews/schema.json` is fetched after the config says it's enabled and adds `<link>`s for `assets/css/reviews-widget.css` and `data/theme/theme.css`, unless the page already has them. `index.html` / `embed.html` include them in `<head>` and use the same single script tag. Everything is fetched once per page, however many widgets or script tags there are (shared through `window.__reviewsWidget`).
- **No flash:** the root starts at `opacity: 0`. The widget waits for the stylesheets, then for weights 400, 700, and italic 300 of the first family in `--rw-font`. That wait has a timeout of `display.font_timeout_ms`; after it, the theme's metric-matched fallback face is used. After the first layout the widget fades in over 0.18s (instantly with reduced motion). The fonts use `font-display: block`. Here the first family is Open Sans; Oswald (score and labels) starts loading during that wait via the theme's loading-message trick.
- **Icons:** the site's own SVG (`icon` in `config.json`, else `data/icons/<platform>.svg`) is always used. Only if that file fails to load does the `<img>` switch to the [Simple Icons CDN](https://simpleicons.org/) (`https://cdn.simpleicons.org/<simple_icon or platform key>`).
- **Accessibility:** each card is a single `<a>` (new tab, `rel="noopener"`) with an aria label like "Read Isabel W.'s review on Amazon (opens in a new tab)". Nothing inside a card is interactive. The tabs are `role="tab"` buttons with counts in their labels, star ratings have text labels, and focus rings are visible. Cards have no shadows: hover lifts them 2px with an accent border, and focus shows a 3px accent outline.
- **Iframe height:** inside an iframe the widget posts `{type: 'reviews-widget-height', height}` to the parent on render, resize, and tab change (not with `data-fixed-height`).
- **Validation (`scripts/build-index.mjs`):** checks the required fields (`id`, `platform`, `reviewer_name`, `reviewer_image`, `text`, `date`, `review_url`, `source`), rating 1-5 or null, ISO dates, unique ids, and that each `reviewer_image` exists under `data/images/reviewers/`. A failure stops the workflow without committing.
- **Workflow:** `.github/workflows/build-index.yml` runs on pushes that touch `data/reviews/**` (other than the generated `index.json` / `schema.json`), `data/config.json`, `data/images/reviewers/**` or `scripts/build-index.mjs`, and on manual dispatch. It commits `index.json` and `schema.json` only if they changed. GitHub Pages deploys the branch as-is (`.nojekyll`).
- **Local preview:** run `python3 -m http.server` in the repo root and open http://localhost:8000/. To try the JS embed against a local copy, point the script `src` at it. The fonts and JSON need CORS when served from a different origin; GitHub Pages sends `Access-Control-Allow-Origin: *`.

---

## Credits

Platform logos: **Amazon** is Amazon's official "a" + smile mark (File:Amazon_icon.svg on Wikimedia Commons), placed on a white rounded tile so it stays legible on the dark active tab; **Etsy** is Etsy's orange "E" app mark (#F45800). Instagram, YouTube and website icons are kept for the linked profiles listed in `sources.json`. All marks belong to their owners and are used only to identify where each review was posted. If an icon file fails to load, the widget falls back to [Simple Icons](https://simpleicons.org/). The brand colors (#1f1f1f, #424242, #212121, #5f6368, #cccccc, #f4f4f4) and the Open Sans and Oswald typefaces ([OFL](data/theme/fonts/OFL-OpenSans.txt), [OFL](data/theme/fonts/OFL-Oswald.txt), self-hosted latin subsets) come from fastonepro.com. FASTONE® is a registered trademark of its owner. Review content belongs to its authors and is shown with a link back to the original.

