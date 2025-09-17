# 🧾 Receipt Intelligence

**Receipt Intelligence** is a service that transforms supermarket receipts into structured database entries.  
It comes with a **Streamlit app** that lets you explore your receipt data through a **conversational interface**, powered by an agentic framework that generates SQL queries for you.

---

## ✨ Features

- 📸 **Receipt processing** – Convert raw receipt images into structured database entries using a multimodal model.  
- 💬 **Conversational interface** – Query your receipt data naturally through a chat-like interface.  
- 🤖 **Agentic query generation** – Built with [Langraph](https://www.langraph.com/) and [LangChain](https://www.langchain.com/) to automatically generate SQL queries.  
- ⚡ **Inference** – Powered by [Groq](https://groq.com/) for efficient model execution.  
- 🐳 **Docker support** – Easily containerize and deploy the app.  

---

## 🛠 Tech Stack

- [Streamlit](https://streamlit.io/) – Web app framework  
- [Langraph](https://www.langraph.com/) & [LangChain](https://www.langchain.com/) – Conversational AI + agentic workflows  
- [Groq](https://groq.com/) – Fast model inference  
- Python 3.10+  

---

## 🚀 Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-username/receipt-intelligence.git
cd receipt-intelligence
pip install -r requirements.txt
