# Personal Loan Eligibility Model (India)

A simple Python command-line project to check personal loan eligibility for applicants in India against 8 major banks and NBFCs.

---

## 1. Overview

This is a basic rule-based eligibility checker. Banks and NBFCs in India don't publish their full internal scoring formulas, but they do share basic criteria like minimum age, salary requirements, work experience, and credit scores.

This program takes an applicant's basic details, checks them against rules from 8 lenders, shows which lenders they qualify for, explains why any checks failed, and suggests the best option based on the lowest interest rate.

**Note:** This is only a simple indicative project for academic purposes, not an actual bank loan approval or guarantee.

---

## 2. Features

- Simple numbered terminal menu (CLI).
- Option to enter a new applicant's details manually.
- Option to test any of the 150 sample applicants by ID (e.g., APP001).
- View list of supported lenders and their rules.
- Clear reasons shown when a lender rejects an applicant.
- Simple estimate for loan amount, rate range, and tenure.
- Best lender recommendation based on lowest starting interest rate.
- Uses only Python's built-in standard library.

---

## 3. Project Structure

```text
Birbal/
├── applicants.csv          # 150 synthetic applicant profiles
├── eligibility.py          # Core eligibility checking functions
├── generate_dataset.py     # Script used to create applicants.csv
├── lenders.csv             # Rules and sources for 8 lenders
├── main.py                 # CLI menu program
├── test_eligibility.py     # 12 test cases
├── requirements.txt        # Dependencies note (standard library only)
├── .gitignore              # Ignores pycache and temp files
└── README.md               # Project documentation
```

---

## 4. Requirements & Installation

- Python 3.8 or higher.
- No external libraries or pip packages are needed. Everything uses Python's built-in modules (`csv`, `os`, `sys`, `unittest`, `random`).

To get started:
```bash
git clone https://github.com/MannAhalpara/personal_loan_birbal.git
cd personal_loan_birbal
```

---

## 5. How to Run

### Run the CLI Application
```bash
python main.py
```

Menu options:
1. Check personal loan eligibility for a new applicant
2. Test an existing sample applicant
3. Display a list of supported lenders
4. Exit

### Run the Tests
```bash
python test_eligibility.py
```

### Re-create Dataset (Optional)
```bash
python generate_dataset.py
```

---

## 6. Input Parameters

The model uses 7 basic parameters:

| Variable | Unit | Type | Description | Source |
| :--- | :--- | :--- | :--- | :--- |
| `age` | Years | Integer | Age of applicant (18 to 100) | Document (Aadhaar / PAN card) |
| `monthly_income` | INR | Float | Net take-home salary or monthly income | Document (Salary slip / Bank statement) |
| `employment_type`| String | `salaried` or `self-employed` | Type of job | Applicant statement / Job ID |
| `work_experience_months` | Months | Integer | Total work experience | Document (Experience letter) |
| `credit_score` | Number | Integer | CIBIL / Credit score (300 to 900) | Credit Bureau (CIBIL / Experian) |
| `existing_emi` | INR | Float | Total current monthly loan EMIs | Credit Bureau / Bank statement |
| `city_category` | String | `metro` or `non-metro` | Location tier | Document (Address proof) |

---

## 7. How the Eligibility Logic Works

For each lender, the program checks these rules in order:
1. **Age:** Applicant must be between the lender's minimum age (usually 21) and maximum age (usually 58 to 68).
2. **Employment Type:** Checks if the lender accepts the applicant's job type. Many banks only lend to salaried individuals.
3. **Monthly Income:** Net monthly income must be greater than or equal to the lender's cutoff. Non-metro applicants get a slightly relaxed cutoff for lenders that support tiered salary rules.
4. **Work Experience:** Must meet the minimum months required (usually 12 or 24 months).
5. **Credit Score:** Must meet the lender's minimum score (e.g., 670 for SBI, 685 for Bajaj, 700 for others).
6. **Debt-to-Income (FOIR):**
   `FOIR = (Existing EMI / Monthly Income) * 100`
   If FOIR exceeds 50%, the applicant fails the debt capacity check.

### Indicative Loan Amount and Recommendation
- If eligible, the program estimates an indicative loan amount using a rule of thumb: `10 * Monthly Income * remaining capacity`, rounded to nearest INR 10,000 (minimum INR 50,000, capped at lender maximum limit).
- The best option is selected by picking the lender with the lowest starting interest rate.

---

## 8. Supported Lenders & Sources

Currently, 8 lenders are included (5 banks and 3 NBFCs):

