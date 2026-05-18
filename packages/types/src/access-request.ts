import { z } from "zod";

export const AccessRequestStatus = z.enum([
  "PENDING",
  "APPROVED",
  "DENIED",
  "REVOKED",
  "EXPIRED",
]);
export type AccessRequestStatus = z.infer<typeof AccessRequestStatus>;

export const AccessRequestSchema = z.object({
  id: z.string().cuid2(),
  requesterId: z.string().cuid2(),
  productId: z.string().cuid2(),
  justification: z.string().min(10),
  status: AccessRequestStatus,
  approvedById: z.string().cuid2().nullable(),
  grantedAt: z.coerce.date().nullable(),
  expiresAt: z.coerce.date().nullable(),
  denialReason: z.string().nullable(),
  createdAt: z.coerce.date(),
  updatedAt: z.coerce.date(),
});
export type AccessRequest = z.infer<typeof AccessRequestSchema>;

export const CreateAccessRequestSchema = z.object({
  productId: z.string().cuid2(),
  justification: z.string().min(10, "Justification must be at least 10 characters"),
  expiresAt: z.coerce.date().optional(),
});
export type CreateAccessRequest = z.infer<typeof CreateAccessRequestSchema>;

export const ReviewAccessRequestSchema = z.object({
  status: z.enum(["APPROVED", "DENIED"]),
  denialReason: z.string().optional(),
  expiresAt: z.coerce.date().optional(),
});
export type ReviewAccessRequest = z.infer<typeof ReviewAccessRequestSchema>;
