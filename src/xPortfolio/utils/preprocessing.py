import pandas as pd
from google.protobuf.json_format import MessageToDict

from xPortfolio.proto.optimizePortfolio_pb2 import Asset


def preprocess_historical(assets: list[Asset]) -> dict[str, pd.DataFrame]:
    historical = {}
    for asset in assets:
        df = pd.DataFrame([MessageToDict(data) for data in asset.historical])
        df.index = pd.to_datetime(df['time'])
        df = df.drop('time', axis=1)
        historical[asset.ticker] = df

    return historical