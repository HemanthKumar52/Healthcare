# Healthcare Data Marketplace Platform (EHDM)

## Project Overview

Enterprise Healthcare Data Marketplace -- a platform that treats curated, governed healthcare datasets as **data products**: packaged, documented, trustworthy assets that business and technical users can discover, understand, and consume with minimal friction.

### Problem Statement

Organizations struggle to discover, trust, and reuse enterprise datasets. Data is scattered across silos, lacks meaningful metadata, trust is low (no quality scores, no ownership), discovery is manual, and access is a bureaucratic bottleneck.

### Solution

Build an Enterprise Healthcare Data Marketplace using PySpark and Unity Catalog integration on Databricks. The platform provides a self-service storefront for thousands of governed datasets and enterprise data products, backed by automated curation pipelines, data quality scoring, and fine-grained access control.

### Target Users

- **Data Consumers** (analysts, data scientists): Browse, search, request access, consume data products
- **Data Stewards/Owners**: Approve requests, manage metadata, monitor quality
- **Platform Admins**: User management, audit logs, system health, usage analytics
- **Data Engineers**: Pipeline status, quality trends, schema changes

---

## Five Data Domains

All data products are organized into five healthcare domains:

| Domain | Description | Examples |
|---|---|---|
| **Clinical** | Patient care and treatment data | EHR extracts, lab results, medication orders, diagnoses, vitals |
| **Operational** | Hospital operations and logistics | Patient flow, bed occupancy, appointment schedules, admissions |
| **Financial** | Billing, claims, and revenue data | Claims, billing, revenue cycle, payments, insurance |
| **Provider** | Healthcare professional information | Physician rosters, credentials, affiliations, specialties |
| **Research** | De-identified data for analysis | De-identified cohorts, trial data, real-world evidence, population health |

---

## Datasets

### Primary Dataset (Must Have)

**Synthetic Healthcare Case-Based Dataset** (Kaggle)
- 15 CSV files covering all 5 domains
- Files: `patients.csv`, `encounters.csv`, `diagnoses.csv`, `procedures.csv`, `prescriptions.csv`, `lab_results.csv`, `vitals.csv`, `appointments.csv`, `admissions.csv`, `rooms_beds.csv`, `departments.csv`, `billing.csv`, `insurance_claims.csv`, `payments.csv`, `doctors.csv`
- Multi-table relational structure, ideal for PySpark joins and transformations
- Intentionally includes imperfect data for quality framework validation

### Strategic Dataset 1

**CMS 2008-2010 Data Entrepreneurs' Synthetic Public Use File (DE-SynPUF)**
- Synthetic Medicare claims data from CMS
- Millions of records across Inpatient, Outpatient, and Prescription Drug Event files
- Real medical coding (ICD, HCPCS)
- Domains: Financial (claims), Operational (utilization), Research (population health)

### Strategic Dataset 2

**CDC WONDER Mortality Data**
- U.S. mortality data by cause, race, and county
- Tab-delimited format
- Domains: Research (public health), Operational (resource planning)

### Related Data Sources (Current and Future)

| Source | Type | Domains |
|---|---|---|
| **MIMIC** (PhysioNet) | Clinical ICU EHR data (requires CITI training + credentialing) | Clinical, Research |
| **CMS** (Centers for Medicare & Medicaid Services) | Claims, costs, provider data (public PUFs + restricted DUA) | Financial, Provider, Operational |
| **CDC** (Centers for Disease Control) | Public health surveillance, epidemiologic data | Clinical, Operational, Research |
| **WHO GHO** | International health statistics, 1000+ indicators, REST API | Clinical, Research, Operational |
| **HealthData.gov** | U.S. federal health datasets (FDA, NIH) | Clinical, Operational, Research |
| **ClinicalTrials.gov** | Clinical studies database, REST API | Clinical, Research |
| **PhysioNet** | 350+ biomedical research datasets | Clinical, Research |
| **Vivli** | Anonymized patient-level clinical trial data | Clinical, Research |
| **Nightingale Open Science** | 400K+ de-identified medical images | Clinical, Research |
| **CMS Open Payments** | Financial relationships between manufacturers and providers | Provider, Financial |
| **IBM MarketScan** | De-identified claims data, 170M+ patients (commercial license) | Financial, Clinical, Operational |
| **TriNetX** | Federated real-world clinical data (commercial license) | Clinical, Research, Financial |
| **LexisNexis Gravitas** | Claims linked to SDoH (commercial license) | Clinical, Operational, Research |
| **IQVIA** | Prescription, claims, EHR data (commercial license) | Clinical, Financial, Operational |
| **Trilliant Health** | National provider directory (available on Databricks Marketplace) | Provider |

