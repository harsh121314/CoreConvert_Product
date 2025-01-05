import pdfplumber
import re
from datetime import datetime

def extract_payment_and_additional_details_from_pdf(pdf_path, debug=False):
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

            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                text = page.extract_text()

                if debug:
                    print(f"\n--- Raw Text from Page {page_num + 1} ---\n{text}")

                if not text:
                    print(f"No text found on Page {page_num + 1}. Skipping...")
                    continue

                # Define regex patterns for extracting payment details
                patterns = {
                    "paymentduedate": r"Payment Due Date\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{4})",
                    "amountoftotaldue": r"Minimum Payment\s*[:\-]?\s*\$?([\d,]+\.\d{2})",
                    "currentbalance": r"New Balance\s*[:\-]?\s*\$?([\d,]+\.\d{2})",
                    "laststatementdate": r"Statement Period\s*(\d{2}/\d{2}/\d{4})\s*to\s*(\d{2}/\d{2}/\d{4})",
                    "laststmtbalance": r"Previous Balance\s*[:\-]?\s*\$?([\d,]+\.\d{2})",
                    "amountofpaymentctd": r"Payments\s*[:\-]?\s*\$?(\d+,?\d*\.\d{2})",
                    "amountofothercreditctd": r"Other Credits\s*[:\-]?\s*\$?(\d+,?\d*\.\d{2})",
                    "amountofcashadvctd": r"Cash Advances\s*[:\-]?\s*\$?(\d+,?\d*\.\d{2})",
                    "amountofpurchasectd": r"Purchases, Balance Transfers &\s*[:\-]?\s*\$?(\d+,?\d*\.\d{2})",
                    "amountfeechargesctd": r"Fees Charged\s*[:\-]?\s*\$?(\d+,?\d*\.\d{2})",
                    "amountofinterestctd": r"Interest Charged\s*[:\-]?\s*\$?(\d+,?\d*\.\d{2})",
                    "creditlimit": r"Total Credit Limit\s*[:\-]?\s*\$?([\d,]+(?:\.\d{2})?)",
                    "opentobuy": r"Total Available Credit\s*[:\-]?\s*\$?([\d,]+(?:\.\d{2})?)"
                }

                # Extract details line by line
                for line in text.split("\n"):
                    for key, pattern in patterns.items():
                        match = re.search(pattern, line)
                        if match:
                            value = match.group(1).replace(",", "")

                            # Handle date extraction for paymentduedate
                            if key == "paymentduedate":
                                payment_details[key] = match.group(1)

                                # Extract day and add 6
                                _, day, _ = match.group(1).split("/")
                                new_day = int(day) + 6
                                billingcycle = str(new_day)  # Convert to string
                                payment_details["billingcycle"] = billingcycle

                                if debug:
                                    print(f"{key} Found: {payment_details[key]}")
                                    print(f"Billing Cycle (Day + 6): {billingcycle}")

                            elif key == "laststatementdate":
                                end_date = match.group(2)
                                payment_details[key] = end_date
                                if debug:
                                    print(f"{key} Found: {payment_details[key]}")

                            else:
                                # Store numeric values for other fields
                                payment_details[key] = f"{float(value):.2f}"
                                if debug:
                                    print(f"{key} Found: {payment_details[key]}")

            return payment_details

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
