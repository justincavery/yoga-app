"""
Pydantic schemas for Practice History API endpoints.
Request and response models for history, statistics, and calendar operations.
"""
from datetime import datetime, date
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

from app.models.practice_session import CompletionStatus


class PracticeSessionBase(BaseModel):
    """Base schema for PracticeSession."""
    session_id: int = Field(..., description="Unique identifier for the session")
    user_id: int = Field(..., description="ID of the user who practiced")
    sequence_id: int = Field(..., description="ID of the sequence practiced")
    started_at: datetime = Field(..., description="When the session started")
    completed_at: Optional[datetime] = Field(None, description="When the session completed")
    duration_seconds: int = Field(..., description="Total duration in seconds")
    completion_status: CompletionStatus = Field(..., description="Session completion status")

    model_config = {
        "from_attributes": True
    }


class PracticeSessionWithSequence(PracticeSessionBase):
    """Practice session with sequence details included."""
    sequence_name: str = Field(..., description="Name of the practiced sequence")
    sequence_difficulty: str = Field(..., description="Difficulty level of the sequence")
    sequence_focus_area: str = Field(..., description="Focus area of the sequence")

    model_config = {
        "from_attributes": True
    }


class PracticeHistoryResponse(BaseModel):
    """Schema for paginated practice history."""
    sessions: List[PracticeSessionWithSequence] = Field(..., description="List of practice sessions")
    total: int = Field(..., description="Total number of sessions matching criteria")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class PracticeStatisticsResponse(BaseModel):
    """Schema for comprehensive practice statistics."""
    total_sessions: int = Field(..., description="Total completed sessions")
    total_practice_time_seconds: int = Field(..., description="Total practice time in seconds")
    total_practice_time_hours: float = Field(..., description="Total practice time in hours")
    average_session_duration_minutes: float = Field(..., description="Average session duration in minutes")
    current_streak_days: int = Field(..., description="Current consecutive days practiced")
    completion_rate_percentage: float = Field(..., description="Percentage of sessions completed (0-100)")
    sessions_last_30_days: int = Field(..., description="Number of sessions in the last 30 days")
    most_practiced_sequences: List[dict] = Field(
        default_factory=list,
        description="Most frequently practiced sequences with counts"
    )


class CalendarDayData(BaseModel):
    """Schema for a single day's practice data."""
    practice_date: date = Field(..., description="Date in YYYY-MM-DD format", alias="date")
    session_count: int = Field(..., description="Number of sessions completed on this day")
    total_duration_seconds: int = Field(..., description="Total practice time on this day in seconds")

    model_config = {
        "populate_by_name": True
    }


class CalendarMonthData(BaseModel):
    """Schema for a month's practice data."""
    year: int = Field(..., description="Year")
    month: int = Field(..., description="Month (1-12)")
    days: List[CalendarDayData] = Field(..., description="Practice data for each day with sessions")


class CalendarResponse(BaseModel):
    """Schema for calendar view of practice history."""
    months: List[CalendarMonthData] = Field(..., description="Practice data grouped by month")
    total_days_practiced: int = Field(..., description="Total unique days with practice sessions")
