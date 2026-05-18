import { z } from "zod";

export const LineageNodeType = z.enum(["SOURCE", "TRANSFORM", "TARGET"]);
export type LineageNodeType = z.infer<typeof LineageNodeType>;

export const LineageNodeSchema = z.object({
  id: z.string().cuid2(),
  productId: z.string().cuid2(),
  nodeType: LineageNodeType,
  name: z.string(),
  description: z.string().nullable(),
  metadata: z.record(z.unknown()).nullable(),
});
export type LineageNode = z.infer<typeof LineageNodeSchema>;

export const LineageEdgeSchema = z.object({
  id: z.string().cuid2(),
  sourceNodeId: z.string().cuid2(),
  targetNodeId: z.string().cuid2(),
  transformDescription: z.string().nullable(),
});
export type LineageEdge = z.infer<typeof LineageEdgeSchema>;
