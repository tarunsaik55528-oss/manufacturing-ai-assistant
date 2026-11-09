# AGENTS.md
## Developer & AI Agent Guidelines for Round 2

This document defines core architectural invariants, conventions, and constraints for any AI agent or software engineer maintaining or extending this codebase.

---

### 1. Invariants & Non-Negotiable Rules

1. **Frozen AI Model**:
   - The classifier model (`ai_model/classifier.npz`), weights, inference pipeline (`ai_model/inference.py`), and decision threshold (`0.5`) are FROZEN.
   - Do NOT retrain, modify weights, alter features, or recalibrate the classification threshold.
   - All inference must pass through the service layer `ai_model/service.py`.

2. **Role-Based Access Control (RBAC)**:
   - Three authoritative roles: `Administrator`, `Engineer`, `Supervisor`.
   - Permissions are enforced on views and serializers via DRF permission classes (`IsAdministrator`, `IsEngineer`, `IsSupervisor`).
   - UI button visibility is never considered an access control mechanism.
   - Unauthenticated access returns HTTP 401; unauthorized role returns HTTP 403; access to another engineer's resource returns HTTP 404 (prevents enumeration).

3. **Data Integrity & Immutability**:
   - Reviews are strictly additive / snapshot-based. A supervisor review NEVER mutates `Inspection.predicted_class`.
   - A single inspection can have at most ONE review; a duplicate review attempt must return HTTP 409 Conflict.
   - Unsafe, undecodable, or rejected files are NEVER persisted to disk; their inspection record is created with status `FAILED` and `uploaded_image = None`.

4. **Batch Processing Fault Isolation**:
   - In batch uploads (1–10 files), failures in one file (e.g. corrupt bytes or invalid dimensions) MUST NOT fail or cancel other valid files in the same batch.
   - Tasks are dispatched asynchronously using `transaction.on_commit`.

---

### 2. Testing Policy
- Every new endpoint, serializer, or model modification MUST have automated unit and integration tests.
- Always run the full test suite before committing:
  ```bash
  python manage.py test tests
  ```
- All tests must pass with 0 failures and 0 errors.

---

### 3. Management Commands
- `python manage.py seed_round2_roles`: Idempotently seeds Administrator, Engineer, and Supervisor groups and default test users.
- `python manage.py seed_products`: Idempotently seeds `P-PLATE01` from `round2_pack/product_details.csv`.
- `python manage.py evaluate_model`: Evaluates all 60 benchmark images and generates `evaluation_results.csv` and `MODEL_EVALUATION.md`.

