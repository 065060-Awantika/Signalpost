# Signalpost

> Evidence-first company intelligence for Norwegian businesses.

Signalpost is a company research and intelligence system that takes a Norwegian organization number and turns it into a structured, evidence-backed company profile.

It resolves the company through the official Norwegian Register of Business Enterprises (BRREG), discovers publicly available company sources, extracts structured facts, verifies that the information belongs to the correct company, stores evidence, and detects changes over time.

## What Signalpost Does

```text
Norwegian Organization Number
            |
            v
       BRREG Registry
            |
            v
     Company Identity
            |
            v
      Registry Facts
            |
            v
     Source Discovery
            |
            v
      Source Fetching
            |
            v
      HTML Cleaning
            |
            v
     Fact Extraction
            |
            v
    Entity Verification
            |
            v
     Evidence Storage
            |
            v
     Change Detection
            |
            v
       Company UI
```

### Core principle

**Fact -> Evidence -> Source -> Verification -> Update**

---

## Key Features

### 1. Official Company Resolution

Signalpost uses BRREG as the authoritative starting point for company identity.

It can resolve:

- Legal company name
- Organization number
- Company type
- Business address
- City
- Municipality
- Industry
- Industry code
- Website

### 2. Public Source Discovery

Signalpost discovers relevant public company sources, including:

- Company homepage
- About pages
- Company pages
- Investor pages
- News pages
- Contact pages
- Official BRREG records

Each source is tracked with its URL and source type.

### 3. Evidence-First Fact Extraction

Signalpost extracts structured facts from public company content.

Supported fact types include:

- Organization number
- Legal name
- Website
- Industry
- Address
- City
- Employee count
- Founded year
- Email
- Phone
- Country
- Company type
- Industry code
- Municipality
- Postal information

Each fact can contain:

- Field name
- Value
- Evidence text
- Confidence score
- Source
- Retrieval timestamp
- Verification status

### 4. Entity Verification

Signalpost verifies source identity using multiple signals:

- Organization number
- Company name
- Website domain
- Address

Verification statuses:

```text
VERIFIED
REVIEW
REJECTED
```

A conflicting organization number causes the source to be rejected.

### 5. Change Detection

Signalpost stores historical company facts so that new research can be compared with previous research.

Detected changes include:

- ADDED
- MODIFIED
- REMOVED

Example:

```text
Field: employee_count

Previous: 24,000
Current: 25,000

Change Type: MODIFIED
```

Pending or uncertain facts are not automatically treated as confirmed changes.

---

## 1,000+ Company Coverage

Signalpost includes a bulk bootstrap pipeline for creating a large company profile base from BRREG.

Validated run:

```text
Companies processed : 1000
Successful          : 1000
Failed              : 0
```

---

## Architecture

```text
                         +----------------------+
                         | Norwegian Org Number |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |     BRREG Client     |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |  Company Repository  |
                         +----------+-----------+
                                    |
                    +---------------+---------------+
                    |                               |
                    v                               v
          +------------------+             +------------------+
          |  Registry Facts  |             | Source Discovery |
          +--------+---------+             +--------+---------+
                   |                                |
                   |                                v
                   |                       +----------------+
                   |                       | Source Fetcher |
                   |                       +-------+--------+
                   |                               |
                   |                               v
                   |                       +----------------+
                   |                       |  HTML Cleaner  |
                   |                       +-------+--------+
                   |                               |
                   |                               v
                   |                       +----------------+
                   |                       | Fact Extractor |
                   |                       +-------+--------+
                   |                               |
                   +---------------+---------------+
                                   |
                                   v
                         +----------------------+
                         | Entity Verification |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Evidence Ingestion   |
                         +----------+-----------+
                                    |
                                    v
                            +---------------+
                            |   SQLite DB   |
                            +-------+-------+
                                    |
                       +------------+------------+
                       |                         |
                       v                         v
              +----------------+        +------------------+
              | Change Detector|        |    FastAPI API   |
              +----------------+        +--------+---------+
                                                 |
                                                 v
                                        +------------------+
                                        | Signalpost UI    |
                                        +------------------+
```

---

## Technology Stack

### Backend

- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite
- Requests
- BeautifulSoup

### Frontend

- HTML
- CSS
- Vanilla JavaScript

### Data Sources

- Norwegian Register of Business Enterprises (BRREG)
- Publicly accessible company websites and sources

### Testing

- Pytest

The core pipeline does not require a paid LLM API.

---

## Project Structure

```text
signalpost/
|
+-- backend/
|   +-- app/
|   |   +-- api/
|   |   |   +-- changes.py
|   |   |   +-- companies.py
|   |   |   +-- intelligence.py
|   |   |
|   |   +-- database/
|   |   +-- models/
|   |   +-- scrapers/
|   |   +-- services/
|   |   +-- verification/
|   |
|   +-- tests/
|
+-- data/
|   +-- company_numbers.txt
|
+-- frontend/
|   +-- index.html
|   +-- styles.css
|   +-- app.js
|
+-- scripts/
|   +-- bootstrap_1000.py
|   +-- bulk_research.py
|
+-- requirements.txt
+-- .gitignore
+-- README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/065060-Awantika/Signalpost.git
cd Signalpost
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

## Running the Backend

Start FastAPI:

```bash
python -m uvicorn backend.app.main:app --reload
```

Backend:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

---

## Running the Frontend

In a second terminal:

```bash
python -m http.server 5500 --directory frontend
```

Open:

`http://127.0.0.1:5500`

