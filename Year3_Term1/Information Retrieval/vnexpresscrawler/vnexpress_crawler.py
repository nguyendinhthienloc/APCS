"""
VnExpress 24-Hour News Crawler (Beginner-Friendly Edition)
==========================================================
Course: Information Retrieval

What this crawler does:
1. Crawls VnExpress (24h news stream + all major categories) to discover articles.
2. Filters articles so ONLY those published within the last 24 hours are kept.
3. Uses BeautifulSoup (`bs4`) to parse HTML and extract:
   - Article Name (Title)
   - Article Images (both URLs and downloaded image files on disk)
   - Total Number of Comments
   - The Most Liked Comment (text, author, and like count)
4. Saves the extracted dataset to both JSON (`vnexpress_articles_24h.json`)
   and CSV (`vnexpress_articles_24h.csv`).

Note for Beginners:
This file is heavily documented! Look for "PYTHON SYNTAX NOTE" comments
throughout the code to learn how specific Python constructs work.
"""

import os
import re
import csv
import json
import time
import argparse
from datetime import datetime, timezone, timedelta
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


# ==============================================================================
# 1. CONFIGURATION & CONSTANTS
# ==============================================================================

BASE_URL = "https://vnexpress.net"

# All major categories on VnExpress, starting with the 24-hour latest news stream.
# Using a Python dictionary (`{key: value}`) maps each category slug to its URL.
VNEXPRESS_CATEGORIES = {
    "tin-tuc-24h": "https://vnexpress.net/tin-tuc-24h",
    "thoi-su": "https://vnexpress.net/thoi-su",
    "the-gioi": "https://vnexpress.net/the-gioi",
    "kinh-doanh": "https://vnexpress.net/kinh-doanh",
    "bat-dong-san": "https://vnexpress.net/bat-dong-san",
    "khoa-hoc-cong-nghe": "https://vnexpress.net/khoa-hoc-cong-nghe",
    "giai-tri": "https://vnexpress.net/giai-tri",
    "the-thao": "https://vnexpress.net/the-thao",
    "phap-luat": "https://vnexpress.net/phap-luat",
    "giao-duc": "https://vnexpress.net/giao-duc",
    "suc-khoe": "https://vnexpress.net/suc-khoe",
    "doi-song": "https://vnexpress.net/doi-song",
    "du-lich": "https://vnexpress.net/du-lich",
    "oto-xe-may": "https://vnexpress.net/oto-xe-may",
    "y-kien": "https://vnexpress.net/y-kien",
    "tam-su": "https://vnexpress.net/tam-su",
    "goc-nhin": "https://vnexpress.net/goc-nhin",
}

# Standard browser User-Agent header.
# Websites often block scripts that identify themselves as "python-requests".
# Sending this header tells the server to treat our request like a normal Chrome browser.
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
}

# VnExpress loads reader comments dynamically via this JSON API endpoint.
COMMENT_API_URL = "https://usi-saas.vnexpress.net/index/get"


# ==============================================================================
# 2. HELPER FUNCTIONS
# ==============================================================================

def fetch_webpage_html(url, timeout=15):
    """
    Downloads the HTML source code of a webpage.

    Logic:
    - Sends an HTTP GET request to `url`.
    - Checks if the status code is 200 (OK).
    - Returns the HTML text if successful, or `None` if an error occurs.

    PYTHON SYNTAX NOTE (`try ... except`):
    Network requests can fail at any time (no internet, slow server, broken link).
    Wrapping the request in `try ... except Exception as error:` catches any crash
    and lets the crawler safely skip the bad page instead of stopping the whole program.
    """
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=timeout)
        if response.status_code == 200:
            # Force UTF-8 encoding so Vietnamese characters (e.g., ă, â, đ, ê) display properly
            response.encoding = "utf-8"
            return response.text
        else:
            # PYTHON SYNTAX NOTE (`f"..."` f-string):
            # Placing an `f` before a string lets you insert variables directly inside `{}`!
            print(f"  [Warning] Server returned status {response.status_code} for {url}")
            return None
    except Exception as error:
        print(f"  [Error] Could not fetch {url}: {error}")
        return None


