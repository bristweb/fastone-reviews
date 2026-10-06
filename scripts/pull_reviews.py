#!/usr/bin/env python3
"""FASTONE Pro Paint review sync: fetch recent reviews from this site's platforms and add only NEW ones.

  python3 scripts/pull_reviews.py --print-inputs   # Apify actor inputs with date windows (JSON)
  python3 scripts/pull_reviews.py --from-raw       # import .pull/<platform>.json saved by another runner
  APIFY_TOKEN=... python3 scripts/pull_reviews.py  # run the actors via the Apify REST API

What to scrape comes from config.json `platforms` (`scrape_url` / `scrape_urls`; a platform without one is skipped):
* Amazon   -> Apify `junglee/amazon-reviews-scraper`      (review pages need a login; the product page renders
              reviews client-side). --all runs once per star rating (free plan: 10 reviews per run).
* Etsy     -> Apify `astravalabs/etsy-reviews-scraper`    (etsy.com is behind DataDome); shop-wide, filtered to
              config.json `listing_ids` by the importer.
Each Apify run asks only for reviews newer than (latest stored review on that platform - since-days) and is capped
with maxTotalChargeUsd. Etsy has no date filter (newest 50 of the shop). --all ignores the date window (full re-pull).
Raw results live in .pull/ (git-ignored). Then runs import_reviews.py (new reviews only; full records stored).
Finally checks the AI summary (config.json `summary`): if any review is dated or was collected after
summary.generated_at, prints SUMMARY STALE and writes .pull/summary_input.txt (all review texts) so the run can
rewrite summary.text and summary.generated_at. Validating, committing and pushing are left to the caller (see README).
"""
import argparse, datetime, json, os, subprocess, sys, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from import_reviews import load_reviews  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--data', default=os.path.dirname(HERE), help='data repo checkout (default: this repo)')
ap.add_argument('--since-days', type=int, default=30, help='overlap window before the newest stored review')
ap.add_argument('--max-usd', type=float, default=0.5, help='Apify cost cap per actor run (Apify\'s minimum is $0.50)')
ap.add_argument('--all', action='store_true', help='full re-pull (no date window)')
ap.add_argument('--print-inputs', action='store_true', help='print {platform: {actor, input}} and exit')
ap.add_argument('--from-raw', action='store_true',
                help='do not call Apify; import .pull/<platform>.json files saved by another runner (e.g. the Apify connector)')
A = ap.parse_args()
ROOT = os.path.abspath(A.data)
RAW = os.path.join(ROOT, '.pull')
# What to scrape comes from config.json platforms (`scrape_url`, or a `scrape_urls` list); actor ids and options are below.
with open(os.path.join(ROOT, 'config.json')) as _f:
    CONFIG = json.load(_f)
_PL = CONFIG.get('platforms', {})
SCRAPE = {k: p.get('scrape_url') or (p.get('scrape_urls') or [None])[0] for k, p in _PL.items()}
SCRAPE_ALL = {k: p.get('scrape_urls') or ([p['scrape_url']] if p.get('scrape_url') else []) for k, p in _PL.items()}
# junglee/amazon-reviews-scraper returns at most 10 reviews per run on Apify's free plan (and 100 per star filter on
# any plan), so a full pull (--all) runs once per star rating; regular pulls use one date-windowed run.
AMAZON_STARS = ['fiveStar', 'fourStar', 'threeStar', 'twoStar', 'oneStar']

# platform -> (actor, build(since) -> one input dict or a list of input dicts (one Apify run each; items are concatenated))
ACTORS = {
    'amazon': ('junglee~amazon-reviews-scraper', lambda since: [{
        'productUrls': [{'url': u} for u in SCRAPE_ALL['amazon']],
        'maxReviews': 100, 'includeGdprSensitive': True, 'sort': 'recent',
        'filterByRatings': [stars], **({'reviewsCutoffDate': since} if since else {})}
        for stars in (['allStars'] if since else AMAZON_STARS)]),
    # The Etsy actor takes the shop (it has no date filter); the importer keeps only config.json `listing_ids`.
    'etsy': ('astravalabs~etsy-reviews-scraper', lambda since: {
        'shops': SCRAPE_ALL['etsy'], 'reviewsSort': 'Recency', 'maxReviews': 50 if since else 0,
        'maxTotalResults': 1000}),
}
ACTORS = {k: v for k, v in ACTORS.items() if SCRAPE.get(k)}  # only platforms with a scrape_url in config.json


