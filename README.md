# Market Trend Predictor

Predict demand and validate product ideas using Google Trends, large-scale market text (Reddit + Amazon), semantic embeddings, and a RAG-driven analyst report.

## Description

Market Trend Predictor helps founders, product managers, and researchers rapidly validate product ideas. Enter a product idea and the system will:

- Pull a Google Trends score for the query.
- Retrieve semantically relevant market documents (Reddit posts + Amazon reviews) from a Qdrant vector database.
- Synthesize an evidence-backed market report using a generative LLM, including demand score, target audience, pros/risks, and launch recommendation.

## Features

- Google Trends integration via `pytrends` for real-world interest signals.
- Document ingestion and embedding using `sentence-transformers`.
- Vector storage and nearest-neighbor search with Qdrant (`vector_db/`).
- RAG (retrieval-augmented generation) report production using a configured generative model.
- Streamlit UI in `app.py` for interactive use and PDF export of reports.

## Contents

- `app.py` - Streamlit web UI and report generator.
- `ingest.py` - Builds documents from datasets, creates embeddings, and uploads to Qdrant.
- `rag.py` - CLI-style RAG runner for single-query reports.
- `google_trends.py` - Helper for retrieving Google Trends scores.
- `data/` - Raw datasets used for ingestion (Reddit, Amazon reviews).
- `vector_db/` - Local Qdrant storage (collection: `market_data`).
- `requirements.txt` - Python dependencies.

## Quickstart

1. Create and activate a Python environment (recommended Python 3.10+).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Environment variables

Create a `.env` file with any required keys. Examples used in the repo:

- `GOOGLE_API_KEY` — if using Google generative APIs in `rag.py`.
- Other API keys (if you swap the LLM provider) can be added as needed.

3. Ingest data (optional — only if you want to rebuild vectors)

```powershell
python ingest.py
```

4. Run the Streamlit app

```powershell
streamlit run app.py
```

5. Run the CLI RAG tool (example)

```powershell
python rag.py
# then enter a product idea at the prompt
```

## Notes

- The repository stores vectors in `vector_db/` for local Qdrant usage. If you delete or re-create this folder, re-run `ingest.py` to rebuild the collection.
- `ingest.py` limits rows during demo runs (`head(2000)`) — adjust as needed for full ingestion.
- `google_trends.py` returns a neutral score (50) on failure to avoid blocking the pipeline.

## GitHub-friendly files

### Add to the repo

- `app.py`
- `rag.py`
- `ingest.py`
- `google_trends.py`
- `requirements.txt`
- `README.md`
- `.gitignore`
- `.env.example` or docs showing required keys
- helper scripts such as `download_data.py` if you add one

### Keep out of the repo

- `data/*.csv` if files are larger than 100 MB
- `vector_db/` (generated Qdrant storage)
- `report_cache.db`
- Python caches and compiled files

## Data download guidance

Large datasets should be stored externally (Google Drive, Dropbox, S3, Kaggle, etc.). Add a small script or README section that explains how to download the data and place it in `data/`.
