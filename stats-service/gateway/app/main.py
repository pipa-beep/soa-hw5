from fastapi import FastAPI, HTTPException
import grpc
import stats_pb2, stats_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, timedelta

app = FastAPI()
channel = grpc.insecure_channel('stats-service:50051')
client = stats_pb2_grpc.StatsServiceStub(channel)

@app.get('/posts/{post_id}/counts')
async def post_counts(post_id: str):
    resp = client.GetPostCounts(stats_pb2.PostRequest(post_id=post_id))
    return resp

@app.get('/posts/{post_id}/dynamics/{metric}')
async def post_dynamics(post_id: str, metric: str, days: int = 7):
    to = datetime.utcnow()
    frm = to - timedelta(days=days)
    tr = Timestamp(); tr.FromDatetime(to)
    fr = Timestamp(); fr.FromDatetime(frm)
    req = stats_pb2.DynamicsRequest(id=post_id, from=fr, to=tr)
    resp = client.GetPostDynamics(req) if metric=='views' else (
        client.GetPromocodeDynamics(req)  # reuse
    )
    return resp.items

@app.get('/top/posts')
async def top_posts(metric: str, limit: int = 10):
    m = stats_pb2.Metric.Value(metric.upper())
    resp = client.GetTopPosts(stats_pb2.TopRequest(metric=m, limit=limit))
    return resp.items

@app.get('/top/users')
async def top_users(metric: str, limit: int = 10):
    m = stats_pb2.Metric.Value(metric.upper())
    resp = client.GetTopUsers(stats_pb2.TopRequest(metric=m, limit=limit))
    return resp.items

# Промокоды аналогично:
@app.get('/promocodes/{promo_id}/counts')
async def promo_counts(promo_id: str):
    resp = client.GetPromocodeCounts(stats_pb2.PromoRequest(promo_id=promo_id))
    return resp

@app.get('/top/promocodes')
async def top_promos(metric: str, limit: int = 10):
    m = stats_pb2.Metric.Value(metric.upper())
    resp = client.GetTopPromocodes(stats_pb2.TopRequest(metric=m, limit=limit))
    return resp.items

@app.get('/top/users/promo')
async def top_users_promo(metric: str, limit: int = 10):
    m = stats_pb2.Metric.Value(metric.upper())
    resp = client.GetTopUsersByPromo(stats_pb2.TopRequest(metric=m, limit=limit))
    return resp.items
