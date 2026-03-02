# 使用輕量級的 Python 3.11 基礎映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 先複製 requirements.txt 並安裝依賴，利用 Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式與資料檔案
# 注意：data.csv 會被包進 image 中 (約 300MB)
COPY main.py .
COPY data.csv .

# 開放 FastAPI 預設通訊埠
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "main.py:app", "--host", "0.0.0.0", "--port", "8000"]
