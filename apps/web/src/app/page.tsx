import Link from "next/link";
import {
  Database,
  Search,
  Shield,
  TrendingUp,
  Users,
  Activity,
} from "lucide-react";

const stats = [
  { label: "Data Products", value: "2,400+", icon: Database },
  { label: "Active Users", value: "850+", icon: Users },
  { label: "Quality Score", value: "94.2%", icon: TrendingUp },
  { label: "Governed Assets", value: "12,000+", icon: Shield },
];

const domains = [
  {
    name: "Clinical",
    description: "EHR extracts, lab results, medication orders, diagnoses",
    count: 620,
    color: "bg-blue-500",
    href: "/marketplace?domain=CLINICAL",
  },
  {
    name: "Operational",
    description: "Patient flow, bed occupancy, appointment schedules",
    count: 480,
    color: "bg-green-500",
    href: "/marketplace?domain=OPERATIONAL",
  },
  {
    name: "Financial",
    description: "Claims, billing, revenue cycle, payments",
    count: 540,
    color: "bg-amber-500",
    href: "/marketplace?domain=FINANCIAL",
  },
  {
    name: "Provider",
    description: "Physician rosters, credentials, affiliations",
    count: 320,
    color: "bg-purple-500",
    href: "/marketplace?domain=PROVIDER",
  },
  {
    name: "Research",
    description: "De-identified cohorts, trial data, real-world evidence",
    count: 440,
    color: "bg-red-500",
    href: "/marketplace?domain=RESEARCH",
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="h-6 w-6 text-primary" />
            <span className="font-bold text-lg">HDM</span>
            <span className="text-muted-foreground text-sm hidden sm:inline">
              Healthcare Data Marketplace
            </span>
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/marketplace"
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition"
            >
              Browse
            </Link>
            <Link
              href="/login"
              className="text-sm font-medium bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition"
            >
              Sign In
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-purple-500/5" />
        <div className="max-w-7xl mx-auto px-6 py-24 relative">
          <div className="max-w-3xl">
            <h1 className="text-5xl font-bold tracking-tight text-foreground mb-6">
              Discover, Trust & Consume{" "}
              <span className="text-primary">Healthcare Data</span>
            </h1>
            <p className="text-xl text-muted-foreground mb-8 leading-relaxed">
              Enterprise-grade data marketplace with thousands of curated,
              governed healthcare datasets. Find the data you need in seconds,
              not weeks.
            </p>
            <div className="flex items-center gap-3">
              <Link
                href="/marketplace"
                className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-lg font-medium hover:bg-primary/90 transition"
              >
                <Search className="h-4 w-4" />
                Explore Data Products
              </Link>
              <Link
                href="/register"
                className="inline-flex items-center gap-2 border px-6 py-3 rounded-lg font-medium hover:bg-secondary transition"
              >
                Request Access
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y bg-white">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <stat.icon className="h-8 w-8 text-primary mx-auto mb-3" />
                <div className="text-3xl font-bold">{stat.value}</div>
                <div className="text-sm text-muted-foreground mt-1">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Domains */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Browse by Domain</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Data products organized across five healthcare domains, each with
            comprehensive quality scores, lineage tracking, and governed access
            controls.
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {domains.map((domain) => (
            <Link
              key={domain.name}
              href={domain.href}
              className="group border rounded-xl p-6 hover:shadow-lg transition-all hover:border-primary/20"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-3 h-3 rounded-full ${domain.color}`} />
                <h3 className="font-semibold text-lg group-hover:text-primary transition">
                  {domain.name}
                </h3>
                <span className="ml-auto text-sm text-muted-foreground bg-secondary px-2 py-0.5 rounded-full">
                  {domain.count}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">
                {domain.description}
              </p>
            </Link>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="border-t bg-secondary/30">
        <div className="max-w-7xl mx-auto px-6 py-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">
              Enterprise-Grade Governance
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white rounded-xl p-6 border">
              <Shield className="h-10 w-10 text-primary mb-4" />
              <h3 className="font-semibold text-lg mb-2">
                HIPAA Compliant
              </h3>
              <p className="text-sm text-muted-foreground">
                Every data product is tagged with sensitivity levels. PHI
                detection, de-identification pipelines, and audit trails built
                in.
              </p>
            </div>
            <div className="bg-white rounded-xl p-6 border">
              <TrendingUp className="h-10 w-10 text-primary mb-4" />
              <h3 className="font-semibold text-lg mb-2">
                Data Quality Scores
              </h3>
              <p className="text-sm text-muted-foreground">
                Automated quality checks on completeness, uniqueness, freshness,
                and referential integrity. SLA monitoring with breach alerts.
              </p>
            </div>
            <div className="bg-white rounded-xl p-6 border">
              <Database className="h-10 w-10 text-primary mb-4" />
              <h3 className="font-semibold text-lg mb-2">
                Unity Catalog Powered
              </h3>
              <p className="text-sm text-muted-foreground">
                Built on Databricks Unity Catalog for unified governance,
                automatic lineage, and fine-grained access control.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-white">
        <div className="max-w-7xl mx-auto px-6 py-8 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            <span className="font-semibold">HDM</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Enterprise Healthcare Data Marketplace
          </p>
        </div>
      </footer>
    </div>
  );
}
