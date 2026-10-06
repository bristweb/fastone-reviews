# FASTONE Pro Paint — reviews data

Every public review of **[FASTONE® Pro Premades](https://www.fastonepro.com/)** (the six-color heavy body acrylic skin tone paint set by Knoxville artist Heather Wolfe), plus the settings and theme for its reviews widget. This repo is **data only**: the widget code, the import/sync scripts and the full documentation live in **[bristweb/reviews-widget](https://github.com/bristweb/reviews-widget)**. GitHub Pages serves these files at `https://bristweb.github.io/fastone-reviews/`.

- **Live widget:** https://bristweb.github.io/reviews-widget/?source=https://bristweb.github.io/fastone-reviews/
- **Settings:** [`config.json`](config.json) · **Reviews:** [`reviews/`](reviews/) (one file per year)

## Contents

1. [Embed](#embed)
2. [What's here](#whats-here)
3. [Reviews and platforms](#reviews-and-platforms)
4. [Weekly sync](#weekly-sync)
5. [Look and feel](#look-and-feel)
6. [Structured data](#structured-data)
7. [Credits](#credits)

## Embed

fastonepro.com is a Google Sites page, so use the fixed-height variant there (*Insert → Embed → Embed code*, paste, then stretch the box to full width and about 420px tall):

```html
<script src="https://bristweb.github.io/reviews-widget/assets/js/reviews-widget.js"
        data-source="https://bristweb.github.io/fastone-reviews/"
        data-fixed-height="true" data-arrows="inside" data-overflow="hidden"
        data-hover-lift="false" data-focus-ring="inside"></script>
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
                      reported counts), links, display, strings, schema, avatar palette, AI summary, reviews.years
reviews/<year>.json   the reviews dated in that year, newest first (2024-2026)
images/reviewers/     avatars: <platform>-<platform_review_id>.<ext>
icons/                amazon.svg, etsy.svg + instagram, youtube, website
theme/                theme.css (colors, Oswald labels) + self-hosted Open Sans and Oswald
.github/workflows/    validate.yml: runs the shared validator on every push
```

The record format is documented in [reviews-widget: Data repo format](https://github.com/bristweb/reviews-widget#data-repo-format). Records store everything collected (full names, full text, profile and avatar URLs, product, Vine and verified-purchase flags); the widget abbreviates names and clips text when it renders.

## Reviews and platforms

| Platform | Reviews stored | Platform-reported | Source page |
|---|---|---|---|
| Amazon | 12 (every written review) | 4.8 ★ · 20 ratings, 12 with text (79% 5★, 21% 4★) | https://www.amazon.com/product-reviews/B0D2LXC354 (ASIN B0D2LXC354) |
| Etsy | 1 | 5.0 ★ · 1 review on the listing | https://www.etsy.com/listing/1872977093#reviews |

fastonepro.com links to exactly one product on each marketplace: Amazon ASIN **B0D2LXC354** and Etsy listing **1872977093** in the HeatherWolfeArt shop. It also links to Faire (wholesale; **0** retailer reviews), a "Buy Local" Google Maps link to Jerry's Artarama Knoxville (a stockist; its reviews are about the store, so not collected), Instagram, YouTube, heatherwolfeart.com, a Drive template and the USPTO trademark record. All are in `config.json` (`platforms` and `links`) with what was checked.

- **Amazon gap:** Amazon counts 20 ratings, but 8 are star-only with no text. Amazon never lists those individually, so they can't be stored or shown; the widget and JSON-LD use the 12 written reviews (average 4.75, shown as 4.8). These reviewers have Amazon's default silhouette, so their avatars are generated initials. Amazon has no public seller replies. 2 of the 12 are **Amazon Vine** reviews (Daytona S., Joe), flagged `amazon_vine: true`. Amazon cards open the individual review (Amazon may ask visitors to sign in).
- **Etsy:** the shop has 3 reviews in total; only Merlyn's (2025-10-21) is for the FASTONE listing, so the importer keeps only `listing_ids` [1872977093]. Etsy has no per-review URL (`review_url` is the listing's reviews section). Merlyn's avatar and profile link come from the listing page's review markup (the actor has no avatar field); a new Etsy review gets an initials avatar unless `buyer_avatar_url` / `buyer_profile_url` are added to its item before importing.
- **About Elfsight:** fastonepro.com has no Elfsight (or other) reviews widget.
- **Also check every few weeks:** the Amazon rating count (if it grew without a new written review, the new ones are star-only), the Faire brand page, and fastonepro.com for new product links (add the ASIN / listing id to `config.json`).

## Weekly sync

A scheduled run (`weekly-fastone-review-sync`) pulls new reviews with the shared scripts through Apify: Amazon (`junglee/amazon-reviews-scraper`, date-windowed to the newest stored review minus 30 days) and Etsy (`astravalabs/etsy-reviews-scraper`, shop-wide, newest 50), each capped at $0.50 per run (a week with no new reviews costs about $0.01). See [reviews-widget: Weekly sync](https://github.com/bristweb/reviews-widget#weekly-sync).

```bash
python3 reviews-widget/scripts/pull_reviews.py --data fastone-reviews --print-inputs
# run the Amazon / Etsy actors, save items to fastone-reviews/.pull/amazon.json and etsy.json
python3 reviews-widget/scripts/pull_reviews.py --data fastone-reviews --from-raw
```

Initial pull (2026-10-05): 3 Amazon runs (12 unique reviews) ≈ $0.13, 1 Etsy run ≈ $0.01, 1 listing-page fetch ≈ $0.002. On Apify's free plan the Amazon actor returns at most 10 reviews per run, so a full re-pull (`--all`) runs once per star rating.

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

The theme also sets the score, rating label and AI-summary label in uppercase Oswald, and starts the Oswald download while the widget waits for Open Sans so the header never repaints.

## Structured data

`schema.type` is **`Product`**, not `LocalBusiness`: every review is about one physical product bought on Amazon or Etsy, and FASTONE has no storefront, address or hours. `schema.extra` adds `@id` `https://www.fastonepro.com/#product`, `description`, `brand` FASTONE, `manufacturer` Heather Wolfe Art, `gtin12` 726872046914, `category`, `image` and `sameAs` (the Amazon and Etsy pages); no `offers` (prices differ per marketplace). The `aggregateRating` covers the 13 stored rated reviews (4.8), not Amazon's 8 star-only ratings. Google asks sites not to aggregate reviews from other websites, so stars in search are unlikely; Amazon labels the 2 Vine reviews, which the cards don't show (stored as `amazon_vine`). If fastonepro.com adds its own `Product` markup, give it the same `@id`.

## Credits

Platform logos: **Amazon** is Amazon's official "a" + smile mark (File:Amazon_icon.svg on Wikimedia Commons) on a white rounded tile; **Etsy** is Etsy's orange "E" app mark (#F45800). Instagram, YouTube and website icons are for the linked profiles. All marks belong to their owners and are used only to identify where each review was posted. The brand colors and the Open Sans and Oswald typefaces ([OFL](theme/fonts/OFL-OpenSans.txt), [OFL](theme/fonts/OFL-Oswald.txt), self-hosted latin subsets) come from fastonepro.com. FASTONE® is a registered trademark of its owner. Review content belongs to its authors and is shown with a link back to the original.
