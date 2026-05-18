import { z } from "zod";

export const NotificationType = z.enum([
  "ACCESS_APPROVED",
  "ACCESS_DENIED",
  "ACCESS_REQUESTED",
  "ACCESS_EXPIRING",
  "QUALITY_ALERT",
  "SLA_BREACH",
  "NEW_PRODUCT",
  "PRODUCT_UPDATED",
  "REVIEW_RECEIVED",
  "PIPELINE_FAILED",
]);
export type NotificationType = z.infer<typeof NotificationType>;

export const NotificationSchema = z.object({
  id: z.string().cuid2(),
  userId: z.string().cuid2(),
  type: NotificationType,
  title: z.string(),
  message: z.string(),
  linkUrl: z.string().nullable(),
  isRead: z.boolean(),
  createdAt: z.coerce.date(),
});
export type Notification = z.infer<typeof NotificationSchema>;
