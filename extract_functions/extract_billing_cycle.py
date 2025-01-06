import pdfplumber
import re
from datetime import datetime, timedelta

def calculate_billing_cycle_from_due_date(pdf_path, debug=False):
    try:
        # Extract text from PDF
        pdf_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                pdf_text += page.extract_text()

        # Regex to extract payment due date in MM/DD/YYYY format
        match = re.search(r"Payment Due Date\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{4})", pdf_text)

        if match:
            due_date_str = match.group(1)
            
            # Convert the extracted date to a datetime object
            due_date = datetime.strptime(due_date_str, '%m/%d/%Y')

            # Force the month to January (01) but keep the day and year
            jan_date = due_date.replace(month=1)

            # Add 6 days to the January date
            billing_cycle_date = jan_date + timedelta(days=6)

            # Extract and return just the day (DD) part as a string
            billing_cycle_day = billing_cycle_date.strftime('%d')

            if debug:
                print(f"Payment Due Date: {due_date_str}")
                print(f"Billing Cycle Day (Day + 6): {billing_cycle_day}")

            return billing_cycle_day
        else:
            if debug:
                print("Payment Due Date not found in PDF text.")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
