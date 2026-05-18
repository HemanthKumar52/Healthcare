import { z } from "zod";

export const UserRole = z.enum([
  "CONSUMER",
  "STEWARD",
  "ADMIN",
  "ENGINEER",
]);
export type UserRole = z.infer<typeof UserRole>;

export const UserSchema = z.object({
  id: z.string().cuid2(),
  name: z.string().min(1),
  email: z.string().email(),
  role: UserRole,
  department: z.string().nullable(),
  avatar: z.string().url().nullable(),
  createdAt: z.coerce.date(),
  updatedAt: z.coerce.date(),
});
export type User = z.infer<typeof UserSchema>;

export const CreateUserSchema = UserSchema.pick({
  name: true,
  email: true,
  role: true,
  department: true,
});
export type CreateUser = z.infer<typeof CreateUserSchema>;
