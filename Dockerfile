
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY cert/ cert/
COPY src/ src/
EXPOSE 8765
CMD ["python", "src/server.py"]
