import {
  Package,
  Clock,
  KeyRound,
  AlertTriangle,
  FileText,
  CheckCircle2,
  ShieldAlert,
  Eye,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StatsCard } from "@/components/dashboard/stats-card";

const approvedProducts = [
  {
    name: "Patient Visit Summary",
    domain: "Clinical",
    expiry: "2026-09-15",
    quality: 96,
  },
  {
    name: "Claims Analytics",
    domain: "Financial",
    expiry: "2026-08-01",
    quality: 91,
  },
  {
    name: "Bed Utilization Report",
    domain: "Operational",
    expiry: "2026-11-30",
    quality: 88,
  },
  {
    name: "De-identified Cohorts",
    domain: "Research",
    expiry: "2026-07-20",
    quality: 94,
  },
  {
    name: "Provider Directory",
    domain: "Provider",
    expiry: "2027-01-10",
    quality: 72,
  },
];

const recentActivity = [
  {
    id: 1,
    icon: CheckCircle2,
    color: "text-green-600",
    message: 'Access approved for "Lab Analytics" by Dr. Priya Mehta',
    time: "12 minutes ago",
  },
  {
    id: 2,
    icon: Eye,
    color: "text-blue-600",
    message: 'You viewed "Revenue Cycle Dashboard"',
    time: "1 hour ago",
  },
  {
    id: 3,
    icon: ShieldAlert,
    color: "text-amber-600",
    message: 'Quality alert: "Provider Directory" completeness dropped to 72%',
    time: "3 hours ago",
  },
  {
    id: 4,
    icon: FileText,
    color: "text-purple-600",
    message: 'You submitted access request for "Medication Summary"',
    time: "Yesterday",
  },
  {
    id: 5,
    icon: CheckCircle2,
    color: "text-green-600",
    message: 'Access approved for "Appointment Analytics" by Dr. James Wilson',
    time: "2 days ago",
  },
];

const domainVariant: Record<string, "clinical" | "financial" | "operational" | "research" | "provider"> = {
  Clinical: "clinical",
  Financial: "financial",
  Operational: "operational",
  Research: "research",
  Provider: "provider",
};

function getQualityColor(score: number) {
  if (score >= 90) return "text-green-600";
  if (score >= 70) return "text-amber-600";
  return "text-red-600";
}

export default function ConsumerDashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Consumer Dashboard</h1>
        <p className="mt-1 text-muted-foreground">
          Monitor your data products, requests, and quality alerts.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          icon={<Package className="h-5 w-5" />}
          label="My Data Products"
          value="5"
          trend={{ direction: "up", percentage: 25 }}
        />
        <StatsCard
          icon={<Clock className="h-5 w-5" />}
          label="Pending Requests"
          value="2"
        />
        <StatsCard
          icon={<KeyRound className="h-5 w-5" />}
          label="Active Access"
          value="5"
          trend={{ direction: "up", percentage: 12 }}
        />
        <StatsCard
          icon={<AlertTriangle className="h-5 w-5" />}
          label="Quality Alerts"
          value="1"
          trend={{ direction: "down", percentage: 50 }}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>My Approved Products</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left">
                    <th className="pb-3 font-medium text-muted-foreground">Product</th>
                    <th className="pb-3 font-medium text-muted-foreground">Domain</th>
                    <th className="pb-3 font-medium text-muted-foreground">Expiry</th>
                    <th className="pb-3 font-medium text-muted-foreground text-right">Quality</th>
                  </tr>
                </thead>
                <tbody>
                  {approvedProducts.map((product) => (
                    <tr key={product.name} className="border-b last:border-0">
                      <td className="py-3 font-medium">{product.name}</td>
                      <td className="py-3">
                        <Badge variant={domainVariant[product.domain]}>
                          {product.domain}
                        </Badge>
                      </td>
                      <td className="py-3 text-muted-foreground">{product.expiry}</td>
                      <td className={`py-3 text-right font-semibold ${getQualityColor(product.quality)}`}>
                        {product.quality}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex gap-3">
                  <activity.icon className={`mt-0.5 h-4 w-4 shrink-0 ${activity.color}`} />
                  <div className="space-y-1">
                    <p className="text-sm leading-snug">{activity.message}</p>
                    <p className="text-xs text-muted-foreground">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
