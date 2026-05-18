import { z } from "zod";

export const AuditAction = z.enum([
  "PRODUCT_CREATED",
  "PRODUCT_UPDATED",
  "PRODUCT_DEPRECATED",
  "ACCESS_REQUESTED",
  "ACCESS_APPROVED",
  "ACCESS_DENIED",
  "ACCESS_REVOKED",
  "ACCESS_EXPIRED",
  "QUALITY_CHECK_RAN",
  "SLA_BREACHED",
  "USER_LOGIN",
  "USER_LOGOUT",
  "REVIEW_SUBMITTED",
  "DATA_EXPORTED",
  "PIPELINE_EXECUTED",
]);
export type AuditAction = z.infer<typeof AuditAction>;

export const AuditLogSchema = z.object({
  id: z.string().cuid2(),
  actorId: z.string().cuid2(),
  action: AuditAction,
  targetType: z.string(),
  targetId: z.string(),
  metadata: z.record(z.unknown()).nullable(),
  ipAddress: z.string().nullable(),
  timestamp: z.coerce.date(),
});
export type AuditLog = z.infer<typeof AuditLogSchema>;

export const AuditFilterSchema = z.object({
  actorId: z.string().optional(),
  action: AuditAction.optional(),
  targetType: z.string().optional(),
  targetId: z.string().optional(),
  from: z.coerce.date().optional(),
  to: z.coerce.date().optional(),
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(50),
});
export type AuditFilter = z.infer<typeof AuditFilterSchema>;