def extract_article_id_from_url(url):
    """
    Extracts the numeric article ID from a VnExpress URL.
    Example:
      Input:  "https://vnexpress.net/gia-dau-cham-moc-115-usd-5136174.html"
      Output: "5136174"

    Logic:
    - VnExpress article URLs end with `-<digits>.html`.
    - We use a Regular Expression (`re.search`) to capture the digits right before `.html`.

    PYTHON SYNTAX NOTE (`r"..."` raw string):
    Putting `r` before a string tells Python not to treat backslashes `\` as escape
    characters. In regex, `\d+` means "one or more digits (0-9)", and `\.` means a literal dot.
    """
    match = re.search(r"-(\d+)\.html", url)
    if match:
        # `match.group(1)` returns the text inside the first parentheses `(\d+)`
        return match.group(1)
    return None


def normalize_article_url(raw_url):
    """
    Cleans up an article link found on a listing page.

    Logic:
    1. Converts relative paths (like `/bai-viet-123.html`) to full URLs (`https://vnexpress.net/...`).
    2. Removes URL fragments (like `#box_comment_vne`) and query strings (`?vn_source=...`)
       so we don't crawl the same article twice under slightly different links.
    3. Keeps only valid `.html` article URLs on `vnexpress.net`.
    """
    if not raw_url:
        return None

    # Convert relative URL to absolute URL
    full_url = urljoin(BASE_URL, raw_url)

    # PYTHON SYNTAX NOTE (`.split("#")[0]`):
    # `.split("#")` breaks a string into a list of pieces wherever "#" appears.
    # `[0]` grabs the very first piece (everything before the "#").
    clean_url = full_url.split("#")[0].split("?")[0].strip()

    # Check that it belongs to vnexpress.net and has a numeric article ID ending in .html
    parsed = urlparse(clean_url)
    if not parsed.netloc.endswith("vnexpress.net"):
        return None

    if extract_article_id_from_url(clean_url) is None:
        return None

    return clean_url


def make_safe_filename(text, max_length=50):
    """
    Turns an article title or image name into a safe filename for Windows/macOS/Linux.

    Logic:
    - Replaces non-alphanumeric characters (like `/`, `:`, `?`, quotes) with underscores.
    - Trims the string to `max_length` characters so file paths don't get too long.

    PYTHON SYNTAX NOTE (`text[:max_length]` Slicing):
    In Python, `my_string[:50]` slices the string from the beginning up to index 50.
    If the string is shorter than 50 characters, Python safely returns the whole string
    without throwing an "index out of bounds" error!
    """
    if not text:
        return "image"

    # Replace anything that is not a letter, number, or hyphen with an underscore
    safe_text = re.sub(r"[^a-zA-Z0-9\-]+", "_", text)
    # Remove leading or trailing underscores
    safe_text = safe_text.strip("_")

    if not safe_text:
        return "image"

    return safe_text[:max_length]


# ==============================================================================
# 3. BEAUTIFUL SOUP PARSING FUNCTIONS (HTML -> STRUCTURED DATA)
# ==============================================================================

