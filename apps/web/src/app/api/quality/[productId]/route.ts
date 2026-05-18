import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@hdm/db";
import { auth } from "@/lib/auth";
import { z } from "zod";

const CreateQualityScoreSchema = z.object({
  completeness: z.number().min(0).max(100),
  uniqueness: z.number().min(0).max(100),
  freshness: z.number().min(0).max(100),
  referentialIntegrity: z.number().min(0).max(100),
  valueRange: z.number().min(0).max(100),
  overallScore: z.number().min(0).max(100),
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

    const limit = Number(request.nextUrl.searchParams.get("limit")) || 30;

    const scores = await prisma.qualityScore.findMany({
      where: { productId },
      orderBy: { checkedAt: "desc" },
      take: limit,
    });

    const latest = scores[0] ?? null;

    return NextResponse.json({
      data: {
        latest,
        history: scores,
      },
    });
  } catch (error) {
    console.error("GET /api/quality/[productId] error:", error);
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
    const data = CreateQualityScoreSchema.parse(body);

    const score = await prisma.qualityScore.create({
      data: {
        productId,
        ...data,
      },
    });

    return NextResponse.json({ data: score }, { status: 201 });
  } catch (error) {
    if (error instanceof Error && error.name === "ZodError") {
      return NextResponse.json({ error: "Validation failed", details: error }, { status: 400 });
    }
    console.error("POST /api/quality/[productId] error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
