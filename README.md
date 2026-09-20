# DataChat

### AI-Powered Conversational Data Analytics

DataChat is a full-stack AI-powered data analytics platform that allows users to upload datasets, ask questions in natural language, generate visualizations, discover statistical insights, run predictive models, and export analysis as a PDF report.

Instead of requiring users to write Python, SQL, or manually build charts, DataChat translates natural-language questions into structured analytical operations and executes them against the uploaded dataset.

> **Live Demo:** Deployed web application
> **Status:** Active / Deployed

---

## Overview

Traditional data analysis often requires users to understand spreadsheets, Python, pandas, statistical concepts, and visualization libraries before they can extract useful information from their data.

DataChat provides a conversational interface for this process.

A user can upload a CSV or Excel dataset and ask questions such as:

```text
Show the distribution of marks
```

```text
Compare average salary by department
```

```text
Show a scatter plot of attendance vs marks
```

```text
Show the correlation matrix
```

```text
Find outliers in salary
```

```text
Describe the age column in detail
```

```text
Predict marks using attendance and study hours
```

The system interprets the request, validates it against the dataset schema, executes the appropriate analysis, generates insights, and presents the result through an interactive interface.

---

## Key Features

### Natural-Language Data Analysis

Ask questions about an uploaded dataset using plain English.

DataChat converts the question into a structured analysis intent before executing it.

```text
User Question
      ↓
Intent Detection
      ↓
Schema Validation
      ↓
Analysis Execution
      ↓
Insight Generation
      ↓
Visualization / Result
```

---

### Dataset Profiling

When a dataset is uploaded, DataChat automatically analyzes its structure.

The profiling layer identifies:

* Column names
* Data types
* Unique values
* Missing values
* Sample values
* Numeric columns
* Categorical columns
* Dataset dimensions
* Data-quality characteristics

The generated schema is then supplied to the intent parser so that the AI works with the actual columns available in the dataset.

---

### Automatic Dataset Exploration

DataChat can automatically investigate a newly uploaded dataset.

The exploration pipeline can identify:

* Dataset statistics
* Column inventory
* Missing values
* Duplicate records
* Data-quality issues
* Important statistical patterns
* Recommended analyses
* Automatic visualizations
* Key findings

This allows the system to provide useful information even before the user asks a specific question.

---

## Supported Analysis Operations

| Operation          | Description                                |
| ------------------ | ------------------------------------------ |
| `summary`          | Dataset-level summary and statistics       |
| `histogram`        | Distribution analysis for numeric columns  |
| `groupby`          | Aggregation across categorical groups      |
| `correlation`      | Correlation matrix between numeric columns |
| `missing`          | Missing-value analysis                     |
| `trend`            | Legacy trend analysis                      |
| `timeseries`       | Time-based trends, growth and volatility   |
| `outliers`         | Outlier detection                          |
| `value_counts`     | Frequency analysis of categorical values   |
| `describe`         | Detailed descriptive statistics            |
| `duplicates`       | Duplicate-row detection                    |
| `invalid_values`   | Data-quality and invalid-value detection   |
| `dynamic_chart`    | Flexible visualization generation          |
| `predictive_model` | Regression and classification modeling     |

---

## Supported Visualizations

DataChat supports multiple visualization types through Plotly:

* Scatter plots
* Bar charts
* Line charts
* Box plots
* Pie charts
* Correlation heatmaps
* KDE / density plots
* Violin plots
* Stacked bar charts
* Area charts
* Histograms

Example natural-language requests:

```text
Show a scatter plot of attendance vs marks
```

```text
Show a violin plot of marks by class
```

```text
Show a stacked bar chart of class by gender
```

```text
Show an area chart of revenue over month
```

```text
Show a density plot of salary
```

The backend generates chart-ready data while the frontend is responsible for rendering the visualization.

---

## AI Intent Parsing

DataChat uses a Groq-hosted LLM through an OpenAI-compatible API to interpret natural-language questions.

The intent parser receives:

1. The user's question
2. The current dataset schema
3. Supported analysis operations
4. Supported visualization types

It then returns a strict JSON representation of the requested operation.

For example:

```json
{
  "operation": "dynamic_chart",
  "chart_type": "scatter",
  "x": "attendance",
  "y": "marks"
}
```

The system validates the returned intent before executing it.