---

## Architecture

### Monorepo Structure (Turborepo)

```
healthcare-data-marketplace/
├── apps/
│   └── web/                          # Next.js 15 (App Router)
│       ├── app/                      # Pages, layouts, API routes
│       │   ├── (auth)/               # Login, register pages
│       │   ├── (dashboard)/          # Role-based dashboards
│       │   │   ├── consumer/         # Data consumer views
│       │   │   ├── steward/          # Data steward views
│       │   │   ├── admin/            # Platform admin views
│       │   │   └── engineer/         # Data engineer views
│       │   ├── marketplace/          # Browse, search, product detail
│       │   ├── lineage/              # Interactive lineage graphs
│       │   ├── api/                  # API routes
│       │   │   ├── products/         # Data product CRUD
│       │   │   ├── access/           # Access request workflow
│       │   │   ├── quality/          # Quality scores and SLAs
│       │   │   ├── audit/            # Audit trail
│       │   │   ├── notifications/    # Notification management
│       │   │   ├── search/           # Search endpoint
│       │   │   └── docs/             # OpenAPI/Swagger UI
│       │   └── layout.tsx            # Root layout
│       ├── components/               # shadcn/ui + custom components
│       │   ├── ui/                   # shadcn primitives
│       │   ├── marketplace/          # Product cards, filters, search bar
│       │   ├── lineage/              # React Flow graph components
│       │   ├── quality/              # Quality score badges, trend charts
│       │   ├── profiling/            # Column stats, histograms, sample viewer
│       │   ├── notifications/        # Bell icon, dropdown, notification items
│       │   └── dashboard/            # Role-specific dashboard widgets
│       └── lib/                      # Utilities
│           ├── prisma.ts             # Prisma client singleton
│           ├── auth.ts               # Auth.js config
│           ├── search.ts             # Meilisearch client
│           └── validators/           # Zod schemas for API validation
├── packages/
│   ├── db/                           # Prisma schema + migrations
│   │   ├── prisma/
│   │   │   ├── schema.prisma         # Database schema
│   │   │   └── migrations/           # Migration files
│   │   └── seed.ts                   # Seed script
│   ├── types/                        # Shared TypeScript types + Zod schemas
│   │   ├── data-product.ts
│   │   ├── access-request.ts
│   │   ├── quality.ts
│   │   ├── audit.ts
│   │   └── user.ts
│   └── config/                       # Shared configs
│       ├── eslint/
│       ├── tailwind/
│       └── typescript/
├── pipelines/                        # PySpark data processing
│   ├── ingestion/                    # Bronze layer - raw data loading
│   │   ├── load_synthetic_healthcare.py
│   │   ├── load_cms_synpuf.py
│   │   └── load_cdc_wonder.py
│   ├── curation/                     # Silver → Gold transformations
│   │   ├── clinical/
│   │   │   ├── patient_visits.py
│   │   │   ├── lab_analytics.py
│   │   │   └── medication_summary.py
│   │   ├── operational/
│   │   │   ├── bed_utilization.py
│   │   │   └── appointment_analytics.py
│   │   ├── financial/
│   │   │   ├── claims_analytics.py
│   │   │   └── revenue_cycle.py
│   │   ├── provider/
│   │   │   └── provider_directory.py
│   │   └── research/
│   │       ├── population_health.py
│   │       └── deidentified_cohorts.py
│   ├── quality/                      # Data quality checks
│   │   ├── quality_engine.py         # Core quality check framework
│   │   ├── checks/
│   │   │   ├── completeness.py
│   │   │   ├── uniqueness.py
│   │   │   ├── freshness.py
│   │   │   ├── referential_integrity.py
│   │   │   └── value_range.py
│   │   └── phi_scanner.py            # PHI/PII detection
│   ├── config/                       # Data product YAML definitions
│   │   ├── clinical_products.yaml
│   │   ├── operational_products.yaml
│   │   ├── financial_products.yaml
│   │   ├── provider_products.yaml
│   │   └── research_products.yaml
│   └── utils/
│       ├── spark_session.py          # Spark session factory
│       ├── unity_catalog.py          # UC metadata helpers
│       └── deidentification.py       # De-identification utilities
├── docker-compose.yml                # PostgreSQL + Meilisearch + app
├── turbo.json                        # Turborepo config
├── package.json                      # Root package.json
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Lint, type-check, test, build
│       └── e2e.yml                   # Playwright E2E tests
├── .env.example                      # Environment variable template
└── CLAUDE.md                         # This file
```

