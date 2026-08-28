# AI SQL Data Analyst

An AI-powered Streamlit application that allows non-technical users to upload a CSV file and ask questions about their data using natural language.

The application uses **Google Gemini (`gemini-3.6-flash`)** to convert a user's question into a DuckDB-compatible SQL query. The generated query is validated and then executed against the uploaded data using **DuckDB**.

## Project Objective

The goal of this project is to make SQL-based data analysis accessible to users who do not know SQL.

Instead of manually writing SQL, a user can upload a CSV file and ask questions such as:

> What is the average price for each region?

The application automatically:

1. Reads the CSV file.
2. Detects the data types of its columns.
3. Creates an SQL schema context.
4. Sends the schema and the user's question to Gemini.
5. Generates a DuckDB SQL query.
6. Validates the generated query.
7. Executes the query using DuckDB.
8. Displays the generated SQL and the actual result.

---

## Application Workflow

```text
CSV Upload
    ↓
Pandas
    ↓
Data-Type Detection
    ↓
SQL Schema Context
    ↓
Natural-Language Question
    ↓
Google Gemini
    ↓
SQL Query Generation
    ↓
SQL Validation
    ↓
DuckDB
    ↓
Query Result
    ↓
Streamlit
```

---

## Key Features

### CSV Upload

Users can upload a CSV file directly through the Streamlit application.

### Data Preview and Inspection

The application processes the uploaded dataset using Pandas and provides information about the data before querying.

### Automatic Data-Type Detection

Column types are detected automatically and mapped to SQL-compatible types.

Examples:

```text
DATE
BIGINT
DOUBLE
BOOLEAN
VARCHAR
```

Date columns are handled separately so that they can be represented appropriately in the generated SQL schema.

### Automatic SQL Schema Generation

The application creates an LLM-friendly schema similar to:

```text
Table: uploaded_data

Columns:
- Date: DATE
- Size_mm: BIGINT
- Customer: VARCHAR
- Region: VARCHAR
- Weight_kg: BIGINT
- Price_INR: DOUBLE
```

This schema is provided to Gemini so the model knows which table and columns are available.

### Natural-Language SQL Generation

Users do not need to know SQL.

For example:

```text
Which region has the highest total price?
```

Gemini converts the question into a DuckDB SQL query.

### SQL Validation

Generated queries are checked before execution.

The application is designed around read-only analytical queries and accepts queries beginning with:

```text
SELECT
WITH
```

Operations such as the following are rejected:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
CREATE
TRUNCATE
REPLACE
```

### DuckDB Execution

The uploaded Pandas DataFrame is registered in DuckDB as:

```text
uploaded_data
```

Gemini's generated SQL is executed directly against that table.

### Result Display

The application displays:

- The generated SQL
- The SQL query result

directly in Streamlit.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Web application interface |
| Pandas | CSV loading and data processing |
| DuckDB | SQL query engine |
| Google Gemini | Natural language to SQL |
| python-dotenv | Local API-key configuration |
| Git | Version control |
| GitHub | Source-code hosting |

---

## Why DuckDB?

DuckDB is a good fit for this application because it can query data directly from Python without requiring a separate database server.

The current architecture is simple:

```text
CSV
 ↓
Pandas DataFrame
 ↓
DuckDB
 ↓
SQL Query
 ↓
Result
```

This makes the application easy to run locally and suitable for a lightweight analytics workflow.

---

## Why Gemini?

Google Gemini provides the natural-language understanding needed to translate questions from non-technical users into SQL.

The model receives:

- The detected SQL schema
- The user's natural-language question
- Instructions to generate one read-only DuckDB SQL query

The current application uses:

```text
gemini-3.6-flash
```

---

## Project Structure

The GitHub repository intentionally contains only the final application file as the main Python program.

```text
AI-SQL-Data-Analyst/
│
├── app5.py
├── requirements.txt
├── README.md
└── .gitignore
```

### `app5.py`

The main Streamlit application containing:

- CSV upload
- Data processing
- Data-type detection
- SQL schema generation
- Gemini integration
- Natural-language question handling
- SQL generation
- SQL validation
- DuckDB connection
- SQL execution
- Result display

### `requirements.txt`

Contains the Python packages required to run the application.

### `.gitignore`

Prevents local secrets, virtual environments, cache files, and other unnecessary files from being committed.

### `README.md`

Project documentation.

---

# Installation

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_FOLDER>
```

