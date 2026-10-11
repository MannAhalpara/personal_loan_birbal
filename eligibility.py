"""eligibility.py - Core evaluation engine for Personal Loan Eligibility Model.

This module provides functions to:
1. Load lender rules and sample applicants from CSV files.
2. Validate input parameters for new and existing applicants.
3. Evaluate applicants against rule-based eligibility criteria for 8 Indian lenders.
4. Distinguish between published criteria and assumed rules.
5. Provide indicative loan amount, interest rate range, tenure, and best recommendation.
"""

import csv
import os
from typing import Dict, List, Tuple, Any, Optional

DISCLAIMER = (
    "NOTE: This is an indicative eligibility estimate based on public lender "
    "criteria and basic rule assumptions. It is NOT an official loan approval, "
    "guarantee, or financial advice. Final approval depends on bank verification."
)


def get_default_file_path(filename: str) -> str:
    """Return the absolute path to a file located in the same directory as this module."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, filename)


def load_lenders(csv_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load lender rules from lenders.csv."""
    if csv_path is None:
        csv_path = get_default_file_path("lenders.csv")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Lenders file not found at: {csv_path}")

    lenders = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            allowed_emp = [e.strip().lower() for e in row["allowed_employment"].split(",")]
            lender = {
                "lender_id": row["lender_id"].strip(),
                "lender_name": row["lender_name"].strip(),
                "lender_type": row["lender_type"].strip(),
                "min_age": int(row["min_age"]),
                "max_age": int(row["max_age"]),
                "min_income_inr": float(row["min_income_inr"]),
                "min_income_non_metro_inr": float(row.get("min_income_non_metro_inr", row["min_income_inr"])),
                "allowed_employment": allowed_emp,
                "min_experience_months": int(row["min_experience_months"]),
                "min_credit_score": int(row["min_credit_score"]),
                "max_foir_pct": float(row["max_foir_pct"]),
                "min_interest_rate_pct": float(row["min_interest_rate_pct"]),
                "max_interest_rate_pct": float(row["max_interest_rate_pct"]),
                "max_tenure_months": int(row["max_tenure_months"]),
                "max_loan_amount_inr": int(row["max_loan_amount_inr"]),
                "source_url": row["source_url"].strip(),
                "date_checked": row["date_checked"].strip(),
                "notes": row["notes"].strip(),
            }
            lenders.append(lender)
    return lenders


