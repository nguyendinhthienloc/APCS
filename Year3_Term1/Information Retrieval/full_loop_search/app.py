import os
import sys
import time
import streamlit as st

from image_indexer import get_or_create_index, get_indexed_doc_count
from image_searcher import search_images
from crawler_loop import load_seen_ids, run_crawling_cycle

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 1. Page Configuration
st.set_page_config(
    page_title="VnExpress Image Search Engine",
    page_icon="🖼️",
    layout="wide"
)

# 2. Cache the index loader
@st.cache_resource
def load_index():
    return get_or_create_index()

ix = load_index()
total_images = get_indexed_doc_count()
seen_ids = load_seen_ids()

# 3. Sidebar
with st.sidebar:
    st.header("🖼️ Image Search Stats")
    st.markdown(f"**Indexed Images (Subdocs):** `{total_images}`")
    st.markdown(f"**Crawled Articles:** `{len(seen_ids)}`")
    st.markdown("**Ranking Model:** BM25F on Associated Text (2.5x) + Title (1.5x)")
    st.divider()

    st.subheader("🔄 15-Minute Crawler")
    st.caption("The background loop checks vnexpress.net/tin-tuc-24h every 15 minutes.")
    if st.button("Trigger Immediate Crawl Cycle"):
        with st.spinner("Crawling latest news stream..."):
            added = run_crawling_cycle(seen_ids, max_new_articles=5)
            st.success(f"Crawl complete! Added {added} new image subdocuments.")
            st.rerun()

    st.divider()
    max_results = st.slider("Max images to display:", 6, 30, 12, step=3)

# 4. Main Search Header
st.title("🖼️ VnExpress Text-Based Image Search Engine")
st.caption("Information Retrieval — Homework 2: Subdocument Retrieval & Incremental Crawling")

# 5. Search Bar
with st.form("image_search_form"):
    col_q, col_btn = st.columns([5, 1])
    with col_q:
        query = st.text_input(
            "Query",
            placeholder="Search for images (e.g., Ronaldo, quạt trần, máy bay)...",
            label_visibility="collapsed"
        )
    with col_btn:
        search_clicked = st.form_submit_button("Search Images", use_container_width=True)

# 6. Display Search Results in a 3-Column Grid
if query or search_clicked:
    if not query.strip():
        st.warning("Please enter a search query.")
    else:
        start_time = time.time()
        results = search_images(query, limit=max_results)
        latency = (time.time() - start_time) * 1000

        st.markdown(f"Found **{len(results)}** images in `{latency:.2f} ms` for: *\"{query}\"*")
        st.divider()

        if not results:
            st.info("No matching images found. Try other keywords or trigger a crawl cycle in the sidebar!")
        else:
            # Render results in 3 columns
            cols = st.columns(3)
            for idx, item in enumerate(results):
                col = cols[idx % 3]
                with col:
                    with st.container(border=True):
                        # Render the image
                        img_url = item.get("image_url")
                        if img_url:
                            st.image(img_url, use_container_width=True)
                        
                        # Associated text immediately following the image
                        caption = item.get("associated_text", "")
                        st.markdown(f"**Caption / Context:**  \n*{caption[:160]}...*" if len(caption) > 160 else f"*{caption}*")
                        
                        # Parent article metadata
                        st.caption(f"🏷️ `{item.get('category')}` | 📊 Score: `{item.get('score')}`")
                        st.markdown(f"🔗 [Read Article]({item.get('article_url')})")
