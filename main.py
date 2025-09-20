
import logging
import subprocess

import src.receipt_intelligence.infrastructure.init_db as init_db
from src.receipt_intelligence.modules.receipt_reader.receiptReader import AHReceiptProcessor, LidlReceiptProcessor

from src.receipt_intelligence.interface.streamlit import app

"""
import os
from pathlib import Path
import sys

project_root = Path().resolve() 
print(project_root)
sys.path.append(str(project_root))
"""

# .venv\Scripts\activate.bat
# python main.py or python chatbot.py
# docker build -t my-python-app:latest .
# docker run -p 8501:8501 my-python-app

def main():


    #logging.basicConfig(level=logging.INFO)
    #init_db.init_db()

    #rpAH = AHReceiptProcessor()
    #rpAH.process_all_receipts()    

    #rpLidl = LidlReceiptProcessor() 
    #rpLidl.process_all_receipts() 
   
    # Start Streamlit
    #subprocess.run(["streamlit", "run", "src/receipt_intelligence/interface/streamlit/app.py"])

    subprocess.run([
        "streamlit", "run", "src/receipt_intelligence/interface/streamlit/app.py",
        "--server.address=0.0.0.0",
        "--server.port=8501",
        "--server.enableCORS=false"
    ])

if __name__ == "__main__":
    main()