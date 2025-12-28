"""
API Routes - Tasks
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
import logging

from ..graph_client import GraphAPIClient, GraphAPIError, TaskStatusFilter, GRAPH_API_DATETIME_FORMAT
from ..models import TaskCreate, TaskUpdate, TaskResponse, TaskStatusUpdate
from ..dependencies import get_todo_client

logger = logging.getLogger(__name__)

router = APIRouter()


def task_to_response(task) -> TaskResponse:
    """Convert Task object to TaskResponse"""
    return TaskResponse(
        task_id=task.task_id,
        title=task.title,
        status=task.status,
        importance=task.importance,
        body=task.body,
        createdDateTime=task.createdDateTime,
        lastModifiedDateTime=task.lastModifiedDateTime,
        completedDateTime=task.completedDateTime,
        dueDateTime=task.dueDateTime,
        reminderDateTime=task.reminderDateTime,
        startDateTime=task.startDateTime,
        isReminderOn=task.isReminderOn,
        hasAttachments=task.hasAttachments,
        categories=task.categories
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    list_id: str = Query(..., description="Task list ID"),
    client: GraphAPIClient = Depends(get_todo_client)
):
    """
    Get a specific task
    
    Args:
        task_id: Task ID
        list_id: Task list ID
        
    Returns:
        Task details
    """
    try:
        task = await client.get_task(task_id=task_id, list_id=list_id)
        return task_to_response(task)
    except GraphAPIError as e:
        logger.error(f"Failed to get task {task_id}: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    list_id: str = Query(..., description="Task list ID"),
    client: GraphAPIClient = Depends(get_todo_client)
):
    """
    Update a task
    
    Args:
        task_id: Task ID
        task_data: Updated task data
        list_id: Task list ID
        
    Returns:
        Updated task
    """
    try:
        # Build update dictionary
        update_dict = {}
        data_dict = task_data.model_dump(exclude_none=True)
        
        for key, value in data_dict.items():
            if key == 'body' and value:
                update_dict['body'] = {'content': value, 'contentType': 'text'}
            elif key == 'dueDateTime' and value:
                # Parse ISO format datetime
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                update_dict['dueDateTime'] = {
                    'dateTime': dt.strftime(GRAPH_API_DATETIME_FORMAT),
                    'timeZone': 'UTC'
                }
            elif key == 'reminderDateTime' and value:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                update_dict['reminderDateTime'] = {
                    'dateTime': dt.strftime(GRAPH_API_DATETIME_FORMAT),
                    'timeZone': 'UTC'
                }
            else:
                update_dict[key] = value
        
        updated_task = await client.update_task(task_id=task_id, list_id=list_id, **update_dict)
        return task_to_response(updated_task)
    except GraphAPIError as e:
        logger.error(f"Failed to update task {task_id}: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    list_id: str = Query(..., description="Task list ID"),
    client: GraphAPIClient = Depends(get_todo_client)
):
    """
    Delete a task
    
    Args:
        task_id: Task ID
        list_id: Task list ID
    """
    try:
        await client.delete_task(task_id=task_id, list_id=list_id)
        return None
    except GraphAPIError as e:
        logger.error(f"Failed to delete task {task_id}: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )


# Include list-specific task routes
from fastapi import APIRouter as _APIRouter
lists_tasks_router = _APIRouter()


@lists_tasks_router.get("/{list_id}/tasks", response_model=List[TaskResponse])
async def get_list_tasks(
    list_id: str,
    status: Optional[str] = Query('notCompleted', description="Filter by status: completed, notCompleted, or all"),
    limit: int = Query(1000, description="Maximum number of tasks to return"),
    client: GraphAPIClient = Depends(get_todo_client)
):
    """
    Get all tasks in a task list
    
    Args:
        list_id: Task list ID
        status: Filter by status (completed, notCompleted, all)
        limit: Maximum number of tasks to return
        
    Returns:
        List of tasks
    """
    try:
        # Map status string to TaskStatusFilter
        status_filter_map = {
            'completed': TaskStatusFilter.COMPLETED,
            'notCompleted': TaskStatusFilter.NOT_COMPLETED,
            'all': TaskStatusFilter.ALL
        }
        status_filter = status_filter_map.get(status, TaskStatusFilter.NOT_COMPLETED)
        
        tasks = await client.get_tasks(list_id=list_id, limit=limit, status=status_filter)
        return [task_to_response(task) for task in tasks]
    except GraphAPIError as e:
        logger.error(f"Failed to get tasks for list {list_id}: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )


@lists_tasks_router.post("/{list_id}/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    list_id: str,
    task_data: TaskCreate,
    client: GraphAPIClient = Depends(get_todo_client)
):
    """
    Create a new task in a task list
    
    Args:
        list_id: Task list ID
        task_data: Task data
        
    Returns:
        Created task
    """
    try:
        # Parse due date if provided
        due_date = None
        if task_data.dueDateTime:
            due_date = datetime.fromisoformat(task_data.dueDateTime.replace('Z', '+00:00'))
        
        # Create basic task
        new_task = await client.create_task(
            title=task_data.title,
            list_id=list_id,
            due_date=due_date,
            body_text=task_data.body
        )
        
        # Update additional fields if provided
        update_dict = {}
        if task_data.importance and task_data.importance != 'normal':
            update_dict['importance'] = task_data.importance
        if task_data.isReminderOn is not None:
            update_dict['isReminderOn'] = task_data.isReminderOn
        if task_data.reminderDateTime:
            dt = datetime.fromisoformat(task_data.reminderDateTime.replace('Z', '+00:00'))
            update_dict['reminderDateTime'] = {
                'dateTime': dt.strftime(GRAPH_API_DATETIME_FORMAT),
                'timeZone': 'UTC'
            }
        if task_data.categories:
            update_dict['categories'] = task_data.categories
        
        if update_dict:
            new_task = await client.update_task(
                task_id=new_task.task_id,
                list_id=list_id,
                **update_dict
            )
        
        return task_to_response(new_task)
    except GraphAPIError as e:
        logger.error(f"Failed to create task in list {list_id}: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
