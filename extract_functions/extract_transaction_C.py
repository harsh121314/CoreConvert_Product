import pdfplumber
import re
from datetime import datetime

def extract_transaction_from_Cpdf(pdf_path, payment_due_date=None, debug=False):
    transactions = []
    card_last4 = None  # Initialize card_last4 as None
    
    # Parse the payment_due_date into a datetime object for reference
    if payment_due_date:
        reference_date = datetime.strptime(payment_due_date, "%Y-%m-%d")
    else:
        reference_date = datetime.now()  # Default to the current date if no due date provided

    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text()

            if debug:
                print(f"\n--- Raw Text from Page {page_num + 1} ---\n")
                print(text)

            # Find "Card Ending in ****"
            if "Card ending in" in text:
                match = re.search(r"Card ending in (\d{4})", text)
                if match:
                    card_last4 = match.group(1)
                    if debug:
                        print(f"Found Card Last 4: {card_last4}")

            # Locate "Payments, Credits and Adjustments" section
            if "Payments, Credits and Adjustments" in text:
                lines = text.splitlines()
                capture_payments = False

                for line in lines:
                    # Start capturing payments section
                    if "Payments, Credits and Adjustments" in line:
                        capture_payments = True
                        if debug:
                            print("\n--- Found Payments Section ---\n")
                        continue

                    # Stop capturing when a new section starts
                    if capture_payments and ("Purchases" in line or "Balance Transfers" in line):
                        capture_payments = False
                        break

                    if capture_payments:
                        # Regex for payment transactions
                        payment_pattern = r"^\s*(\d{2}/\d{2})\s+(.+?)\s+(-?\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)$"
                        match = re.match(payment_pattern, line)

                        if match:
                            try:
                                post_date = match.group(1)  # Post Date
                                description = match.group(2).strip()
                                amount = float(match.group(3).replace("$", "").replace(",", ""))

                                # Infer the year using date wraparound logic
                                transaction_date = datetime.strptime(post_date, "%m/%d")
                                inferred_year = reference_date.year
                                if transaction_date.month > reference_date.month or (
                                    transaction_date.month == reference_date.month
                                    and transaction_date.day > reference_date.day
                                ):
                                    inferred_year -= 1
                                transaction_date = transaction_date.replace(year=inferred_year)
                                formatted_post_date = transaction_date.strftime("%Y-%m-%d")

                                # Add payment transaction
                                transactions.append({
                                    "cardlast4": card_last4,
                                    "tranpostdate": formatted_post_date,
                                    "trandescription": description,
                                    "transactionamount": amount
                                })

                                if debug:
                                    print(f"Added payment transaction: {transactions[-1]}")
                            except Exception as e:
                                if debug:
                                    print(f"Error parsing line: {line} - {e}")
                        elif debug:
                            print(f"No match found for line: {line}")

            # Locate "Standard Purchases" section
            if "Standard Purchases" in text:
                lines = text.splitlines()
                capture_purchases = False
                transaction_buffer = []  # Buffer to accumulate lines for a single transaction

                for line in lines:
                    # Start capturing purchases section
                    if "Standard Purchases" in line:
                        capture_purchases = True
                        if debug:
                            print("\n--- Found Standard Purchases Section ---\n")
                        continue

                    # Stop capturing when "Fees Charged" is found
                    if capture_purchases and "Fees Charged" in line:
                        capture_purchases = False
                        break

                    if capture_purchases:
                        transaction_buffer.append(line.strip())

                        # Regex for detecting complete transactions
                        purchase_pattern = (
                            r"(\d{2}/\d{2})\s+"  # Effective Date
                            r"(\d{2}/\d{2})\s+"  # Post Date
                            r"(.+?)\s+"          # Description until state abbreviation
                            r"(\b[A-Z]{2}\b)\s+"  # State Abbreviation
                            r"(\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)$"  # Transaction Amount
                        )
                        combined_line = " ".join(transaction_buffer)
                        match = re.search(purchase_pattern, combined_line)

                        if match:
                            try:
                                # Extract transaction details
                                effective_date = match.group(1)
                                post_date = match.group(2)
                                location = f"{match.group(3)} {match.group(4)}"  # Include the state abbreviation
                                amount = float(match.group(5).replace("$", "").replace(",", ""))

                                # Infer the year for effective date
                                effective_date_obj = datetime.strptime(effective_date, "%m/%d")
                                inferred_year = reference_date.year
                                if effective_date_obj.month > reference_date.month or (
                                    effective_date_obj.month == reference_date.month
                                    and effective_date_obj.day > reference_date.day
                                ):
                                    inferred_year -= 1
                                effective_date_obj = effective_date_obj.replace(year=inferred_year)
                                formatted_effective_date = effective_date_obj.strftime("%Y-%m-%d")

                                # Infer the year for post date
                                post_date_obj = datetime.strptime(post_date, "%m/%d").replace(year=inferred_year)
                                formatted_post_date = post_date_obj.strftime("%Y-%m-%d")

                                # Add purchase transaction
                                transactions.append({
                                    "cardlast4": card_last4,
                                    "traneffectivedate": formatted_effective_date,
                                    "tranpostdate": formatted_post_date,
                                    "cardacceptornamelocation": location.strip(),
                                    "transactionamount": amount
                                })

                                if debug:
                                    print(f"Added purchase transaction: {transactions[-1]}")

                                # Reset the buffer for the next transaction
                                transaction_buffer = []
                            except Exception as e:
                                if debug:
                                    print(f"Error parsing transaction: {combined_line} - {e}")
                                transaction_buffer = []

    return transactions
