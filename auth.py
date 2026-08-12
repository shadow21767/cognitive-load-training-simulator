import hmac

from config import researcher_password, researcher_username


def valid_credentials(username: str, password: str) -> bool:
    return (
        hmac.compare_digest(username, researcher_username())
        and hmac.compare_digest(password, researcher_password())
    )
