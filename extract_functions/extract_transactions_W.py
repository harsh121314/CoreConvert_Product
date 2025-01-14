import pdfplumber
import re
from datetime import datetime


# Function to extract transactions from the PDF
def extract_transactions_from_Wpdf(pdf_path, debug=False):
    try:
        transactions = []
        current_year = datetime.now().year
        with pdfplumber.open(pdf_path) as pdf:
            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                text = page.extract_text()

                if debug:
                    print(f"\n--- Raw Text from Page {page_num + 1} ---\n")
                    print(text)

                payments_section = []
                purchases_section = []
                capture_payments = False
                capture_purchases = False

                # Extract line by line to ensure no missed entries
                for line in text.splitlines():
                    if "Payments" in line:
                        capture_payments = True
                        capture_purchases = False
                    elif "TOTAL PAYMENTS FOR THIS PERIOD" in line:
                        capture_payments = False
                    elif "Purchases, Balance Transfers & Other Charges" in line:
                        capture_purchases = True
                        capture_payments = False
                    elif "TOTAL PURCHASES, BALANCE TRANSFERS & OTHER CHARGES FOR THIS PERIOD" in line:
                        capture_purchases = False
                    
                    if capture_payments and re.match(r'\d{2}/\d{2}', line):
                        payments_section.append(line)
                    if capture_purchases and re.match(r'\d{4}', line):
                        purchases_section.append(line)

                if debug and payments_section:
                    print("\n--- Payments Section Extracted ---\n")
                    print("\n".join(payments_section))
                
                if debug and purchases_section:
                    print("\n--- Purchases Section Extracted ---\n")
                    print("\n".join(purchases_section))

                # Combine extracted payment and purchase lines for regex processing
                payments_section_text = "\n".join(payments_section)
                purchases_section_text = "\n".join(purchases_section)

                # Updated regex to capture transactions for Payments
                payments_pattern = r"(\d{2}/\d{2})\s+(\d{2}/\d{2})\s+(\w+)\s+(.+?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)"
                # Updated regex to capture full description for Purchases until amount
                purchases_pattern = r"(\d{4})\s(\d{2}/\d{2})\s(\d{2}/\d{2})\s(\w+)\s+(.+?)\s(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)$"

                # Parsing Payments Section
                payment_matches = re.findall(payments_pattern, payments_section_text, re.MULTILINE)
                for match in payment_matches:
                    effective_date = datetime.strptime(f"{current_year}/{match[0]}", "%Y/%m/%d").strftime("%Y-%m-%d")
                    post_date = datetime.strptime(f"{current_year}/{match[1]}", "%Y/%m/%d").strftime("%Y-%m-%d")
                    amount = -float(match[4].replace(',', ''))  # Mark as negative for credit
                    
                    transactions.append({
                        "traneffectivedate": effective_date,
                        "tranpostdate": post_date,
                        "tranreferencenumber": match[2],
                        "cardacceptornamelocation": match[3],
                        "amount": amount
                    })
                
                # Parsing Purchases Section
                purchase_matches = re.findall(purchases_pattern, purchases_section_text, re.MULTILINE)
                for match in purchase_matches:
                    effective_date = datetime.strptime(f"{current_year}/{match[1]}", "%Y/%m/%d").strftime("%Y-%m-%d")
                    post_date = datetime.strptime(f"{current_year}/{match[2]}", "%Y/%m/%d").strftime("%Y-%m-%d")
                    amount = float(match[5].replace(',', ''))  # Positive for charges
                    
                    transactions.append({
                        "cardlast4": match[0],
                        "traneffectivedate": effective_date,
                        "tranpostdate": post_date,
                        "tranreferencenumber": match[3],
                        "cardacceptornamelocation": match[4],
                        "amount": amount
                    })
        return transactions
    except Exception as e:
        print(f"An error occurred: {e}")
        return []