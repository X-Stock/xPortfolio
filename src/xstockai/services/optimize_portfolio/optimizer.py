import numpy as np
import pandas as pd

from skfolio import RiskMeasure
from skfolio.optimization import MeanRisk, ObjectiveFunction
from skfolio.preprocessing import prices_to_returns

_RISK_FREE_RATE = 0


def _calculate_capital(prices: np.ndarray, total_capital: int, weighs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    capitals = weighs * total_capital
    shares = (((capitals // prices) // 100) * 100).astype(np.uint)
    rounded_capitals = (shares * prices).astype(np.uint)
    return rounded_capitals, shares


def optimize_portfolio(historical: dict[str, pd.DataFrame], objective: str, total_capital: int) -> dict:
    df_list = []
    for ticker, df in historical.items():
        df = df.filter(['close'])
        df = df.rename(columns={'close': ticker})
        df_list.append(df)

    prices = df_list[0].join(df_list[1:])
    prices = prices.sort_index().dropna()

    X = prices_to_returns(prices)
    expected_returns = np.mean(X, axis=0)
    if (expected_returns <= _RISK_FREE_RATE).all():
        raise ValueError("At least one of the assets must have an expected return exceeding the risk-free rate")
    # X_train, X_test = train_test_split(X, test_size=0.33, shuffle=False)

    match objective:
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
    capitals, total_shares = _calculate_capital(prices.iloc[-1], total_capital, weights)
    remaining_capital = total_capital - capitals.sum()

    optimized_portfolio = {
        'assets': [
            {
                'ticker': ticker,
                'weight': weight,
                'capital': capital,
                'shares': shares
            }
            for ticker, weight, shares, capital in zip(historical.keys(), weights, total_shares, capitals)
        ],
        'expected_returns': portfolio.cumulative_returns[-1],
        'risk': portfolio.variance,
        'remaining_capital': remaining_capital
    }

    return optimized_portfolio
