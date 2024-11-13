from concurrent import futures
from signal import signal, SIGTERM

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
    logger.info(f"gRPC Server started, listening on port {port}")

    def handle_sigterm(*_):
        logger.info("Shutting down gRPC server...")
        events = server.stop(30)
        events.wait(30)

    signal(SIGTERM, handle_sigterm)
    server.wait_for_termination()
    logger.info("gRPC Server stopped")


if __name__ == "__main__":
    serve()
