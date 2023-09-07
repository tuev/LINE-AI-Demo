from datetime import datetime, timezone
from typing import Annotated, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from peewee import CharField, DateTimeField, IntegerField

import requests
from pydantic import BaseModel

from repository.base_db import BaseDBModel, get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class LineUserInternalToken(BaseDBModel):
    user_id = CharField(unique=True)
    token = CharField()
    timestamp = DateTimeField()


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
            LineUserInternalToken.insert(
                user_id=user_id, token=token, timestamp=timestamp
            )
            .on_conflict(
                conflict_target=[LineUserInternalToken.user_id],
                update={
                    LineUserInternalToken.token: token,
                    LineUserInternalToken.timestamp: timestamp,
                },
            )
            .execute()
        )

    def get_token_timestamp(self, user_id):
        item = LineUserInternalToken.get(user_id=user_id)
        return item.timestamp.replace(tzinfo=timezone.utc)

    def get_token(self, user_id):
        item = LineUserInternalToken.get(user_id=user_id)
        return item.token


# Create table if not exists
get_db().create_tables([LineUserInternalToken])
