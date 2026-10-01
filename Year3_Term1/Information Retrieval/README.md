# BaoMoi Image Web Crawler 🕷️🖼️

A fast, multithreaded web crawler and image downloader for **[baomoi.com](https://baomoi.com/)**, designed for Information Retrieval, Computer Vision datasets, and data mining projects.

---

## 🌟 Key Features

- **⏱️ 24-Hour Recency Constraint**: Enforces strict temporal filtering so only news published within the last 24 hours is crawled and downloaded. Stale or older articles are automatically rejected.
- **⚡ High-Resolution Extraction**: Automatically upgrades low-resolution CDN thumbnails (`w300`, `w500`, `w700`) to full HD resolution (`w1200_r1` / 1000px+).
- **🧠 Next.js `__NEXT_DATA__` Parsing**: Extracts structured article data directly from BaoMoi's internal JSON state (article title, categories, descriptions, publication timestamps, captions, and CDN links) with an HTML fallback parser.
- **🚀 Multithreaded Concurrency**: Uses `ThreadPoolExecutor` for high-throughput parallel image downloads.
- **🗂️ Clean Folder Organization**: Automatically organizes images into category folders and per-article subfolders with safe, sanitized filenames.
- **📊 Metadata Export**: Exports comprehensive metadata for every downloaded image to both **`metadata.json`** and **`metadata.csv`** (including title, URL, article URL, publication date, calculated age in hours, caption, file size, and download timestamp).
- **🛡️ Polite & Safe Crawling**: Built-in rate limiting, polite delays, and max crawl duration constraints.
- **🎯 Multiple Crawling Modes**:
  - Hot / Trending news (Trang chủ)
  - By category (`xa-hoi`, `the-thao`, `cong-nghe`, `kinh-te`, `giai-tri`, `phap-luat`, etc.)
  - By search keyword (`tim-kiem/{query}`)
  - Direct article or custom URLs
  - Interactive console menu

---

## 📁 Project Structure

```
.
├── crawler.py          # Complete, self-contained crawler (BeautifulSoup, 24h constraint, CLI)
├── requirements.txt    # Python dependencies (requests, beautifulsoup4, tqdm, lxml)
└── README.md           # Documentation
```

> **Note**: `crawler.py` is entirely self-contained in a single file with zero internal dependencies.

---

## 🛠️ Installation

Ensure you have Python 3.9+ installed, then install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🚀 Quick Start (CLI)

You can run `crawler.py` directly as a single standalone script:

### 1. Interactive Mode
Run without arguments to launch the friendly interactive menu:
```bash
python crawler.py
```

### 2. Crawl Hot / Trending News
Download 20 images from current trending news on the homepage:
```bash
python crawler.py -c hot -n 20
```

### 3. Crawl a Specific Category
Download images from technology (`cong-nghe`), sports (`the-thao`), society (`xa-hoi`), etc.:
```bash
python crawler.py -c cong-nghe -n 30 -a 10
python crawler.py -c the-thao -n 50 -o sports_images
```

### 4. Crawl by Search Query Keyword
Search for any topic and download related news photos:
```bash
python crawler.py -q "tri tue nhan tao" -n 25
python crawler.py -q "xe dien" -n 40
```

### 5. Crawl a Specific Article or Custom URL
```bash
python crawler.py -u "https://baomoi.com/tu-hom-nay-1-10-cao-toc-ben-luc-long-thanh-ket-noi-mien-dong-mien-tay-nam-bo-dua-vao-khai-thac-c56170596.epi"
```

### 6. List All Supported Categories
```bash
python crawler.py --list-categories
```

---

## ⚙️ CLI Command Reference

| Flag | Long Option | Default | Description |
|------|-------------|---------|-------------|
| `-c` | `--category` | `hot` | Category code (e.g. `cong-nghe`, `the-thao`, `kinh-te`, `xa-hoi`) |
| `-q` | `--query` | `None` | Search query keyword on BaoMoi |
| `-u` | `--url` | `None` | Direct URL of an article or listing page |
| `-n` | `--max-images` | `30` | Maximum number of images to download |
| `-a` | `--max-articles` | `15` | Maximum number of valid articles to visit |
| `-o` | `--output-dir` | `baomoi_images` | Destination directory for images and metadata |
| `-w` | `--workers` | `5` | Number of concurrent download threads |
| `-d` | `--delay` | `0.5` | Delay in seconds between article requests |
| `--flat` | `--flat` | `False` | Save images in a single folder without article subfolders |
| `--no-upgrade` | `--no-upgrade` | `False` | Keep original thumbnail resolution without upgrading to HD |
| `--max-age-hours` | `--max-age-hours` | `24.0` | **Constraint**: Only crawl articles published within this many hours |
| `--no-time-limit` | `--no-time-limit` | `False` | Disable the 24-hour publication constraint |
| `--allow-unknown-date` | `--allow-unknown-date` | `False` | Allow articles where publication date cannot be verified |
| `--max-crawl-duration` | `--max-crawl-duration` | `86400` | **Constraint**: Maximum crawler execution time in seconds (24 hours) |
| `-i` | `--interactive` | `False` | Run interactive console prompt |

---

## 🐍 Python API Usage

You can easily integrate `BaoMoiImageCrawler` into your own scripts or Jupyter notebooks:

```python
from crawler import BaoMoiImageCrawler

# Initialize crawler with 24-hour freshness constraint
crawler = BaoMoiImageCrawler(
    output_dir="dataset/baomoi",
    max_images=50,
    max_articles=20,
    concurrency=8,
    delay=0.5,
    upgrade_resolution=True,
    organize_by_article=True,
    max_age_hours=24.0  # Enforces constraint: articles must be within 24 hours
)

# Option A: Crawl by category
records = crawler.crawl_category("cong-nghe")

# Option B: Crawl by keyword search
records = crawler.crawl_query("thoi tiet")

# Option C: Crawl custom list of URLs
records = crawler.crawl([
    "https://baomoi.com/tin-moi.epi"
], category_name="tin_moi")

print(f"Downloaded {len(records)} images!")
```

---

## 📑 Output Metadata Format

For every crawl run, a `<category>_metadata.json` and `<category>_metadata.csv` file are automatically generated with fields:

```json
[
  {
    "file_name": "Tu-hom-nay-1-10-cao-toc-Ben-Luc-Long-Tha_01.jpg",
    "local_path": "D:\\APCS\\Year3_Term1\\Information Retrieval\\baomoi_images\\hot\\Tu-hom-nay-1-10-cao-toc-Ben-Luc-Long-Tha_01.jpg",
    "image_url": "https://photo-baomoi.bmcdn.me/w1200_r1/2026_10_01_16_56170596/562aae9a1ed1f78faec0.jpg",
    "original_url": "https://photo-baomoi.bmcdn.me/w1000_r1/2026_10_01_16_56170596/562aae9a1ed1f78faec0.jpg",
    "article_url": "https://baomoi.com/tu-hom-nay-1-10-cao-toc-ben-luc-long-thanh-ket-noi-mien-dong-mien-tay-nam-bo-dua-vao-khai-thac-c56170596.epi",
    "article_title": "Từ hôm nay (1-10), cao tốc Bến Lức - Long Thành kết nối miền Đông - miền Tây Nam Bộ đưa vào khai thác",
    "category": "giao-thong",
    "published_date": "2026-10-01T09:44:00+07:00",
    "article_age_hours": 3.58,
    "caption": "Hình ảnh tuyến cao tốc Bến Lức - Long Thành",
    "file_size_bytes": 131311,
    "download_time": "2026-10-01T13:18:39.838009"
  }
]
```

---

## 📌 Recognized Categories

- `hot`: Trang chủ (Tin nóng)
- `tin-moi`: Tin mới nhất
- `xa-hoi`: Xã hội
- `the-gioi`: Thế giới
- `kinh-te`: Kinh tế
- `giao-thong`: Giao thông
- `phap-luat`: Pháp luật
- `the-thao`: Thể thao
- `giai-tri`: Giải trí
- `cong-nghe` / `khoa-hoc-cong-nghe`: Khoa học - Công nghệ
- `suc-khoe`: Sức khỏe
- `doi-song`: Đời sống
- `xe-co`: Xe cộ
- `nha-dat`: Nhà đất
- `du-lich`: Du lịch
- `giao-duc`: Giáo dục
