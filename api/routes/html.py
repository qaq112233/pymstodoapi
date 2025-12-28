"""
API Routes - HTML Rendering for E-ink Display
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from datetime import datetime
from pathlib import Path
import logging
import pytz

from pymstodo.client import ToDoConnection, PymstodoError, TaskStatusFilter
from ..dependencies import get_todo_client
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Set up Jinja2 templates
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Timezone for all datetime operations
SHANGHAI_TZ = pytz.timezone('Asia/Shanghai')


async def verify_query_auth(passwd: Optional[str] = Query(None)) -> None:
    """
    Verify query-based authentication if enabled
    
    Args:
        passwd: Password from query string
        
    Raises:
        HTTPException: If authentication fails
    """
    if not settings.enable_query_auth:
        return
    
    if not passwd or passwd != settings.query_passwd:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing password"
        )


@router.get("/{list_id}/tasks.html", response_class=HTMLResponse)
async def render_tasks_html(
    list_id: str,
    request: Request,
    client: ToDoConnection = Depends(get_todo_client),
    _auth: None = Depends(verify_query_auth)
):
    """
    Render tasks as HTML for e-ink display
    
    Args:
        list_id: Task list ID
        request: FastAPI request object
        
    Returns:
        HTML page with tasks formatted for e-ink display
    """
    try:
        # Get all incomplete tasks
        tasks = client.get_tasks(
            list_id=list_id, 
            limit=1000, 
            status=TaskStatusFilter.NOT_COMPLETED
        )
        
        # Get current date in Shanghai timezone
        now_shanghai = datetime.now(SHANGHAI_TZ)
        today_date = now_shanghai.date()
        
        # Process tasks
        processed_tasks = []
        for task in tasks:
            # Determine if starred (high importance)
            is_starred = task.importance == 'high'
            
            # Determine if due today
            is_due_today = False
            if task.dueDateTime:
                # Parse the due date and convert to Shanghai timezone
                try:
                    # dueDateTime format from API: {'dateTime': '2024-01-01T00:00:00.0000000', 'timeZone': 'UTC'}
                    due_dt_str = task.dueDateTime.get('dateTime', '')
                    if due_dt_str:
                        # Parse the datetime string
                        due_dt = datetime.fromisoformat(due_dt_str.replace('Z', '+00:00'))
                        
                        # Get timezone from task or default to UTC
                        task_tz_str = task.dueDateTime.get('timeZone', 'UTC')
                        if task_tz_str == 'UTC':
                            task_tz = pytz.UTC
                        else:
                            try:
                                task_tz = pytz.timezone(task_tz_str)
                            except:
                                task_tz = pytz.UTC
                        
                        # If datetime is naive, localize it
                        if due_dt.tzinfo is None:
                            due_dt = task_tz.localize(due_dt)
                        
                        # Convert to Shanghai timezone
                        due_dt_shanghai = due_dt.astimezone(SHANGHAI_TZ)
                        is_due_today = due_dt_shanghai.date() == today_date
                except Exception as e:
                    logger.warning(f"Failed to parse due date for task {task.task_id}: {e}")
            
            processed_tasks.append({
                'title': task.title,
                'is_starred': is_starred,
                'is_due_today': is_due_today
            })
        
        # Generate timestamp
        generated_at = now_shanghai.strftime('%Y-%m-%d %H:%M:%S')
        
        # Render template
        return templates.TemplateResponse(
            "tasks.html",
            {
                "request": request,
                "tasks": processed_tasks,
                "generated_at": generated_at
            }
        )
        
    except PymstodoError as e:
        logger.error(f"Failed to get tasks for list {list_id}: {e}")
        raise HTTPException(
            status_code=404 if "404" in str(e) else 500,
            detail=f"Failed to get tasks: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error rendering tasks HTML: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to render tasks: {str(e)}"
        )
