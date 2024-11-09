import warnings

import pandas as pd
from google.protobuf.json_format import MessageToDict

from .portfolio import optimize_portfolio
from xstockai.grpc_proto.optimze_portfolio import optimizePortfolio_pb2_grpc, optimizePortfolio_pb2
from xstockai.utils import logger


class OptimizePortfolioServicer(optimizePortfolio_pb2_grpc.OptimizePortfolioServicer):
    def Optimize(self, request, context):
        assets = request.assets

        dfs = []
        tickers = []
        for asset in assets:
            tickers.append(asset.ticker)
            df = pd.DataFrame([MessageToDict(data) for data in asset.historical])
            df.index = pd.to_datetime(df['time'])
            df = df.drop('time', axis=1)
            dfs.append(df)

        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                portfolio_weights = optimize_portfolio(tickers, dfs)

            optimized_portfolio = [optimizePortfolio_pb2.WeightedAsset(ticker=ticker, weight=portfolio_weights[ticker])
                                   for ticker in tickers]
        except ValueError as e:
            logger.info(e)
            optimized_portfolio = [optimizePortfolio_pb2.WeightedAsset(ticker=ticker, weight=0.0) for ticker in tickers]

        return optimizePortfolio_pb2.OptimizedPortfolioResponse(portfolio=optimized_portfolio)