### Data Flow (Medallion Architecture)

```
Raw CSVs → [Bronze: Raw Tables] → [Silver: Cleaned/Standardized] → [Gold: Curated Data Products]
                                                                          ↓
                                                                  Unity Catalog
                                                                  (tags, lineage, grants)
                                                                          ↓
                                                                  Quality Engine
                                                                  (scores, SLAs, alerts)
                                                                          ↓
                                                                  Marketplace API
                                                                  (Next.js API routes)
                                                                          ↓
                                                                  Marketplace UI
                                                                  (browse, search, request)
```

---

## Tech Stack

### Frontend + Backend

| Technology | Purpose |
|---|---|
| **Next.js 15** (App Router) | Full-stack framework -- pages, layouts, API routes, SSR |
| **TypeScript** (strict mode) | End-to-end type safety |
| **shadcn/ui** | Professional UI component library |
| **Tailwind CSS** | Utility-first styling |
| **React Flow** | Interactive data lineage DAG visualization |
| **Recharts** | Quality score trends, profiling histograms, usage charts |
| **Auth.js (NextAuth)** | Authentication with OAuth/SSO (Entra ID, Google, credentials) |
| **Zod** | Runtime schema validation at all API boundaries |

### Database & Search

| Technology | Purpose |
|---|---|
| **PostgreSQL** | Primary database -- marketplace metadata, access requests, audit logs, users |
| **Prisma** | Type-safe ORM with auto-generated types and migrations |
| **Meilisearch** | Full-text search with faceted filtering, typo tolerance, relevance ranking |

### Data Processing

| Technology | Purpose |
|---|---|
| **PySpark** | All data transformations (bronze → silver → gold) |
| **Delta Lake** | ACID storage format (native to Databricks) |
| **Unity Catalog** | Governance -- metastore, lineage, tags, grants, row/column security |
| **Databricks Workflows** | Pipeline orchestration and scheduling |
| **Delta Live Tables (DLT)** | Declarative, production-grade pipelines (enterprise enhancement) |

### DevOps & Infrastructure

| Technology | Purpose |
|---|---|
| **Turborepo** | Monorepo management |
| **Docker Compose** | Local development (PostgreSQL + Meilisearch + app) |
| **GitHub Actions** | CI/CD -- lint, type-check, test, build on every PR |
| **Playwright** | End-to-end browser testing |
| **Vitest** | Unit and integration testing |
| **Husky + lint-staged** | Pre-commit hooks |
| **Vercel** | Frontend deployment with preview URLs |
| **Terraform** (Databricks provider) | Infrastructure as code for Databricks resources |

### Observability

