# MediLinda: AI-Powered Pharmacovigilance for Safer TB Treatment in Kenya

**MediLinda** is an integrated web platform that streamlines **Adverse Drug Reaction (ADR)** reporting, real-time monitoring, and **explainable AI-driven causality assessment** for Kenya’s Pharmacy and Poisons Board (PPB).

It directly addresses a **critical patient safety gap** in tuberculosis (TB) treatment:

> **First-line anti-TB drugs (Pyrazinamide, Ethambutol, Isoniazid, Rifampin)** are among the **most frequently reported for serious ADRs** in Kenya’s national pharmacovigilance database — yet manual causality assessment is **slow, subjective, and resource-constrained**.

## Demo screenshots

### Predicted Causality Assessment level

![Predicted Causality Assessment level](docs/images/predicted_causality_assessment_level.png)

-   As per WHO-UMC Causality Assessment Levels

### Class Rankings using SHAP

![Class Rankings using SHAP](docs/images/class_rankings.png)

| Term                  | Meaning                                                                        |
| --------------------- | ------------------------------------------------------------------------------ |
| **Base Value**        | Starting probability _before_ seeing patient data (from training set averages) |
| **SHAP Value**        | **How much this case's features _pushed_ each class up or down**               |
| **Final Probability** | Final confidence after applying evidence                                       |

### Feature Rankings per Causality Assessment Level using SHAP

![Feature Rankings using SHAP](docs/images/feature_rankings.png)

**Top 5 reasons it said "possible":**

1. **No rechallenge** → **+26%**
2. **Symptoms improved after stopping** → **+21%**
3. **Reaction soon after Pyrazinamide** → **+13%**
4. **Low patient weight** → **+13%**
5. **Rifampicin started during reaction** → **+12%**

-   Other fields not shown to keep screenshot small

## The Business Problem We're Solving

### The Pain Point

-   **ADRs contribute to ~5% of global hospital admissions** (WHO, 2020)
-   In Kenya, **TB drugs dominate ADR reports** (PPB, 2023), but:
    -   Causality assessment is **manual, time-consuming, and inconsistent**
    -   **Expert shortages** delay signal detection
    -   **Poor communication** between regulators and remote facilities
    -   **Limited transparency** in decision-making erodes trust

### The Impact

Delayed or inaccurate causality assessment →  
**Prolonged patient exposure to harmful drugs** →  
**Avoidable morbidity, mortality, and healthcare costs**

## How MediLinda Solves It

| Challenge                             | MediLinda Solution                                                                             |
| ------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **Slow & subjective causality**       | ML model predicts **WHO-UMC causality levels** (Certain → Unlikely) with **SHAP explanations** |
| **Expert overload**                   | AI assists — **not replaces** — PPB reviewers                                                  |
| **Poor visibility**                   | Real-time **interactive dashboards** for ADR trends, seriousness, outcomes                     |
| **Communication gaps in rural areas** | **Automated SMS alerts & follow-up requests** (80%+ mobile penetration in Kenya)               |
| **Low trust in AI**                   | **Explainable AI (XAI)** shows _why_ a prediction was made                                     |

> **Result**: Faster, consistent, transparent pharmacovigilance — **protecting TB patients nationwide**.

## Key Features

-   **ADR Reporting Portal**  
    User-friendly forms aligned with PPB’s PvERS workflow

-   **AI Causality Assistant**  
    Predicts causality + generates **SHAP explanation charts** for every case

-   **Monitoring Dashboard**  
    Visualize trends: drug-wise ADRs, seriousness, outcomes, reporting gaps

-   **SMS Communication Engine**  
    Auto-send alerts or request missing info from healthcare facilities

-   **Role-Based Access**  
    PPB Officers, Data Managers, Reviewers, Admins

## Data & Model Details

-   **Target**: WHO-UMC Causality Categories
-   **Dataset**: Synthetic ADR data modeled on PPB summary statistics (anonymized, realistic distributions)
-   **Model**: Gradient Boosting (handles class imbalance via imbalanced-learn)
-   **Explainability**: SHAP values per prediction — auditable by PPB experts
-   **Evaluation**: F1 > 0.78 on held-out synthetic test set (aligned with Kreimeyer et al., 2021)

## Built With Real-World Context

-   **Kenya PPB** – Official pharmacovigilance partner
-   **IntelliSOFT Consulting Ltd** – Health systems implementation
-   **University of Nairobi** – Academic research & evaluation

