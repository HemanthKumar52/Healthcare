import { notFound } from "next/navigation";
import type { Domain, Sensitivity } from "@hdm/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { QualityScoreRing } from "@/components/quality/quality-score-ring";
import { QualityMetrics } from "@/components/quality/quality-metrics";
import { cn, formatNumber } from "@/lib/utils";

/* -------------------------------------------------------------------------- */
/*  Mock data                                                                  */
/* -------------------------------------------------------------------------- */

interface MockProductDetail {
  name: string;
  slug: string;
  description: string;
  domain: Domain;
  sensitivity: Sensitivity;
  ownerName: string;
  stewardName: string;
  version: string;
  recordCount: number;
  refreshCadence: string;
  lastRefreshedAt: string;
  quality: {
    overall: number;
    completeness: number;
    uniqueness: number;
    freshness: number;
    referentialIntegrity: number;
    valueRange: number;
  };
  schema: {
    name: string;
    type: string;
    nullable: boolean;
    description: string;
  }[];
  sampleData: Record<string, string | number | null>[];
  reviews: {
    user: string;
    rating: number;
    comment: string;
    date: string;
  }[];
}

const PRODUCTS: Record<string, MockProductDetail> = {
  "patient-visit-summary": {
    name: "Patient Visit Summary",
    slug: "patient-visit-summary",
    description:
      "Aggregated view of patient encounters including diagnoses, procedures, vitals, and outcomes across all care settings. This data product joins encounter records with diagnosis codes (ICD-10), procedure codes (CPT), and clinical observations to provide a comprehensive picture of each patient visit. Covers inpatient, outpatient, and emergency department encounters. Data is refreshed daily from the EHR system and undergoes automated quality checks before publication.",
    domain: "CLINICAL",
    sensitivity: "PHI",
    ownerName: "Dr. Sarah Chen",
    stewardName: "Clinical Data Team",
    version: "2.3.1",
    recordCount: 2_456_831,
    refreshCadence: "Daily",
    lastRefreshedAt: "2026-05-18T04:30:00Z",
    quality: {
      overall: 94,
      completeness: 97.2,
      uniqueness: 99.8,
      freshness: 92.0,
      referentialIntegrity: 88.5,
      valueRange: 93.1,
    },
    schema: [
      { name: "encounter_id", type: "STRING", nullable: false, description: "Unique identifier for the encounter" },
      { name: "patient_id", type: "STRING", nullable: false, description: "De-identified patient identifier" },
      { name: "encounter_date", type: "DATE", nullable: false, description: "Date of the clinical encounter" },
      { name: "encounter_type", type: "STRING", nullable: false, description: "Type: INPATIENT, OUTPATIENT, ED" },
      { name: "primary_diagnosis", type: "STRING", nullable: false, description: "ICD-10 code for primary diagnosis" },
      { name: "diagnosis_description", type: "STRING", nullable: true, description: "Human-readable diagnosis name" },
      { name: "procedure_codes", type: "ARRAY<STRING>", nullable: true, description: "List of CPT procedure codes" },
      { name: "attending_provider_id", type: "STRING", nullable: false, description: "NPI of attending provider" },
      { name: "department", type: "STRING", nullable: false, description: "Hospital department or clinic" },
      { name: "length_of_stay_days", type: "INTEGER", nullable: true, description: "Days admitted (inpatient only)" },
      { name: "discharge_disposition", type: "STRING", nullable: true, description: "Discharge status code" },
    ],
    sampleData: [
      { encounter_id: "ENC-2026-00142", patient_id: "PAT-8834", encounter_date: "2026-05-15", encounter_type: "OUTPATIENT", primary_diagnosis: "E11.9", diagnosis_description: "Type 2 diabetes mellitus", department: "Endocrinology", length_of_stay_days: null },
      { encounter_id: "ENC-2026-00143", patient_id: "PAT-2291", encounter_date: "2026-05-15", encounter_type: "INPATIENT", primary_diagnosis: "I50.9", diagnosis_description: "Heart failure, unspecified", department: "Cardiology", length_of_stay_days: 4 },
      { encounter_id: "ENC-2026-00144", patient_id: "PAT-5507", encounter_date: "2026-05-16", encounter_type: "ED", primary_diagnosis: "S52.501A", diagnosis_description: "Fracture of lower end of radius", department: "Emergency", length_of_stay_days: null },
    ],
    reviews: [
      { user: "Anna Lopez", rating: 5, comment: "Excellent data product. The encounter-to-diagnosis linkage is very reliable and the daily refresh keeps it current for our clinical dashboards.", date: "2026-04-22" },
      { user: "David Kim", rating: 4, comment: "Good overall quality. The procedure code arrays are sometimes incomplete for ED visits, but the team is working on it.", date: "2026-03-15" },
      { user: "Priya Sharma", rating: 5, comment: "We use this as the backbone for our readmission prediction model. The data consistency is impressive.", date: "2026-02-08" },
    ],
  },
  "claims-analytics": {
    name: "Claims Analytics",
    slug: "claims-analytics",
    description:
      "Processed insurance claims with adjudication status, denial reasons, payment amounts, and payer mix analysis. Includes both professional (CMS-1500) and facility (UB-04) claims. Supports financial reporting, denial management, and payer contract analysis. Data is sourced from the clearinghouse and reconciled with internal billing records.",
    domain: "FINANCIAL",
    sensitivity: "PHI",
    ownerName: "Michael Torres",
    stewardName: "Revenue Cycle Analytics",
    version: "1.8.0",
    recordCount: 8_934_102,
    refreshCadence: "Daily",
    lastRefreshedAt: "2026-05-17T22:00:00Z",
    quality: {
      overall: 91,
      completeness: 94.5,
      uniqueness: 99.9,
      freshness: 88.0,
      referentialIntegrity: 90.2,
      valueRange: 91.8,
    },
    schema: [
      { name: "claim_id", type: "STRING", nullable: false, description: "Unique claim identifier" },
      { name: "patient_id", type: "STRING", nullable: false, description: "De-identified patient identifier" },
      { name: "claim_type", type: "STRING", nullable: false, description: "PROFESSIONAL or FACILITY" },
      { name: "payer_name", type: "STRING", nullable: false, description: "Insurance payer name" },
      { name: "service_date", type: "DATE", nullable: false, description: "Date of service" },
      { name: "billed_amount", type: "DECIMAL(12,2)", nullable: false, description: "Total billed amount" },
      { name: "allowed_amount", type: "DECIMAL(12,2)", nullable: true, description: "Payer allowed amount" },
      { name: "paid_amount", type: "DECIMAL(12,2)", nullable: true, description: "Amount paid by payer" },
      { name: "adjudication_status", type: "STRING", nullable: false, description: "PAID, DENIED, PENDING" },
      { name: "denial_reason_code", type: "STRING", nullable: true, description: "Denial reason (CARC code)" },
    ],
    sampleData: [
      { claim_id: "CLM-2026-98231", patient_id: "PAT-4412", claim_type: "PROFESSIONAL", payer_name: "Blue Cross", service_date: "2026-05-10", billed_amount: 450.0, allowed_amount: 380.0, paid_amount: 304.0, adjudication_status: "PAID", denial_reason_code: null },
      { claim_id: "CLM-2026-98232", patient_id: "PAT-7789", claim_type: "FACILITY", payer_name: "Medicare", service_date: "2026-05-11", billed_amount: 12500.0, allowed_amount: 8200.0, paid_amount: 6560.0, adjudication_status: "PAID", denial_reason_code: null },
      { claim_id: "CLM-2026-98233", patient_id: "PAT-1156", claim_type: "PROFESSIONAL", payer_name: "Aetna", service_date: "2026-05-12", billed_amount: 275.0, allowed_amount: null, paid_amount: null, adjudication_status: "DENIED", denial_reason_code: "CO-4" },
    ],
    reviews: [
      { user: "Rachel Green", rating: 4, comment: "Very useful for denial tracking. The CARC code mapping saves us hours of manual work.", date: "2026-04-10" },
      { user: "Tom Bradley", rating: 5, comment: "Our finance team relies on this daily. The payer mix breakdowns are accurate and timely.", date: "2026-03-28" },
    ],
  },
};

