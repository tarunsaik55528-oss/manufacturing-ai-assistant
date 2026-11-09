# REQUIREMENTS CHECKLIST
## Round 2 – AI Visual Quality Inspection System

| ID | Requirement Description | Django Module | DB Model | API Endpoint | Frontend Screen | Automated Test | Status |
|---|---|---|---|---|---|---|---|
| REQ-01 | User Authentication (Session + DRF) | `accounts` | `accounts.User` | `POST /api/auth/login/`, `POST /api/auth/logout/` | `/login/` | `test_login_logout_flow` | DONE (tested) |
| REQ-02 | Current User Profile & Role Info | `accounts` | `accounts.User` | `GET /api/auth/me/` | Dashboard Header | `test_auth_me_returns_profile_and_role` | DONE (tested) |
| REQ-03 | RBAC Permission Classes & Mixins | `accounts` | `accounts.User` | Permissions on all views | Role-specific views | `test_rbac_permission_classes_with_mock_urls` | DONE (tested) |
| REQ-04 | Demo Users & Role Seeding Command | `accounts` | `accounts.User` | `seed_round2_roles` management command | N/A | `test_seed_round2_roles_management_command` | DONE (tested) |
| REQ-05 | Product Registration & Catalogue | `products` | `products.Product` | `GET/POST /api/products/`, `PUT /api/products/<id>/` | `/admin/products/` | `test_product_api_authorization` | DONE (tested) |
| REQ-06 | Product Seeding from CSV | `products` | `products.Product` | `seed_products` management command | N/A | `test_seed_products_idempotency` | DONE (tested) |
| REQ-07 | Image Server-side Validation | `inspections` | `inspections.Inspection` | Upload handlers | Upload Dropzone | `test_validation_corrupt_image_fails_safely` | DONE (tested) |
| REQ-08 | Protected Media Serving (RBAC) | `inspections` | `inspections.Inspection` | `GET /media/inspections/<id>/image/` | Inspection View | `test_protected_media_access` | DONE (tested) |
| REQ-09 | AI Model Wrapper & Verification | `ai_model` | N/A | `ai_model.service.predict_image` | N/A | `test_service_wrapper_prediction_on_real_samples` | DONE (tested) |
| REQ-10 | Single-Image Inspection Flow | `inspections` | `inspections.Inspection` | `POST /api/inspections/upload/` | `/inspections/new/` | `test_valid_single_upload_real_samples` | DONE (tested) |
| REQ-11 | Batch Inspection Flow (Celery+Redis) | `inspections` | `inspections.Batch`, `Inspection` | `POST /api/inspections/batch/` | `/inspections/batch/` | `test_mixed_batch_processing_and_isolation` | DONE (tested) |
| REQ-12 | Per-item Status Polling & Tracking | `inspections` | `inspections.Inspection` | `GET /api/inspections/<id>/status/`, `GET /api/batches/<id>/` | Batch Tracker | `test_mixed_batch_processing_and_isolation` | DONE (tested) |
| REQ-13 | Inspection History with Filtering | `inspections` | `inspections.Inspection` | `GET /api/inspections/` | `/inspections/history/` | `test_role_scoped_inspection_history` | DONE (tested) |
| REQ-14 | Supervisor Review Submission | `reviews` | `reviews.Review` | `POST /api/reviews/<inspection_id>/` | `/supervisor/review/<id>/` | `test_supervisor_review_submission_and_immutability` | DONE (tested) |
| REQ-15 | Engineer Review Forbidden (403) | `reviews` | `reviews.Review` | `POST /api/reviews/<inspection_id>/` | N/A | `test_engineer_cannot_review_returns_403` | DONE (tested) |
| REQ-16 | Review Immutability & Conflict (409) | `reviews` | `reviews.Review` | `POST /api/reviews/<inspection_id>/` | `/supervisor/reviews/` | `test_duplicate_review_returns_409_conflict` | DONE (tested) |
| REQ-17 | Model Evaluation (60 samples + CSV) | `ai_model` | N/A | `evaluate_model` management command | N/A | `test_evaluate_model_command_generates_outputs` | DONE (tested) |
| REQ-18 | System Health & Deploy Checks | `config` | N/A | `python manage.py check --deploy` | N/A | `test_django_system_check` | DONE (tested) |
