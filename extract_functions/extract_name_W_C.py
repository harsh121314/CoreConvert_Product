import pdfplumber
import re

def extract_name_and_address_from_WCpdf(pdf_path, debug=False):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            extracted_details = {
                "firstname": "",
                "middlename": "",
                "lastname": "",
                "addressline1": "",
                "addressline2": ""
            }

            # Access the first page and define the extraction region (bottom-left)
            page = pdf.pages[0]
            page_width = page.width
            page_height = page.height
            bottom_left_bbox = (0, page_height * 0.8, page_width * 0.4, page_height)

            cropped_text = page.within_bbox(bottom_left_bbox).extract_text()

            if not cropped_text:
                print("No text found in the bottom-left corner.")
                return extracted_details

            # Split the extracted text into lines
            lines = cropped_text.split("\n")
            name_found = False
            address_lines = []

            # Step 1: Parse name and address from the text
            for line in lines:
                line = line.strip()
                if not name_found:
                    # Match name pattern (first, optional middle, last)
                    name_pattern = r"([A-Z]+)\s([A-Z]+)(?:\s([A-Z]+))?$"
                    name_match = re.match(name_pattern, line)
                    
                    if name_match:
                        extracted_details["firstname"] = name_match.group(1)
                        if name_match.group(3):  # If a third match exists, it's the last name
                            extracted_details["middlename"] = name_match.group(2)
                            extracted_details["lastname"] = name_match.group(3)
                        else:
                            extracted_details["lastname"] = name_match.group(2)
                        
                        name_found = True
                        continue
                
                # Append remaining lines as potential address lines
                if name_found and line:
                    address_lines.append(line)

            # Step 2: Assign address lines
            if len(address_lines) > 0:
                extracted_details["addressline1"] = address_lines[0]
            
            if len(address_lines) > 1:
                raw_addressline2 = address_lines[1]
                
                # Step 3: Remove all spaces from the address
                cleaned_addressline2 = re.sub(r'\s+', '', raw_addressline2)
                
                # Step 4: Locate the first number (ZIP code start) and insert space before it
                zip_match = re.search(r"\d", cleaned_addressline2)
                
                if zip_match:
                    zip_index = zip_match.start()
                    formatted_addressline2 = cleaned_addressline2[:zip_index] + " " + cleaned_addressline2[zip_index:]
                    
                    # Add extra space 2 characters before the ZIP code
                    if zip_index > 2:
                        formatted_addressline2 = (
                            formatted_addressline2[:zip_index - 2] + " " + formatted_addressline2[zip_index - 2:]
                        )
                    
                    extracted_details["addressline2"] = formatted_addressline2
                else:
                    # If no ZIP code is found, fallback to cleaned address without modifications
                    extracted_details["addressline2"] = cleaned_addressline2

            # Print extracted details (for testing/debugging)
            print(f"Name and Address Extracted: {extracted_details}")
            return extracted_details

    except Exception as e:
        print(f"Error during name extraction: {e}")
        return None
