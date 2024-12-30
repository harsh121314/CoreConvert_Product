import pdfplumber
import re
import json
from datetime import datetime

# Function to extract name and address from the bottom-left corner of the first column
def extract_name_and_address_from_pdf(pdf_path, debug=False):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            extracted_details = {
                "firstname": "",
                "middlename": "",
                "lastname": "",
                "addressline1": "",
                "addressline2": ""
            }

            # Only process the first page
            page = pdf.pages[0]

            # Get dimensions of the page and calculate column boundaries
            page_width = page.width
            page_height = page.height

            # Define the region for the bottom-left corner (cropping vertically and horizontally)
            bottom_left_bbox = (0, page_height * 0.7, page_width * 0.4, page_height)

            # Crop the region for the bottom-left corner
            cropped_text = page.within_bbox(bottom_left_bbox).extract_text()

            if debug:
                print("\n--- Cropped Text from Bottom-Left Corner ---\n")
                print(cropped_text)

            if not cropped_text:
                print("No text found in the bottom-left corner. Skipping...")
                return extracted_details

            # Split cropped text into lines
            lines = cropped_text.split("\n")

            # Extract name and address from the cropped text
            name_found = False
            address_lines = []
            for line in lines:
                line = line.strip()
                if not name_found:
                    # Look for the name as a sequence of uppercase words
                    name_pattern = r"([A-Z]+)\s([A-Z]+)(?:\s([A-Z]+))?"
                    name_match = re.match(name_pattern, line)
                    if name_match:
                        extracted_details["firstname"] = name_match.group(1)
                        extracted_details["middlename"] = name_match.group(2) if name_match.group(2) else ""
                        extracted_details["lastname"] = name_match.group(3) if name_match.group(3) else ""
                        name_found = True
                        continue  # Move to the next line for address extraction

                # Append lines to the address list after name is found
                if name_found:
                    address_lines.append(line)

            # Format the address into addressline1 and addressline2
            if address_lines:
                if len(address_lines) >= 2:
                    extracted_details["addressline1"] = address_lines[0]
                    formatted_address = address_lines[1].replace(" ", "")

                    # Apply logic to insert space before the first numeric part
                    address_match = re.search(r"(\D+)(\d{5}.*)", formatted_address)
                    if address_match:
                        alpha_part = address_match.group(1)
                        numeric_part = address_match.group(2)

                        # Insert a space two characters before the numeric part starts
                        if len(alpha_part) > 2:
                            alpha_part = alpha_part[:-2] + ' ' + alpha_part[-2:]

                        extracted_details["addressline2"] = alpha_part + " " + numeric_part
                else:
                    extracted_details["addressline1"] = address_lines[0]

            return extracted_details
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to extract payment and additional details
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

            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                text = page.extract_text()

                if debug:
                    print(f"\n--- Raw Text from Page {page_num + 1} ---\n")
                    print(text)

                if not text:
                    print(f"No text found on Page {page_num + 1}. Skipping...")
                    continue

                # Define regex patterns for payment details
                patterns = {
                    "paymentduedate": r"Payment Due Date\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})",
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

                for line in text.split("\n"):
                    for key, pattern in patterns.items():
                        match = re.search(pattern, line)
                        if match:
                            value = match.group(1).replace(",", "")
                            if key == "laststatementdate":
                                end_date = match.group(2)
                                payment_details[key] = datetime.strptime(end_date, '%m/%d/%Y').strftime('%Y-%m-%d')
                            elif key.endswith("date"):
                                payment_details[key] = datetime.strptime(value, '%m/%d/%Y').strftime('%Y-%m-%d')
                            else:
                                payment_details[key] = f"{float(value):.2f}"
                            if debug:
                                print(f"{key} Found: {payment_details[key]}")

            return payment_details
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
        

# Function to extract transactions from the PDF
def extract_transactions_from_pdf(pdf_path, debug=False):
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




    
# Function to extract interest charge and cash advance details from the PDF
def extract_interest_and_cash_advance_from_pdf(pdf_path, debug=False):
    try:
        details = []
        interest_pattern = r"(PURCHASES|CASH ADVANCES)\s+(\d+\.\d+)%\s+\$([\d,]+\.\d{2})\s+(\d+)\s+\$([\d,]+\.\d{2})\s+\$([\d,]+\.\d{2})"
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                text = page.extract_text()
                
                if debug:
                    print(f"\n--- Extracted Text from Page {page_num + 1} ---\n")
                    print(text)
                
                # Extract rows matching the interest pattern
                matches = re.findall(interest_pattern, text)
                for match in matches:
                    entry = {
                        "plantype": match[0],
                        "apr": float(match[1]),
                        "totalbsfc": float(match[2].replace(",", "")),
                        "daysincycle": int(match[3]),
                        "interestbnp": float(match[4].replace(",", "")),
                        "planbalance": float(match[5].replace(",", ""))
                    }
                    details.append(entry)
                
                if not matches and debug:
                    print(f"No Interest Charge Calculation data found on page {page_num + 1}")
        return details
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Main execution
pdf_path = "WellsFargo2.pdf"  
debug_mode = True  # Set to True for debugging output

# Extract name and address
name_and_address = extract_name_and_address_from_pdf(pdf_path, debug=debug_mode)

# Extract payment and additional details
payment_details = extract_payment_and_additional_details_from_pdf(pdf_path, debug=debug_mode)

# Extract transactions
transactions = extract_transactions_from_pdf(pdf_path, debug=debug_mode)

# Extract Interest charge details
interest = extract_interest_and_cash_advance_from_pdf(pdf_path, debug=debug_mode)

# Combine all extracted details into a flat structure
extracted_details = {
    "file_name": pdf_path,
    "account": {
        **name_and_address,
        **payment_details
    },
    "transactions": transactions,
    "plan": interest
}

# Save all extracted details to JSON file
output_file = "extracted_details.json"
with open(output_file, "w") as json_file:
    json.dump(extracted_details, json_file, indent=4)
print(f"Extracted details saved to {output_file}")

