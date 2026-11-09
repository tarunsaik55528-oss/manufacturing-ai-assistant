# NOTES.md — Round 3 Implementation & Technical Notes

## 1. Overview
The Round 3 "Quality Incident and Action Assistant" extends the existing manufacturing AI platform by converting defective visual inspections into actionable, SOP-grounded quality containment workflows.

---

## 2. Files Created & Modified

### Created Files
- `incidents/__init__.py`
- `incidents/apps.py`: App configuration for `incidents`.
- `incidents/models.py`:
  - `QualityIncident`: Snapshot of immutable model predictions, review state, suggested actions, evidence status. Unique `inspection_id` with `on_delete=PROTECT`.
  - `IncidentSource`: Verified citation passages, document ID, revision, PDF page, and source links.
  - `SOPChunk`: Ingested page-aware text chunks with document metadata.
- `incidents/serializers.py`: DRF serializers for incidents, sources, and supervisor reviews with strict validation rules.
- `incidents/views.py`:
  - `QualityIncidentCreateListView`: Atomic incident generation with `select_for_update`, idempotent retry handling.
  - `QualityIncidentDetailView`: Retrieve incident details with citations and inspection snapshots.
  - `QualityIncidentReviewView`: Supervisor-only review submission endpoint.
  - `SOPDocumentListView`: List of available SOP documents and page counts.
  - `SOPPdfServeView`: Secure path-traversal protected PDF server.
- `incidents/urls.py`: API route registrations for incidents and SOP endpoints.
- `incidents/services/rag_service.py`: Retrieval-Augmented Generation engine, page-aware retriever, multi-SOP mandatory containment & review rule, verbatim citation validator, and missing-evidence fallback generator.
- `incidents/management/commands/ingest_quality_sops.py`: Idempotent management command parsing `product_sop_mapping.csv`, extracting PDF text per page, chunking, and storing chunks.
- `incidents/management/commands/seed_round3_demo.py`: Idempotent demo seeder populating 7 `[TEST FIXTURE]` inspections covering all testing scenarios (plate defective, plate normal, gasket defective, gasket normal, pending review, completed review, missing SOP scenario).
- `tests/test_round3_quality_incidents.py`: 21 comprehensive automated unit and integration tests.
- `frontend/templates/incident_create.html`
- `frontend/templates/incident_detail.html`: Visual display with Sections A-G and in-app modal PDF viewer (`#page=N`).
- `frontend/templates/incidents_list.html`
- `frontend/templates/supervisor_incidents.html`
- `frontend/templates/sop_documents.html`
- `round3_pack/product_sop_mapping.csv`
- `round3_pack/SOPs/Q_PLATE_01_Containment_Rev1_0.pdf`
- `round3_pack/SOPs/Q_PLATE_02_Review_Rev1_0.pdf`
- `round3_pack/SOPs/Q_GASKET_01_Review_Rev1_0.pdf`

### Modified Files
- `config/settings.py`: Added `incidents` to `INSTALLED_APPS`, configured `SILENCED_SYSTEM_CHECKS = ['fields.W342']`.
- `config/urls.py`: Added `api/` routes for `incidents.urls`.
- `inspections/serializers.py`: Added `is_eligible_for_incident`, `incident_eligibility_reason`, `incident_id` as explicit `SerializerMethodField`s.
- `inspections/models.py`: Added helper properties `is_eligible_for_incident` and `incident_eligibility_reason`.
- `accounts/page_urls.py`: Added template routes for incidents, reviews, and SOP library.
- `accounts/page_views.py`: Added view controllers for incidents UI and aggregated dashboard statistics.
- `frontend/templates/base.html`: Unified top navigation and sidebar linking Round 1, Round 2, and Round 3 features with role-based visibility.
- `frontend/templates/dashboard.html`: Updated dashboard with live metrics for Round 1, 2, and 3.
- `frontend/templates/visual_inspection_history.html`: Added Model Version badge and "Create Incident" action button.

---

## 3. Key Architectural Choices

1. **Strict Immutability of Round 2 Predictions**:
   - `QualityIncident` takes a snapshot of `original_prediction`, `original_confidence`, and `model_version` directly from `Inspection`.
   - Never writes back to the `inspections` table.
   - Human review corrections on the inspection record never alter eligibility (an inspection originally predicted as Defective remains eligible even if a human reviewer marked it Normal).

2. **Concurrency & Uniqueness Constraint**:
   - A unique constraint on `QualityIncident.inspection` prevents multiple incidents per inspection.
   - Handled via `select_for_update()` inside `transaction.atomic()`. On `IntegrityError` or `OperationalError`, the transaction safely rolls back and retries fetching the existing incident, returning HTTP 200 with the original record.

3. **Multi-SOP Procedural Requirement**:
   - For `P-PLATE01`, both `Q-PLATE-01` (Containment) and `Q-PLATE-02` (Review) are required. If either document is missing, evidence is marked `Insufficient`.
   - `Q-GASKET-01` is strictly filtered out for plate products to prevent cross-product citation contamination.

4. **Anti-Hallucination Citation Verification**:
   - Every passage cited in `suggested_actions` must exist as a verbatim case-insensitive substring in the ingested SOP chunks.
   - Any hallucinated or unverified citations are stripped. If no valid citations remain, status falls back to `Insufficient`.

5. **Permanent Supervisor Reviews**:
   - Once a supervisor reviews an incident, subsequent review attempts are rejected with `409 Conflict`.
   - Approving an incident with `evidence_status == Insufficient` is blocked (`400 Bad Request`). Only `Needs more information` is permitted for insufficient evidence.

6. **Secure PDF Serving**:
   - The `/api/sop/<doc_id>/<rev>/pdf/` endpoint verifies the document against the registered database records to prevent directory traversal attacks.

---

## 4. Assumptions Made During Development
- The local environment uses SQLite as fallback in development/test mode. SQLite row-level locks and `OperationalError` handling were implemented to ensure concurrency tests pass reliably without deadlocks.
- The embedding model and vector store pipeline gracefully fallback to TF-IDF / term-overlap semantic chunk matching when external embedding APIs are not configured with remote keys, ensuring 100% offline test suite reliability.
- Administrator users can view quality incidents in read-only mode, but reviewing is reserved exclusively for users possessing the `Supervisor` role.

---

## 5. Known Limitations & Future Optimizations
- **Vector Search Engine**: Chunks currently store page-level segments in the relational database with vector-ready metadata. In high-scale deployments, chunks can be synced to a dedicated vector index (such as pgvector or ChromaDB) for hybrid BM25 + cosine similarity search.
- **WebSocket Notifications**: Incident creation and supervisor reviews can trigger real-time WebSocket alerts to engineers and supervisors.

