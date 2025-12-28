"""
Microsoft Graph API Client for To Do Tasks
"""
import logging
import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Microsoft Graph API datetime format constant
GRAPH_API_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.0000000'


class GraphAPIError(Exception):
    """Custom exception for Graph API errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
    
    def __str__(self):
        return f"[{self.status_code}] {self.message}"


class TaskStatusFilter:
    """Task status filter constants"""
    ALL = "all"
    COMPLETED = "completed"
    NOT_COMPLETED = "notCompleted"


class TaskList:
    """Task List object"""
    def __init__(self, data: Dict[str, Any]):
        self.list_id = data.get('id', '')
        self.displayName = data.get('displayName', '')
        self.isOwner = data.get('isOwner', False)
        self.isShared = data.get('isShared', False)
        self.wellknownListName = data.get('wellknownListName')


class Task:
    """Task object"""
    def __init__(self, data: Dict[str, Any]):
        self.task_id = data.get('id', '')
        self.title = data.get('title', '')
        self.status = data.get('status', 'notStarted')
        self.importance = data.get('importance', 'normal')
        self.body = data.get('body')
        self.createdDateTime = data.get('createdDateTime')
        self.lastModifiedDateTime = data.get('lastModifiedDateTime')
        self.completedDateTime = data.get('completedDateTime')
        self.dueDateTime = data.get('dueDateTime')
        self.reminderDateTime = data.get('reminderDateTime')
        self.startDateTime = data.get('startDateTime')
        self.isReminderOn = data.get('isReminderOn', False)
        self.hasAttachments = data.get('hasAttachments', False)
        self.categories = data.get('categories', [])


class GraphAPIClient:
    """Microsoft Graph API client for To Do operations"""
    
    def __init__(self, access_token: str, api_version: str = "beta"):
        """
        Initialize Graph API client
        
        Args:
            access_token: OAuth access token
            api_version: API version (v1.0 or beta)
        """
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f"https://graph.microsoft.com/{api_version}"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Graph API
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            
        Returns:
            Response JSON data
            
        Raises:
            GraphAPIError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params,
                    timeout=30.0
                )
            
            # Handle different status codes
            if response.status_code == 204:
                return {}
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', response.text)
                except (ValueError, KeyError):
                    error_msg = response.text
                logger.error(f"Graph API error {response.status_code}: {error_msg}")
                raise GraphAPIError(error_msg, status_code=response.status_code)
            
            # Parse JSON response
            try:
                return response.json() if response.content else {}
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise GraphAPIError(f"Invalid JSON response: {str(e)}", status_code=500)
            
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            raise GraphAPIError(f"Request failed: {str(e)}", status_code=503)
    
    # List operations
    
    async def get_lists(self, limit: int = 99, skip_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all task lists with pagination support
        
        Args:
            limit: Maximum number of lists to return
            skip_token: Pagination token for next page
            
        Returns:
            Dictionary with 'value' (list of TaskList objects), 'nextLink' (optional), and 'count'
        """
        endpoint = "/me/todo/lists"
        params = {"$top": limit}
        
        if skip_token:
            params["$skiptoken"] = skip_token
        
        response = await self._make_request("GET", endpoint, params=params)
        lists_data = response.get('value', [])
        
        return {
            'value': [TaskList(list_data) for list_data in lists_data],
            'nextLink': response.get('@odata.nextLink'),
            'count': len(lists_data)
        }
    
    async def get_list(self, list_id: str) -> TaskList:
        """
        Get a specific task list
        
        Args:
            list_id: Task list ID
            
        Returns:
            TaskList object
        """
        endpoint = f"/me/todo/lists/{list_id}"
        response = await self._make_request("GET", endpoint)
        return TaskList(response)
    
    async def create_list(self, name: str) -> TaskList:
        """
        Create a new task list
        
        Args:
            name: Display name for the list
            
        Returns:
            Created TaskList object
        """
        endpoint = "/me/todo/lists"
        data = {"displayName": name}
        
        response = await self._make_request("POST", endpoint, data=data)
        return TaskList(response)
    
    async def update_list(self, list_id: str, **kwargs) -> TaskList:
        """
        Update a task list
        
        Args:
            list_id: Task list ID
            **kwargs: Fields to update (e.g., displayName)
            
        Returns:
            Updated TaskList object
        """
        endpoint = f"/me/todo/lists/{list_id}"
        
        # Build update data
        data = {}
        if 'displayName' in kwargs:
            data['displayName'] = kwargs['displayName']
        
        response = await self._make_request("PATCH", endpoint, data=data)
        return TaskList(response)
    
    async def delete_list(self, list_id: str) -> None:
        """
        Delete a task list
        
        Args:
            list_id: Task list ID
        """
        endpoint = f"/me/todo/lists/{list_id}"
        await self._make_request("DELETE", endpoint)
    
    # Task operations
    
    async def get_tasks(
        self,
        list_id: str,
        limit: int = 1000,
        status: str = TaskStatusFilter.NOT_COMPLETED,
        skip_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get tasks from a list with pagination support
        
        Args:
            list_id: Task list ID
            limit: Maximum number of tasks to return
            status: Filter by status (all, completed, notCompleted)
            skip_token: Pagination token for next page
            
        Returns:
            Dictionary with 'value' (list of Task objects), 'nextLink' (optional), and 'count'
        """
        endpoint = f"/me/todo/lists/{list_id}/tasks"
        params = {"$top": limit}
        
        if skip_token:
            params["$skiptoken"] = skip_token
        
        # Add status filter
        if status == TaskStatusFilter.COMPLETED:
            params["$filter"] = "status eq 'completed'"
        elif status == TaskStatusFilter.NOT_COMPLETED:
            params["$filter"] = "status ne 'completed'"
        # For 'all', no filter needed
        
        response = await self._make_request("GET", endpoint, params=params)
        tasks_data = response.get('value', [])
        
        return {
            'value': [Task(task_data) for task_data in tasks_data],
            'nextLink': response.get('@odata.nextLink'),
            'count': len(tasks_data)
        }
    
    async def get_task(self, task_id: str, list_id: str) -> Task:
        """
        Get a specific task
        
        Args:
            task_id: Task ID
            list_id: Task list ID
            
        Returns:
            Task object
        """
        endpoint = f"/me/todo/lists/{list_id}/tasks/{task_id}"
        response = await self._make_request("GET", endpoint)
        return Task(response)
    
    async def create_task(
        self,
        title: str,
        list_id: str,
        due_date: Optional[datetime] = None,
        body_text: Optional[str] = None
    ) -> Task:
        """
        Create a new task
        
        Args:
            title: Task title
            list_id: Task list ID
            due_date: Optional due date
            body_text: Optional body text
            
        Returns:
            Created Task object
        """
        endpoint = f"/me/todo/lists/{list_id}/tasks"
        
        data = {"title": title}
        
        if body_text:
            data['body'] = {
                'content': body_text,
                'contentType': 'text'
            }
        
        if due_date:
            data['dueDateTime'] = {
                'dateTime': due_date.strftime(GRAPH_API_DATETIME_FORMAT),
                'timeZone': 'UTC'
            }
        
        response = await self._make_request("POST", endpoint, data=data)
        return Task(response)
    
    async def update_task(self, task_id: str, list_id: str, **kwargs) -> Task:
        """
        Update a task
        
        Args:
            task_id: Task ID
            list_id: Task list ID
            **kwargs: Fields to update
            
        Returns:
            Updated Task object
        """
        endpoint = f"/me/todo/lists/{list_id}/tasks/{task_id}"
        
        # Build update data from kwargs
        data = {}
        
        # Handle simple fields
        for field in ['title', 'status', 'importance', 'isReminderOn', 'categories']:
            if field in kwargs:
                data[field] = kwargs[field]
        
        # Handle complex fields
        if 'body' in kwargs:
            data['body'] = kwargs['body']
        
        if 'dueDateTime' in kwargs:
            data['dueDateTime'] = kwargs['dueDateTime']
        
        if 'reminderDateTime' in kwargs:
            data['reminderDateTime'] = kwargs['reminderDateTime']
        
        response = await self._make_request("PATCH", endpoint, data=data)
        return Task(response)
    
    async def delete_task(self, task_id: str, list_id: str) -> None:
        """
        Delete a task
        
        Args:
            task_id: Task ID
            list_id: Task list ID
        """
        endpoint = f"/me/todo/lists/{list_id}/tasks/{task_id}"
        await self._make_request("DELETE", endpoint)
