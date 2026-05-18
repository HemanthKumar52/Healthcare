"""
Generate realistic sample healthcare CSV datasets for the Healthcare Data Marketplace.
Creates 15 CSV files in data/datasets/ covering all 5 domains.
"""

import csv
import os
import random
from datetime import datetime, timedelta

random.seed(42)
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "datasets")
os.makedirs(BASE_DIR, exist_ok=True)

# ─── Reference Data ────────────────────────────────────────

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Daniel", "Lisa", "Matthew", "Nancy",
    "Anthony", "Betty", "Mark", "Margaret", "Donald", "Sandra", "Steven", "Ashley",
    "Paul", "Dorothy", "Andrew", "Kimberly", "Joshua", "Emily", "Kenneth", "Donna",
    "Aisha", "Raj", "Mei", "Carlos", "Fatima", "Olga", "Hiroshi", "Priya", "Ahmed", "Ingrid",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Patel", "Kim", "Nguyen", "Chen", "Singh", "Yamamoto", "Mueller", "Ivanov",
]

DEPARTMENTS = [
    {"id": "DEPT001", "name": "Emergency Medicine", "floor": 1, "building": "Main"},
    {"id": "DEPT002", "name": "Cardiology", "floor": 3, "building": "Main"},
    {"id": "DEPT003", "name": "Orthopedics", "floor": 4, "building": "Main"},
    {"id": "DEPT004", "name": "Neurology", "floor": 5, "building": "Main"},
    {"id": "DEPT005", "name": "Oncology", "floor": 6, "building": "West Wing"},
    {"id": "DEPT006", "name": "Pediatrics", "floor": 2, "building": "East Wing"},
    {"id": "DEPT007", "name": "Internal Medicine", "floor": 3, "building": "Main"},
    {"id": "DEPT008", "name": "Pulmonology", "floor": 4, "building": "West Wing"},
    {"id": "DEPT009", "name": "Radiology", "floor": 1, "building": "West Wing"},
    {"id": "DEPT010", "name": "General Surgery", "floor": 2, "building": "Main"},
]

SPECIALTIES = [
    "Emergency Medicine", "Cardiology", "Orthopedics", "Neurology", "Oncology",
    "Pediatrics", "Internal Medicine", "Pulmonology", "Radiology", "General Surgery",
    "Dermatology", "Gastroenterology", "Endocrinology", "Nephrology", "Urology",
]

ICD10_CODES = [
    ("I10", "Essential hypertension"), ("E11.9", "Type 2 diabetes mellitus"),
    ("J06.9", "Acute upper respiratory infection"), ("M54.5", "Low back pain"),
    ("J44.1", "COPD with acute exacerbation"), ("I25.10", "Coronary artery disease"),
    ("N39.0", "Urinary tract infection"), ("K21.0", "GERD with esophagitis"),
    ("F32.1", "Major depressive disorder"), ("J18.9", "Pneumonia, unspecified"),
    ("E78.5", "Hyperlipidemia"), ("G43.909", "Migraine, unspecified"),
    ("M79.3", "Panniculitis"), ("R10.9", "Abdominal pain"), ("K80.20", "Gallstone"),
]

CPT_CODES = [
    ("99213", "Office visit, established patient, level 3"),
    ("99214", "Office visit, established patient, level 4"),
    ("99283", "Emergency department visit, level 3"),
    ("99284", "Emergency department visit, level 4"),
    ("71046", "Chest X-ray, 2 views"),
    ("93000", "Electrocardiogram, 12-lead"),
    ("80053", "Comprehensive metabolic panel"),
    ("85025", "Complete blood count with differential"),
    ("36415", "Venipuncture"),
    ("99232", "Subsequent hospital care, level 2"),
]

