import pandas as pd
import torch
from rlportfolio.algorithm import EpisodicPolicyGradient
from rlportfolio.data import GroupByScaler
from rlportfolio.environment import PortfolioOptimizationEnv

from xPortfolio.utils import api_client

_DEVICE = 'cuda:0' if torch.cuda.is_available() else 'cpu'
_TIME_WINDOW = 14


def eiee_optimizer(portfolio_request: dict):
    tickers = portfolio_request['tickers']
    tickers.sort()

    with api_client() as client:
        historical = client.get_intersected_historical(tickers, portfolio_request['fromDate'],
                                                       portfolio_request['toDate'])

    df = pd.concat(historical)
    df_portfolio = df[["time", "ticker", "close", "high", "low"]]
    df_portfolio = GroupByScaler(columns=["close", "high", "low"], by="ticker").fit_transform(df_portfolio)

    environment = PortfolioOptimizationEnv(
        df_portfolio,
        initial_amount=portfolio_request['capital'],
        state_normalization="by_last_close",
        comission_fee_pct=0.0025,
        time_window=_TIME_WINDOW,
        tic_column='ticker',
        time_column='time',
        features=["close", "high", "low"],
        print_metrics=False,
        plot_graphs=False,
        # comission_fee_model="trf_approx"
    )

    model = EpisodicPolicyGradient(
        environment,
        policy_kwargs={"time_window": _TIME_WINDOW},
        sample_bias=0.001,
        batch_size=200,
        lr=5e-5,
        action_noise="dirichlet",
        action_epsilon=0.2,
        action_alpha=0.01,
        device=_DEVICE
    )
    
    model.target_train_policy.load_state_dict(torch.load('model/policy_BR.pt', torch.device(_DEVICE), weights_only=True))
    result = model.test(environment)

    weight = pd.DataFrame(data=environment._final_weights, columns=['cash'] + tickers)

    optimized_portfolio = {
        'assets': [
            {
                'ticker': ticker,
                'weight': weight[ticker],
            }
            for ticker in tickers
        ],
        'expectedReturns': result['fapv'],
        'risk': result['mdd'],
        'sharpeRatio': result['sharpe_ratio']
    }
    return optimized_portfolio
