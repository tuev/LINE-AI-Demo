from datetime import datetime, timedelta, timezone
import json
from typing import Annotated, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from peewee import CharField, DateTimeField, DoesNotExist, IntegerField, TextField

import requests
from pydantic import BaseModel

from repository.base_db import BaseDBModel, from_datetime, from_int, from_str, get_db
from repository.helpers import cprint_warn, get_timestamp

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


def check_token_expired(token: LineUserInternalToken | None) -> LineUserInternalToken:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="internal token not found",
        )

    if token.is_expired():
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="unable to proceed because the internal token is about to expire.",
        )

    return token


class LineUserInfoDB(BaseDBModel):
    iss = CharField()
    sub = CharField()
    aud = CharField()
    exp = IntegerField()
    iat = IntegerField()
    amr = TextField()
    name = CharField()
    picture = CharField()


class LineUserInfo(BaseModel):
    iss: str
    sub: str
    aud: str
    exp: int
    iat: int
    amr: List[str]
    name: str
    picture: str

    def to_db(self) -> LineUserInfoDB:
        return LineUserInfoDB(
            iss=self.iss,
            sub=self.sub,
            aud=self.aud,
            exp=self.exp,
            iat=self.iat,
            amr=json.dumps(self.amr),
            name=self.name,
            picture=self.picture,
        )

    @staticmethod
    def from_db(db_model: LineUserInfoDB):
        return LineUserInfo(
            iss=from_str(db_model.iss),
            sub=from_str(db_model.sub),
            aud=from_str(db_model.aud),
            exp=from_int(db_model.exp),
            iat=from_int(db_model.iat),
            amr=from_str(db_model.amr).split(","),
            name=from_str(db_model.name),
            picture=from_str(db_model.picture),
        )


class AuthRepo:
    def __init__(self, client_id: str) -> None:
        self.client_id = client_id

    def verify_access_token(self, token: str):
        response = requests.get(
            f"https://api.line.me/oauth2/v2.1/verify?access_token={token}"
        )

        return response.text

    def verify_id_token(self, id_token: str):
        try:
            response = requests.post(
                "https://api.line.me/oauth2/v2.1/verify",
                data={
                    "id_token": id_token,
                    "client_id": self.client_id,
                },
            )

        except Exception as e:
            print(">>> ERR connect to auth server", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="unable to connect to auth server",
            )

        resp_obj = response.json()
        resp_err = resp_obj.get("error")
        if resp_err is not None:
            cprint_warn(f"unauthorized {str(resp_obj)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="cannot verify id_token",
            )

        try:
            user = LineUserInfo.parse_obj(resp_obj)

        except Exception as e:
            print(">>> ERR parsing LineUserInfo", e)
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

    async def get_current_user(
        self, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> LineUserInfo:
        user_data_jwk = self.verify_id_token(token)
        user_data_db = LineUserInfoDB.get_or_none(
            LineUserInfoDB.sub == user_data_jwk.sub
        )
        user_data = (
            LineUserInfo.from_db(user_data_db) if user_data_db is not None else None
        )

        if user_data is None:
            user_data_jwk.to_db().save()
        else:
            time_now = get_timestamp()
            user_data_timestamp = datetime.fromtimestamp(float(user_data.iat)).replace(
                tzinfo=timezone.utc
            )
            if time_now - user_data_timestamp > timedelta(minutes=5):
                user_data_jwk.to_db().save()

        return user_data_jwk

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
get_db().create_tables([LineUserInternalTokenDB, LineUserInfoDB])
