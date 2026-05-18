import Link from "next/link";
import type { DataProduct, Domain, Sensitivity } from "@hdm/types";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn, formatNumber, formatRelativeTime, getQualityColor } from "@/lib/utils";

type BadgeVariant =
  | "clinical"
  | "operational"
  | "financial"
  | "provider"
  | "research";

const domainVariantMap: Record<Domain, BadgeVariant> = {
  CLINICAL: "clinical",
  OPERATIONAL: "operational",
  FINANCIAL: "financial",
  PROVIDER: "provider",
  RESEARCH: "research",
};

const sensitivityVariantMap: Record<Sensitivity, "phi" | "noPhi" | "restricted"> = {
  PHI: "phi",
  NO_PHI: "noPhi",
  RESTRICTED: "restricted",
};

const sensitivityLabel: Record<Sensitivity, string> = {
  PHI: "PHI",
  NO_PHI: "No PHI",
  RESTRICTED: "Restricted",
};

interface ProductCardProps {
  product: Pick<
    DataProduct,
    | "name"
    | "slug"
    | "description"
    | "domain"
    | "sensitivity"
    | "recordCount"
    | "lastRefreshedAt"
  > & {
    qualityScore: number;
    ownerName: string;
  };
}

export function ProductCard({ product }: ProductCardProps) {
  const qualityColorClass = getQualityColor(product.qualityScore);

  return (
    <Link href={`/marketplace/${product.slug}`} className="group block">
      <Card className="h-full transition-shadow duration-200 group-hover:shadow-md">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <h3 className="text-base font-semibold leading-tight group-hover:text-primary">
              {product.name}
            </h3>
            <div
              className={cn(
                "flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold",
                qualityColorClass,
                product.qualityScore >= 90
                  ? "bg-green-100"
                  : product.qualityScore >= 70
                    ? "bg-yellow-100"
                    : "bg-red-100"
              )}
              title={`Quality score: ${product.qualityScore}%`}
            >
              {product.qualityScore}
            </div>
          </div>
          <div className="flex flex-wrap gap-1.5 pt-1">
            <Badge variant={domainVariantMap[product.domain]}>
              {product.domain.charAt(0) + product.domain.slice(1).toLowerCase()}
            </Badge>
            <Badge variant={sensitivityVariantMap[product.sensitivity]}>
              {sensitivityLabel[product.sensitivity]}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <p className="line-clamp-2 text-sm text-muted-foreground">
            {product.description}
          </p>
          <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
            <span>
              {product.recordCount != null
                ? `${formatNumber(product.recordCount)} records`
                : "N/A"}
            </span>
            <span>
              {product.lastRefreshedAt
                ? formatRelativeTime(new Date(product.lastRefreshedAt))
                : "Never refreshed"}
            </span>
          </div>
          <div className="mt-2 text-xs text-muted-foreground">
            Owner: <span className="font-medium text-foreground">{product.ownerName}</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
