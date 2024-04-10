from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from config import config


def team_secret(request: Request):
    param = request.query_params.get("team_secret")
    if param is None:
        return get_remote_address(request)

    return param


limiter = Limiter(key_func=team_secret, default_limits=["10000/second"],  # TODO: vrati na 3
                  storage_uri=f"redis://localhost:{config['redis']['port']}/0")
