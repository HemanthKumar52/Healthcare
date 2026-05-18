import { z } from "zod";

export const QualityMetric = z.enum([
  "COMPLETENESS",
  "UNIQUENESS",
  "FRESHNESS",
  "REFERENTIAL_INTEGRITY",
  "VALUE_RANGE",
]);
export type QualityMetric = z.infer<typeof QualityMetric>;

export const SLAOperator = z.enum(["GTE", "LTE"]);
export type SLAOperator = z.infer<typeof SLAOperator>;

export const QualityScoreSchema = z.object({
  id: z.string().cuid2(),
  productId: z.string().cuid2(),
  completeness: z.number().min(0).max(100),
  uniqueness: z.number().min(0).max(100),
  freshness: z.number().min(0).max(100),
  referentialIntegrity: z.number().min(0).max(100),
  valueRange: z.number().min(0).max(100),
  overallScore: z.number().min(0).max(100),
  checkedAt: z.coerce.date(),
});
export type QualityScore = z.infer<typeof QualityScoreSchema>;

export const QualitySLASchema = z.object({
  id: z.string().cuid2(),
  productId: z.string().cuid2(),
  metric: QualityMetric,
  threshold: z.number().min(0).max(100),
  operator: SLAOperator,
  isBreached: z.boolean(),
  lastCheckedAt: z.coerce.date(),
});
export type QualitySLA = z.infer<typeof QualitySLASchema>;

export const CreateQualitySLASchema = z.object({
  productId: z.string().cuid2(),
  metric: QualityMetric,
  threshold: z.number().min(0).max(100),
  operator: SLAOperator,
});
export type CreateQualitySLA = z.infer<typeof CreateQualitySLASchema>;