This separation between **AI interpretation** and **deterministic analysis execution** prevents the LLM from directly manipulating the dataset.

---

## Analysis Architecture

The project separates language understanding from data computation.

```text
                         ┌─────────────────────┐
                         │      User Query     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Intent Parser     │
                         │      (Groq LLM)     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Schema Validation   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Analysis Executor   │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       Statistical             Visualization        ML / Predictive
        Analysis                  Engine               Analysis
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Insight Engine     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     Frontend        │
                         │  Charts + Results   │
                         └─────────────────────┘
```

---

## Predictive Modeling

DataChat also provides tabular predictive modeling.

Supported models include:

### Regression

* Linear Regression
* Random Forest Regressor

### Classification

* Logistic Regression
* Random Forest Classifier

The system automatically determines whether the target is more suitable for regression or classification based on the target column.

Example:

```text
Predict marks using attendance and study hours
```

The modeling pipeline includes:

* Feature selection
* Numeric preprocessing
* Missing-value imputation
* Categorical encoding
* Feature scaling
* Train/test splitting
* Model training
* Evaluation
* Feature importance
* Prediction confidence estimation

Example supported metrics include:

```text
Regression:
- MAE
- MSE
- RMSE
- R²

Classification:
- Accuracy
- Precision
- Recall
- F1 Score
```

---

## Insight Engine

DataChat does more than display raw statistical results.

The insight engine interprets analytical results and generates structured findings.

For example, a correlation analysis can identify:

```text
Strongest relationship:
attendance ↔ marks

Pearson r = 0.78
```

A distribution analysis can identify:

* Mean vs median differences
* Distribution skew
* Standard deviation
* Interquartile range
* Potential outliers
* Coefficient of variation

Group comparisons can identify:

* Highest-performing groups
* Lowest-performing groups
* Spread between groups
* Groups above the overall average

These insights are returned alongside the visualization.

---

## Conversational Context

DataChat maintains analytical context between questions.

For example:

```text
User:
Show a histogram of marks

DataChat:
[Histogram]

User:
Now compare this by class

DataChat:
[Grouped analysis]
```

The session-memory layer tracks information such as:

* Last operation
* Last chart type
* Previously used columns
* Last grouping column
* Last intent
* Last result
* Previous insights
* Active filters

This allows follow-up questions to reference previous analytical context.

---

## Data Filtering

The system supports natural-language filtering such as:

```text
Show students where marks > 80
```

```text
Focus on class A
```

```text
Show only high scorers
```

The filter parser converts these requests into dataframe operations before analysis.

---

## Time-Series Analysis

DataChat provides dedicated time-series analysis for temporal datasets.

The time-series engine calculates:

* Trend direction
* Rolling mean
* Period-over-period growth
* Total growth
* CAGR when applicable
* Volatility
* Coefficient of variation
* Peak value
* Trough value
* Date range
* Number of observations

Example:

```text
Show revenue growth over time
```

---

## PDF Report Generation

Users can generate a downloadable PDF report containing information derived from the dataset and recent analysis.

The reporting pipeline can include:

* Dataset summary
* Schema information
* Key findings
* Generated insights
* Recent analysis
* Visualizations
* Interpretations

Reports are generated using ReportLab.

---

## Large Dataset Handling

DataChat includes basic protection against excessive memory usage.

The backend currently supports:

* Maximum upload size: **50 MB**
* Maximum in-memory dataset size: **100,000 rows**

For datasets exceeding the configured row threshold, the system samples the dataset before analysis while preserving information about the original row count.

The frontend can indicate when sampling has occurred.

---

## Tech Stack

### Frontend

* Next.js 14
* React 18
* TypeScript
* Tailwind CSS
* Plotly.js
* react-plotly.js

### Backend

* Python
* FastAPI
* Uvicorn
* Pandas
* NumPy
* Scikit-learn

### AI

* Groq API
* OpenAI-compatible API interface
* LLM-based intent parsing
* LLM-assisted natural-language explanations

### Data & Reporting

* Pandas
* OpenPyXL
* xlrd
* ReportLab

### Deployment

* Vercel — Frontend
* Render — Backend

---

## Project Structure

