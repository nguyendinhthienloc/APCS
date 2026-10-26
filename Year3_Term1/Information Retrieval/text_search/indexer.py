import os
import sys 
import json
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, STORED 
from whoosh.analysis import RegexTokenizer, LowercaseFilter

# Anchor all paths to the folder where indexer.py is saved
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_DIR = os.path.join(BASE_DIR, "indexdir")
DEFAULT_DATA_PATH = os.path.join(BASE_DIR, "vnexpress_articles_24h.json")

def get_schema():
    # Regex matches words including Vietnamese unicode accents
    vn_analyzer = RegexTokenizer(r"\w+") | LowercaseFilter()
    return Schema(
        article_id=ID(stored=True, unique=True),
        article_title=TEXT(stored=True, analyzer=vn_analyzer, field_boost=2.0),
        category=TEXT(stored=True, analyzer=vn_analyzer),
        article_url=ID(stored=True),
        comments=TEXT(stored=True, analyzer=vn_analyzer),
        published_time=STORED,
    )

def build_or_open_index(data_path=DEFAULT_DATA_PATH, index_dir=INDEX_DIR):
    # Defense Layer 1: Check if index already exists
    if index.exists_in(index_dir):
        print(f"[INFO] Found existing index in '{index_dir}'. Opening...")
        return index.open_dir(index_dir)
    print(f"[INFO] No index found. Building index in '{index_dir}'...")
    os.makedirs(index_dir, exist_ok=True)
    schema = get_schema()
    ix = index.create_in(index_dir, schema)
    
    # Read the crawled JSON
    with open(data_path, "r", encoding="utf-8") as f:
        articles = json.load(f)
    writer = ix.writer()
    for art in articles:
        writer.update_document(
            article_id=str(art.get("article_id", "")),
            article_title=art.get("article_title", ""),
            category=art.get("category", ""),
            article_url=art.get("article_url", ""),  
            comments=art.get("most_liked_comment_text", "") or "",
            published_time=art.get("published_time", "") or "",
        )
    
    # Save to disk!
    writer.commit()
    print(f"[INFO] Indexed {len(articles)} documents successfully.")
    return ix

if __name__ == "__main__":
    ix = build_or_open_index()
    print("Total documents in index:", ix.doc_count())