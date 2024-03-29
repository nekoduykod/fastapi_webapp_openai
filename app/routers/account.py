from fastapi import Request, Form, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import db

from passlib.context import CryptContext

from app.models.models import Users as ModelUsers


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get('/account', response_class=HTMLResponse)
async def account_page(request: Request):
    user = request.session.get("user")
    if user:
       return templates.TemplateResponse("account.html", 
                                        {"request": request,
                                            "user": user, 
                                           "error": None})
    else:
       return templates.TemplateResponse("account.html",
                                        {"request": request,
                                            "user": None, 
                                           "error": "You are not logged in"})


@router.post('/account', response_class=HTMLResponse)
async def change_pass(request: Request,
                      current_password: str = Form(...),
                      new_password: str = Form(...),
                      confirm_password: str = Form(...)):
    username = request.session.get("user")["username"]

    existing_user = db.session.query(ModelUsers) \
                              .filter(ModelUsers.username == username).first()

    if not existing_user or not pwd_context.verify(current_password, existing_user.hashed_password):
        return templates.TemplateResponse("account.html",
                                    {"request": request,
                                        "user": {"username": username},
                                       "error": "Incorrect current password"})
    if new_password != confirm_password:
        return templates.TemplateResponse("account.html",
                                    {"request": request,
                                        "user": {"username": username},
                                       "error": "New and confirm password do not match"})
    existing_user.set_password(new_password)
    db.session.commit()
    return templates.TemplateResponse("account.html",
                                {"request": request,
                                    "user": {"username": username},
                                 "success": "Password changed successfully"})
