import os
import sys

# Ensure UTF-8 output in Windows terminals for Vietnamese characters
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from whoosh.qparser import MultifieldParser, OrGroup
from indexer import build_or_open_index

def search_articles(query_string: str, limit: int = 10):
    if not query_string or not query_string.strip():
        return []

    # 1. Open the existing index (guaranteed not to re-index)
    ix = build_or_open_index()

    # 2. Setup parser across title, category, and comments
    # OrGroup(0.9): prefers matching all words, but still returns partial matches
    parser = MultifieldParser(
        ["article_title", "comments", "category"],
        schema=ix.schema,
        group=OrGroup.factory(0.9)
    )
    
    # Parse the query string safely
    try:
        query = parser.parse(query_string)
    except Exception as e:
        print(f"[ERROR] Failed to parse query '{query_string}': {e}")
        return []

    # 3. Execute search with BM25F ranking
    results_list = []
    with ix.searcher() as searcher:
        hits = searcher.search(query, limit=limit)
        
        for hit in hits:
            # Extract highlights / snippets if available
            title_highlight = hit.highlights("article_title") or hit["article_title"]
            comment_snippet = hit.highlights("comments") or hit.get("comments", "")
            
            results_list.append({
                "article_id": hit.get("article_id"),
                "title": hit.get("article_title"),
                "title_highlight": title_highlight,
                "url": hit.get("article_url"),
                "category": hit.get("category"),
                "published_time": hit.get("published_time"),
                "comment_snippet": comment_snippet,
                "score": round(hit.score, 4),
            })

    return results_list

if __name__ == "__main__":
    # Test with a sample query
    test_query = "Ronaldo"
    print(f"\n--- Searching for: '{test_query}' ---")
    results = search_articles(test_query, limit=5)
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r['category']}] {r['title']} (Score: {r['score']})")
        print(f"   URL: {r['url']}")