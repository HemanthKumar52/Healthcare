import { NextRequest, NextResponse } from "next/server";
import { prisma, Prisma } from "@hdm/db";
import { AuditFilterSchema } from "@hdm/types";
import { auth } from "@/lib/auth";

export async function GET(request: NextRequest) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const params = Object.fromEntries(request.nextUrl.searchParams);
    const filter = AuditFilterSchema.parse(params);

    const where: Prisma.AuditLogWhereInput = {};

    if (filter.actorId) {
      where.actorId = filter.actorId;
    }
    if (filter.action) {
      where.action = filter.action;
    }
    if (filter.targetType) {
      where.targetType = filter.targetType;
    }
    if (filter.targetId) {
      where.targetId = filter.targetId;
    }
    if (filter.from || filter.to) {
      where.timestamp = {};
      if (filter.from) {
        where.timestamp.gte = filter.from;
      }
      if (filter.to) {
        where.timestamp.lte = filter.to;
      }
    }

    const skip = (filter.page - 1) * filter.limit;

    const [logs, total] = await Promise.all([
      prisma.auditLog.findMany({
        where,
        skip,
        take: filter.limit,
        orderBy: { timestamp: "desc" },
        include: {
          actor: { select: { id: true, name: true, email: true, avatar: true } },
        },
      }),
      prisma.auditLog.count({ where }),
    ]);

    return NextResponse.json({
      data: logs,
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
    console.error("GET /api/audit error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
