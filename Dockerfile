# Python resmi imajını kullan
FROM python:3.9

# Çalışma dizinini belirle
WORKDIR /app

# Bağımlılıkları yükle
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Gerekli portu aç
EXPOSE 8765

# Sunucuyu başlat
CMD ["python", "server.py"]
