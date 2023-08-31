from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import requests
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class LineUserInfo(BaseModel):
    sub: str
    name: str
    picture: str


class AuthRepo:
    def verify_line_token(self, token: str) -> LineUserInfo:
        response = requests.get(
            "https://api.line.me/oauth2/v2.1/userinfo",
            headers={"Authorization": f"Bearer {token}"},
        )
        user = LineUserInfo.parse_raw(response.text)

        return user

    async def get_current_user(self, token: Annotated[str, Depends(oauth2_scheme)]):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            user = self.verify_line_token(token)
        except Exception as e:
            print("failed verify line token", e)
            raise credentials_exception

        if user is None:
            raise credentials_exception

        return user
