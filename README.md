# SEO-URL-Automator

![CI Status](https://img.shields.io/github/actions/workflow/status/fabricio-hunt/sistema-de-tratamento-de-parametos-de-url/ci.yml?label=CI)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?logo=streamlit&logoColor=white)
![Databricks](https://img.shields.io/badge/Databricks-SQL-FF3621?logo=databricks&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

> Automated URL normalization and 301 redirect management for VTEX e-commerce platforms — powered by a Streamlit UI, Databricks SQL backend, and a dedicated VTEX API client.

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Setup](#local-setup)
  - [Environment Variables](#environment-variables)
- [Usage](#usage)
- [CI/CD Pipeline](#cicd-pipeline)
- [Security](#security)
- [Author](#author)

---

## Overview

**SEO-URL-Automator** is a production-ready internal tool built for BEMOL's e-commerce team. It automates the ingestion, cleaning, filtering, and dispatching of 301 redirects directly to the VTEX Rewriter API — eliminating hundreds of hours of manual SEO audit work.

The application detects product-slug URLs using a regex filter, presents results through a modern **Streamlit** web UI, and stores processed data in **Databricks Delta Lake** for traceability and analytics.

---

## Problem Statement

During platform migrations or information architecture changes, legacy URLs frequently generate crawl errors and 404s at scale. Manually identifying patterns in datasets with thousands of entries is inefficient and error-prone.

This tool solves the problem with:

1. **Agnostic Ingestion** — Accepts URLs pasted directly or uploaded as `.csv` / `.txt` files.
2. **Algorithmic Normalization** — Lowercases paths, strips query parameters and fragments.
3. **Regex-based Filtering** — Precisely identifies product SKU URLs matching the VTEX slug pattern:
   $$u \in \{ s \in \Sigma^* \mid s \text{ ends with } (/p \cup -p) \cdot d^+,\ d \in [0\text{-}9] \}$$
4. **Automated Redirect Dispatch** — Sends batched 301 redirect payloads to VTEX via the official Rewriter API.
5. **Databricks Persistence** — Stores every processed redirect batch in a Delta Lake table for full audit history.

---

## Architecture

The system follows a **layered, decoupled architecture** for testability and maintainability:

```
┌──────────────────────────────────────────────────────┐
│                  Streamlit UI (app.py)                │
│  Step 1: Input URLs   Step 2: Process   Step 3: Send │
└───────────────────────────┬──────────────────────────┘
                            │
              ┌─────────────▼─────────────┐
              │  Business Logic (backend.py)│
              │  - extract_paths()          │
              │  - filter_product_urls()    │
              │  - build_redirects()        │
              └──────┬──────────────┬──────┘
                     │              │
       ┌─────────────▼───┐  ┌───────▼──────────────┐
       │  DAL (dal.py)   │  │ VTEX Client           │
       │  Databricks SQL │  │ (vtex_client.py)      │
       └─────────────────┘  └──────────────────────┘
                     │
       ┌─────────────▼───────────────┐
       │  Config (config.py)         │
       │  Reads st.secrets / .env    │
       └─────────────────────────────┘
```

| File | Responsibility |
|---|---|
| `app.py` | Streamlit frontend — input, process, send redirects |
| `backend.py` | Business logic — pure URL transformation functions |
| `dal.py` | Data Access Layer — Databricks SQL connection & queries |
| `vtex_client.py` | VTEX HTTP client — create, list, delete redirects |
| `config.py` | Centralized credential loading (`.env` + `st.secrets`) |

---

## Key Features

- 🖥️ **Modern Streamlit Web UI** with dark theme and step-by-step workflow
- ⚡ **Batch 301 redirect creation** via VTEX Rewriter API with progress tracking
- 🗄️ **Databricks SQL integration** for reading raw URL tables and persisting processed redirects to Delta Lake
- 🔐 **Zero hardcoded credentials** — all secrets loaded from `.env` (local) or Streamlit Cloud Secrets (production)
- 📁 **Flexible URL input** — paste text, upload CSV, or upload TXT files
- 📊 **Real-time metrics** — raw URLs, generated redirects, and utilization rate
- ⬇️ **CSV download** of generated redirect table before sending
- 🛡️ **CI/CD with GitHub Actions** — lint (Ruff), type check (Mypy), tests (Pytest), SAST (Bandit), secret scan (detect-secrets)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | [Streamlit](https://streamlit.io/) 1.32+ |
| Data Processing | [Pandas](https://pandas.pydata.org/) 2.0+ |
| Database | [Databricks SQL Connector](https://docs.databricks.com/dev-tools/python-sql-connector.html) |
| VTEX API | [Requests](https://requests.readthedocs.io/) via VTEX Rewriter REST API |
| Config/Secrets | `python-dotenv` + `st.secrets` |
| Linting | [Ruff](https://docs.astral.sh/ruff/) |
| Type Checking | [Mypy](https://mypy-lang.org/) |
| Testing | [Pytest](https://pytest.org/) |
| SAST | [Bandit](https://bandit.readthedocs.io/) |
| CI/CD | GitHub Actions |

---

## Getting Started

### Prerequisites

- Python 3.11+
- A Databricks SQL Warehouse with access credentials
- A VTEX account with an App Key and App Token

### Local Setup

```bash
git clone https://github.com/fabricio-hunt/sistema-de-tratamento-de-parametos-de-url.git
cd sistema-de-tratamento-de-parametos-de-url

python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root (it is already in `.gitignore` and will **never** be committed):

```env
# Databricks
DATABRICKS_HOST=adb-xxxxxxxxxxxx.x.azuredatabricks.net
DATABRICKS_HTTP_PATH=sql/protocolv1/o/xxxx/xxxx
DATABRICKS_TOKEN=dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# VTEX
VTEX_ACCOUNT=your-account-name
VTEX_ENVIRONMENT=vtexcommercestable
VTEX_APP_KEY=your-app-key
VTEX_APP_TOKEN=your-app-token
```

> **Streamlit Cloud:** Add the same keys under **Settings → Secrets** in your Streamlit Cloud dashboard instead of a `.env` file.

Then run the app:

```bash
streamlit run app.py
```

---

## Usage

The application guides you through three steps:

**Step 1 — Input URLs**
Paste URLs directly into the text field (one per line) or upload a `.csv` / `.txt` file.

**Step 2 — Process URLs**
Click **"⚡ Process URLs"**. The backend extracts paths, strips query strings, and filters only valid VTEX product URLs matching the `-p{digits}` pattern. A metrics dashboard shows total input, generated redirects, and utilization rate. You can download the result as CSV before proceeding.

**Step 3 — Send to VTEX**
Confirm the action and click **"🚀 Send to VTEX now"**. The VTEX client sends each redirect via the Rewriter API with a real-time progress bar and a per-URL error report.

---

## CI/CD Pipeline

Two workflows run on every push to `main` or `develop`:

**`.github/workflows/ci.yml`** — Full quality gate:
| Step | Tool | Purpose |
|---|---|---|
| Lint | Ruff | Style and code quality |
| Type Check | Mypy | Static type verification |
| Tests | Pytest | Unit tests with mocked credentials |
| SAST | Bandit | Static security analysis |
| Secret Scan | detect-secrets | Prevents credential leaks |

**`.github/workflows/main.yml`** — Integration smoke test:
Runs the processing pipeline end-to-end with a sample URL and uploads the resulting `output.csv` as a build artifact.

---

## Security

- All credentials are loaded exclusively from **environment variables** or **Streamlit Secrets** — never hardcoded.
- `.env`, `.streamlit/`, `.venv/`, `__pycache__/`, and `*.csv` are listed in `.gitignore`.
- SAST (Bandit) and secret scanning (detect-secrets) run automatically on every CI build.

---

## Author

**Fabricio Barauna** — BEMOL Digital & E-commerce Team

[![GitHub](https://img.shields.io/badge/GitHub-fabricio--hunt-181717?logo=github)](https://github.com/fabricio-hunt)
