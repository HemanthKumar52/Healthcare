"use client";

import { useState } from "react";
import { Bell, Check, CheckCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { formatRelativeTime } from "@/lib/utils";

interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  isRead: boolean;
  createdAt: string;
  linkUrl?: string;
}

const mockNotifications: Notification[] = [
  {
    id: "1",
    type: "ACCESS_APPROVED",
    title: "Access Approved",
    message: "Your request for Patient Visit Summary has been approved.",
    isRead: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    linkUrl: "/marketplace/patient-visit-summary",
  },
  {
    id: "2",
    type: "SLA_BREACH",
    title: "SLA Breach Alert",
    message: "Claims Analytics freshness SLA breached. Last refresh: 28 hours ago.",
    isRead: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    linkUrl: "/marketplace/claims-analytics",
  },
  {
    id: "3",
    type: "NEW_PRODUCT",
    title: "New Data Product",
    message: "Population Health Cohorts v2.0 has been published in the Research domain.",
    isRead: true,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    linkUrl: "/marketplace/population-health-cohorts",
  },
  {
    id: "4",
    type: "QUALITY_ALERT",
    title: "Quality Score Drop",
    message: "Lab Results Analytics completeness dropped to 87% (below 95% SLA).",
    isRead: true,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
  },
];

const typeIcons: Record<string, string> = {
  ACCESS_APPROVED: "text-green-600 bg-green-50",
  ACCESS_DENIED: "text-red-600 bg-red-50",
  ACCESS_REQUESTED: "text-blue-600 bg-blue-50",
  SLA_BREACH: "text-red-600 bg-red-50",
  QUALITY_ALERT: "text-amber-600 bg-amber-50",
  NEW_PRODUCT: "text-purple-600 bg-purple-50",
  REVIEW_RECEIVED: "text-blue-600 bg-blue-50",
  PIPELINE_FAILED: "text-red-600 bg-red-50",
};

export function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState(mockNotifications);

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  const markAsRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, isRead: true } : n))
    );
  };

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, isRead: true })));
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-md hover:bg-secondary transition"
      >
        <Bell className="h-5 w-5 text-muted-foreground" />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 h-4 w-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 top-12 z-50 w-96 bg-white border rounded-lg shadow-xl">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="font-semibold">Notifications</h3>
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-xs text-primary hover:underline flex items-center gap-1"
                >
                  <CheckCheck className="h-3 w-3" />
                  Mark all read
                </button>
              )}
            </div>
            <div className="max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-8 text-center text-sm text-muted-foreground">
                  No notifications
                </div>
              ) : (
                notifications.map((notif) => (
                  <div
                    key={notif.id}
                    className={`p-4 border-b last:border-b-0 hover:bg-gray-50 transition cursor-pointer ${
                      !notif.isRead ? "bg-blue-50/50" : ""
                    }`}
                    onClick={() => markAsRead(notif.id)}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                          typeIcons[notif.type] ?? "text-gray-600 bg-gray-50"
                        }`}
                      >
                        <Bell className="h-3.5 w-3.5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">{notif.title}</span>
                          {!notif.isRead && (
                            <div className="w-2 h-2 bg-blue-500 rounded-full shrink-0" />
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                          {notif.message}
                        </p>
                        <span className="text-xs text-muted-foreground mt-1 block">
                          {formatRelativeTime(new Date(notif.createdAt))}
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
