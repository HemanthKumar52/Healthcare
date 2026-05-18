import { z } from "zod";

export const ColumnProfileSchema = z.object({
  id: z.string().cuid2(),
  productId: z.string().cuid2(),
  columnName: z.string(),
  dataType: z.string(),
  nullPercentage: z.number().min(0).max(100),
  distinctCount: z.number().int().nonnegative(),
  minValue: z.string().nullable(),
  maxValue: z.string().nullable(),
  meanValue: z.number().nullable(),
  sampleValues: z.array(z.string()).nullable(),
});
export type ColumnProfile = z.infer<typeof ColumnProfileSchema>;

export const UsageMetricAction = z.enum(["VIEW", "DOWNLOAD", "QUERY", "API_ACCESS"]);
export type UsageMetricAction = z.infer<typeof UsageMetricAction>;

export const UsageMetricSchema = z.object({
  id: z.string().cuid2(),
  productId: z.string().cuid2(),
  userId: z.string().cuid2(),
  action: UsageMetricAction,
  timestamp: z.coerce.date(),
});
export type UsageMetric = z.infer<typeof UsageMetricSchema>;
