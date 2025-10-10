## Server Overview

This server provides an API and backend infrastructure for the ADR Causality Assessment Classification Model. It handles data ingestion, model inference, and integration with pharmacovigilance workflows.

### Features

-   REST API for submitting ADR reports and retrieving causality assessments
-   Integration with MLflow for model tracking and management
-   Support for both real and synthetic ADR data
-   Logging and monitoring for auditability

### Requirements

-   Python 3.8+
-   MLflow
-   Flask or FastAPI (depending on implementation)
-   SQLite (default for MLflow backend)

### Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the MLflow server:

```bash
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns \
  --host 0.0.0.0 \
  --port 8081
```

3. Run the server:

```bash
python app.py
```

### API Endpoints

-   `POST /predict` — Submit an ADR report for causality assessment
-   `GET /health` — Health check endpoint

---

## Other

### Input Features

-   The **yellow ADR reporting form** from PPB

---

## Challenges

-   Accessing real ADR reports that:
    -   Focus on **first-line antitubercular drugs**
    -   Already have **assigned causality levels**
-   Dataset size:
    -   Even a small portion of real data would help
    -   **Synthetic data** can be used to increase dataset size

---

## Other Features (Future Work)

-   Notifications for **incomplete or low-detail reports**

---

## Key Stakeholders

-   **Christine**

    -   Data Access
    -   Engaging PPB
    -   Clear thinking

-   **Terry**
-   **Ken**

---

## Health Use Case

-   **Health Benefit:** Patient safety

    -   Why?
    -   Directly linked to **pharmacovigilance (Pv)**
    -   Prevents harm by assessing causality of ADRs
    -   Supports **digital health** solutions enhanced with AI

-   **Big Health Impact Pathway:**  
    `Patient Safety → Pharmacovigilance → Digital Health → AI Solution`

---

## Research Approach

-   **Implementation Science** (applied research)
-   Write with the mindset of preparing a **scientific paper**:
    -   Clearly state the problem
    -   Link to public health impact
    -   Show how technology (AI/ML) comes in
    -   **Cite properly**
-   Compare **synthetic vs. real data** use
-   Reduce ambition → define **timelines** and **scopes**

---

## Guidance & Encouragement

-   Focus on **where the greatest problems lie**
-   Ensure a **clear connection** between:
    -   The **problem**
    -   The **solution at scale**

---

## Reading Points

-   **Surveillance**:
    -   Detecting outbreaks
    -   Responding quickly
    -   Containment
-   **Public health**
-   **Pharmacovigilance graphs** → Do not reinvent the wheel

---

## Online Courses

-   **Fundamentals of Disease Surveillance**

---

## Career PDP Update

-   Define **specific career goal**
-   Clarify **area of AI application**
-   Possible direction: **Surveillance AI for health science**
