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
                "opentobuy": None
            }

            # Define regex patterns for extracting payment details
            patterns = {
                "paymentduedate": re.compile(r"Payment Due Date\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{4})"),
                "amountoftotaldue": re.compile(r"Minimum Payment\s*[:\-]?\s*\$?([\d,]+\.\d{2})"),
                "currentbalance": re.compile(r"New Balance\s*[:\-]?\s*\$?([\d,]+\.\d{2})"),
                "laststatementdate": re.compile(r"Statement Period\s*(\d{2}/\d{2}/\d{4})\s*to\s*(\d{2}/\d{2}/\d{4})"),
                "laststmtbalance": re.compile(r"Previous Balance\s*[:\-]?\s*\$?([\d,]+\.\d{2})"),
                "amountofpaymentctd": re.compile(r"Payments\s*[:\-]?\s*\$?(\d+,?\d*\.\d{2})"),
                "amountofothercreditctd": re.compile(r"Other Credits\s*[:\-]?\s*\$?(\d+,?\d*\.\d{2})"),
                "amountofcashadvctd": re.compile(r"Cash Advances\s*[:\-]?\s*\$?(\d+,?\d*\.\d{2})"),
                "amountofpurchasectd": re.compile(r"Purchases, Balance Transfers &\s*[:\-]?\s*\$?(\d+,?\d*\.\d{2})"),
                "amountfeechargesctd": re.compile(r"Fees Charged\s*[:\-]?\s*\$?(\d+,?\d*\.\d{2})"),
                "amountofinterestctd": re.compile(r"Interest Charged\s*[:\-]?\s*\$?(\d+,?\d*\.\d{2})"),
                "creditlimit": re.compile(r"Total Credit Limit\s*[:\-]?\s*\$?([\d,]+(?:\.\d{2})?)"),
                "opentobuy": re.compile(r"Total Available Credit\s*[:\-]?\s*\$?([\d,]+(?:\.\d{2})?)")
            }

            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                text = page.extract_text()

                if debug:
                    print(f"\n--- Raw Text from Page {page_num + 1} ---\n{text}")

                if not text:
                    print(f"No text found on Page {page_num + 1}. Skipping...")
                    continue

                # Extract details line by line
                for line in text.split("\n"):
                    for key, pattern in patterns.items():
                        match = re.search(pattern, line)
                        if match:
                            value = match.group(1).replace(",", "")

                            # Store payment due date directly
                            if key == "paymentduedate":
                                payment_details[key] = match.group(1)
                                if debug:
                                    print(f"{key} Found: {payment_details[key]}")

                            # Extract last statement date
                            elif key == "laststatementdate":
                                end_date = match.group(2)
                                payment_details[key] = end_date
                                if debug:
                                    print(f"{key} Found: {payment_details[key]}")

                            # Store numeric values for other fields
                            else:
                                payment_details[key] = f"{float(value):.2f}"
                                if debug:
                                    print(f"{key} Found: {payment_details[key]}")

            return payment_details

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
