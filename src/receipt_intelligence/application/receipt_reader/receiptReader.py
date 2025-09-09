import sys
import sqlite3
from pathlib import Path
import os
import pdfplumber
from abc import ABC, abstractmethod
from typing import Dict, Any
import re

#sys.path.append(str(Path().resolve()))

from src.receipt_intelligence.config import settings

class ReceiptProcessor(ABC):
    """Abstract base class for receipt readers."""

    def __init__(self):
        
        # connect to database
        self.conn = sqlite3.connect(settings.DB_PATH)
        self.cursor = self.conn.cursor()


    def read_pdf(self, file_path: str) -> str:
        """
            Extracts plain text from a PDF.
            Returns the full receipt in a single string
            Each product is separated by a new line
        """

        full_text = ""

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                full_text += text

        return full_text 

    def process_all_receipts(self, folder_path: str):
        """
            Process all PDFs in a folder.
        """
        for file in os.listdir(folder_path):
            if file.lower().endswith(".pdf"):
                file_path = os.path.join(folder_path, file)
                text = self.read_pdf(file_path)
                self.parse_receipt(file, text)

        # Close connection
        self.conn.close()


class AHReceiptProcessor(ReceiptProcessor):
    """
        Subclass to parse AH receipts
        Contains method to process a Albert Heijn receipt string and write the results to database      
    """

    def parse_receipt(self, filename: str, receipt_text: str) -> None:

        # define booleans to catch start of receipt and end of receipt
        start_receipt = 0
        end_receipt = 0

        print(filename)
        print(receipt_text)

        # loop over all lines in the receipt
        for line in receipt_text.splitlines():

            if 'SUBTOTAAL' in line:
                end_receipt = 1  

            # only for the line items: extarct the different components
            if start_receipt == 1 and end_receipt == 0:
                match = re.match(r"(\d+)?\s*([A-Z ]+)?\s*([\d,]+)?\s*([\d,]+)?\s*([A-Z])?", line)
                if match:
                    quantity, product, price_unit, price_total, bonuscode = match.groups()
                    
                    
                    # transform values to database types
                    quantity = int(quantity)
                    product = product.strip()
                    price_unit = float(price_unit.replace(",", "."))
                    price_total = quantity * price_unit
                    discount_ind = "J" if bonuscode == "B" else "N"

                    # Insert a row into a table
                    self.cursor.execute(
                        """
                            INSERT INTO receiptTable (filename, product, quantity, price_unit, price_total, discount_ind)
                            SELECT ?, ?, ?, ?, ?, ?
                            WHERE NOT EXISTS (
                            SELECT 1 FROM receiptTable WHERE filename = ?
                            )
                        """,
                        (filename, product, quantity, price_unit, price_total, discount_ind, filename)
                    )
                    # Commit changes
                    self.conn.commit()


            if 'BONUSKAART' in line:
                start_receipt = 1

