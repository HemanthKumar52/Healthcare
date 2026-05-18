"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

const DOMAINS = [
  { label: "All Domains", value: "" },
  { label: "Clinical", value: "CLINICAL" },
  { label: "Operational", value: "OPERATIONAL" },
  { label: "Financial", value: "FINANCIAL" },
  { label: "Provider", value: "PROVIDER" },
  { label: "Research", value: "RESEARCH" },
] as const;

const SENSITIVITIES = [
  { label: "All Sensitivity", value: "" },
  { label: "PHI", value: "PHI" },
  { label: "No PHI", value: "NO_PHI" },
  { label: "Restricted", value: "RESTRICTED" },
] as const;

export function SearchBar() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [query, setQuery] = useState(searchParams.get("q") ?? "");
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const updateParams = useCallback(
    (updates: Record<string, string>) => {
      const params = new URLSearchParams(searchParams.toString());
      for (const [key, value] of Object.entries(updates)) {
        if (value) {
          params.set(key, value);
        } else {
          params.delete(key);
        }
      }
      router.push(`/marketplace?${params.toString()}`);
    },
    [router, searchParams]
  );

  const handleQueryChange = (value: string) => {
    setQuery(value);
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }
    debounceTimer.current = setTimeout(() => {
      updateParams({ q: value });
    }, 300);
  };

  useEffect(() => {
    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, []);

  const currentDomain = searchParams.get("domain") ?? "";
  const currentSensitivity = searchParams.get("sensitivity") ?? "";

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
      <div className="relative flex-1">
        <svg
          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.3-4.3" />
        </svg>
        <Input
          type="search"
          placeholder="Search data products..."
          value={query}
          onChange={(e) => handleQueryChange(e.target.value)}
          className="pl-9"
        />
      </div>
      <select
        value={currentDomain}
        onChange={(e) => updateParams({ domain: e.target.value })}
        className={cn(
          "h-10 rounded-md border border-input bg-background px-3 text-sm ring-offset-background",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
        )}
      >
        {DOMAINS.map((d) => (
          <option key={d.value} value={d.value}>
            {d.label}
          </option>
        ))}
      </select>
      <select
        value={currentSensitivity}
        onChange={(e) => updateParams({ sensitivity: e.target.value })}
        className={cn(
          "h-10 rounded-md border border-input bg-background px-3 text-sm ring-offset-background",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
        )}
      >
        {SENSITIVITIES.map((s) => (
          <option key={s.value} value={s.value}>
            {s.label}
          </option>
        ))}
      </select>
    </div>
  );
}
