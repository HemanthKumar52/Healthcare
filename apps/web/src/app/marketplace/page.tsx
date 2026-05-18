import { Suspense } from "react";
import type { Domain, Sensitivity, ProductStatus } from "@hdm/types";
import { SearchBar } from "@/components/marketplace/search-bar";
import { DomainFilter } from "@/components/marketplace/domain-filter";
import { ProductCard } from "@/components/marketplace/product-card";

interface MockProduct {
  id: string;
  name: string;
  slug: string;
  description: string;
  domain: Domain;
  sensitivity: Sensitivity;
  status: ProductStatus;
  qualityScore: number;
  recordCount: number;
  lastRefreshedAt: Date;
  ownerName: string;
}

const MOCK_PRODUCTS: MockProduct[] = [
  {
    id: "clx1a0001",
    name: "Patient Visit Summary",
    slug: "patient-visit-summary",
    description:
      "Aggregated view of patient encounters including diagnoses, procedures, vitals, and outcomes across all care settings. Linked to provider and facility data.",
    domain: "CLINICAL",
    sensitivity: "PHI",
    status: "PUBLISHED",
    qualityScore: 94,
    recordCount: 2_456_831,
    lastRefreshedAt: new Date("2026-05-18T04:30:00Z"),
    ownerName: "Dr. Sarah Chen",
  },
  {
    id: "clx1a0002",
    name: "Claims Analytics",
    slug: "claims-analytics",
    description:
      "Processed insurance claims with adjudication status, denial reasons, payment amounts, and payer mix analysis. Includes both professional and facility claims.",
    domain: "FINANCIAL",
    sensitivity: "PHI",
    status: "PUBLISHED",
    qualityScore: 91,
    recordCount: 8_934_102,
    lastRefreshedAt: new Date("2026-05-17T22:00:00Z"),
    ownerName: "Michael Torres",
  },
  {
    id: "clx1a0003",
    name: "Bed Utilization Report",
    slug: "bed-utilization-report",
    description:
      "Real-time bed occupancy rates by unit, floor, and facility. Includes average length of stay, turnover rates, and capacity forecasting metrics.",
    domain: "OPERATIONAL",
    sensitivity: "NO_PHI",
    status: "PUBLISHED",
    qualityScore: 87,
    recordCount: 365_420,
    lastRefreshedAt: new Date("2026-05-18T06:00:00Z"),
    ownerName: "Lisa Ramirez",
  },
  {
    id: "clx1a0004",
    name: "Provider Directory",
    slug: "provider-directory",
    description:
      "Comprehensive physician and practitioner directory with credentials, specialties, NPI numbers, affiliations, panel status, and accepting-new-patients indicators.",
    domain: "PROVIDER",
    sensitivity: "NO_PHI",
    status: "PUBLISHED",
    qualityScore: 96,
    recordCount: 42_318,
    lastRefreshedAt: new Date("2026-05-16T08:00:00Z"),
    ownerName: "James Park",
  },
  {
    id: "clx1a0005",
    name: "Population Health Cohorts",
    slug: "population-health-cohorts",
    description:
      "De-identified patient cohorts segmented by chronic condition, risk score, and social determinants of health. Supports population-level analytics and intervention targeting.",
    domain: "RESEARCH",
    sensitivity: "RESTRICTED",
    status: "PUBLISHED",
    qualityScore: 89,
    recordCount: 1_203_445,
    lastRefreshedAt: new Date("2026-05-15T12:00:00Z"),
    ownerName: "Dr. Aisha Patel",
  },
  {
    id: "clx1a0006",
    name: "Lab Results Analytics",
    slug: "lab-results-analytics",
    description:
      "Longitudinal laboratory test results with reference ranges, critical flags, trending values, and LOINC-coded test identifiers. Covers chemistry, hematology, and microbiology panels.",
    domain: "CLINICAL",
    sensitivity: "PHI",
    status: "PUBLISHED",
    qualityScore: 92,
    recordCount: 15_678_230,
    lastRefreshedAt: new Date("2026-05-18T05:15:00Z"),
    ownerName: "Dr. Sarah Chen",
  },
  {
    id: "clx1a0007",
    name: "Revenue Cycle Dashboard",
    slug: "revenue-cycle-dashboard",
    description:
      "End-to-end revenue cycle metrics including charge capture rates, days in A/R, clean claim rates, collection percentages, and write-off analysis by service line.",
    domain: "FINANCIAL",
    sensitivity: "NO_PHI",
    status: "PUBLISHED",
    qualityScore: 78,
    recordCount: 523_890,
    lastRefreshedAt: new Date("2026-05-17T20:00:00Z"),
    ownerName: "Michael Torres",
  },
  {
    id: "clx1a0008",
    name: "Appointment Scheduling Data",
    slug: "appointment-scheduling-data",
    description:
      "Appointment volume, no-show rates, wait times, scheduling lead times, and slot utilization by department and provider. Supports capacity planning and access optimization.",
    domain: "OPERATIONAL",
    sensitivity: "NO_PHI",
    status: "PUBLISHED",
    qualityScore: 85,
    recordCount: 1_847_562,
    lastRefreshedAt: new Date("2026-05-18T03:00:00Z"),
    ownerName: "Lisa Ramirez",
  },
];

interface MarketplacePageProps {
  searchParams: Promise<{
    q?: string;
    domain?: string;
    sensitivity?: string;
  }>;
}

export default async function MarketplacePage({ searchParams }: MarketplacePageProps) {
  const params = await searchParams;
  const query = params.q?.toLowerCase() ?? "";
  const domainFilter = params.domain ?? "";
  const sensitivityFilter = params.sensitivity ?? "";

  const filtered = MOCK_PRODUCTS.filter((product) => {
    if (query && !product.name.toLowerCase().includes(query) && !product.description.toLowerCase().includes(query)) {
      return false;
    }
    if (domainFilter && product.domain !== domainFilter) {
      return false;
    }
    if (sensitivityFilter && product.sensitivity !== sensitivityFilter) {
      return false;
    }
    return true;
  });

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Data Marketplace</h1>
        <p className="mt-2 text-muted-foreground">
          Discover, evaluate, and request access to trusted healthcare data products.
        </p>
      </div>

      <div className="mb-6 space-y-4">
        <Suspense fallback={null}>
          <SearchBar />
        </Suspense>
        <Suspense fallback={null}>
          <DomainFilter />
        </Suspense>
      </div>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-16 text-center">
          <p className="text-lg font-medium">No data products found</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Try adjusting your search or filters.
          </p>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
}
