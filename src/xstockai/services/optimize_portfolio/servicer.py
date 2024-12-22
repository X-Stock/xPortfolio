from xstockai.proto.optimze_portfolio import optimizePortfolio_pb2_grpc, optimizePortfolio_pb2
from xstockai.utils import logger
from .optimizer import optimize_portfolio
from ...proto.optimze_portfolio.optimizePortfolio_pb2 import OptimizedPortfolioRequest
from ...utils.preprocessing import preprocess_historical


class OptimizePortfolioServicer(optimizePortfolio_pb2_grpc.OptimizePortfolioServicer):
    def Optimize(self, request: OptimizedPortfolioRequest, context):
        assets = request.assets
        historical = preprocess_historical(list(assets))

        try:
            result = optimize_portfolio(historical, request.objective)

            assets = [
                optimizePortfolio_pb2.WeightedAsset(
                    ticker=data['ticker'],
                    weight=data['weight'],
                ) for data in result['assets']
            ]
            expected_returns = result['expected_returns']
            risk = result['risk']
            sharpe_ratio = result['sharpe_ratio']

        except ValueError as e:
            logger.info(e)
            assets = [optimizePortfolio_pb2.WeightedAsset(ticker=asset.ticker) for asset in assets]
            expected_returns = risk = sharpe_ratio = 0

        response = optimizePortfolio_pb2.OptimizedPortfolioResponse(
            assets=assets,
            expected_returns=expected_returns,
            risk=risk,
            sharpe_ratio=sharpe_ratio
        )

        return response
