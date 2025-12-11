"""
API Routes - Task Lists
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from pymstodo.client import ToDoConnection, PymstodoError
from ..models import TaskListCreate, TaskListUpdate, TaskListResponse
from ..dependencies import get_todo_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[TaskListResponse])
async def get_all_lists(
    limit: int = 99,
    client: ToDoConnection = Depends(get_todo_client)
):
    """
    Get all task lists
    
    Args:
        limit: Maximum number of lists to return (default: 99)
        
    Returns:
        List of task lists
    """
    try:
        lists = client.get_lists(limit=limit)
        return [
            TaskListResponse(
                list_id=lst.list_id,
                displayName=lst.displayName,
                isOwner=lst.isOwner,
                isShared=lst.isShared,
                wellknownListName=lst.wellknownListName
            )
            for lst in lists
        ]
    except PymstodoError as e:
        logger.error(f"Failed to get lists: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get lists: {str(e)}"
        )


@router.post("", response_model=TaskListResponse, status_code=201)
async def create_list(
    list_data: TaskListCreate,
    client: ToDoConnection = Depends(get_todo_client)
):
    """
    Create a new task list
    
    Args:
        list_data: Task list data
        
    Returns:
        Created task list
    """
    try:
        new_list = client.create_list(name=list_data.displayName)
        return TaskListResponse(
            list_id=new_list.list_id,
            displayName=new_list.displayName,
            isOwner=new_list.isOwner,
            isShared=new_list.isShared,
            wellknownListName=new_list.wellknownListName
        )
    except PymstodoError as e:
        logger.error(f"Failed to create list: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create list: {str(e)}"
        )


@router.get("/{list_id}", response_model=TaskListResponse)
async def get_list(
    list_id: str,
    client: ToDoConnection = Depends(get_todo_client)
):
    """
    Get a specific task list
    
    Args:
        list_id: Task list ID
        
    Returns:
        Task list details
    """
    try:
        lst = client.get_list(list_id=list_id)
        return TaskListResponse(
            list_id=lst.list_id,
            displayName=lst.displayName,
            isOwner=lst.isOwner,
            isShared=lst.isShared,
            wellknownListName=lst.wellknownListName
        )
    except PymstodoError as e:
        logger.error(f"Failed to get list {list_id}: {e}")
        raise HTTPException(
            status_code=404 if "404" in str(e) else 500,
            detail=f"Failed to get list: {str(e)}"
        )


@router.patch("/{list_id}", response_model=TaskListResponse)
async def update_list(
    list_id: str,
    list_data: TaskListUpdate,
    client: ToDoConnection = Depends(get_todo_client)
):
    """
    Update a task list
    
    Args:
        list_id: Task list ID
        list_data: Updated list data
        
    Returns:
        Updated task list
    """
    try:
        update_dict = list_data.model_dump(exclude_none=True)
        updated_list = client.update_list(list_id=list_id, **update_dict)
        return TaskListResponse(
            list_id=updated_list.list_id,
            displayName=updated_list.displayName,
            isOwner=updated_list.isOwner,
            isShared=updated_list.isShared,
            wellknownListName=updated_list.wellknownListName
        )
    except PymstodoError as e:
        logger.error(f"Failed to update list {list_id}: {e}")
        raise HTTPException(
            status_code=404 if "404" in str(e) else 500,
            detail=f"Failed to update list: {str(e)}"
        )


@router.delete("/{list_id}", status_code=204)
async def delete_list(
    list_id: str,
    client: ToDoConnection = Depends(get_todo_client)
):
    """
    Delete a task list
    
    Args:
        list_id: Task list ID
    """
    try:
        client.delete_list(list_id=list_id)
        return None
    except PymstodoError as e:
        logger.error(f"Failed to delete list {list_id}: {e}")
        raise HTTPException(
            status_code=404 if "404" in str(e) else 500,
            detail=f"Failed to delete list: {str(e)}"
        )
