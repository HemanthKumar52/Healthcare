"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  LayoutGrid,
  Search,
  BarChart3,
  Package,
  KeyRound,
  ShieldCheck,
  Users,
  ClipboardList,
  Activity,
  Menu,
  X,
  LogOut,
} from "lucide-react";

const navigation = [
  {
    section: "Main",
    items: [
      { name: "Marketplace", href: "/marketplace", icon: LayoutGrid },
      { name: "Search", href: "/marketplace/search", icon: Search },
    ],
  },
  {
    section: "Dashboard",
    items: [
      { name: "Overview", href: "/consumer", icon: BarChart3 },
      { name: "My Products", href: "/steward", icon: Package },
      { name: "Access Requests", href: "/consumer/requests", icon: KeyRound },
      { name: "Quality Monitor", href: "/engineer/quality", icon: ShieldCheck },
    ],
  },
  {
    section: "Admin",
    items: [
      { name: "Users", href: "/admin/users", icon: Users },
      { name: "Audit Trail", href: "/admin/audit", icon: ClipboardList },
      { name: "System Health", href: "/admin", icon: Activity },
    ],
  },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const pathname = usePathname();

  const sidebarContent = (
    <div className="flex h-full flex-col">
      <div className="flex h-16 items-center gap-2 px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
          H
        </div>
        <span className="text-lg font-semibold tracking-tight">HDM</span>
      </div>

      <Separator />

      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {navigation.map((group) => (
          <div key={group.section} className="mb-4">
            <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              {group.section}
            </p>
            {group.items.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  <item.icon className="h-4 w-4 shrink-0" />
                  {item.name}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      <Separator />

      <div className="p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
            SA
          </div>
          <div className="flex-1 overflow-hidden">
            <p className="truncate text-sm font-medium">Sarah Adams</p>
            <Badge variant="secondary" className="mt-0.5 text-[10px]">
              Admin
            </Badge>
          </div>
        </div>
        <Link
          href="/login"
          className="mt-3 flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </Link>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar - mobile */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 transform border-r bg-card transition-transform duration-200 ease-in-out lg:hidden",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="absolute right-2 top-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
            <span className="sr-only">Close sidebar</span>
          </Button>
        </div>
        {sidebarContent}
      </aside>

      {/* Sidebar - desktop */}
      <aside className="hidden w-64 shrink-0 border-r bg-card lg:block">
        {sidebarContent}
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top bar for mobile */}
        <header className="flex h-14 items-center gap-4 border-b bg-card px-4 lg:hidden">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
            <span className="sr-only">Open sidebar</span>
          </Button>
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-xs">
              H
            </div>
            <span className="font-semibold">HDM</span>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
