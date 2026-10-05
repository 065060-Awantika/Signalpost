# Signalpost

> Evidence-first AI company intelligence for Norwegian businesses.

Signalpost takes a Norwegian organization number and turns it into a structured company intelligence profile.

It resolves the company through the official Norwegian Register of Business Enterprises (BRREG), discovers public company sources, extracts useful facts, verifies that the evidence belongs to the correct company, stores the evidence, and detects changes over time.

---

## 🚀 What Signalpost Does

Signalpost follows an evidence-first research pipeline:

```text
Norwegian Organization Number
            │
            ▼
       BRREG Registry
            │
            ▼
     Company Identity
            │
            ▼
     Registry Facts
            │
            ▼
     Source Discovery
            │
            ▼
      Source Fetching
            │
            ▼
    Content Extraction
            │
            ▼
     Fact Extraction
            │
            ▼
    Entity Verification
            │
            ▼
      Evidence Storage
            │
            ▼
      Change Detection

      # Signalpost

> Evidence-first company intelligence for Norwegian businesses.

Signalpost is a company research and intelligence system that takes a Norwegian organization number and turns it into a structured, evidence-backed company profile.

The system resolves the company through the official Norwegian Register of Business Enterprises (BRREG), discovers publicly available company sources, extracts structured facts, verifies that the information belongs to the correct company, stores the evidence, and detects changes over time.

---

## 🚀 What Signalpost Does

Signalpost follows an evidence-first research pipeline:

```text
Norwegian Organization Number
            │
            ▼
       BRREG Registry
            │
            ▼
     Company Identity
            │
            ▼
      Registry Facts
            │
            ▼
     Source Discovery
            │
            ▼
      Source Fetching
            │
            ▼
      HTML Cleaning
            │
            ▼
     Fact Extraction
            │
            ▼
    Entity Verification
            │
            ▼
     Evidence Storage
            │
            ▼
     Change Detection
            │
            ▼
       Company UI

The core principle is:
Fact → Evidence → Source → Verification → Update
✨ Key Features
1. Official Company Resolution
Signalpost uses BRREG as the authoritative starting point for company identity.
Given a Norwegian organization number, the system can resolve information such as:
- Legal company name
- Organization number
- Company type
- Business address
- City
- Municipality
- Industry
- Industry code
- Website
2. Public Source Discovery
After resolving the company, Signalpost discovers relevant public sources.
Examples include:
- Company homepage
- About pages
- Company pages
- Investor pages
- News pages
- Contact pages
- Official BRREG registry records
Each discovered source is tracked with its URL and source type.
3. Evidence-First Fact Extraction
Signalpost extracts structured facts from publicly available company content.
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
4. Entity Verification
One of the biggest risks in company intelligence is assigning information from the wrong company.
Signalpost therefore verifies the identity of a source before accepting extracted facts.
The verification engine uses multiple identity signals:
- Organization number
- Company name
- Website domain
- Address
Verification results are classified as:
VERIFIED
REVIEW
REJECTED

A conflicting organization number causes the source to be rejected.
Matching organization numbers provide the strongest identity signal.
This helps prevent incorrect information from being associated with the wrong company.
5. Change Detection
Signalpost stores company facts as historical records rather than simply overwriting previous information.
New research can therefore be compared against earlier research.
Detected changes include:
ADDED
MODIFIED
REMOVED

Example:
Employee Count

Previous: 24,000
Current: 25,000

Change Type: MODIFIED

Pending or uncertain facts are not automatically treated as confirmed changes.
📊 1,000+ Company Coverage
Signalpost includes a bulk bootstrap pipeline for creating a large company profile base from BRREG.
A validated run successfully processed:
Companies processed : 1000
Successful          : 1000
Failed              : 0

This demonstrates that the system can populate a 1,000-company profile base without requiring a separate paid data provider.
🧠 Architecture
                    ┌──────────────────────┐
                    │ Norwegian Org Number │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    BRREG Client      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Company Repository   │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
       ┌────────────────┐           ┌────────────────┐
       │ Registry Facts │           │Source Discovery│
       └───────┬────────┘           └───────┬────────┘
               │                            │
               │                            ▼
               │                   ┌────────────────┐
               │                   │ Source Fetcher │
               │                   └───────┬────────┘
               │                           │
               │                           ▼
               │                   ┌────────────────┐
               │                   │  HTML Cleaner  │
               │                   └───────┬────────┘
               │                           │
               │                           ▼
               │                   ┌────────────────┐
               │                   │ Fact Extractor │
               │                   └───────┬────────┘
               │                           │
               └────────────┬──────────────┘
                            ▼
                  ┌─────────────────────┐
                  │ Entity Verification │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Evidence Ingestion  │
                  └──────────┬──────────┘
                             │
                             ▼
                     ┌──────────────┐
                     │   SQLite DB  │
                     └──────┬───────┘
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
        ┌────────────────┐    ┌──────────────────┐
        │ Change Detector│    │    FastAPI API   │
        └────────────────┘    └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ Signalpost UI    │
                              └──────────────────┘

🛠️ Technology Stack
Backend
- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite
- Requests
- BeautifulSoup
Frontend
- HTML
- CSS
- Vanilla JavaScript
Data Sources
- Norwegian Register of Business Enterprises (BRREG)
- Publicly accessible company websites and sources
Testing
- Pytest
The core system does not require a paid LLM API.
📁 Project Structure
signalpost/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── changes.py
│   │   │   ├── companies.py
│   │   │   └── intelligence.py
│   │   │
│   │   ├── database/
│   │   ├── models/
│   │   ├── scrapers/
│   │   ├── services/
│   │   └── verification/
│   │
│   └── tests/
│
├── data/
│   └── company_numbers.txt
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
│
├── scripts/
│   ├── bootstrap_1000.py
│   └── bulk_research.py
│
├── requirements.txt
├── .gitignore
└── README.md

