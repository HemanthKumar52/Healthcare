# Healthcare Data Marketplace Platform

Enterprise Healthcare Data Marketplace built with **Next.js 15**, **PySpark**, **Prisma**, and **Unity Catalog** integration on Databricks. A self-service platform where users can discover, trust, and consume governed healthcare data products.

---

## Problem Statement

Organizations struggle to discover, trust, and reuse enterprise datasets. Data is scattered across silos, lacks meaningful metadata, trust is low (no quality scores, no ownership), discovery is manual, and access is a bureaucratic bottleneck.

## Solution

A curated data marketplace that treats healthcare datasets as **data products** — packaged, documented, trustworthy assets with quality scores, lineage tracking, access controls, and HIPAA compliance built in.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Next.js 15 Marketplace UI                     │
│  Landing Page │ Browse/Search │ Product Detail │ 4 Dashboards    │
├─────────────────────────────────────────────────────────────────┤
│                     Next.js API Routes (13)                      │
│  Products │ Search │ Access │ Quality │ Audit │ Notifications    │
├─────────────────────────────────────────────────────────────────┤
│              PostgreSQL (Prisma ORM, 16 models)                  │
│     Users │ Products │ Quality │ Access │ Audit │ Lineage        │
├─────────────────────────────────────────────────────────────────┤
│                   PySpark Data Pipelines                         │
│         Bronze (Raw) → Silver (Clean) → Gold (Curated)           │
├─────────────────────────────────────────────────────────────────┤
│                    Data Sources (20 CSVs)                         │
│  Phase 1: Synthetic Healthcare │ Phase 2: CMS │ Phase 3: CDC     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Five Healthcare Data Domains

| Domain | Description | Data Products |
|--------|-------------|---------------|
| **Clinical** | EHR extracts, lab results, medications, diagnoses, vitals | Patient Visit Summary, Lab Analytics, Medication Summary |
| **Operational** | Patient flow, bed occupancy, appointment scheduling | Bed Utilization, Appointment Analytics |
| **Financial** | Claims, billing, revenue cycle, CMS Medicare analysis | Claims Analytics, Revenue Cycle, CMS Claims, CMS Prescriptions |
| **Provider** | Physician rosters, credentials, performance metrics | Provider Directory |
| **Research** | De-identified cohorts, population health, mortality trends | Population Health, De-identified Cohorts, CDC Mortality Analysis |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15 (App Router), TypeScript, shadcn/ui, Tailwind CSS |
| **Visualization** | React Flow (lineage graphs), Recharts (quality trends) |
| **Database** | PostgreSQL with Prisma ORM (16 models) |
| **Search** | Meilisearch (full-text, faceted filtering) |
| **Auth** | Auth.js v5 (OAuth/SSO ready) |
| **Data Processing** | PySpark (medallion architecture) |
| **Governance** | Unity Catalog (tags, lineage, grants) |
| **Type Safety** | Zod schemas + Prisma + TypeScript strict mode |
| **Monorepo** | Turborepo + pnpm workspaces |
| **CI/CD** | GitHub Actions |
| **Infrastructure** | Docker Compose (PostgreSQL + Meilisearch) |

---

## Features (29 Total)

### Core Features
1. **Medallion Architecture** — Bronze → Silver → Gold data pipeline pattern
2. **PySpark Curation Pipelines** — 13 pipelines across 5 domains
3. **Unity Catalog Integration** — Metadata, lineage, tagging, grants
4. **Data Quality Framework** — 5 automated checks (completeness, uniqueness, freshness, referential integrity, value range)
5. **Config-Driven Data Products** — YAML definitions, no code needed for new products
6. **Next.js Marketplace App** — SSR pages, API routes, App Router
7. **Professional UI** — shadcn/ui components with domain-specific badges
8. **PostgreSQL Database** — 16 Prisma models covering all business entities
9. **Authentication** — Auth.js v5 with OAuth/SSO support
10. **Access Request Workflow** — Request → Approve/Deny → Auto-grant
11. **HIPAA Compliance** — PHI classification, sensitivity badges, audit trails
12. **3-Phase Dataset Integration** — Synthetic Healthcare + CMS + CDC (583K+ rows)
13. **De-identification Pipelines** — Safe Harbor, SHA-256 hashing, age generalization
14. **PHI Scanner** — Regex-based detection of SSN, MRN, phone, email patterns

