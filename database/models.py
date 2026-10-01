from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DateIdea(Base):
    __tablename__ = "date_ideas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    location_type = Column(String(50), default="home")     # home / outside
    time_type = Column(String(50), default="any")          # day / night / any
    activity_type = Column(String(50), default="any")      # relax / active / food / any
    weather_type = Column(String(50), default="any")
    requirements_text = Column(Text, default="")
    dress_code = Column(String(255), default="")
    requires_booking = Column(Boolean, default=False)
    photo_url = Column(String(500), default="")
    place_link = Column(String(500), default="")
    is_active = Column(Boolean, default=True)

class ActiveDate(Base):
    __tablename__ = "active_dates"

    id = Column(Integer, primary_key=True, index=True)
    date_idea_id = Column(Integer, nullable=False)
    selected_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="chosen")          # chosen / completed
    rating = Column(Integer, nullable=True)
    review_text = Column(Text, nullable=True)
    photos = Column(JSON, default=list)                    # list of photo URLs