| Technology | Purpose |
|---|---|
| **Sentry** | Error tracking (frontend + backend) |
| **Pino** | Structured JSON logging |
| **PostHog** or **Vercel Analytics** | Product analytics and usage tracking |

### Notifications

| Technology | Purpose |
|---|---|
| **Resend** | Transactional email (access approvals, quality alerts) |
| **In-app notifications** | Bell icon + dropdown (stored in PostgreSQL) |
| **Webhooks** | Slack/Teams integration for enterprise notification channels |

---

## Feature Set (29 Features)

### Core Features (14)

1. **Medallion Architecture** -- Bronze → Silver → Gold data pipeline pattern with PySpark
2. **PySpark Curation Pipelines** -- Configurable, parameterized data transformations
3. **Unity Catalog Integration** -- Metadata layer for governance, lineage, tagging, grants
4. **Data Quality Framework** -- Automated checks: completeness, uniqueness, freshness, referential integrity, value range
5. **5-Domain Coverage** -- Clinical, Operational, Financial, Provider, Research data products
6. **Next.js Marketplace App** -- SSR pages, API routes, App Router with nested layouts
7. **shadcn/ui Professional Interface** -- Cards, tables, filters, modals, forms
8. **PostgreSQL Marketplace Database** -- Metadata, access requests, audit logs, user profiles
9. **Auth.js Authentication** -- OAuth/SSO with Entra ID, Google, or credential-based login
10. **Access Request & Approval Workflow** -- User requests → steward approves → auto-grants UC permissions
11. **HIPAA Compliance Tagging** -- PHI classification badges, sensitivity indicators on every data product
12. **Dataset Integration** -- Synthetic Healthcare, CMS DE-SynPUF, CDC WONDER ingested and curated
13. **Config-Driven Data Product Registration** -- YAML definitions for each data product (schema, owner, SLA, tags)
14. **De-identification Pipeline Templates** -- PySpark modules for Safe Harbor, k-anonymization

### Professional Enhancements (15)

15. **End-to-End Type Safety** -- Zod + Prisma + TypeScript strict mode across all boundaries
16. **Full-Text Search** -- Meilisearch with faceted filtering (domain, sensitivity, quality, owner, freshness)
17. **Interactive Lineage Graphs** -- React Flow DAG showing upstream sources → data product → downstream consumers
18. **Data Profiling & Preview** -- Column-level stats (null %, distinct count, min/max, distribution), sample data viewer, schema diff
19. **Notification System** -- In-app bell notifications + email (Resend) + Slack/Teams webhooks
20. **4 Role-Based Dashboards** -- Consumer, Steward, Admin, Engineer each get a tailored view
21. **Immutable Audit Trail** -- Every action logged with timestamp, actor, action, target; exportable reports
22. **Data Contracts & SLAs** -- Freshness SLA ("refreshes daily by 6 AM"), quality SLA ("completeness > 95%"), breach alerts
23. **Star Ratings & Reviews** -- Users rate and review data products; social proof builds trust
24. **Usage Analytics** -- Track views, downloads, popularity; trending/popular sections on marketplace
25. **Turborepo Monorepo** -- Shared configs, parallel builds, dependency management
26. **Docker Compose Dev Environment** -- One command: `docker-compose up` starts PostgreSQL + Meilisearch + app
27. **CI/CD Pipeline** -- GitHub Actions for lint, type-check, test, build; Playwright E2E tests
28. **Auto-Generated API Docs** -- OpenAPI spec from API routes, Swagger UI at `/api/docs`
29. **Observability Stack** -- Sentry error tracking + Pino structured logging + PostHog product analytics

---

## Database Schema (Prisma -- Key Models)

### Core Models