### Professional Enhancements
15. **End-to-End Type Safety** — Zod + Prisma + TypeScript strict
16. **Full-Text Search** — Meilisearch with faceted filtering
17. **Interactive Lineage Graphs** — React Flow DAG visualization
18. **Data Profiling** — Column-level stats, null %, distributions, sample data
19. **Notification System** — In-app bell + email-ready (Resend)
20. **4 Role-Based Dashboards** — Consumer, Steward, Admin, Engineer
21. **Immutable Audit Trail** — Every action logged with actor, timestamp, target
22. **Data Contracts & SLAs** — Freshness/quality thresholds with breach alerts
23. **Ratings & Reviews** — Star ratings and comments on data products
24. **Usage Analytics** — View/download tracking, trending products
25. **Turborepo Monorepo** — Shared types, parallel builds
26. **Docker Compose** — One command local dev (PostgreSQL + Meilisearch)
27. **CI/CD Pipeline** — GitHub Actions: lint, type-check, test, build
28. **API Documentation** — OpenAPI-ready endpoints
29. **Observability** — Sentry + Pino + PostHog ready

---

## Project Structure

```
healthcare-data-marketplace/
├── apps/web/                          # Next.js 15 App
│   ├── src/app/                       # Pages & API Routes
│   │   ├── page.tsx                   # Landing page
│   │   ├── marketplace/               # Browse & product detail
│   │   ├── (dashboard)/               # 4 role-based dashboards
│   │   ├── (auth)/                    # Login & register
│   │   └── api/                       # 13 API routes
│   ├── src/components/                # 17 UI components
│   │   ├── ui/                        # shadcn/ui primitives
│   │   ├── marketplace/               # Product cards, search, filters
│   │   ├── lineage/                   # React Flow graph
│   │   ├── quality/                   # Score rings, metric bars
│   │   ├── notifications/             # Bell dropdown
│   │   ├── profiling/                 # Column stats table
│   │   └── dashboard/                 # Stats cards
│   └── src/lib/                       # Auth, utils, validators
├── packages/
│   ├── db/                            # Prisma schema (16 models) + seed
│   └── types/                         # Shared Zod schemas (9 files)
├── pipelines/
│   ├── ingestion/                     # 3 ingestion pipelines
│   │   ├── load_synthetic_healthcare.py
│   │   ├── load_cms_synpuf.py
│   │   └── load_cdc_wonder.py
│   ├── curation/                      # 13 gold-layer pipelines
│   │   ├── clinical/                  # patient_visits, lab_analytics, medication_summary
│   │   ├── operational/               # bed_utilization, appointment_analytics
│   │   ├── financial/                 # claims_analytics, revenue_cycle, cms_claims, cms_prescriptions
│   │   ├── provider/                  # provider_directory
│   │   └── research/                  # population_health, deidentified_cohorts, cdc_mortality
│   ├── quality/                       # Quality engine + 5 checks + PHI scanner
│   ├── config/                        # 7 YAML product definitions
│   └── utils/                         # Spark session, UC helpers, de-identification
├── data/datasets/                     # 20 CSV files (583K+ rows)
├── scripts/                           # Data generators
├── docker-compose.yml                 # PostgreSQL + Meilisearch
├── .github/workflows/ci.yml          # CI/CD pipeline
└── CLAUDE.md                          # Full project documentation
```

---

## Datasets (3 Phases)

### Phase 1 — Synthetic Healthcare (15 CSVs, 103K rows)
Core hospital operations data: patients, encounters, diagnoses, procedures, prescriptions, lab results, vitals, appointments, admissions, rooms/beds, departments, billing, insurance claims, payments, doctors.

### Phase 2 — CMS DE-SynPUF (4 CSVs, 53K rows)
Synthetic Medicare claims data: beneficiary summary (demographics, chronic conditions), inpatient claims, outpatient claims, prescription drug events.

### Phase 3 — CDC WONDER (1 CSV, 428K rows)
Mortality data: deaths by cause, state, year, age group, gender, and race across all 50 US states (2015–2023) with 15 leading causes of death.

**Total: 20 CSVs | 583,737 rows | 13 data products | 7 YAML configs**

---

## Database Schema

16 Prisma models covering the full marketplace domain:

