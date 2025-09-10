
import src.receipt_intelligence.infrastructure.init_db as init_db

from src.receipt_intelligence.config import settings
from src.receipt_intelligence.application.receipt_reader.receiptReader import AHReceiptProcessor, LidlReceiptProcessor


# .venv\Scripts\activate.bat
# python src/main.py


def main():

    init_db.init_db()

    r = AHReceiptProcessor()
    r.process_all_receipts()    

    #r = LidlReceiptProcessor() 
      
    

if __name__ == "__main__":
    main()