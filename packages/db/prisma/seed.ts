import {
  PrismaClient,
  UserRole,
  Domain,
  Sensitivity,
  ProductStatus,
  AccessRequestStatus,
  AuditAction,
  NotificationType,
  QualityMetric,
  SLAOperator,
  LineageNodeType,
  UsageAction,
} from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  console.log("Seeding database...");

  // ─── Users ──────────────────────────────────────────────

  const admin = await prisma.user.upsert({
    where: { email: "sarah.adams@healthcare.org" },
    update: {},
    create: {
      name: "Sarah Adams",
      email: "sarah.adams@healthcare.org",
      password: "admin123",
      role: UserRole.ADMIN,
      department: "Platform Administration",
    },
  });

  const steward1 = await prisma.user.upsert({
    where: { email: "priya.mehta@healthcare.org" },
    update: {},
    create: {
      name: "Dr. Priya Mehta",
      email: "priya.mehta@healthcare.org",
      password: "steward123",
      role: UserRole.STEWARD,
      department: "Clinical Data Governance",
    },
  });

  const steward2 = await prisma.user.upsert({
    where: { email: "james.wilson@healthcare.org" },
    update: {},
    create: {
      name: "Dr. James Wilson",
      email: "james.wilson@healthcare.org",
      password: "steward123",
      role: UserRole.STEWARD,
      department: "Financial Data Governance",
    },
  });

  const engineer = await prisma.user.upsert({
    where: { email: "kevin.park@healthcare.org" },
    update: {},
    create: {
      name: "Kevin Park",
      email: "kevin.park@healthcare.org",
      password: "engineer123",
      role: UserRole.ENGINEER,
      department: "Data Engineering",
    },
  });

  const consumer1 = await prisma.user.upsert({
    where: { email: "emily.chen@healthcare.org" },
    update: {},
    create: {
      name: "Dr. Emily Chen",
      email: "emily.chen@healthcare.org",
      password: "consumer123",
      role: UserRole.CONSUMER,
      department: "Clinical Research",
    },
  });

  const consumer2 = await prisma.user.upsert({
    where: { email: "mark.thompson@healthcare.org" },
    update: {},
    create: {
      name: "Mark Thompson",
      email: "mark.thompson@healthcare.org",
      password: "consumer123",
      role: UserRole.CONSUMER,
      department: "Revenue Cycle",
    },
  });

  console.log("  Users created.");

  // ─── Data Products ────────────────────────────────────────

  const products = [
    {
      name: "Patient Visit Summary",
      slug: "patient-visit-summary",
      description:
        "Aggregated view of patient encounters with diagnoses, procedures, and outcomes. Includes admission/discharge dates, primary and secondary diagnoses, procedures performed, and attending provider details.",
      domain: Domain.CLINICAL,
      sensitivity: Sensitivity.PHI,
      status: ProductStatus.PUBLISHED,
      ownerId: steward1.id,
      stewardId: steward1.id,
      catalogName: "healthcare_marketplace",
      schemaName: "clinical",
      tableName: "patient_visit_summary",
      refreshCadence: "daily",
      lastRefreshedAt: new Date("2026-05-18T06:00:00Z"),
      recordCount: 148320,
      sizeBytes: BigInt(2_415_000_000),
    },
    {
      name: "Lab Analytics",
      slug: "lab-analytics",
      description:
        "Comprehensive laboratory results analytics including turnaround times, critical value flagging, and trending analysis. Supports quality improvement initiatives for clinical lab operations.",
      domain: Domain.CLINICAL,
      sensitivity: Sensitivity.PHI,
      status: ProductStatus.PUBLISHED,
      ownerId: steward1.id,
      stewardId: steward1.id,
      catalogName: "healthcare_marketplace",
      schemaName: "clinical",
      tableName: "lab_analytics",
      refreshCadence: "daily",
      lastRefreshedAt: new Date("2026-05-18T06:00:00Z"),
      recordCount: 892150,
      sizeBytes: BigInt(5_120_000_000),
    },
    {
      name: "Medication Summary",
      slug: "medication-summary",
      description:
        "Patient medication history including prescriptions, dosages, refill patterns, and drug interaction alerts. Critical for polypharmacy analysis and medication reconciliation workflows.",
      domain: Domain.CLINICAL,
      sensitivity: Sensitivity.PHI,
      status: ProductStatus.PUBLISHED,
      ownerId: steward1.id,
      stewardId: steward1.id,
      catalogName: "healthcare_marketplace",
      schemaName: "clinical",
      tableName: "medication_summary",
      refreshCadence: "daily",
      lastRefreshedAt: new Date("2026-05-18T06:00:00Z"),
      recordCount: 425800,
      sizeBytes: BigInt(1_890_000_000),
    },
    {
      name: "Bed Utilization Report",
      slug: "bed-utilization-report",
      description:
        "Real-time and historical bed occupancy analytics by unit, floor, and facility. Tracks average length of stay, turnover rate, and capacity forecasting for hospital operations.",
      domain: Domain.OPERATIONAL,
      sensitivity: Sensitivity.NO_PHI,
      status: ProductStatus.PUBLISHED,
      ownerId: steward2.id,
      stewardId: steward2.id,
      catalogName: "healthcare_marketplace",
      schemaName: "operational",
      tableName: "bed_utilization",
      refreshCadence: "hourly",
      lastRefreshedAt: new Date("2026-05-18T09:00:00Z"),
      recordCount: 56200,
      sizeBytes: BigInt(320_000_000),
    },
    {
      name: "Appointment Analytics",
      slug: "appointment-analytics",
      description:
        "Scheduling analytics covering appointment volumes, no-show rates, wait times, and provider utilization. Enables optimization of clinic schedules and resource allocation.",
      domain: Domain.OPERATIONAL,
      sensitivity: Sensitivity.NO_PHI,
      status: ProductStatus.PUBLISHED,
      ownerId: steward2.id,
      stewardId: steward2.id,
      catalogName: "healthcare_marketplace",
      schemaName: "operational",
      tableName: "appointment_analytics",
      refreshCadence: "daily",
      lastRefreshedAt: new Date("2026-05-18T06:00:00Z"),
      recordCount: 234500,
      sizeBytes: BigInt(780_000_000),
    },
    {
      name: "Claims Analytics",
      slug: "claims-analytics",
      description:
        "Insurance claims processing analytics with denial rates, average reimbursement, payer mix analysis, and aging reports. Key dataset for revenue cycle management and payer contract negotiations.",
      domain: Domain.FINANCIAL,
      sensitivity: Sensitivity.RESTRICTED,
      status: ProductStatus.PUBLISHED,
      ownerId: steward2.id,
      stewardId: steward2.id,
      catalogName: "healthcare_marketplace",
      schemaName: "financial",
      tableName: "claims_analytics",
      refreshCadence: "daily",
      lastRefreshedAt: new Date("2026-05-18T06:00:00Z"),
      recordCount: 512840,
      sizeBytes: BigInt(3_200_000_000),
    },
    {
      name: "Revenue Cycle Dashboard",
      slug: "revenue-cycle-dashboard",
      description:
        "End-to-end revenue cycle metrics from charge capture through final payment. Includes days in A/R, clean claim rate, net collection rate, and cost-to-collect ratios.",
      domain: Domain.FINANCIAL,
      sensitivity: Sensitivity.RESTRICTED,
      status: ProductStatus.PUBLISHED,
      ownerId: steward2.id,
      stewardId: steward2.id,
      catalogName: "healthcare_marketplace",
      schemaName: "financial",
      tableName: "revenue_cycle",
      refreshCadence: "daily",
      lastRefreshedAt: new Date("2026-05-17T06:00:00Z"),
      recordCount: 189400,
      sizeBytes: BigInt(1_150_000_000),
    },
    {
      name: "Provider Directory",
      slug: "provider-directory",
      description:
        "Comprehensive healthcare provider registry with credentials, specialties, affiliations, NPI numbers, and practice locations. Maintained in compliance with CMS provider data requirements.",
      domain: Domain.PROVIDER,
      sensitivity: Sensitivity.NO_PHI,
      status: ProductStatus.PUBLISHED,
      ownerId: steward1.id,
      stewardId: steward1.id,
      catalogName: "healthcare_marketplace",
      schemaName: "provider",
      tableName: "provider_directory",
      refreshCadence: "weekly",
      lastRefreshedAt: new Date("2026-05-15T06:00:00Z"),
      recordCount: 12450,
      sizeBytes: BigInt(85_000_000),
    },
    {
      name: "Population Health Metrics",
      slug: "population-health-metrics",
      description:
        "De-identified population-level health indicators including chronic disease prevalence, risk stratification scores, social determinants of health indicators, and geographic health disparities.",
      domain: Domain.RESEARCH,
      sensitivity: Sensitivity.NO_PHI,
      status: ProductStatus.PUBLISHED,
      ownerId: steward1.id,
      stewardId: steward1.id,
      catalogName: "healthcare_marketplace",
      schemaName: "research",
      tableName: "population_health",
      refreshCadence: "monthly",
      lastRefreshedAt: new Date("2026-05-01T06:00:00Z"),
      recordCount: 85200,
      sizeBytes: BigInt(620_000_000),
    },
    {
      name: "De-identified Cohorts",
      slug: "deidentified-cohorts",
      description:
        "Pre-built de-identified patient cohorts for research use cases. Includes diabetes management cohort, heart failure readmission cohort, and oncology treatment outcomes cohort. Safe Harbor compliant.",
      domain: Domain.RESEARCH,
      sensitivity: Sensitivity.NO_PHI,
      status: ProductStatus.PUBLISHED,
      ownerId: steward1.id,
      stewardId: steward1.id,
      catalogName: "healthcare_marketplace",
      schemaName: "research",
      tableName: "deidentified_cohorts",
      refreshCadence: "monthly",
      lastRefreshedAt: new Date("2026-05-01T06:00:00Z"),
      recordCount: 42600,
      sizeBytes: BigInt(310_000_000),
    },
  ];

  const createdProducts = [];
  for (const p of products) {
    const product = await prisma.dataProduct.upsert({
      where: { slug: p.slug },
      update: {},
      create: p,
    });
    createdProducts.push(product);
  }

  console.log("  Data products created.");

  // ─── Tags ─────────────────────────────────────────────────

  const tagData: { productIndex: number; key: string; value: string }[] = [
    { productIndex: 0, key: "contains_phi", value: "true" },
    { productIndex: 0, key: "hipaa_certified", value: "true" },
    { productIndex: 0, key: "business_unit", value: "clinical-analytics" },
    { productIndex: 1, key: "contains_phi", value: "true" },
    { productIndex: 1, key: "hipaa_certified", value: "true" },
    { productIndex: 1, key: "business_unit", value: "clinical-analytics" },
    { productIndex: 2, key: "contains_phi", value: "true" },
    { productIndex: 2, key: "hipaa_certified", value: "true" },
    { productIndex: 2, key: "business_unit", value: "pharmacy" },
    { productIndex: 3, key: "contains_phi", value: "false" },
    { productIndex: 3, key: "business_unit", value: "hospital-operations" },
    { productIndex: 4, key: "contains_phi", value: "false" },
    { productIndex: 4, key: "business_unit", value: "clinic-operations" },
    { productIndex: 5, key: "contains_phi", value: "false" },
    { productIndex: 5, key: "hipaa_certified", value: "true" },
    { productIndex: 5, key: "business_unit", value: "revenue-cycle" },
    { productIndex: 6, key: "contains_phi", value: "false" },
    { productIndex: 6, key: "business_unit", value: "revenue-cycle" },
    { productIndex: 7, key: "contains_phi", value: "false" },
    { productIndex: 7, key: "business_unit", value: "provider-network" },
    { productIndex: 8, key: "contains_phi", value: "false" },
    { productIndex: 8, key: "safe_harbor", value: "true" },
    { productIndex: 8, key: "business_unit", value: "research" },
    { productIndex: 9, key: "contains_phi", value: "false" },
    { productIndex: 9, key: "safe_harbor", value: "true" },
    { productIndex: 9, key: "business_unit", value: "research" },
    { productIndex: 9, key: "irb_approved", value: "true" },
  ];

  for (const t of tagData) {
    await prisma.dataProductTag.upsert({
      where: {
        productId_key: {
          productId: createdProducts[t.productIndex].id,
          key: t.key,
        },
      },
      update: {},
      create: {
        productId: createdProducts[t.productIndex].id,
        key: t.key,
        value: t.value,
      },
    });
  }

  console.log("  Tags created.");

  // ─── Quality Scores (3 per product showing trend) ──────────

  const now = new Date();
  for (let i = 0; i < createdProducts.length; i++) {
    const product = createdProducts[i];
    const baseScores = [
      { completeness: 0.95, uniqueness: 0.99, freshness: 0.98, ri: 0.96, vr: 0.97 },
      { completeness: 0.96, uniqueness: 0.99, freshness: 0.97, ri: 0.97, vr: 0.98 },
      { completeness: 0.97, uniqueness: 1.0, freshness: 0.99, ri: 0.97, vr: 0.98 },
    ];

    // Make Provider Directory show lower quality
    if (i === 7) {
      baseScores[0] = { completeness: 0.85, uniqueness: 0.95, freshness: 0.80, ri: 0.88, vr: 0.90 };
      baseScores[1] = { completeness: 0.78, uniqueness: 0.96, freshness: 0.75, ri: 0.85, vr: 0.88 };
      baseScores[2] = { completeness: 0.72, uniqueness: 0.96, freshness: 0.70, ri: 0.82, vr: 0.86 };
    }

    for (let j = 0; j < 3; j++) {
      const s = baseScores[j];
      const overall = (s.completeness + s.uniqueness + s.freshness + s.ri + s.vr) / 5;
      const checkedAt = new Date(now.getTime() - (2 - j) * 7 * 24 * 60 * 60 * 1000);

      await prisma.qualityScore.create({
        data: {
          productId: product.id,
          completeness: s.completeness * 100,
          uniqueness: s.uniqueness * 100,
          freshness: s.freshness * 100,
          referentialIntegrity: s.ri * 100,
          valueRange: s.vr * 100,
          overallScore: overall * 100,
          checkedAt,
        },
      });
    }
  }

  console.log("  Quality scores created.");

  // ─── Quality SLAs ─────────────────────────────────────────

  for (const product of createdProducts) {
    const isProviderDir = product.slug === "provider-directory";
    const isRevCycle = product.slug === "revenue-cycle-dashboard";

    await prisma.qualitySLA.upsert({
      where: {
        productId_metric: {
          productId: product.id,
          metric: QualityMetric.COMPLETENESS,
        },
      },
      update: {},
      create: {
        productId: product.id,
        metric: QualityMetric.COMPLETENESS,
        threshold: 90,
        operator: SLAOperator.GTE,
        isBreached: isProviderDir,
      },
    });

    await prisma.qualitySLA.upsert({
      where: {
        productId_metric: {
          productId: product.id,
          metric: QualityMetric.FRESHNESS,
        },
      },
      update: {},
      create: {
        productId: product.id,
        metric: QualityMetric.FRESHNESS,
        threshold: 95,
        operator: SLAOperator.GTE,
        isBreached: isRevCycle,
      },
    });
  }

  console.log("  Quality SLAs created.");

  // ─── Access Requests ──────────────────────────────────────

  const accessRequests = [
    {
      requesterId: consumer1.id,
      productId: createdProducts[0].id,
      justification: "Need patient visit data for readmission analysis study approved by IRB #2026-0412.",
      status: AccessRequestStatus.PENDING,
    },
    {
      requesterId: consumer2.id,
      productId: createdProducts[5].id,
      justification: "Quarterly financial reconciliation requires claims data for FY2026 Q2 close.",
      status: AccessRequestStatus.PENDING,
    },
    {
      requesterId: consumer1.id,
      productId: createdProducts[1].id,
      justification: "Tracking turnaround times for critical lab results as part of Joint Commission prep.",
      status: AccessRequestStatus.APPROVED,
      approvedById: steward1.id,
      grantedAt: new Date("2026-05-10T14:30:00Z"),
      expiresAt: new Date("2026-09-10T14:30:00Z"),
    },
    {
      requesterId: consumer1.id,
      productId: createdProducts[9].id,
      justification: "Diabetes management cohort needed for population health research project.",
      status: AccessRequestStatus.APPROVED,
      approvedById: steward1.id,
      grantedAt: new Date("2026-04-20T10:00:00Z"),
      expiresAt: new Date("2026-10-20T10:00:00Z"),
    },
    {
      requesterId: consumer2.id,
      productId: createdProducts[6].id,
      justification: "Revenue cycle analysis for board reporting.",
      status: AccessRequestStatus.APPROVED,
      approvedById: steward2.id,
      grantedAt: new Date("2026-05-05T09:00:00Z"),
      expiresAt: new Date("2026-11-05T09:00:00Z"),
    },
    {
      requesterId: consumer2.id,
      productId: createdProducts[0].id,
      justification: "Cross-referencing visit data with billing for payment integrity audit.",
      status: AccessRequestStatus.DENIED,
      approvedById: steward1.id,
      denialReason: "PHI access requires HIPAA training completion. Please submit certificate and re-request.",
    },
    {
      requesterId: consumer1.id,
      productId: createdProducts[3].id,
      justification: "Bed utilization analysis for capacity planning project.",
      status: AccessRequestStatus.APPROVED,
      approvedById: steward2.id,
      grantedAt: new Date("2026-05-12T11:00:00Z"),
      expiresAt: new Date("2026-11-12T11:00:00Z"),
    },
    {
      requesterId: consumer2.id,
      productId: createdProducts[4].id,
      justification: "Appointment no-show patterns for clinic optimization initiative.",
      status: AccessRequestStatus.PENDING,
    },
  ];

  for (const req of accessRequests) {
    await prisma.accessRequest.create({ data: req });
  }

  console.log("  Access requests created.");

  // ─── Audit Logs ───────────────────────────────────────────

  const auditLogs = [
    { actorId: admin.id, action: AuditAction.USER_LOGIN, targetType: "Session", targetId: "session_001", ipAddress: "10.0.1.50" },
    { actorId: steward1.id, action: AuditAction.PRODUCT_CREATED, targetType: "DataProduct", targetId: createdProducts[0].id, metadata: { productName: "Patient Visit Summary" } },
    { actorId: steward1.id, action: AuditAction.PRODUCT_CREATED, targetType: "DataProduct", targetId: createdProducts[1].id, metadata: { productName: "Lab Analytics" } },
    { actorId: consumer1.id, action: AuditAction.ACCESS_REQUESTED, targetType: "DataProduct", targetId: createdProducts[0].id, metadata: { productName: "Patient Visit Summary" } },
    { actorId: steward1.id, action: AuditAction.ACCESS_APPROVED, targetType: "DataProduct", targetId: createdProducts[1].id, metadata: { productName: "Lab Analytics", requester: "Dr. Emily Chen" } },
    { actorId: steward1.id, action: AuditAction.ACCESS_DENIED, targetType: "DataProduct", targetId: createdProducts[0].id, metadata: { productName: "Patient Visit Summary", requester: "Mark Thompson", reason: "Missing HIPAA cert" } },
    { actorId: engineer.id, action: AuditAction.PIPELINE_EXECUTED, targetType: "Pipeline", targetId: "pipeline_clinical_ingestion", metadata: { duration: "4m 12s", records: 148320 } },
    { actorId: engineer.id, action: AuditAction.QUALITY_CHECK_RAN, targetType: "DataProduct", targetId: createdProducts[0].id, metadata: { overallScore: 96.2 } },
    { actorId: admin.id, action: AuditAction.SLA_BREACHED, targetType: "DataProduct", targetId: createdProducts[7].id, metadata: { metric: "completeness", current: 72, threshold: 90 } },
    { actorId: consumer2.id, action: AuditAction.DATA_EXPORTED, targetType: "DataProduct", targetId: createdProducts[6].id, metadata: { format: "csv", rows: 5000 } },
    { actorId: steward2.id, action: AuditAction.PRODUCT_UPDATED, targetType: "DataProduct", targetId: createdProducts[3].id, metadata: { field: "refreshCadence", oldValue: "daily", newValue: "hourly" } },
    { actorId: consumer1.id, action: AuditAction.USER_LOGIN, targetType: "Session", targetId: "session_002", ipAddress: "10.0.2.15" },
    { actorId: engineer.id, action: AuditAction.PIPELINE_EXECUTED, targetType: "Pipeline", targetId: "pipeline_financial_curation", metadata: { duration: "7m 45s", records: 512840 } },
    { actorId: consumer1.id, action: AuditAction.REVIEW_SUBMITTED, targetType: "DataProduct", targetId: createdProducts[1].id, metadata: { rating: 5 } },
    { actorId: admin.id, action: AuditAction.USER_LOGOUT, targetType: "Session", targetId: "session_001", ipAddress: "10.0.1.50" },
  ];

  for (let i = 0; i < auditLogs.length; i++) {
    const log = auditLogs[i];
    await prisma.auditLog.create({
      data: {
        ...log,
        metadata: log.metadata ?? undefined,
        timestamp: new Date(now.getTime() - (auditLogs.length - i) * 45 * 60 * 1000),
      },
    });
  }

  console.log("  Audit logs created.");

  // ─── Notifications ────────────────────────────────────────

  const notifications = [
    { userId: consumer1.id, type: NotificationType.ACCESS_APPROVED, title: "Access Approved", message: 'Your request for "Lab Analytics" has been approved by Dr. Priya Mehta. Access expires on Sep 10, 2026.', isRead: true },
    { userId: consumer1.id, type: NotificationType.ACCESS_APPROVED, title: "Access Approved", message: 'Your request for "De-identified Cohorts" has been approved. Access expires on Oct 20, 2026.', isRead: true },
    { userId: consumer2.id, type: NotificationType.ACCESS_DENIED, title: "Access Denied", message: 'Your request for "Patient Visit Summary" was denied. Reason: Missing HIPAA training certificate.', isRead: false },
    { userId: consumer2.id, type: NotificationType.ACCESS_APPROVED, title: "Access Approved", message: 'Your request for "Revenue Cycle Dashboard" has been approved by Dr. James Wilson.', isRead: true },
    { userId: steward1.id, type: NotificationType.ACCESS_REQUESTED, title: "New Access Request", message: 'Dr. Emily Chen requested access to "Patient Visit Summary" for readmission analysis.', isRead: false },
    { userId: steward1.id, type: NotificationType.QUALITY_ALERT, title: "Quality Alert", message: '"Provider Directory" completeness dropped to 72%, below the 90% SLA threshold.', isRead: false },
    { userId: steward2.id, type: NotificationType.ACCESS_REQUESTED, title: "New Access Request", message: 'Mark Thompson requested access to "Claims Analytics" for quarterly reconciliation.', isRead: false },
    { userId: engineer.id, type: NotificationType.PIPELINE_FAILED, title: "Pipeline Failed", message: '"Provider Sync - Directory Update" failed at 07:30 AM. Error: Connection timeout to source system.', isRead: false },
    { userId: admin.id, type: NotificationType.SLA_BREACH, title: "SLA Breach", message: '"Provider Directory" completeness SLA breached. Current: 72%, Threshold: 90%.', isRead: false },
    { userId: consumer1.id, type: NotificationType.NEW_PRODUCT, title: "New Data Product", message: '"Population Health Metrics" is now available in the Research domain. Request access to explore.', isRead: false },
  ];

  for (let i = 0; i < notifications.length; i++) {
    await prisma.notification.create({
      data: {
        ...notifications[i],
        createdAt: new Date(now.getTime() - (notifications.length - i) * 3 * 60 * 60 * 1000),
      },
    });
  }

  console.log("  Notifications created.");

  // ─── Reviews ──────────────────────────────────────────────

  const reviews = [
    { userId: consumer1.id, productId: createdProducts[1].id, rating: 5, comment: "Excellent dataset for lab turnaround analysis. Well-documented and consistently fresh. Critical value flags are extremely useful for our quality improvement dashboards." },
    { userId: consumer2.id, productId: createdProducts[6].id, rating: 4, comment: "Comprehensive revenue cycle data. The days-in-AR metrics are accurate and align with our internal tracking. Would benefit from a payer-level breakdown." },
    { userId: consumer1.id, productId: createdProducts[9].id, rating: 5, comment: "De-identification is thorough and Safe Harbor compliant. The diabetes cohort is well-curated with appropriate inclusion/exclusion criteria documented." },
    { userId: consumer2.id, productId: createdProducts[3].id, rating: 4, comment: "Hourly refresh cadence is valuable for real-time capacity planning. Occupancy rates match our internal census within 2% variance." },
    { userId: consumer1.id, productId: createdProducts[4].id, rating: 3, comment: "Good scheduling data but no-show prediction features could be enhanced. Historical patterns are solid for the last 18 months." },
    { userId: consumer2.id, productId: createdProducts[7].id, rating: 2, comment: "Provider data has significant completeness gaps, especially for affiliated providers. NPI coverage is only about 72%. Needs attention." },
  ];

  for (const review of reviews) {
    await prisma.review.upsert({
      where: {
        userId_productId: {
          userId: review.userId,
          productId: review.productId,
        },
      },
      update: {},
      create: review,
    });
  }

  console.log("  Reviews created.");

  // ─── Column Profiles (2 products, 5-8 columns each) ──────

  // Patient Visit Summary columns
  const pvsCols = [
    { columnName: "patient_id", dataType: "STRING", nullPercentage: 0, distinctCount: 45230, minValue: "P000001", maxValue: "P045230", sampleValues: ["P012345", "P028901", "P003456"] },
    { columnName: "encounter_date", dataType: "DATE", nullPercentage: 0.1, distinctCount: 1825, minValue: "2020-01-01", maxValue: "2026-05-18", sampleValues: ["2026-03-15", "2025-11-22", "2026-01-08"] },
    { columnName: "diagnosis_code", dataType: "STRING", nullPercentage: 0.5, distinctCount: 8420, minValue: "A00.0", maxValue: "Z99.9", sampleValues: ["E11.65", "I10", "J18.9", "M54.5", "K21.0"] },
    { columnName: "diagnosis_description", dataType: "STRING", nullPercentage: 0.5, distinctCount: 8420, minValue: null, maxValue: null, sampleValues: ["Type 2 diabetes with hyperglycemia", "Essential hypertension", "Pneumonia, unspecified"] },
    { columnName: "attending_provider", dataType: "STRING", nullPercentage: 2.1, distinctCount: 342, minValue: null, maxValue: null, sampleValues: ["Dr. Smith", "Dr. Patel", "Dr. Johnson"] },
    { columnName: "length_of_stay", dataType: "INTEGER", nullPercentage: 0, distinctCount: 45, minValue: "0", maxValue: "120", meanValue: 4.2, sampleValues: ["1", "3", "5", "2", "7"] },
    { columnName: "discharge_disposition", dataType: "STRING", nullPercentage: 1.3, distinctCount: 12, minValue: null, maxValue: null, sampleValues: ["Home", "SNF", "Rehab", "AMA", "Expired"] },
    { columnName: "total_charges", dataType: "DECIMAL", nullPercentage: 0.8, distinctCount: 142500, minValue: "150.00", maxValue: "1250000.00", meanValue: 28450.75, sampleValues: ["5200.00", "18750.50", "42300.00"] },
  ];

  for (const col of pvsCols) {
    await prisma.columnProfile.upsert({
      where: {
        productId_columnName: {
          productId: createdProducts[0].id,
          columnName: col.columnName,
        },
      },
      update: {},
      create: {
        productId: createdProducts[0].id,
        ...col,
      },
    });
  }

  // Claims Analytics columns
  const claimsCols = [
    { columnName: "claim_id", dataType: "STRING", nullPercentage: 0, distinctCount: 512840, minValue: "CLM000001", maxValue: "CLM512840", sampleValues: ["CLM128450", "CLM305201", "CLM004521"] },
    { columnName: "payer_name", dataType: "STRING", nullPercentage: 0, distinctCount: 45, minValue: null, maxValue: null, sampleValues: ["Medicare", "Blue Cross", "Aetna", "UnitedHealth", "Cigna"] },
    { columnName: "claim_amount", dataType: "DECIMAL", nullPercentage: 0, distinctCount: 98500, minValue: "25.00", maxValue: "850000.00", meanValue: 12450.30, sampleValues: ["3500.00", "15200.50", "890.00"] },
    { columnName: "paid_amount", dataType: "DECIMAL", nullPercentage: 5.2, distinctCount: 87300, minValue: "0.00", maxValue: "720000.00", meanValue: 9875.60, sampleValues: ["2800.00", "12100.00", "0.00"] },
    { columnName: "denial_code", dataType: "STRING", nullPercentage: 78.5, distinctCount: 156, minValue: null, maxValue: null, sampleValues: ["CO-4", "CO-16", "CO-45", "PR-1", "OA-23"] },
    { columnName: "service_date", dataType: "DATE", nullPercentage: 0, distinctCount: 1460, minValue: "2022-01-01", maxValue: "2026-05-18", sampleValues: ["2026-04-10", "2025-12-01", "2026-02-15"] },
  ];

  for (const col of claimsCols) {
    await prisma.columnProfile.upsert({
      where: {
        productId_columnName: {
          productId: createdProducts[5].id,
          columnName: col.columnName,
        },
      },
      update: {},
      create: {
        productId: createdProducts[5].id,
        ...col,
      },
    });
  }

  console.log("  Column profiles created.");

  // ─── Lineage Nodes & Edges (2 products) ───────────────────

  // Patient Visit Summary lineage
  const pvsSource1 = await prisma.lineageNode.create({
    data: {
      productId: createdProducts[0].id,
      nodeType: LineageNodeType.SOURCE,
      name: "bronze.raw_encounters",
      description: "Raw encounter records from EHR extract",
      metadata: { format: "delta", recordCount: 320000 },
    },
  });
  const pvsSource2 = await prisma.lineageNode.create({
    data: {
      productId: createdProducts[0].id,
      nodeType: LineageNodeType.SOURCE,
      name: "bronze.raw_diagnoses",
      description: "Raw ICD-10 diagnosis codes from clinical systems",
      metadata: { format: "delta", recordCount: 580000 },
    },
  });
  const pvsSource3 = await prisma.lineageNode.create({
    data: {
      productId: createdProducts[0].id,
      nodeType: LineageNodeType.SOURCE,
      name: "bronze.raw_procedures",
      description: "Raw CPT procedure codes",
      metadata: { format: "delta", recordCount: 215000 },
    },
  });
  const pvsTransform = await prisma.lineageNode.create({
    data: {
      productId: createdProducts[0].id,
      nodeType: LineageNodeType.TRANSFORM,
      name: "silver.clean_patient_visits",
      description: "Join, deduplicate, and standardize encounter data",
      metadata: { pipeline: "clinical/patient_visits.py" },
    },
  });
  const pvsTarget = await prisma.lineageNode.create({
    data: {
      productId: createdProducts[0].id,
      nodeType: LineageNodeType.TARGET,
      name: "clinical.patient_visit_summary",
      description: "Curated patient visit summary data product",
      metadata: { catalog: "healthcare_marketplace" },
    },
  });

  await prisma.lineageEdge.createMany({
    data: [
      { sourceNodeId: pvsSource1.id, targetNodeId: pvsTransform.id, transformDescription: "Join encounters on encounter_id" },
      { sourceNodeId: pvsSource2.id, targetNodeId: pvsTransform.id, transformDescription: "Join diagnoses on encounter_id, pivot to primary/secondary" },
      { sourceNodeId: pvsSource3.id, targetNodeId: pvsTransform.id, transformDescription: "Join procedures on encounter_id, aggregate per visit" },
      { sourceNodeId: pvsTransform.id, targetNodeId: pvsTarget.id, transformDescription: "Apply quality checks, write to gold table" },
    ],
  });

  // Claims Analytics lineage
  const claimsSource1 = await prisma.lineageNode.create({
    data: {
      productId: createdProducts[5].id,
      nodeType: LineageNodeType.SOURCE,
      name: "bronze.raw_insurance_claims",
      description: "Raw insurance claim submissions",
      metadata: { format: "delta", recordCount: 650000 },
    },
  });
  const claimsSource2 = await prisma.lineageNode.create({
    data: {
      productId: createdProducts[5].id,
      nodeType: LineageNodeType.SOURCE,
      name: "bronze.raw_payments",
      description: "Raw payment and remittance records",
      metadata: { format: "delta", recordCount: 480000 },
    },
  });
  const claimsTransform = await prisma.lineageNode.create({
    data: {
      productId: createdProducts[5].id,
      nodeType: LineageNodeType.TRANSFORM,
      name: "silver.clean_claims",
      description: "Match claims to payments, compute denial rates, calculate aging",
      metadata: { pipeline: "financial/claims_analytics.py" },
    },
  });
  const claimsTarget = await prisma.lineageNode.create({
    data: {
      productId: createdProducts[5].id,
      nodeType: LineageNodeType.TARGET,
      name: "financial.claims_analytics",
      description: "Curated claims analytics data product",
      metadata: { catalog: "healthcare_marketplace" },
    },
  });

  await prisma.lineageEdge.createMany({
    data: [
      { sourceNodeId: claimsSource1.id, targetNodeId: claimsTransform.id, transformDescription: "Deduplicate claims, standardize payer names" },
      { sourceNodeId: claimsSource2.id, targetNodeId: claimsTransform.id, transformDescription: "Match payments to claims on claim_id" },
      { sourceNodeId: claimsTransform.id, targetNodeId: claimsTarget.id, transformDescription: "Compute denial analytics, write to gold table" },
    ],
  });

  console.log("  Lineage nodes and edges created.");

  // ─── Usage Metrics (30 entries) ───────────────────────────

  const usageActions = [UsageAction.VIEW, UsageAction.DOWNLOAD, UsageAction.QUERY, UsageAction.API_ACCESS];
  const usageUsers = [consumer1, consumer2, steward1, steward2, engineer, admin];

  for (let i = 0; i < 30; i++) {
    const productIdx = i % createdProducts.length;
    const userIdx = i % usageUsers.length;
    const actionIdx = i % usageActions.length;
    await prisma.usageMetric.create({
      data: {
        productId: createdProducts[productIdx].id,
        userId: usageUsers[userIdx].id,
        action: usageActions[actionIdx],
        timestamp: new Date(now.getTime() - i * 2 * 60 * 60 * 1000),
      },
    });
  }

  console.log("  Usage metrics created.");
  console.log("Seeding complete.");
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
