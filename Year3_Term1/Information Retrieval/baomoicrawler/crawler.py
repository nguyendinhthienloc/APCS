"""
BaoMoi Image Web Crawler
=============================================================
A simple, robust web crawler and image downloader for baomoi.com.
- Uses BeautifulSoup for HTML parsing.
- Constraint: Only crawls articles published within the last 24 hours.
- Distinctive collection: Distributes image downloads evenly across distinct articles
  and deduplicates images so no duplicate image or single-article domination occurs.
- Self-contained in a single file for simplicity.
"""

import os
import sys
import re
import csv
import json
import time
import math
import hashlib
import logging
import argparse
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict
from urllib.parse import urljoin, urlparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BaoMoiCrawler")


# =====================================================================
# Configuration & Supported Categories
# =====================================================================

CATEGORIES = {
    "hot": "https://baomoi.com/",
    "tin-moi": "https://baomoi.com/tin-moi.epi",
    "xa-hoi": "https://baomoi.com/xa-hoi.epi",
    "the-gioi": "https://baomoi.com/the-gioi.epi",
    "kinh-te": "https://baomoi.com/kinh-te.epi",
    "giao-thong": "https://baomoi.com/giao-thong.epi",
    "phap-luat": "https://baomoi.com/phap-luat.epi",
    "the-thao": "https://baomoi.com/the-thao.epi",
    "giai-tri": "https://baomoi.com/giai-tri.epi",
    "khoa-hoc-cong-nghe": "https://baomoi.com/khoa-hoc-cong-nghe.epi",
    "cong-nghe": "https://baomoi.com/khoa-hoc-cong-nghe.epi",
    "suc-khoe": "https://baomoi.com/suc-khoe.epi",
    "doi-song": "https://baomoi.com/doi-song.epi",
    "xe-co": "https://baomoi.com/xe-co.epi",
    "nha-dat": "https://baomoi.com/nha-dat.epi",
    "du-lich": "https://baomoi.com/du-lich.epi",
    "giao-duc": "https://baomoi.com/giao-duc.epi",
}

IGNORED_URL_KEYWORDS = ["logo", "icon", "avatar", "favicon", "data:image", "adtimaserver", "bm-icon"]


# =====================================================================
# Helper Functions
# =====================================================================

def clean_filename(text: str, max_length: int = 40) -> str:
    """Creates a clean, safe filename from a string."""
    if not text:
        return "image"
    # Basic transliteration of common Vietnamese characters
    replacements = {
        'đ': 'd', 'Đ': 'D',
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y'
    }
    for k, v in replacements.items():
        text = text.replace(k, v).replace(k.upper(), v.upper())
    # Keep only alphanumeric and hyphen
    cleaned = re.sub(r'[^a-zA-Z0-9_\-]+', '-', text).strip('-')
    cleaned = re.sub(r'-+', '-', cleaned)
    return cleaned[:max_length] or "item"


def upgrade_image_url(url: str) -> str:
    """Upgrades BaoMoi CDN thumbnail URL to full resolution (w1200_r1)."""
    if not url or "photo-baomoi" not in url:
        return url
    return re.sub(r'/w\d+(?:_r[\dx]+)?/', '/w1200_r1/', url)


def parse_date_to_utc(val) -> Optional[datetime]:
    """Parses timestamps or ISO datetime strings into UTC datetime."""
    if not val:
        return None
    # Unix timestamp (seconds or milliseconds)
    if isinstance(val, (int, float)):
        if val > 1e11:
            val /= 1000.0
        try:
            return datetime.fromtimestamp(val, tz=timezone.utc)
        except Exception:
            return None
    if isinstance(val, str):
        val = val.strip()
        if not val:
            return None
        # String timestamp
        try:
            num = float(val)
            if num > 1e11:
                num /= 1000.0
            return datetime.fromtimestamp(num, tz=timezone.utc)
        except ValueError:
            pass
        # ISO format
        try:
            dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass
    return None


