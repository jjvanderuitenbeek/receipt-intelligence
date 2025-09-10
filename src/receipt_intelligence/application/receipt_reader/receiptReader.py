import sys
import sqlite3
from pathlib import Path
import os
import pdfplumber
from abc import ABC, abstractmethod
from typing import Dict, Any
import re
from datetime import date

import base64
from groq import Groq

from dotenv import load_dotenv
import json

#sys.path.append(str(Path().resolve()))

load_dotenv()
from src.receipt_intelligence.config import settings
from src.receipt_intelligence.application.receipt_reader.utils import encode_image

class ReceiptProcessor(ABC):
    """Abstract base class for receipt readers."""

    def __init__(self):
        
        # connect to database
        self.conn = sqlite3.connect(settings.DB_PATH)
        self.cursor = self.conn.cursor()

    @abstractmethod
    def process_all_receipts(self):
        pass

    @abstractmethod
    def read_receipt(self):
        pass

    @abstractmethod
    def parse_receipt(self):
        pass


    def insert_receiptline_into_database(self, filename: str, receipt_date: str, store_cod: str, product: str, quantity: int, price_unit: float, price_total: float, discount_ind: str):
        
        load_date = date.today()
        submitted_by = "jjvanderuitenbeek"
        
        # Insert a row into a table
        self.cursor.execute(
        """
            INSERT INTO receiptTable (submitted_by, filename, receipt_date, store_cod, product, quantity, price_unit, price_total, discount_ind, load_date)
            SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            WHERE NOT EXISTS (SELECT 1 FROM receiptTable WHERE filename = ?)
        """,
            (submitted_by, filename, receipt_date, store_cod, product, quantity, price_unit, price_total, discount_ind, load_date, filename)
        )
        # Commit changes
        self.conn.commit()



class AHReceiptProcessor(ReceiptProcessor):
    """
        Subclass to parse AH receipts
        Contains method to process a Albert Heijn receipt string and write the results to database      
    """

    def process_all_receipts(self):
        """
            Process all PDFs in a folder.
        """

        folder_path = settings.PDF_AH_PATH

        for file in os.listdir(folder_path):
            if file.lower().endswith(".pdf"):
                file_path = os.path.join(folder_path, file)
                text = self.read_receipt(file_path)
                self.parse_receipt(file, text)

        # Close connection
        self.conn.close()

    def read_receipt(self, file_path: str) -> str:
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
    
    def parse_receipt(self, filename: str, receipt_text: str) -> None:
        """
            Process a Albert Heijn receipt string and write the results to database
            The boolean variables start_receipt and end_receipt are used to catch the start and end of the receipt
            For each line in the receipt, the following components are extracted: quantity, product, price_unit, price_total, bonuscode
            The values are then written to the receiptTable in the database
        """

        # define booleans to catch start of receipt and end of receipt
        start_receipt = 0
        end_receipt = 0

        # loop over all lines in the receipt
        for line in receipt_text.splitlines():

            if 'SUBTOTAAL' in line:
                end_receipt = 1  

            # only for the line items: extarct the different components
            if start_receipt == 1 and end_receipt == 0:
                match = re.match(r"(\d+)?\s*([A-Z ]+)?\s*([\d,]+)?\s*([\d,]+)?\s*([A-Z])?", line)
                if match:
                    quantity, product, price_unit, price_total, bonuscode = match.groups()
                    
                    # define variables to insert into database
                    filename = filename
                    receipt_date = "9999-12-31"
                    store_cod = "AH"

                    # transform values to database types
                    quantity = int(quantity)
                    product = product.strip()
                    price_unit = float(price_unit.replace(",", "."))
                    price_total = quantity * price_unit
                    discount_ind = "J" if bonuscode == "B" else "N"

                    # write to database
                    self.insert_receiptline_into_database(filename, receipt_date, store_cod, product, quantity, price_unit, price_total, discount_ind)

            if 'BONUSKAART' in line:
                start_receipt = 1

class LidlReceiptProcessor(ReceiptProcessor):
    """
        Subclass to parse Lidl receipts
        Contains method to process a Lidl receipt image using a multimodal model and write the results to database      
    """

