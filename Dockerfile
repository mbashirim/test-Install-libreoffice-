FROM python:3.11-slim

# نصب LibreOffice
RUN apt-get update && \
    apt-get install -y libreoffice && \
    apt-get clean

# ایجاد یک اسکریپت ساده برای تست
WORKDIR /app
COPY test.py .

CMD ["python", "test.py"]
