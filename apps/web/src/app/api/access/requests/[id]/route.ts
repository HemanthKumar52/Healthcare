import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@hdm/db";
import { ReviewAccessRequestSchema } from "@hdm/types";
import { auth } from "@/lib/auth";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { id } = await params;

    const accessRequest = await prisma.accessRequest.findUnique({
      where: { id },
      include: {
        requester: { select: { id: true, name: true, email: true, avatar: true } },
        approvedBy: { select: { id: true, name: true, email: true, avatar: true } },
        product: {
          select: {
            id: true,
            name: true,
            slug: true,
            domain: true,
            sensitivity: true,
            ownerId: true,
            stewardId: true,
          },
        },
      },
    });

    if (!accessRequest) {
      return NextResponse.json({ error: "Access request not found" }, { status: 404 });
    }

    return NextResponse.json({ data: accessRequest });
  } catch (error) {
    console.error("GET /api/access/requests/[id] error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { id } = await params;
    const body = await request.json();
    const data = ReviewAccessRequestSchema.parse(body);

    const existing = await prisma.accessRequest.findUnique({
      where: { id },
    });

    if (!existing) {
      return NextResponse.json({ error: "Access request not found" }, { status: 404 });
    }

    if (existing.status !== "PENDING") {
      return NextResponse.json({ error: "Only pending requests can be reviewed" }, { status: 400 });
    }

    const updateData: Record<string, unknown> = {
      status: data.status,
      approvedById: session.user.id,
    };

    if (data.status === "APPROVED") {
      updateData.grantedAt = new Date();
      if (data.expiresAt) {
        updateData.expiresAt = data.expiresAt;
      }
    }

    if (data.status === "DENIED" && data.denialReason) {
      updateData.denialReason = data.denialReason;
    }

    const accessRequest = await prisma.accessRequest.update({
      where: { id },
      data: updateData,
      include: {
        requester: { select: { id: true, name: true, email: true, avatar: true } },
        approvedBy: { select: { id: true, name: true, email: true, avatar: true } },
        product: { select: { id: true, name: true, slug: true } },
      },
    });

    return NextResponse.json({ data: accessRequest });
  } catch (error) {
    if (error instanceof Error && error.name === "ZodError") {
      return NextResponse.json({ error: "Validation failed", details: error }, { status: 400 });
    }
    console.error("PATCH /api/access/requests/[id] error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
