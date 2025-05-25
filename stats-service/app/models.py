from clickhouse_driver import Client

# Подключаемся к ClickHouse
client = Client(host='clickhouse')

# Создаем таблицу событий, если не существует
client.execute("""
CREATE TABLE IF NOT EXISTS events (
    id String,
    user_id String,
    metric String,
    ts DateTime
) ENGINE = ReplacingMergeTree(ts)
PARTITION BY toDate(ts)
ORDER BY (id, ts)
""")

# Вставка события

def insert_event(id: str, user_id: str, metric: str, ts):
    client.execute(
        'INSERT INTO events (id, user_id, metric, ts) VALUES',
        [{'id': id, 'user_id': user_id, 'metric': metric, 'ts': ts}]
    )

# Получение суммарных счетчиков по id (post_id или promo_id)

def get_counts(id: str) -> dict:
    sql = 'SELECT metric, count() FROM events WHERE id = %(id)s GROUP BY metric'
    rows = client.execute(sql, {'id': id})
    res = {'views': 0, 'likes': 0, 'comments': 0, 'clicks': 0}
    for metric, cnt in rows:
        res[metric] = cnt
    return res

# Получение динамики по дням для заданного metric

def get_dynamics(id: str, metric: str, from_date, to_date) -> list:
    sql = """
SELECT toDate(ts) AS date, count() AS cnt
FROM events
WHERE id = %(id)s AND metric = %(metric)s AND ts BETWEEN %(from)s AND %(to)s
GROUP BY date
ORDER BY date
"""
    rows = client.execute(sql, {'id': id, 'metric': metric, 'from': from_date, 'to': to_date})
    return [{'date': str(r[0]), 'count': r[1]} for r in rows]

# Получение топовых id или user_id по metric

def get_top(metric: str, limit: int, by_user: bool = False) -> list:
    field = 'user_id' if by_user else 'id'
    sql = f"SELECT {field}, count() FROM events WHERE metric = %(metric)s GROUP BY {field} ORDER BY count() DESC LIMIT %(limit)s"
    rows = client.execute(sql, {'metric': metric, 'limit': limit})
    return [{'id': r[0], 'value': r[1]} for r in rows]
