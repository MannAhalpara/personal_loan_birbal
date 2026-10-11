"""main.py - Command-Line Interface (CLI) for Basic Personal Loan Eligibility Model.

Offers a plain and simple numbered menu:
1. Check personal loan eligibility for a new applicant.
2. Test an existing sample applicant.
3. Display a list of supported lenders.
4. Exit.
"""

import sys
import os
from typing import Dict, Any, Optional

# Ensure standard output safely handles text on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import eligibility


def print_header(title: str) -> None:
    print("\n" + "=" * 68)
    print(f"   {title}")
    print("=" * 68)


def print_subheader(title: str) -> None:
    print("\n" + "-" * 68)
    print(f" {title}")
    print("-" * 68)


def get_integer_input(prompt: str, min_val: int, max_val: int) -> int:
    while True:
        raw = input(f"{prompt} ({min_val} - {max_val}): ").strip()
        try:
            val = int(raw)
            if min_val <= val <= max_val:
                return val
            print(f"Error: Value must be between {min_val} and {max_val}.")
        except ValueError:
            print("Error: Please enter a valid whole number.")


def get_float_input(prompt: str, min_val: float, max_val: Optional[float] = None) -> float:
    while True:
        raw = input(f"{prompt}: ").strip().replace(",", "")
        try:
            val = float(raw)
            if val < min_val:
                print(f"Error: Value cannot be less than {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"Error: Value cannot exceed {max_val}.")
                continue
            return val
        except ValueError:
            print("Error: Please enter a valid numeric value.")


def get_choice_input(prompt: str, options: Dict[str, str]) -> str:
    print(f"{prompt}")
    for key, desc in options.items():
        print(f"  [{key}] {desc}")
    while True:
        raw = input("Enter choice: ").strip().lower()
        if raw in options:
            return options[raw].lower()
        # Also allow typing the option value directly
        for val in options.values():
            if raw == val.lower():
                return val.lower()
        print(f"Error: Please choose one of: {', '.join(options.keys())}")


def display_evaluation_results(result: Dict[str, Any]) -> None:
    app = result["applicant"]
    print_header("EVALUATION RESULT (INDICATIVE)")

    print("\n[Applicant Profile]")
    print(f"  Applicant ID          : {app.get('applicant_id', 'New Applicant')}")
    print(f"  Age                   : {app['age']} years")
    print(f"  Monthly Income        : INR {app['monthly_income']:,.0f}")
    print(f"  Employment Type       : {app['employment_type'].title()}")
    print(f"  Work Experience       : {app['work_experience_months']} months")
    print(f"  Credit Score (CIBIL)  : {app['credit_score']}")
    print(f"  Existing Monthly EMI  : INR {app['existing_emi']:,.0f}")
    print(f"  City Category         : {app['city_category'].title()}")
    print(f"  Calculated FOIR       : {result['foir_pct']:.1f}% (Debt-to-Income)")

    eligible = result["eligible_lenders"]
    ineligible = result["ineligible_lenders"]

    print_subheader(f"ELIGIBLE LENDERS ({len(eligible)} / {len(eligible) + len(ineligible)})")
    if eligible:
        for idx, el in enumerate(eligible, 1):
            print(f"\n  {idx}. {el['lender_name']} [{el['lender_type']}] (ID: {el['lender_id']})")
            print(f"     - Indicative Loan Amount : Up to INR {el['indicative_loan_amount']:,.0f}*")
            print(f"     - Indicative Interest Rate: {el['min_rate']:.2f}% - {el['max_rate']:.2f}% p.a.")
            print(f"     - Indicative Max Tenure   : {el['indicative_tenure_months']} months")
            print(f"     - Source URL              : {el['source_url']}")
            print(f"     - Verified On             : {el['date_checked']}")
            print(f"     - Notes                   : {el['notes']}")
    else:
        print("  None of the evaluated lenders match the applicant's current profile.")

    print_subheader(f"INELIGIBLE LENDERS ({len(ineligible)} / {len(eligible) + len(ineligible)})")
    if ineligible:
        for idx, iel in enumerate(ineligible, 1):
            print(f"\n  {idx}. {iel['lender_name']} [{iel['lender_type']}]")
            for r in iel["reasons"]:
                print(f"     * Reason: {r}")
    else:
        print("  None. Applicant passed checks across all lenders.")

    print_subheader("RECOMMENDED OPTION")
    rec = result["recommended_lender"]
    if rec:
        print(f"  Best Pick: {rec['lender_name']} ({rec['lender_type']})")
        print(f"  Rationale: {result['recommendation_reason']}")
        print(f"  Indicative Rate : Starting at {rec['min_rate']:.2f}% p.a.")
        print(f"  Estimated Amount: Up to INR {rec['indicative_loan_amount']:,.0f}")
    else:
        print("  No recommendation possible.")
        print(f"  Rationale: {result['recommendation_reason']}")

    print("\n" + "=" * 68)
    print(f"  {result['disclaimer']}")
    print("=" * 68)


def handle_new_applicant(lenders: list) -> None:
    print_header("1. CHECK ELIGIBILITY FOR A NEW APPLICANT")
    print("Please enter the financial and employment details below:\n")

    age = get_integer_input("Enter Age in years", 18, 100)
    monthly_income = get_float_input("Enter Net Monthly Income in INR", 1000.0, 10000000.0)
    
    emp_options = {"1": "Salaried", "2": "Self-employed"}
    emp_type = get_choice_input("Select Employment Type:", emp_options)
    
    work_exp = get_integer_input("Enter Total Work Experience in months", 0, 600)
    credit_score = get_integer_input("Enter Approximate Credit Score (CIBIL)", 300, 900)
    existing_emi = get_float_input("Enter Existing Monthly EMI in INR (enter 0 if none)", 0.0, monthly_income * 2)

    city_options = {"1": "Metro", "2": "Non-metro"}
    city = get_choice_input("Select City Category:", city_options)

    applicant_data = {
        "applicant_id": "NEW_USER",
        "age": age,
        "monthly_income": monthly_income,
        "employment_type": emp_type,
        "work_experience_months": work_exp,
        "credit_score": credit_score,
        "existing_emi": existing_emi,
        "city_category": city,
    }

    result = eligibility.evaluate_applicant(applicant_data, lenders)
    display_evaluation_results(result)


def handle_test_sample_applicant(lenders: list, applicants: list) -> None:
    print_header("2. TEST AN EXISTING SAMPLE APPLICANT")
    print(f"Total available sample profiles: {len(applicants)} (APP001 to APP{len(applicants):03d})")
    print("Quick examples: APP001 (Prime Salaried), APP021 (Low Income), APP041 (High EMI),")
    print("                APP061 (Low Credit), APP096 (Self-Employed), APP121 (Underage)\n")

    app_map = {a["applicant_id"].upper(): a for a in applicants}

    while True:
        raw_id = input("Enter Applicant ID (or number 1-150, 'list' to view, 'b' to go back): ").strip()
        if not raw_id:
            continue
        if raw_id.lower() == "b":
            return
        if raw_id.lower() == "list":
            print("\nDisplaying first 15 sample profiles:")
            print(f"{'ID':<8} {'Age':<5} {'Income (INR)':<14} {'Type':<14} {'Exp(m)':<8} {'Score':<7} {'EMI (INR)':<12} {'City'}")
            print("-" * 80)
            for a in applicants[:15]:
                print(f"{a['applicant_id']:<8} {a['age']:<5} {a['monthly_income']:<14,.0f} {a['employment_type']:<14} {a['work_experience_months']:<8} {a['credit_score']:<7} {a['existing_emi']:<12,.0f} {a['city_category']}")
            print("... and 135 more profiles available in applicants.csv.")
            continue

        formatted_id = raw_id.upper()
        if raw_id.isdigit():
            num = int(raw_id)
            if 1 <= num <= len(applicants):
                formatted_id = f"APP{num:03d}"

        if formatted_id in app_map:
            chosen = app_map[formatted_id]
            result = eligibility.evaluate_applicant(chosen, lenders)
            display_evaluation_results(result)
            break
        else:
            print(f"Error: Applicant ID '{raw_id}' not found. Please enter a valid ID such as APP001.")


def handle_display_lenders(lenders: list) -> None:
    print_header("3. SUPPORTED LENDERS (8 BANKS & NBFCs IN INDIA)")
    print("These rules are retrieved from public bank criteria and documented assumptions.\n")

    for idx, l in enumerate(lenders, 1):
        print(f"[{idx}] {l['lender_name']} ({l['lender_type']}) - ID: {l['lender_id']}")
        print(f"    - Eligible Age       : {l['min_age']} - {l['max_age']} years")
        print(f"    - Min Monthly Income : INR {l['min_income_inr']:,.0f} (Metro) / INR {l['min_income_non_metro_inr']:,.0f} (Non-Metro)")
        print(f"    - Employment Types   : {', '.join(l['allowed_employment'])}")
        print(f"    - Min Work Experience: {l['min_experience_months']} months")
        print(f"    - Min Credit Score   : {l['min_credit_score']}")
        print(f"    - Max Allowed FOIR   : {l['max_foir_pct']:.0f}% (Assumed standard cap)")
        print(f"    - Indicative Rates   : {l['min_interest_rate_pct']:.2f}% - {l['max_interest_rate_pct']:.2f}% p.a.")
        print(f"    - Max Tenure         : {l['max_tenure_months']} months ({l['max_tenure_months'] // 12} years)")
        print(f"    - Max Loan Ceiling   : INR {l['max_loan_amount_inr']:,.0f}")
        print(f"    - Source URL         : {l['source_url']}")
        print(f"    - Verified Date      : {l['date_checked']}")
        print(f"    - Rule Details       : {l['notes']}")
        print("-" * 68)


def main() -> None:
    try:
        lenders = eligibility.load_lenders()
        applicants = eligibility.load_applicants()
    except Exception as e:
        print(f"Startup Error: Failed to load data files: {e}")
        sys.exit(1)

    while True:
        print_header("PERSONAL LOAN ELIGIBILITY MODEL (INDIA)")
        print("  1. Check personal loan eligibility for a new applicant")
        print("  2. Test an existing sample applicant")
        print("  3. Display a list of supported lenders")
        print("  4. Exit")
        print("=" * 68)

        choice = input("Please select an option (1-4): ").strip()

        if choice == "1":
            handle_new_applicant(lenders)
        elif choice == "2":
            handle_test_sample_applicant(lenders, applicants)
        elif choice == "3":
            handle_display_lenders(lenders)
        elif choice == "4":
            print("\nThank you for using the Personal Loan Eligibility Model. Goodbye!\n")
            break
        else:
            print("\nInvalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
