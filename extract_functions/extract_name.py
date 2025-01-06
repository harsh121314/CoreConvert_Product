import pdfplumber
import re

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

            page = pdf.pages[0]
            page_width = page.width
            page_height = page.height
            bottom_left_bbox = (0, page_height * 0.7, page_width * 0.4, page_height)

            cropped_text = page.within_bbox(bottom_left_bbox).extract_text()

            if not cropped_text:
                print("No text found in the bottom-left corner.")
                return extracted_details

            lines = cropped_text.split("\n")
            name_found = False
            address_lines = []
            for line in lines:
                line = line.strip()
                if not name_found:
                    name_pattern = r"([A-Z]+)\s([A-Z]+)(?:\s([A-Z]+))?"
                    name_match = re.match(name_pattern, line)
                    if name_match:
                        extracted_details["firstname"] = name_match.group(1)
                        extracted_details["middlename"] = name_match.group(2) if name_match.group(2) else ""
                        extracted_details["lastname"] = name_match.group(3) if name_match.group(3) else ""
                        name_found = True
                        continue

                if name_found:
                    address_lines.append(line)

            if address_lines:
                extracted_details["addressline1"] = address_lines[0]
                print(f"Name and Address Extracted: {extracted_details}")

            return extracted_details
    except Exception as e:
        print(f"Error during name extraction: {e}")
        return None
