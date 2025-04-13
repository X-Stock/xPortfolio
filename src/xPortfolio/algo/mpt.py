import numpy as np
import pandas as pd
from skfolio import RiskMeasure
from skfolio.optimization import MeanRisk, ObjectiveFunction
from skfolio.preprocessing import prices_to_returns

from xPortfolio.utils import api_client

_RISK_FREE_RATE = 0


def mpt_optimizer(portfolio_request: dict) -> dict:
    tickers = portfolio_request['tickers']

    with api_client() as client:
        historical = client.get_intersected_historical(tickers, portfolio_request['fromDate'],
                                                       portfolio_request['toDate'])

    prices = pd.concat(
        (df[['close']]
        .rename(
            columns={'close': df['ticker'].iat[0]})
            for df in historical),
        axis=1
    ).sort_index()

    historical_returns = prices_to_returns(prices)
    expected_returns = np.mean(historical_returns, axis=0)
    if (expected_returns <= _RISK_FREE_RATE).all():
        raise ValueError("At least one of the assets must have an expected return exceeding the risk-free rate")

    match portfolio_request['objective']:
        case 'max_ratio':
            objective_function = ObjectiveFunction.MAXIMIZE_RATIO
        case 'max_return':
            objective_function = ObjectiveFunction.MAXIMIZE_RETURN
        case 'min_risk':
            objective_function = ObjectiveFunction.MINIMIZE_RISK
        case _:
            raise ValueError("Invalid portfolio optimization objective")

    model = MeanRisk(
        objective_function=objective_function,
        risk_measure=RiskMeasure.VARIANCE,
        risk_free_rate=_RISK_FREE_RATE
    )

    model.fit(historical_returns)
    portfolio = model.predict(historical_returns)
    weights = np.round(portfolio.weights, 2)

    optimized_portfolio = {
        'assets': [
            {
                'ticker': ticker,
                'weight': weight,
            }
            for ticker, weight in zip(tickers, weights)
        ],
        'expectedReturns': portfolio.cumulative_returns[-1],
        'risk': portfolio.variance,
        'sharpeRatio': portfolio.sharpe_ratio
    }

    return optimized_portfolio
