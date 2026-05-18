import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@hdm/db";

export async function GET(_request: NextRequest) {
  try {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    // Get products with most VIEW actions in the last 30 days
    const trending = await prisma.usageMetric.groupBy({
      by: ["productId"],
      where: {
        action: "VIEW",
        timestamp: { gte: thirtyDaysAgo },
      },
      _count: { id: true },
      orderBy: { _count: { id: "desc" } },
      take: 10,
    });

    const productIds = trending.map((t) => t.productId);

    const products = await prisma.dataProduct.findMany({
      where: { id: { in: productIds } },
      include: {
        owner: { select: { id: true, name: true, avatar: true } },
        tags: true,
        qualityScores: {
          orderBy: { checkedAt: "desc" },
          take: 1,
        },
        _count: {
          select: { reviews: true },
        },
      },
    });

    // Build a map for easy lookup and preserve trending order
    const productMap = new Map(products.map((p) => [p.id, p]));
    const viewCountMap = new Map(trending.map((t) => [t.productId, t._count.id]));

    const results = productIds
      .map((id) => {
        const product = productMap.get(id);
        if (!product) return null;
        return {
          ...product,
          viewCount: viewCountMap.get(id) ?? 0,
        };
      })
      .filter(Boolean);

    return NextResponse.json({ data: results });
  } catch (error) {
    console.error("GET /api/usage error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