LAB_TESTS = [
    {"name": "Complete Blood Count", "code": "CBC", "unit": "10^3/uL", "low": 4.5, "high": 11.0},
    {"name": "Hemoglobin", "code": "HGB", "unit": "g/dL", "low": 12.0, "high": 17.5},
    {"name": "Glucose, Fasting", "code": "GLU", "unit": "mg/dL", "low": 70, "high": 100},
    {"name": "Creatinine", "code": "CREAT", "unit": "mg/dL", "low": 0.6, "high": 1.2},
    {"name": "ALT", "code": "ALT", "unit": "U/L", "low": 7, "high": 56},
    {"name": "Total Cholesterol", "code": "CHOL", "unit": "mg/dL", "low": 0, "high": 200},
    {"name": "HbA1c", "code": "A1C", "unit": "%", "low": 4.0, "high": 5.7},
    {"name": "TSH", "code": "TSH", "unit": "mIU/L", "low": 0.4, "high": 4.0},
    {"name": "Potassium", "code": "K", "unit": "mEq/L", "low": 3.5, "high": 5.0},
    {"name": "Sodium", "code": "NA", "unit": "mEq/L", "low": 136, "high": 145},
]

MEDICATIONS = [
    ("Metformin", "500mg", "BID", "oral"), ("Lisinopril", "10mg", "QD", "oral"),
    ("Atorvastatin", "20mg", "QD", "oral"), ("Omeprazole", "20mg", "QD", "oral"),
    ("Amlodipine", "5mg", "QD", "oral"), ("Metoprolol", "25mg", "BID", "oral"),
    ("Levothyroxine", "50mcg", "QD", "oral"), ("Prednisone", "10mg", "QD", "oral"),
    ("Amoxicillin", "500mg", "TID", "oral"), ("Ibuprofen", "400mg", "TID", "oral"),
    ("Gabapentin", "300mg", "TID", "oral"), ("Sertraline", "50mg", "QD", "oral"),
    ("Albuterol", "90mcg", "Q4H PRN", "inhaled"), ("Insulin Glargine", "20 units", "QD", "subcutaneous"),
]

INSURANCE_COMPANIES = [
    "Blue Cross Blue Shield", "Aetna", "UnitedHealth", "Cigna", "Humana",
    "Kaiser Permanente", "Medicare", "Medicaid", "Anthem", "Centene",
]

ROOMS = []
for floor in range(1, 7):
    for room in range(1, 21):
        for bed in ["A", "B"]:
            ROOMS.append({
                "room_id": f"R{floor}{room:02d}{bed}",
                "room_number": f"{floor}{room:02d}",
                "bed_label": bed,
                "floor": floor,
                "room_type": random.choice(["Standard", "ICU", "Private", "Semi-Private"]),
                "department_id": DEPARTMENTS[min(floor - 1, len(DEPARTMENTS) - 1)]["id"],
            })


def rand_date(start_year: int = 2023, end_year: int = 2025) -> str:
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = (end - start).days
    d = start + timedelta(days=random.randint(0, delta))
    return d.strftime("%Y-%m-%d")


def rand_datetime(start_year: int = 2023, end_year: int = 2025) -> str:
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = int((end - start).total_seconds())
    d = start + timedelta(seconds=random.randint(0, delta))
    return d.strftime("%Y-%m-%d %H:%M:%S")


def rand_phone() -> str:
    return f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"


def write_csv(filename: str, rows: list[dict]) -> None:
    filepath = os.path.join(BASE_DIR, filename)
    if not rows:
        return
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Written {len(rows):,} rows to {filename}")


# ─── Generate Datasets ────────────────────────────────────

def generate_departments() -> list[dict]:
    return [
        {
            "department_id": d["id"],
            "department_name": d["name"],
            "floor": d["floor"],
            "building": d["building"],
            "head_doctor_id": f"DOC{i+1:04d}",
            "phone": rand_phone(),
            "status": "Active",
        }
        for i, d in enumerate(DEPARTMENTS)
    ]


