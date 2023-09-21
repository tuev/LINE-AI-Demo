from datetime import timedelta
from repository.auth_repo import LineUserInternalToken
from repository.helpers import get_timestamp


def test_check_token_expire():
    now = get_timestamp()
    expire_duration = timedelta(days=1)
    expired_token = LineUserInternalToken(
        user_id="",
        token="",
        timestamp=(now - expire_duration),
    )
    not_expired_token = LineUserInternalToken(
        user_id="",
        token="",
        timestamp=(now - expire_duration + timedelta(minutes=12)),
    )
    assert (
        expired_token.is_expired(
            expire_duration=expire_duration,
            allow_diff_delta=timedelta(minutes=10),
        )
        is True
    )
    assert (
        not_expired_token.is_expired(
            expire_duration=expire_duration,
            allow_diff_delta=timedelta(minutes=10),
        )
        is False
    )
