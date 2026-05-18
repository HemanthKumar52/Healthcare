import { z } from "zod";

export const ReviewSchema = z.object({
  id: z.string().cuid2(),
  userId: z.string().cuid2(),
  productId: z.string().cuid2(),
  rating: z.number().int().min(1).max(5),
  comment: z.string().min(1).max(1000),
  createdAt: z.coerce.date(),
});
export type Review = z.infer<typeof ReviewSchema>;

export const CreateReviewSchema = z.object({
  productId: z.string().cuid2(),
  rating: z.number().int().min(1).max(5),
  comment: z.string().min(1).max(1000),
});
export type CreateReview = z.infer<typeof CreateReviewSchema>;
