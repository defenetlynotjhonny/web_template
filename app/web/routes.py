from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.security import authenticate_user, create_access_token, decode_token, get_user

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

def get_page_user(request: Request):
    token = request.cookies.get(settings.cookie_name)
    if not token:
        return None
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        return None
    return get_user(payload["sub"])

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    user = get_page_user(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    user = get_page_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    user = authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"}, status_code=400)

    token = create_access_token(subject=user["username"])
    resp = RedirectResponse(url="/dashboard", status_code=303)
    resp.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # set True behind HTTPS
        max_age=settings.access_token_exp_minutes * 60,
    )
    return resp

@router.post("/logout")
def logout_post():
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie(settings.cookie_name)
    return resp

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = get_page_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})
