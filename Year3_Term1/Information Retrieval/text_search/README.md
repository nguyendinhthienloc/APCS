# Information Retrieval - Homework 1: Text-Based Search Engine

**Student ID (MSSV):** 24125093

## Overview
A text-based search engine built with **Whoosh** and **Streamlit** using crawled VnExpress articles.

## Key Features & Requirements
- **Text-Based Search Engine (Whoosh)**: Implemented with `MultifieldParser` and `BM25F` ranking scoring. Match fields include `article_title` (boosted by 2.0x), `category`, and `comments`.
- **Graphical User Interface (Streamlit)**: Interactive web interface showing real-time query results, execution latency in milliseconds, metadata badges (category, score, publish date), snippet/comment previews, and direct links to the articles.
- **Single-Index Guarantee**: Protected by a two-layer defense:
  1. *Disk-level verification* (`index.exists_in`): Skips parsing and creating index if already built on disk.
  2. *Streamlit memory caching* (`@st.cache_resource`): Retains the index in RAM to prevent redundant file open operations during user interactions.

## How to Run

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the application**:
   ```bash
   streamlit run app.py
   ```
   or from the parent directory:
   ```bash
   streamlit run 24125093/app.py
   ```
