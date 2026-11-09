# IMPLEMENTATION PLAN
## Round 2 – AI Visual Quality Inspection System

### Phase Overview
- **Phase 0: Analysis & Specifications** (Done)
  - Verify challenge pack, checksums, Round 1 codebase inspection.
  - Create `PROJECT_ANALYSIS.md`, `REQUIREMENTS_CHECKLIST.md`, `SYSTEM_ARCHITECTURE.md`, `DATABASE_DESIGN.md`, `IMPLEMENTATION_PLAN.md`.
- **Phase 1: Architecture & Environment Configuration**
  - Verify PostgreSQL / DB settings, Celery + Redis configs, `.env` file structure.
- **Phase 2: Authentication & Roles** (Current Focus)
  - Django Groups and Role integration (`Administrator`, `Engineer`, `Supervisor`).
  - Endpoints: `POST /api/auth/login/`, `POST /api/auth/logout/`, `GET /api/auth/me/`.
  - Reusable DRF permissions (`IsAdministrator`, `IsEngineer`, `IsSupervisor`).
  - Seed command `seed_round2_roles` for development demo accounts.
  - Automated tests for all role restrictions and unauthenticated scenarios.
- **Phase 3: Models & Product Seed**
  - `Product`, `Batch`, `Inspection`, `Review` models.
  - Migration generation.
  - Idempotent management command `seed_products` from `product_details.csv`.
- **Phase 4: AI Model Integration & Integrity Verification**
  - Copy frozen model to `ai_model/`, verify SHA256 checksums in automated tests.
  - Implement wrapper `ai_model/service.py` to invoke `predict()`.
- **Phase 5: Single Upload & Server-side Validation**
  - Content, dimension, and size boundary validators.
  - Synchronous inspection endpoint `POST /api/inspections/upload/`.
  - Protected media serving view.
- **Phase 6: Celery / Redis Batch Processing**
  - Batch upload endpoint `POST /api/inspections/batch/` (1–10 items).
  - Celery task with transactional commit dispatch.
  - Status polling endpoints `GET /api/inspections/<id>/status/` and batch tracking.
- **Phase 7: Dashboard & Inspection History**
  - Responsive Bootstrap 5 UI: stat cards, data tables, search, filters.
- **Phase 8: Supervisor Review & Audit Trail**
  - Dedicated review view with row-level locks (`select_for_update`).
  - Immutability enforcement and duplicate conflict handling (HTTP 409).
- **Phase 9: Model Evaluation & Scoring**
  - Management command evaluating all 60 samples from `Samples/images/`.
  - Generation of `evaluation_results.csv` and `MODEL_EVALUATION.md`.
- **Phase 10: Automated Test Suite & Deploy Checks**
  - Comprehensive unit/integration tests (`ROUND2_TEST_REPORT.md`).
  - `python manage.py check --deploy`.
- **Phase 11: End-to-End System Integration**
  - Full walkthrough of all three roles.
- **Phase 12: Final Documentation & Submission Prep**
  - `README.md`, `AGENTS.md`, `ROUND2_DEMO_GUIDE.md`.

