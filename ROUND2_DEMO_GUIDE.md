# ROUND 2 SYSTEM DEMONSTRATION GUIDE
## AI Visual Quality Inspection System (Python Full Stack)

This guide provides an end-to-end presentation walkthrough for evaluating the AI Visual Quality Inspection system.

---

### Prerequisites for Live Demo
1. Django server running at `http://127.0.0.1:8000/`.
2. Seed data loaded via `python manage.py seed_round2_roles` and `python manage.py seed_products`.

---

### Step 1: Login & Role-Based Navigation
1. Open [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/).
2. Log in with the **Engineer** account:
   - **Username**: `engineer`
   - **Password**: `EngineerDemo2026!`
3. **Verification**: Notice automatic redirect to `/inspections/` (Visual Inspection Station). The top navigation displays `Visual Inspection` and `Inspection History`, while `Supervisor Reviews` and `Admin` are hidden.

---

### Step 2: Single Image Synchronous Inspection
1. On `/inspections/`, ensure **Product** is set to `P-PLATE01 - Demonstration metal plate`.
2. In the **Single Image Inspection** card, click **Choose File** and select a sample image:
   - Path: `round2_pack/Samples/images/inspection_001.png`
3. Click **Inspect Plate**.
4. **Verification**:
   - The result panel immediately updates without page reload.
   - Status badge shows `COMPLETED`.
   - Classification displays `Defective` with **100.00%** confidence.
   - The annotated preview card reflects the inspection attributes and model version `BIT-PLATE-CV-1.0`.

---

### Step 3: Server-Side Validation Rejection (Safe Failure)
1. In the same **Single Image Inspection** card, click **Choose File** and select an invalid sample:
   - Path: `round2_pack/Validation/corrupt.jpg` (or `too_small.png` / `not_an_image.txt`).
2. Click **Inspect Plate**.
3. **Verification**:
   - The application does NOT crash or raise 500 error.
   - A descriptive red alert appears indicating the exact validation error (e.g., corrupted image bytes or dimension bounds violation).
   - An audit record is created with status `FAILED` and prediction fields set to `NULL`.

---

### Step 4: Batch Asynchronous Upload (Fault Isolation)
1. Scroll down to the **Batch Upload & Processing** card.
2. Click **Choose Files** and select multiple images at once (e.g., 3 files):
   - `round2_pack/Samples/images/inspection_002.jpg` (Valid - Normal)
   - `round2_pack/Samples/images/inspection_003.png` (Valid - Defective)
   - `round2_pack/Validation/oversized.png` (Invalid - Exceeds 5 MiB)
3. Click **Upload & Process Batch**.
4. **Verification**:
   - An immediate `HTTP 202 Accepted` confirmation appears with the generated `Batch ID`.
   - A live progress card polls `GET /api/inspections/batch/<batch_id>/`.
   - **Fault Isolation**: The valid images are queued and completed cleanly; the invalid image fails independently without aborting the batch.

---

### Step 5: Inspection History & Data Filtering
1. Click **Inspection History** in the navigation bar (or visit `/inspections/history/`).
2. **Verification**:
   - Real-time KPI summary widgets display: Total Inspections, Defect Count, Defect Rate, and Pending Review count.
   - Filter by **Status** (`COMPLETED`, `FAILED`), **AI Result** (`Defective`, `Normal`), or **Review State** (`Pending Review`, `Reviewed`).
   - Use the **Search** bar to filter by filename.
   - **Data Isolation**: Engineer `engineer` only sees their own inspection records.

---

### Step 6: Supervisor Review & Immutable Audit Trail
1. Click **Logout** at the top right, then log in with the **Supervisor** account:
   - **Username**: `supervisor`
   - **Password**: `SupervisorDemo2026!`
2. Notice automatic redirect to `/supervisor/reviews/` (Supervisor Quality Portal).
3. **Verification**:
   - The supervisor sees all inspections submitted across ALL engineers.
   - Filter to `Pending Review`.
4. Click **Review Plate** next to any completed inspection.
5. In the Review modal:
   - View the original AI predicted class and confidence.
   - Select a decision (e.g., `Confirm Defect` or `Override to Normal`).
   - Enter supervisor notes: `"Verified surface roughness under optical microscope - false positive."`
   - Click **Submit Official Review**.
6. **Verification of Immutability & Concurrency**:
   - The inspection is immediately marked as `Reviewed`.
   - In the database, the inspection's original `predicted_class` remains intact.
   - The review is recorded in `reviews.Review` with `original_predicted_class` snapshot.
   - Submitting a second review on the same inspection returns `409 Conflict`.

---

### Step 7: Engineer Access Control Verification
1. Log back in as `engineer`.
2. Attempt to visit `/supervisor/reviews/` directly in the browser or via API (`POST /api/reviews/<id>/`).
3. **Verification**:
   - Access is denied with `HTTP 403 Forbidden`.
   - Role boundaries are strictly enforced at the API layer.

