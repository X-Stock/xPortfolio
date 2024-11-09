from typing import OrderedDict

from pandas import DataFrame
from pypfopt import expected_returns, risk_models, EfficientFrontier


def optimize_portfolio(tickers: list[str], portfolio: list[DataFrame]) -> OrderedDict[str, float]:
    dfs = []
    for ticker, df in zip(tickers, portfolio):
        df = df.filter(['close'])
        df.rename(columns={'close': ticker}, inplace=True)
        dfs.append(df)

    cb_df = dfs[0].join(dfs[1:])
    cb_df = cb_df.sort_index().dropna()

    # Calculate expected returns and sample covariance
    mu = expected_returns.mean_historical_return(cb_df)
    S = risk_models.sample_cov(cb_df)

    # Optimize for maximal Sharpe ratio
    ef = EfficientFrontier(mu, S)
    raw_weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights(rounding=2)

    # ef.save_weights_to_file("weights.csv")  # saves to file
    # ef.portfolio_performance(verbose=True)

    return cleaned_weights
