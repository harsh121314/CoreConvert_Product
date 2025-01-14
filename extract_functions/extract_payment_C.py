import pdfplumber
import re
from datetime import datetime, timedelta

def extract_payment_and_additional_details_from_Cpdf(pdf_path, debug=False):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            payment_details = {
                "paymentduedate": None,
                "amountoftotaldue": None,
                "currentbalance": None,
                "laststatementdate": None,
                "laststmtbalance": None,
                "amountofpaymentctd": None,
                "amountofothercreditctd": None,
                "amountofcashadvctd": None,
                "amountofpurchasectd": None,
                "amountfeechargesctd": None,
                "amountofinterestctd": None,
                "creditlimit": None,
                "opentobuy": None,
                "billingcycle": None
            }

            # Updated regex patterns for extracting payment details
            patterns = {
                "amountoftotaldue": re.compile(r"Minimum payment due\s*[:\-]?\s*\$?([\d,]+\.\d{2})"),
                "currentbalance": re.compile(r"New balance\s*[:\-]?\s*\$?([\d,]+\.\d{2})"),
                "laststmtbalance": re.compile(r"Previous balance\s*[:\-]?\s*\$?([\d,]+\.\d{2})"),
                "amountofpaymentctd": re.compile(r"Payments\s*[:\-]?\s*\$?([\d,]+\.\d{2})"),
                "amountofothercreditctd": re.compile(r"Credits\s*[:\-]?\s*\$?([\d,]+\.\d{2})"),
                "amountofcashadvctd": re.compile(r"Cash advances\s*[:\-\+]?\s*\$?([\d,]+\.\d{2})"),
                "amountofpurchasectd": re.compile(r"Purchases\s*[:\-\+]?\s*\$?([\d,]+\.\d{2})"),
                "amountfeechargesctd": re.compile(r"Fees\s*[:\-\+]?\s*\$?([\d,]+\.\d{2})"),
                "amountofinterestctd": re.compile(r"Interest\s*[:\-\+]?\s*\$?([\d,]+\.\d{2})"),
                "creditlimit": re.compile(r"Credit Limit\s*[:\-]?\s*\$?([\d,]+)"),
                "opentobuy": re.compile(r"Available Credit Limit\s*[:\-]?\s*\$?([\d,]+)")
            }

            # Only process the first page
            page = pdf.pages[0]
            text = page.extract_text()

            # Extract payment due date explicitly
            payment_due_date_match = re.search(r"Payment due date\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", text)
            if payment_due_date_match:
                date_str = payment_due_date_match.group(1)
                try:
                    date_obj = datetime.strptime(date_str, "%m/%d/%y")
                    payment_details["paymentduedate"] = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    try:
                        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
                        payment_details["paymentduedate"] = date_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        if debug:
                            print(f"Error parsing payment due date: {date_str}")
                if debug:
                    print(f"paymentduedate Found: {payment_details['paymentduedate']}")

                # Calculate the billing cycle based on paymentduedate
                if date_obj:
                    # Force month to January
                    january_date = date_obj.replace(month=1)

                    # Add 6 days
                    billing_cycle_date = january_date + timedelta(days=6)

                    # Handle day overflow
                    if billing_cycle_date.day > 31:
                        billing_cycle_date = billing_cycle_date.replace(day=billing_cycle_date.day - 31)

                    # Extract only the day part and store it
                    payment_details["billingcycle"] = f"{billing_cycle_date.day:02d}"

            # Extract billing period
            billing_period_match = re.search(r"Billing Period:\s*(.+?)(?=\n|$)", text, re.DOTALL)
            if billing_period_match:
                billing_period_text = billing_period_match.group(1).strip()
                date_range_match = re.search(r"(\d{1,2}/\d{1,2}/\d{2})-(\d{1,2}/\d{1,2}/\d{2})", billing_period_text)
                if date_range_match:
                    end_date_str = date_range_match.group(2)
                    try:
                        end_date_obj = datetime.strptime(end_date_str, "%m/%d/%y")
                        payment_details["laststatementdate"] = end_date_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        try:
                            end_date_obj = datetime.strptime(end_date_str, "%m/%d/%Y")
                            payment_details["laststatementdate"] = end_date_obj.strftime("%Y-%m-%d")
                        except ValueError:
                            if debug:
                                print(f"Error parsing last statement date: {end_date_str}")
                if debug:
                    print(f"Billing Period Found: {billing_period_text}")

            # Extract other details
            for key, pattern in patterns.items():
                match = re.search(pattern, text)
                if match:
                    value = match.group(1).replace(",", "")
                    payment_details[key] = f"{float(value):.2f}"
                    if debug:
                        print(f"{key} Found: {payment_details[key]}")

            return payment_details

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