```text
datachat/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   └── investigation_agent.py
│   │   │
│   │   ├── ai/
│   │   │   └── intent_parser.py
│   │   │
│   │   ├── analysis/
│   │   │   ├── analysis_executor.py
│   │   │   ├── auto_explorer.py
│   │   │   ├── correlation.py
│   │   │   ├── describe.py
│   │   │   ├── duplicates.py
│   │   │   ├── dynamic_chart.py
│   │   │   ├── explanation.py
│   │   │   ├── groupby.py
│   │   │   ├── health_auditor.py
│   │   │   ├── histogram.py
│   │   │   ├── insight_engine.py
│   │   │   ├── invalid_values.py
│   │   │   ├── missing.py
│   │   │   ├── outliers.py
│   │   │   ├── predictive_model.py
│   │   │   ├── summary.py
│   │   │   ├── timeseries.py
│   │   │   ├── trend.py
│   │   │   └── value_counts.py
│   │   │
│   │   ├── context/
│   │   │   └── session_memory.py
│   │   │
│   │   ├── reporting/
│   │   │   └── report_generator.py
│   │   │
│   │   ├── services/
│   │   │   └── profiling.py
│   │   │
│   │   ├── utils/
│   │   │   └── validator.py
│   │   │
│   │   └── main.py
│   │
│   ├── reports/
│   ├── requirements.txt
│   └── runtime.txt
│
├── frontend/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   │
│   ├── components/
│   │   └── ChartRenderer.tsx
│   │
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── tsconfig.json
│
└── README.md
```

---

# Getting Started

## Prerequisites

Make sure the following are installed:

* Python 3.10+
* Node.js 18+
* npm
* Git
* A Groq API key

---

## Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd datachat
```

---

# Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it.

### Windows

```powershell
.\venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file inside `backend/`.

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant

FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
```

> Never commit `.env` files or API keys to GitHub.

---

## Run the Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The backend will run on:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "Backend running"
}
```

---

# Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

The frontend will be available at:

```text
http://localhost:3000
```

---

# Usage

### 1. Upload a Dataset

Upload one of the supported formats:

```text
.csv
.xlsx
.xls
```

DataChat automatically profiles the dataset and generates an initial exploration.

### 2. Ask a Question

Use natural language:

```text
Show summary
```

```text
Show histogram of salary
```

```text
Compare average salary by department
```

```text
Show correlation matrix
```

```text
Find outliers in age
```

### 3. Explore the Result

DataChat returns:

* Analysis result
* Interactive visualization
* Statistical information
* Plain-English explanation
* Generated insights
* Recommended follow-up analyses

### 4. Generate a Report

After analysis, generate a PDF report containing the relevant findings and visualizations.

---

# API

The FastAPI backend exposes several core endpoints.

| Method   | Endpoint                | Purpose                              |
| -------- | ----------------------- | ------------------------------------ |
| `GET`    | `/health`               | Backend health check                 |
| `POST`   | `/upload`               | Upload and profile dataset           |
| `POST`   | `/query`                | Analyze natural-language question    |
| `POST`   | `/investigate`          | Run autonomous dataset investigation |
| `POST`   | `/generate-report`      | Generate PDF analysis report         |
| `DELETE` | `/session/{session_id}` | Release session data                 |

---

## Example Query Request

```http
POST /query
Content-Type: application/json
```

```json
{
  "question": "Show a scatter plot of attendance vs marks",
  "session_id": "your-session-id"
}
```

The backend returns the parsed intent, analytical result, explanation, and generated insights.

---

# Deployment

DataChat uses a split deployment architecture:

```text
                 ┌────────────────────┐
                 │      Vercel        │
                 │ Next.js Frontend   │
                 └─────────┬──────────┘
                           │
                           │ HTTPS API
                           ▼
                 ┌────────────────────┐
                 │      Render        │
                 │  FastAPI Backend   │
                 └─────────┬──────────┘
                           │
                  ┌────────┴─────────┐
                  │                  │
                  ▼                  ▼
             Groq API            Analysis
                                 Engine
```

### Frontend

Deployed using Vercel.

Required environment variable:

```env
NEXT_PUBLIC_API_URL=<BACKEND_URL>
```

### Backend

Deployed using Render.

Required environment variables:

```env
GROQ_API_KEY=<YOUR_KEY>
GROQ_MODEL=llama-3.1-8b-instant
FRONTEND_URL=<FRONTEND_URL>
CORS_ORIGINS=<FRONTEND_URL>
```

---

# Testing

