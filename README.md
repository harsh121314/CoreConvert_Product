# CoreConvert Product

## Overview
CoreConvert Product is a comprehensive Python-based solution designed for the extraction and conversion of
financial data from bank statement PDFs into JSON formats. This product supports PDFs from CITI Bank and 
Wells Fargo, parsing detailed information like transactions, payments, and interest charges, and make this
data easily accessible and manipulable for financial analysis or integration into software system.

## PDFs Processed
This system processes the following types of PDFs:
~ CITI Bank Statement: Includes transactions, payments, and Account Summaries for accounts linked with the
Costco Anywhere Visa Card.
~ Wells Fargo Statement: Contains detailed transactions and account summaries for Wells Fargo Advised Premium 
Rewards Signature accounts.

These documents provide comprehensive monthly financial summaries crucial for personal and 
corporate finance management.

## Modules Description

# extract_name_W_C.py
This module extracts the name and the address details from the first page of the PDFs, specifically
targetting the bottom-left region. It identifies the name( including first, middle and last names) 
using a regex pattern and parses the address lines, formatting them appropriately. The module ensures
accurate extraction by handling variations in text structure and formatting, making it useful for
processing both CITI Bank and Wells Fargo statements.

# extract_payment_C.py & extract_payment_W.py
These modules extracts details from CITI Bank and Wells Fargo PDF statements using pdfplumber and regex.
They parse key data like payment due date, balances, and charges, format datesto YYYY-MM-DD,
and calculate billing cycle while supporting debug output for troubleshooting.

# extract_transaction_from_Cpdf.py & extract_transaction_from_Wpdf.py
These modules parse transaction details from CITI Bank and Wells Fargo PDF statements using pdfplumber
for text extraction and regex for identifying patterns like dates, amounts and descriptions. Both 
handle date interference for transactions, split text line-by-line for detailed parsing, and 
return structured data as a list of transactions.

# extract_interest_C.py & extract_interest_W.py
This module extracts interest-related details from Citi Bank and Wells Fargo PDF statements,respectively.
Both modules use pdfplumber to extract text and regex to identify patterns for key fields like APR,
balances, and interest amounts. While the Citi Bank module focuses on parsing "Interest charge calculation"
sections for purchases and advances, the Wells Fargo module captures additional details like days in cycle and
plan balances for purchases and cash advances. Both return structured interest details as lists of dictionaries
for further analysis.

## Installation

Clone the repository to your local machine:
~ git clone (("https://github.com/harsh121314/CoreConvert_Product.git"))

Navigate to the project directory:
~ cd CoreConvert

Install the required dependencies:
~ pip install -r requirements.txt

## Usage

Run the main script to extract data from the PDF

## Features

Modular Design: Separate modules for Citi Bank and Wells Fargo PDFs.

Interest and Transaction Extraction: Parses APR, balances, and transaction details.

Custom Regex Matching: Tailored regex patterns for specific PDF formats.

Debugging Support: Optional debugging mode for troubleshooting.

Cross-Bank Support: Handles both text-based and scanned PDF formats.

Date Handling: Automatically infers years for transaction dates.



