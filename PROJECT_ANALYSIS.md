# PROJECT ANALYSIS
## Round 2 – AI Visual Quality Inspection System (Python Full Stack)

### (A) Organization's Problem
A manufacturing organization producing precision metal plates (`P-PLATE01`) requires automated screening of manufactured parts for visible surface defects (scratches, pits, and cracks) to improve throughput, reduce human visual fatigue, and ensure consistent quality standards. The solution must run on-premises with predictable CPU inference, provide real-time results for individual items, support asynchronous batch processing for multi-part trays, and allow supervisors to audit, verify, and correct model predictions while keeping complete audit integrity.

### (B) What the Application Must Solve
1. **Automated Defect Screening**: Seamless integration of a frozen binary classifier (`BIT-PLATE-CV-1.0`) capable of predicting `Normal` (Class 0) or `Defective` (Class 1) with an associated confidence score and defect probability.
2. **Strict File Validation**: Server-side validation of incoming images (size, dimensions, MIME, actual decoded byte structure, decompression bomb prevention) before any model execution.
3. **Dual Processing Flows**:
   - Single-image synchronous (or immediate) inspection flow for on-demand bench testing.
   - Asynchronous batch processing (1–10 images) utilizing Celery and Redis with robust item-level isolation (one corrupted image must never halt or fail valid items).
4. **Role-Based Access Control**: Clean separation of responsibilities across Administrators, Quality Engineers, and Quality Supervisors.
5. **Supervisor Verification & Auditability**: Dedicated review workflows allowing supervisors to confirm or correct AI predictions without mutating the original AI prediction record.
6. **Persistence & Resilience**: Full relational database persistence in PostgreSQL, resilient across application and worker restarts.

### (C) Users and Permissions
The application defines three strict user roles:
1. **Administrator**:
   - Manages product catalogue (`product_id`, `product_name`, `description`).
   - Manages user accounts and accesses Django admin.
   - Read-only visibility over all inspections and reviews across the organization.
   - Prohibited from submitting inspections or conducting supervisor reviews.
2. **Quality Engineer**:
   - Submits single and batch inspections for supported products.
   - Views their own inspection history and individual inspection results.
   - Prohibited from reviewing inspections (API access returns HTTP 403 Forbidden).
   - Prohibited from viewing or accessing inspections submitted by other engineers (returns HTTP 404 to prevent ID enumeration).
3. **Quality Supervisor**:
   - Views all inspections across all engineers.
   - Reviews completed inspections: confirms predictions or corrects them (`Normal` <-> `Defective`) with optional explanatory comments.
   - Prohibited from submitting new inspections or modifying product metadata.

### (D) Engineer Workflow
1. Log in via session-based web login or REST API (`POST /api/auth/login/`).
2. Navigate to Inspection Dashboard.
3. Select supported product (`P-PLATE01`).
4. Upload single image or batch of 1–10 images (JPEG/PNG, 64x64 to 4096x4096, <= 5 MiB).
5. For single upload: immediate validation and inference; receive Inspection ID, predicted class, confidence %, defect probability, model version, and submission timestamp.
6. For batch upload: receive immediate HTTP 202 Accepted with batch ID and queued item IDs; poll batch status until background workers complete inference.
7. Filter and search personal inspection history.

### (E) Supervisor Workflow
1. Log in and access Supervisor Review Portal.
2. Filter inspections by status (`Pending review`, `Completed`, `Normal`, `Defective`), date range, or engineer.
3. Open a pending inspection: review uploaded plate image, AI predicted class, confidence %, model version, submitting engineer, and timestamp.
4. Execute review action: "Confirm", "Correct to Normal", or "Correct to Defective", with optional supervisor comments.
5. Review record is saved atomically in a OneToOne relation with row locking (`select_for_update`).
6. Original model output remains immutable. Inspection record now reflects `is_reviewed=True`.

### (F) Model Integration
- **Model Version**: `BIT-PLATE-CV-1.0`.
- **Target Product**: `P-PLATE01` (Demonstration metal plate).
- **Architecture**: 17 standardized hand-crafted image features + logistic regression with sigmoid activation. Decision threshold = 0.5.
- **Packaging**: Frozen weights in `classifier.npz` (`mean`, `scale`, `coef`, `intercept`).
- **Wrapper Architecture**: Service wrapper in `ai_model/service.py` wrapping `Model/inference.py` without modifying original inference logic. Handles dynamic model path resolution, input sanitization, and structured return format.

