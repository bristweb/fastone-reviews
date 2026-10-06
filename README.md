# FASTONE Pro Paint — reviews data

Every public review of **[FASTONE® Pro Premades](https://www.fastonepro.com/)** (the six-color heavy body acrylic skin tone paint set by Knoxville artist Heather Wolfe), plus the settings and theme for its reviews widget. The widget code and its documentation live in **[bristweb/reviews-widget](https://github.com/bristweb/reviews-widget)** (including a short [feature comparison](https://github.com/bristweb/reviews-widget/blob/main/COMPARISON.md) with hosted review-widget SaaS and reputation platforms); this repo holds the data plus this site's own [sync tooling](#sync-tooling). GitHub Pages serves these files at `https://bristweb.github.io/fastone-reviews/`.

- **Live widget:** https://bristweb.github.io/reviews-widget/?source=https://bristweb.github.io/fastone-reviews/
- **Settings:** [`config.json`](config.json) · **Reviews:** [`reviews/`](reviews/) (one file per year)

## Contents

1. [Embed](#embed)
2. [What's here](#whats-here)
3. [Reviews and platforms](#reviews-and-platforms)
4. [Sync tooling](#sync-tooling)
5. [Look and feel](#look-and-feel)
6. [Structured data](#structured-data)
7. [Credits](#credits)

## Embed

fastonepro.com is a Google Sites page, so use the constrained preset there (*Insert → Embed → Embed code*, paste, then stretch the box to full width and about 420px tall):

```html
<script src="https://bristweb.github.io/reviews-widget/assets/js/reviews-widget.js"
        data-source="https://bristweb.github.io/fastone-reviews/"
        data-constrained="true"></script>
```

Anywhere else, the plain JavaScript embed sizes itself:

```html
<script src="https://bristweb.github.io/reviews-widget/assets/js/reviews-widget.js"
        data-source="https://bristweb.github.io/fastone-reviews/" defer></script>
```

Iframe:

```html
<iframe id="reviews-widget" src="https://bristweb.github.io/reviews-widget/embed.html?source=https://bristweb.github.io/fastone-reviews/"
        title="Reviews" loading="lazy" scrolling="no" style="width:100%;border:0;height:420px"></iframe>
<script>
  addEventListener('message', function (e) {
    if (e.data && e.data.type === 'reviews-widget-height')
      document.getElementById('reviews-widget').style.height = e.data.height + 'px';
  });
</script>
```

All options (layout, platform filter, limit, fitting options): see the [reviews-widget README](https://github.com/bristweb/reviews-widget#options).

## What's here

```
config.json           business + product, platforms (Amazon, Etsy: links, ASIN / listing filters, scrape URLs,
                      reported counts), links, display, strings, schema, avatar palette, summary, reviews.years
reviews/<year>.json   the reviews dated in that year, newest first (2024-2026)
images/reviewers/     avatars: <platform>-<platform_review_id>.<ext>
icons/                amazon.svg, etsy.svg + instagram, youtube, website
theme/                theme.css (colors, Oswald labels) + self-hosted Open Sans and Oswald
scripts/              this site's sync tooling (never loaded by the widget)
.github/workflows/    validate.yml: runs the shared validator on every push
```

The record format is documented in [reviews-widget: Data repo format](https://github.com/bristweb/reviews-widget#data-repo-format). How reviews are obtained (Amazon and Etsy through Apify) lives only in `config.json` / `scripts/`, never on the review objects. Records store everything collected (full names, full text, profile and avatar URLs, product, Vine and verified-purchase flags); the widget abbreviates names and clips text when it renders.

## Reviews and platforms

| Platform | Reviews stored | Platform-reported | Source page |
|---|---|---|---|
| Amazon | 12 (every written review) | 4.8 ★ · 20 ratings, 12 with text (79% 5★, 21% 4★) | https://www.amazon.com/product-reviews/B0D2LXC354 (ASIN B0D2LXC354) |
| Etsy | 1 | 5.0 ★ · 1 review on the listing | https://www.etsy.com/listing/1872977093#reviews |

fastonepro.com links to exactly one product on each marketplace: Amazon ASIN **B0D2LXC354** and Etsy listing **1872977093** in the HeatherWolfeArt shop. It also links to Faire (wholesale; **0** retailer reviews), a "Buy Local" Google Maps link to Jerry's Artarama Knoxville (a stockist; its reviews are about the store, so not collected), Instagram, YouTube, heatherwolfeart.com, a Drive template and the USPTO trademark record. All are in `config.json` (`platforms` and `links`) with what was checked.

- **Amazon gap:** Amazon counts 20 ratings, but 8 are star-only with no text. Amazon never lists those individually, so they can't be stored or shown; the widget and JSON-LD use the 12 written reviews (average 4.75, shown as 4.8). These reviewers have Amazon's default silhouette, so their avatars are generated initials. Amazon has no public seller replies. 2 of the 12 are **Amazon Vine** reviews (Daytona S., Joe), flagged `amazon_vine: true`. Amazon cards open the individual review (Amazon may ask visitors to sign in).
- **Etsy:** the shop has 3 reviews in total; only Merlyn's (2025-10-21) is for the FASTONE listing, so the importer keeps only `listing_ids` [1872977093]. Etsy has no per-review URL (`review_url` is the listing's reviews section). Merlyn's avatar and profile link come from the listing page's review markup (the actor has no avatar field); a new Etsy review gets an initials avatar unless `buyer_avatar_url` / `buyer_profile_url` are added to its item before importing.
- **Also check from time to time:** the Amazon rating count (if it grew without a new written review, the new ones are star-only), the Faire brand page, and fastonepro.com for new product links (add the ASIN / listing id to `config.json`).

## Sync tooling

`scripts/` collects this site's reviews (Python 3, no packages); the widget never loads it. Settings live in `config.json` `platforms`: `scrape_urls` (Amazon product URL, Etsy shop), `asins` / `listing_ids` (import only the FASTONE product), `product_title`, `page_url` (fallback link), and `avatars` (initials colors). How often it runs is up to whoever schedules it.

| Platform | Method | Actor | Why |
|---|---|---|---|
| Amazon | Apify | `junglee/amazon-reviews-scraper` (run with `includeGdprSensitive` for names and profile links) | the product page renders reviews client-side; review pages redirect to Sign in |
| Etsy | Apify | `astravalabs/etsy-reviews-scraper` (shop-wide; the importer keeps listing 1872977093 only) | etsy.com is behind DataDome (403) |

Amazon runs ask only for reviews newer than the newest stored Amazon review minus 30 days (`--since-days`); Etsy has no date filter (newest 50 in the shop). Each run is capped at $0.50 (Apify's minimum); a run with no new reviews costs about $0.01. On Apify's free plan the Amazon actor returns at most 10 reviews per run, so a full re-pull (`--all`) runs once per star rating. Initial pull (2026-10-05): 3 Amazon runs (12 unique reviews) ≈ $0.13, 1 Etsy run ≈ $0.01, 1 listing-page fetch ≈ $0.002.

**Etsy avatars:** the Etsy actor has no avatar field. A new Etsy review gets an initials avatar unless `buyer_avatar_url` / `buyer_profile_url` (from the listing page's review markup) are added to its item in `.pull/etsy.json` before importing.

```bash
python3 scripts/pull_reviews.py --print-inputs   # per platform: actor, input with the date window, cost cap, save path
# run each actor with that input (e.g. Apify connector call-actor, maxTotalChargeUsd 0.5) and save its dataset items
# as a JSON array to the printed path (.pull/amazon.json, .pull/etsy.json)
python3 scripts/pull_reviews.py --from-raw       # imports NEW reviews only, checks the summary
node ../reviews-widget/scripts/validate.mjs .    # optional local check (the push workflow runs it too)
git add reviews images/reviewers config.json && git commit -m "reviews: sync $(date +%F)" && git push
```

Other ways to run it: `APIFY_TOKEN=… python3 scripts/pull_reviews.py` calls the Apify REST API itself; `--all` drops the date window (still adds only new reviews); `python3 scripts/import_reviews.py --update --<platform> <file>` refreshes existing records (keeping `collected_at`, avatars and `featured_on_website`). `.pull/` holds raw scraper output and is git-ignored.

New reviews are added to `reviews/<year>.json` (a new year gets a new file and is added to `reviews.years`), with avatars downloaded to `images/reviewers/<platform>-<platform_review_id>.<ext>` or an initials SVG in the `avatars` colors. **Summary:** after an import the script prints `SUMMARY STALE` when any review is dated or was collected after `summary.generated_at`, and writes every review text to `.pull/summary_input.txt`. Rewrite `summary.text` from it (2-4 sentences, about 300 characters, only themes that appear in the reviews, no invented facts, no attributed quotes, no star claims) and set `summary.generated_at` to the current UTC time.

## Look and feel

[`theme/theme.css`](theme/theme.css), from fastonepro.com (a deliberately monochrome Google Sites theme, headings in uppercase Oswald, body in Open Sans):

| Variable | Value |
|---|---|
| `--rw-font` | `"FASTONE Open Sans"`, metric-matched Arial fallback, system fonts |
| `--rw-ink` / `--rw-body` / `--rw-muted` | `#1f1f1f` / `#424242` / `#5f6368` |
| `--rw-line` / `--rw-line-strong` | `#e4e4e4` / `#cccccc` |
| `--rw-card` / `--rw-tint` | `#fff` / `#f4f4f4` |
| `--rw-accent` / `--rw-accent-2` | `#424242` / `#1f1f1f` |
| `--rw-star` / `--rw-star-off` | `#f5b301` / `#dddddd` |
| `--rw-radius` / `--rw-max-width` | `8px` / `1200px` |

The theme also sets the score, rating label and Summary label in uppercase Oswald, and starts the Oswald download while the widget waits for Open Sans so the header never repaints.

## Structured data

`schema.type` is **`Product`**, not `LocalBusiness`: every review is about one physical product bought on Amazon or Etsy, and FASTONE has no storefront, address or hours. `schema.extra` adds `@id` `https://www.fastonepro.com/#product`, `description`, `brand` FASTONE, `manufacturer` Heather Wolfe Art, `gtin12` 726872046914, `category`, `image` and `sameAs` (the Amazon and Etsy pages); no `offers` (prices differ per marketplace). The `aggregateRating` covers the 13 stored rated reviews (4.8), not Amazon's 8 star-only ratings. Google asks sites not to aggregate reviews from other websites, so stars in search are unlikely; Amazon labels the 2 Vine reviews, which the cards don't show (stored as `amazon_vine`). If fastonepro.com adds its own `Product` markup, give it the same `@id`.

## Credits

Platform logos: **Amazon** is Amazon's official "a" + smile mark (File:Amazon_icon.svg on Wikimedia Commons) on a white rounded tile; **Etsy** is Etsy's orange "E" app mark (#F45800). Instagram, YouTube and website icons are for the linked profiles. All marks belong to their owners and are used only to identify where each review was posted. The brand colors and the Open Sans and Oswald typefaces ([OFL](theme/fonts/OFL-OpenSans.txt), [OFL](theme/fonts/OFL-Oswald.txt), self-hosted latin subsets) come from fastonepro.com. FASTONE® is a registered trademark of its owner. Review content belongs to its authors and is shown with a link back to the original.
