from datetime import datetime, timedelta, timezone
import json
from typing import Annotated, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from peewee import CharField, IntegerField, TextField

import requests
from pydantic import BaseModel

from repository.base_db import BaseDBModel, from_int, from_str, get_db
from repository.helpers import cprint_warn, get_timestamp

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class LineUserInfoDB(BaseDBModel):
    iss = CharField()
    sub = CharField(unique=True)
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

    def get_users(self, user_ids: List[str]):
        users_db = LineUserInfoDB.select().where(LineUserInfoDB.sub.in_(user_ids))
        return [LineUserInfo.from_db(user_db) for user_db in users_db]

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

        if user_data_db is None or user_data is None:
            user_data_jwk.to_db().save()
        else:
            # Check if the record in db is old one. If it is too old then we need to update it.
            user_data_timestamp = datetime.fromtimestamp(float(user_data.iat)).replace(
                tzinfo=timezone.utc
            )
            delta_user_issue_at_timestamp = get_timestamp() - user_data_timestamp
            if delta_user_issue_at_timestamp > timedelta(minutes=5):
                print(
                    "nanii >>",
                    user_data_db.get_id(),
                    delta_user_issue_at_timestamp,
                    user_data.iat,
                    user_data_jwk.iat,
                )
                LineUserInfoDB.set_by_id(user_data_db.get_id(), user_data_jwk.dict())

        return user_data_jwk


# Create table if not exists
get_db().create_tables([LineUserInfoDB])