The repository includes backend tests covering several parts of the system.

Examples include:

```text
test_complete.py
test_extended.py
test_health_auditor.py
test_predictive_model.py
test_unit.py
test_validation.py
```

Additional integration and feature-level tests are included for areas such as:

* Auto exploration
* Backend responses
* Follow-up memory
* Insight generation
* Scatter validation
* Module imports

Run the test suite with:

```bash
pytest
```

---

# Design Principles

DataChat follows several architectural principles.

### 1. AI interprets — deterministic code executes

The LLM is primarily responsible for understanding the user's request.

The actual statistical computation is performed by deterministic Python code.

```text
LLM
 ↓
Structured Intent
 ↓
Validation
 ↓
Deterministic Analysis
```

This makes the analytical pipeline easier to reason about and test.

### 2. Schema-aware analysis

The AI receives the actual dataset schema before interpreting a query.

This helps prevent requests from referring to columns that do not exist.

### 3. Modular analysis engine

Each analytical capability is separated into its own module.

This makes it easier to add new analytical operations without rewriting the entire backend.

### 4. Frontend/backend separation

The frontend focuses on:

* User interaction
* Dataset upload
* Conversation UI
* Visualization
* Report downloads

The backend handles:

* Data processing
* AI interpretation
* Analysis
* Session management
* Insight generation
* Report creation

---

# Current Limitations

DataChat is an actively developed project and has several limitations.

* Analysis operates on uploaded datasets rather than persistent databases.
* Session data is stored in server memory.
* Session state is temporary.
* Large datasets may be sampled to control memory usage.
* Predictive modeling is intended for tabular experimentation rather than production ML deployment.
* LLM-generated explanations depend on external API availability.
* The current intent parser supports a defined set of analytical operations rather than arbitrary Python/SQL execution.
* Future forecasting is intentionally outside the currently supported analysis pipeline.
* Authentication and multi-user persistent storage are not currently part of the core architecture.

---

# Roadmap

### Data Analysis

* [x] Dataset profiling
* [x] Missing-value analysis
* [x] Duplicate detection
* [x] Outlier detection
* [x] Descriptive statistics
* [x] Correlation analysis
* [x] Time-series analysis
* [x] Data-quality analysis

### Visualization

* [x] Histogram
* [x] Bar chart
* [x] Scatter plot
* [x] Line chart
* [x] Box plot
* [x] Pie chart
* [x] Heatmap
* [x] KDE
* [x] Violin plot
* [x] Stacked bar
* [x] Area chart

### AI

* [x] Natural-language query parsing
* [x] Schema-aware intent generation
* [x] Follow-up query resolution
* [x] AI explanations
* [x] Automated insights
* [x] Autonomous dataset investigation

### Machine Learning

* [x] Regression
* [x] Classification
* [x] Feature importance
* [x] Model evaluation

### Reporting

* [x] PDF report generation
* [x] Dataset summary
* [x] Findings
* [x] Insights
* [x] Visualization inclusion

### Future Development

* [ ] Persistent database-backed sessions
* [ ] Authentication and user accounts
* [ ] Multi-dataset workspaces
* [ ] Advanced statistical testing
* [ ] More ML models
* [ ] Improved autonomous analysis
* [ ] Database / SQL data sources
* [ ] Production-grade observability
* [ ] More advanced report customization

---

# Security Notes

Do not commit sensitive credentials.

The following files should remain local:

```text
.env
.env.local
```

API keys should be provided through environment variables.

The production deployment should also configure CORS to allow only trusted frontend origins.

---

# Contributing

Contributions are welcome.

A typical workflow is:

```bash
git checkout -b feature/your-feature
```

Make your changes, test them, and commit:

```bash
git add .
git commit -m "feat: add your feature"
```

Push the branch:

```bash
git push origin feature/your-feature
```

Then open a pull request.

---

# License

Add the project's chosen license here.

For example:

```text
MIT License
```

---

# Author

**Ayush Kottary**

Built as a full-stack AI/data analytics engineering project combining:

```text
Artificial Intelligence
        +
Data Science
        +
Machine Learning
        +
Data Visualization
        +
Full-Stack Development
```

---

## Project Status

**DataChat is deployed and actively developed.**

The current version focuses on conversational dataset analysis, automated insights, interactive visualizations, predictive modeling, and report generation.
