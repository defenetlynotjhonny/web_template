from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security import authenticate_user, create_access_token, decode_token, get_user

router = APIRouter()

def current_user(request: Request):
    token = request.cookies.get(settings.cookie_name)
    # Also allow Authorization: Bearer <token> for API clients
    auth_header = request.headers.get("Authorization")
    if not token and auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1].strip()

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = get_user(payload["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user

@router.post("/login")
def api_login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = create_access_token(subject=user["username"])
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # set True behind HTTPS
        max_age=settings.access_token_exp_minutes * 60,
    )
    return {"message": "logged_in"}

@router.post("/logout")
def api_logout(response: Response):
    response.delete_cookie(settings.cookie_name)
    return {"message": "logged_out"}

@router.get("/me")
def me(user=Depends(current_user)):
    return {"username": user["username"], "full_name": user.get("full_name")}
