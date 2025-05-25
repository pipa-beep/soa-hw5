import asyncio
from aiokafka import AIOKafkaConsumer
from .models import insert_event
import json

# Парсинг события из Kafka

def parse_event(record):
    data = json.loads(record.value)
    return data['id'], data['user_id'], data['metric'], data['ts']

# Асинхронный консьюмер
async def consume():
    consumer = AIOKafkaConsumer(
        'posts.events', 'promocodes.events',
        bootstrap_servers='kafka:9092', group_id='stats_group'
    )
    await consumer.start()
    try:
        async for msg in consumer:
            id, user_id, metric, ts = parse_event(msg)
            insert_event(id, user_id, metric, ts)
    finally:
        await consumer.stop()

# Точка входа
if __name__ == '__main__':
    asyncio.run(consume())
