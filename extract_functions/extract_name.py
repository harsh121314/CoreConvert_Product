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

            if debug:
                print("\n--- Cropped Text from Bottom-Left Corner ---\n")
                print(cropped_text)

            if not cropped_text:
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
                if len(address_lines) >= 2:
                    extracted_details["addressline1"] = address_lines[0]
                    formatted_address = address_lines[1].replace(" ", "")
                    address_match = re.search(r"(\D+)(\d{5}.*)", formatted_address)
                    if address_match:
                        alpha_part = address_match.group(1)
                        numeric_part = address_match.group(2)
                        if len(alpha_part) > 2:
                            alpha_part = alpha_part[:-2] + ' ' + alpha_part[-2:]
                        extracted_details["addressline2"] = alpha_part + " " + numeric_part
                else:
                    extracted_details["addressline1"] = address_lines[0]

            return extracted_details
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