## Tech Stack

-   **Frontend:** Nuxt 3, TypeScript, Tailwind CSS, Nuxt UI
-   **Backend:** FastAPI, SQLAlchemy, Pydantic
-   **ML Pipeline:** scikit-learn, MLflow, SHAP, imbalanced-learn
-   **Database:** SQLite (dev), compatible with PostgreSQL
-   **Containerization:** Docker, docker-compose

## Getting Started

### Prerequisites

-   Node.js (v20+)
-   Python (3.11)
-   Docker & docker-compose (optional, for containerized setup)

### Setup

#### 1. Clone the repository

```sh
git clone https://github.com/yourusername/medilinda.git
cd medilinda
```

#### 2. Environment Variables

Copy `.env.example` to `.env` and fill in required values for both `client/` and `server/`.

#### 3. Install Dependencies

**Frontend:**

```sh
cd client
npm install --legacy-peer-deps
```

**Backend:**

```sh
cd ../server
uv pip install --system -r pyproject.toml
```

#### 4. Set up authentication

Authentication uses [Better Auth](https://www.better-auth.com), which runs inside the Nuxt app. FastAPI only verifies the tokens.

1. Set the auth variables from `.env.example` (`BETTER_AUTH_*`, `INTERNAL_API_SECRET`, `TURSO_*`).
   `INTERNAL_API_SECRET` (client) and `BETTER_AUTH_INTERNAL_SECRET` (server) must hold the same value.
2. Create the auth tables:
    ```sh
    cd client
    npx @better-auth/cli migrate --config server/utils/auth.ts
    ```
3. Optional: copy users from the old FastAPI database. This keeps user ids and passwords.
    ```sh
    node scripts/migrate-users.mjs --dry-run   # preview
    node scripts/migrate-users.mjs
    ```

**API keys for scripts.** Sign in, open the avatar menu, choose **API keys**, and create a key. Then call the API directly:

```sh
curl -H "x-api-key: <your key>" http://localhost:8000/api/v1/users/me
```

#### 5. App database (Turso, optional)

By default the server uses the SQLite file in `server/src/server/db/`. Hosts without a persistent disk (such as Render) lose that file on every restart. To keep data, store it in Turso:

```sh
turso db create medilinda-app --from-file server/src/server/db/db.sqlite   # one-time import
turso db show medilinda-app --url
turso db tokens create medilinda-app
```

Set `TURSO_APP_DATABASE_URL` and `TURSO_APP_AUTH_TOKEN` on the server. Leave them unset for local development and tests. This is a separate database from the auth one (`medilinda-auth`).

Every query is a network call, so keep the server and the database in nearby regions.

#### 6. Run the Application

**Development (separate terminals):**

-   Frontend:
    ```sh
    cd client
    npm run dev
    ```
-   Backend:
    ```sh
    cd server
    uvicorn src/server/main:app --reload
    ```

**Or with Docker Compose:**

```sh
docker-compose up --build
```

## Audit trail and history

Every change to an ADR, its causality assessments, reviews, SMS messages, medical institutions and telephones is written to an append-only `audit_log` table: who, when, which fields changed (old and new), and a full snapshot of the row. Only requests from a signed-in user are recorded.

-   Editing an ADR keeps every earlier version. If the edit changes anything the ML model reads, a **new** causality assessment is added. The old one stays with the reviews given on it, so the ADR shows as needing review again.
-   Deleting an ADR removes it and its assessments and reviews, and records a snapshot of each. It can be undone with `POST /api/v1/adrs/{id}/restore`.
-   History endpoints: `GET /api/v1/adrs/{id}/versions`, `GET /api/v1/adrs/{id}/versions/{n}`, `GET /api/v1/adrs/{id}/activity`, `GET /api/v1/audit-logs`.
-   Rows that existed before auditing was added get a baseline version 1 the first time they change.
-   Bulk updates and raw SQL on audited tables bypass the hooks, so use the ORM for writes.

## Usage

-   Access the frontend at [http://localhost:3000](http://localhost:3000)
-   API available at [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure

```
client/         # Nuxt 3 frontend
server/         # FastAPI backend
medilinda_ml/   # ML pipeline and model code
```

## Acknowledgements

-   Kenya Pharmacy and Poisons Board (PPB)
-   IntelliSOFT Consulting Ltd
-   University of Nairobi
