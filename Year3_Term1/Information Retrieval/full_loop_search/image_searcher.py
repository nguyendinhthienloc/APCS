import sys
from whoosh.qparser import MultifieldParser, OrGroup
from image_indexer import get_or_create_index

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def search_images(query_string: str, limit: int = 12):
    """
    Searches the image subdocuments using BM25F ranking.
    Matches primarily on text immediately following the image (`associated_text`).
    """
    if not query_string or not query_string.strip():
        return []

    ix = get_or_create_index()

    parser = MultifieldParser(
        ["associated_text", "article_title", "category"],
        schema=ix.schema,
        group=OrGroup.factory(0.9)
    )

    try:
        query = parser.parse(query_string)
    except Exception as e:
        print(f"[ERROR] Failed to parse image search query '{query_string}': {e}")
        return []

    results = []
    with ix.searcher() as searcher:
        hits = searcher.search(query, limit=limit)

        for hit in hits:
            # Highlight matched keywords in associated text
            highlighted = hit.highlights("associated_text") or hit.get("associated_text", "")

            results.append({
                "subdoc_id": hit.get("subdoc_id"),
                "image_url": hit.get("image_url"),
                "associated_text": hit.get("associated_text"),
                "highlighted_text": highlighted,
                "article_title": hit.get("article_title"),
                "article_url": hit.get("article_url"),
                "category": hit.get("category"),
                "score": round(hit.score, 4),
            })

    return results

if __name__ == "__main__":
    # Test queries
    test_queries = ["tranh cãi", "Al-Hamdan", "Ronaldo"]
    for q in test_queries:
        print(f"\n--- Searching images for: '{q}' ---")
        hits = search_images(q, limit=2)
        for i, hit in enumerate(hits, 1):
            print(f"{i}. [Score: {hit['score']}] Image: {hit['image_url']}")
            print(f"   Caption: {hit['associated_text'][:100]}...")