/* Fallback for slugs not in the detailed map */
function getFallbackProduct(slug: string): MockProductDetail | null {
  const fallbackMap: Record<string, Partial<MockProductDetail>> = {
    "bed-utilization-report": {
      name: "Bed Utilization Report",
      domain: "OPERATIONAL",
      sensitivity: "NO_PHI",
      ownerName: "Lisa Ramirez",
      stewardName: "Operations Analytics",
      description: "Real-time bed occupancy rates by unit, floor, and facility. Includes average length of stay, turnover rates, and capacity forecasting metrics for resource planning and patient flow optimization.",
      recordCount: 365_420,
      quality: { overall: 87, completeness: 91.3, uniqueness: 98.5, freshness: 85.0, referentialIntegrity: 82.4, valueRange: 89.7 },
    },
    "provider-directory": {
      name: "Provider Directory",
      domain: "PROVIDER",
      sensitivity: "NO_PHI",
      ownerName: "James Park",
      stewardName: "Provider Data Management",
      description: "Comprehensive physician and practitioner directory with credentials, specialties, NPI numbers, affiliations, panel status, and accepting-new-patients indicators. Used for referral management and network adequacy reporting.",
      recordCount: 42_318,
      quality: { overall: 96, completeness: 98.1, uniqueness: 100, freshness: 93.5, referentialIntegrity: 95.0, valueRange: 97.2 },
    },
    "population-health-cohorts": {
      name: "Population Health Cohorts",
      domain: "RESEARCH",
      sensitivity: "RESTRICTED",
      ownerName: "Dr. Aisha Patel",
      stewardName: "Population Health Research",
      description: "De-identified patient cohorts segmented by chronic condition, risk score, and social determinants of health. Supports population-level analytics, risk stratification, and intervention targeting for value-based care programs.",
      recordCount: 1_203_445,
      quality: { overall: 89, completeness: 92.0, uniqueness: 99.1, freshness: 84.5, referentialIntegrity: 87.3, valueRange: 91.6 },
    },
    "lab-results-analytics": {
      name: "Lab Results Analytics",
      domain: "CLINICAL",
      sensitivity: "PHI",
      ownerName: "Dr. Sarah Chen",
      stewardName: "Clinical Data Team",
      description: "Longitudinal laboratory test results with reference ranges, critical flags, trending values, and LOINC-coded test identifiers. Covers chemistry, hematology, and microbiology panels.",
      recordCount: 15_678_230,
      quality: { overall: 92, completeness: 95.8, uniqueness: 99.5, freshness: 90.2, referentialIntegrity: 86.8, valueRange: 92.3 },
    },
    "revenue-cycle-dashboard": {
      name: "Revenue Cycle Dashboard",
      domain: "FINANCIAL",
      sensitivity: "NO_PHI",
      ownerName: "Michael Torres",
      stewardName: "Revenue Cycle Analytics",
      description: "End-to-end revenue cycle metrics including charge capture rates, days in A/R, clean claim rates, collection percentages, and write-off analysis by service line.",
      recordCount: 523_890,
      quality: { overall: 78, completeness: 82.5, uniqueness: 97.0, freshness: 74.0, referentialIntegrity: 72.8, valueRange: 80.1 },
    },
    "appointment-scheduling-data": {
      name: "Appointment Scheduling Data",
      domain: "OPERATIONAL",
      sensitivity: "NO_PHI",
      ownerName: "Lisa Ramirez",
      stewardName: "Operations Analytics",
      description: "Appointment volume, no-show rates, wait times, scheduling lead times, and slot utilization by department and provider. Supports capacity planning and access optimization.",
      recordCount: 1_847_562,
      quality: { overall: 85, completeness: 88.4, uniqueness: 99.2, freshness: 82.0, referentialIntegrity: 80.5, valueRange: 87.6 },
    },
  };

  const partial = fallbackMap[slug];
  if (!partial) return null;

  return {
    name: partial.name ?? slug,
    slug,
    description: partial.description ?? "",
    domain: partial.domain ?? "CLINICAL",
    sensitivity: partial.sensitivity ?? "NO_PHI",
    ownerName: partial.ownerName ?? "Unknown",
    stewardName: partial.stewardName ?? "Unknown",
    version: "1.0.0",
    recordCount: partial.recordCount ?? 0,
    refreshCadence: "Daily",
    lastRefreshedAt: "2026-05-17T06:00:00Z",
    quality: partial.quality ?? { overall: 80, completeness: 80, uniqueness: 80, freshness: 80, referentialIntegrity: 80, valueRange: 80 },
    schema: [
      { name: "id", type: "STRING", nullable: false, description: "Primary key identifier" },
      { name: "name", type: "STRING", nullable: false, description: "Record name" },
      { name: "value", type: "DECIMAL(12,2)", nullable: true, description: "Metric value" },
      { name: "category", type: "STRING", nullable: false, description: "Record category" },
      { name: "recorded_at", type: "TIMESTAMP", nullable: false, description: "When the record was captured" },
      { name: "updated_at", type: "TIMESTAMP", nullable: false, description: "Last update timestamp" },
    ],
    sampleData: [
      { id: "REC-001", name: "Sample Record A", value: 142.5, category: "Primary", recorded_at: "2026-05-15T08:00:00Z", updated_at: "2026-05-15T08:00:00Z" },
      { id: "REC-002", name: "Sample Record B", value: 89.3, category: "Secondary", recorded_at: "2026-05-15T09:30:00Z", updated_at: "2026-05-15T10:00:00Z" },
      { id: "REC-003", name: "Sample Record C", value: null, category: "Primary", recorded_at: "2026-05-16T07:15:00Z", updated_at: "2026-05-16T07:15:00Z" },
    ],
    reviews: [
      { user: "Alex Johnson", rating: 4, comment: "Reliable and well-documented. Great addition to the marketplace.", date: "2026-04-05" },
    ],
  };
}

