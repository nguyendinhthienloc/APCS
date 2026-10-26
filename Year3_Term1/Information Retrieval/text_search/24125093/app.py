import time
import streamlit as st
from indexer import build_or_open_index
from searcher import search_articles

# 1. Page Configuration
st.set_page_config(
    page_title="VnExpress Search Engine",
    page_icon="🔎",
    layout="wide"
)

# 2. Guarantee Single-Index Execution via Streamlit Cache
@st.cache_resource
def load_search_index():
    return build_or_open_index()

# Initialize the index on app start
ix = load_search_index()
total_docs = ix.doc_count()

# 3. Header & Sidebar
st.title("🔎 VnExpress Search Engine")
st.caption(f"Course: Information Retrieval — Built with Whoosh & Streamlit (Indexed: {total_docs} articles)")

with st.sidebar:
    st.header("⚙️ Search Engine Info")
    st.markdown(f"**Total Indexed Documents:** `{total_docs}`")
    st.markdown("**Ranking Algorithm:** BM25F")
    st.markdown("**Indexed Fields:** `title` (boost 2.0x), `category`, `comments`")
    st.divider()
    max_results = st.slider("Max results to display:", min_value=5, max_value=50, value=10, step=5)

# 4. Search Form
with st.form(key="search_bar", clear_on_submit=False):
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        query = st.text_input(
            "Search Query",
            placeholder="Type your search query",
            label_visibility="collapsed"
        )
    with col_btn:
        submitted = st.form_submit_button("Search", use_container_width=True)

# 5. Search Execution & Display
if submitted or query:
    if not query.strip():
        st.warning("Please enter a query to search.")
    else:
        start_time = time.time()
        results = search_articles(query, limit=max_results)
        search_time = (time.time() - start_time) * 1000  # in ms

        st.markdown(f"Found **{len(results)}** results in `{search_time:.2f} ms` for: *\"{query}\"*")
        st.divider()

        if not results:
            st.info("No matching articles found. Try different keywords or check spelling.")
        else:
            for idx, item in enumerate(results, start=1):
                with st.container():
                    # Title & Link
                    st.markdown(f"### {idx}. [{item['title']}]({item['url']})")
                    
                    # Metadata badges
                    col_meta1, col_meta2, col_meta3 = st.columns([2, 2, 6])
                    with col_meta1:
                        st.markdown(f"🏷️ **Category:** `{item['category']}`")
                    with col_meta2:
                        st.markdown(f"📊 **BM25 Score:** `{item['score']}`")
                    with col_meta3:
                        if item.get("published_time"):
                            st.markdown(f"🕒 **Published:** `{item['published_time']}`")

                    # Snippet or comments if available
                    if item.get("comment_snippet"):
                        st.markdown(f"> 💬 *Top Comment / Snippet:* {item['comment_snippet']}")
                    
                    st.write("")  # Spacing