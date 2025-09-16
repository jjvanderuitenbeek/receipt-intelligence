import sys
import sqlite3
from pathlib import Path
import os
import pdfplumber
from abc import ABC, abstractmethod
from typing import Dict, Any
import re
from datetime import date
from groq import Groq
from dotenv import load_dotenv
import logging

#sys.path.append(str(Path().resolve()))

load_dotenv()
from src.receipt_intelligence.config import settings
from src.receipt_intelligence.modules.receipt_reader.utils import encode_image, parse_str

class ReceiptProcessor(ABC):
    """Abstract base class for receipt readers."""

    def __init__(self):
        
        self.logger = logging.getLogger(__name__)

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
        """,
            (submitted_by, filename, receipt_date, store_cod, product, quantity, price_unit, price_total, discount_ind, load_date)
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

        folder_path = settings.AH_RAW_PATH

        for file in os.listdir(folder_path):
            if file.lower().endswith(".pdf"):
                file_path = os.path.join(folder_path, file)
                text = self.read_receipt(file_path)
                self.parse_receipt(file, text)
                self.logger.info(f"Finished writing to database filename: {file_path}")

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
                
                # extract the different components from a receipt line
                match = re.match(r"(\d+)?\s*([A-Z ]+)?\s*([\d,]+)?\s*([\d,]+)?\s*([A-Z])?", line)
                if match:
                    quantity, product, price_unit, price_total, bonuscode = match.groups()
                    
                    # define variables to insert into database, transform when necessary

                    try:
                        filename = filename
                        receipt_date = re.search(r"\d{4}-\d{2}-\d{2}", filename).group()
                        store_cod = "AH"

                        quantity = int(quantity)
                        product = product.strip()
                        price_unit = float(price_unit.replace(",", "."))
                        price_total = quantity * price_unit
                        discount_ind = "J" if bonuscode == "B" else "N"

                        # write to database
                        self.insert_receiptline_into_database(filename, receipt_date, store_cod, product, quantity, price_unit, price_total, discount_ind)
                    except Exception as e:
                        self.logger.error(f"Failed to parse line: {line}. Error: {e}")

            if 'BONUS' in line:
                start_receipt = 1


class LidlReceiptProcessor(ReceiptProcessor):
    """
        Subclass to parse Lidl receipts
        Contains method to process a Lidl receipt image and write the results to database      
    """

    def process_all_receipts(self):
        """
            Process all images in a folder.
        """

        folder_path = settings.LIDL_RAW_PATH

        for file in os.listdir(folder_path):
            if file.lower().endswith(".jpeg"):
                file_path = os.path.join(folder_path, file)
                base64_image = self.read_receipt(file_path)
                self.parse_receipt(file, base64_image)
                self.logger.info(f"Finished writing to database filename: {file_path}")

        # Close connection
        self.conn.close()

    def read_receipt(self, file_path: str) -> str:
        """
            Converts image to base64
        """

        base64_image = encode_image(file_path) 

        return base64_image
    
    def parse_receipt(self, filename: str, base64_image: str) -> None:
        """
            Process a Lidl receipt base64 image and write the results to database
            The values are then written to the receiptTable in the database
        """

        # Groq and OpenAI both follow the Chat Completions API format, which is structured around a list of messages.
        """
            The structure is nested arrays and dictionaries:
            Outer array → list of messages (prompt)
            Each message → dictionary with role and content
            Content array → list of content parts (text, image, etc.)
        """
        prompt = [
            {
                "role": "system",
                "content": [
                    { "type": "text", "text": "You are a helpful assistant that extracts structured data from receipts." }
                ]
            },
            {
                "role": "user",
                "content": [
                    { 
                        "type": "text", 
                        "text": (
                            "Extract all items from this receipt and return the data in a JSON table format "
                            "with the following columns: product, quantity, price_unit, price_total, discount_amount, discount_ind. "
                            "If a field is not present, use null. "
                            "If a line represents a discount, add the value to the discount_amount of the item above and mark the discount_ind = 'J' for the item above. Do not change other values of the item above. "
                            "Do not include discount lines as separate rows. "
                            "Do not include any extra text, just return the JSON."
                        ) 
                    },
                    { "type": "image_url", "image_url": { "url": f"data:image/jpeg;base64,{base64_image}" } }
                ]
            }
        ]

        client = Groq()
        chat_completion = client.chat.completions.create(
            messages=prompt,
            model="meta-llama/llama-4-scout-17b-16e-instruct",
        )
        message_content = chat_completion.choices[0].message.content

        parsed_output = parse_str(message_content)

        for receipt_line in parsed_output:

            try:
                # define variables to insert into database
                filename = filename
                receipt_date = re.search(r"\d{4}-\d{2}-\d{2}", filename).group()
                store_cod = "LIDL"

                # transform values to database types
                quantity = (receipt_line['quantity'] or 1)
                product = receipt_line['product'].strip()
                price_unit = receipt_line['price_unit']
                price_total = quantity * price_unit
                discount_ind = (receipt_line['discount_ind'] or 'N')

                # write to database
                self.insert_receiptline_into_database(filename, receipt_date, store_cod, product, quantity, price_unit, price_total, discount_ind)
            except Exception as e:
                self.logger.error(f"Failed to parse line: {receipt_line}. Error: {e}")