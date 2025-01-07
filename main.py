import json
from extract_functions.extract_name import extract_name_and_address_from_pdf
from extract_functions.extract_payment import extract_payment_and_additional_details_from_pdf
from extract_functions.extract_transactions import extract_transactions_from_pdf
from extract_functions.extract_interest import extract_interest_and_cash_advance_from_pdf
from extract_functions.extract_billing_cycle import calculate_billing_cycle_from_due_date

def main():
    # Define the PDF file path
    pdf_path = "pdf_files/WellsFargo1.pdf"
    debug_mode = True  # Enable debugging

    # Step 1: Extract name and address
    name_and_address = extract_name_and_address_from_pdf(pdf_path, debug=debug_mode) 

    # Step 2: Extract payment details
    payment_details = extract_payment_and_additional_details_from_pdf(pdf_path, debug=debug_mode) 

    # Step 3: Extract transactions
    transactions = extract_transactions_from_pdf(pdf_path, debug=debug_mode) 

    # Step 4: Extract interest details
    interest_details = extract_interest_and_cash_advance_from_pdf(pdf_path, debug=debug_mode) 

    # Step 5: Extract PDF text for billing cycle calculation
    billing_cycle_day = calculate_billing_cycle_from_due_date(pdf_path, debug=debug_mode)
    # Combine extracted details
    extracted_details = {
        "file_name": pdf_path,
        "account": {
            **name_and_address,
            **payment_details,
            "billingcycle": billing_cycle_day if billing_cycle_day else "N/A"
        },
        "transactions": transactions,
        "plan": interest_details
    }

    # Save to JSON
    output_file = "extracted_details.json"
    with open(output_file, "w") as json_file:
        json.dump(extracted_details, json_file, indent=4)

    print(f"Extracted details saved to {output_file}")

# Entry point
if __name__ == "__main__":
    main()
