# SYSTEM ARCHITECTURE
## Round 2 – AI Visual Quality Inspection System

```mermaid
flowchart TD
    subgraph Client["Frontend Client (Bootstrap 5 + Vanilla JS)"]
        UI_Admin["Administrator UI\n(Products & Users)"]
        UI_Eng["Engineer UI\n(Single / Batch Upload & History)"]
        UI_Sup["Supervisor UI\n(Review Queue & History Audit)"]
    end

    subgraph Security["Security & Routing Layer"]
        AuthMiddleware["Session & Auth Middleware"]
        RBAC["RBAC Permissions\n(IsAdministrator, IsEngineer, IsSupervisor)"]
        ProtectedMedia["Protected Media View\n(Role & Owner Verified)"]
    end

    subgraph Django["Django Backend (REST Framework)"]
        AuthApp["accounts\n(User, Login, /me, Groups)"]
        ProdApp["products\n(Product Catalogue & Seeding)"]
        InspApp["inspections\n(Upload, Validation, History)"]
        RevApp["reviews\n(Supervisor Audit & Immutability)"]
        ModelWrapper["ai_model.service\n(Wrapper for Model/inference.py)"]
    end

    subgraph CeleryAsync["Asynchronous Processing"]
        RedisBroker[("Redis Broker & Result Backend")]
        CeleryWorker["Celery Worker\n(Batch Inference Tasks)"]
    end

    subgraph Storage["Persistence & Media"]
        PostgresDB[("PostgreSQL Database\n(Products, Batches, Inspections, Reviews)")]
        MediaStorage[("Local Media Directory\n(UUID Named Images)")]
        FrozenModel[("Frozen Model\nclassifier.npz (BIT-PLATE-CV-1.0)")]
    end

    Client --> Security
    Security --> Django
    InspApp -->|Enqueue Valid Batch Items| RedisBroker
    RedisBroker --> CeleryWorker
    CeleryWorker --> ModelWrapper
    InspApp -->|Single Upload| ModelWrapper
    ModelWrapper --> FrozenModel
    Django --> PostgresDB
    Django --> MediaStorage
    ProtectedMedia --> MediaStorage
```

### Key Subsystems
1. **Frontend**: Bootstrap 5 responsive layout with unified industrial theme, role-tailored navigation bars, stat cards, asynchronous polling with live status badges.
2. **REST API**: Session and Token-compatible DRF endpoints strictly validating payload schemas and user privileges.
3. **Queueing Subsystem**: Celery dispatch via `transaction.on_commit()` ensuring zero orphaned tasks if a database rollback occurs.
4. **AI Inference Service**: Isolated Python wrapper executing standard feature extraction and logistic regression with CPU thread safety.
5. **Database**: PostgreSQL maintaining strict relational integrity, indexed foreign keys, and atomic review transactions.

