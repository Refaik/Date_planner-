import os
import shutil
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.database import get_db
from database.models import DateIdea, ActiveDate, DatePhoto
from bot.bot_instance import notify_admin_about_choice, notify_admin_report

app = FastAPI(title="Date Planner WebApp")

os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index_page(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/admin")
async def admin_page(request: Request):
    return templates.TemplateResponse(request, "admin.html")


@app.get("/api/ideas")
async def get_ideas(category: str = "all", db: AsyncSession = Depends(get_db)):
    query = select(DateIdea).where(DateIdea.is_active == True)
    if category != "all":
        query = query.where(DateIdea.location_type == category)

    result = await db.execute(query)
    ideas = result.scalars().all()

    # Можно возвращать объектами (FastAPI сам их сериализует с новыми полями)
    return ideas


@app.post("/api/select-date/{idea_id}")
async def select_date(idea_id: int, db: AsyncSession = Depends(get_db)):
    idea = await db.get(DateIdea, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    active_date = ActiveDate(date_idea_id=idea.id, status='chosen')
    db.add(active_date)
    await db.commit()
    await db.refresh(active_date)

    await notify_admin_about_choice(
        idea_title=idea.title,
        description=idea.description,
        requirements=idea.requirements_text,
        requires_booking=idea.requires_booking,
        active_date_id=active_date.id
    )

    return {"status": "success", "active_date_id": active_date.id}


@app.get("/api/active-date")
async def get_active_date(db: AsyncSession = Depends(get_db)):
    query = select(ActiveDate).where(ActiveDate.status == 'chosen').order_by(ActiveDate.selected_at.desc())
    result = await db.execute(query)
    active = result.scalars().first()
    if not active:
        return {"has_active": False}

    idea = await db.get(DateIdea, active.date_idea_id)
    return {
        "has_active": True,
        "active_id": active.id,
        "title": idea.title if idea else "Свидание"
    }


@app.post("/api/complete-date")
async def complete_date(
        active_date_id: int = Form(...),
        rating: int = Form(...),
        review_text: str = Form(...),
        photos: List[UploadFile] = File(...),
        db: AsyncSession = Depends(get_db)
):
    if len(photos) < 3:
        raise HTTPException(status_code=400, detail="Нужно минимум 3 фото!")

    active_date = await db.get(ActiveDate, active_date_id)
    if not active_date:
        raise HTTPException(status_code=404, detail="Active date not found")

    active_date.rating = rating
    active_date.review_text = review_text
    active_date.status = 'completed'

    for file in photos:
        file_path = f"static/uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        photo_record = DatePhoto(active_date_id=active_date.id, photo_url=f"/{file_path}")
        db.add(photo_record)

    await db.commit()
    await notify_admin_report(rating=rating, review=review_text, photos_count=len(photos))
    return {"status": "success"}


@app.post("/api/admin/ideas")
async def add_idea(
        title: str = Form(...),
        description: str = Form(...),
        location_type: str = Form(...),
        weather_type: str = Form(...),
        requirements_text: str = Form(""),
        dress_code: Optional[str] = Form(None),  # 👈 Принимаем dress_code от админа
        requires_booking: bool = Form(False),
        photo: Optional[UploadFile] = File(None),
        db: AsyncSession = Depends(get_db)
):
    photo_url = None
    if photo and photo.filename:
        file_path = f"static/uploads/idea_{photo.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        photo_url = f"/{file_path}"

    new_idea = DateIdea(
        title=title,
        description=description,
        location_type=location_type,
        weather_type=weather_type,
        requirements_text=requirements_text,
        dress_code=dress_code,  # 👈 Сохраняем в базу данных
        requires_booking=requires_booking,
        photo_url=photo_url
    )
    db.add(new_idea)
    await db.commit()
    return {"status": "success"}