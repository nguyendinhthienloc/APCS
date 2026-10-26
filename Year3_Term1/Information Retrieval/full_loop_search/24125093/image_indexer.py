import os
import sys
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.analysis import RegexTokenizer, LowercaseFilter

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_DIR = os.path.join(BASE_DIR, "image_indexdir")

def get_image_schema():
    vn_analyzer = RegexTokenizer(r"\w+") | LowercaseFilter()
    return Schema(
        subdoc_id=ID(stored=True, unique=True),
        article_id=ID(stored=True),
        article_title=TEXT(stored=True, analyzer=vn_analyzer, field_boost=1.5),
        article_url=ID(stored=True),
        category=TEXT(stored=True, analyzer=vn_analyzer),
        image_url=STORED,
        associated_text=TEXT(stored=True, analyzer=vn_analyzer, field_boost=2.5),
    )

def get_or_create_index(index_dir=INDEX_DIR):
    """Opens existing index or creates a fresh one if absent."""
    if index.exists_in(index_dir):
        return index.open_dir(index_dir)
    os.makedirs(index_dir, exist_ok=True)
    schema = get_image_schema()
    return index.create_in(index_dir, schema)

def add_subdocuments(subdocs, index_dir=INDEX_DIR):
    """
    Incrementally appends new image subdocuments to the Whoosh index.
    Does NOT wipe out previously indexed documents!
    """
    if not subdocs:
        return 0

    ix = get_or_create_index(index_dir)
    writer = ix.writer()

    for doc in subdocs:
        writer.update_document(
            subdoc_id=str(doc["subdoc_id"]),
            article_id=str(doc.get("article_id", "")),
            article_title=doc.get("article_title", ""),
            article_url=doc.get("article_url", ""),
            category=doc.get("category", ""),
            image_url=doc.get("image_url", ""),
            associated_text=doc.get("associated_text", ""),
        )

    writer.commit()
    return len(subdocs)

def get_indexed_doc_count(index_dir=INDEX_DIR):
    """Returns total subdocuments currently indexed."""
    if not index.exists_in(index_dir):
        return 0
    ix = index.open_dir(index_dir)
    return ix.doc_count()

if __name__ == "__main__":
    from image_extractor import fetch_and_extract_subdocuments

    test_url = "https://vnexpress.net/ronaldo-nhuong-giai-cau-thu-hay-nhat-tran-sau-khi-ghi-ban-thu-982-5136251.html"
    print(f"Extracting subdocs from: {test_url}")
    docs = fetch_and_extract_subdocuments(test_url)

    added = add_subdocuments(docs)
    print(f"Added {added} subdocuments into '{INDEX_DIR}'")
    print(f"Total subdocuments in index: {get_indexed_doc_count()}")
