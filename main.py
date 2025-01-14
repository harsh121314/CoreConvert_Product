import json
import pdfplumber
from extract_functions.extract_name_W_C import extract_name_and_address_from_WCpdf
from extract_functions.extract_payment_W import extract_payment_and_additional_details_from_Wpdf
from extract_functions.extract_transactions_W import extract_transactions_from_Wpdf
from extract_functions.extract_interest_W import extract_interest_from_Wpdf
from extract_functions.extract_payment_C import extract_payment_and_additional_details_from_Cpdf
from extract_functions.extract_interest_C import extract_interest_from_Cpdf
from extract_functions.extract_transaction_C import extract_transaction_from_Cpdf  # Import the new function

def identify_bank(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        first_line = first_page.extract_text().split('\n')[0] if first_page.extract_text() else ""
        
        if "WELLS FARGO" in first_line:
            return "Wells Fargo"
        elif "Citi" in first_line or "Citibank" in first_line:
            return "Citi"
        else:
            return None

def main():
    # Define the PDF file path
    pdf_path = "pdf_files/WellsFargo2.pdf"
    debug_mode = True  # Enable debugging

    # Identify the bank from the PDF
    bank = identify_bank(pdf_path)
    if not bank:
        print("Bank not recognized. Exiting...")
        return

    # Extract name and address (shared function for both banks)
    name_and_address = extract_name_and_address_from_WCpdf(pdf_path, debug=debug_mode)

    if bank == "Wells Fargo":
        # Extract Wells Fargo-specific details
        payment_details = extract_payment_and_additional_details_from_Wpdf(pdf_path, debug=debug_mode)
        transactions = extract_transactions_from_Wpdf(pdf_path, debug=debug_mode)
        interest_details = extract_interest_from_Wpdf(pdf_path, debug=debug_mode)

    elif bank == "Citi":
        # Extract Citi-specific details
        payment_details = extract_payment_and_additional_details_from_Cpdf(pdf_path, debug=debug_mode)
        laststatementdate = payment_details.get("laststatementdate")

        transactions = extract_transaction_from_Cpdf(pdf_path, debug=debug_mode)  # Use the new function for Citi transactions
        interest_details = extract_interest_from_Cpdf(pdf_path, debug=debug_mode)

    # Combine extracted details into a structured format
    extracted_details = {
        "file_name": pdf_path,
        "account": {
            **name_and_address,
            **payment_details,
        },
        "transactions": transactions,
        "plan": interest_details  # Save interest details here
    }

    # Save the extracted details to a JSON file
    output_file = "extracted_details.json"
    with open(output_file, "w") as json_file:
        json.dump(extracted_details, json_file, indent=4)

    print(f"Extracted details saved to {output_file}")

# Entry point
if __name__ == "__main__":
    main()
