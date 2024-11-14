import warnings

from xstockai.grpc_proto.optimze_portfolio import optimizePortfolio_pb2_grpc, optimizePortfolio_pb2
from xstockai.utils import logger
from .portfolio import optimize_portfolio
from ...grpc_proto.optimze_portfolio.optimizePortfolio_pb2 import OptimizedPortfolioRequest
from ...utils.preprocessing import preprocess_historical


class OptimizePortfolioServicer(optimizePortfolio_pb2_grpc.OptimizePortfolioServicer):
    def Optimize(self, request: OptimizedPortfolioRequest, context):
        assets = request.assets
        historical = preprocess_historical(list(assets))

        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                portfolio_weights = optimize_portfolio(historical)

            optimized_portfolio = [optimizePortfolio_pb2.WeightedAsset(ticker=ticker, weight=weight)
                                   for ticker, weight in portfolio_weights.items()]
        except ValueError as e:
            logger.info(e)
            optimized_portfolio = [optimizePortfolio_pb2.WeightedAsset(ticker=asset.ticker, weight=0.0) for asset in assets]

        return optimizePortfolio_pb2.OptimizedPortfolioResponse(portfolio=optimized_portfolio)
