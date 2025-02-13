import os
from contextlib import contextmanager

import xstockapi


@contextmanager
def api_client():
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    api_host = os.getenv('API_HOST')

    client = xstockapi.Client(client_id, client_secret, api_host)
    try:
        yield client
    finally:
        client.close()