- **User** -- id, name, email, role (CONSUMER | STEWARD | ADMIN | ENGINEER), avatar, department
- **DataProduct** -- id, name, slug, description, domain (CLINICAL | OPERATIONAL | FINANCIAL | PROVIDER | RESEARCH), owner (User), steward (User), sensitivity (PHI | NO_PHI | RESTRICTED), status (DRAFT | PUBLISHED | DEPRECATED), refreshCadence, lastRefreshedAt, catalogName, schemaName, tableName, version, createdAt, updatedAt
- **DataProductTag** -- id, productId, key, value (e.g., key: "contains_phi", value: "true")
- **QualityScore** -- id, productId, completeness (float), uniqueness (float), freshness (float), referentialIntegrity (float), overallScore (float), checkedAt
- **QualitySLA** -- id, productId, metric (COMPLETENESS | FRESHNESS | etc.), threshold (float), operator (GTE | LTE), isBreached, lastCheckedAt
- **AccessRequest** -- id, requesterId, productId, justification, status (PENDING | APPROVED | DENIED | REVOKED), approvedBy (User), grantedAt, expiresAt, createdAt
- **AuditLog** -- id, actorId, action (enum), targetType, targetId, metadata (JSON), ipAddress, timestamp
- **Notification** -- id, userId, type (ACCESS_APPROVED | ACCESS_DENIED | QUALITY_ALERT | NEW_PRODUCT | SLA_BREACH), title, message, isRead, createdAt
- **Review** -- id, userId, productId, rating (1-5), comment, createdAt
- **ColumnProfile** -- id, productId, columnName, dataType, nullPercentage, distinctCount, minValue, maxValue, sampleValues (JSON)
- **LineageNode** -- id, productId, nodeType (SOURCE | TRANSFORM | TARGET), name, metadata (JSON)
- **LineageEdge** -- id, sourceNodeId, targetNodeId, transformDescription
- **UsageMetric** -- id, productId, userId, action (VIEW | DOWNLOAD | QUERY), timestamp

---

## Data Product YAML Configuration Format

Each data product is defined by a YAML file in `pipelines/config/`:

```yaml
product:
  name: "Patient Visit Summary"
  slug: "patient-visit-summary"
  domain: "clinical"
  description: "Aggregated view of patient encounters with diagnoses, procedures, and outcomes"
  owner: "clinical-data-team"
  steward: "dr-smith"
  sensitivity: "phi"
  version: "1.0.0"

source:
  catalog: "healthcare_marketplace"
  schema: "clinical"
  table: "patient_visit_summary"
  format: "delta"

refresh:
  cadence: "daily"
  sla_hour: 6  # Must be refreshed by 6 AM

quality:
  checks:
    - metric: "completeness"
      columns: ["patient_id", "encounter_date", "diagnosis_code"]
      threshold: 0.98
    - metric: "uniqueness"
      columns: ["encounter_id"]
      threshold: 1.0
    - metric: "freshness"
      max_age_hours: 26
    - metric: "value_range"
      column: "age"
      min: 0
      max: 120

lineage:
  sources:
    - "bronze.raw_encounters"
    - "bronze.raw_diagnoses"
    - "bronze.raw_procedures"
  transforms:
    - "Join encounters with diagnoses on encounter_id"
    - "Filter active patients only"
    - "Aggregate procedures per visit"

tags:
  contains_phi: "true"
  hipaa_certified: "true"
  business_unit: "clinical-analytics"
```

---

## Unity Catalog Structure

```
healthcare_marketplace (catalog)
├── clinical (schema)
│   ├── patient_visit_summary
│   ├── lab_analytics
│   └── medication_summary
├── operational (schema)
│   ├── bed_utilization
│   └── appointment_analytics
├── financial (schema)
│   ├── claims_analytics
│   └── revenue_cycle
├── provider (schema)
│   └── provider_directory
└── research (schema)
    ├── population_health
    └── deidentified_cohorts

marketplace_metadata (catalog)
├── quality (schema)
│   └── quality_scores
├── audit (schema)
│   └── audit_log
└── access (schema)
    └── access_requests
```

---

## Key Marketplace UI Pages

### Public / Auth

- `/login` -- OAuth/SSO login page
- `/register` -- Registration (if not SSO-only)

### Marketplace (all authenticated users)

