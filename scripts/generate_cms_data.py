"""
Generate synthetic CMS DE-SynPUF-like datasets.
Creates 4 CSV files mimicking the CMS 2008-2010 Data Entrepreneurs' Synthetic PUF.
- Beneficiary Summary
- Inpatient Claims
- Outpatient Claims
- Prescription Drug Events
"""

import csv
import os
import random
from datetime import datetime, timedelta

random.seed(99)
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "datasets")
os.makedirs(BASE_DIR, exist_ok=True)

# ─── Reference Data ────────────────────────────────────────

STATES = [
    "01", "02", "04", "05", "06", "08", "09", "10", "11", "12",
    "13", "15", "16", "17", "18", "19", "20", "21", "22", "23",
    "24", "25", "26", "27", "28", "29", "30", "31", "32", "33",
    "34", "35", "36", "37", "38", "39", "40", "41", "42", "44",
    "45", "46", "47", "48", "49", "50", "51", "53", "54", "55", "56",
]

COUNTY_CODES = [f"{random.randint(1, 999):03d}" for _ in range(200)]

ICD9_DX = [
    "4011", "25000", "4019", "2724", "41401", "5849", "486", "4280",
    "42731", "51881", "V5861", "496", "2720", "311", "5990", "78060",
    "53081", "2859", "27800", "V4581", "7804", "71590", "78900",
    "4241", "412", "V1582", "4439", "56400", "V4582", "2449",
]

ICD9_PROC = [
    "3893", "3995", "9904", "8856", "9671", "3324", "3722",
    "3612", "8154", "8151", "3961", "9921", "3491", "9390",
]

HCPCS = [
    "99213", "99214", "99232", "99233", "99283", "99284", "99285",
    "71046", "93000", "80053", "85025", "36415", "76700", "43239",
    "29881", "27447", "99291", "G0378", "G0463", "J2001",
]

NDC_CODES = [
    "00006007431", "00006073154", "00078037115", "00093505601",
    "00143314501", "00186077660", "00228206611", "00310075190",
    "00378180510", "00527132437", "00591042601", "00603399221",
    "49999039530", "54569479400", "55111015130", "59762500001",
    "60505257009", "63304034705", "65862001901", "68180072009",
]

DRUG_NAMES = [
    "METFORMIN HCL", "LISINOPRIL", "ATORVASTATIN CALCIUM", "AMLODIPINE BESYLATE",
    "OMEPRAZOLE", "METOPROLOL TARTRATE", "SIMVASTATIN", "LOSARTAN POTASSIUM",
    "ALBUTEROL SULFATE", "HYDROCHLOROTHIAZIDE", "LEVOTHYROXINE SODIUM",
    "GABAPENTIN", "FUROSEMIDE", "PREDNISONE", "AMOXICILLIN",
    "TRAMADOL HCL", "SERTRALINE HCL", "PANTOPRAZOLE SODIUM", "CLOPIDOGREL",
    "WARFARIN SODIUM",
]


def rand_date(start: str, end: str) -> str:
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    d = s + timedelta(days=random.randint(0, (e - s).days))
    return d.strftime("%Y%m%d")


def rand_date_iso(start: str, end: str) -> str:
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    d = s + timedelta(days=random.randint(0, (e - s).days))
    return d.strftime("%Y-%m-%d")


def write_csv(filename: str, rows: list[dict]) -> None:
    filepath = os.path.join(BASE_DIR, filename)
    if not rows:
        return
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Written {len(rows):,} rows to {filename}")


# ─── Generate Beneficiary Summary ──────────────────────────

