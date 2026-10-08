import datetime
import hashlib
import time
from functools import lru_cache

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError, PyJWKClientError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing_extensions import Annotated

from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.models.user import UserModel
from server.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(plain_password):
    return pwd_context.hash(plain_password)


_API_KEY_CACHE_TTL_SECONDS = 60
_api_key_cache: dict[str, tuple[str, float]] = {}

bearer_scheme = HTTPBearer(auto_error=False)
api_key_scheme = APIKeyHeader(name="x-api-key", auto_error=False)


def _unauthorized(detail: str = "Could not validate credentials") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


@lru_cache
def get_jwks_client() -> PyJWKClient:
    return PyJWKClient(f"{settings.better_auth_url}/api/auth/jwks", cache_keys=True)


def decode_better_auth_jwt(token: str) -> dict:
    """Verify a Better Auth JWT against the Nuxt app's JWKS and return its claims."""
    try:
        signing_key = get_jwks_client().get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA", "ES256", "RS256"],
            audience=settings.better_auth_audience,
            issuer=settings.better_auth_url,
            options={"require": ["exp", "sub"]},
        )
    except (InvalidTokenError, PyJWKClientError):
        raise _unauthorized()


async def verify_api_key(api_key: str) -> str:
    """Return the owner's user id for a valid Better Auth API key."""
    cache_key = hashlib.sha256(api_key.encode()).hexdigest()
    cached = _api_key_cache.get(cache_key)
    if cached and cached[1] > time.monotonic():
        return cached[0]

    try:
        async with httpx.AsyncClient(timeout=5) as http:
            response = await http.post(
                f"{settings.better_auth_url}/api/auth/api-key/verify",
                json={"key": api_key},
            )
        result = response.json()
    except (httpx.HTTPError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )

    if not result.get("valid") or not result.get("key"):
        raise _unauthorized("Invalid API key")

    user_id = result["key"]["referenceId"]
    _api_key_cache[cache_key] = (
        user_id,
        time.monotonic() + _API_KEY_CACHE_TTL_SECONDS,
    )
    return user_id


def _get_or_create_local_user(db: Session, user_id: str, claims: dict) -> UserModel:
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user:
        return user

    # First request from a user created in Better Auth. `password` is a
    # required unique column in the legacy schema, so store a placeholder.
    user = UserModel(
        id=user_id,
        username=claims.get("username") or user_id,
        password=f"better-auth:{user_id}",
        first_name=claims.get("first_name"),
        last_name=claims.get("last_name"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def get_current_user(
    bearer: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    api_key: Annotated[str | None, Depends(api_key_scheme)],
    db: Session = Depends(get_db),
):
    if bearer:
        claims = decode_better_auth_jwt(bearer.credentials)
        user_id = claims["sub"]
    elif api_key:
        claims = {}
        user_id = await verify_api_key(api_key)
    else:
        raise _unauthorized()

    user = _get_or_create_local_user(db, user_id, claims)

    return UserDetailsBaseModel(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        disabled=user.disabled,
    )


async def get_current_active_user(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=15
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.server_access_secret_key,
        algorithm=settings.server_access_algorithm,
    )
    return encoded_jwt


# def create_refresh_token(data: dict, expires_delta: datetime.timedelta | None = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
#     else:
#         expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
#             days=7
#         )
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(
#         to_encode,
#         settings.server_refresh_secret_key,
#         algorithm=settings.server_refresh_algorithm,
#     )
#     return encoded_jwt