def generate_doctors(n: int = 60) -> list[dict]:
    doctors = []
    for i in range(n):
        dept = random.choice(DEPARTMENTS)
        doctors.append({
            "doctor_id": f"DOC{i+1:04d}",
            "first_name": random.choice(FIRST_NAMES),
            "last_name": random.choice(LAST_NAMES),
            "specialty": random.choice(SPECIALTIES),
            "department_id": dept["id"],
            "email": f"dr.{LAST_NAMES[i % len(LAST_NAMES)].lower()}{i}@hospital.org",
            "phone": rand_phone(),
            "license_number": f"MD{random.randint(100000, 999999)}",
            "hire_date": rand_date(2005, 2023),
            "status": random.choice(["Active"] * 9 + ["On Leave"]),
        })
    return doctors


def generate_patients(n: int = 2000) -> list[dict]:
    patients = []
    for i in range(n):
        dob_year = random.randint(1940, 2010)
        patients.append({
            "patient_id": f"PAT{i+1:06d}",
            "first_name": random.choice(FIRST_NAMES),
            "last_name": random.choice(LAST_NAMES),
            "date_of_birth": f"{dob_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            "gender": random.choice(["Male", "Female", "Other"]),
            "race": random.choice(["White", "Black", "Asian", "Hispanic", "Other"]),
            "ethnicity": random.choice(["Hispanic", "Non-Hispanic"]),
            "address": f"{random.randint(100,9999)} {random.choice(['Main', 'Oak', 'Elm', 'Pine', 'Cedar'])} {random.choice(['St', 'Ave', 'Blvd', 'Dr'])}",
            "city": random.choice(["Springfield", "Riverside", "Georgetown", "Franklin", "Madison"]),
            "state": random.choice(["CA", "TX", "NY", "FL", "IL", "PA", "OH"]),
            "zip_code": f"{random.randint(10000, 99999)}",
            "phone": rand_phone(),
            "email": f"patient{i+1}@email.com",
            "insurance_provider": random.choice(INSURANCE_COMPANIES),
            "insurance_id": f"INS{random.randint(100000000, 999999999)}",
            "primary_doctor_id": f"DOC{random.randint(1, 60):04d}",
            "registration_date": rand_date(2020, 2024),
            "status": random.choice(["Active"] * 8 + ["Inactive", "Deceased"]),
        })
    return patients


def generate_encounters(patients: list[dict], n: int = 8000) -> list[dict]:
    encounters = []
    encounter_types = ["Inpatient", "Outpatient", "Emergency", "Observation"]
    for i in range(n):
        pat = random.choice(patients)
        admit = rand_datetime()
        stay_hours = random.randint(1, 240) if random.random() > 0.3 else random.randint(1, 8)
        discharge = (datetime.strptime(admit, "%Y-%m-%d %H:%M:%S") + timedelta(hours=stay_hours)).strftime("%Y-%m-%d %H:%M:%S")
        encounters.append({
            "encounter_id": f"ENC{i+1:08d}",
            "patient_id": pat["patient_id"],
            "encounter_type": random.choice(encounter_types),
            "admit_date": admit,
            "discharge_date": discharge if random.random() > 0.05 else "",
            "department_id": random.choice(DEPARTMENTS)["id"],
            "attending_doctor_id": f"DOC{random.randint(1, 60):04d}",
            "admission_source": random.choice(["ER", "Physician Referral", "Transfer", "Self-referral", "Walk-in"]),
            "discharge_disposition": random.choice(["Home", "SNF", "Rehab", "AMA", "Expired", "Home Health"]),
            "primary_diagnosis_code": random.choice(ICD10_CODES)[0],
            "status": random.choice(["Completed"] * 9 + ["In Progress"]),
        })
    return encounters


def generate_diagnoses(encounters: list[dict]) -> list[dict]:
    diagnoses = []
    idx = 0
    for enc in encounters:
        num_dx = random.randint(1, 4)
        used_codes = set()
        for rank in range(1, num_dx + 1):
            code, desc = random.choice(ICD10_CODES)
            if code in used_codes:
                continue
            used_codes.add(code)
            idx += 1
            diagnoses.append({
                "diagnosis_id": f"DX{idx:08d}",
                "encounter_id": enc["encounter_id"],
                "patient_id": enc["patient_id"],
                "icd10_code": code,
                "description": desc,
                "diagnosis_type": "Primary" if rank == 1 else "Secondary",
                "diagnosis_rank": rank,
                "diagnosed_by": enc["attending_doctor_id"],
                "diagnosis_date": enc["admit_date"][:10],
            })
    return diagnoses