## 2. Create a Virtual Environment

On Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

# Gemini API Configuration

The application requires a Google Gemini API key.

## Local Development

Create a `.env` file in the project root:

```text
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

The application loads the key using `python-dotenv`.

**Never commit `.env` to GitHub.**

Your `.gitignore` should include:

```text
.env
.venv/
__pycache__/
*.pyc
```

---

# Run the Application Locally

Run:

```powershell
python -m streamlit run app5.py
```

Streamlit will start the application and provide a local URL in the terminal.

---

# How to Use the Application

## Step 1 — Upload a CSV

Upload a CSV file through the Streamlit interface.

The application reads the file using Pandas.

## Step 2 — Review the Dataset

The application displays the processed dataset and its information.

## Step 3 — Review the Detected SQL Schema

The application creates a schema for the uploaded data.

Example:

```text
Table: uploaded_data

Columns:
- Date: DATE
- Customer: VARCHAR
- Region: VARCHAR
- Price_INR: DOUBLE
```

## Step 4 — Ask a Question

Enter a question in normal language.

Example:

```text
What is the average price for each region?
```

## Step 5 — Gemini Generates SQL

Gemini receives the schema and question and generates SQL similar to:

```sql
SELECT
    Region,
    AVG(Price_INR) AS average_price
FROM uploaded_data
GROUP BY Region;
```

## Step 6 — SQL Validation

The generated SQL is checked to ensure it is intended to be a read-only analytical query.

## Step 7 — DuckDB Executes the Query

The validated SQL is executed against the uploaded dataset.

## Step 8 — Result

The result is displayed in the Streamlit application.

---

# Example Questions

The application can answer analytical questions such as:

```text
What is the average price for each region?
```

```text
Which customer has the highest total price?
```

```text
How many records are there for each region?
```

```text
Show all sales where the price is greater than 500000.
```

```text
What was the total price in April 2025?
```

The exact questions supported depend on the columns and data available in the uploaded CSV.

---

# Example End-to-End Query

### User

```text
Which customer has the highest total price?
```

### Gemini

```sql
SELECT
    Customer,
    SUM(Price_INR) AS total_price
FROM uploaded_data
GROUP BY Customer
ORDER BY total_price DESC
LIMIT 1;
```

### DuckDB

DuckDB executes the generated SQL against:

```text
uploaded_data
```

### Streamlit

The application displays the resulting record.

---

# Application Architecture

```text
                         USER
                           │
                           │ Upload CSV
                           ↓
                  ┌─────────────────┐
                  │    Streamlit    │
                  └────────┬────────┘
                           ↓
                     ┌───────────┐
                     │  Pandas   │
                     └─────┬─────┘
                           ↓
                 Data-Type Detection
                           ↓
                    SQL Schema
                           │
                           │
              ┌────────────┴────────────┐
              │                         │
              ↓                         ↓
       User Question              SQL Schema
              │                         │
              └────────────┬────────────┘
                           ↓
                    ┌─────────────┐
                    │   Gemini    │
                    │ NL → SQL    │
                    └──────┬──────┘
                           ↓
                    Generated SQL
                           ↓
                    SQL Validation
                           ↓
                    ┌─────────────┐
                    │   DuckDB    │
                    │ SQL Execute │
                    └──────┬──────┘
                           ↓
                     Query Result
                           ↓
                      Streamlit
