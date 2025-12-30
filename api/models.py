"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime


# Error Models
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    status_code: Optional[int] = None


# Auth Models
class LoginResponse(BaseModel):
    """Login URL response"""
    authorization_url: str
    message: str = "Please visit this URL to authorize the application"


class CallbackRequest(BaseModel):
    """Callback request with authorization code"""
    code: str
    state: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response"""
    message: str
    authenticated: bool


# Task List Models
class TaskListCreate(BaseModel):
    """Create task list request"""
    displayName: str = Field(
        ..., 
        min_length=1, 
        max_length=255, 
        description="Name of the task list",
        pattern=r'^[^<>"\'&]*$'  # Prevent XSS characters
    )


class TaskListUpdate(BaseModel):
    """Update task list request"""
    displayName: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=255, 
        description="Name of the task list",
        pattern=r'^[^<>"\'&]*$'  # Prevent XSS characters
    )


class TaskListResponse(BaseModel):
    """Task list response"""
    list_id: str
    displayName: str
    isOwner: bool
    isShared: bool
    wellknownListName: Optional[str] = None


class PaginatedTaskListResponse(BaseModel):
    """Paginated task list response"""
    value: List[TaskListResponse]
    nextLink: Optional[str] = Field(None, description="URL to fetch next page of results")
    count: int = Field(description="Total number of items in current page")


# Task Models
class DateTimeTimeZone(BaseModel):
    """DateTime with timezone"""
    dateTime: str
    timeZone: str


class TaskBody(BaseModel):
    """Task body content"""
    content: str
    contentType: Literal['text', 'html'] = 'text'


class TaskCreate(BaseModel):
    """Create task request"""
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=255, 
        description="Task title",
        pattern=r'^[^<>"\']*$'  # Prevent XSS characters
    )
    body: Optional[str] = Field(None, max_length=10000, description="Task body content")
    dueDateTime: Optional[str] = Field(None, description="Due date in ISO 8601 format")
    reminderDateTime: Optional[str] = Field(None, description="Reminder date in ISO 8601 format")
    importance: Optional[Literal['low', 'normal', 'high']] = Field('normal', description="Task importance")
    isReminderOn: Optional[bool] = Field(False, description="Enable reminder")
    categories: Optional[List[str]] = Field(None, max_length=10, description="Task categories (max 10)")


class TaskUpdate(BaseModel):
    """Update task request"""
    title: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=255, 
        description="Task title",
        pattern=r'^[^<>"\']*$'  # Prevent XSS characters
    )
    body: Optional[str] = Field(None, max_length=10000, description="Task body content")
    status: Optional[Literal['notStarted', 'inProgress', 'completed', 'waitingOnOthers', 'deferred']] = Field(
        None, description="Task status"
    )
    importance: Optional[Literal['low', 'normal', 'high']] = Field(None, description="Task importance")
    isReminderOn: Optional[bool] = Field(None, description="Enable reminder")
    dueDateTime: Optional[str] = Field(None, description="Due date in ISO 8601 format")
    reminderDateTime: Optional[str] = Field(None, description="Reminder date in ISO 8601 format")
    categories: Optional[List[str]] = Field(None, max_length=10, description="Task categories (max 10)")


class TaskResponse(BaseModel):
    """Task response"""
    task_id: str
    title: str
    status: str
    importance: str
    body: Optional[dict] = None
    createdDateTime: Optional[str] = None
    lastModifiedDateTime: Optional[str] = None
    completedDateTime: Optional[dict] = None
    dueDateTime: Optional[dict] = None
    reminderDateTime: Optional[dict] = None
    startDateTime: Optional[dict] = None
    isReminderOn: bool
    hasAttachments: bool
    categories: Optional[List[str]] = None


class TaskStatusUpdate(BaseModel):
    """Update task status"""
    completed: bool = Field(..., description="Set to true to mark as completed, false for incomplete")


class PaginatedTaskResponse(BaseModel):
    """Paginated task response"""
    value: List[TaskResponse]
    nextLink: Optional[str] = Field(None, description="URL to fetch next page of results")
    count: int = Field(description="Total number of items in current page")
