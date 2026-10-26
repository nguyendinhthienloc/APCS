import sys
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
}

def extract_image_subdocuments(soup, article_id: str, article_title: str, article_url: str, category: str = ""):
    """
    Splits an article into multiple image subdocuments.
    Each subdocument contains:
      - subdoc_id: Unique ID (e.g. 5136251_img_0)
      - image_url: Direct URL to the high-res image
      - associated_text: Text immediately following the image (<figcaption> + next <p>)
      - article_title: Parent article title
      - article_url: Parent article URL
      - category: News category
    """
    subdocuments = []
    
    # 1. Target the main article body
    article_body = soup.find("article", class_="fck_detail") or soup

    # 2. Find all <figure> tags containing images
    figures = article_body.find_all("figure")
    seen_images = set()

    for idx, fig in enumerate(figures):
        # Extract the real image URL (prefer data-src for lazy-loading)
        img_tag = fig.find("img")
        meta_url = fig.find("meta", attrs={"itemprop": "url"})

        img_url = None
        if meta_url and meta_url.get("content"):
            img_url = meta_url.get("content").strip()
        elif img_tag:
            img_url = img_tag.get("data-src") or img_tag.get("src")

        if not img_url or img_url.startswith("data:image") or ".svg" in img_url.lower():
            continue

        # Clean query parameters for deduplication (e.g., ?w=... resize params)
        base_img = img_url.split("?")[0]
        if base_img in seen_images:
            continue
        seen_images.add(base_img)

        # 3. Extract text content immediately following the image:
        # A. Semantic caption inside <figcaption>
        caption_tag = fig.find("figcaption")
        caption_text = caption_tag.get_text(" ", strip=True) if caption_tag else ""

        # B. Paragraph immediately following the <figure>
        next_p = fig.find_next_sibling("p")
        next_p_text = next_p.get_text(" ", strip=True) if next_p else ""

        # Combine both for comprehensive context
        text_parts = [t for t in [caption_text, next_p_text] if t]
        associated_text = " — ".join(text_parts) if text_parts else article_title

        subdocuments.append({
            "subdoc_id": f"{article_id}_img_{len(subdocuments)}",
            "article_id": str(article_id),
            "article_title": article_title,
            "article_url": article_url,
            "category": category,
            "image_url": img_url,
            "associated_text": associated_text,
        })

    return subdocuments

def fetch_and_extract_subdocuments(article_url: str):
    """Helper to fetch HTML from a URL and extract all image subdocuments."""
    try:
        resp = requests.get(article_url, headers=REQUEST_HEADERS, timeout=10)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Extract title
        title_tag = soup.find("h1", class_="title-detail") or soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        
        # Extract article id
        id_match = re.search(r"-(\d+)\.html", article_url)
        article_id = id_match.group(1) if id_match else "unknown"

        # Extract category
        cat_tag = soup.find("ul", class_="breadcrumb")
        category = cat_tag.find("a").get_text(strip=True) if (cat_tag and cat_tag.find("a")) else "Chung"

        return extract_image_subdocuments(soup, article_id, title, article_url, category)
    except Exception as e:
        print(f"[ERROR] Failed to fetch {article_url}: {e}")
        return []

if __name__ == "__main__":
    # Test on a real VnExpress article
    test_url = "https://vnexpress.net/ronaldo-nhuong-giai-cau-thu-hay-nhat-tran-sau-khi-ghi-ban-thu-982-5136251.html"
    print(f"Fetching: {test_url}\n")
    subdocs = fetch_and_extract_subdocuments(test_url)
    print(f"Extracted {len(subdocs)} image subdocuments:\n")
    for s in subdocs:
        print(f"ID: {s['subdoc_id']}")
        print(f"Image: {s['image_url']}")
        print(f"Associated Text: {s['associated_text'][:120]}...\n")
