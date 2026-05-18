"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { cn } from "@/lib/utils";

const DOMAINS = [
  { label: "All", value: "" },
  { label: "Clinical", value: "CLINICAL" },
  { label: "Operational", value: "OPERATIONAL" },
  { label: "Financial", value: "FINANCIAL" },
  { label: "Provider", value: "PROVIDER" },
  { label: "Research", value: "RESEARCH" },
] as const;

export function DomainFilter() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const activeDomain = searchParams.get("domain") ?? "";

  function handleSelect(value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (value) {
      params.set("domain", value);
    } else {
      params.delete("domain");
    }
    router.push(`/marketplace?${params.toString()}`);
  }

  return (
    <div className="flex flex-wrap gap-2" role="tablist" aria-label="Filter by domain">
      {DOMAINS.map((domain) => {
        const isActive = activeDomain === domain.value;
        return (
          <button
            key={domain.value}
            role="tab"
            aria-selected={isActive}
            onClick={() => handleSelect(domain.value)}
            className={cn(
              "rounded-full px-4 py-1.5 text-sm font-medium transition-colors",
              isActive
                ? "bg-primary text-primary-foreground shadow-sm"
                : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
            )}
          >
            {domain.label}
          </button>
        );
      })}
    </div>
  );
}
