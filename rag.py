import os
from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

import google.generativeai as genai

from google_trends import get_trend_score

# ----------------------------------
# LOAD ENV VARIABLES
# ----------------------------------

load_dotenv()

genai.configure(
    api_key=os.getenv("GOOGLE_API_KEY")
)

llm = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# ----------------------------------
# LOAD EMBEDDING MODEL
# ----------------------------------

print("Loading embedding model...")

embedder = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# ----------------------------------
# LOAD VECTOR DATABASE
# ----------------------------------

print("Loading vector database...")

client = QdrantClient(
    path="vector_db"
)

# ----------------------------------
# USER QUERY
# ----------------------------------

query = input(
    "\nEnter Product Idea: "
)

# ----------------------------------
# GOOGLE TRENDS
# ----------------------------------

trend_score = get_trend_score(query)

print(
    f"\nGoogle Trends Score: {trend_score}/100"
)

# ----------------------------------
# QUERY EMBEDDING
# ----------------------------------

query_vector = embedder.encode(
    query
).tolist()

# ----------------------------------
# RETRIEVE DOCUMENTS
# ----------------------------------

results = client.query_points(
    collection_name="market_data",
    query=query_vector,
    limit=10
)

# ----------------------------------
# BUILD CONTEXT
# ----------------------------------

context = ""

for point in results.points:

    source = point.payload.get(
        "source",
        "unknown"
    )

    text = point.payload.get(
        "text",
        ""
    )

    context += f"""
SOURCE: {source}

TEXT:
{text}

----------------------------------------
"""

# ----------------------------------
# PROMPT
# ----------------------------------

prompt = f"""
You are an expert market analyst.

Google Trends Score:
{trend_score}/100

Retrieved Market Data:

{context}

Product Idea:
{query}

IMPORTANT:

1. Use retrieved context as PRIMARY evidence.
2. Use Google Trends score as current market signal.
3. You may use general business reasoning if needed.
4. Clearly separate evidence and inference.

Provide:

1. Demand Score (/100)

2. Trend Analysis

3. Target Audience

4. Evidence from Retrieved Data

5. Market Inference

6. Pros

7. Risks

8. Launch Recommendation
"""

# ----------------------------------
# GENERATE REPORT
# ----------------------------------

print("\nGenerating report...\n")

response = llm.generate_content(
    prompt
)

# ----------------------------------
# OUTPUT
# ----------------------------------

print("\n")
print("=" * 60)
print("MARKET TREND REPORT")
print("=" * 60)
print("\n")

print(response.text)

# ----------------------------------
# CLOSE DB
# ----------------------------------

client.close()