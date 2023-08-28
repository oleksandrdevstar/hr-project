from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Logs
import datetime

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from starlette import status
from starlette.responses import RedirectResponse
router = APIRouter(
    prefix="/logging",
    tags=["logging"],
)

templates = Jinja2Templates(directory='templates')

class Log(BaseModel):
    action: str = Field(...)
    description: str = Field(...)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/")
async def show_logging(request: Request, db: Session = Depends(get_db)):
    logs = db.query(Logs).order_by(Logs.id.desc()).limit(400).all()

    return templates.TemplateResponse("logging.html", {"request": request, "logs": logs})

@router.post("/create_log")
async def create_log(request: Request, log: Log, db: Session = Depends(get_db)):
    log_model = Logs()

    log_model.action = log.action
    log_model.description = log.description
    log_model.date = datetime.now()

    db.add(log_model)
    db.commit()

    return RedirectResponse(url="/logging", status_code=status.HTTP_302_FOUND)