def generate_beneficiaries(n: int = 5000) -> list[dict]:
    """Generate CMS-style beneficiary summary records."""
    rows = []
    for i in range(n):
        bene_id = f"BENE{i+1:08d}"
        birth_year = random.randint(1920, 1960)
        death_date = ""
        if random.random() < 0.08:
            death_date = rand_date("2008-01-01", "2010-12-31")

        rows.append({
            "DESYNPUF_ID": bene_id,
            "BENE_BIRTH_DT": f"{birth_year}{random.randint(1,12):02d}{random.randint(1,28):02d}",
            "BENE_DEATH_DT": death_date,
            "BENE_SEX_IDENT_CD": random.choice([1, 2]),  # 1=Male, 2=Female
            "BENE_RACE_CD": random.choice([1, 1, 1, 2, 2, 3, 5]),  # 1=White, 2=Black, 3=Other, 5=Hispanic
            "SP_STATE_CODE": random.choice(STATES),
            "BENE_COUNTY_CD": random.choice(COUNTY_CODES),
            "BENE_HI_CVRAGE_TOT_MONS": random.randint(0, 12),
            "BENE_SMI_CVRAGE_TOT_MONS": random.randint(0, 12),
            "BENE_HMO_CVRAGE_TOT_MONS": random.randint(0, 12),
            "PLAN_CVRG_MOS_NUM": random.randint(0, 12),
            "SP_ALZHDMTA": random.choice([1, 2, 2, 2, 2]),
            "SP_CHF": random.choice([1, 2, 2, 2]),
            "SP_CHRNKIDN": random.choice([1, 2, 2, 2, 2]),
            "SP_CNCR": random.choice([1, 2, 2, 2, 2]),
            "SP_COPD": random.choice([1, 2, 2, 2]),
            "SP_DEPRESSN": random.choice([1, 2, 2, 2]),
            "SP_DIABETES": random.choice([1, 1, 2, 2, 2]),
            "SP_ISCHMCHT": random.choice([1, 1, 2, 2]),
            "SP_OSTEOPRS": random.choice([1, 2, 2, 2, 2]),
            "SP_RA_OA": random.choice([1, 2, 2, 2]),
            "SP_STRKETIA": random.choice([1, 2, 2, 2, 2]),
            "MEDREIMB_IP": round(random.uniform(0, 50000), 2),
            "BENRES_IP": round(random.uniform(0, 5000), 2),
            "PPPYMT_IP": round(random.uniform(0, 2000), 2),
            "MEDREIMB_OP": round(random.uniform(0, 15000), 2),
            "BENRES_OP": round(random.uniform(0, 3000), 2),
            "PPPYMT_OP": round(random.uniform(0, 1000), 2),
            "MEDREIMB_CAR": round(random.uniform(0, 20000), 2),
            "BENRES_CAR": round(random.uniform(0, 4000), 2),
            "PPPYMT_CAR": round(random.uniform(0, 1500), 2),
        })
    return rows


# ─── Generate Inpatient Claims ─────────────────────────────

def generate_inpatient_claims(beneficiaries: list[dict], n: int = 8000) -> list[dict]:
    """Generate CMS-style inpatient claims."""
    rows = []
    for i in range(n):
        bene = random.choice(beneficiaries)
        admit = rand_date("2008-01-01", "2010-12-31")
        stay_days = random.randint(1, 21)
        discharge = (datetime.strptime(admit, "%Y%m%d") + timedelta(days=stay_days)).strftime("%Y%m%d")
        num_dx = random.randint(1, 10)
        num_proc = random.randint(0, 6)

        row = {
            "DESYNPUF_ID": bene["DESYNPUF_ID"],
            "CLM_ID": f"IP{i+1:010d}",
            "SEGMENT": 1,
            "CLM_FROM_DT": admit,
            "CLM_THRU_DT": discharge,
            "PRVDR_NUM": f"{random.randint(10000, 99999):05d}",
            "CLM_PMT_AMT": round(random.uniform(2000, 80000), 2),
            "NCH_PRMRY_PYR_CLM_PD_AMT": round(random.uniform(0, 10000), 2),
            "AT_PHYSN_NPI": f"{random.randint(1000000000, 9999999999)}",
            "OP_PHYSN_NPI": f"{random.randint(1000000000, 9999999999)}",
            "OT_PHYSN_NPI": f"{random.randint(1000000000, 9999999999)}",
            "CLM_ADMSN_DT": admit,
            "ADMTNG_ICD9_DGNS_CD": random.choice(ICD9_DX),
            "CLM_PASS_THRU_PER_DIEM_AMT": round(random.uniform(0, 500), 2),
            "NCH_BENE_IP_DDCTBL_AMT": round(random.uniform(0, 1200), 2),
            "NCH_BENE_PTA_COINSRNC_LBLTY_AM": round(random.uniform(0, 5000), 2),
            "NCH_BENE_BLOOD_DDCTBL_LBLTY_AM": round(random.uniform(0, 200), 2),
            "CLM_UTLZTN_DAY_CNT": stay_days,
            "NCH_BENE_DSCHRG_DT": discharge,
            "CLM_DRG_CD": random.randint(1, 999),
        }

        # Add diagnosis codes (up to 10)
        for j in range(1, 11):
            row[f"ICD9_DGNS_CD_{j}"] = random.choice(ICD9_DX) if j <= num_dx else ""

        # Add procedure codes (up to 6)
        for j in range(1, 7):
            row[f"ICD9_PRCDR_CD_{j}"] = random.choice(ICD9_PROC) if j <= num_proc else ""

        # HCPCS codes
        row["HCPCS_CD_1"] = random.choice(HCPCS)

        rows.append(row)
    return rows


