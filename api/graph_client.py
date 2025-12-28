"""
Microsoft Graph API Client for To Do Tasks
"""
import logging
import requests
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class GraphAPIError(Exception):
    """Custom exception for Graph API errors"""
    pass


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
    
    def _make_request(
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
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            
            # Handle different status codes
            if response.status_code == 204:
                return {}
            
            if response.status_code >= 400:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', {}).get('message', response.text)
                logger.error(f"Graph API error {response.status_code}: {error_msg}")
                raise GraphAPIError(f"{response.status_code}: {error_msg}")
            
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise GraphAPIError(f"Request failed: {str(e)}")
    
    # List operations
    
    def get_lists(self, limit: int = 99) -> List[TaskList]:
        """
        Get all task lists
        
        Args:
            limit: Maximum number of lists to return
            
        Returns:
            List of TaskList objects
        """
        endpoint = "/me/todo/lists"
        params = {"$top": limit}
        
        response = self._make_request("GET", endpoint, params=params)
        lists_data = response.get('value', [])
        
        return [TaskList(list_data) for list_data in lists_data]
    
    def get_list(self, list_id: str) -> TaskList:
        """
        Get a specific task list
        
        Args:
            list_id: Task list ID
            
        Returns:
            TaskList object
        """
        endpoint = f"/me/todo/lists/{list_id}"
        response = self._make_request("GET", endpoint)
        return TaskList(response)
    
    def create_list(self, name: str) -> TaskList:
        """
        Create a new task list
        
        Args:
            name: Display name for the list
            
        Returns:
            Created TaskList object
        """
        endpoint = "/me/todo/lists"
        data = {"displayName": name}
        
        response = self._make_request("POST", endpoint, data=data)
        return TaskList(response)
    
    def update_list(self, list_id: str, **kwargs) -> TaskList:
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
        
        response = self._make_request("PATCH", endpoint, data=data)
        return TaskList(response)
    
    def delete_list(self, list_id: str) -> None:
        """
        Delete a task list
        
        Args:
            list_id: Task list ID
        """
        endpoint = f"/me/todo/lists/{list_id}"
        self._make_request("DELETE", endpoint)
    
    # Task operations
    
    def get_tasks(
        self,
        list_id: str,
        limit: int = 1000,
        status: str = TaskStatusFilter.NOT_COMPLETED
    ) -> List[Task]:
        """
        Get tasks from a list
        
        Args:
            list_id: Task list ID
            limit: Maximum number of tasks to return
            status: Filter by status (all, completed, notCompleted)
            
        Returns:
            List of Task objects
        """
        endpoint = f"/me/todo/lists/{list_id}/tasks"
        params = {"$top": limit}
        
        # Add status filter
        if status == TaskStatusFilter.COMPLETED:
            params["$filter"] = "status eq 'completed'"
        elif status == TaskStatusFilter.NOT_COMPLETED:
            params["$filter"] = "status ne 'completed'"
        # For 'all', no filter needed
        
        response = self._make_request("GET", endpoint, params=params)
        tasks_data = response.get('value', [])
        
        return [Task(task_data) for task_data in tasks_data]
    
    def get_task(self, task_id: str, list_id: str) -> Task:
        """
        Get a specific task
        
        Args:
            task_id: Task ID
            list_id: Task list ID
            
        Returns:
            Task object
        """
        endpoint = f"/me/todo/lists/{list_id}/tasks/{task_id}"
        response = self._make_request("GET", endpoint)
        return Task(response)
    
    def create_task(
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
                'dateTime': due_date.strftime('%Y-%m-%dT%H:%M:%S.0000000'),
                'timeZone': 'UTC'
            }
        
        response = self._make_request("POST", endpoint, data=data)
        return Task(response)
    
    def update_task(self, task_id: str, list_id: str, **kwargs) -> Task:
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
        
        response = self._make_request("PATCH", endpoint, data=data)
        return Task(response)
    
    def delete_task(self, task_id: str, list_id: str) -> None:
        """
        Delete a task
        
        Args:
            task_id: Task ID
            list_id: Task list ID
        """
        endpoint = f"/me/todo/lists/{list_id}/tasks/{task_id}"
        self._make_request("DELETE", endpoint)
