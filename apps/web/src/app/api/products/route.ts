import { NextRequest, NextResponse } from "next/server";
import { prisma, Prisma } from "@hdm/db";
import { DataProductFilterSchema, CreateDataProductSchema } from "@hdm/types";
import { auth } from "@/lib/auth";

export async function GET(request: NextRequest) {
  try {
    const params = Object.fromEntries(request.nextUrl.searchParams);
    const filter = DataProductFilterSchema.parse(params);

    const where: Prisma.DataProductWhereInput = {};

    if (filter.domain) {
      where.domain = filter.domain;
    }
    if (filter.sensitivity) {
      where.sensitivity = filter.sensitivity;
    }
    if (filter.status) {
      where.status = filter.status;
    }
    if (filter.ownerId) {
      where.ownerId = filter.ownerId;
    }
    if (filter.search) {
      where.OR = [
        { name: { contains: filter.search, mode: "insensitive" } },
        { description: { contains: filter.search, mode: "insensitive" } },
      ];
    }

    const skip = (filter.page - 1) * filter.limit;

    const [products, total] = await Promise.all([
      prisma.dataProduct.findMany({
        where,
        skip,
        take: filter.limit,
        orderBy: { createdAt: "desc" },
        include: {
          owner: { select: { id: true, name: true, email: true, avatar: true } },
          steward: { select: { id: true, name: true, email: true, avatar: true } },
          tags: true,
          qualityScores: {
            orderBy: { checkedAt: "desc" },
            take: 1,
          },
          _count: {
            select: { reviews: true, accessRequests: true },
          },
        },
      }),
      prisma.dataProduct.count({ where }),
    ]);

    // Convert BigInt fields to Number for JSON serialization
    const serialized = products.map((p) => ({
      ...p,
      sizeBytes: p.sizeBytes ? Number(p.sizeBytes) : null,
    }));

    return NextResponse.json({
      data: serialized,
      pagination: {
        page: filter.page,
        limit: filter.limit,
        total,
        totalPages: Math.ceil(total / filter.limit),
      },
    });
  } catch (error) {
    if (error instanceof Error && error.name === "ZodError") {
      return NextResponse.json({ error: "Invalid query parameters", details: error }, { status: 400 });
    }
    console.error("GET /api/products error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const data = CreateDataProductSchema.parse(body);

    const existing = await prisma.dataProduct.findUnique({
      where: { slug: data.slug },
    });
    if (existing) {
      return NextResponse.json({ error: "A product with this slug already exists" }, { status: 409 });
    }

    const product = await prisma.dataProduct.create({
      data: {
        ...data,
        sizeBytes: data.sizeBytes != null ? BigInt(data.sizeBytes) : null,
      },
      include: {
        owner: { select: { id: true, name: true, email: true, avatar: true } },
        steward: { select: { id: true, name: true, email: true, avatar: true } },
        tags: true,
      },
    });

    return NextResponse.json({ data: product }, { status: 201 });
  } catch (error) {
    if (error instanceof Error && error.name === "ZodError") {
      return NextResponse.json({ error: "Validation failed", details: error }, { status: 400 });
    }
    console.error("POST /api/products error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
