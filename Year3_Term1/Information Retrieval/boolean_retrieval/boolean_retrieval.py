import re
import random
import numpy as np


def generate_mock_documents(num_docs: int = 100, seed: int = 42) -> dict:
    random.seed(seed)

    # 4 distinct topical vocabularies to make boolean AND / OR / NOT behavior clear
    topics = {
        "search_and_ai": {
            "subjects": [
                "Information retrieval systems",
                "Boolean search engines",
                "Vector databases",
                "Neural bi-encoders",
                "Dense embeddings",
                "Full-text indexing algorithms",
            ],
            "verbs": ["optimize", "evaluate", "implement", "process", "accelerate", "benchmark"],
            "objects": [
                "query latency",
                "inverted index lookups",
                "relevance ranking",
                "precision and recall",
                "TF-IDF weights",
                "token parsing",
            ],
        },
        "cloud_and_db": {
            "subjects": [
                "PostgreSQL clusters",
                "Redis cache layers",
                "Distributed database nodes",
                "Kafka event streams",
                "Docker containers",
                "Kubernetes pods",
            ],
            "verbs": ["scale", "replicate", "monitor", "partition", "synchronize", "deploy"],
            "objects": [
                "sharded storage",
                "high availability replicas",
                "memory consumption",
                "read-write throughput",
                "transaction logs",
                "microservice traffic",
            ],
        },
        "cybersecurity": {
            "subjects": [
                "Firewall rules",
                "Zero-trust architectures",
                "Intrusion detection models",
                "Authentication tokens",
                "Vulnerability scanners",
                "Security analysts",
            ],
            "verbs": ["detect", "mitigate", "audit", "block", "investigate", "isolate"],
            "objects": [
                "anomalous network traffic",
                "brute force attacks",
                "unauthorized access",
                "compromised credentials",
                "data breach risks",
                "encrypted payloads",
            ],
        },
        "software_dev": {
            "subjects": [
                "Python scripts",
                "Automated unit tests",
                "CI/CD pipelines",
                "Open-source frameworks",
                "Compilers and linkers",
                "REST API gateways",
            ],
            "verbs": ["refactor", "build", "maintain", "execute", "validate", "debug"],
            "objects": [
                "production source code",
                "memory leaks",
                "dependency trees",
                "error handling workflows",
                "developer productivity",
                "unit test suites",
            ],
        },
    }

    domain_keys = list(topics.keys())
    docs = {}

    for doc_id in range(1, num_docs + 1):
        # Pick 1 primary domain, with a 30% chance to blend in terms from a 2nd domain
        primary_domain = random.choice(domain_keys)
        vocab = topics[primary_domain]

        sentence_parts = [
            random.choice(vocab["subjects"]),
            random.choice(vocab["verbs"]),
            random.choice(vocab["objects"]),
        ]

        # Cross-domain blending (creates interesting overlap for AND queries)
        if random.random() < 0.30:
            secondary_domain = random.choice([k for k in domain_keys if k != primary_domain])
            extra_vocab = topics[secondary_domain]
            sentence_parts.append("while managing " + random.choice(extra_vocab["objects"]))

        docs[doc_id] = " ".join(sentence_parts) + "."

    return docs


# ==============================================================================
# 1. Inverted Index Builder (Postings List Model)
# ==============================================================================
class InvertedIndex:
    def __init__(self, docs: dict):
        self.all_doc_ids = set(docs.keys())
        self.index = {}
        self._build_index(docs)

    def _tokenize(self, text: str):
        return set(re.findall(r"\w+", text.lower()))

    def _build_index(self, docs):
        for doc_id, text in docs.items():
            for token in self._tokenize(text):
                self.index.setdefault(token, set()).add(doc_id)

    def get_postings(self, term: str) -> set:
        return self.index.get(term.lower(), set())


