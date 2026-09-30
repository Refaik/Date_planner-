from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    role = Column(String, default='user')  # 'admin' | 'user'
    name = Column(String, nullable=True)

class DateIdea(Base):
    __tablename__ = 'date_ideas'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location_type = Column(String, default='home')  # 'home' | 'outside'
    weather_type = Column(String, default='any')   # 'sunny' | 'indoor' | 'any'
    requirements_text = Column(Text, nullable=True)
    requires_booking = Column(Boolean, default=False)
    photo_url = Column(String, nullable=True)
    dress_code = Column(String, nullable=True)  # 👈 Добавлено поле для одежды
    is_active = Column(Boolean, default=True)

class ActiveDate(Base):
    __tablename__ = 'active_dates'

    id = Column(Integer, primary_key=True, index=True)
    date_idea_id = Column(Integer, ForeignKey('date_ideas.id'), nullable=False)
    selected_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default='chosen')  # 'chosen' | 'completed' | 'failed'
    rating = Column(Integer, nullable=True)
    review_text = Column(Text, nullable=True)

    date_idea = relationship("DateIdea")
    photos = relationship("DatePhoto", back_populates="active_date")

class DatePhoto(Base):
    __tablename__ = 'date_photos'

    id = Column(Integer, primary_key=True, index=True)
    active_date_id = Column(Integer, ForeignKey('active_dates.id'), nullable=False)
    photo_url = Column(String, nullable=False)

    active_date = relationship("ActiveDate", back_populates="photos")

class Penalty(Base):
    __tablename__ = 'penalties'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reason = Column(String, nullable=False)
    is_redeemed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)