def generate_procedures(encounters: list[dict]) -> list[dict]:
    procedures = []
    idx = 0
    for enc in encounters:
        if random.random() > 0.6:
            continue
        num_proc = random.randint(1, 3)
        for _ in range(num_proc):
            code, desc = random.choice(CPT_CODES)
            idx += 1
            procedures.append({
                "procedure_id": f"PROC{idx:08d}",
                "encounter_id": enc["encounter_id"],
                "patient_id": enc["patient_id"],
                "cpt_code": code,
                "description": desc,
                "procedure_date": enc["admit_date"][:10],
                "performing_doctor_id": enc["attending_doctor_id"],
                "department_id": enc["department_id"],
                "status": "Completed",
                "notes": "",
            })
    return procedures


def generate_prescriptions(encounters: list[dict]) -> list[dict]:
    prescriptions = []
    idx = 0
    for enc in encounters:
        if random.random() > 0.7:
            continue
        num_rx = random.randint(1, 4)
        for _ in range(num_rx):
            med, dose, freq, route = random.choice(MEDICATIONS)
            idx += 1
            start = enc["admit_date"][:10]
            prescriptions.append({
                "prescription_id": f"RX{idx:08d}",
                "encounter_id": enc["encounter_id"],
                "patient_id": enc["patient_id"],
                "doctor_id": enc["attending_doctor_id"],
                "medication_name": med,
                "dosage": dose,
                "frequency": freq,
                "route": route,
                "start_date": start,
                "end_date": (datetime.strptime(start, "%Y-%m-%d") + timedelta(days=random.randint(7, 90))).strftime("%Y-%m-%d"),
                "refills": random.randint(0, 5),
                "status": random.choice(["Active", "Completed", "Discontinued"]),
            })
    return prescriptions


def generate_lab_results(encounters: list[dict]) -> list[dict]:
    results = []
    idx = 0
    for enc in encounters:
        if random.random() > 0.5:
            continue
        num_tests = random.randint(1, 5)
        for _ in range(num_tests):
            test = random.choice(LAB_TESTS)
            value = round(random.uniform(test["low"] * 0.7, test["high"] * 1.4), 2)
            flag = "Normal"
            if value < test["low"]:
                flag = "Low"
            elif value > test["high"]:
                flag = "High"
            idx += 1
            results.append({
                "lab_result_id": f"LAB{idx:08d}",
                "encounter_id": enc["encounter_id"],
                "patient_id": enc["patient_id"],
                "test_name": test["name"],
                "test_code": test["code"],
                "result_value": value,
                "unit": test["unit"],
                "reference_low": test["low"],
                "reference_high": test["high"],
                "abnormal_flag": flag,
                "ordering_doctor_id": enc["attending_doctor_id"],
                "result_date": enc["admit_date"][:10],
                "status": "Final",
            })
    return results


def generate_vitals(encounters: list[dict]) -> list[dict]:
    vitals = []
    idx = 0
    for enc in encounters:
        if random.random() > 0.6:
            continue
        num_readings = random.randint(1, 4)
        for r in range(num_readings):
            idx += 1
            ts = datetime.strptime(enc["admit_date"], "%Y-%m-%d %H:%M:%S") + timedelta(hours=r * 4)
            vitals.append({
                "vital_id": f"VIT{idx:08d}",
                "encounter_id": enc["encounter_id"],
                "patient_id": enc["patient_id"],
                "recorded_at": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "temperature_f": round(random.uniform(96.5, 103.0), 1),
                "heart_rate": random.randint(55, 120),
                "systolic_bp": random.randint(90, 180),
                "diastolic_bp": random.randint(55, 110),
                "respiratory_rate": random.randint(12, 28),
                "oxygen_saturation": round(random.uniform(88.0, 100.0), 1),
                "weight_lbs": round(random.uniform(100, 300), 1),
                "height_in": round(random.uniform(58, 76), 1),
                "recorded_by": f"DOC{random.randint(1, 60):04d}",
            })
    return vitals


