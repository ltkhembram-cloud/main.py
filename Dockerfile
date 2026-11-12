FROM python:3.11-slim

WORKDIR /app

# সিস্টেম ডিপেন্ডেন্সি আপডেট
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# লাইব্রেরি ইনস্টল
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# বটের পাইথন ফাইল কপি করা
COPY bot.py .

# বট রান করার কমান্ড
CMD ["python", "bot.py"]
