from datetime import datetime, timedelta
from typing import Annotated, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from peewee import CharField, DateTimeField, DoesNotExist

import requests
from pydantic import BaseModel

from repository.base_db import BaseDBModel, from_datetime, from_str, get_db
from repository.helpers import get_timestamp

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class LineUserInternalTokenDB(BaseDBModel):
    user_id = CharField(unique=True)
    token = CharField()
    timestamp = DateTimeField()


class LineUserInternalToken(BaseModel):
    user_id: str
    token: str
    timestamp: datetime

    @staticmethod
    def from_db(v: LineUserInternalTokenDB):
        return LineUserInternalToken(
            user_id=from_str(v.user_id),
            token=from_str(v.token),
            timestamp=from_datetime(v.timestamp),
        )

    def is_expired(
        self,
        expire_duration: timedelta = timedelta(days=1),
        allow_diff_delta: timedelta = timedelta(minutes=30),
    ) -> bool:
        time_now = get_timestamp()
        expired_ts = self.timestamp + expire_duration
        return expired_ts - time_now < allow_diff_delta


class LineUserInfo(BaseModel):
    iss: str
    sub: str
    aud: str
    exp: int
    iat: int
    amr: List[str]
    name: str
    picture: str


class AuthRepo:
    def __init__(self, client_id: str) -> None:
        self.client_id = client_id

    def verify_access_token(self, token: str):
        response = requests.get(
            f"https://api.line.me/oauth2/v2.1/verify?access_token={token}"
        )

        return response.text

    def verify_id_token(self, id_token: str):
        response = requests.post(
            "https://api.line.me/oauth2/v2.1/verify",
            data={
                "id_token": id_token,
                "client_id": self.client_id,
            },
        )
        resp_obj = response.json()
        resp_err = resp_obj.get("error")
        if resp_err is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=resp_obj
            )

        try:
            user = LineUserInfo.parse_raw(response.text)
        except Exception as e:
            print(">>> ERR verify_id_token", response.text, e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="unable to parse LineUserInfo",
            )

        if user.aud != self.client_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="aud is not client_id. you are in incorrect liff app.",
            )

        return user

    async def get_current_user(self, token: Annotated[str, Depends(oauth2_scheme)]):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"Authorization": "Bearer"},
        )
        try:
            user = self.verify_id_token(token)
        except Exception as e:
            print("failed verify line token", e)
            raise credentials_exception

        if user is None:
            raise credentials_exception

        return user

    def set_internal_token(self, user_id: str, token: str):
        token_splits = token.split("|")
        if len(token_splits) != 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="wrong token form"
            )
        timestamp = datetime.fromtimestamp(float(token_splits[1]))
        (
            LineUserInternalTokenDB.insert(
                user_id=user_id, token=token, timestamp=timestamp
            )
            .on_conflict(
                conflict_target=[LineUserInternalTokenDB.user_id],
                update={
                    LineUserInternalTokenDB.token: token,
                    LineUserInternalTokenDB.timestamp: timestamp,
                },
            )
            .execute()
        )

    def get_token(self, user_id: str) -> LineUserInternalToken | None:
        try:
            item = LineUserInternalTokenDB.get(user_id=user_id)
            return LineUserInternalToken.from_db(item)
        except DoesNotExist:
            return None


# Create table if not exists
get_db().create_tables([LineUserInternalTokenDB])