def generate_appointments(patients: list[dict], n: int = 5000) -> list[dict]:
    appointments = []
    statuses = ["Completed", "Completed", "Completed", "No-Show", "Cancelled", "Scheduled"]
    for i in range(n):
        pat = random.choice(patients)
        dt = rand_datetime()
        appointments.append({
            "appointment_id": f"APT{i+1:08d}",
            "patient_id": pat["patient_id"],
            "doctor_id": f"DOC{random.randint(1, 60):04d}",
            "department_id": random.choice(DEPARTMENTS)["id"],
            "appointment_date": dt[:10],
            "appointment_time": dt[11:],
            "duration_minutes": random.choice([15, 30, 30, 45, 60]),
            "appointment_type": random.choice(["Follow-up", "New Patient", "Annual Physical", "Urgent", "Consultation", "Procedure"]),
            "status": random.choice(statuses),
            "check_in_time": dt[11:] if random.random() > 0.2 else "",
            "notes": "",
        })
    return appointments


def generate_admissions(encounters: list[dict]) -> list[dict]:
    admissions = []
    idx = 0
    for enc in encounters:
        if enc["encounter_type"] not in ["Inpatient", "Observation"]:
            continue
        idx += 1
        room = random.choice(ROOMS)
        admissions.append({
            "admission_id": f"ADM{idx:06d}",
            "encounter_id": enc["encounter_id"],
            "patient_id": enc["patient_id"],
            "room_id": room["room_id"],
            "bed_label": room["bed_label"],
            "admit_date": enc["admit_date"],
            "discharge_date": enc["discharge_date"],
            "department_id": enc["department_id"],
            "admission_type": random.choice(["Emergency", "Elective", "Urgent", "Newborn"]),
            "attending_doctor_id": enc["attending_doctor_id"],
            "insurance_verified": random.choice(["Yes", "No", "Pending"]),
        })
    return admissions


def generate_rooms_beds() -> list[dict]:
    return [
        {
            "room_id": r["room_id"],
            "room_number": r["room_number"],
            "bed_label": r["bed_label"],
            "floor": r["floor"],
            "room_type": r["room_type"],
            "department_id": r["department_id"],
            "is_occupied": random.choice(["Yes", "No"]),
            "last_cleaned": rand_datetime(2025, 2025),
            "equipment": random.choice(["Standard", "Cardiac Monitor", "Ventilator", "Standard", "IV Pump"]),
        }
        for r in ROOMS[:200]
    ]


