import { NextRequest, NextResponse } from "next/server";
import { prisma, Prisma } from "@hdm/db";
import { CreateAccessRequestSchema } from "@hdm/types";
import { auth } from "@/lib/auth";
import { z } from "zod";

const ListParamsSchema = z.object({
  requesterId: z.string().optional(),
  productId: z.string().optional(),
  status: z.enum(["PENDING", "APPROVED", "DENIED", "REVOKED", "EXPIRED"]).optional(),
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(20),
});

export async function GET(request: NextRequest) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const params = Object.fromEntries(request.nextUrl.searchParams);
    const filter = ListParamsSchema.parse(params);

    const where: Prisma.AccessRequestWhereInput = {};

    if (filter.requesterId) {
      where.requesterId = filter.requesterId;
    }
    if (filter.productId) {
      where.productId = filter.productId;
    }
    if (filter.status) {
      where.status = filter.status;
    }

    const skip = (filter.page - 1) * filter.limit;

    const [requests, total] = await Promise.all([
      prisma.accessRequest.findMany({
        where,
        skip,
        take: filter.limit,
        orderBy: { createdAt: "desc" },
        include: {
          requester: { select: { id: true, name: true, email: true, avatar: true } },
          approvedBy: { select: { id: true, name: true, email: true, avatar: true } },
          product: { select: { id: true, name: true, slug: true, domain: true, sensitivity: true } },
        },
      }),
      prisma.accessRequest.count({ where }),
    ]);

    return NextResponse.json({
      data: requests,
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
    console.error("GET /api/access/requests error:", error);
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
    const data = CreateAccessRequestSchema.parse(body);

    // Check product exists
    const product = await prisma.dataProduct.findUnique({
      where: { id: data.productId },
    });
    if (!product) {
      return NextResponse.json({ error: "Product not found" }, { status: 404 });
    }

    // Check for existing pending request
    const existingRequest = await prisma.accessRequest.findFirst({
      where: {
        requesterId: session.user.id,
        productId: data.productId,
        status: "PENDING",
      },
    });
    if (existingRequest) {
      return NextResponse.json({ error: "You already have a pending access request for this product" }, { status: 409 });
    }

    const accessRequest = await prisma.accessRequest.create({
      data: {
        requesterId: session.user.id,
        productId: data.productId,
        justification: data.justification,
        expiresAt: data.expiresAt ?? null,
      },
      include: {
        requester: { select: { id: true, name: true, email: true, avatar: true } },
        product: { select: { id: true, name: true, slug: true, domain: true } },
      },
    });

    return NextResponse.json({ data: accessRequest }, { status: 201 });
  } catch (error) {
    if (error instanceof Error && error.name === "ZodError") {
      return NextResponse.json({ error: "Validation failed", details: error }, { status: 400 });
    }
    console.error("POST /api/access/requests error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