The frontend allows a user to enter a Norwegian organization number and view the resulting company intelligence profile.

---

## Example Research

Example organization number:

```text
923609016
```

This resolves to:

```text
EQUINOR ASA
```

Research endpoint:

```text
POST /companies/{organization_number}/research
```

Example:

```text
POST /companies/923609016/research
```

Change endpoint:

```text
GET /companies/923609016/changes
```

---

## Bulk Company Bootstrap

Signalpost includes a bootstrap script that retrieves company records from BRREG and stores them locally.

Run:

```bash
python -m scripts.bootstrap_1000
```

Validated result:

```text
Companies processed : 1000
Successful          : 1000
Failed              : 0
```

---

## Bulk Research

Organization numbers can be stored in:

```text
data/company_numbers.txt
```

One organization number per line:

```text
923609016
123456789
987654321
```

Run:

```bash
python scripts/bulk_research.py
```

The bulk process records:

- Company identity
- Research success/failure
- Source results
- Extracted fact counts
- Research results

---

## Change Detection

Signalpost supports historical comparison of company facts.

```text
Previous Facts
      |
      v
Current Facts
      |
      v
Change Detector
      |
  +---+---------+
  |   |         |
  v   v         v
 ADD MODIFY   REMOVE
```

Example:

```text
Field: employee_count

Previous Value: 24,000
Current Value: 25,000

Change Type: MODIFIED
```

Pending facts are ignored when determining confirmed changes.

The change repository also prevents the same fact transition from being recorded repeatedly.

---

## Testing

Run the complete backend test suite:

```bash
python -m pytest backend/tests -q
```

Latest validated result:

```text
87 passed
1 warning
0 failed
```

Additional change-detection tests:

```text
9 passed
```

The warning is a Starlette/httpx test-client deprecation warning and does not represent a failing test.

---

## Cost

Signalpost is designed to operate without paid AI APIs.

The core pipeline uses:

- BRREG public data
- Public web pages
- Deterministic extraction
- Rule-based entity verification
- Local SQLite storage
- Open-source Python libraries

No paid API key is required for the core implementation.

This keeps the prototype within the challenge's external API cost constraints.

---

## Evidence and Verification Philosophy

Signalpost follows three principles.

### Identity Before Intelligence

Before accepting information from a source, Signalpost determines which company the source belongs to.

### Evidence Before Claims

Facts are stored together with the evidence text from which they were extracted.

### Preserve Uncertainty

Not every extracted fact is automatically considered confirmed.

The system distinguishes between:

```text
VERIFIED
REVIEW
PENDING
REJECTED
```

This allows uncertain information to remain visible without presenting it as confirmed intelligence.

---

## Confidence

Extracted facts contain confidence scores.

Typical examples:

| Fact | Typical Confidence |
|---|---:|
| Organization Number | 98%+ |
| Legal Name | 90%+ |
| Website | 95%+ |
| Employee Count | 90% |
| Industry | 85% |
| Address | 85% |

Official BRREG facts receive stronger verification treatment because BRREG is the authoritative registry source.

---

## Source Evidence

Every persisted fact can be associated with a source.

A source record can contain:

- URL
- Source type
- Publisher
- Retrieved timestamp
- Content hash
- Raw retrieved content

Relationship:

```text
Company
   |
   v
Fact
   |
   v
Evidence
   |
   v
Source URL
```

This makes the system traceable and auditable.

---

## Challenge Alignment

| Evaluation Area | Signalpost Implementation |
|---|---|
| Coverage | 1,000-company BRREG bootstrap |
| Correct company matching | Multi-signal entity verification |
| Evidence | Fact-level evidence and source storage |
| Updates | Historical facts and change detection |
| Explanations | Evidence text and confidence scores |
| Usability | FastAPI backend and web dashboard |
| Cost efficiency | No paid LLM API required |

---

## Future Improvements

Potential extensions include:

- Scheduled automatic company refresh
- More public source types
- Improved news extraction
- Financial statement extraction
- Industry-specific intelligence
- Confidence aggregation across multiple sources
- Duplicate-source suppression
- Rate-limited parallel research
- Company search and filtering
- CSV/JSON export
- Automated change alerts
- Scheduled monitoring of important company facts

---

## Project Highlights

Signalpost demonstrates an end-to-end company intelligence workflow:

```text
INPUT
  |
  v
Organization Number
  |
  v
IDENTITY
  |
  v
BRREG Verification
  |
  v
DISCOVERY
  |
  v
Public Sources
  |
  v
EXTRACTION
  |
  v
Structured Facts
  |
  v
VERIFICATION
  |
  v
Evidence-backed Facts
  |
  v
STORAGE
  |
  v
Historical Records
  |
  v
UPDATES
  |
  v
Change Detection
```

The core idea:

> **Don't just find company information. Prove where it came from, verify that it belongs to the right company, and detect when it changes.**

---

## Repository

GitHub: https://github.com/065060-Awantika/Signalpost

Built as a proof-of-concept for the Builderr.ai company information agent challenge.
