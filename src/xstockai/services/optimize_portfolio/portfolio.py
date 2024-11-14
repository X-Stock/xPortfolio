import numpy as np
import pandas as pd

from skfolio import RiskMeasure
from skfolio.optimization import MeanRisk, ObjectiveFunction
from skfolio.preprocessing import prices_to_returns

_RISK_FREE_RATE = 0

def optimize_portfolio(historical: dict[str, pd.DataFrame]) -> dict[str, float]:
    df_list = []
    for ticker, df in historical.items():
        df = df.filter(['close'])
        df = df.rename(columns={'close': ticker})
        df_list.append(df)

    prices = df_list[0].join(df_list[1:])
    prices = prices.sort_index().dropna()

    X = prices_to_returns(prices)
    er = np.mean(X, axis=0)
    if (er <= _RISK_FREE_RATE).all():
        raise ValueError("At least one of the assets must have an expected return exceeding the risk-free rate")
    # X_train, X_test = train_test_split(X, test_size=0.33, shuffle=False)

    model = MeanRisk(
        objective_function=ObjectiveFunction.MAXIMIZE_RATIO,
        risk_measure=RiskMeasure.VARIANCE,
        risk_free_rate=_RISK_FREE_RATE
    )
    # model.fit(X_train)
    model.fit(X)

    # portfolio = model.predict(X_test)
    # print(portfolio.sharpe_ratio)

    optimized_portfolio = {ticker: weight for ticker, weight in zip(historical.keys(), model.weights_)}
    return optimized_portfolio

