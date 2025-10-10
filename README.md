# MediLinda

MediLinda is an integrated platform for Adverse Drug Reaction (ADR) reporting, monitoring, and explainable AI-driven causality assessment. It streamlines pharmacovigilance workflows for healthcare professionals and regulatory bodies.

## Features

-   **ADR Reporting:** User-friendly forms for submitting ADR cases.
-   **Dashboard & Monitoring:** Visual analytics for ADR trends, seriousness, and outcomes.
-   **Explainable AI:** Machine learning model predicts causality assessment levels with SHAP-based explanations.
-   **Communication Tools:** Automated SMS alerts and additional information requests.
-   **Role-based Access:** Secure authentication and authorization for users.

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
npm install
```

**Backend:**

```sh
cd ../server
uv pip install --system -r pyproject.toml
```

#### 4. Run the Application

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
