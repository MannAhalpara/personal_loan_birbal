"""Script to generate 150 synthetic sample applicant profiles for applicants.csv."""

import csv
import random

random.seed(42)

profiles = []

# Archetype generators to guarantee balanced representation
# We will create 150 profiles with explicit scenarios:

def clamp(val, min_v, max_v):
    return max(min_v, min(max_v, val))

for i in range(1, 151):
    app_id = f"APP{i:03d}"
    
    # Bucket allocation to ensure rich mix
    if 1 <= i <= 20:
        # Prime eligible applicants (will pass all/most lenders)
        age = random.randint(25, 48)
        monthly_income = random.choice([40000, 50000, 65000, 75000, 90000, 120000, 150000])
        employment_type = "salaried"
        work_exp = random.randint(24, 140)
        credit_score = random.randint(750, 825)
        # Moderate EMI, FOIR <= 30%
        existing_emi = int(monthly_income * random.uniform(0.0, 0.25))
        city_category = random.choice(["metro", "non-metro"])
        
    elif 21 <= i <= 40:
        # Low-income applicants (below 20k, will fail most bank cutoffs)
        age = random.randint(21, 55)
        monthly_income = random.choice([12000, 14000, 15500, 16000, 17500, 18500, 19500])
        employment_type = random.choice(["salaried", "salaried", "self-employed"])
        work_exp = random.randint(12, 90)
        credit_score = random.randint(650, 760)
        existing_emi = int(monthly_income * random.uniform(0.0, 0.35))
        city_category = random.choice(["metro", "non-metro"])
        
    elif 41 <= i <= 60:
        # High existing EMI (FOIR > 50%, fails debt-to-income)
        age = random.randint(26, 52)
        monthly_income = random.choice([35000, 45000, 60000, 80000, 100000])
        employment_type = "salaried"
        work_exp = random.randint(24, 120)
        credit_score = random.randint(710, 790)
        # FOIR between 55% and 80%
        existing_emi = int(monthly_income * random.uniform(0.55, 0.80))
        city_category = random.choice(["metro", "non-metro"])
        
    elif 61 <= i <= 80:
        # Poor / Low Credit score (< 660, fails credit check)
        age = random.randint(23, 50)
        monthly_income = random.choice([30000, 40000, 55000, 70000])
        employment_type = random.choice(["salaried", "salaried", "self-employed"])
        work_exp = random.randint(18, 100)
        credit_score = random.randint(510, 650)
        existing_emi = int(monthly_income * random.uniform(0.0, 0.30))
        city_category = random.choice(["metro", "non-metro"])
        
    elif 81 <= i <= 95:
        # Borderline credit score (670-695, passes SBI/Bajaj, fails others)
        age = random.randint(24, 50)
        monthly_income = random.choice([30000, 40000, 50000, 65000])
        employment_type = "salaried"
        work_exp = random.randint(24, 80)
        credit_score = random.choice([670, 675, 680, 685, 690, 695])
        existing_emi = int(monthly_income * random.uniform(0.1, 0.35))
        city_category = random.choice(["metro", "non-metro"])
        
    elif 96 <= i <= 110:
        # Self-employed applicants with good financial profile
        age = random.randint(28, 55)
        monthly_income = random.choice([45000, 60000, 85000, 110000, 140000])
        employment_type = "self-employed"
        work_exp = random.randint(25, 120)
        credit_score = random.randint(720, 810)
        existing_emi = int(monthly_income * random.uniform(0.0, 0.30))
        city_category = random.choice(["metro", "non-metro"])
        
    elif 111 <= i <= 120:
        # Limited work experience (< 12 months, fails work exp)
        age = random.randint(21, 26)
        monthly_income = random.choice([28000, 35000, 42000, 50000])
        employment_type = "salaried"
        work_exp = random.choice([2, 4, 6, 8, 9, 10, 11])
        credit_score = random.randint(710, 770)
        existing_emi = int(monthly_income * random.uniform(0.0, 0.20))
        city_category = random.choice(["metro", "non-metro"])
        
    elif 121 <= i <= 130:
        # Age edge cases: either underage (< 21) or elderly (> 58 / > 60)
        is_young = (i % 2 == 1)
        if is_young:
            age = random.choice([18, 19, 20])
            monthly_income = random.choice([25000, 30000, 35000])
            work_exp = random.randint(6, 18)
        else:
            age = random.choice([59, 61, 62, 63, 65])
            monthly_income = random.choice([45000, 65000, 90000])
            work_exp = random.randint(60, 240)
        employment_type = random.choice(["salaried", "self-employed"])
        credit_score = random.randint(700, 780)
        existing_emi = int(monthly_income * random.uniform(0.0, 0.25))
        city_category = random.choice(["metro", "non-metro"])
        
    else:
        # 131 to 150: Realistic mixed middle-class borrowers
        age = random.randint(24, 52)
        monthly_income = random.choice([22000, 26000, 32000, 38000, 48000, 58000])
        employment_type = random.choice(["salaried", "salaried", "salaried", "self-employed"])
        work_exp = random.randint(14, 110)
        credit_score = random.randint(675, 780)
        existing_emi = int(monthly_income * random.uniform(0.1, 0.45))
        city_category = random.choice(["metro", "non-metro"])

    profiles.append({
        "applicant_id": app_id,
        "age": age,
        "monthly_income": monthly_income,
        "employment_type": employment_type,
        "work_experience_months": work_exp,
        "credit_score": credit_score,
        "existing_emi": existing_emi,
        "city_category": city_category
    })

import os

output_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "applicants.csv")
with open(output_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "applicant_id", "age", "monthly_income", "employment_type",
        "work_experience_months", "credit_score", "existing_emi", "city_category"
    ])
    writer.writeheader()
    writer.writerows(profiles)

print(f"Generated {len(profiles)} synthetic profiles in {output_csv} successfully.")
