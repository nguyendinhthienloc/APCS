import os
import sys
import re
import json
import time
import argparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from image_extractor import fetch_and_extract_subdocuments
from image_indexer import add_subdocuments, get_indexed_doc_count

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEEN_IDS_FILE = os.path.join(BASE_DIR, "crawled_article_ids.json")
STREAM_URL = "https://vnexpress.net/tin-tuc-24h"

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
}

def load_seen_ids():
    """Loads previously crawled article IDs from disk."""
    if os.path.exists(SEEN_IDS_FILE):
        try:
            with open(SEEN_IDS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"[WARN] Failed to load seen IDs: {e}")
    return set()

def save_seen_ids(seen_ids):
    """Saves updated set of crawled article IDs to disk."""
    with open(SEEN_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen_ids), f, indent=2)

def extract_article_links_from_stream():
    """Fetches vnexpress.net/tin-tuc-24h and extracts recent article links."""
    try:
        resp = requests.get(STREAM_URL, headers=REQUEST_HEADERS, timeout=10)
        if resp.status_code != 200:
            print(f"[ERROR] Failed to fetch stream (status {resp.status_code})")
            return []
        
        soup = BeautifulSoup(resp.text, "html.parser")
        article_links = []
        seen_links = set()

        for a in soup.find_all("a", href=True):
            href = a["href"].split("#")[0].split("?")[0]
            # Match standard VnExpress article URLs
            if re.search(r"-(\d+)\.html$", href) and "vnexpress.net" in href:
                if href not in seen_links and "/video" not in href:
                    seen_links.add(href)
                    article_links.append(href)
        return article_links
    except Exception as e:
        print(f"[ERROR] Stream crawl failed: {e}")
        return []

def run_crawling_cycle(seen_ids, max_new_articles=10):
    """
    Executes one crawling & indexing cycle:
    1. Checks for new articles.
    2. Filters out already-seen content.
    3. Crawls & indexes new image subdocuments.
    4. Updates seen IDs on disk.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{now_str}] 🔎 Checking for new content on VnExpress 24h...")

    links = extract_article_links_from_stream()
    new_urls = []

    for url in links:
        match = re.search(r"-(\d+)\.html$", url)
        if match:
            art_id = match.group(1)
            if art_id not in seen_ids:
                new_urls.append((art_id, url))

    if not new_urls:
        print(f"[{now_str}] ✅ No new articles found. Everything is up to date.")
        return 0

    print(f"[{now_str}] 🚀 Found {len(new_urls)} new articles! Processing up to {max_new_articles}...")
    batch_subdocs = []
    processed_ids = []

    for art_id, url in new_urls[:max_new_articles]:
        print(f"  -> Crawling: {url}")
        subdocs = fetch_and_extract_subdocuments(url)
        if subdocs:
            batch_subdocs.extend(subdocs)
            print(f"     Extracted {len(subdocs)} image subdocuments.")
        processed_ids.append(art_id)
        time.sleep(1)  # Polite crawling delay

    # 3. Incrementally index new subdocuments into Whoosh
    if batch_subdocs:
        added_count = add_subdocuments(batch_subdocs)
        print(f"[{now_str}] 💾 Successfully indexed {added_count} new image subdocuments.")

    # 4. Update seen IDs and persist to disk
    seen_ids.update(processed_ids)
    save_seen_ids(seen_ids)
    print(f"[{now_str}] 📊 Total subdocuments in index: {get_indexed_doc_count()} | Total seen articles: {len(seen_ids)}")
    return len(batch_subdocs)

def start_crawler_loop(interval_minutes=15, run_once=False):
    """Main crawler loop that runs every 15 minutes."""
    seen_ids = load_seen_ids()
    interval_seconds = interval_minutes * 60

    print("=" * 60)
    print(f"VnExpress Periodic Crawler Loop Started")
    print(f"Interval: Every {interval_minutes} minutes ({interval_seconds} seconds)")
    print(f"Initial seen articles: {len(seen_ids)}")
    print("=" * 60)

    if run_once:
        run_crawling_cycle(seen_ids)
        return

    while True:
        try:
            run_crawling_cycle(seen_ids)
            print(f"\n💤 Sleeping for {interval_minutes} minutes... (Press Ctrl+C to stop)\n")
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n[STOP] Crawler loop stopped by user.")
            break
        except Exception as e:
            print(f"[ERROR] Unexpected error in loop: {e}")
            print(f"Retrying in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VnExpress 15-minute Periodic Crawler Loop")
    parser.add_argument("--interval", type=int, default=15, help="Interval in minutes (default: 15)")
    parser.add_argument("--once", action="store_true", help="Run once and exit (for quick testing)")
    args = parser.parse_args()

    start_crawler_loop(interval_minutes=args.interval, run_once=args.once)