def load_applicants(csv_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load synthetic sample applicant profiles from applicants.csv."""
    if csv_path is None:
        csv_path = get_default_file_path("applicants.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Applicants file not found at: {csv_path}")

    applicants = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            applicant = {
                "applicant_id": row["applicant_id"].strip(),
                "age": int(row["age"]),
                "monthly_income": float(row["monthly_income"]),
                "employment_type": row["employment_type"].strip().lower(),
                "work_experience_months": int(row["work_experience_months"]),
                "credit_score": int(row["credit_score"]),
                "existing_emi": float(row["existing_emi"]),
                "city_category": row["city_category"].strip().lower(),
            }
            applicants.append(applicant)
    return applicants


def validate_applicant_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate user entered or loaded applicant fields.
    
    Returns (is_valid, error_messages).
    """
    errors = []

    # Age check
    age = data.get("age")
    if age is None or not isinstance(age, (int, float)) or age < 18 or age > 100:
        errors.append("Age must be a valid number between 18 and 100.")

    # Monthly income check
    income = data.get("monthly_income")
    if income is None or not isinstance(income, (int, float)) or income <= 0:
        errors.append("Monthly income must be a positive number greater than 0.")

    # Employment type check
    emp_type = str(data.get("employment_type", "")).strip().lower()
    if emp_type not in ["salaried", "self-employed"]:
        errors.append("Employment type must be either 'salaried' or 'self-employed'.")

    # Work experience check
    exp = data.get("work_experience_months")
    if exp is None or not isinstance(exp, (int, float)) or exp < 0:
        errors.append("Work experience in months must be a non-negative number.")

    # Credit score check
    credit_score = data.get("credit_score")
    if credit_score is None or not isinstance(credit_score, (int, float)) or credit_score < 300 or credit_score > 900:
        errors.append("Credit score must be between 300 and 900 (standard CIBIL range).")

    # Existing EMI check
    existing_emi = data.get("existing_emi")
    if existing_emi is None or not isinstance(existing_emi, (int, float)) or existing_emi < 0:
        errors.append("Existing monthly EMI must be a non-negative number.")

    # City category check
    city = str(data.get("city_category", "")).strip().lower()
    if city not in ["metro", "non-metro"]:
        errors.append("City category must be either 'metro' or 'non-metro'.")

    return (len(errors) == 0, errors)


def calculate_indicative_loan_amount(monthly_income: float, existing_emi: float, max_foir_pct: float, max_lender_amount: int) -> int:
    """Calculate an indicative loan amount using a standard 10x net monthly income multiplier,
    bounded by the remaining debt capacity (FOIR) and lender ceiling.
    
    Assumption: Standard conservative rule-of-thumb multiplier of 10x monthly income,
    adjusted downward if existing EMI consumes significant borrowing capacity.
    """
    max_allowed_emi = monthly_income * (max_foir_pct / 100.0)
    available_emi = max_allowed_emi - existing_emi
    
    if available_emi <= 0:
        return 0

    # Capacity factor: fraction of allowable EMI still free
    capacity_ratio = available_emi / max_allowed_emi
    
    # Base loan estimate: 10 times monthly income * capacity ratio
    base_estimate = monthly_income * 10 * capacity_ratio
    
    # Bound between INR 50,000 minimum and lender maximum limit
    bounded_amount = min(max_lender_amount, base_estimate)
    
    # Round to nearest 10,000
    indicative_amount = int(round(bounded_amount / 10000.0) * 10000)
    return max(50000, indicative_amount)


def evaluate_applicant(applicant: Dict[str, Any], lenders: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Evaluate an applicant against all lenders using rule-based criteria.
    
    Returns structured results:
    - applicant: original data
    - eligible_lenders: list of passed lenders with indicative loan terms
    - ineligible_lenders: list of failed lenders with specific failure reasons
    - recommended_lender: best option based on lowest indicative interest rate
    - recommendation_reason: brief explanation
    - disclaimer: legal/informative disclaimer
    """
    is_valid, val_errors = validate_applicant_data(applicant)
    if not is_valid:
        return {
            "applicant": applicant,
            "is_valid": False,
            "validation_errors": val_errors,
            "eligible_lenders": [],
            "ineligible_lenders": [],
            "recommended_lender": None,
            "recommendation_reason": "Applicant data validation failed.",
            "disclaimer": DISCLAIMER,
        }

    age = int(applicant["age"])
    monthly_income = float(applicant["monthly_income"])
    emp_type = applicant["employment_type"].strip().lower()
    work_exp = int(applicant["work_experience_months"])
    credit_score = int(applicant["credit_score"])
    existing_emi = float(applicant["existing_emi"])
    city = applicant["city_category"].strip().lower()

    # Calculate Fixed Obligation to Income Ratio (FOIR)
    foir_pct = (existing_emi / monthly_income) * 100.0

    eligible_lenders = []
    ineligible_lenders = []

    for lender in lenders:
        reasons = []

        # 1. Age Rule (Published criteria)
        if age < lender["min_age"] or age > lender["max_age"]:
            reasons.append(
                f"Age {age} is outside the eligible range of {lender['min_age']} to {lender['max_age']} years."
            )

        # 2. Employment Type Rule (Published criteria)
        if emp_type not in lender["allowed_employment"]:
            allowed_str = ", ".join(lender["allowed_employment"])
            reasons.append(
                f"Employment type '{emp_type}' is not accepted (requires: {allowed_str})."
            )

        # 3. Minimum Monthly Income Rule (Published criteria + City Category)
        required_income = lender["min_income_non_metro_inr"] if city == "non-metro" else lender["min_income_inr"]
        if monthly_income < required_income:
            reasons.append(
                f"Monthly income of INR {monthly_income:,.0f} is below the minimum required INR {required_income:,.0f} for {city} areas."
            )

        # 4. Work Experience Rule (Published criteria)
        if work_exp < lender["min_experience_months"]:
            reasons.append(
                f"Work experience of {work_exp} months is below required {lender['min_experience_months']} months."
            )

        # 5. Credit Score Rule (Published criteria / Floor assumption)
        if credit_score < lender["min_credit_score"]:
            reasons.append(
                f"Credit score of {credit_score} is below minimum requirement of {lender['min_credit_score']}."
            )

        # 6. Existing EMI / FOIR Rule (Documented model assumption: 50% max)
        if foir_pct > lender["max_foir_pct"]:
            reasons.append(
                f"Existing EMI consumes {foir_pct:.1f}% of income, exceeding maximum FOIR threshold of {lender['max_foir_pct']:.0f}%."
            )

        if not reasons:
            # Passed all checks
            loan_amount = calculate_indicative_loan_amount(
                monthly_income=monthly_income,
                existing_emi=existing_emi,
                max_foir_pct=lender["max_foir_pct"],
                max_lender_amount=lender["max_loan_amount_inr"],
            )
            eligible_lenders.append({
                "lender_id": lender["lender_id"],
                "lender_name": lender["lender_name"],
                "lender_type": lender["lender_type"],
                "min_rate": lender["min_interest_rate_pct"],
                "max_rate": lender["max_interest_rate_pct"],
                "indicative_loan_amount": loan_amount,
                "indicative_tenure_months": lender["max_tenure_months"],
                "source_url": lender["source_url"],
                "date_checked": lender["date_checked"],
                "notes": lender["notes"],
            })
        else:
            ineligible_lenders.append({
                "lender_id": lender["lender_id"],
                "lender_name": lender["lender_name"],
                "lender_type": lender["lender_type"],
                "reasons": reasons,
                "source_url": lender["source_url"],
            })

    # Recommendation: Best option with lowest starting indicative interest rate
    recommended_lender = None
    rec_reason = ""
    if eligible_lenders:
        # Sort by minimum interest rate, then max tenure descending
        sorted_eligible = sorted(
            eligible_lenders,
            key=lambda x: (x["min_rate"], -x["indicative_tenure_months"])
        )
        recommended_lender = sorted_eligible[0]
        rec_reason = (
            f"Offers the lowest indicative starting interest rate of {recommended_lender['min_rate']:.2f}% p.a. "
            f"among all {len(eligible_lenders)} eligible lender(s)."
        )
    else:
        rec_reason = "No lenders found matching the applicant's current profile."

    return {
        "applicant": applicant,
        "is_valid": True,
        "foir_pct": foir_pct,
        "eligible_lenders": eligible_lenders,
        "ineligible_lenders": ineligible_lenders,
        "recommended_lender": recommended_lender,
        "recommendation_reason": rec_reason,
        "disclaimer": DISCLAIMER,
    }