def pull_apify(actor, inputs, token, max_usd, path):
    items = []
    for inp in inputs if isinstance(inputs, list) else [inputs]:
        qs = urllib.parse.urlencode({'token': token, 'format': 'json', 'clean': '1',
                                     'maxTotalChargeUsd': max_usd, 'timeout': 600})
        url = f'https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items?{qs}'
        req = urllib.request.Request(url, data=json.dumps(inp).encode(), method='POST',
                                     headers={'Content-Type': 'application/json'})
        items += json.loads(urllib.request.urlopen(req, timeout=660).read())
    json.dump(items, open(path, 'w'))
    return len(items)


def latest_dates(reviews):
    out = {}
    for r in reviews:
        out[r['platform']] = max(out.get(r['platform'], ''), r['date'])
    return out


def main():
    a = A
    os.makedirs(RAW, exist_ok=True)
    token = os.environ.get('APIFY_TOKEN')
    latest = latest_dates(load_reviews(ROOT))

    def since_for(plat):
        if a.all or plat not in latest:
            return None
        dt = datetime.datetime.fromisoformat(latest[plat].replace('Z', '+00:00')) - datetime.timedelta(days=a.since_days)
        return dt.date().isoformat()

    if a.print_inputs:
        print(json.dumps({p: {'actor': act.replace('~', '/'), 'input': b(since_for(p)),
                              'maxTotalChargeUsd': a.max_usd, 'save_items_to': os.path.join(RAW, f'{p}.json')}
                          for p, (act, b) in ACTORS.items()}, indent=2))
        return
    args, apify_args = [], []  # direct pulls (none here) / Apify pulls (imported with source 'apify')
    for plat, (actor, build) in ACTORS.items():
        path = os.path.join(RAW, f'{plat}.json')
        if a.from_raw:
            if os.path.exists(path):
                print(f'{plat}: importing {path}')
                apify_args += [f'--{plat}', path]
            else:
                print(f'{plat}: no {path}, skipped')
            continue
        if not token:
            print(f'{plat}: skipped (no APIFY_TOKEN)')
            continue
        since = since_for(plat)
        try:
            print(f'{plat} (apify {actor}, since {since or "all"}):', pull_apify(actor, build(since), token, a.max_usd, path), 'items')
            apify_args += [f'--{plat}', path]
        except Exception as e:
            print(f'{plat} failed:', e, file=sys.stderr)
    if not args and not apify_args:
        sys.exit('nothing pulled')
    importer = os.path.join(HERE, 'import_reviews.py')
    if args:
        subprocess.run([sys.executable, importer, '--data', ROOT, *args, '--source', 'direct'], check=True)
    if apify_args:
        subprocess.run([sys.executable, importer, '--data', ROOT, *apify_args, '--source', 'apify'], check=True)
    check_summary()


def check_summary():
    """The AI summary (config.json `summary` {text, generated_at}) is written by a person/agent from the stored
    reviews. It is stale when any review is dated or was collected after generated_at; then the review texts are
    dumped for rewriting it."""
    revs = load_reviews(ROOT)
    summ = json.load(open(os.path.join(ROOT, 'config.json'))).get('summary') or {}
    gen = summ.get('generated_at') or ''
    ts = lambda s: datetime.datetime.fromisoformat(s.replace('Z', '+00:00')) if s else None
    g = ts(gen)
    newer = [r for r in revs if g is None or any(ts(r.get(k)) and ts(r.get(k)) > g for k in ('date', 'collected_at'))]
    if summ.get('text') and not newer:
        print(f'summary: up to date ({len(revs)} reviews, generated {gen})')
        return
    path = os.path.join(RAW, 'summary_input.txt')
    with open(path, 'w') as f:
        for r in sorted(revs, key=lambda r: r['date'], reverse=True):
            if (r.get('text') or '').strip():
                f.write(f"[{r['platform']} {r['date'][:10]} rating={r.get('rating')}] {' '.join(r['text'].split())}\n")
    print(f"SUMMARY STALE: {len(newer)} review(s) dated/collected after config.json summary.generated_at ({gen or 'missing'}). "
          f"Rewrite summary.text from {path} and set summary.generated_at to now (see README).")


if __name__ == '__main__':
    main()