- `/marketplace` -- Browse all data products with search bar, faceted filters, domain tabs
- `/marketplace/[slug]` -- Product detail: description, schema, quality scores, lineage graph, profiling stats, sample data, reviews, "Request Access" button
- `/marketplace/search?q=...&domain=...&sensitivity=...` -- Search results with facets

### Consumer Dashboard

- `/dashboard/consumer` -- My approved data products, pending requests, consumption instructions
- `/dashboard/consumer/requests` -- Access request history

### Steward Dashboard

- `/dashboard/steward` -- Pending approval requests, managed products, quality alerts
- `/dashboard/steward/products` -- Manage owned data products (edit metadata, view usage)
- `/dashboard/steward/quality` -- Quality score trends, SLA breach alerts

### Admin Dashboard

- `/dashboard/admin` -- System overview: total products, users, requests, health
- `/dashboard/admin/users` -- User management (roles, permissions)
- `/dashboard/admin/audit` -- Audit trail viewer with filters and export

### Engineer Dashboard

- `/dashboard/engineer` -- Pipeline status, recent runs, failures
- `/dashboard/engineer/quality` -- Quality trends across all products
- `/dashboard/engineer/lineage` -- Full platform lineage graph

### API Documentation

- `/api/docs` -- Swagger UI for all API endpoints

---

## API Endpoints

### Data Products

- `GET /api/products` -- List all products (paginated, filterable)
- `GET /api/products/[slug]` -- Get product detail
- `POST /api/products` -- Create product (steward/admin)
- `PATCH /api/products/[slug]` -- Update product metadata
- `DELETE /api/products/[slug]` -- Deprecate product

### Search

- `GET /api/search?q=&domain=&sensitivity=&minQuality=` -- Full-text search with facets

### Access

- `POST /api/access/request` -- Submit access request
- `GET /api/access/requests` -- List requests (filtered by role)
- `PATCH /api/access/requests/[id]` -- Approve/deny request
- `DELETE /api/access/requests/[id]` -- Revoke access

### Quality

- `GET /api/quality/[productId]` -- Get quality scores and trend
- `GET /api/quality/sla/breaches` -- List active SLA breaches

### Audit

- `GET /api/audit` -- Query audit logs (admin only)
- `GET /api/audit/export` -- Export audit logs as CSV

### Notifications

- `GET /api/notifications` -- Get user notifications
- `PATCH /api/notifications/[id]/read` -- Mark as read
- `POST /api/notifications/read-all` -- Mark all as read

### Profiling

- `GET /api/profiling/[productId]` -- Get column-level statistics
- `GET /api/profiling/[productId]/sample` -- Get sample data (10 rows)

### Reviews

- `GET /api/reviews/[productId]` -- Get reviews for a product
- `POST /api/reviews/[productId]` -- Submit a review

### Usage

- `GET /api/usage/[productId]` -- Get usage metrics
- `GET /api/usage/trending` -- Get trending products

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/healthcare_marketplace

# Meilisearch
MEILISEARCH_HOST=http://localhost:7700
MEILISEARCH_API_KEY=your-master-key

# Auth
AUTH_SECRET=your-auth-secret
AUTH_GOOGLE_ID=your-google-client-id
AUTH_GOOGLE_SECRET=your-google-client-secret
# For enterprise: AUTH_AZURE_AD_CLIENT_ID, AUTH_AZURE_AD_CLIENT_SECRET, AUTH_AZURE_AD_TENANT_ID

# Databricks (for Unity Catalog API access)
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-personal-access-token

# Email (Resend)
RESEND_API_KEY=your-resend-api-key

# Error Tracking
SENTRY_DSN=your-sentry-dsn
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn

