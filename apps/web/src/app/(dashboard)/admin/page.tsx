import {
  Package,
  Users,
  KeyRound,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  AlertTriangle,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StatsCard } from "@/components/dashboard/stats-card";

const auditEntries = [
  {
    id: 1,
    timestamp: "2026-05-18 09:42:11",
    actor: "Sarah Adams",
    action: "USER_LOGIN",
    target: "Session #s8k2m",
  },
  {
    id: 2,
    timestamp: "2026-05-18 09:38:05",
    actor: "Dr. Priya Mehta",
    action: "ACCESS_APPROVED",
    target: "Lab Analytics",
  },
  {
    id: 3,
    timestamp: "2026-05-18 09:15:33",
    actor: "System",
    action: "QUALITY_CHECK_RAN",
    target: "Patient Visit Summary",
  },
  {
    id: 4,
    timestamp: "2026-05-18 08:52:19",
    actor: "Dr. Emily Chen",
    action: "ACCESS_REQUESTED",
    target: "Patient Visit Summary",
  },
  {
    id: 5,
    timestamp: "2026-05-18 08:30:00",
    actor: "System",
    action: "SLA_BREACHED",
    target: "Provider Directory",
  },
  {
    id: 6,
    timestamp: "2026-05-17 17:12:44",
    actor: "Kevin Park",
    action: "PIPELINE_EXECUTED",
    target: "Claims Analytics Pipeline",
  },
  {
    id: 7,
    timestamp: "2026-05-17 16:45:02",
    actor: "Dr. James Wilson",
    action: "PRODUCT_UPDATED",
    target: "Bed Utilization Report",
  },
  {
    id: 8,
    timestamp: "2026-05-17 15:20:18",
    actor: "Mark Thompson",
    action: "DATA_EXPORTED",
    target: "Revenue Cycle Dashboard",
  },
];

const pipelineStatuses = [
  { name: "Clinical Ingestion", status: "healthy", lastRun: "6 min ago" },
  { name: "Financial Curation", status: "healthy", lastRun: "12 min ago" },
  { name: "Quality Engine", status: "healthy", lastRun: "18 min ago" },
  { name: "Search Indexer", status: "warning", lastRun: "45 min ago" },
  { name: "PHI Scanner", status: "healthy", lastRun: "1 hour ago" },
  { name: "Provider Sync", status: "error", lastRun: "3 hours ago" },
];

const actionBadgeVariant: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  USER_LOGIN: "secondary",
  ACCESS_APPROVED: "default",
  QUALITY_CHECK_RAN: "secondary",
  ACCESS_REQUESTED: "outline",
  SLA_BREACHED: "destructive",
  PIPELINE_EXECUTED: "secondary",
  PRODUCT_UPDATED: "outline",
  DATA_EXPORTED: "outline",
};

function StatusIndicator({ status }: { status: string }) {
  if (status === "healthy") {
    return <CheckCircle2 className="h-4 w-4 text-green-500" />;
  }
  if (status === "warning") {
    return <AlertTriangle className="h-4 w-4 text-amber-500" />;
  }
  return <XCircle className="h-4 w-4 text-red-500" />;
}

export default function AdminDashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Admin Dashboard</h1>
        <p className="mt-1 text-muted-foreground">
          Platform overview, audit trail, and system health monitoring.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          icon={<Package className="h-5 w-5" />}
          label="Total Products"
          value="10"
          trend={{ direction: "up", percentage: 11 }}
        />
        <StatsCard
          icon={<Users className="h-5 w-5" />}
          label="Total Users"
          value="6"
          trend={{ direction: "up", percentage: 20 }}
        />
        <StatsCard
          icon={<KeyRound className="h-5 w-5" />}
          label="Access Requests Today"
          value="3"
        />
        <StatsCard
          icon={<ShieldAlert className="h-5 w-5" />}
          label="SLA Breaches"
          value="2"
          trend={{ direction: "down", percentage: 33 }}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Recent Audit Trail</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left">
                    <th className="pb-3 font-medium text-muted-foreground">Timestamp</th>
                    <th className="pb-3 font-medium text-muted-foreground">Actor</th>
                    <th className="pb-3 font-medium text-muted-foreground">Action</th>
                    <th className="pb-3 font-medium text-muted-foreground">Target</th>
                  </tr>
                </thead>
                <tbody>
                  {auditEntries.map((entry) => (
                    <tr key={entry.id} className="border-b last:border-0">
                      <td className="py-3 font-mono text-xs text-muted-foreground whitespace-nowrap">
                        {entry.timestamp}
                      </td>
                      <td className="py-3">{entry.actor}</td>
                      <td className="py-3">
                        <Badge variant={actionBadgeVariant[entry.action] ?? "secondary"}>
                          {entry.action.replace(/_/g, " ")}
                        </Badge>
                      </td>
                      <td className="py-3 text-muted-foreground">{entry.target}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Health</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {pipelineStatuses.map((pipeline) => (
                <div
                  key={pipeline.name}
                  className="flex items-center justify-between rounded-lg border p-3"
                >
                  <div className="flex items-center gap-3">
                    <StatusIndicator status={pipeline.status} />
                    <div>
                      <p className="text-sm font-medium">{pipeline.name}</p>
                      <p className="text-xs text-muted-foreground">
                        Last run: {pipeline.lastRun}
                      </p>
                    </div>
                  </div>
                  <Badge
                    variant={
                      pipeline.status === "healthy"
                        ? "default"
                        : pipeline.status === "warning"
                          ? "outline"
                          : "destructive"
                    }
                  >
                    {pipeline.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