### (G) Image Validation
- **Formats Allowed**: JPEG and PNG only. Reject WebP, GIF, BMP, TIFF, SVG, etc.
- **Content Inspection**: Pillow `Image.open().verify()` followed by full `Image.open().load()` to catch truncated or corrupted files regardless of file extension.
- **Size Boundary**: Exactly 5 MiB ($5 \times 1024 \times 1024 = 5,242,880$ bytes) is accepted; 5,242,881 bytes is rejected with HTTP 400/413.
- **Dimensions**: Min 64x64, max 4096x4096 inclusive.
- **Safety**: Decompression bomb limits enforced; storage uses generated UUIDs to eliminate path traversal risks; static media separation.

### (H) Batch Processing
- **Stack**: Celery + Redis broker and result backend.
- **Batch Constraints**: 1 to 10 files per request. Empty batch or >10 files rejected immediately.
- **Atomic Queueing**: Inspections created in DB first (valid files as `QUEUED`, invalid as `FAILED`), and Celery tasks dispatched via `transaction.on_commit()`.
- **Worker Execution**: Worker atomically transitions `QUEUED` -> `PROCESSING` -> `COMPLETED` (or `FAILED` with error message). Stuck tasks recovered if worker restarts.

### (I) Persistence
- PostgreSQL database stores `Product`, `Batch`, `Inspection`, and `Review`.
- Enforces relational constraints: ForeignKeys, unique indexes, CHECK constraints on probabilities ($[0, 1]$), status state machine constraints.
- Full auditability across restarts.

### (J) Security
- Environment variable configuration (`.env`).
- CSRF protection enabled on web sessions.
- Secure media serving: Uploaded images served via protected Django view verifying user ownership or supervisor/admin role; no direct directory browsing.
- Sanitized error messages with no stack traces or server paths exposed to clients.

### (K) Testing Strategy
- Unit and integration tests covering:
  - Image validation edge cases (boundaries, corrupt, non-image, unsupported MIME).
  - RBAC enforcement across all endpoints (Admin, Engineer, Supervisor, Anonymous).
  - Model inference consistency and wrapper accuracy.
  - Celery task execution, commit hooks, and failure isolation.
  - Supervisor review immutability and duplicate conflict handling.

### (L) Evaluation and Submission Requirements
- Comprehensive model evaluation across all 60 sample images in `Samples/images/` compared against `Samples/labels.csv`.
- Metrics: Confusion matrix (2x2), TN, FP, FN, TP, Accuracy, Precision, Recall, F1 score.
- Output artifacts: `evaluation_results.csv` and `MODEL_EVALUATION.md`.

### (M) Model Limitations
1. Trained on synthetic procedural images; not representative of varied lighting, lens distortion, or real factory debris.
2. Strict fixed framing requirement: plate must be centered with surrounding border cropped at coordinates [16:112, 16:112]. Rotated or unaligned parts will produce erroneous predictions.
3. Binary classification only: cannot locate defect bounding boxes, classify defect types (scratch vs pit), or evaluate defect depth/severity.
4. Uncalibrated confidence scores: probabilities reflect logistic regression outputs, not calibrated physical failure probabilities.

### (N) Conflicts & Ambiguities Resolved
1. **Challenge Brief Checksum**: `Round2_Student_Challenge_Brief.pdf` and `.docx` had SHA256 hashes differing from `SHA256SUMS.txt`, while all 72 model, image, and data files matched 100%. The PDF was inspected and verified as the authentic Version 1.0 challenge brief.
2. **Database Engine**: PDF allows PostgreSQL or MySQL; prompt mandates PostgreSQL. App uses PostgreSQL as primary engine with graceful fallback for testing.
3. **Admin Upload Policy**: Master prompt left Admin upload as a policy decision. Decision: Admin is restricted to product and user management; only Engineers upload images.
4. **Engineer Unauthorized Inspection Access**: Returns HTTP 404 Not Found to prevent leaking existence of other engineers' inspections.

