import { NextRequest, NextResponse } from "next/server";
import { prisma, Prisma } from "@hdm/db";
import { z } from "zod";

const SearchParamsSchema = z.object({
  q: z.string().optional(),
  domain: z.enum(["CLINICAL", "OPERATIONAL", "FINANCIAL", "PROVIDER", "RESEARCH"]).optional(),
  sensitivity: z.enum(["PHI", "NO_PHI", "RESTRICTED"]).optional(),
  minQuality: z.coerce.number().min(0).max(100).optional(),
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(20),
});

export async function GET(request: NextRequest) {
  try {
    const params = Object.fromEntries(request.nextUrl.searchParams);
    const filter = SearchParamsSchema.parse(params);

    const where: Prisma.DataProductWhereInput = {
      status: "PUBLISHED",
    };

    if (filter.q) {
      where.OR = [
        { name: { contains: filter.q, mode: "insensitive" } },
        { description: { contains: filter.q, mode: "insensitive" } },
        { tags: { some: { value: { contains: filter.q, mode: "insensitive" } } } },
      ];
    }

    if (filter.domain) {
      where.domain = filter.domain;
    }

    if (filter.sensitivity) {
      where.sensitivity = filter.sensitivity;
    }

    if (filter.minQuality !== undefined) {
      where.qualityScores = {
        some: {
          overallScore: { gte: filter.minQuality },
        },
      };
    }

    const skip = (filter.page - 1) * filter.limit;

    const [products, total] = await Promise.all([
      prisma.dataProduct.findMany({
        where,
        skip,
        take: filter.limit,
        orderBy: { createdAt: "desc" },
        include: {
          owner: { select: { id: true, name: true, avatar: true } },
          steward: { select: { id: true, name: true, avatar: true } },
          tags: true,
          qualityScores: {
            orderBy: { checkedAt: "desc" },
            take: 1,
          },
          _count: {
            select: { reviews: true },
          },
        },
      }),
      prisma.dataProduct.count({ where }),
    ]);

    // Compute average ratings for found products
    const productIds = products.map((p) => p.id);
    const ratings = await prisma.review.groupBy({
      by: ["productId"],
      where: { productId: { in: productIds } },
      _avg: { rating: true },
    });
    const ratingMap = new Map(ratings.map((r) => [r.productId, r._avg.rating]));

    const results = products.map((p) => ({
      ...p,
      averageRating: ratingMap.get(p.id) ?? null,
    }));

    return NextResponse.json({
      data: results,
      pagination: {
        page: filter.page,
        limit: filter.limit,
        total,
        totalPages: Math.ceil(total / filter.limit),
      },
    });
  } catch (error) {
    if (error instanceof Error && error.name === "ZodError") {
      return NextResponse.json({ error: "Invalid search parameters", details: error }, { status: 400 });
    }
    console.error("GET /api/search error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