| Lender | Type | Min Age | Min Income (Metro / Non-Metro) | Allowed Jobs | Min Exp | Min Score | Rate Range (p.a.) | Max Tenure | Source URL | Date Checked |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **HDFC Bank** | Bank | 21-60 | INR 25,000 / INR 20,000 | Salaried | 12 mo | 700 | 10.50% - 24.00% | 60 mo | https://www.hdfcbank.com/personal/borrow/popular-loans/personal-loan/eligibility-calculator | 2026-10-11 |
| **State Bank of India** | Bank | 21-60 | INR 20,000 / INR 20,000 | Salaried | 12 mo | 670 | 11.15% - 14.30% | 72 mo | https://sbi.bank.in/web/personal-banking/loans/personal-loans/xpress-credit | 2026-10-11 |
| **ICICI Bank** | Bank | 21-58 | INR 30,000 / INR 25,000 | Salaried, Self-employed | 24 mo | 700 | 10.80% - 16.50% | 60 mo | https://www.icicibank.com/personal-banking/loans/personal-loan/eligibility | 2026-10-11 |
| **Axis Bank** | Bank | 21-60 | INR 25,000 / INR 20,000 | Salaried | 12 mo | 700 | 10.99% - 22.00% | 60 mo | https://www.axisbank.com/retail/loans/personal-loan/eligibility-criteria | 2026-10-11 |
| **Kotak Mahindra Bank** | Bank | 21-60 | INR 25,000 / INR 25,000 | Salaried | 12 mo | 700 | 10.99% - 24.00% | 60 mo | https://www.kotak.bank.in/en/personal-banking/loans/personal-loan/eligibility.html | 2026-10-11 |
| **Bajaj Finserv** | NBFC | 21-68 | INR 25,001 / INR 22,000 | Salaried | 12 mo | 685 | 11.00% - 26.00% | 84 mo | https://www.bajajfinserv.in/personal-loan-eligibility-criteria | 2026-10-11 |
| **Tata Capital** | NBFC | 21-58 | INR 15,000 / INR 15,000 | Salaried, Self-employed | 12 mo | 700 | 10.99% - 26.00% | 72 mo | https://www.tatacapital.com/personal-loan/eligibility.html | 2026-10-11 |
| **Aditya Birla Capital** | NBFC | 21-60 | INR 25,000 / INR 20,000 | Salaried, Self-employed | 24 mo | 700 | 11.25% - 28.00% | 60 mo | https://www.adityabirlacapital.com/personal-loan/eligibility-criteria | 2026-10-11 |

*Note on Lender Scope:* The original project PDF asks for 20 lenders. For this initial project version, I implemented 8 lenders to keep the model straightforward and easy to debug. Adding the remaining 12 lenders is listed under future improvements.

---

## 9. Published Rules vs Assumptions

Here is what is directly based on public lender info versus what I had to assume:

- **Published Rules:**
  - Minimum and maximum age ranges.
  - Minimum monthly income floors.
  - Allowed employment types (salaried vs self-employed).
  - Minimum work experience requirements.
  - Published credit score floors (like SBI 670 and Bajaj 685).
  - Published interest rate ranges and tenures.

- **Assumed Rules:**
  - **FOIR threshold:** Fixed at 50% across all lenders (banks usually vary this between 40% and 65% depending on salary).
  - **Credit score 700 floor:** Assumed for lenders that state "good credit score preferred" without giving a rigid public cutoff.
  - **Loan amount estimate:** Calculated as 10x monthly income adjusted by existing EMI, rather than an internal bank underwriting formula.
  - **Non-metro discount:** Assumed a simple INR 5,000 lower income cutoff for non-metro locations where lenders have tiered city rules.

---

## 10. Synthetic Dataset

The file `applicants.csv` contains 150 synthetic applicant profiles.
- None of this is real customer data.
- It covers different situations: prime applicants, low-income earners (< 20k), high existing EMIs (FOIR > 50%), poor credit scores (< 650), borderline credit scores (670-695), self-employed people, young people (< 21), and applicants with short work experience.

---

## 11. Results and Simple Insights

Running all 150 sample applicants through the model gives these results:
- **74 applicants (49.3%)** qualify for at least one lender.
- **76 applicants (50.7%)** qualify for none.

**Lender comparison:**
- **Tata Capital:** Approved 51 applicants (34.0%) - highest because it accepts self-employed and has the lowest income floor (INR 15,000).
- **SBI:** Approved 50 applicants (33.3%) - high because of lower credit cutoff (670) and INR 20,000 salary floor.
- **Aditya Birla Capital:** Approved 46 applicants (30.7%) - accepts self-employed.
- **Bajaj Finserv:** Approved 42 applicants (28.0%) - accepts older applicants up to 68 and 685 score.
- **ICICI Bank:** Approved 39 applicants (26.0%).
- **HDFC Bank:** Approved 29 applicants (19.3%) - more selective (salaried only, 700 score, 25k salary).
- **Axis Bank:** Approved 29 applicants (19.3%).
- **Kotak Mahindra Bank:** Approved 25 applicants (16.7%).

**Most common reasons for rejection:**
1. **Credit score too low:** 397 rejections (most common failure)
2. **Employment type:** 200 rejections (self-employed applicants rejected by salaried-only banks)
3. **Monthly income too low:** 176 rejections
4. **Existing EMI too high (FOIR > 50%):** 160 rejections
5. **Work experience too short:** 120 rejections
6. **Age out of bounds:** 75 rejections

---

## 12. Limitations & Future Work

- **Lender count:** Only 8 lenders are supported so far, compared to the 20 requested in the assignment brief.
- **Simplified scoring:** Real banks look at employer category (Cat A, B, C companies), banking history, bounced checks, and detailed credit reports.
- **Static FOIR:** A flat 50% FOIR is used, whereas real banks allow higher FOIR for higher salaries.
- **Next steps:** Add the remaining 12 lenders (like PNB, Bank of Baroda, IDFC First, IndusInd, etc.) and add employer category support.
