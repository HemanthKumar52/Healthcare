import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@hdm/db";
import { UpdateDataProductSchema } from "@hdm/types";
import { auth } from "@/lib/auth";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  try {
    const { slug } = await params;

    const product = await prisma.dataProduct.findUnique({
      where: { slug },
      include: {
        owner: { select: { id: true, name: true, email: true, avatar: true, role: true } },
        steward: { select: { id: true, name: true, email: true, avatar: true, role: true } },
        tags: true,
        qualityScores: {
          orderBy: { checkedAt: "desc" },
          take: 1,
        },
        reviews: {
          include: {
            user: { select: { id: true, name: true, avatar: true } },
          },
          orderBy: { createdAt: "desc" },
        },
        _count: {
          select: { reviews: true, accessRequests: true, usageMetrics: true },
        },
      },
    });

    if (!product) {
      return NextResponse.json({ error: "Product not found" }, { status: 404 });
    }

    const avgRating = await prisma.review.aggregate({
      where: { productId: product.id },
      _avg: { rating: true },
    });

    return NextResponse.json({
      data: {
        ...product,
        averageRating: avgRating._avg.rating ?? null,
      },
    });
  } catch (error) {
    console.error("GET /api/products/[slug] error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { slug } = await params;
    const body = await request.json();
    const data = UpdateDataProductSchema.parse(body);

    const existing = await prisma.dataProduct.findUnique({ where: { slug } });
    if (!existing) {
      return NextResponse.json({ error: "Product not found" }, { status: 404 });
    }

    const updateData: Record<string, unknown> = { ...data };
    if (data.sizeBytes != null) {
      updateData.sizeBytes = BigInt(data.sizeBytes);
    }

    const product = await prisma.dataProduct.update({
      where: { slug },
      data: updateData,
      include: {
        owner: { select: { id: true, name: true, email: true, avatar: true } },
        steward: { select: { id: true, name: true, email: true, avatar: true } },
        tags: true,
      },
    });

    return NextResponse.json({ data: product });
  } catch (error) {
    if (error instanceof Error && error.name === "ZodError") {
      return NextResponse.json({ error: "Validation failed", details: error }, { status: 400 });
    }
    console.error("PATCH /api/products/[slug] error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function DELETE(
  _request: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { slug } = await params;

    const existing = await prisma.dataProduct.findUnique({ where: { slug } });
    if (!existing) {
      return NextResponse.json({ error: "Product not found" }, { status: 404 });
    }

    const product = await prisma.dataProduct.update({
      where: { slug },
      data: { status: "DEPRECATED" },
    });

    return NextResponse.json({ data: product });
  } catch (error) {
    console.error("DELETE /api/products/[slug] error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
