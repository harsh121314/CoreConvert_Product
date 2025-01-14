import pdfplumber
import re

def extract_interest_from_Cpdf(pdf_path, debug=False):
    def clean_value(value):
        
        value = re.sub(r'[^\d.-]', '', value)  # Keep only numbers, decimal points, and minus signs
        return float(value) if value else None

    interest_details = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if "Interest charge calculation" in text:
                if debug:
                    print("Found 'Interest charge calculation' section.")

                # Extract the "Interest charge calculation" section
                table_text = text.split("Interest charge calculation", 1)[-1]

                # Regex to match data for Standard Purch and Standard Adv
                purchases_match = re.search(r"Standard Purch\s+([\d.]+)%.*?\$([\d.,]+).*?\$([\d.,]+)", table_text)
                advances_match = re.search(r"Standard Adv\s+([\d.]+)%.*?\$([\d.,]+).*?\$([\d.,]+)", table_text)

                if purchases_match:
                    apr, totalbsfc, interestbnp = map(clean_value, purchases_match.groups())
                    interest_details.append({
                        "plantype": "PURCHASES",
                        "apr": apr,
                        "totalbsfc": totalbsfc,
                        "interestbnp": interestbnp,
                    })
                    if debug:
                        print(f"Parsed PURCHASES: {interest_details[-1]}")

                if advances_match:
                    apr, totalbsfc, interestbnp = map(clean_value, advances_match.groups())
                    interest_details.append({
                        "plantype": "ADVANCES",
                        "apr": apr,
                        "totalbsfc": totalbsfc,
                        "interestbnp": interestbnp,
                    })
                    if debug:
                        print(f"Parsed ADVANCES: {interest_details[-1]}")

                # Exit early after processing relevant data
                break

    if debug and not interest_details:
        print("No valid interest details found.")

    return interest_details