# ==============================================================================
# 2. Term-Document Incidence Matrix Builder (Boolean Matrix Model)
# ==============================================================================
class TermDocumentMatrix:
    """
    Term-Document Incidence Matrix for Classical Boolean Retrieval.
    - Rows: Vocabulary terms (V)
    - Columns: Documents (D)
    - Values: Boolean {0, 1} indicating term presence in each document.
    """

    def __init__(self, docs: dict):
        self.doc_ids = sorted(docs.keys())
        self.doc_id_to_idx = {doc_id: idx for idx, doc_id in enumerate(self.doc_ids)}
        self.num_docs = len(self.doc_ids)

        # Collect and sort all distinct vocabulary tokens
        vocab_set = set()
        for text in docs.values():
            vocab_set.update(self._tokenize(text))
        self.vocabulary = sorted(list(vocab_set))
        self.term_to_idx = {term: idx for idx, term in enumerate(self.vocabulary)}

        # Build 2D incidence matrix (V x D)
        self.matrix = np.zeros((len(self.vocabulary), self.num_docs), dtype=np.int8)
        for doc_id, text in docs.items():
            col_idx = self.doc_id_to_idx[doc_id]
            for token in self._tokenize(text):
                row_idx = self.term_to_idx[token]
                self.matrix[row_idx, col_idx] = 1

    def _tokenize(self, text: str):
        return set(re.findall(r"\w+", text.lower()))

    def get_term_vector(self, term: str) -> np.ndarray:
        """Returns a 1D binary vector of length N (num_docs) for the term."""
        term = term.lower()
        if term in self.term_to_idx:
            return self.matrix[self.term_to_idx[term], :].copy()
        return np.zeros(self.num_docs, dtype=np.int8)

    def get_submatrix(self, terms: list, doc_ids: list = None):
        """Extracts a submatrix for specified terms and doc_ids."""
        if doc_ids is None:
            doc_ids = self.doc_ids
        col_indices = [self.doc_id_to_idx[d] for d in doc_ids if d in self.doc_id_to_idx]
        valid_terms = [t.lower() for t in terms if t.lower() in self.term_to_idx]
        row_indices = [self.term_to_idx[t] for t in valid_terms]
        sub = self.matrix[np.ix_(row_indices, col_indices)]
        return sub, valid_terms, [d for d in doc_ids if d in self.doc_id_to_idx]


# ==============================================================================
# 3. Query Parser & Dual Evaluator (Inverted Index + Boolean Matrix)
# ==============================================================================
class BooleanSearchEngine:
    PRECEDENCE = {"NOT": 3, "AND": 2, "OR": 1}

    def __init__(self, index: InvertedIndex, matrix: TermDocumentMatrix = None):
        self.index = index
        self.matrix = matrix

    def tokenize_query(self, query: str):
        # Extract parentheses, boolean operators, or alphanumeric words
        raw_tokens = re.findall(r"\(|\)|\bAND\b|\bOR\b|\bNOT\b|[a-zA-Z0-9]+", query)
        tokens = [t if t in {"AND", "OR", "NOT", "(", ")"} else t.lower() for t in raw_tokens]

        # Insert implicit AND when an operand or ')' is followed by an operand, '(', or 'NOT'
        normalized = []
        for i, token in enumerate(tokens):
            if i > 0:
                prev = normalized[-1]
                if (prev not in {"AND", "OR", "NOT", "("}) and (token not in {"AND", "OR", ")"}):
                    normalized.append("AND")
            normalized.append(token)
        return normalized

    def to_postfix(self, tokens):
        output, stack = [], []
        for token in tokens:
            if token in self.PRECEDENCE:
                while stack and stack[-1] != "(" and self.PRECEDENCE.get(stack[-1], 0) >= self.PRECEDENCE[token]:
                    output.append(stack.pop())
                stack.append(token)
            elif token == "(":
                stack.append(token)
            elif token == ")":
                while stack and stack[-1] != "(":
                    output.append(stack.pop())
                stack.pop()  # Discard '('
            else:
                output.append(token)
        while stack:
            output.append(stack.pop())
        return output

    def evaluate(self, query: str) -> set:
        """Evaluates using postings list sets (Inverted Index)."""
        tokens = self.tokenize_query(query)
        postfix = self.to_postfix(tokens)
        eval_stack = []

        for token in postfix:
            if token == "NOT":
                operand = eval_stack.pop()
                eval_stack.append(self.index.all_doc_ids - operand)
            elif token == "AND":
                right, left = eval_stack.pop(), eval_stack.pop()
                eval_stack.append(left & right)
            elif token == "OR":
                right, left = eval_stack.pop(), eval_stack.pop()
                eval_stack.append(left | right)
            else:
                eval_stack.append(self.index.get_postings(token))

        return eval_stack[0] if eval_stack else set()

    def evaluate_vector(self, query: str) -> np.ndarray:
        """Evaluates using bitwise operations over boolean vectors (Incidence Matrix)."""
        if self.matrix is None:
            raise ValueError("TermDocumentMatrix not configured for vector evaluation.")

        tokens = self.tokenize_query(query)
        postfix = self.to_postfix(tokens)
        eval_stack = []

        for token in postfix:
            if token == "NOT":
                operand = eval_stack.pop()
                eval_stack.append(1 - operand)
            elif token == "AND":
                right, left = eval_stack.pop(), eval_stack.pop()
                eval_stack.append(left & right)
            elif token == "OR":
                right, left = eval_stack.pop(), eval_stack.pop()
                eval_stack.append(left | right)
            else:
                eval_stack.append(self.matrix.get_term_vector(token))

        return eval_stack[0] if eval_stack else np.zeros(self.matrix.num_docs, dtype=np.int8)

    def evaluate_both(self, query: str):
        """Evaluates using both engines and confirms equivalence."""
        set_matches = self.evaluate(query)
        vector = self.evaluate_vector(query)
        vec_matches = {self.matrix.doc_ids[i] for i, val in enumerate(vector) if val == 1}
        assert set_matches == vec_matches, f"Mismatch for query: {query}"
        return set_matches, vector


