import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@hdm/db";
import { CreateReviewSchema } from "@hdm/types";
import { auth } from "@/lib/auth";
import { z } from "zod";

const ListParamsSchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(20),
});

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ productId: string }> }
) {
  try {
    const { productId } = await params;

    const product = await prisma.dataProduct.findUnique({
      where: { id: productId },
      select: { id: true },
    });
    if (!product) {
      return NextResponse.json({ error: "Product not found" }, { status: 404 });
    }

    const searchParams = Object.fromEntries(request.nextUrl.searchParams);
    const filter = ListParamsSchema.parse(searchParams);
    const skip = (filter.page - 1) * filter.limit;

    const [reviews, total, avgRating] = await Promise.all([
      prisma.review.findMany({
        where: { productId },
        skip,
        take: filter.limit,
        orderBy: { createdAt: "desc" },
        include: {
          user: { select: { id: true, name: true, avatar: true } },
        },
      }),
      prisma.review.count({ where: { productId } }),
      prisma.review.aggregate({
        where: { productId },
        _avg: { rating: true },
      }),
    ]);

    return NextResponse.json({
      data: reviews,
      averageRating: avgRating._avg.rating ?? null,
      pagination: {
        page: filter.page,
        limit: filter.limit,
        total,
        totalPages: Math.ceil(total / filter.limit),
      },
    });
  } catch (error) {
    console.error("GET /api/reviews/[productId] error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ productId: string }> }
) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { productId } = await params;

    const product = await prisma.dataProduct.findUnique({
      where: { id: productId },
      select: { id: true },
    });
    if (!product) {
      return NextResponse.json({ error: "Product not found" }, { status: 404 });
    }

    const body = await request.json();
    // Override productId from URL param
    const data = CreateReviewSchema.parse({ ...body, productId });

    // Check if user already reviewed this product
    const existingReview = await prisma.review.findUnique({
      where: {
        userId_productId: {
          userId: session.user.id,
          productId,
        },
      },
    });
    if (existingReview) {
      return NextResponse.json({ error: "You have already reviewed this product" }, { status: 409 });
    }

    const review = await prisma.review.create({
      data: {
        userId: session.user.id,
        productId,
        rating: data.rating,
        comment: data.comment,
      },
      include: {
        user: { select: { id: true, name: true, avatar: true } },
      },
    });

    return NextResponse.json({ data: review }, { status: 201 });
  } catch (error) {
    if (error instanceof Error && error.name === "ZodError") {
      return NextResponse.json({ error: "Validation failed", details: error }, { status: 400 });
    }
    console.error("POST /api/reviews/[productId] error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
