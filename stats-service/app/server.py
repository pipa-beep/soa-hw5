from concurrent import futures
import grpc
import stats_pb2, stats_pb2_grpc
from .models import get_counts, get_dynamics, get_top
from google.protobuf.timestamp_pb2 import Timestamp

class StatsService(stats_pb2_grpc.StatsServiceServicer):
    def GetPostCounts(self, req, ctx):
        c = get_counts(req.post_id)
        return stats_pb2.CountResponse(views=c['views'], likes=c['likes'], comments=c['comments'])

    def GetPostDynamics(self, req, ctx):
        items = get_dynamics(req.id, 'views', req.from.ToDatetime(), req.to.ToDatetime())
        return stats_pb2.DynamicsResponse(items=[stats_pb2.DayCount(date=d['date'], count=d['count']) for d in items])

    def GetTopPosts(self, req, ctx):
        items = get_top(req.metric.name.lower(), req.limit)
        return stats_pb2.TopItemsResponse(items=[stats_pb2.TopItem(id=i['id'], value=i['value']) for i in items])

    def GetTopUsers(self, req, ctx):
        items = get_top(req.metric.name.lower(), req.limit, by_user=True)
        return stats_pb2.TopItemsResponse(items=[stats_pb2.TopItem(id=i['id'], value=i['value']) for i in items])

    # Promocode методы аналогично:
    def GetPromocodeCounts(self, req, ctx): return self.GetPostCounts(req, ctx)
    def GetPromocodeDynamics(self, req, ctx): return self.GetPostDynamics(req, ctx)
    def GetTopPromocodes(self, req, ctx): return self.GetTopPosts(req, ctx)
    def GetTopUsersByPromo(self, req, ctx): return self.GetTopUsers(req, ctx)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stats_pb2_grpc.add_StatsServiceServicer_to_server(StatsService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__': serve()
