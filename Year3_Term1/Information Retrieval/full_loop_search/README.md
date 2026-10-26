# Information Retrieval - Homework 2: Text-Based Image Search Engine & Incremental Crawler Loop

**Student ID (MSSV):** 24125093

## Overview
This project extends the Homework 1 search engine in two directions:
1. **Text-based Image Search (Subdocument Passage Retrieval)**:
   - Webpages are split into multiple subdocuments, where each subdocument consists of an image and the text content immediately following it (`<figcaption>` combined with the subsequent `<p>` paragraph).
   - Images are indexed and ranked using Whoosh BM25F, boosting matches in the associated text (2.5x).
2. **15-Minute Periodic Crawler Loop**:
   - Continuously revisits `vnexpress.net/tin-tuc-24h` every 15 minutes.
   - Maintains persistent state (`crawled_article_ids.json`) to skip already crawled content.
   - Incrementally indexes new image subdocuments into Whoosh without rewriting previous index data.

## Project Structure
- `image_extractor.py`: Parses HTML to extract `(image_url, associated_text)` subdocuments.
- `image_indexer.py`: Whoosh schema and incremental indexing routines.
- `image_searcher.py`: BM25F search engine retrieving matching images.
- `crawler_loop.py`: 15-minute scheduled crawler polling loop.
- `app.py`: Streamlit graphical interface rendering responsive image search cards and crawler controls.

## How to Run

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the Image Search UI**:
   ```bash
   python -m streamlit run app.py
   ```

3. **(Optional) Run the 15-minute background crawler loop**:
   ```bash
   python crawler_loop.py --interval 15
   ```
   Or run a single check cycle:
   ```bash
   python crawler_loop.py --once
   ```