# ─── Generate Outpatient Claims ────────────────────────────

def generate_outpatient_claims(beneficiaries: list[dict], n: int = 15000) -> list[dict]:
    """Generate CMS-style outpatient claims."""
    rows = []
    for i in range(n):
        bene = random.choice(beneficiaries)
        svc_date = rand_date("2008-01-01", "2010-12-31")
        num_dx = random.randint(1, 10)
        num_proc = random.randint(0, 6)

        row = {
            "DESYNPUF_ID": bene["DESYNPUF_ID"],
            "CLM_ID": f"OP{i+1:010d}",
            "SEGMENT": 1,
            "CLM_FROM_DT": svc_date,
            "CLM_THRU_DT": svc_date,
            "PRVDR_NUM": f"{random.randint(10000, 99999):05d}",
            "CLM_PMT_AMT": round(random.uniform(50, 15000), 2),
            "NCH_PRMRY_PYR_CLM_PD_AMT": round(random.uniform(0, 3000), 2),
            "AT_PHYSN_NPI": f"{random.randint(1000000000, 9999999999)}",
            "OP_PHYSN_NPI": f"{random.randint(1000000000, 9999999999)}",
            "OT_PHYSN_NPI": f"{random.randint(1000000000, 9999999999)}",
            "NCH_BENE_BLOOD_DDCTBL_LBLTY_AM": round(random.uniform(0, 100), 2),
            "NCH_BENE_PTB_DDCTBL_AMT": round(random.uniform(0, 200), 2),
            "NCH_BENE_PTB_COINSRNC_AMT": round(random.uniform(0, 3000), 2),
            "ADMTNG_ICD9_DGNS_CD": random.choice(ICD9_DX),
        }

        for j in range(1, 11):
            row[f"ICD9_DGNS_CD_{j}"] = random.choice(ICD9_DX) if j <= num_dx else ""

        for j in range(1, 7):
            row[f"ICD9_PRCDR_CD_{j}"] = random.choice(ICD9_PROC) if j <= num_proc else ""

        for j in range(1, 46):
            if j <= random.randint(1, 5):
                row[f"HCPCS_CD_{j}"] = random.choice(HCPCS)
            else:
                row[f"HCPCS_CD_{j}"] = ""

        rows.append(row)
    return rows


# ─── Generate Prescription Drug Events ─────────────────────

def generate_prescription_events(beneficiaries: list[dict], n: int = 25000) -> list[dict]:
    """Generate CMS-style prescription drug event records."""
    rows = []
    for i in range(n):
        bene = random.choice(beneficiaries)
        svc_date = rand_date("2008-01-01", "2010-12-31")
        drug_idx = random.randint(0, len(NDC_CODES) - 1)
        qty = random.choice([30, 30, 30, 60, 90, 14, 7, 10, 20, 100])
        days = random.choice([30, 30, 30, 60, 90, 14, 7, 10])

        rows.append({
            "DESYNPUF_ID": bene["DESYNPUF_ID"],
            "PDE_ID": f"PDE{i+1:010d}",
            "SRVC_DT": svc_date,
            "PROD_SRVC_ID": NDC_CODES[drug_idx],
            "QTY_DSPNSD_NUM": qty,
            "DAYS_SUPLY_NUM": days,
            "PTNT_PAY_AMT": round(random.uniform(0, 200), 2),
            "TOT_RX_CST_AMT": round(random.uniform(5, 2000), 2),
            "DRUG_NAME": DRUG_NAMES[drug_idx % len(DRUG_NAMES)],
            "PRSCRBR_ID": f"{random.randint(1000000000, 9999999999)}",
            "SRVC_PRVDR_ID": f"{random.randint(1000000, 9999999)}",
        })
    return rows


def main() -> None:
    print("Generating CMS DE-SynPUF synthetic datasets...\n")

    print("1. Generating beneficiary summary...")
    beneficiaries = generate_beneficiaries(5000)
    write_csv("cms_beneficiary_summary.csv", beneficiaries)

    print("2. Generating inpatient claims...")
    inpatient = generate_inpatient_claims(beneficiaries, 8000)
    write_csv("cms_inpatient_claims.csv", inpatient)

    print("3. Generating outpatient claims...")
    outpatient = generate_outpatient_claims(beneficiaries, 15000)
    write_csv("cms_outpatient_claims.csv", outpatient)

    print("4. Generating prescription drug events...")
    prescriptions = generate_prescription_events(beneficiaries, 25000)
    write_csv("cms_prescription_events.csv", prescriptions)

    print(f"\nDone! CMS files generated in {BASE_DIR}")


if __name__ == "__main__":
    main()
