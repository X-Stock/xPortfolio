import os
from contextlib import contextmanager

import xstockapi


@contextmanager
def api_client():
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    api_endpoint = os.getenv('API_ENDPOINT')

    client = xstockapi.Client(client_id, client_secret, api_endpoint)
    try:
        yield client
    finally:
        client.close()