- **User** — Roles: Consumer, Steward, Admin, Engineer
- **DataProduct** — 5 domains, 3 sensitivity levels, versioned
- **DataProductTag** — Key-value metadata (PHI, HIPAA, business unit)
- **QualityScore** — 5 metrics + overall score with history
- **QualitySLA** — Threshold-based monitoring with breach detection
- **AccessRequest** — Full lifecycle: Pending → Approved/Denied → Expired
- **AuditLog** — 15 action types with actor, target, metadata
- **Notification** — 10 types with read/unread tracking
- **Review** — Star ratings (1-5) with comments
- **ColumnProfile** — Schema statistics per column
- **LineageNode/Edge** — DAG representation of data flow
- **UsageMetric** — View, download, query tracking

---

## Getting Started

### Prerequisites
- Node.js 22+
- pnpm 11+
- Docker & Docker Compose
- Python 3.12+ (for PySpark pipelines)

### Setup

```bash
# Clone the repository
git clone https://github.com/HemanthKumar52/Healthcare.git
cd Healthcare

# Install dependencies
pnpm install

# Start PostgreSQL and Meilisearch
docker-compose up -d

# Copy environment variables
cp .env.example .env

# Generate Prisma client and run migrations
pnpm turbo db:generate
pnpm turbo db:migrate

# Seed the database with sample data
pnpm turbo db:seed

# Start the development server
pnpm turbo dev
```

Open [http://localhost:3000](http://localhost:3000) to see the marketplace.

### Running PySpark Pipelines

```bash
# Install Python dependencies
pip install -r pipelines/requirements.txt

# Generate sample datasets (if not already present)
python scripts/generate_sample_data.py
python scripts/generate_cms_data.py
python scripts/generate_cdc_data.py

# Run ingestion (bronze layer)
spark-submit pipelines/ingestion/load_synthetic_healthcare.py
spark-submit pipelines/ingestion/load_cms_synpuf.py
spark-submit pipelines/ingestion/load_cdc_wonder.py

# Run curation (gold layer)
spark-submit pipelines/curation/clinical/patient_visits.py
spark-submit pipelines/curation/financial/cms_claims_analysis.py
spark-submit pipelines/curation/research/cdc_mortality_analysis.py

# Run quality checks
python pipelines/quality/quality_engine.py --config pipelines/config/clinical_products.yaml
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | List data products (paginated, filterable) |
| POST | `/api/products` | Create a data product |
| GET | `/api/products/[slug]` | Get product detail with quality, reviews |
| PATCH | `/api/products/[slug]` | Update product metadata |
| GET | `/api/search` | Full-text search with facets |
| POST | `/api/access/requests` | Submit access request |
| PATCH | `/api/access/requests/[id]` | Approve or deny request |
| GET | `/api/quality/[productId]` | Quality scores and SLA status |
| GET | `/api/audit` | Query audit logs |
| GET | `/api/notifications` | User notifications |
| GET | `/api/profiling/[productId]` | Column-level statistics |
| GET/POST | `/api/reviews/[productId]` | Product reviews |
| GET | `/api/usage` | Trending products |

---

## PySpark Pipeline Summary

| Pipeline | Type | Output Table |
|----------|------|-------------|
| load_synthetic_healthcare.py | Ingestion | 15 bronze tables |
| load_cms_synpuf.py | Ingestion | 4 bronze tables |
| load_cdc_wonder.py | Ingestion | 1 bronze table |
| patient_visits.py | Curation | clinical.patient_visit_summary |
| lab_analytics.py | Curation | clinical.lab_analytics |
| medication_summary.py | Curation | clinical.medication_summary |
| bed_utilization.py | Curation | operational.bed_utilization |
| appointment_analytics.py | Curation | operational.appointment_analytics |
| claims_analytics.py | Curation | financial.claims_analytics |
| revenue_cycle.py | Curation | financial.revenue_cycle |
| cms_claims_analysis.py | Curation | financial.cms_claims_analysis |
| cms_prescription_analysis.py | Curation | financial.cms_prescription_analysis |
| provider_directory.py | Curation | provider.provider_directory |
| population_health.py | Curation | research.population_health |
| deidentified_cohorts.py | Curation | research.deidentified_cohorts |
| cdc_mortality_analysis.py | Curation | research.cdc_mortality_analysis |
| quality_engine.py | Quality | Runs checks from YAML config |
| phi_scanner.py | Quality | Scans for PHI patterns |

---

## Role-Based Dashboards

| Role | Dashboard Features |
|------|-------------------|
| **Consumer** | Approved products, pending requests, recent activity |
| **Steward** | Pending approvals, managed products, quality alerts |
| **Admin** | System overview, user management, audit trail, system health |
| **Engineer** | Pipeline runs, quality trends, data lineage |

---

## License

This project is built for the Healthcare Data Marketplace hackathon.