⚙️ Installation
1. Clone the repository
git clone https://github.com/065060-Awantika/Signalpost.git
cd Signalpost

2. Create a virtual environment
python -m venv .venv

Activate it on Windows:
.venv\Scripts\Activate.ps1

3. Install dependencies
python -m pip install -r requirements.txt

▶️ Running the Backend
Start the FastAPI server:
python -m uvicorn backend.app.main:app --reload

The API will be available at:
http://127.0.0.1:8000

FastAPI interactive documentation:
http://127.0.0.1:8000/docs

🖥️ Running the Frontend
In a second terminal, from the project root:
python -m http.server 5500 --directory frontend

Open:
http://127.0.0.1:5500

The frontend allows a user to enter a Norwegian organization number and view the resulting company intelligence profile.
🔎 Example Research
Example organization number:
923609016

This resolves to:
EQUINOR ASA

A research request can be made through:
POST /companies/{organization_number}/research

Example:
POST /companies/923609016/research

Company facts can be accessed through:
GET /companies/923609016/facts

Change information can be accessed through:
GET /companies/923609016/changes

📦 Bulk Company Bootstrap
Signalpost includes a bootstrap script that retrieves company records from BRREG and stores them locally.
Run:
python -m scripts.bootstrap_1000

Validated result:
Companies processed : 1000
Successful          : 1000
Failed              : 0

The resulting profiles provide the initial large-scale company coverage required by the challenge.
🔄 Bulk Research
Organization numbers can be stored in:
data/company_numbers.txt

Use one organization number per line:
923609016
123456789
987654321

Run:
python scripts/bulk_research.py

The bulk research process records:
- Company identity
- Research success/failure
- Source results
- Extracted fact counts
- Research results
🔄 Change Detection
Signalpost supports historical comparison of company facts.
The change detection pipeline compares previous and current facts.
Previous Facts
      │
      ▼
Current Facts
      │
      ▼
Change Detector
      │
 ┌────┼────────┐
 ▼    ▼        ▼
ADD  MODIFY   REMOVE

Example:
Field: employee_count

Previous Value: 24,000
Current Value: 25,000

Change Type: modified

The system also ignores pending facts when determining confirmed changes.
🧪 Testing
Run the complete backend test suite:
python -m pytest backend/tests -q

Latest validated result:
87 passed
1 warning
0 failed

The warning is a Starlette/httpx test-client deprecation warning and does not represent a failing test.
💰 Cost
Signalpost was designed to operate without paid AI APIs.
The core pipeline uses:
- BRREG public data
- Public web pages
- Deterministic extraction
- Rule-based entity verification
- Local SQLite storage
- Open-source Python libraries
No paid API key is required for the core implementation.
The system therefore avoids dependency on:
- OpenAI API
- Anthropic API
- Google Gemini API
- Paid search APIs
This keeps the prototype within the challenge's external API cost constraints.
🔐 Evidence and Verification Philosophy
Signalpost follows three principles.
1. Identity Before Intelligence
Before accepting information from a source, Signalpost determines which company the source belongs to.
2. Evidence Before Claims
Facts are stored together with the evidence text from which they were extracted.
3. Preserve Uncertainty
Not every extracted fact is automatically considered confirmed.
The system distinguishes between:
VERIFIED
REVIEW
PENDING
REJECTED

This allows uncertain information to remain visible without presenting it as confirmed intelligence.
📈 Confidence
Extracted facts contain confidence scores.
Examples:
Organization Number    98%+
Legal Name             90%+
Website                95%+
Employee Count         90%
Industry               85%
Address                85%

Official BRREG facts receive stronger verification treatment because BRREG is the authoritative registry source used for company identity.
🌐 Source Evidence
Every persisted fact can be associated with a source.
A source record can contain:
- URL
- Source type
- Publisher
- Retrieved timestamp
- Content hash
- Raw retrieved content
This creates a traceable relationship:
Company
   │
   ▼
Fact
   │
   ▼
Evidence
   │
   ▼
Source URL

This makes the system explainable and auditable.
🎯 Challenge Alignment
Evaluation Area	Signalpost Implementation
Coverage	1,000-company BRREG bootstrap
Correct company matching	Multi-signal entity verification
Evidence	Fact-level evidence and source storage
Updates	Historical facts and change detection
Explanations	Evidence text and confidence scores
Usability	FastAPI backend and web dashboard
Cost efficiency	No paid LLM API required


🚀 Future Improvements
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
🏆 Project Highlights
Signalpost demonstrates an end-to-end company intelligence workflow:
INPUT
  │
  ▼
Organization Number
  │
  ▼
IDENTITY
  │
  ▼
BRREG Verification
  │
  ▼
DISCOVERY
  │
  ▼
Public Sources
  │
  ▼
EXTRACTION
  │
  ▼
Structured Facts
  │
  ▼
VERIFICATION
  │
  ▼
Evidence-backed Facts
  │
  ▼
STORAGE
  │
  ▼
Historical Records
  │
  ▼
UPDATES
  │
  ▼
Change Detection

The system is designed around one core idea:
Don't just find company information. Prove where it came from, verify that it belongs to the right company, and detect when it changes.

👥 Project
Signalpost
Company Intelligence & Evidence Research System
Repository:
https://github.com/065060-Awantika/Signalpost
Built as a proof-of-concept for the Builderr.ai company information agent challenge.