def is_within_24_hours(dt: Optional[datetime], max_hours: float = 24.0) -> (bool, Optional[float]):
    """Checks if article datetime is within max_hours of the current time."""
    if not dt:
        return False, None
    now_utc = datetime.now(timezone.utc)
    age_seconds = (now_utc - dt).total_seconds()
    age_hours = round(age_seconds / 3600.0, 2)
    # Allow 30 min future clock skew tolerance
    is_valid = (-1800 <= age_seconds <= max_hours * 3600)
    return is_valid, age_hours


# =====================================================================
# Main Crawler Class
# =====================================================================

class BaoMoiCrawler:
    """
    Crawls distinctive articles and high-resolution images from BaoMoi using BeautifulSoup.
    """

    def __init__(
        self,
        output_dir: str = "baomoi_images",
        max_images: int = 20,
        max_articles: int = 10,
        max_age_hours: float = 24.0,
        concurrency: int = 5,
        delay: float = 0.5,
        timeout: int = 15,
    ):
        """
        Args:
            output_dir: Output folder for images and metadata.
            max_images: Total maximum images to download.
            max_articles: Number of distinctive articles to collect images from.
            max_age_hours: Time constraint: only accept articles published within this window (default: 24h).
            concurrency: Parallel download workers.
            delay: Delay in seconds between article requests.
            timeout: HTTP request timeout.
        """
        self.output_dir = output_dir
        self.max_images = max_images
        self.max_articles = max_articles
        self.max_age_hours = max_age_hours
        self.concurrency = concurrency
        self.delay = delay
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "vi,en;q=0.9",
        })
        os.makedirs(self.output_dir, exist_ok=True)

    def _fetch_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Fetches page HTML and returns a parsed BeautifulSoup object."""
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            return BeautifulSoup(resp.text, "lxml")
        except Exception as e:
            logger.warning(f"Could not load {url}: {e}")
            return None

    def extract_article_links(self, soup: BeautifulSoup, base_url: str = "https://baomoi.com") -> List[str]:
        """Uses BeautifulSoup to find all article links ending with -c<id>.epi on the page."""
        links = []
        seen = set()
        article_pattern = re.compile(r'[-/]c\d+\.epi$')

        for a_tag in soup.find_all("a", href=True):
            clean_href = a_tag["href"].split("#")[0].split("?")[0].strip()
            if article_pattern.search(clean_href):
                full_url = urljoin(base_url, clean_href)
                if full_url not in seen:
                    seen.add(full_url)
                    links.append(full_url)
        return links

    def parse_article(self, article_url: str) -> Optional[dict]:
        """
        Uses BeautifulSoup to extract title, date, and unique images from an article.
        Enforces the 24-hour recency constraint.
        """
        soup = self._fetch_soup(article_url)
        if not soup:
            return None

        # 1. Title via BeautifulSoup
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else (soup.title.get_text(strip=True) if soup.title else "article")

        # 2. Publication Date via BeautifulSoup (meta / time / script)
        raw_date = None
        time_meta = soup.find("meta", property="article:published_time") or soup.find("meta", attrs={"name": "pubdate"})
        time_tag = soup.find("time")
        if time_meta and time_meta.get("content"):
            raw_date = time_meta["content"]
        elif time_tag and time_tag.get("datetime"):
            raw_date = time_tag["datetime"]

        # Fallback to Next.js data if tag missing
        script = soup.find("script", id="__NEXT_DATA__")
        next_data = None
        if script and script.string:
            try:
                next_data = json.loads(script.string)
                if not raw_date:
                    content_data = next_data.get("props", {}).get("pageProps", {}).get("resp", {}).get("data", {}).get("content", {})
                    raw_date = content_data.get("publishedDate") or content_data.get("date")
            except Exception:
                pass

        # 3. Check 24-Hour Constraint
        dt = parse_date_to_utc(raw_date)
        is_valid, age_hours = is_within_24_hours(dt, self.max_age_hours)
        if not is_valid:
            age_str = f"{age_hours}h ago" if age_hours is not None else "unknown date"
            logger.info(f"Skipping article '{title[:40]}' ({age_str} > {self.max_age_hours}h constraint)")
            return None

        # 4. Extract Distinctive Images (Avoid duplicate thumbnails)
        distinct_images = []
        seen_image_ids = set()

        # Primary source: Next.js structured content blocks
        if next_data:
            content_data = next_data.get("props", {}).get("pageProps", {}).get("resp", {}).get("data", {}).get("content", {})
            for item in content_data.get("bodys", []):
                if isinstance(item, dict) and item.get("type") == "image":
                    raw_img_url = item.get("contentOrigin") or item.get("content") or item.get("originUrl")
                    if raw_img_url and not any(k in raw_img_url.lower() for k in IGNORED_URL_KEYWORDS):
                        # Extract core filename ID to prevent duplicate resolutions of same image
                        img_id = raw_img_url.split("/")[-1].split("?")[0]
                        if img_id not in seen_image_ids:
                            seen_image_ids.add(img_id)
                            distinct_images.append({
                                "url": upgrade_image_url(raw_img_url),
                                "caption": item.get("caption") or item.get("title") or "",
                                "id": img_id
                            })

        # Secondary source: BeautifulSoup HTML tags (figure, og:image, img)
        if not distinct_images:
            for fig in soup.find_all("figure"):
                img_tag = fig.find("img")
                cap_tag = fig.find("figcaption")
                if img_tag:
                    src = img_tag.get("src") or img_tag.get("data-src")
                    if src and ("photo-baomoi" in src or "bmcdn.me" in src) and not any(k in src.lower() for k in IGNORED_URL_KEYWORDS):
                        img_id = src.split("/")[-1].split("?")[0]
                        if img_id not in seen_image_ids:
                            seen_image_ids.add(img_id)
                            distinct_images.append({
                                "url": upgrade_image_url(src),
                                "caption": cap_tag.get_text(strip=True) if cap_tag else "",
                                "id": img_id
                            })

            og_img = soup.find("meta", property="og:image")
            if og_img and og_img.get("content"):
                src = og_img["content"]
                img_id = src.split("/")[-1].split("?")[0]
                if img_id not in seen_image_ids:
                    seen_image_ids.add(img_id)
                    distinct_images.append({
                        "url": upgrade_image_url(src),
                        "caption": "",
                        "id": img_id
                    })

        if not distinct_images:
            return None

        # Vietnam local time ISO string (+07:00)
        formatted_date = dt.astimezone(timezone(timedelta(hours=7))).isoformat() if dt else ""

        return {
            "url": article_url,
            "title": title,
            "published_date": formatted_date,
            "article_age_hours": age_hours,
            "images": distinct_images
        }

    def _download_image(self, img_info: dict, article_title: str, article_url: str, pub_date: str, age_hours: float, folder: str, index: int) -> Optional[dict]:
        """Downloads a single image and writes it to disk."""
        url = img_info["url"]
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code != 200 or len(resp.content) < 1024:
                return None
            content = resp.content
        except Exception:
            return None

        ext = os.path.splitext(urlparse(url).path)[1].lower() or ".jpg"
        safe_name = f"{clean_filename(article_title, 35)}_{index:02d}{ext}"
        filepath = os.path.join(folder, safe_name)

        try:
            with open(filepath, "wb") as f:
                f.write(content)
        except Exception as e:
            logger.warning(f"Error saving image to {filepath}: {e}")
            return None

        return {
            "file_name": safe_name,
            "local_path": os.path.abspath(filepath),
            "image_url": url,
            "article_title": article_title,
            "article_url": article_url,
            "published_date": pub_date,
            "article_age_hours": age_hours,
            "caption": img_info.get("caption", ""),
            "file_size_bytes": len(content),
            "download_time": datetime.now().isoformat(),
        }

    def crawl(self, start_urls: List[str], category_name: str = "general") -> List[dict]:
        """
        Executes the crawl:
        - Finds candidate articles using BeautifulSoup.
        - Enforces the 24-hour constraint.
        - Distributes downloads across DISTINCT articles up to max_articles.
        - Ensures every image is DISTINCT.
        """
        logger.info(f"Starting crawl for [{category_name}]. Target: {self.max_images} images across {self.max_articles} articles (within {self.max_age_hours}h).")

        # 1. Discover article links using BeautifulSoup
        candidate_urls = []
        for start_url in start_urls:
            logger.info(f"Scanning page with BeautifulSoup: {start_url}")
            soup = self._fetch_soup(start_url)
            if not soup:
                continue
            links = self.extract_article_links(soup)
            for l in links:
                if l not in candidate_urls:
                    candidate_urls.append(l)

        logger.info(f"Discovered {len(candidate_urls)} candidate articles.")

        # 2. Determine balanced images per article to ensure distinct articles
        images_per_article = max(1, math.ceil(self.max_images / max(1, self.max_articles)))

        metadata_records = []
        seen_global_image_ids = set()
        articles_visited = 0
        pbar = tqdm(total=self.max_images, desc="Downloading Distinct Images", unit="img")

        for art_url in candidate_urls:
            if len(metadata_records) >= self.max_images:
                break
            if articles_visited >= self.max_articles:
                break

            # Parse article and check 24-hour constraint
            art_info = self.parse_article(art_url)
            if not art_info:
                continue

            # Select distinctive images from this article that have never been seen
            candidate_images = [img for img in art_info["images"] if img["id"] not in seen_global_image_ids]
            if not candidate_images:
                continue

            # Take up to images_per_article to guarantee multiple articles are used
            remaining_needed = self.max_images - len(metadata_records)
            take_count = min(images_per_article, remaining_needed, len(candidate_images))
            selected_images = candidate_images[:take_count]

            # Mark selected image IDs as seen
            for img in selected_images:
                seen_global_image_ids.add(img["id"])

            articles_visited += 1

            # Prepare article folder
            art_folder_name = clean_filename(art_info["title"], 45)
            target_folder = os.path.join(self.output_dir, category_name, art_folder_name)
            os.makedirs(target_folder, exist_ok=True)

            # Download selected images for this article
            for idx, img_info in enumerate(selected_images, 1):
                if len(metadata_records) >= self.max_images:
                    break
                rec = self._download_image(
                    img_info,
                    art_info["title"],
                    art_info["url"],
                    art_info["published_date"],
                    art_info["article_age_hours"],
                    target_folder,
                    idx
                )
                if rec:
                    metadata_records.append(rec)
                    pbar.update(1)

            if self.delay > 0:
                time.sleep(self.delay)

        pbar.close()

        # 3. Save metadata to JSON and CSV
        base_meta = os.path.join(self.output_dir, f"{category_name}_metadata")
        with open(base_meta + ".json", "w", encoding="utf-8") as f:
            json.dump(metadata_records, f, ensure_ascii=False, indent=2)

        if metadata_records:
            with open(base_meta + ".csv", "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=list(metadata_records[0].keys()))
                writer.writeheader()
                writer.writerows(metadata_records)

        distinct_articles_count = len(set(r["article_url"] for r in metadata_records))
        logger.info(
            f"Done! Downloaded {len(metadata_records)} distinctive images across {distinct_articles_count} distinctive articles (all within {self.max_age_hours}h)."
        )
        logger.info(f"Metadata saved to {base_meta}.json and .csv")
        return metadata_records

    def crawl_category(self, category_key: str) -> List[dict]:
        """Crawls a recognized category or custom category URL."""
        url = CATEGORIES.get(category_key, category_key if category_key.startswith("http") else f"https://baomoi.com/{category_key}.epi")
        return self.crawl([url], category_name=category_key)

    def crawl_query(self, query: str) -> List[dict]:
        """Crawls articles by search keyword on BaoMoi."""
        search_url = f"https://baomoi.com/tim-kiem/{quote(query.strip())}.epi"
        return self.crawl([search_url], category_name=f"search_{clean_filename(query, 20)}")


# Backward compatibility alias
BaoMoiImageCrawler = BaoMoiCrawler


# =====================================================================
# Command Line & Interactive UI
# =====================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Download distinctive images across distinctive articles within 24 hours using BeautifulSoup."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--category", type=str, help="Category to crawl (e.g. 'hot', 'tin-moi', 'cong-nghe', 'the-thao').")
    group.add_argument("-q", "--query", type=str, help="Search query keyword.")
    group.add_argument("-u", "--url", type=str, help="Direct article or listing URL.")
    group.add_argument("--list-categories", action="store_true", help="List available categories.")
    group.add_argument("-i", "--interactive", action="store_true", help="Launch interactive menu.")

    parser.add_argument("-n", "--max-images", type=int, default=20, help="Total maximum images to download (default: 20).")
    parser.add_argument("-a", "--max-articles", type=int, default=10, help="Number of distinct articles to collect from (default: 10).")
    parser.add_argument("--max-age-hours", type=float, default=24.0, help="Constraint: max article age in hours (default: 24.0).")
    parser.add_argument("-o", "--output-dir", type=str, default="baomoi_images", help="Output directory path (default: baomoi_images).")
    parser.add_argument("-d", "--delay", type=float, default=0.3, help="Politeness delay between requests (default: 0.3s).")
    return parser.parse_args()


def display_categories():
    print("\nRecognized Categories:")
    print("-" * 50)
    for k, v in CATEGORIES.items():
        print(f"  • {k.ljust(20)} -> {v}")
    print("-" * 50)


def interactive_mode():
    print("\n=============================================================")
    print("      B A O M O I   C R A W L E R   (BeautifulSoup)          ")
    print("  Distinctive Images & Articles within 24-Hour Constraint    ")
    print("=============================================================")
    print("Select Mode:")
    print("  1. Hot / Trending News (Homepage)")
    print("  2. Latest News (tin-moi)")
    print("  3. Specific Category (e.g. cong-nghe, the-thao, kinh-te)")
    print("  4. Search by Keyword")
    print("  5. View Available Categories")
    print("  6. Exit")

    choice = input("\nEnter choice (1-6) [default: 1]: ").strip() or "1"
    if choice == "6":
        sys.exit(0)
    if choice == "5":
        display_categories()
        return interactive_mode()

    max_images_input = input("Enter max images to download [default: 10]: ").strip()
    max_images = int(max_images_input) if max_images_input.isdigit() else 10

    max_articles_input = input("Enter max distinct articles to visit [default: 5]: ").strip()
    max_articles = int(max_articles_input) if max_articles_input.isdigit() else 5

    max_age_input = input("Enter max article age in hours [default: 24 (within 24h)]: ").strip()
    try:
        max_age_hours = float(max_age_input) if max_age_input else 24.0
    except ValueError:
        max_age_hours = 24.0

    crawler = BaoMoiCrawler(
        output_dir="baomoi_images",
        max_images=max_images,
        max_articles=max_articles,
        max_age_hours=max_age_hours,
    )

    if choice == "1":
        crawler.crawl_category("hot")
    elif choice == "2":
        crawler.crawl_category("tin-moi")
    elif choice == "3":
        display_categories()
        cat = input("\nEnter category code: ").strip().lower()
        crawler.crawl_category(cat)
    elif choice == "4":
        q = input("\nEnter search keyword: ").strip()
        crawler.crawl_query(q)
    else:
        crawler.crawl_category("hot")


def main():
    args = parse_args()
    if args.list_categories:
        display_categories()
        return
    if len(sys.argv) == 1 or args.interactive:
        interactive_mode()
        return

    crawler = BaoMoiCrawler(
        output_dir=args.output_dir,
        max_images=args.max_images,
        max_articles=args.max_articles,
        max_age_hours=args.max_age_hours,
        delay=args.delay,
    )

    if args.category:
        crawler.crawl_category(args.category)
    elif args.query:
        crawler.crawl_query(args.query)
    elif args.url:
        crawler.crawl([args.url], category_name="custom_url")
    else:
        crawler.crawl_category("hot")


if __name__ == "__main__":
    main()