def generate_billing(encounters: list[dict]) -> list[dict]:
    billing = []
    idx = 0
    for enc in encounters:
        if random.random() > 0.85:
            continue
        idx += 1
        total = round(random.uniform(150, 50000), 2)
        insurance_paid = round(total * random.uniform(0.5, 0.95), 2)
        patient_resp = round(total - insurance_paid, 2)
        billing.append({
            "billing_id": f"BILL{idx:08d}",
            "encounter_id": enc["encounter_id"],
            "patient_id": enc["patient_id"],
            "total_charge": total,
            "insurance_paid": insurance_paid,
            "patient_responsibility": patient_resp,
            "billing_date": enc["admit_date"][:10],
            "due_date": (datetime.strptime(enc["admit_date"][:10], "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d"),
            "status": random.choice(["Paid", "Paid", "Pending", "Overdue", "In Collections", "Denied"]),
            "billing_code": random.choice(CPT_CODES)[0],
            "department_id": enc["department_id"],
        })
    return billing


def generate_insurance_claims(billing: list[dict]) -> list[dict]:
    claims = []
    for i, bill in enumerate(billing):
        claims.append({
            "claim_id": f"CLM{i+1:08d}",
            "billing_id": bill["billing_id"],
            "patient_id": bill["patient_id"],
            "insurance_provider": random.choice(INSURANCE_COMPANIES),
            "claim_amount": bill["total_charge"],
            "approved_amount": bill["insurance_paid"],
            "claim_date": bill["billing_date"],
            "processed_date": (datetime.strptime(bill["billing_date"], "%Y-%m-%d") + timedelta(days=random.randint(5, 45))).strftime("%Y-%m-%d"),
            "status": random.choice(["Approved", "Approved", "Approved", "Denied", "Pending", "Under Review"]),
            "denial_reason": random.choice(["", "", "", "Not medically necessary", "Pre-auth required", "Out of network", "Duplicate claim"]),
            "claim_type": random.choice(["Professional", "Institutional", "Pharmacy"]),
        })
    return claims


def generate_payments(billing: list[dict]) -> list[dict]:
    payments = []
    idx = 0
    for bill in billing:
        if bill["status"] in ["Denied", "In Collections"]:
            continue
        if random.random() > 0.8:
            continue
        idx += 1
        payments.append({
            "payment_id": f"PAY{idx:08d}",
            "billing_id": bill["billing_id"],
            "patient_id": bill["patient_id"],
            "amount": bill["insurance_paid"] if random.random() > 0.3 else bill["patient_responsibility"],
            "payment_date": (datetime.strptime(bill["billing_date"], "%Y-%m-%d") + timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"),
            "payment_method": random.choice(["Insurance", "Credit Card", "Check", "Cash", "Wire Transfer", "Insurance"]),
            "payment_source": random.choice(["Insurance", "Patient", "Insurance", "Insurance"]),
            "transaction_id": f"TXN{random.randint(10000000, 99999999)}",
            "status": random.choice(["Completed", "Completed", "Pending", "Refunded"]),
        })
    return payments


def main() -> None:
    print("Generating Healthcare Data Marketplace sample datasets...\n")

    print("1. Generating departments...")
    departments = generate_departments()
    write_csv("departments.csv", departments)

    print("2. Generating doctors...")
    doctors = generate_doctors(60)
    write_csv("doctors.csv", doctors)

    print("3. Generating patients...")
    patients = generate_patients(2000)
    write_csv("patients.csv", patients)

    print("4. Generating encounters...")
    encounters = generate_encounters(patients, 8000)
    write_csv("encounters.csv", encounters)

    print("5. Generating diagnoses...")
    diagnoses = generate_diagnoses(encounters)
    write_csv("diagnoses.csv", diagnoses)

    print("6. Generating procedures...")
    procedures = generate_procedures(encounters)
    write_csv("procedures.csv", procedures)

    print("7. Generating prescriptions...")
    prescriptions = generate_prescriptions(encounters)
    write_csv("prescriptions.csv", prescriptions)

    print("8. Generating lab results...")
    lab_results = generate_lab_results(encounters)
    write_csv("lab_results.csv", lab_results)

    print("9. Generating vitals...")
    vitals = generate_vitals(encounters)
    write_csv("vitals.csv", vitals)

    print("10. Generating appointments...")
    appointments = generate_appointments(patients, 5000)
    write_csv("appointments.csv", appointments)

    print("11. Generating admissions...")
    admissions = generate_admissions(encounters)
    write_csv("admissions.csv", admissions)

    print("12. Generating rooms & beds...")
    rooms_beds = generate_rooms_beds()
    write_csv("rooms_beds.csv", rooms_beds)

    print("13. Generating billing...")
    billing = generate_billing(encounters)
    write_csv("billing.csv", billing)

    print("14. Generating insurance claims...")
    insurance_claims = generate_insurance_claims(billing)
    write_csv("insurance_claims.csv", insurance_claims)

    print("15. Generating payments...")
    payments = generate_payments(billing)
    write_csv("payments.csv", payments)

    print(f"\nDone! All 15 CSV files generated in {BASE_DIR}")


if __name__ == "__main__":
    main()