# Analytics
NEXT_PUBLIC_POSTHOG_KEY=your-posthog-key
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
```

---

## PySpark Pipeline Conventions

- **Spark session**: Always created via `utils/spark_session.py` factory with consistent app name and config
- **Naming**: Bronze tables = `bronze.raw_{source}`, Silver tables = `silver.clean_{entity}`, Gold tables = `{domain}.{product_name}`
- **Idempotency**: All pipelines are idempotent; safe to re-run without duplicating data
- **Quality checks**: Run after every curation step; results written to `marketplace_metadata.quality.quality_scores`
- **Metadata tagging**: Every gold table gets UC tags set via `ALTER TABLE ... SET TAGS` immediately after creation
- **Config-driven**: New data products are added by creating a YAML config file; no new Python code needed for standard patterns
- **De-identification**: PHI fields are handled via `utils/deidentification.py`; never write PHI to research-domain tables

---

## Development Commands

```bash
# Install dependencies
pnpm install

# Start local dev environment (PostgreSQL + Meilisearch)
docker-compose up -d

# Run database migrations
pnpm turbo db:migrate

# Seed database with sample data
pnpm turbo db:seed

# Start Next.js dev server
pnpm turbo dev

# Run all tests
pnpm turbo test

# Run E2E tests
pnpm exec playwright test

# Lint and type-check
pnpm turbo lint
pnpm turbo type-check

# Build for production
pnpm turbo build

# Run PySpark pipelines (from pipelines/ directory)
spark-submit pipelines/ingestion/load_synthetic_healthcare.py
spark-submit pipelines/curation/clinical/patient_visits.py
spark-submit pipelines/quality/quality_engine.py --product patient-visit-summary
```

---

## Git Workflow

- **Never push directly to main** -- always raise a PR
- Branch naming: `feature/`, `fix/`, `chore/` prefixes
- PRs require passing CI (lint + type-check + tests) before merge
- Commit messages: conventional commits (`feat:`, `fix:`, `chore:`, `docs:`)

---

## Future Enhancements (Post-Hackathon Roadmap)

### Phase 2: Targeted Enhancements

- **Real-time streaming data products** from ICU monitors, wearables (Spark Structured Streaming)
- **Genomic & multi-omics data layer** (Cancer Imaging Archive, dbGaP)
- **Social Determinants of Health (SDoH)** data products integrated with clinical data
- **Federated data product queries** across multiple Databricks deployments
- **Delta Live Tables (DLT)** migration for declarative pipeline management
- **ServiceNow/Jira integration** for access request ticketing

### Phase 3: AI-Powered Features

- **Natural language data discovery** -- AI copilot that understands "find me diabetes readmission data"
- **Auto-generated data product descriptions** from schema and sample data
- **Smart recommendations** -- "Users who accessed this also accessed..."
- **Anomaly detection** on quality scores with automatic alerting
- **Schema evolution advisor** -- AI suggests migration strategy for breaking changes

### Phase 4: Enterprise Scale

- **Multi-cloud support** (Azure + AWS)
- **Azure Purview / AWS Glue integration** for automatic PHI/PII classification
- **Collibra/Alation integration** for business glossary synchronization
- **Custom Databricks Marketplace listings** for external data sharing
- **Open APIs and community** -- external partners publish governed data products

---

## Key Design Decisions

1. **Next.js over Streamlit** -- Professional marketplace UI, not a data science prototype; SSR for performance; API routes eliminate separate backend
2. **Meilisearch over PostgreSQL full-text** -- Sub-millisecond typo-tolerant search with facets; critical for marketplace UX
3. **Prisma over raw SQL** -- Type-safe database access; auto-generated migrations; developer productivity
4. **YAML config over code** -- New data products should not require new Python code; config-driven registration scales to thousands of products
5. **React Flow for lineage** -- Industry-standard DAG library; interactive, not static images
6. **Monorepo over polyrepo** -- Shared types between frontend and pipelines config; atomic changes; single CI pipeline
7. **PostgreSQL for marketplace state** -- Not everything belongs in Unity Catalog; access requests, reviews, notifications, audit logs are application-layer concerns
8. **PySpark over dbt** -- Hackathon requires PySpark per project spec; PySpark handles complex healthcare transformations (de-identification, FHIR flattening) better than SQL-first tools
