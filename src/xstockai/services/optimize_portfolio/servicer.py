from xstockai.grpc_proto.optimze_portfolio import optimizePortfolio_pb2_grpc, optimizePortfolio_pb2
from xstockai.utils import logger
from .optimizer import optimize_portfolio
from ...grpc_proto.optimze_portfolio.optimizePortfolio_pb2 import OptimizedPortfolioRequest
from ...utils.preprocessing import preprocess_historical


class OptimizePortfolioServicer(optimizePortfolio_pb2_grpc.OptimizePortfolioServicer):
    def Optimize(self, request: OptimizedPortfolioRequest, context):
        assets = request.assets
        historical = preprocess_historical(list(assets))

        try:
            result = optimize_portfolio(historical, request.objective, request.capital)

            portfolio = [
                optimizePortfolio_pb2.WeightedAsset(
                    ticker=data['ticker'],
                    weight=data['weight'],
                    shares=data['shares'],
                    capital=data['capital']
                ) for data in result['assets']
            ]
            expected_returns = result['expected_returns']
            risk = result['risk']
            remaining_capital = result['remaining_capital']

        except ValueError as e:
            logger.info(e)
            portfolio = [optimizePortfolio_pb2.WeightedAsset(ticker=asset.ticker) for asset in assets]
            expected_returns = 0
            risk = 0
            remaining_capital = request.capital

        response = optimizePortfolio_pb2.OptimizedPortfolioResponse(
            portfolio=portfolio,
            expected_returns=expected_returns,
            risk=risk,
            remaining_capital=remaining_capital
        )

        return response