```

---

# Security Considerations

This project is a portfolio/MVP application and is not intended to be a production enterprise data platform.

### API Key Protection

Never place API keys directly in `app5.py`.

Use:

```text
.env
```

for local development and Streamlit Secrets when deploying.

### SQL Validation

The generated SQL is validated before execution and the application is designed for read-only analytical queries.

However, simple keyword-based validation is **not a complete enterprise-grade SQL security system**.

A production implementation should use stronger SQL parsing, query allowlisting, database permissions, authentication, logging, and other security controls.

### Data Privacy

Do not upload or commit confidential, sensitive, or unauthorized customer data to the repository.

Use synthetic or authorized datasets for demonstrations.

---

# Streamlit Cloud Deployment

The application can be deployed using Streamlit Community Cloud.

## Repository

Push the following files to GitHub:

```text
app5.py
requirements.txt
README.md
.gitignore
```

## Main File

When configuring the Streamlit application, select:

```text
app5.py
```

## Streamlit Secrets

Instead of `.env`, configure the Gemini API key in Streamlit Secrets:

```toml
GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"
```

The application first attempts to read:

```python
st.secrets["GOOGLE_API_KEY"]
```

and falls back to the local environment variable when running locally.

**Never publish the real API key in GitHub.**

---

# Current Project Status

## Completed

- [x] Streamlit application
- [x] CSV upload
- [x] CSV reading
- [x] Data preview
- [x] Dataset inspection
- [x] Automatic data-type detection
- [x] Date detection and SQL type mapping
- [x] SQL schema generation
- [x] Gemini API integration
- [x] Natural-language question input
- [x] Natural language → SQL generation
- [x] SQL validation
- [x] DuckDB integration
- [x] Generated SQL execution
- [x] Query result display

The core MVP workflow is complete:

```text
Upload → Ask → Generate SQL → Validate → Execute → Result
```

---

# Development Phases

### Phase 1 — CSV and SQL Foundation

Built the initial Streamlit application, CSV upload workflow, Pandas processing, and basic DuckDB SQL execution.

### Phase 2 — Data Inspection

Added dataset preview and inspection capabilities.

### Phase 3 — Schema Detection

Added automatic data-type detection, date handling, SQL type mapping, and LLM schema context generation.

### Phase 4 — AI SQL Engine

Integrated Google Gemini to convert natural-language questions into SQL and connected the generated SQL to DuckDB for execution.

---

# Current Limitations

The current version is an MVP.

Some possible limitations include:

- Very large CSV files may require additional optimization.
- Gemini-generated SQL depends on the quality of the user's question and detected schema.
- Simple SQL validation is not a replacement for production-grade SQL security.
- The current application is focused on CSV datasets.
- Persistent cloud storage is not included.
- User authentication is not included.
- Query history is not included.
- Automatic visualization is not included.

---

# Future Improvements

Possible future improvements include:

- Conversational follow-up questions
- Query history
- Automatic charts and visualizations
- KPI dashboards
- Better SQL parsing and validation
- Better handling of ambiguous questions
- Excel file support
- Larger dataset handling
- Multiple dataset support
- Cloud storage
- User authentication
- Role-based access control
- Query caching
- Data-quality checks
- Export results to CSV/Excel
- Production-grade logging and monitoring

---

# Learning Outcomes

This project demonstrates practical experience with:

- Python
- Streamlit
- Pandas
- SQL
- DuckDB
- Data-type detection
- Date handling
- Generative AI
- Google Gemini API
- Prompt engineering
- Natural language to SQL
- SQL validation
- API integration
- Environment variables
- Secrets management
- Git
- GitHub
- Cloud deployment concepts
- Data analytics

---

# Project Purpose

The central idea of this project is to make SQL-based data analysis accessible to non-technical users.

Instead of:

```text
Learn SQL
    ↓
Write SQL
    ↓
Execute SQL
    ↓
Interpret Result
```

the user experience becomes:

```text
Upload CSV
    ↓
Ask a Question
    ↓
AI Generates SQL
    ↓
DuckDB Executes SQL
    ↓
Get Result
```

This demonstrates how **Generative AI + Python + SQL + DuckDB + Streamlit** can be combined to create a practical AI-assisted analytics application.

---

# License

This project is intended primarily for educational and portfolio purposes.

If you publish the repository for open-source reuse, add an appropriate license such as MIT after reviewing its terms.
