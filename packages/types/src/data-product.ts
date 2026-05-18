import { z } from "zod";

export const Domain = z.enum([
  "CLINICAL",
  "OPERATIONAL",
  "FINANCIAL",
  "PROVIDER",
  "RESEARCH",
]);
export type Domain = z.infer<typeof Domain>;

export const Sensitivity = z.enum(["PHI", "NO_PHI", "RESTRICTED"]);
export type Sensitivity = z.infer<typeof Sensitivity>;

export const ProductStatus = z.enum(["DRAFT", "PUBLISHED", "DEPRECATED"]);
export type ProductStatus = z.infer<typeof ProductStatus>;

export const DataProductSchema = z.object({
  id: z.string().cuid2(),
  name: z.string().min(1).max(200),
  slug: z.string().regex(/^[a-z0-9-]+$/),
  description: z.string().min(1),
  domain: Domain,
  sensitivity: Sensitivity,
  status: ProductStatus,
  version: z.string().default("1.0.0"),
  ownerId: z.string().cuid2(),
  stewardId: z.string().cuid2(),
  catalogName: z.string(),
  schemaName: z.string(),
  tableName: z.string(),
  refreshCadence: z.string().nullable(),
  lastRefreshedAt: z.coerce.date().nullable(),
  recordCount: z.number().int().nonnegative().nullable(),
  sizeBytes: z.number().int().nonnegative().nullable(),
  createdAt: z.coerce.date(),
  updatedAt: z.coerce.date(),
});
export type DataProduct = z.infer<typeof DataProductSchema>;

export const CreateDataProductSchema = DataProductSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type CreateDataProduct = z.infer<typeof CreateDataProductSchema>;

export const UpdateDataProductSchema = CreateDataProductSchema.partial();
export type UpdateDataProduct = z.infer<typeof UpdateDataProductSchema>;

export const DataProductFilterSchema = z.object({
  domain: Domain.optional(),
  sensitivity: Sensitivity.optional(),
  status: ProductStatus.optional(),
  ownerId: z.string().optional(),
  search: z.string().optional(),
  minQuality: z.coerce.number().min(0).max(100).optional(),
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(20),
});
export type DataProductFilter = z.infer<typeof DataProductFilterSchema>;

export const DataProductTagSchema = z.object({
  id: z.string().cuid2(),
  productId: z.string().cuid2(),
  key: z.string().min(1),
  value: z.string().min(1),
});
export type DataProductTag = z.infer<typeof DataProductTagSchema>;