/* -------------------------------------------------------------------------- */
/*  Tab component (simple div-based, no Radix)                                */
/* -------------------------------------------------------------------------- */

function TabTrigger({
  active,
  children,
  id,
}: {
  active: boolean;
  children: React.ReactNode;
  id: string;
}) {
  return (
    <a
      href={`#${id}`}
      className={cn(
        "border-b-2 px-4 py-2.5 text-sm font-medium transition-colors",
        active
          ? "border-primary text-primary"
          : "border-transparent text-muted-foreground hover:border-muted-foreground/30 hover:text-foreground"
      )}
    >
      {children}
    </a>
  );
}

/* -------------------------------------------------------------------------- */
/*  Domain / sensitivity badge helpers                                         */
/* -------------------------------------------------------------------------- */

const domainVariant: Record<Domain, "clinical" | "operational" | "financial" | "provider" | "research"> = {
  CLINICAL: "clinical",
  OPERATIONAL: "operational",
  FINANCIAL: "financial",
  PROVIDER: "provider",
  RESEARCH: "research",
};

const sensitivityVariant: Record<Sensitivity, "phi" | "noPhi" | "restricted"> = {
  PHI: "phi",
  NO_PHI: "noPhi",
  RESTRICTED: "restricted",
};

const sensitivityLabel: Record<Sensitivity, string> = {
  PHI: "PHI",
  NO_PHI: "No PHI",
  RESTRICTED: "Restricted",
};

