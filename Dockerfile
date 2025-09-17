

FROM python

WORKDIR /app

COPY requirements.txt .

# Install Python deps
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# If your app listens on 8000 (adjust if different)
EXPOSE 8501

# Default command (change to your entrypoint)
CMD ["python", "main.py"]