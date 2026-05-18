import { cn } from "@/lib/utils";

interface QualityMetricsProps {
  completeness: number;
  uniqueness: number;
  freshness: number;
  referentialIntegrity: number;
  valueRange: number;
  className?: string;
}

const metricLabels: { key: keyof Omit<QualityMetricsProps, "className">; label: string }[] = [
  { key: "completeness", label: "Completeness" },
  { key: "uniqueness", label: "Uniqueness" },
  { key: "freshness", label: "Freshness" },
  { key: "referentialIntegrity", label: "Referential Integrity" },
  { key: "valueRange", label: "Value Range" },
];

function getBarColor(value: number): string {
  if (value >= 90) return "bg-green-500";
  if (value >= 70) return "bg-yellow-500";
  return "bg-red-500";
}

export function QualityMetrics(props: QualityMetricsProps) {
  return (
    <div className={cn("space-y-4", props.className)}>
      {metricLabels.map(({ key, label }) => {
        const value = props[key];
        return (
          <div key={key}>
            <div className="mb-1.5 flex items-center justify-between text-sm">
              <span className="font-medium">{label}</span>
              <span className="tabular-nums text-muted-foreground">
                {value.toFixed(1)}%
              </span>
            </div>
            <div className="h-2.5 w-full overflow-hidden rounded-full bg-secondary">
              <div
                className={cn(
                  "h-full rounded-full transition-all duration-500 ease-out",
                  getBarColor(value)
                )}
                style={{ width: `${Math.min(value, 100)}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
