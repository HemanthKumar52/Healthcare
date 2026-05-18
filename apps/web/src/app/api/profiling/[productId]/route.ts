import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@hdm/db";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ productId: string }> }
) {
  try {
    const { productId } = await params;

    const product = await prisma.dataProduct.findUnique({
      where: { id: productId },
      select: { id: true, name: true, slug: true },
    });

    if (!product) {
      return NextResponse.json({ error: "Product not found" }, { status: 404 });
    }

    const profiles = await prisma.columnProfile.findMany({
      where: { productId },
      orderBy: { columnName: "asc" },
    });

    return NextResponse.json({
      data: {
        product,
        columns: profiles,
      },
    });
  } catch (error) {
    console.error("GET /api/profiling/[productId] error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
