import {
  Package,
  ClipboardCheck,
  BarChart3,
  Users,
  AlertTriangle,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { StatsCard } from "@/components/dashboard/stats-card";

const pendingRequests = [
  {
    id: "req-001",
    requester: "Dr. Emily Chen",
    product: "Patient Visit Summary",
    department: "Clinical Research",
    requestedAt: "2026-05-16",
    justification: "Need access to patient visit data for readmission analysis study approved by IRB #2026-0412.",
  },
  {
    id: "req-002",
    requester: "Mark Thompson",
    product: "Claims Analytics",
    department: "Revenue Cycle",
    requestedAt: "2026-05-17",
    justification: "Quarterly financial reconciliation requires claims data for FY2026 Q2 close.",
  },
  {
    id: "req-003",
    requester: "Lisa Nguyen",
    product: "Lab Analytics",
    department: "Quality Improvement",
    requestedAt: "2026-05-17",
    justification: "Tracking turnaround times for critical lab results as part of Joint Commission preparation.",
  },
  {
    id: "req-004",
    requester: "Robert Garcia",
    product: "Medication Summary",
    department: "Pharmacy",
    requestedAt: "2026-05-18",
    justification: "Polypharmacy analysis for patients aged 65+ as directed by Chief Pharmacy Officer.",
  },
];

const qualityAlerts = [
  {
    id: 1,
    product: "Provider Directory",
    metric: "Completeness",
    current: 72,
    threshold: 90,
    severity: "high" as const,
  },
  {
    id: 2,
    product: "Bed Utilization Report",
    metric: "Freshness",
    current: 26,
    threshold: 24,
    severity: "medium" as const,
  },
  {
    id: 3,
    product: "Revenue Cycle Dashboard",
    metric: "Referential Integrity",
    current: 87,
    threshold: 95,
    severity: "high" as const,
  },
];

const severityStyles = {
  high: "border-red-200 bg-red-50 text-red-800",
  medium: "border-amber-200 bg-amber-50 text-amber-800",
};

export default function StewardDashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Steward Dashboard</h1>
        <p className="mt-1 text-muted-foreground">
          Manage data products, approve requests, and monitor quality.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          icon={<Package className="h-5 w-5" />}
          label="Managed Products"
          value="10"
          trend={{ direction: "up", percentage: 11 }}
        />
        <StatsCard
          icon={<ClipboardCheck className="h-5 w-5" />}
          label="Pending Approvals"
          value="4"
          trend={{ direction: "up", percentage: 33 }}
        />
        <StatsCard
          icon={<BarChart3 className="h-5 w-5" />}
          label="Avg Quality Score"
          value="91.4%"
          trend={{ direction: "up", percentage: 2 }}
        />
        <StatsCard
          icon={<Users className="h-5 w-5" />}
          label="Active Users"
          value="24"
          trend={{ direction: "up", percentage: 8 }}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Pending Access Requests</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {pendingRequests.map((request) => (
                <div
                  key={request.id}
                  className="rounded-lg border p-4"
                >
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div className="space-y-1">
                      <p className="font-medium">{request.requester}</p>
                      <p className="text-sm text-muted-foreground">
                        {request.department} &middot; Requested {request.requestedAt}
                      </p>
                    </div>
                    <Badge variant="outline">{request.product}</Badge>
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {request.justification}
                  </p>
                  <div className="mt-3 flex gap-2">
                    <Button size="sm">Approve</Button>
                    <Button size="sm" variant="outline">
                      Deny
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-amber-500" />
              Quality Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {qualityAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`rounded-lg border p-3 ${severityStyles[alert.severity]}`}
                >
                  <p className="font-medium">{alert.product}</p>
                  <p className="mt-1 text-sm">
                    <span className="font-semibold">{alert.metric}</span>: {alert.current}
                    {alert.metric === "Freshness" ? "h" : "%"} (threshold:{" "}
                    {alert.metric === "Freshness"
                      ? `${alert.threshold}h max`
                      : `${alert.threshold}% min`}
                    )
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
