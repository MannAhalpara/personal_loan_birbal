# Basic Personal Loan Eligibility Model (India)

A simple, rule-based Python command-line project that evaluates personal loan eligibility for applicants in India across major banks and NBFCs based on published lender criteria and documented assumptions.

---

## 1. Overview

This project is a beginner-to-intermediate student implementation of a **Personal Loan Eligibility Model** for the Indian lending market. When a borrower asks, *"Can I get a personal loan, and from whom?"*, banks rarely publish their entire internal underwriting algorithms. However, key eligibility criteria—such as minimum age, income thresholds, credit score cutoffs, and debt-to-income limits—are available through public product pages, rate calculators, and regulatory frameworks.

This program takes an applicant's financial and employment parameters, evaluates them against rule-based criteria, displays passing and failing checks with specific reasons, estimates indicative loan capacity and interest rates, and highlights the best recommended lender.

> **Disclaimer:** This tool provides **indicative eligibility estimates only**. It does not constitute a loan sanction, financial guarantee, or prediction of actual bank credit approval.

---

## 2. Features

- **Command-Line Interface (CLI):** Clean, text-based numbered menu with no unnecessary animations, external web servers, or complex UI frameworks.
- **Interactive Evaluation:** Evaluate new applicants interactively with built-in input validation.
- **Synthetic Profile Testing:** Test and inspect any of the 150 synthetic applicants by Applicant ID.
- **Supported Lenders Directory:** View criteria, indicative interest rates, maximum tenures, public source links, and dates verified.
- **Transparent Decisions:** Every rejection includes clear, plain-language reasons (e.g., credit score below cutoff, existing EMI exceeding debt limits).
- **Indicative Loan Estimates:** Conservatively estimates loan amount, rate range, and tenure without misrepresenting them as approved sanctions.
- **Best Option Pick:** Ranks eligible lenders by lowest starting interest rate and explains the recommendation.
- **Zero External Dependencies:** Built 100% on the Python Standard Library.

---

## 3. Project Structure

The repository follows a clean, flat structure with the root directory serving as the single source of truth:

```text
Birbal/
├── .gitignore                          # Excludes Python bytecode, caches, venvs, and editor files
├── applicants.csv                      # 150 synthetic applicant profiles for testing
├── eligibility.py                     # Core rule-based eligibility evaluation engine
├── generate_dataset.py                 # Reproducible generator for applicants.csv
├── lenders.csv                         # 8 lenders criteria, rate ranges, source URLs, and dates
├── main.py                             # CLI application entry point with interactive menus
├── Personal loan eligibility model.pdf # Original assignment specification document
├── README.md                           # Project documentation, data dictionary, and insights
├── requirements.txt                    # Project dependencies (Python Standard Library only)
└── test_eligibility.py                 # Standard unit test suite (12 test cases)
```

---

## 4. Requirements and Installation

### Prerequisites
- **Python 3.8** or higher (tested with Python 3.13 on Windows).
- **No external packages required.** All functionality uses Python's built-in standard library (`csv`, `os`, `sys`, `unittest`, `typing`, `random`).

### Installation
Clone or download the repository to your local machine:

```bash
git clone <repository-url>
cd Birbal
```

Verify your Python installation:
```bash
python --version
```

---

## 5. Commands to Run the Application and Tests

### Launch the CLI
Run the main program from the repository root:

```bash
python main.py
```

The numbered menu will appear:
```text
====================================================================
   PERSONAL LOAN ELIGIBILITY MODEL (INDIA)
====================================================================
  1. Check personal loan eligibility for a new applicant
  2. Test an existing sample applicant
  3. Display a list of supported lenders
  4. Exit
====================================================================
```

### Run the Automated Test Suite
Execute the 12 unit test cases using Python's built-in `unittest` runner:

```bash
python test_eligibility.py
```

### Re-generate Synthetic Dataset (Optional)
If you wish to re-generate `applicants.csv` deterministically:

```bash
python generate_dataset.py
```

---

## 6. Input Parameters and Data Origins

As required by the assignment specification, the model evaluates applicants using seven standardized parameters. The table below details each variable's name, unit, type, description, and source origin:

| Variable Name | Unit | Data Type | Description | Source / Origin |
| :--- | :--- | :--- | :--- | :--- |
| `age` | Years | Integer | Age of the borrower (18–100) | Document (Aadhaar / PAN Card / Passport) |
| `monthly_income` | INR | Float | Net take-home monthly salary or net business profit | Document (Salary slip / Form 16 / Bank statement) |
| `employment_type` | Categorical | String (`salaried`, `self-employed`) | Nature of applicant's primary occupation | Applicant Statement / Employer ID |
| `work_experience_months`| Months | Integer | Total career experience or business continuity tenure | Document (Experience letter / Service certificate) |
| `credit_score` | Score (300–900) | Integer | Approximate credit score from a licensed bureau | Credit Bureau (CIBIL / Experian / CRIF) |
| `existing_emi` | INR | Float | Sum of all current monthly loan/card repayments | Credit Bureau / Bank Account Statement |
| `city_category` | Categorical | String (`metro`, `non-metro`) | Location tier of borrower residence | Document (Current address proof / KYC) |

---

## 7. How the Eligibility Logic Works

For each lender, the applicant profile undergoes six sequential rule evaluations:

1. **Age Verification:** Checks whether `min_age <= applicant.age <= max_age`.
2. **Employment Type Verification:** Checks whether the applicant's status (`salaried` or `self-employed`) is accepted by the lender.
3. **Minimum Net Income Verification:** Evaluates net monthly income against the lender's threshold. Non-metro applicants are checked against the lender's non-metro threshold where applicable.
4. **Work Experience Verification:** Checks whether career experience meets or exceeds the lender's required months (typically 12 or 24 months).
5. **Credit Score Verification:** Checks whether the credit score meets the minimum floor (typically 670 to 700).
6. **Debt Burden / FOIR Verification:** Calculates Fixed Obligation to Income Ratio:
   $$\text{FOIR} = \left(\frac{\text{Existing Monthly EMI}}{\text{Monthly Income}}\right) \times 100$$
   Checks whether $\text{FOIR} \le \text{max\_foir\_pct}$ (standard model threshold: 50%).

### Indicative Loan Amount Estimation
When an applicant passes all checks for a lender, the model calculates an indicative loan amount:
1. Available monthly EMI capacity:
   $$\text{Available EMI} = \left(\text{Monthly Income} \times \frac{\text{Max FOIR}}{100}\right) - \text{Existing EMI}$$
2. Capacity ratio:
   $$\text{Capacity Ratio} = \frac{\text{Available EMI}}{\text{Max Allowed EMI}}$$
3. Estimated loan amount:
   $$\text{Estimated Amount} = \min(\text{Lender Max Ceiling}, \text{Monthly Income} \times 10 \times \text{Capacity Ratio})$$
   Rounded to the nearest INR 10,000, with a floor of INR 50,000.

### Best Option Selection
- Eligible lenders are ranked primarily by their **lowest indicative starting interest rate** (`min_rate`).
- Ties are broken using maximum available tenure (`max_tenure_months`).
- A human-readable explanation describes why the lender was recommended.

---

## 8. Supported Lenders & Source Information

The model currently implements **8 major Indian lenders** (5 banks and 3 NBFCs):