/* -------------------------------------------------------------------------- */
/*  Stars                                                                      */
/* -------------------------------------------------------------------------- */

function Stars({ rating }: { rating: number }) {
  return (
    <div className="flex gap-0.5">
      {Array.from({ length: 5 }).map((_, i) => (
        <svg
          key={i}
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill={i < rating ? "currentColor" : "none"}
          stroke="currentColor"
          strokeWidth="1.5"
          className={cn("h-4 w-4", i < rating ? "text-yellow-500" : "text-muted-foreground/40")}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z"
          />
        </svg>
      ))}
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*  Page component                                                             */
/* -------------------------------------------------------------------------- */

interface ProductDetailPageProps {
  params: Promise<{ slug: string }>;
}

export default async function ProductDetailPage({ params }: ProductDetailPageProps) {
  const { slug } = await params;
  const product = PRODUCTS[slug] ?? getFallbackProduct(slug);

  if (!product) {
    notFound();
  }

  const avgRating =
    product.reviews.length > 0
      ? product.reviews.reduce((sum, r) => sum + r.rating, 0) / product.reviews.length
      : 0;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8 flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <Badge variant={domainVariant[product.domain]}>
              {product.domain.charAt(0) + product.domain.slice(1).toLowerCase()}
            </Badge>
            <Badge variant={sensitivityVariant[product.sensitivity]}>
              {sensitivityLabel[product.sensitivity]}
            </Badge>
            <Badge variant="outline">v{product.version}</Badge>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">{product.name}</h1>
          <p className="mt-3 max-w-3xl text-muted-foreground leading-relaxed">
            {product.description}
          </p>
          <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
            <span>
              Owner: <span className="font-medium text-foreground">{product.ownerName}</span>
            </span>
            <span>
              Steward: <span className="font-medium text-foreground">{product.stewardName}</span>
            </span>
            <span>
              Records: <span className="font-medium text-foreground">{formatNumber(product.recordCount)}</span>
            </span>
            <span>
              Refresh: <span className="font-medium text-foreground">{product.refreshCadence}</span>
            </span>
          </div>
        </div>
        <div className="flex flex-col items-center gap-3">
          <QualityScoreRing score={product.quality.overall} size={130} />
          <Button size="lg" className="w-full min-w-[200px]">
            Request Access
          </Button>
        </div>
      </div>

      {/* Tabs (all sections visible, navigable by anchor) */}
      <div className="border-b">
        <nav className="-mb-px flex gap-0 overflow-x-auto">
          <TabTrigger active id="quality">Quality</TabTrigger>
          <TabTrigger active={false} id="schema">Schema</TabTrigger>
          <TabTrigger active={false} id="sample-data">Sample Data</TabTrigger>
          <TabTrigger active={false} id="lineage">Lineage</TabTrigger>
          <TabTrigger active={false} id="reviews">Reviews</TabTrigger>
        </nav>
      </div>

      <div className="mt-8 space-y-12">
        {/* Quality Section */}
        <section id="quality">
          <h2 className="mb-4 text-xl font-semibold">Quality Scores</h2>
          <Card>
            <CardContent className="p-6">
              <QualityMetrics
                completeness={product.quality.completeness}
                uniqueness={product.quality.uniqueness}
                freshness={product.quality.freshness}
                referentialIntegrity={product.quality.referentialIntegrity}
                valueRange={product.quality.valueRange}
              />
            </CardContent>
          </Card>
        </section>

        {/* Schema Section */}
        <section id="schema">
          <h2 className="mb-4 text-xl font-semibold">Schema</h2>
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="px-4 py-3 text-left font-medium">Column</th>
                      <th className="px-4 py-3 text-left font-medium">Type</th>
                      <th className="px-4 py-3 text-center font-medium">Nullable</th>
                      <th className="px-4 py-3 text-left font-medium">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {product.schema.map((col, i) => (
                      <tr
                        key={col.name}
                        className={cn(
                          "border-b last:border-0",
                          i % 2 === 0 ? "bg-background" : "bg-muted/20"
                        )}
                      >
                        <td className="px-4 py-2.5 font-mono text-xs">{col.name}</td>
                        <td className="px-4 py-2.5 font-mono text-xs text-muted-foreground">
                          {col.type}
                        </td>
                        <td className="px-4 py-2.5 text-center">
                          {col.nullable ? (
                            <span className="text-yellow-600">Yes</span>
                          ) : (
                            <span className="text-green-600">No</span>
                          )}
                        </td>
                        <td className="px-4 py-2.5 text-muted-foreground">{col.description}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Sample Data Section */}
        <section id="sample-data">
          <h2 className="mb-4 text-xl font-semibold">Sample Data</h2>
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      {product.schema.map((col) => (
                        <th key={col.name} className="whitespace-nowrap px-4 py-3 text-left font-medium">
                          {col.name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {product.sampleData.map((row, rowIdx) => (
                      <tr
                        key={rowIdx}
                        className={cn(
                          "border-b last:border-0",
                          rowIdx % 2 === 0 ? "bg-background" : "bg-muted/20"
                        )}
                      >
                        {product.schema.map((col) => (
                          <td
                            key={col.name}
                            className="whitespace-nowrap px-4 py-2.5 font-mono text-xs"
                          >
                            {row[col.name] != null ? String(row[col.name]) : (
                              <span className="text-muted-foreground italic">null</span>
                            )}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Lineage Section */}
        <section id="lineage">
          <h2 className="mb-4 text-xl font-semibold">Data Lineage</h2>
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-12 w-12 text-muted-foreground/50"
              >
                <circle cx="12" cy="5" r="3" />
                <line x1="12" y1="8" x2="12" y2="14" />
                <circle cx="6" cy="19" r="3" />
                <circle cx="18" cy="19" r="3" />
                <line x1="12" y1="14" x2="6" y2="16" />
                <line x1="12" y1="14" x2="18" y2="16" />
              </svg>
              <p className="mt-4 text-lg font-medium text-muted-foreground">
                Interactive lineage graph
              </p>
              <p className="mt-1 text-sm text-muted-foreground">
                Visual DAG showing upstream sources, transformations, and downstream consumers will be rendered here using React Flow.
              </p>
            </CardContent>
          </Card>
        </section>

        {/* Reviews Section */}
        <section id="reviews">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold">Reviews</h2>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Stars rating={Math.round(avgRating)} />
              <span>
                {avgRating.toFixed(1)} ({product.reviews.length}{" "}
                {product.reviews.length === 1 ? "review" : "reviews"})
              </span>
            </div>
          </div>
          <div className="space-y-4">
            {product.reviews.map((review, i) => (
              <Card key={i}>
                <CardContent className="p-5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
                        {review.user.charAt(0)}
                      </div>
                      <div>
                        <p className="text-sm font-medium">{review.user}</p>
                        <p className="text-xs text-muted-foreground">{review.date}</p>
                      </div>
                    </div>
                    <Stars rating={review.rating} />
                  </div>
                  <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
                    {review.comment}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
