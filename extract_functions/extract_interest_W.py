import pdfplumber
import re

# Function to extract interest charge and cash advance details from the PDF
def extract_interest_from_Wpdf(pdf_path, debug=False):
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