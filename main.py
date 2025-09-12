
import logging
import subprocess

import src.receipt_intelligence.infrastructure.init_db as init_db
from src.receipt_intelligence.modules.receipt_reader.receiptReader import AHReceiptProcessor, LidlReceiptProcessor

from src.receipt_intelligence.interface.streamlit import app

# .venv\Scripts\activate.bat
# python main.py


def main():


    logging.basicConfig(level=logging.INFO)
    init_db.init_db()

    rpAH = AHReceiptProcessor()
    rpAH.process_all_receipts()    

    rpLidl = LidlReceiptProcessor() 
    rpLidl.process_all_receipts() 
   
    # Start Streamlit
    subprocess.run(["streamlit", "run", "src/receipt_intelligence/interface/streamlit/app.py"])


if __name__ == "__main__":
    main()