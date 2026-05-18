import {
  Play,
  XCircle,
  Timer,
  RefreshCcw,
  TrendingUp,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StatsCard } from "@/components/dashboard/stats-card";

const pipelineRuns = [
  {
    id: 1,
    name: "Clinical Ingestion - Patient Visits",
    status: "success",
    duration: "4m 12s",
    records: 148320,
    startedAt: "09:30 AM",
  },
  {
    id: 2,
    name: "Financial Curation - Claims Analytics",
    status: "success",
    duration: "7m 45s",
    records: 512840,
    startedAt: "09:00 AM",
  },
  {
    id: 3,
    name: "Quality Engine - Full Scan",
    status: "success",
    duration: "12m 03s",
    records: 1024000,
    startedAt: "08:00 AM",
  },
  {
    id: 4,
    name: "Provider Sync - Directory Update",
    status: "failed",
    duration: "1m 58s",
    records: 0,
    startedAt: "07:30 AM",
  },
  {
    id: 5,
    name: "Research - De-identification Pipeline",
    status: "success",
    duration: "9m 31s",
    records: 85200,
    startedAt: "06:00 AM",
  },
  {
    id: 6,
    name: "Operational - Bed Utilization Refresh",
    status: "running",
    duration: "2m 14s",
    records: 32150,
    startedAt: "09:42 AM",
  },
];

const statusBadge: Record<string, { variant: "default" | "destructive" | "outline" | "secondary"; label: string }> = {
  success: { variant: "default", label: "Success" },
  failed: { variant: "destructive", label: "Failed" },
  running: { variant: "secondary", label: "Running" },
};

const qualityTrends = [
  { domain: "Clinical", current: 96.2, previous: 94.8, products: 3 },
  { domain: "Operational", current: 89.5, previous: 91.2, products: 2 },
  { domain: "Financial", current: 93.1, previous: 92.7, products: 2 },
  { domain: "Provider", current: 72.0, previous: 85.4, products: 1 },
  { domain: "Research", current: 94.8, previous: 93.1, products: 2 },
];

function formatRecords(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export default function EngineerDashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Engineer Dashboard</h1>
        <p className="mt-1 text-muted-foreground">
          Pipeline monitoring, run history, and quality trends.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          icon={<Play className="h-5 w-5" />}
          label="Pipeline Runs Today"
          value="18"
          trend={{ direction: "up", percentage: 12 }}
        />
        <StatsCard
          icon={<XCircle className="h-5 w-5" />}
          label="Failed Pipelines"
          value="1"
          trend={{ direction: "down", percentage: 67 }}
        />
        <StatsCard
          icon={<Timer className="h-5 w-5" />}
          label="Avg Processing Time"
          value="6m 14s"
          trend={{ direction: "down", percentage: 8 }}
        />
        <StatsCard
          icon={<RefreshCcw className="h-5 w-5" />}
          label="Data Products Updated"
          value="9"
          trend={{ direction: "up", percentage: 5 }}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Recent Pipeline Runs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left">
                    <th className="pb-3 font-medium text-muted-foreground">Pipeline</th>
                    <th className="pb-3 font-medium text-muted-foreground">Status</th>
                    <th className="pb-3 font-medium text-muted-foreground">Duration</th>
                    <th className="pb-3 font-medium text-muted-foreground text-right">Records</th>
                  </tr>
                </thead>
                <tbody>
                  {pipelineRuns.map((run) => {
                    const badge = statusBadge[run.status];
                    return (
                      <tr key={run.id} className="border-b last:border-0">
                        <td className="py-3">
                          <div>
                            <p className="font-medium">{run.name}</p>
                            <p className="text-xs text-muted-foreground">
                              Started at {run.startedAt}
                            </p>
                          </div>
                        </td>
                        <td className="py-3">
                          <Badge variant={badge.variant}>{badge.label}</Badge>
                        </td>
                        <td className="py-3 font-mono text-xs text-muted-foreground">
                          {run.duration}
                        </td>
                        <td className="py-3 text-right font-medium">
                          {formatRecords(run.records)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              Quality Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {qualityTrends.map((trend) => {
                const delta = trend.current - trend.previous;
                const isPositive = delta >= 0;
                return (
                  <div key={trend.domain} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium">{trend.domain}</p>
                        <p className="text-xs text-muted-foreground">
                          {trend.products} product{trend.products > 1 ? "s" : ""}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-bold">{trend.current}%</p>
                        <p
                          className={`text-xs font-medium ${
                            isPositive ? "text-green-600" : "text-red-600"
                          }`}
                        >
                          {isPositive ? "+" : ""}
                          {delta.toFixed(1)}%
                        </p>
                      </div>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-muted">
                      <div
                        className={`h-full rounded-full transition-all ${
                          trend.current >= 90
                            ? "bg-green-500"
                            : trend.current >= 70
                              ? "bg-amber-500"
                              : "bg-red-500"
                        }`}
                        style={{ width: `${trend.current}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
