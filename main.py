
from src.receipt_intelligence.config import settings
from src.receipt_intelligence.application.receipt_reader.receiptReader import AHReceiptProcessor


# .venv\Scripts\activate.bat
# python src/main.py


def main():

    r = AHReceiptProcessor()
    r.process_all_receipts(settings.PDF_AH_PATH)    
      
    

if __name__ == "__main__":
    main()