import os
import uuid
import aiofiles
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from database.database import get_db, init_db
from database.models import DateIdea, ActiveDate
from bot.bot_instance import notify_admin_date_chosen, notify_admin_date_completed

app = FastAPI(title="Date Planner WebApp")

os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def on_startup():
    await init_db()


# Отдача HTML страниц через FileResponse без ошибок Jinja2
@app.get("/", response_class=FileResponse)
async def get_index():
    return FileResponse("templates/index.html")


@app.get("/admin", response_class=FileResponse)
async def get_admin():
    return FileResponse("templates/admin.html")


# API получения свиданий с фильтрами
@app.get("/api/ideas")
async def get_ideas(
        location: str = "all",
        time: str = "any",
        activity: str = "any",
        category: str = None,
        db: AsyncSession = Depends(get_db)
):
    loc = category if category else location
    query = select(DateIdea).where(DateIdea.is_active == True)

    if loc and loc != "all":
        query = query.where(DateIdea.location_type == loc)
    if time and time != "any":
        query = query.where((DateIdea.time_type == "any") | (DateIdea.time_type == time) | (DateIdea.time_type == None))
    if activity and activity != "any":
        query = query.where(
            (DateIdea.activity_type == "any") | (DateIdea.activity_type == activity) | (DateIdea.activity_type == None))

    result = await db.execute(query)
    ideas = result.scalars().all()
    return ideas


# Выбор свидания девушкой
@app.post("/api/select-date/{idea_id}")
async def select_date(idea_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DateIdea).where(DateIdea.id == idea_id))
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    active_date = ActiveDate(
        date_idea_id=idea.id,
        status="chosen"
    )
    db.add(active_date)
    await db.commit()
    await db.refresh(active_date)

    await notify_admin_date_chosen(
        idea_title=idea.title,
        description=idea.description,
        requirements=idea.requirements_text,
        requires_booking=idea.requires_booking,
        active_date_id=active_date.id,
        place_link=idea.place_link,
        dress_code=idea.dress_code
    )

    return {"status": "success", "active_date_id": active_date.id, "active_id": active_date.id}


# Проверка активного выбранного свидания
@app.get("/api/active-date")
async def get_active_date(db: AsyncSession = Depends(get_db)):
    query = select(ActiveDate).where(ActiveDate.status == "chosen").order_by(desc(ActiveDate.id))
    result = await db.execute(query)
    active = result.scalars().first()
    if not active:
        return {"has_active": False}

    idea_res = await db.execute(select(DateIdea).where(DateIdea.id == active.date_idea_id))
    idea = idea_res.scalar_one_or_none()
    return {
        "has_active": True,
        "active_id": active.id,
        "active_date_id": active.id,
        "title": idea.title if idea else "Свидание"
    }


# Сдача отчета о свидании и фоток
@app.post("/api/complete-date")
async def complete_date(
        active_date_id: int = Form(...),
        rating: int = Form(5),
        review_text: str = Form(""),
        photos: list[UploadFile] = File(...),
        db: AsyncSession = Depends(get_db)
):
    if len(photos) < 3:
        raise HTTPException(status_code=400, detail="Нужно минимум 3 фото!")

    result = await db.execute(select(ActiveDate).where(ActiveDate.id == active_date_id))
    active = result.scalar_one_or_none()
    if not active:
        raise HTTPException(status_code=404, detail="Active date not found")

    saved_photo_urls = []
    for file in photos:
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        unique_name = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join("static/uploads", unique_name)
        async with aiofiles.open(filepath, "wb") as f:
            content = await file.read()
            await f.write(content)
        saved_photo_urls.append(f"/static/uploads/{unique_name}")

    active.rating = rating
    active.review_text = review_text
    active.status = "completed"
    active.photos = saved_photo_urls
    await db.commit()

    await notify_admin_date_completed(
        rating=rating,
        review=review_text,
        photos_count=len(photos)
    )

    return {"status": "success"}


# Получение истории для альбома воспоминаний
@app.get("/api/history")
async def get_history(db: AsyncSession = Depends(get_db)):
    query = select(ActiveDate).where(ActiveDate.status == "completed").order_by(desc(ActiveDate.id))
    result = await db.execute(query)
    completed_dates = result.scalars().all()

    memories = []
    for d in completed_dates:
        idea_res = await db.execute(select(DateIdea).where(DateIdea.id == d.date_idea_id))
        idea = idea_res.scalar_one_or_none()
        memories.append({
            "id": d.id,
            "title": idea.title if idea else "Романтическое свидание",
            "description": idea.description if idea else "",
            "location_type": idea.location_type if idea else "home",
            "selected_at": d.selected_at.isoformat() if d.selected_at else "",
            "rating": d.rating,
            "review_text": d.review_text,
            "photos": d.photos or []
        })

    return memories


# Добавление нового свидания через панель парня
@app.post("/api/admin/ideas")
async def admin_add_idea(
        title: str = Form(...),
        description: str = Form(...),
        location_type: str = Form("home"),
        weather_type: str = Form("any"),
        time_type: str = Form("any"),
        activity_type: str = Form("food"),
        requirements_text: str = Form(""),
        dress_code: str = Form(""),
        requires_booking: bool = Form(False),
        place_link: str = Form(""),
        photo: UploadFile = File(None),
        db: AsyncSession = Depends(get_db)
):
    photo_url = "https://images.unsplash.com/photo-1518199266791-5375a83190b7?w=500"
    if photo and photo.filename:
        ext = os.path.splitext(photo.filename)[1] or ".jpg"
        unique_name = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join("static/uploads", unique_name)
        async with aiofiles.open(filepath, "wb") as f:
            content = await photo.read()
            await f.write(content)
        photo_url = f"/static/uploads/{unique_name}"

    new_idea = DateIdea(
        title=title,
        description=description,
        location_type=location_type,
        weather_type=weather_type,
        time_type=time_type,
        activity_type=activity_type,
        requirements_text=requirements_text,
        dress_code=dress_code,
        requires_booking=requires_booking,
        place_link=place_link,
        photo_url=photo_url,
        is_active=True
    )
    db.add(new_idea)
    await db.commit()
    await db.refresh(new_idea)
    return {"status": "success", "idea_id": new_idea.id}