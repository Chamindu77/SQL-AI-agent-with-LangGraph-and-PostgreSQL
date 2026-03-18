# 🤖 SQL AI Agent

> An intelligent, self-correcting SQL agent built with **LangGraph**, **PostgreSQL**, and **OpenRouter** that converts natural language questions into accurate database queries using the **Reflection design pattern**.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Reflection Design Pattern](#reflection-design-pattern)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Agent](#running-the-agent)
- [API Reference](#api-reference)
- [Postman Usage](#postman-usage)
- [Free Models (OpenRouter)](#free-models-openrouter)
- [Example Queries](#example-queries)
- [Tech Stack](#tech-stack)

---

## Overview

SQL AI Agent allows users to query any PostgreSQL database using plain English. Instead of writing SQL manually, you simply ask a question like:

> *"Which category generated the most revenue last month?"*

The agent automatically:
1. Reads your database schema
2. Generates a SQL query
3. Executes it against PostgreSQL
4. **Reflects** on the result and fixes any errors
5. Returns a clean, accurate answer

---

## Architecture

```
<img width="728" height="638" alt="Screenshot 2026-03-18 091906" src="https://github.com/user-attachments/assets/10689b22-fbc8-4c40-8a53-bd21ab07f412" />

```

---

## Reflection Design Pattern

This project implements the **Reflection Pattern** — a core agentic AI design pattern where the agent reviews its own outputs and iteratively improves them before returning a final answer.

### Why reflection matters

A first-pass SQL query often has subtle issues:
- Negative totals (sales stored as negative `qty_delta`)
- Missing filters (wrong date range)
- Wrong aggregations (SUM vs ABS)

Without reflection, these errors are silently returned as answers. With reflection:

| Pass | What happens |
|------|-------------|
| **V1** | LLM generates initial SQL from question + schema |
| **Execute** | SQL runs against real PostgreSQL data |
| **Reflect** | LLM sees actual output, identifies issues, rewrites SQL |
| **V2** | Corrected SQL is re-executed |
| **Final** | Verified, accurate result returned |

The `MAX_REFLECTION_RETRIES` setting controls how many correction loops run (default: `2`).

---

## Project Structure

```
sql_ai_agent/
│
├── .env                        
├── requirements.txt            
├── README.md                   
│
├── app/
│   ├── __init__.py
│   ├── main.py                 
│   ├── config.py               
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py            
│   │   ├── state.py            
│   │   ├── nodes.py            
│   │   └── edges.py            
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── db.py               
│   │   └── schema.py          
│   │
│   └── prompts/
│       ├── generate_sql.py     
│       └── reflect_sql.py      
│
├── tests/
│   ├── test_nodes.py
│   ├── test_db.py
│   └── test_graph.py
│
└── scripts/
    ├── seed_db.py              
    └── run_agent.py            
```

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** installed
- **PostgreSQL 14+** running locally or remotely
- **OpenRouter API key** — free at [openrouter.ai/keys](https://openrouter.ai/keys)
- **Postman** (optional) — for API testing

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Chamindu77/SQL-AI-agent-with-LangGraph-and-PostgreSQL.git
cd sql-ai-agent
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

**`requirements.txt`**
```
langgraph>=0.2.0
langchain-openai>=0.1.0
langchain-anthropic>=0.1.0
langchain-core>=0.2.0
psycopg2-binary>=2.9.9
sqlalchemy>=2.0.0
fastapi>=0.111.0
uvicorn>=0.30.0
python-dotenv>=1.0.0
pandas>=2.0.0
tabulate>=0.9.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
```

---

## Configuration

### 1. Create your `.env` file

```env
# OpenRouter (free LLM API)
OPENROUTER_API_KEY=sk-or-your-key-here
LLM_MODEL=meta-llama/llama-3.3-70b-instruct:free

# PostgreSQL 
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/sql_agent_db

#  Agent settings 
MAX_REFLECTION_RETRIES=2
```

> **Get your free OpenRouter key:** Visit [openrouter.ai/keys](https://openrouter.ai/keys) → Sign up → Create key

### 2. Verify configuration loads correctly

```bash
python -c "from app.config import settings; print(settings.llm_model)"
```

---

## Database Setup

### 1. Create the database in PostgreSQL

```sql
CREATE DATABASE sql_agent_db;
```

### 2. Seed sample data

```bash
python scripts/seed_db.py
```

This creates a `transactions` table with product sales data across multiple months.

### Schema overview

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-increment primary key |
| `product_name` | TEXT | Name of the product |
| `category` | TEXT | Product category |
| `color` | TEXT | Product color |
| `action` | TEXT | Event type: `sale`, `restock`, `insert`, `price_update` |
| `qty_delta` | INTEGER | Stock change (negative for sales) |
| `unit_price` | NUMERIC | Price at time of event (NULL for restock) |
| `ts` | TIMESTAMP | Event timestamp |

> **Note:** `qty_delta` is stored as a **negative number for sales** (stock leaving). The reflection step catches and corrects queries that forget to apply `ABS()` when calculating totals.

---

## Running the Agent

### Option A — CLI (terminal)

```bash
python scripts/run_agent.py "Which category generated the most revenue?"
```

**Sample output:**
```
 Question: Which category generated the most revenue?
────────────────────────────────────────────────────────────
 SQL V1:
SELECT category, SUM(qty_delta * unit_price) FROM transactions ...

 Reflection feedback:
The total sales are negative because qty_delta is negative for sales.
Applying ABS() to fix the calculation.

 Final SQL:
SELECT category, SUM(ABS(qty_delta) * unit_price) AS total_revenue ...

 Answer:
| category    | total_revenue |
|:------------|:-------------|
| Electronics | 1249.50      |
────────────────────────────────────────────────────────────
```

### Option B — REST API (FastAPI)

Start the server:

```bash
uvicorn app.main:app --reload
```

Server runs at: `http://127.0.0.1:8000`

Interactive API docs: `http://127.0.0.1:8000/docs`

---

## API Reference

### `POST /ask`

Ask a natural language question about your database.

**Request body:**
```json
{
  "question": "Which category generated the most revenue?"
}
```

**Response:**
```json
{
  "question": "Which category generated the most revenue?",
  "sql": "SELECT category, SUM(ABS(qty_delta) * unit_price) AS total_revenue FROM transactions WHERE action = 'sale' GROUP BY category ORDER BY total_revenue DESC LIMIT 1",
  "feedback": "The original query had negative totals due to negative qty_delta for sales. Fixed by applying ABS().",
  "answer": "| category    | total_revenue |\n|:------------|:-------------|\n| Electronics | 1249.50      |"
}
```

### `GET /health`

Health check endpoint.

**Response:**
```json
{ "status": "ok" }
```

---

## Postman Usage

### Setup

| Setting | Value |
|---------|-------|
| Method | `POST` |
| URL | `http://127.0.0.1:8000/ask` |
| Header Key | `Content-Type` |
| Header Value | `application/json` |
| Body type | `raw` → `JSON` |

### Request body

```json
{
  "question": "Show me all sale transactions"
}
```


### Steps in Postman

1. Open Postman → click **New Request**
2. Set method to **POST**
3. Enter URL: `http://127.0.0.1:8000/ask`
4. Click **Headers** tab → add `Content-Type: application/json`
5. Click **Body** tab → select **raw** → choose **JSON** from dropdown
6. Paste your JSON body
7. Click **Send**

---

## Free Models (OpenRouter)

Get a free API key at [openrouter.ai](https://openrouter.ai) and use any of these models:

| Model | Strength | Set in `.env` |
|-------|----------|---------------|
| `meta-llama/llama-3.3-70b-instruct:free` | Best overall for SQL | ✅ Recommended |
| `deepseek/deepseek-r1:free` | Strong reasoning & code | ✅ Good for complex queries |
| `google/gemma-3-27b-it:free` | Balanced performance | ✅ Good fallback |
| `mistralai/mistral-7b-instruct:free` | Fast & lightweight | ⚡ Quick responses |

> **Rate limits:** Free models may occasionally return `429 Too Many Requests`. If this happens, wait a few seconds and retry, or switch to a different free model in `.env`.

---

## Example Queries

Try these questions with the seeded sample data:

```bash
# Revenue analysis
python scripts/run_agent.py "Which category generated the most revenue?"
python scripts/run_agent.py "Which category generated the most revenue last month?"
python scripts/run_agent.py "What is the total revenue for each product?"

# Sales analysis
python scripts/run_agent.py "Show me all sale transactions"
python scripts/run_agent.py "Which color has the highest total units sold?"
python scripts/run_agent.py "Show me all transactions from this month"

# Inventory
python scripts/run_agent.py "What is the current stock level for each product?"
python scripts/run_agent.py "Which product was restocked most recently?"

# Pricing
python scripts/run_agent.py "Which product has the highest unit price?"
python scripts/run_agent.py "Show the average price per category"
```
---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Agent orchestration** | [LangGraph](https://github.com/langchain-ai/langgraph) |
| **LLM calls** | [LangChain OpenAI](https://python.langchain.com/) via [OpenRouter](https://openrouter.ai) |
| **Database** | [PostgreSQL](https://www.postgresql.org/) |
| **DB connector** | [SQLAlchemy](https://www.sqlalchemy.org/) + [psycopg2](https://pypi.org/project/psycopg2/) |
| **REST API** | [FastAPI](https://fastapi.tiangolo.com/) |
| **Server** | [Uvicorn](https://www.uvicorn.org/) |
| **Data handling** | [Pandas](https://pandas.pydata.org/) |
| **Config** | [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) + [python-dotenv](https://pypi.org/project/python-dotenv/) |

---

## License

MIT License — feel free to use, modify, and distribute.

---

> Built with the **Reflection design pattern** for reliable, self-correcting AI agents.
