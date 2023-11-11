from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Roles, Settings
from routers.admin import get_current_user
from routers.logging import create_log, Log

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from starlette import status
from starlette.responses import RedirectResponse

router = APIRouter(
    prefix="/about",
    tags=["about"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory='templates')

@router.get("/")
async def test(request: Request, db: Session = Depends(get_db)):

    user = await get_current_user(request)

    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.logs == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    log = Log(action="Info",user=user['username'],description="Viewed the about page.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("about.html", {"request": request, "logged_in_user": user, "role_state": role_state, "nav": 'settings', "settings": settings})