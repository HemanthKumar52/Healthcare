import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(n: number): string {
  return new Intl.NumberFormat("en-US").format(n);
}

export function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 30) return `${days}d ago`;
  return date.toLocaleDateString();
}

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

export function getQualityColor(score: number): string {
  if (score >= 90) return "text-green-600";
  if (score >= 70) return "text-yellow-600";
  return "text-red-600";
}

export function getQualityBadge(score: number): string {
  if (score >= 90) return "Excellent";
  if (score >= 70) return "Good";
  if (score >= 50) return "Fair";
  return "Poor";
}

export function getDomainColor(domain: string): string {
  const colors: Record<string, string> = {
    CLINICAL: "bg-blue-100 text-blue-800",
    OPERATIONAL: "bg-green-100 text-green-800",
    FINANCIAL: "bg-amber-100 text-amber-800",
    PROVIDER: "bg-purple-100 text-purple-800",
    RESEARCH: "bg-red-100 text-red-800",
  };
  return colors[domain] ?? "bg-gray-100 text-gray-800";
}

export function getSensitivityBadge(sensitivity: string): string {
  const badges: Record<string, string> = {
    PHI: "bg-red-100 text-red-800 border-red-200",
    NO_PHI: "bg-green-100 text-green-800 border-green-200",
    RESTRICTED: "bg-yellow-100 text-yellow-800 border-yellow-200",
  };
  return badges[sensitivity] ?? "bg-gray-100 text-gray-800";
}
