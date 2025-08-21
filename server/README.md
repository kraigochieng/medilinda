# ADR Causality Assessment Classification Model

## Goal
Create a classification model that takes **ADR reports** and assigns them a **level of causality assessment**.

---

## Input Features
- The **yellow ADR reporting form** from PPB

---

## Challenges
- Accessing real ADR reports that:
  - Focus on **first-line antitubercular drugs**
  - Already have **assigned causality levels**
- Dataset size:
  - Even a small portion of real data would help
  - **Synthetic data** can be used to increase dataset size

---

## Other Features (Future Work)
- Notifications for **incomplete or low-detail reports**

---

## Key Stakeholders
- **Christine**
  - Data Access
  - Engaging PPB
  - Clear thinking

- **Terry**
- **Ken**

---

## Health Use Case
- **Health Benefit:** Patient safety
  - Why?  
    - Directly linked to **pharmacovigilance (Pv)**  
    - Prevents harm by assessing causality of ADRs  
    - Supports **digital health** solutions enhanced with AI  

- **Big Health Impact Pathway:**  
  `Patient Safety → Pharmacovigilance → Digital Health → AI Solution`

---

## Research Approach
- **Implementation Science** (applied research)  
- Write with the mindset of preparing a **scientific paper**:
  - Clearly state the problem
  - Link to public health impact
  - Show how technology (AI/ML) comes in
  - **Cite properly**
- Compare **synthetic vs. real data** use
- Reduce ambition → define **timelines** and **scopes**

---

## Guidance & Encouragement
- Focus on **where the greatest problems lie**  
- Ensure a **clear connection** between:
  - The **problem**
  - The **solution at scale**

---

## Reading Points
- **Surveillance**:
  - Detecting outbreaks
  - Responding quickly
  - Containment  
- **Public health**  
- **Pharmacovigilance graphs** → Do not reinvent the wheel

---

## Online Courses
- **Fundamentals of Disease Surveillance**

---

## Career PDP Update
- Define **specific career goal**
- Clarify **area of AI application**
- Possible direction: **Surveillance AI for health science**

---

## MLflow Commands
```bash
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns \
  --host 0.0.0.0 \
  --port 8081
