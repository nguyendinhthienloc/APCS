# VnExpress 24-Hour News Crawler (Beginner-Friendly Guide)

A clean, robust, and easy-to-read web crawler built with **`requests`** and **`BeautifulSoup` (`bs4`)** for **Information Retrieval**.

It extracts all VnExpress articles published in the **last 24 hours** across `/tin-tuc-24h` and all major categories, collecting:
1. **Article Name (Title)** and Category
2. **Article Images** (saves all image URLs in the dataset **and** downloads the actual image files into `downloaded_images/<article_id>/`)
3. **Total Number of Comments** (both total comments including replies and top-level comments)
4. **The Most Liked Comment** (comment text, author name, and like count)

---

## 📁 Folder Structure

```text
vnexpresscrawler/
├── vnexpress_crawler.py         # Main crawler script (heavily commented for beginners)
├── requirements.txt             # Python dependencies (requests, beautifulsoup4)
├── README.md                    # Documentation of logic & Python syntax guide
├── vnexpress_articles_24h.json  # Generated JSON dataset (after running)
├── vnexpress_articles_24h.csv   # Generated CSV dataset for Excel/Pandas (after running)
└── downloaded_images/           # Downloaded images organized by article_id (after running)
```

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Crawl ALL Articles from the Last 24 Hours (Default)
```bash
python vnexpress_crawler.py
```
This crawls `/tin-tuc-24h` and all 16 VnExpress categories (`thoi-su`, `the-gioi`, `kinh-doanh`, `khoa-hoc-cong-nghe`, `the-thao`, `giai-tri`, `phap-luat`, etc.), automatically stopping pagination in each category once articles are older than 24 hours.

### 3. Quick Test Run (Limit to e.g. 5 or 10 Articles)
If you want a quick test run for demonstration in class:
```bash
python vnexpress_crawler.py --max-articles 5
```

### 4. Crawl a Specific Category Only
```bash
python vnexpress_crawler.py --category khoa-hoc-cong-nghe
```

---

## 🧠 How the Crawler Works (Function-by-Function Logic)

### Step 1: Fetching HTML (`fetch_webpage_html`)
- Sends an HTTP `GET` request with a realistic browser `User-Agent` header so VnExpress does not block the script.
- Forces `response.encoding = "utf-8"` so Vietnamese diacritics (`ă, â, đ, ê, ô, ơ, ư`) are never corrupted.

### Step 2: Discovering Article Links (`parse_article_links_from_listing`)
- Parses category and `/tin-tuc-24h` pages using `BeautifulSoup(html_text, "html.parser")`.
- Finds all `<article class="item-news">` blocks and extracts the `<a href="...">` URL.
- **URL Normalization (`normalize_article_url`)**: Strips `#box_comment_vne` anchors and `?vn_source=...` tracking parameters so the same article is never crawled twice. Uses regex `-(\d+)\.html` (`extract_article_id_from_url`) to extract the unique VnExpress article ID (e.g., `5135952`).

### Step 3: Checking the 24-Hour Recency Filter (`extract_publication_datetime`)
To make sure the crawler never fails if VnExpress changes one of its templates, it checks 3 places in order:
1. `<meta name="pubdate" content="2026-10-23T20:39:28+07:00">` (ISO-8601 format)
2. `<meta name="its_publication" content="1792762768">` (Unix timestamp in seconds)
3. `<span class="date">Thứ sáu, 23/10/2026, 20:39 (GMT+7)</span>` (Visible Vietnamese date text)

We subtract `pub_datetime` from `current_time`. If `age_in_hours > 24.0`, the article is rejected!

### Step 4: Extracting Lazy-Loaded Images (`extract_article_images` & `download_article_images`)
> **Why simple crawlers fail on VnExpress images:**
> VnExpress uses **Lazy Loading** to make pages load faster. Because of this, `<img src="...">` inside the HTML actually holds a fake 1×1 blank GIF (`data:image/gif;base64,...`)!

Our `extract_article_images(soup)` function solves this by reading:
- `img.get("data-src")` (where VnExpress stores the real high-res image URL before scrolling)
- `<meta itemprop="url" content="...">` inside `<figure>` tags
- `<meta property="og:image">` for the article's main thumbnail

Then `download_article_images(...)` saves each image as binary bytes (`"wb"`) into `downloaded_images/<article_id>/`.

