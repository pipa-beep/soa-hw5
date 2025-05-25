FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache -r requirements.txt
COPY app/ ./app/
WORKDIR /app/app
RUN python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. stats.proto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
