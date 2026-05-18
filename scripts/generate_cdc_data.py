"""
Generate synthetic CDC WONDER-like mortality datasets.
Creates a tab-delimited file mimicking CDC WONDER Detailed Mortality export.
Covers: deaths by cause, state, year, age group, race, gender.
"""

import csv
import os
import random

random.seed(77)
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "datasets")
os.makedirs(BASE_DIR, exist_ok=True)

# ─── Reference Data ────────────────────────────────────────

STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming",
]

STATE_CODES = {s: f"{i+1:02d}" for i, s in enumerate(STATES)}

YEARS = list(range(2015, 2024))

AGE_GROUPS = [
    "< 1 year", "1-4 years", "5-14 years", "15-24 years",
    "25-34 years", "35-44 years", "45-54 years", "55-64 years",
    "65-74 years", "75-84 years", "85+ years",
]

GENDERS = ["Male", "Female"]

RACES = [
    "White", "Black or African American", "American Indian or Alaska Native",
    "Asian or Pacific Islander",
]

# ICD-10 cause of death categories (leading causes)
CAUSES_OF_DEATH = [
    {"code": "I00-I09", "cause": "Diseases of heart", "category": "Heart Disease"},
    {"code": "C00-C97", "cause": "Malignant neoplasms", "category": "Cancer"},
    {"code": "V01-X59", "cause": "Accidents (unintentional injuries)", "category": "Unintentional Injuries"},
    {"code": "J40-J47", "cause": "Chronic lower respiratory diseases", "category": "CLRD"},
    {"code": "I60-I69", "cause": "Cerebrovascular diseases", "category": "Stroke"},
    {"code": "G30", "cause": "Alzheimer disease", "category": "Alzheimer's"},
    {"code": "E10-E14", "cause": "Diabetes mellitus", "category": "Diabetes"},
    {"code": "J10-J18", "cause": "Influenza and pneumonia", "category": "Flu/Pneumonia"},
    {"code": "K70-K76", "cause": "Chronic liver disease and cirrhosis", "category": "Liver Disease"},
    {"code": "A00-B99", "cause": "Certain infectious and parasitic diseases", "category": "Infectious Disease"},
    {"code": "X60-X84", "cause": "Intentional self-harm (suicide)", "category": "Suicide"},
    {"code": "N00-N07", "cause": "Nephritis, nephrotic syndrome", "category": "Kidney Disease"},
    {"code": "J00-J06", "cause": "Acute respiratory infections", "category": "Respiratory Infections"},
    {"code": "F01-F99", "cause": "Mental and behavioural disorders", "category": "Mental Disorders"},
    {"code": "U07.1", "cause": "COVID-19", "category": "COVID-19"},
]

# Base death rates per 100K by cause (rough approximations)
BASE_RATES = {
    "Heart Disease": 170,
    "Cancer": 150,
    "Unintentional Injuries": 55,
    "CLRD": 40,
    "Stroke": 38,
    "Alzheimer's": 32,
    "Diabetes": 25,
    "Flu/Pneumonia": 15,
    "Liver Disease": 13,
    "Infectious Disease": 10,
    "Suicide": 14,
    "Kidney Disease": 13,
    "Respiratory Infections": 8,
    "Mental Disorders": 6,
    "COVID-19": 0,  # Only from 2020+
}

# State populations (rough, in thousands)
STATE_POPS = {s: random.randint(600, 40000) for s in STATES}
STATE_POPS["California"] = 39500
STATE_POPS["Texas"] = 29100
STATE_POPS["Florida"] = 21500
STATE_POPS["New York"] = 20200
STATE_POPS["Wyoming"] = 577

# Age group multipliers for death rates
AGE_MULTIPLIERS = {
    "< 1 year": 0.8, "1-4 years": 0.05, "5-14 years": 0.03,
    "15-24 years": 0.15, "25-34 years": 0.25, "35-44 years": 0.4,
    "45-54 years": 0.8, "55-64 years": 1.5, "65-74 years": 2.5,
    "75-84 years": 4.0, "85+ years": 8.0,
}


def generate_mortality_data() -> list[dict]:
    """Generate CDC WONDER-style mortality records."""
    rows = []

    for state in STATES:
        for year in YEARS:
            for cause in CAUSES_OF_DEATH:
                category = cause["category"]
                base_rate = BASE_RATES[category]

                # COVID only from 2020+
                if category == "COVID-19":
                    if year < 2020:
                        continue
                    base_rate = {2020: 95, 2021: 115, 2022: 50, 2023: 15}.get(year, 0)

                # Year trend (slight increase in some causes)
                year_factor = 1.0 + (year - 2015) * random.uniform(-0.01, 0.02)

                for age_group in AGE_GROUPS:
                    age_mult = AGE_MULTIPLIERS[age_group]

                    for gender in GENDERS:
                        gender_mult = 1.1 if gender == "Male" else 0.9

                        for race in RACES:
                            race_mult = random.uniform(0.7, 1.4)

                            # Calculate deaths
                            pop_fraction = STATE_POPS[state] * 0.001  # rough scaling
                            rate = base_rate * age_mult * gender_mult * race_mult * year_factor
                            deaths = max(0, int(rate * pop_fraction * random.uniform(0.6, 1.4) / 100))

                            if deaths == 0 and random.random() > 0.3:
                                continue  # Skip zero-death rows most of the time

                            population = int(STATE_POPS[state] * 1000 *
                                           (0.09 if age_group != "85+ years" else 0.02) *
                                           0.5 * 0.3 * random.uniform(0.8, 1.2))

                            crude_rate = round(deaths / max(population, 1) * 100000, 1) if population > 0 else 0

                            rows.append({
                                "Notes": "",
                                "State": state,
                                "State Code": STATE_CODES[state],
                                "Year": year,
                                "Year Code": year,
                                "Cause of death": cause["cause"],
                                "Cause of death Code": cause["code"],
                                "Cause Category": category,
                                "Age Group": age_group,
                                "Age Group Code": AGE_GROUPS.index(age_group) + 1,
                                "Gender": gender,
                                "Gender Code": "M" if gender == "Male" else "F",
                                "Race": race,
                                "Race Code": RACES.index(race) + 1,
                                "Deaths": deaths,
                                "Population": population,
                                "Crude Rate": crude_rate,
                                "Age Adjusted Rate": round(crude_rate * random.uniform(0.85, 1.15), 1),
                            })

    return rows


def main() -> None:
    print("Generating CDC WONDER synthetic mortality dataset...\n")

    rows = generate_mortality_data()

    filepath = os.path.join(BASE_DIR, "cdc_wonder_mortality.csv")
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    print(f"  Written {len(rows):,} rows to cdc_wonder_mortality.csv")
    print(f"\nDone! CDC WONDER file generated in {BASE_DIR}")


if __name__ == "__main__":
    main()
