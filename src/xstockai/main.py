from concurrent import futures

import grpc

from xstockai.grpc_proto.optimze_portfolio import optimizePortfolio_pb2_grpc
from xstockai.services.optimize_portfolio.servicer import OptimizePortfolioServicer
from xstockai.utils import logger


def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    optimizePortfolio_pb2_grpc.add_OptimizePortfolioServicer_to_server(OptimizePortfolioServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info(f"gRPC server started, listening on port {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