# ==============================================================================
# 4. Helper Functions for Presenting Matrices
# ==============================================================================
def print_matrix_table(
    matrix: np.ndarray,
    row_labels: list,
    col_labels: list,
    title: str = "",
    extra_col: list = None,
    extra_header: str = "Total",
):
    """Prints a cleanly formatted ASCII table for any 2D boolean/incidence matrix."""
    if title:
        print(f"\n{title}")
    col_w = max(4, max(len(str(c)) for c in col_labels)) if col_labels else 4
    row_w = max(len(str(r)) for r in row_labels) if row_labels else 6

    header = f"{'':<{row_w}}  " + " ".join(f"{str(c):>{col_w}}" for c in col_labels)
    if extra_col is not None:
        header += f"  |  {extra_header}"
    sep = "-" * len(header)

    print(header)
    print(sep)
    for i, (r_label, row) in enumerate(zip(row_labels, matrix)):
        vals = " ".join(f"{val:>{col_w}}" for val in row)
        line = f"{r_label:<{row_w}}  {vals}"
        if extra_col is not None:
            line += f"  |  {extra_col[i]:>{len(extra_header)}}"
        print(line)
    print(sep)


def export_results_matrix(
    matrix: np.ndarray,
    query_labels: list,
    queries: list,
    doc_ids: list,
    csv_filename: str = "query_document_matrix.csv",
    txt_filename: str = "query_document_matrix.txt",
):
    """Exports full query-document results matrix to CSV and formatted text files."""
    # 1. Export CSV
    with open(csv_filename, "w", encoding="utf-8") as f:
        col_headers = [f"Doc_{d:03d}" for d in doc_ids]
        f.write("Query_ID,Query_Text," + ",".join(col_headers) + ",Total_Matches\n")
        for q_id, q_text, row in zip(query_labels, queries, matrix):
            row_str = ",".join(str(int(val)) for val in row)
            total = int(np.sum(row))
            f.write(f'"{q_id}","{q_text}",{row_str},{total}\n')

    # 2. Export Formatted TXT
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write("=" * 100 + "\n")
        f.write("QUERY-DOCUMENT BOOLEAN RESULTS MATRIX (FULL 100 DOCUMENTS)\n")
        f.write("=" * 100 + "\n\n")
        f.write("Query Legend:\n")
        for q_id, q_text, row in zip(query_labels, queries, matrix):
            f.write(f"  {q_id:<4}: {q_text:<38} -> {int(np.sum(row)):2d} matches\n")
        f.write("\n")

        block_size = 20
        for start in range(0, len(doc_ids), block_size):
            end = min(start + block_size, len(doc_ids))
            block_cols = [f"D{d:02d}" for d in doc_ids[start:end]]
            block_data = matrix[:, start:end]
            col_w = 4
            row_w = 4
            header = f"{'':<{row_w}}  " + " ".join(f"{str(c):>{col_w}}" for c in block_cols)
            sep = "-" * len(header)
            f.write(f"\nBlock Documents {start + 1:03d} - {end:03d}:\n")
            f.write(header + "\n" + sep + "\n")
            for r_label, row_vals in zip(query_labels, block_data):
                vals_str = " ".join(f"{val:>{col_w}}" for val in row_vals)
                f.write(f"{r_label:<{row_w}}  {vals_str}\n")
            f.write(sep + "\n")