| Lender Name | Type | Min Age | Min Income (Metro / Non-Metro) | Allowed Employment | Min Exp | Min CIBIL | Indicative Rate (p.a.) | Max Tenure | Public Source URL | Date Checked |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **HDFC Bank** | Bank | 21–60 | INR 25,000 / INR 20,000 | Salaried | 12 mo | 700 | 10.50% – 24.00% | 60 mo | [HDFC Bank](https://www.hdfcbank.com/personal/borrow/popular-loans/personal-loan/eligibility-calculator) | 2026-10-11 |
| **State Bank of India** | Bank | 21–60 | INR 20,000 / INR 20,000 | Salaried | 12 mo | 670 | 11.15% – 14.30% | 72 mo | [SBI Xpress Credit](https://sbi.bank.in/web/personal-banking/loans/personal-loans/xpress-credit) | 2026-10-11 |
| **ICICI Bank** | Bank | 21–58 | INR 30,000 / INR 25,000 | Salaried, Self-employed | 24 mo | 700 | 10.80% – 16.50% | 60 mo | [ICICI Bank](https://www.icicibank.com/personal-banking/loans/personal-loan/eligibility) | 2026-10-11 |
| **Axis Bank** | Bank | 21–60 | INR 25,000 / INR 20,000 | Salaried | 12 mo | 700 | 10.99% – 22.00% | 60 mo | [Axis Bank](https://www.axisbank.com/retail/loans/personal-loan/eligibility-criteria) | 2026-10-11 |
| **Kotak Mahindra Bank** | Bank | 21–60 | INR 25,000 / INR 25,000 | Salaried | 12 mo | 700 | 10.99% – 24.00% | 60 mo | [Kotak Bank](https://www.kotak.bank.in/en/personal-banking/loans/personal-loan/eligibility.html) | 2026-10-11 |
| **Bajaj Finserv** | NBFC | 21–68 | INR 25,001 / INR 22,000 | Salaried | 12 mo | 685 | 11.00% – 26.00% | 84 mo | [Bajaj Finserv](https://www.bajajfinserv.in/personal-loan-eligibility-criteria) | 2026-10-11 |
| **Tata Capital** | NBFC | 21–58 | INR 15,000 / INR 15,000 | Salaried, Self-employed | 12 mo | 700 | 10.99% – 26.00% | 72 mo | [Tata Capital](https://www.tatacapital.com/personal-loan/eligibility.html) | 2026-10-11 |
| **Aditya Birla Capital** | NBFC | 21–60 | INR 25,000 / INR 20,000 | Salaried, Self-employed | 24 mo | 700 | 11.25% – 28.00% | 60 mo | [Aditya Birla Capital](https://www.adityabirlacapital.com/personal-loan/eligibility-criteria) | 2026-10-11 |

> **Assignment Scope Note (8 vs. 20 Lenders):**
> The original project brief mentions covering the top 20 personal loan lenders in India. This implementation deliberately covers **8 prominent lenders** (5 public/private banks and 3 large NBFCs) to maintain a straightforward, student-level codebase that runs without complex database engines. Section 12 details this gap and how it can be expanded.

---

## 9. Published Rules versus Documented Assumptions

To maintain academic honesty, the table below distinguishes between published bank policies and model assumptions:

| Rule Dimension | Published Lender Policy | Model Assumption |
| :--- | :--- | :--- |
| **Age Limits** | Published on lender product pages (typically 21 to 58/60/68). | None. |
| **Minimum Income** | Published base salary requirements (ranging from INR 15,000 to INR 30,000). | Modest INR 5,000 regional buffer applied for non-metro cities where tiered income applies. |
| **Employment Type** | Explicitly stated (e.g., SBI Xpress Credit is salaried only; Tata Capital accepts self-employed). | None. |
| **Work Experience** | Stated on product FAQ pages (typically 12 or 24 months total). | None. |
| **Credit Score** | Stated by some lenders (SBI: 670, Bajaj: 685). Other lenders advise "700+" or "750+". | Fixed cutoff floor of 700 assumed where lenders recommend 700+ without publishing a rigid minimum. |
| **FOIR (Debt-to-Income)** | Banks state FOIR is evaluated, but use internal sliding scales (40%–65%). | Standard industry cap of **50%** assumed across all lenders. |
| **Loan Amount** | Maximum absolute ceilings published (INR 30L – 50L). | 10× monthly income formula assumed as an indicative estimate, not a sanction. |

---

## 10. Description of the Synthetic Dataset

The file `applicants.csv` contains **150 synthetic applicant profiles** created by `generate_dataset.py`.

- **Privacy Statement:** No real customer data, personal names, phone numbers, or actual banking records are contained in this dataset. All records are 100% synthetically generated.
- **Coverage of Scenarios:**
  - **Prime Borrowers (APP001–APP020):** Strong income (INR 40k–150k), credit score 750–825, low EMI.
  - **Low Income (APP021–APP040):** Incomes below INR 20,000, testing minimum salary cutoffs.
  - **High Existing EMI (APP041–APP060):** FOIR obligations exceeding 55%–80%, testing debt caps.
  - **Low Credit Score (APP061–APP080):** Scores between 510 and 650, testing credit score rejection.
  - **Borderline Credit Score (APP081–APP095):** Scores between 670 and 695, qualifying for SBI or Bajaj but failing others.
  - **Self-Employed Borrowers (APP096–APP110):** Testing employment filter behavior.
  - **Low Work Experience (APP111–APP120):** Experience between 2 and 11 months, testing stability cutoffs.
  - **Age Limits (APP121–APP130):** Underage (18–20) and senior applicants (59–65).
  - **Mixed Profiles (APP131–APP150):** Realistic middle-income salaried and self-employed applicants.

---

## 11. Results and Empirical Insights

Running the 150 synthetic applicants across all 8 lenders generates **1,200 individual eligibility evaluations**. The empirical results reveal several key insights:

### Overall Eligibility Distribution
- **74 applicants (49.3%)** qualify for at least one lender.
- **76 applicants (50.7%)** are ineligible across all 8 lenders.

### Lender Qualification Comparison
Lenders differ significantly in eligibility rates due to variations in their published criteria:

| Lender | Type | Eligible Applicants | Eligibility Rate | Primary Driver |
| :--- | :--- | :-: | :-: | :--- |
| **Tata Capital** | NBFC | 51 / 150 | 34.0% | Lowest income floor (INR 15,000) and accepts self-employed borrowers. |
| **State Bank of India** | Bank | 50 / 150 | 33.3% | Lower credit cutoff (670) and accessible INR 20,000 income floor. |
| **Aditya Birla Capital** | NBFC | 46 / 150 | 30.7% | Accepts self-employed borrowers with stable financials. |
| **Bajaj Finserv** | NBFC | 42 / 150 | 28.0% | Accessible 685 credit cutoff and higher maximum age (68 years). |
| **ICICI Bank** | Bank | 39 / 150 | 26.0% | Accepts self-employed, but requires 24 months experience and INR 30k metro salary. |
| **HDFC Bank** | Bank | 29 / 150 | 19.3% | Stricter salaried-only restriction and INR 25k income threshold. |
| **Axis Bank** | Bank | 29 / 150 | 19.3% | Salaried-only, 700 score cutoff, INR 25k income floor. |
| **Kotak Mahindra Bank** | Bank | 25 / 150 | 16.7% | Most selective in this dataset due to salaried-only and uniform INR 25k floor. |

### Most Common Failure Rules
Across all 1,200 lender evaluations, the causes of rejection rank as follows:

```text
1. Credit Score Cutoff      : 397 rejections (33.1%) - Single biggest barrier to approval
2. Employment Type Filter   : 200 rejections (16.7%) - 5 of 8 lenders exclude self-employed
3. Minimum Monthly Income   : 176 rejections (14.7%) - Incomes below INR 15k-30k thresholds
4. Debt Burden / FOIR Cap   : 160 rejections (13.3%) - Existing EMI exceeding 50% of income
5. Work Experience Tenure   : 120 rejections (10.0%) - Less than 12 or 24 months in career
6. Age Range Limits         :  75 rejections ( 6.2%) - Under 21 or over 58-60 years
```

**Key Finding:** Credit score and employment type restrictions account for nearly **50% of all rejections**. Self-employed applicants face immediate exclusion from major bank personal loan schemes unless applying to lenders with specialized self-employed criteria (e.g., Tata Capital, ICICI Bank, Aditya Birla Capital).

---

## 12. Limitations and Future Improvements

### Known Limitations
1. **Scope Gap (8 vs. 20 Lenders):** The original assignment specifies 20 lenders. The current implementation deliberately focuses on 8 lenders to keep the logic clear, readable, and auditable for a beginner-to-intermediate codebase.
2. **Simplified FOIR Modeling:** Uses a static 50% cap. In reality, banks use progressive FOIR scales (e.g., 40% for low earners, up to 65% for incomes exceeding INR 100,000).
3. **Employer Categorization Omitted:** Leading private banks classify corporate employers into Category A, B, and C tiers, which influences interest rates and salary cutoffs.
4. **Indicative Loan Calculation:** The 10× income multiplier is a conservative heuristic, not a reflection of bank risk-adjusted credit limit assignment.

### Future Improvements
1. **Expand to 20 Lenders:** Add 12 additional lenders (e.g., Bank of Baroda, Punjab National Bank, IndusInd Bank, IDFC FIRST Bank, Federal Bank, Muthoot Finance, Piramal Finance, Fullerton/SMFG India, InCred, Poonawalla Fincorp, MoneyTap, and Navi).
2. **Dynamic FOIR Tiers:** Implement tiered FOIR percentages that increase with net disposable income.
3. **Interactive Batch Evaluation:** Add an option in the CLI to evaluate the entire `applicants.csv` file at once and output a summary statistics report.
