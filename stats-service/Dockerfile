FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache -r requirements.txt

COPY app/ ./app/
WORKDIR /app/app
# Генерация Python-stubs по proto
RUN python -m grpc_tools.protoc -I proto \
    --python_out=. --grpc_python_out=. proto/stats.proto

CMD ["sh", "-c", "python consumer.py & python server.py"]
