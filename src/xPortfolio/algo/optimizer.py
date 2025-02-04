import numpy as np
from skfolio import RiskMeasure
from skfolio.optimization import MeanRisk, ObjectiveFunction
from skfolio.preprocessing import prices_to_returns

from xPortfolio.utils import api_client

_RISK_FREE_RATE = 0


def optimize_portfolio(portfolio_request: dict, ) -> dict:
    with api_client() as client:
        historical = client.get_intersected_historical(portfolio_request['tickers'])

    df_list = []
    for df in historical:
        ticker = df['ticker'].iat[0]
        df = df.filter(['close']).rename(columns={'close': ticker})
        df_list.append(df)

    prices = df_list[0].join(df_list[1:])
    prices = prices.sort_index()

    X = prices_to_returns(prices)
    expected_returns = np.mean(X, axis=0)
    if (expected_returns <= _RISK_FREE_RATE).all():
        raise ValueError("At least one of the assets must have an expected return exceeding the risk-free rate")
    # X_train, X_test = train_test_split(X, test_size=0.33, shuffle=False)

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

    # model.fit(X_train)
    model.fit(X)
    portfolio = model.predict(X)

    # portfolio = model.predict(X_test)

    weights = np.round(portfolio.weights, 2)

    optimized_portfolio = {
        'assets': [
            {
                'ticker': ticker,
                'weight': weight,
            }
            for ticker, weight in zip(portfolio_request['tickers'], weights)
        ],
        'expected_returns': portfolio.cumulative_returns[-1],
        'risk': portfolio.variance,
        'sharpe_ratio': portfolio.sharpe_ratio
    }

    return optimized_portfolio
