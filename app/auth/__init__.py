"""Google OpenID Connect authentication.

Every request must carry a Google-issued ID token as `Authorization: Bearer <token>`.
The token is verified cryptographically (signature, audience, issuer, expiry) against
Google's public certificates; the resulting identity is attached to `request.state.user`.
"""
import logging
import os
import time
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests as google_transport
from google.oauth2 import id_token as google_id_token
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

CLOCK_SKEW_SECONDS = 10
CHALLENGE = {"WWW-Authenticate": 'Bearer realm="personal-wallet", charset="UTF-8"'}
# Paths reachable without authentication: liveness, self-documentation and the OpenAPI schema.
PUBLIC_PATHS = frozenset({"/health", "/help", "/docs", "/redoc", "/openapi.json"})


class AuthenticatedUser(BaseModel):
    """Caller identity as asserted by a verified Google ID token."""
    sub: str
    email: str
    name: str | None = None
    picture: str | None = None


class AuthError(Exception):
    """Raised when a request cannot be authenticated. Always surfaces as 401."""


_transport = google_transport.Request()
# Verified tokens keyed by the raw token, valued as (expiry epoch seconds, user). A browser
# session reuses the same ID token for many calls, so this avoids re-fetching Google's certs.
_verified: dict[str, tuple[float, AuthenticatedUser]] = {}


def get_client_id() -> str:
    """Returns the Google OAuth 2.0 client ID the ID tokens must be issued for."""
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    if not client_id:
        raise RuntimeError("GOOGLE_CLIENT_ID is not set; Google ID tokens cannot be verified.")
    return client_id


def verify_id_token(token: str) -> AuthenticatedUser:
    """Verifies a Google ID token and returns the caller identity.

    Raises:
        AuthError: if the signature, audience, issuer or expiry is invalid, or the
            account has no verified email address.
    """
    now = time.time()
    cached = _verified.get(token)
    if cached and cached[0] > now + CLOCK_SKEW_SECONDS:
        return cached[1]

    try:
        claims = google_id_token.verify_oauth2_token(
            token, _transport, audience=get_client_id(), clock_skew_in_seconds=CLOCK_SKEW_SECONDS
        )
    except (GoogleAuthError, ValueError) as error:
        raise AuthError(f"Invalid Google ID token: {error}") from error

    if not claims.get("email") or not claims.get("email_verified"):
        raise AuthError("The Google account has no verified email address.")

    user = AuthenticatedUser(
        sub=claims["sub"],
        email=claims["email"],
        name=claims.get("name"),
        picture=claims.get("picture"),
    )
    for expired in [key for key, (expiry, _) in _verified.items() if expiry <= now]:
        del _verified[expired]
    _verified[token] = (float(claims["exp"]), user)
    return user


def _bearer_token(request: Request) -> str:
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise AuthError("Missing or malformed Authorization header; expected 'Bearer <Google ID token>'.")
    return token.strip()


class GoogleAuthMiddleware(BaseHTTPMiddleware):
    """Rejects with 401 every request that does not carry a valid Google ID token."""

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS" or request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        try:
            # Token verification may hit the network, so keep it off the event loop.
            request.state.user = await run_in_threadpool(verify_id_token, _bearer_token(request))
        except AuthError as error:
            logger.warning("Rejected unauthenticated %s %s: %s", request.method, request.url.path, error)
            return JSONResponse({"detail": str(error)}, status_code=401, headers=CHALLENGE)

        return await call_next(request)


def current_user(request: Request) -> AuthenticatedUser:
    """FastAPI dependency exposing the user authenticated by `GoogleAuthMiddleware`."""
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated.", headers=CHALLENGE)
    return user


CurrentUser = Annotated[AuthenticatedUser, Depends(current_user)]