# ==============================================================================
# 5. Demonstration and Testing Output
# ==============================================================================
# Generate the 100 documents at module level
DOCUMENTS = generate_mock_documents(100)

if __name__ == "__main__":
    output_filename = "mock_documents.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        for doc_id, text in sorted(DOCUMENTS.items()):
            f.write(f"[Doc {doc_id}] {text}\n")
    print(f"Saved 100 documents to '{output_filename}'.")

    # Build Inverted Index and Term-Document Incidence Matrix
    index = InvertedIndex(DOCUMENTS)
    matrix = TermDocumentMatrix(DOCUMENTS)
    engine = BooleanSearchEngine(index, matrix)

    print(f"Vocabulary Size: {len(matrix.vocabulary)} unique terms across {matrix.num_docs} documents.")
    print(f"Term-Document Incidence Matrix Shape: {matrix.matrix.shape[0]} terms x {matrix.matrix.shape[1]} documents")

    # --------------------------------------------------------------------------
    # DEMO 1: Term-Document Incidence Matrix (Boolean Values 0/1)
    # --------------------------------------------------------------------------
    demo_terms = [
        "search",
        "engines",
        "vector",
        "security",
        "network",
        "database",
        "redis",
        "clusters",
        "inverted",
        "index",
    ]
    demo_doc_ids = list(range(1, 16))  # Sample Docs 1 to 15
    sub_mat, valid_terms, valid_docs = matrix.get_submatrix(demo_terms, demo_doc_ids)

    print("\n" + "=" * 80)
    print("1. DEMONSTRATION: TERM-DOCUMENT INCIDENCE MATRIX (BOOLEAN VALUES)")
    print("   Rows = Vocabulary Terms | Columns = Documents | Values = 1 (True) / 0 (False)")
    print("=" * 80)
    print_matrix_table(
        sub_mat,
        row_labels=valid_terms,
        col_labels=[f"D{d:02d}" for d in valid_docs],
        title="Term-Document Incidence Submatrix (Terms x Docs 01-15):",
    )

    # --------------------------------------------------------------------------
    # DEMO 2: Bitwise Vector Operations for Query Evaluation
    # --------------------------------------------------------------------------
    sample_q = "(search AND engines) NOT vector"
    # Show active documents for search, engines, vector to highlight 1/0 bitwise operations
    demo_calc_docs = [47, 63, 70, 72, 74, 75]
    demo_indices = [matrix.doc_id_to_idx[d] for d in demo_calc_docs]

    vec_search = matrix.get_term_vector("search")[demo_indices]
    vec_engines = matrix.get_term_vector("engines")[demo_indices]
    vec_vector = matrix.get_term_vector("vector")[demo_indices]
    vec_and = (vec_search & vec_engines)
    vec_not = (1 - vec_vector)
    vec_final = (vec_and & vec_not)

    print("\n" + "=" * 80)
    print(f"2. VECTOR BITWISE EVALUATION DEMONSTRATION: '{sample_q}'")
    print("=" * 80)
    step_matrix = np.vstack([vec_search, vec_engines, vec_and, vec_not, vec_final])
    step_labels = [
        "vec('search')",
        "vec('engines')",
        "AND: search & engines",
        "NOT: 1 - vec('vector')",
        "RESULT: AND & NOT",
    ]
    print_matrix_table(
        step_matrix,
        row_labels=step_labels,
        col_labels=[f"D{d:02d}" for d in demo_calc_docs],
        title=f"Step-by-step Boolean Vector Calculation on Target Docs {demo_calc_docs}:",
    )

    matches_set, matches_vec = engine.evaluate_both(sample_q)
    print(f"Sample Query: '{sample_q}'")
    print(f"Matches across all 100 docs: {sorted(list(matches_set))}")
    for doc_id in sorted(list(matches_set)):
        print(f"  [Doc {doc_id}]: {DOCUMENTS[doc_id]}")

    # --------------------------------------------------------------------------
    # DEMO 3: Testing Output Presented as a Matrix (Query-Document Incidence Matrix)
    # --------------------------------------------------------------------------
    test_queries = [
        "inverted AND index",
        "security AND NOT network",
        "(search AND engines) NOT vector",
        "docker OR kubernetes",
        "(database OR redis) AND cluster",
        "python AND (pipelines OR tests)",
    ]

    query_labels = [f"Q{i+1}" for i in range(len(test_queries))]
    results_matrix = np.zeros((len(test_queries), matrix.num_docs), dtype=np.int8)

    for i, q in enumerate(test_queries):
        matches, vec = engine.evaluate_both(q)
        results_matrix[i, :] = vec

    print("\n" + "=" * 80)
    print("3. TESTING OUTPUT PRESENTED AS A MATRIX (QUERY-DOCUMENT RESULTS MATRIX)")
    print("   Rows = Test Queries | Columns = Documents | 1 = Match, 0 = No Match")
    print("=" * 80)

    print("\nQuery Legend:")
    for q_id, q_text in zip(query_labels, test_queries):
        total = int(np.sum(results_matrix[int(q_id[1:]) - 1, :]))
        print(f"  {q_id:<4} : {q_text:<38} -> {total:2d} matches")

    # (A) Matrix View: Preview for Docs 1 to 20
    preview_slice = results_matrix[:, :20]
    totals = [int(np.sum(row)) for row in results_matrix]
    print_matrix_table(
        preview_slice,
        row_labels=query_labels,
        col_labels=[f"D{d:02d}" for d in range(1, 21)],
        title="[Matrix View A] Query-Document Matrix (Preview across Docs 01 to 20):",
        extra_col=totals,
        extra_header="Total",
    )

    # (B) Matrix View: Active Matching Documents Only
    active_doc_indices = np.where(results_matrix.sum(axis=0) > 0)[0]
    active_doc_ids = [matrix.doc_ids[idx] for idx in active_doc_indices]
    active_matrix = results_matrix[:, active_doc_indices]

    print_matrix_table(
        active_matrix,
        row_labels=query_labels,
        col_labels=[f"D{d:02d}" for d in active_doc_ids],
        title=f"[Matrix View B] Query-Document Matrix for All Matching Documents ({len(active_doc_ids)} docs):",
        extra_col=totals,
        extra_header="Total",
    )

    # (C) Matrix View: Full 100-Document Matrix in Blocks of 20 Documents
    print(f"\n[Matrix View C] Full Query-Document Boolean Matrix across all {matrix.num_docs} Documents:")
    block_size = 20
    for start in range(0, matrix.num_docs, block_size):
        end = min(start + block_size, matrix.num_docs)
        block_cols = [f"D{d:02d}" for d in matrix.doc_ids[start:end]]
        block_data = results_matrix[:, start:end]
        print_matrix_table(
            block_data,
            row_labels=query_labels,
            col_labels=block_cols,
            title=f"  Block Documents {start + 1:03d} - {end:03d}:",
        )

    # (D) Raw Numpy 2D Boolean Matrix Display
    print("\n[Matrix View D] Raw NumPy 2D Array Representation (shape: {} x {}):".format(
        results_matrix.shape[0], results_matrix.shape[1]
    ))
    print(results_matrix)

    # Export full matrix to CSV and TXT
    csv_filename = "query_document_matrix.csv"
    txt_filename = "query_document_matrix.txt"
    export_results_matrix(results_matrix, query_labels, test_queries, matrix.doc_ids, csv_filename, txt_filename)
    print(f"\nExported complete {results_matrix.shape[0]} x {results_matrix.shape[1]} query-document matrix to '{csv_filename}' and '{txt_filename}'.")

    # --------------------------------------------------------------------------
    # DEMO 4: Matched Document Text Snippets
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("4. MATCHED DOCUMENT DETAILS")
    print("=" * 80)
    for q_id, q in zip(query_labels, test_queries):
        matches = engine.evaluate(q)
        print(f"\n{q_id}: '{q}' -> {len(matches)} matched documents")
        for doc_id in sorted(list(matches))[:3]:
            print(f"  [Doc {doc_id}]: {DOCUMENTS[doc_id]}")
