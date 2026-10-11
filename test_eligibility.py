"""test_eligibility.py - Unit test suite for Personal Loan Eligibility Model.

Uses Python's standard unittest framework to verify ordinary cases and key edge cases:
1. Underage applicant (below minimum age)
2. Elderly applicant (exceeding maximum age for banks)
3. Low monthly income (below lender minimum)
4. Borderline income (qualifying for select lenders)
5. Low credit score (below minimum threshold)
6. Borderline credit score (qualifying for lower cutoff lenders)
7. High existing EMI (exceeding maximum allowed FOIR)
8. Limited work experience (below minimum requirement)
9. Self-employed applicant (qualifying only for lenders allowing self-employed)
10. Prime salaried applicant (qualifying for all 8 lenders)
11. Non-metro city category income threshold behavior
12. Dataset loading and schema integrity for 150 applicants and 8 lenders
"""

import unittest
import eligibility


class TestPersonalLoanEligibility(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lenders = eligibility.load_lenders()
        cls.applicants = eligibility.load_applicants()

    def test_dataset_integrity(self):
        """Verify that exactly 8 lenders and 150 synthetic applicants exist with valid data."""
        self.assertEqual(len(self.lenders), 8, "Expected exactly 8 lenders in lenders.csv")
        self.assertEqual(len(self.applicants), 150, "Expected exactly 150 profiles in applicants.csv")
        
        # Verify all 150 profiles pass data validation
        for app in self.applicants:
            is_valid, errors = eligibility.validate_applicant_data(app)
            self.assertTrue(is_valid, f"Applicant {app.get('applicant_id')} failed validation: {errors}")

    def test_case_1_underage_applicant(self):
        """Applicant below min age (19 years old) must fail age checks on all lenders."""
        applicant = {
            "applicant_id": "TEST_AGE_LOW",
            "age": 19,
            "monthly_income": 45000,
            "employment_type": "salaried",
            "work_experience_months": 24,
            "credit_score": 750,
            "existing_emi": 0,
            "city_category": "metro"
        }
        res = eligibility.evaluate_applicant(applicant, self.lenders)
        self.assertEqual(len(res["eligible_lenders"]), 0)
        self.assertEqual(len(res["ineligible_lenders"]), 8)
        for inel in res["ineligible_lenders"]:
            reasons_text = " ".join(inel["reasons"])
            self.assertIn("Age 19 is outside the eligible range", reasons_text)

    def test_case_2_overage_applicant(self):
        """Applicant aged 64 should fail banks (max 58-60) but pass Bajaj Finserv (max 68)."""
        applicant = {
            "applicant_id": "TEST_AGE_HIGH",
            "age": 64,
            "monthly_income": 60000,
            "employment_type": "salaried",
            "work_experience_months": 120,
            "credit_score": 760,
            "existing_emi": 5000,
            "city_category": "metro"
        }
        res = eligibility.evaluate_applicant(applicant, self.lenders)
        eligible_names = [l["lender_name"] for l in res["eligible_lenders"]]
        self.assertIn("Bajaj Finserv", eligible_names)
        self.assertNotIn("HDFC Bank", eligible_names)
        self.assertNotIn("State Bank of India", eligible_names)

    def test_case_3_low_income_applicant(self):
        """Income INR 14,000 is below the lowest lender threshold (Tata Capital INR 15,000)."""
        applicant = {
            "applicant_id": "TEST_LOW_INC",
            "age": 28,
            "monthly_income": 14000,
            "employment_type": "salaried",
            "work_experience_months": 36,
            "credit_score": 740,
            "existing_emi": 1000,
            "city_category": "metro"
        }
        res = eligibility.evaluate_applicant(applicant, self.lenders)
        self.assertEqual(len(res["eligible_lenders"]), 0)
        for inel in res["ineligible_lenders"]:
            reasons_text = " ".join(inel["reasons"])
            self.assertIn("below the minimum required", reasons_text)

    def test_case_4_borderline_income_applicant(self):
        """Income INR 22,000 in metro meets SBI (INR 20,000) and Tata (INR 15,000), but fails HDFC (25k) & ICICI (30k)."""
        applicant = {
            "applicant_id": "TEST_BORDER_INC",
            "age": 29,
            "monthly_income": 22000,
            "employment_type": "salaried",
            "work_experience_months": 24,
            "credit_score": 730,
            "existing_emi": 2000,
            "city_category": "metro"
        }
        res = eligibility.evaluate_applicant(applicant, self.lenders)
        eligible_names = [l["lender_name"] for l in res["eligible_lenders"]]
        self.assertIn("State Bank of India", eligible_names)
        self.assertIn("Tata Capital", eligible_names)
        self.assertNotIn("HDFC Bank", eligible_names)
        self.assertNotIn("ICICI Bank", eligible_names)

    def test_case_5_low_credit_score_applicant(self):
        """Credit score 580 fails credit check across all lenders (lowest cutoff is SBI 670)."""
        applicant = {
            "applicant_id": "TEST_LOW_CIBIL",
            "age": 32,
            "monthly_income": 60000,
            "employment_type": "salaried",
            "work_experience_months": 48,
            "credit_score": 580,
            "existing_emi": 3000,
            "city_category": "metro"
        }
        res = eligibility.evaluate_applicant(applicant, self.lenders)
        self.assertEqual(len(res["eligible_lenders"]), 0)
        for inel in res["ineligible_lenders"]:
            reasons_text = " ".join(inel["reasons"])
            self.assertIn("Credit score of 580 is below minimum", reasons_text)

    def test_case_6_borderline_credit_score(self):
        """Credit score 675 qualifies for SBI (670 cutoff), but fails lenders requiring 685 or 700."""
        applicant = {
            "applicant_id": "TEST_BORDER_CIBIL",
            "age": 30,
            "monthly_income": 45000,
            "employment_type": "salaried",
            "work_experience_months": 24,
            "credit_score": 675,
            "existing_emi": 3000,
            "city_category": "metro"
        }
        res = eligibility.evaluate_applicant(applicant, self.lenders)
        eligible_names = [l["lender_name"] for l in res["eligible_lenders"]]
        self.assertEqual(eligible_names, ["State Bank of India"])

    def test_case_7_high_existing_emi_applicant(self):
        """EMI of INR 35,000 on INR 50,000 income produces FOIR = 70% (> 50% limit) and fails all lenders."""
        applicant = {
            "applicant_id": "TEST_HIGH_EMI",
            "age": 35,
            "monthly_income": 50000,
            "employment_type": "salaried",
            "work_experience_months": 48,
            "credit_score": 780,
            "existing_emi": 35000,
            "city_category": "metro"
        }
        res = eligibility.evaluate_applicant(applicant, self.lenders)
        self.assertEqual(len(res["eligible_lenders"]), 0)
        for inel in res["ineligible_lenders"]:
            reasons_text = " ".join(inel["reasons"])
            self.assertIn("exceeding maximum FOIR threshold", reasons_text)

    def test_case_8_limited_work_experience(self):
        """Work experience of 6 months fails all lenders (all require at least 12 or 24 months)."""
        applicant = {
            "applicant_id": "TEST_LOW_EXP",
            "age": 24,
            "monthly_income": 50000,
            "employment_type": "salaried",
            "work_experience_months": 6,
            "credit_score": 750,
            "existing_emi": 2000,
            "city_category": "metro"
        }
        res = eligibility.evaluate_applicant(applicant, self.lenders)
        self.assertEqual(len(res["eligible_lenders"]), 0)
        for inel in res["ineligible_lenders"]:
            reasons_text = " ".join(inel["reasons"])
            self.assertIn("is below required", reasons_text)

    def test_case_9_self_employed_applicant(self):
        """Self-employed applicant should qualify for ICICI, Tata Capital, and Aditya Birla Capital only."""
        applicant = {
            "applicant_id": "TEST_SELF_EMP",
            "age": 36,
            "monthly_income": 85000,
            "employment_type": "self-employed",
            "work_experience_months": 36,
            "credit_score": 765,
            "existing_emi": 8000,
            "city_category": "metro"
        }
        res = eligibility.evaluate_applicant(applicant, self.lenders)
        eligible_names = set(l["lender_name"] for l in res["eligible_lenders"])
        expected_names = {"ICICI Bank", "Tata Capital", "Aditya Birla Capital"}
        self.assertEqual(eligible_names, expected_names)

    def test_case_10_prime_salaried_applicant(self):
        """Prime salaried applicant qualifies for all 8 lenders with HDFC recommended (lowest starting rate)."""
        applicant = {
            "applicant_id": "TEST_PRIME",
            "age": 32,
            "monthly_income": 80000,
            "employment_type": "salaried",
            "work_experience_months": 48,
            "credit_score": 790,
            "existing_emi": 5000,
            "city_category": "metro"
        }
        res = eligibility.evaluate_applicant(applicant, self.lenders)
        self.assertEqual(len(res["eligible_lenders"]), 8)
        self.assertEqual(len(res["ineligible_lenders"]), 0)
        self.assertIsNotNone(res["recommended_lender"])
        self.assertEqual(res["recommended_lender"]["lender_name"], "HDFC Bank")
        self.assertEqual(res["recommended_lender"]["min_rate"], 10.50)

    def test_case_11_non_metro_relief(self):
        """Income INR 22,000 in non-metro qualifies for HDFC (non-metro threshold 20k), but not in metro (25k)."""
        applicant_metro = {
            "applicant_id": "TEST_METRO",
            "age": 30,
            "monthly_income": 22000,
            "employment_type": "salaried",
            "work_experience_months": 24,
            "credit_score": 740,
            "existing_emi": 1000,
            "city_category": "metro"
        }
        applicant_non_metro = {
            "applicant_id": "TEST_NON_METRO",
            "age": 30,
            "monthly_income": 22000,
            "employment_type": "salaried",
            "work_experience_months": 24,
            "credit_score": 740,
            "existing_emi": 1000,
            "city_category": "non-metro"
        }
        res_metro = eligibility.evaluate_applicant(applicant_metro, self.lenders)
        res_non_metro = eligibility.evaluate_applicant(applicant_non_metro, self.lenders)
        
        hdfc_metro = any(l["lender_name"] == "HDFC Bank" for l in res_metro["eligible_lenders"])
        hdfc_non_metro = any(l["lender_name"] == "HDFC Bank" for l in res_non_metro["eligible_lenders"])
        
        self.assertFalse(hdfc_metro, "HDFC should fail for INR 22k in metro (requires INR 25k)")
        self.assertTrue(hdfc_non_metro, "HDFC should pass for INR 22k in non-metro (requires INR 20k)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