def parse_article_links_from_listing(html_text):
    """
    Uses BeautifulSoup to extract all article URLs from a category or 24h listing page.

    Logic:
    - Parses the HTML into a BeautifulSoup tree object.
    - Looks for `<article class="item-news">` blocks (which VnExpress uses for news cards),
      as well as `<h3 class="title-news">` / `<h2 class="title-news">` links.
    - Returns a deduplicated list of clean article URLs in the order they appear.

    PYTHON SYNTAX NOTE (`class_="..."`):
    In BeautifulSoup, we write `class_="item-news"` with an underscore at the end.
    Why? Because `class` is a reserved keyword in Python (used to define classes)!
    Adding the trailing underscore avoids a Python syntax error.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    found_urls = []
    seen_urls = set()  # A `set` stores unique items and checks `x in seen_urls` instantly.

    # Find all `<article>` tags that represent news items on the page
    article_tags = soup.find_all("article", class_="item-news")

    for article_tag in article_tags:
        # Look for the first `<a>` (anchor/hyperlink) tag inside the article card
        link_tag = article_tag.find("a", href=True)
        if link_tag:
            raw_href = link_tag.get("href")
            clean_url = normalize_article_url(raw_href)

            if clean_url and clean_url not in seen_urls:
                seen_urls.add(clean_url)
                found_urls.append(clean_url)

    return found_urls


def extract_publication_datetime(soup):
    """
    Extracts the exact publication date and time of an article using BeautifulSoup.

    Logic (Multi-step fallback for robustness):
    1. First, checks `<meta name="pubdate" content="2026-10-23T20:39:28+07:00">` in `<head>`.
       This is the cleanest ISO-8601 timestamp.
    2. Second, checks `<meta name="its_publication" content="1792762768">` (Unix timestamp).
    3. Third, checks the visible `<span class="date">` text inside the article header
       (e.g., "Thứ sáu, 23/10/2026, 20:39 (GMT+7)").

    Returns:
    - A timezone-aware `datetime` object (in UTC+7), or `None` if no date could be found.
    """
    vietnam_tz = timezone(timedelta(hours=7))

    # Method 1: Check `<meta name="pubdate">` or `<meta property="article:published_time">`
    meta_pubdate = (
        soup.find("meta", attrs={"name": "pubdate"})
        or soup.find("meta", attrs={"itemprop": "datePublished"})
        or soup.find("meta", attrs={"property": "article:published_time"})
    )

    # PYTHON SYNTAX NOTE (`dict.get("key")`):
    # In BeautifulSoup, HTML tag attributes act like a Python dictionary.
    # Using `meta_pubdate.get("content")` safely returns `None` if the `content` attribute
    # is missing, whereas `meta_pubdate["content"]` would crash with a `KeyError`!
    if meta_pubdate and meta_pubdate.get("content"):
        iso_string = meta_pubdate.get("content").strip()
        try:
            return datetime.fromisoformat(iso_string)
        except ValueError:
            pass  # `pass` means "do nothing and continue to the fallback method below"

    # Method 2: Check `<meta name="its_publication">` (Unix epoch seconds)
    meta_timestamp = soup.find("meta", attrs={"name": "its_publication"})
    if meta_timestamp and meta_timestamp.get("content"):
        raw_ts = meta_timestamp.get("content").strip()
        if raw_ts.isdigit():
            return datetime.fromtimestamp(int(raw_ts), tz=vietnam_tz)

    # Method 3: Parse visible Vietnamese date string `<span class="date">`
    # Example text: "Thứ sáu, 23/10/2026, 20:39 (GMT+7)"
    date_span = soup.find("span", class_="date")
    if date_span:
        date_text = date_span.get_text(strip=True)
        match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4}),\s*(\d{1,2}):(\d{2})", date_text)
        if match:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))
            hour = int(match.group(4))
            minute = int(match.group(5))
            return datetime(year, month, day, hour, minute, tzinfo=vietnam_tz)

    return None


def extract_article_title(soup):
    """
    Extracts the article's headline/title using BeautifulSoup.

    Logic:
    1. Looks for `<h1 class="title-detail">` (standard VnExpress article title).
    2. Falls back to `<h1 class="title-gn">` (used in "Góc nhìn" opinion columns)
       or any `<h1>` tag on the page.
    3. Falls back to `<meta property="og:title">` in `<head>`.
    """
    title_tag = (
        soup.find("h1", class_="title-detail")
        or soup.find("h1", class_="title-gn")
        or soup.find("h1")
    )
    if title_tag:
        # `get_text(strip=True)` removes all inner HTML tags and trims extra whitespace
        return title_tag.get_text(strip=True)

    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content"):
        return og_title.get("content").strip()

    return "Untitled Article"


def extract_article_category(soup, default_category="unknown"):
    """
    Extracts the category name of the article from the HTML breadcrumb or meta tags.
    """
    # Check breadcrumb `<ul class="breadcrumb"><li><a>Category Name</a></li></ul>`
    breadcrumb = soup.find("ul", class_="breadcrumb")
    if breadcrumb:
        first_link = breadcrumb.find("a")
        if first_link:
            return first_link.get_text(strip=True)

    # Fallback to `<meta itemprop="articleSection" content="Pháp luật">`
    meta_section = soup.find("meta", attrs={"itemprop": "articleSection"})
    if meta_section and meta_section.get("content"):
        return meta_section.get("content").strip()

    return default_category


def extract_article_images(soup):
    """
    Extracts all valid article image URLs using BeautifulSoup.

    IMPORTANT INFORMATION RETRIEVAL / WEB CRAWLING NOTE (Lazy Loading):
    On modern news sites like VnExpress, images inside the article body use "lazy loading"
    to save bandwidth. That means the standard `<img src="...">` attribute actually contains
    a tiny 1x1 blank placeholder (`data:image/gif;base64,...`)!
    The REAL high-resolution image URL is stored inside:
      - `img.get("data-src")`, OR
      - `<meta itemprop="url" content="...">` inside `<figure>`, OR
      - `<meta property="og:image">` for the main article thumbnail.
    This function checks those attributes so we always get the real photos!
    """
    image_urls = []
    seen_base_paths = set()

    def add_image_if_new(url):
        """Inner helper function to validate and deduplicate image URLs."""
        if not url:
            return
        url = url.strip()
        # Ignore base64 placeholder gifs, SVGs, or site logos/icons
        if url.startswith("data:image") or ".svg" in url.lower() or "logos/" in url.lower():
            return
        if not url.startswith("http"):
            return

        # Deduplicate using the base URL path (without `?w=...` resize query parameters)
        base_path = url.split("?")[0]
        if base_path not in seen_base_paths:
            seen_base_paths.add(base_path)
            image_urls.append(url)

    # 1. Extract images inside the main article body (`<article class="fck_detail">`)
    article_body = soup.find("article", class_="fck_detail") or soup

    # Check `<figure>` blocks first (VnExpress wraps article photos in `<figure>`)
    for figure in article_body.find_all("figure"):
        meta_url = figure.find("meta", attrs={"itemprop": "url"})
        if meta_url and meta_url.get("content"):
            add_image_if_new(meta_url.get("content"))

        img_tag = figure.find("img")
        if img_tag:
            # Prefer `data-src` over `src` because of lazy loading!
            real_img_url = img_tag.get("data-src") or img_tag.get("src")
            add_image_if_new(real_img_url)

    # Also check any standalone `<img>` tags inside the article body
    if article_body != soup:
        for img_tag in article_body.find_all("img"):
            real_img_url = img_tag.get("data-src") or img_tag.get("src")
            add_image_if_new(real_img_url)

    # 2. If the article body had no inline photos (or in addition to them),
    # check the OpenGraph main thumbnail `<meta property="og:image">`
    og_image = soup.find("meta", attrs={"property": "og:image"})
    if og_image and og_image.get("content"):
        og_url = og_image.get("content")
        # Skip VnExpress default fallback logo thumbnail
        if "default/thumb" not in og_url:
            add_image_if_new(og_url)

    return image_urls


def download_article_images(image_urls, article_id, output_Root_folder):
    """
    Downloads the extracted image URLs to a local folder on disk.

    Folder structure:
      `<output_Root_folder>/<article_id>/image_1.jpg`, `image_2.jpg`, ...

    PYTHON SYNTAX NOTE (`os.makedirs(..., exist_ok=True)`):
    `os.makedirs` creates the folder (and any parent folders needed).
    Setting `exist_ok=True` tells Python: "If the folder already exists, don't crash!"

    PYTHON SYNTAX NOTE (`enumerate(image_urls, start=1)`):
    When looping over a list, `enumerate(..., start=1)` gives us TWO things on each step:
    the counter number (`index`: 1, 2, 3...) AND the item itself (`img_url`).
    """
    if not image_urls:
        return []

    article_image_folder = os.path.join(output_Root_folder, str(article_id))
    os.makedirs(article_image_folder, exist_ok=True)

    saved_file_paths = []

    for index, img_url in enumerate(image_urls, start=1):
        try:
            # Determine file extension (.jpg, .png, .webp) from the URL path
            url_path = img_url.split("?")[0]
            _, extension = os.path.splitext(url_path)
            if extension.lower() not in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
                extension = ".jpg"

            filename = f"article_{article_id}_img_{index}{extension}"
            local_path = os.path.join(article_image_folder, filename)

            # Download the image bytes
            response = requests.get(img_url, headers=REQUEST_HEADERS, timeout=15)
            if response.status_code == 200:
                # PYTHON SYNTAX NOTE (`with open(local_path, "wb") as img_file:`):
                # - `"wb"` means "Write Binary" mode (used for images, PDFs, audio, etc.,
                #   as opposed to `"w"` which is for plain text).
                # - The `with` statement is a Context Manager: it automatically closes
                #   the file as soon as the indented block finishes!
                with open(local_path, "wb") as img_file:
                    img_file.write(response.content)
                saved_file_paths.append(local_path)
        except Exception as error:
            print(f"    [Warning] Failed to download image {img_url}: {error}")

    return saved_file_paths


# ==============================================================================
# 4. COMMENTS & MOST-LIKED COMMENT EXTRACTION
# ==============================================================================

def fetch_article_comments_info(soup, article_id):
    """
    Extracts the total number of comments and the most liked comment for an article.

    Why do we combine BeautifulSoup + a JSON API request here?
    - In VnExpress's HTML, the comments themselves are not pre-rendered in the initial HTML.
    - Instead, VnExpress puts a `<div id="box_comment_vne" data-component-input='{...}'>`
      tag in the HTML containing the `article_id`, `site_id`, `category_id`, and `sign`.
    - The browser's JavaScript reads that `<div>` and calls `https://usi-saas.vnexpress.net/index/get`.
    - So we use BeautifulSoup to extract those parameters from the HTML, call the exact
      same endpoint, and then use BeautifulSoup again to strip any HTML tags (`<br/>`, `&nbsp;`)
      inside the comment text!
    """
    # Default values in case the article has 0 comments
    result = {
        "total_comments": 0,
        "top_level_comments": 0,
        "most_liked_comment_text": "",
        "most_liked_comment_author": "",
        "most_liked_comment_likes": 0,
    }

    # Step 1: Extract comment widget configuration from HTML using BeautifulSoup
    site_id = "1000000"
    category_id = ""
    object_type = "1"
    sign_token = ""

    comment_box = soup.find("div", id="box_comment_vne")
    if comment_box and comment_box.get("data-component-input"):
        try:
            config_json = json.loads(comment_box.get("data-component-input"))
            article_id = str(config_json.get("article_id", article_id))
            site_id = str(config_json.get("site_id", site_id))
            category_id = str(config_json.get("category_id", ""))
            object_type = str(config_json.get("article_type", "1"))
            sign_token = str(config_json.get("sign", ""))
        except Exception:
            pass

    # Fallback: read `<meta name="tt_category_id">` and `<meta name="tt_site_id">`
    if not category_id:
        meta_cat = soup.find("meta", attrs={"name": "tt_category_id"})
        if meta_cat and meta_cat.get("content"):
            category_id = meta_cat.get("content").strip()

    # Step 2: Query VnExpress's comment microservice (`sort=like` gets most-liked first)
    query_params = {
        "offset": 0,
        "limit": 24,
        "frommobile": 0,
        "sort": "like",
        "is_onload": 1,
        "objectid": article_id,
        "objecttype": object_type,
        "siteid": site_id,
        "categoryid": category_id,
        "tab_active": "most_like",
    }
    if sign_token:
        query_params["sign"] = sign_token

    try:
        response = requests.get(
            COMMENT_API_URL,
            params=query_params,
            headers=REQUEST_HEADERS,
            timeout=10,
        )
        if response.status_code != 200:
            return result

        json_data = response.json()
        data_block = json_data.get("data", {})

        # Sometimes `data` is an empty list `[]` instead of a dict `{}` when comments are disabled
        if not isinstance(data_block, dict):
            return result

        # `totalitem` includes both top-level comments and replies; `total` is top-level comments
        top_level_count = int(data_block.get("total", 0) or 0)
        total_with_replies = int(data_block.get("totalitem", top_level_count) or 0)

        result["total_comments"] = total_with_replies
        result["top_level_comments"] = top_level_count

        comment_items = data_block.get("items", [])
        if not comment_items:
            return result

        # Step 3: Find the comment with the highest number of likes (`userlike`)
        # Even though `sort=like` usually places the top comment first, we loop through
        # all returned comments explicitly to be 100% sure we pick the maximum `userlike`.
        best_comment = None
        max_likes = -1

        for comment in comment_items:
            likes = int(comment.get("userlike", 0) or 0)
            if likes > max_likes:
                max_likes = likes
                best_comment = comment

        if best_comment:
            raw_content = best_comment.get("content", "")
            # Use BeautifulSoup to clean HTML tags like `<br />` and entities like `&nbsp;`
            clean_comment_text = BeautifulSoup(raw_content, "html.parser").get_text(
                separator=" ", strip=True
            )
            result["most_liked_comment_text"] = clean_comment_text
            result["most_liked_comment_author"] = best_comment.get("full_name", "Anonymous")
            result["most_liked_comment_likes"] = max_likes

    except Exception as error:
        print(f"    [Warning] Could not fetch comments for article {article_id}: {error}")

    return result


# ==============================================================================
# 5. SINGLE ARTICLE PROCESSOR & 24-HOUR FILTER
# ==============================================================================

def process_single_article(article_url, current_time, max_age_hours=24.0,
                           download_images=True, images_folder="downloaded_images"):
    """
    Downloads and parses a single VnExpress article.

    Returns:
      A tuple `(status, article_data_dict)`:
      - `status == "ok"`: Article is within 24 hours and was successfully extracted.
      - `status == "too_old"`: Article was published more than `max_age_hours` ago.
      - `status == "skip"`: Page could not be fetched or has no valid publication date.

    PYTHON SYNTAX NOTE (Returning a Tuple `return "ok", article_data`):
    Python functions can return multiple values separated by a comma!
    The caller can unpack them directly like:
        `status, data = process_single_article(...)`
    """
    article_id = extract_article_id_from_url(article_url)
    if not article_id:
        return "skip", None

    html_text = fetch_webpage_html(article_url)
    if not html_text:
        return "skip", None

    soup = BeautifulSoup(html_text, "html.parser")

    # 1. Check publication date (24-Hour Recency Constraint)
    pub_datetime = extract_publication_datetime(soup)
    if pub_datetime is None:
        return "skip", None

    # Calculate how many hours ago the article was published
    time_difference = current_time - pub_datetime
    age_in_hours = time_difference.total_seconds() / 3600.0

    # If the article is older than 24 hours, reject it!
    if age_in_hours > max_age_hours:
        return "too_old", {"age_hours": round(age_in_hours, 2), "published_time": pub_datetime.isoformat()}

    # 2. Extract Title & Category
    title = extract_article_title(soup)
    category = extract_article_category(soup)

    # 3. Extract Image URLs & Optionally Download Image Files
    image_urls = extract_article_images(soup)
    downloaded_paths = []
    if download_images and image_urls:
        downloaded_paths = download_article_images(image_urls, article_id, images_folder)

    # 4. Extract Comment Count & Most Liked Comment
    comment_info = fetch_article_comments_info(soup, article_id)

    # 5. Assemble the complete dictionary for this article
    article_data = {
        "article_id": article_id,
        "article_title": title,
        "article_url": article_url,
        "category": category,
        "published_time": pub_datetime.isoformat(),
        "age_hours": round(age_in_hours, 2),
        "image_count": len(image_urls),
        "image_urls": image_urls,
        "downloaded_image_paths": downloaded_paths,
        "total_comments": comment_info["total_comments"],
        "top_level_comments": comment_info["top_level_comments"],
        "most_liked_comment_text": comment_info["most_liked_comment_text"],
        "most_liked_comment_author": comment_info["most_liked_comment_author"],
        "most_liked_comment_likes": comment_info["most_liked_comment_likes"],
    }

    return "ok", article_data


# ==============================================================================
# 6. SAVING DATA TO JSON & CSV
# ==============================================================================

def save_results_to_json(articles_list, json_filepath):
    """
    Saves the list of extracted article dictionaries to a formatted JSON file.

    PYTHON SYNTAX NOTE (`ensure_ascii=False` and `indent=2`):
    - `ensure_ascii=False` writes Vietnamese characters directly (like "Thời sự")
      instead of escaped Unicode codes (like "\\u0111").
    - `indent=2` pretty-prints the JSON with 2-space indentation so humans can read it!
    """
    with open(json_filepath, "w", encoding="utf-8") as json_file:
        json.dump(articles_list, json_file, ensure_ascii=False, indent=2)


def save_results_to_csv(articles_list, csv_filepath):
    """
    Saves the list of extracted articles to a CSV spreadsheet file.

    Note:
    - Because a CSV cell can only hold plain text (not a Python list), we join
      `image_urls` and `downloaded_image_paths` with `" | "` inside the CSV.
    - We use `encoding="utf-8-sig"` (UTF-8 with BOM) so Microsoft Excel opens
      Vietnamese characters properly without garbled text!
    """
    fieldnames = [
        "article_id",
        "article_title",
        "category",
        "published_time",
        "age_hours",
        "total_comments",
        "top_level_comments",
        "most_liked_comment_likes",
        "most_liked_comment_author",
        "most_liked_comment_text",
        "image_count",
        "image_urls",
        "downloaded_image_paths",
        "article_url",
    ]

    with open(csv_filepath, "w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for item in articles_list:
            # Make a shallow copy of the dictionary so we can convert lists to strings for CSV
            row = dict(item)
            # PYTHON SYNTAX NOTE (`" | ".join(my_list)`):
            # `.join()` takes a list of strings and glues them together into one string,
            # putting `" | "` between each element.
            row["image_urls"] = " | ".join(item.get("image_urls", []))
            row["downloaded_image_paths"] = " | ".join(item.get("downloaded_image_paths", []))
            writer.writerow(row)


# ==============================================================================
# 7. MAIN CRAWLER LOOP (ALL CATEGORIES, LAST 24 HOURS)
# ==============================================================================

def crawl_vnexpress_last_24h(
    categories_to_crawl=None,
    max_articles=None,
    max_pages_per_category=10,
    max_age_hours=24.0,
    download_images=True,
    output_dir=".",
    delay_seconds=0.3,
):
    """
    Main function that crawls VnExpress categories and collects all articles
    published in the last 24 hours.

    How pagination & stopping works:
    - For each category (e.g., `https://vnexpress.net/tin-tuc-24h`), page 1 is the base URL,
      page 2 is `...-p2`, page 3 is `...-p3`, and so on.
    - On each page, we extract all article links and visit each unvisited article.
    - Since articles are listed newest-first, once we see several old articles (> 24h)
      in a row on a category page, we know we've passed the 24-hour window for that
      category and can move on to the next category!
    """
    os.makedirs(output_dir, exist_ok=True)
    images_folder = os.path.join(output_dir, "downloaded_images")
    json_filepath = os.path.join(output_dir, "vnexpress_articles_24h.json")
    csv_filepath = os.path.join(output_dir, "vnexpress_articles_24h.csv")

    if categories_to_crawl is None:
        categories_to_crawl = VNEXPRESS_CATEGORIES

    # Current time in Vietnam timezone (UTC+7)
    vietnam_tz = timezone(timedelta(hours=7))
    current_time = datetime.now(vietnam_tz)

    collected_articles = []
    visited_article_ids = set()

    print("=" * 75)
    print("Starting VnExpress 24-Hour Crawler")
    print(f"Current Time (GMT+7): {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Categories   : {len(categories_to_crawl)} categories")
    print(f"Max Articles Limit  : {'No limit (All 24h articles)' if not max_articles else max_articles}")
    print(f"Download Images     : {download_images} -> {os.path.abspath(images_folder)}")
    print("=" * 75)

    # PYTHON SYNTAX NOTE (`.items()` on a dictionary):
    # Looping over `categories_to_crawl.items()` gives us both the key (`cat_slug`)
    # and the value (`cat_url`) at the same time!
    for cat_slug, cat_url in categories_to_crawl.items():
        print(f"\n>>> Crawling Section: [{cat_slug}] ({cat_url})")

        for page_num in range(1, max_pages_per_category + 1):
            if page_num == 1:
                page_url = cat_url
            else:
                page_url = f"{cat_url}-p{page_num}"

            print(f"  [Page {page_num}] Fetching listing: {page_url}")
            listing_html = fetch_webpage_html(page_url)
            if not listing_html:
                break

            article_links = parse_article_links_from_listing(listing_html)
            if not article_links:
                print(f"  [Page {page_num}] No article links found. Moving to next section.")
                break

            new_articles_on_page = 0
            old_articles_in_a_row = 0

            for article_url in article_links:
                article_id = extract_article_id_from_url(article_url)
                if not article_id or article_id in visited_article_ids:
                    continue

                visited_article_ids.add(article_id)

                # Polite delay so we don't overload VnExpress servers
                if delay_seconds > 0:
                    time.sleep(delay_seconds)

                # Update `current_time` so age calculation stays accurate during long crawls
                current_time = datetime.now(vietnam_tz)

                status, data = process_single_article(
                    article_url=article_url,
                    current_time=current_time,
                    max_age_hours=max_age_hours,
                    download_images=download_images,
                    images_folder=images_folder,
                )

                if status == "ok":
                    old_articles_in_a_row = 0
                    new_articles_on_page += 1
                    collected_articles.append(data)

                    # Print a friendly summary of the extracted article
                    print(
                        f"    + [{len(collected_articles)}] {data['article_title'][:60]}... "
                        f"| Age: {data['age_hours']}h "
                        f"| Images: {data['image_count']} "
                        f"| Comments: {data['total_comments']} "
                        f"(Top Likes: {data['most_liked_comment_likes']})"
                    )

                    # Save progress every 10 articles in case the user stops the script early
                    if len(collected_articles) % 10 == 0:
                        save_results_to_json(collected_articles, json_filepath)
                        save_results_to_csv(collected_articles, csv_filepath)

                    # Check if we reached the user's `--max-articles` limit
                    if max_articles and len(collected_articles) >= max_articles:
                        print(f"\nReached max_articles limit ({max_articles}). Stopping crawl.")
                        save_results_to_json(collected_articles, json_filepath)
                        save_results_to_csv(collected_articles, csv_filepath)
                        return collected_articles

                elif status == "too_old":
                    old_articles_in_a_row += 1
                    # Category pages sometimes have 1 or 2 pinned older stories at the top.
                    # Wait until we see 5 old articles in a row before stopping pagination
                    # for this category.
                    if old_articles_in_a_row >= 5:
                        print(
                            f"  [Page {page_num}] Reached articles older than {max_age_hours}h "
                            f"({data['age_hours']}h old). Moving to next category."
                        )
                        break

            # If we hit 5 old articles in a row, stop paginating this category
            if old_articles_in_a_row >= 5:
                break

            # If an entire page had 0 new 24h articles and we're past page 1, stop paginating
            if page_num >= 2 and new_articles_on_page == 0:
                break

    # Save final JSON and CSV files
    save_results_to_json(collected_articles, json_filepath)
    save_results_to_csv(collected_articles, csv_filepath)

    print("\n" + "=" * 75)
    print(f"Crawl Complete! Extracted {len(collected_articles)} articles from the last 24 hours.")
    print(f"JSON saved to : {os.path.abspath(json_filepath)}")
    print(f"CSV saved to  : {os.path.abspath(csv_filepath)}")
    if download_images:
        print(f"Images folder : {os.path.abspath(images_folder)}")
    print("=" * 75)

    return collected_articles


# ==============================================================================
# 8. COMMAND-LINE INTERFACE (ENTRY POINT)
# ==============================================================================

def main():
    """
    Parses optional command-line arguments so you can either:
    1. Run `python vnexpress_crawler.py` to crawl ALL 24h articles across all categories.
    2. Run `python vnexpress_crawler.py --max-articles 10` for a quick 10-article test.
    3. Run `python vnexpress_crawler.py --category cong-nghe` for a single category.
    """
    parser = argparse.ArgumentParser(
        description="Beginner-Friendly VnExpress 24-Hour News Crawler using BeautifulSoup."
    )
    parser.add_argument(
        "--max-articles",
        type=int,
        default=None,
        help="Optional limit on number of articles to crawl (default: None = crawl all 24h articles).",
    )
    parser.add_argument(
        "--category",
        type=str,
        default="all",
        help="Category slug to crawl (e.g., 'tin-tuc-24h', 'thoi-su', 'the-thao') or 'all' (default).",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Maximum pagination pages to check per category (default: 10).",
    )
    parser.add_argument(
        "--no-download-images",
        action="store_true",
        help="Only save image URLs in JSON/CSV without downloading image files to disk.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=os.path.dirname(os.path.abspath(__file__)),
        help="Directory where JSON, CSV, and downloaded_images/ will be saved.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.25,
        help="Polite delay in seconds between article requests (default: 0.25).",
    )

    args = parser.parse_args()

    # Select categories based on `--category` argument
    if args.category.lower() == "all":
        selected_categories = VNEXPRESS_CATEGORIES
    elif args.category in VNEXPRESS_CATEGORIES:
        selected_categories = {args.category: VNEXPRESS_CATEGORIES[args.category]}
    else:
        print(f"Unknown category '{args.category}'. Available categories:")
        for slug in VNEXPRESS_CATEGORIES:
            print(f"  - {slug}")
        return

    crawl_vnexpress_last_24h(
        categories_to_crawl=selected_categories,
        max_articles=args.max_articles,
        max_pages_per_category=args.max_pages,
        max_age_hours=24.0,
        download_images=not args.no_download_images,
        output_dir=args.output_dir,
        delay_seconds=args.delay,
    )


# PYTHON SYNTAX NOTE (`if __name__ == "__main__":`):
# Every Python file has a built-in variable called `__name__`.
# - When you run this file directly in the terminal (`python vnexpress_crawler.py`),
#   Python sets `__name__` to `"__main__"`, so `main()` is executed.
# - When another Python file imports functions from this file (`import vnexpress_crawler`),
#   `__name__` is set to `"vnexpress_crawler"`, so `main()` does NOT run automatically!
if __name__ == "__main__":
    main()
