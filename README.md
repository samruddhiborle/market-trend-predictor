# Market Trend Predictor

## Overview

Market Trend Predictor is an AI-powered market validation platform that helps entrepreneurs, startups, and product teams evaluate new product ideas before launch.

The system combines:

* Google Trends for real-world search demand
* Reddit discussions for consumer sentiment and market conversations
* Amazon reviews for product feedback and customer insights
* Semantic search using Sentence Transformers and Qdrant
* Retrieval-Augmented Generation (RAG) for evidence-backed market reports

Users simply enter a product idea, and the system generates a detailed market analysis report including demand score, target audience, market opportunities, risks, and launch recommendations.

---

## Features

### Google Trends Integration

Analyze real-world search interest and demand patterns using Google Trends.

### Semantic Market Retrieval

Retrieve relevant Reddit discussions and Amazon reviews using vector embeddings and similarity search.

### RAG-Based Market Intelligence

Generate structured market reports grounded in retrieved evidence rather than generic AI responses.

### AI-Powered Analysis

Evaluate:

* Demand Score
* Trend Analysis
* Target Audience
* Market Opportunities
* Risks and Challenges
* Launch Recommendations

### Interactive Streamlit Dashboard

Modern web interface with:

* Product analysis workflow
* Real-time progress tracking
* Trend metrics
* Downloadable reports

### PDF Report Export

Download generated market reports for sharing and documentation.

---

## System Architecture

```text
User Input
    ↓
Google Trends API
    ↓
Query Embedding
    ↓
Qdrant Vector Search
    ↓
Relevant Reddit + Amazon Data
    ↓
RAG Pipeline
    ↓
LLM Report Generation
    ↓
Market Intelligence Dashboard
```

---

## Tech Stack

### Frontend

* Streamlit

### AI & Machine Learning

* Groq / LLM
* Sentence Transformers
* Retrieval-Augmented Generation (RAG)

### Vector Database

* Qdrant

### Data Sources

* Google Trends
* Reddit Discussions
* Amazon Product Reviews

### Utilities

* Python
* ReportLab
* Python Dotenv

---

## Project Structure

```text
Market-Trend-Predictor/
│
├── app.py
├── rag.py
├── ingest.py
├── google_trends.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── vector_db/
│
└── data/
    ├── business_data.csv
    ├── Entrepreneur_data.csv
    ├── engineering_data.csv
    ├── employment_reddit_data.csv
    ├── povertyfinance_data.csv
    ├── science_data.csv
```

---

## Example Workflow

1. Enter a product idea
2. Fetch Google Trends score
3. Retrieve relevant market documents
4. Generate AI-powered market report
5. Review opportunities and risks
6. Download the report

Example product ideas:

* Protein Chips
* Sustainable Clothing
* AI Resume Builder
* Smart Water Bottle
* Budget Travel Planner

---

## Sample Output

The generated report includes:

* Demand Score
* Trend Analysis
* Target Audience
* Supporting Evidence
* Market Inference
* Pros and Cons
* Risk Assessment
* Launch Recommendation

---

## Future Enhancements

* Live Reddit API Integration
* Real-Time Amazon Review Analysis
* Trend Visualization Charts
* Competitor Analysis
* Multi-LLM Support
* Report History Dashboard
* Cloud Qdrant Deployment
* Market Forecasting Models
* Social Media Trend Analysis (Instagram, X/Twitter, YouTube, TikTok)
* Influencer & Creator Trend Tracking
* Hashtag Popularity Analysis

---

Due to GitHub's file size limitations, the datasets used for training and vector database generation are not included in this repository.

The complete dataset collection can be downloaded from the following Google Drive link:

Dataset Download: https://drive.google.com/drive/folders/11F-s71Y9sGdhhnZCStlpDx5FRDPzJJC3?usp=sharing