### Step 5: Extracting Total Comments & Most Liked Comment (`fetch_article_comments_info`)
> **Why comments aren't directly inside `<article>` HTML:**
> VnExpress loads reader comments asynchronously when you scroll down. However, the HTML page contains a `<div id="box_comment_vne" data-component-input='{...}'>` element with the article's comment configuration (`article_id`, `site_id`, `category_id`, `sign`).

1. We use **BeautifulSoup** to find `<div id="box_comment_vne">` and parse its JSON configuration.
2. We send a request to VnExpress's comment microservice (`https://usi-saas.vnexpress.net/index/get`) with `sort=like&tab_active=most_like`.
3. From the JSON response:
   - `data["totalitem"]` gives the **total number of comments** (including replies).
   - `data["total"]` gives the number of **top-level comments**.
   - We loop through `data["items"]` to find the comment with the highest `userlike` count, and use **BeautifulSoup** again (`BeautifulSoup(raw_content, "html.parser").get_text()`) to strip HTML tags like `<br />` and `&nbsp;` from the comment text!

---

## 🐍 "Weird" Python Syntax Explained for Beginners

If you are new to Python or Information Retrieval, here is a cheat-sheet explaining the Python syntax used in `vnexpress_crawler.py`:

### 1. Why `class_="..."` has an underscore in BeautifulSoup
```python
soup.find_all("article", class_="item-news")
```
- **Why the underscore?** In Python, `class` is a reserved keyword used to create object-oriented classes (`class MyCrawler:`). You cannot name a function argument `class=...`. So BeautifulSoup uses `class_="..."` instead!

### 2. `f"..."` (Formatted String Literals / f-strings)
```python
page_url = f"{cat_url}-p{page_num}"
```
- Putting the letter `f` right before the opening quote lets you embed Python variables or expressions directly inside curly braces `{}`. Python automatically converts them to strings.

### 3. `r"..."` (Raw Strings for Regular Expressions)
```python
match = re.search(r"-(\d+)\.html", url)
```
- Putting `r` before a quote tells Python to treat backslashes `\` literally instead of as escape codes (like `\n` for newline). This is essential for Regular Expressions where `\d+` means "one or more digits".

### 4. `dict.get("key", default)` vs `dict["key"]`
```python
likes = comment.get("userlike", 0)
```
- If you write `comment["userlike"]` and the `"userlike"` key is missing, Python crashes with a `KeyError`.
- Writing `comment.get("userlike", 0)` safely returns `0` (or `None` if no default is given) when the key does not exist.

### 5. `set()` for Instant Deduplication
```python
visited_article_ids = set()
visited_article_ids.add(article_id)
```
- A `set` is like a list, except it **cannot contain duplicates** and checking `if article_id in visited_article_ids:` takes $O(1)$ constant time (instantaneous even with 100,000 URLs, whereas searching a list `[]` gets slower as it grows).

### 6. String Slicing `text[:50]` and `.split("?")[0]`
```python
base_path = url.split("?")[0]
short_title = title[:60]
```
- `url.split("?")` chops a URL into a list of pieces around the `?` character, and `[0]` grabs the first piece (everything before `?`).
- `title[:60]` takes the first 60 characters of `title` (from index `0` up to `60`). Unlike many other languages, slicing in Python never crashes if the string is shorter than 60 characters!

### 7. Tuple Unpacking (`status, data = ...`)
```python
status, data = process_single_article(...)
```
- A Python function can return two values separated by a comma (`return "ok", article_data`). You can catch both values on the left side of `=` in a single line.

### 8. `enumerate(my_list, start=1)`
```python
for index, img_url in enumerate(image_urls, start=1):
```
- Instead of manually maintaining a counter variable `i = 1; i += 1`, `enumerate()` gives you both the counter (`index`) and the value (`img_url`) on every loop iteration.

### 9. `with open(...) as file:` (Context Managers)
```python
with open(local_path, "wb") as img_file:
    img_file.write(response.content)
```
- The `with` block guarantees that Python will automatically flush and close the file as soon as the block finishes—even if an error happens midway!
- `"wb"` stands for **Write Binary** (for raw image bytes), while `"w"` is for **Write Text**.

### 10. `if __name__ == "__main__":`
```python
if __name__ == "__main__":
    main()
```
- When you run `python vnexpress_crawler.py`, Python sets the special built-in variable `__name__` to `"__main__"`, which triggers `main()`.
- If you import this file from another script (`import vnexpress_crawler`), `__name__` is `"vnexpress_crawler"`, so it won't accidentally start crawling on import.
