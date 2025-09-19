from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

import httpx


class TimeRange(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class WakapiLog:
    id: str
    user_id: str
    project_name: str
    language: str
    editor: str
    operating_system: str
    machine: str
    entity: str
    type: str
    time: datetime
    data: Dict[str, Any]
    branch: Optional[str] = None
    is_write: bool = False


@dataclass
class WakapiStats:
    total_time: float
    total_count: int
    languages: Dict[str, int]
    projects: Dict[str, int]


@dataclass
class WakapiConfig:
    base_url: str
    api_key: str
    user_id: str

    def __post_init__(self):
        if not self.base_url.endswith("/"):
            self.base_url += "/"


class WakapiClient:
    def __init__(self, config: WakapiConfig):
        self.config = config
        self.client = httpx.AsyncClient()
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        project_name: Optional[str] = None,
        limit: int = 1000
    ) -> List[WakapiLog]:
        params: Dict[str, Any] = {"limit": limit}
        
        if start_date:
            params["start"] = start_date.isoformat()
        if end_date:
            params["end"] = end_date.isoformat()
        if project_name:
            params["project"] = project_name
            
        url = f"{self.config.base_url}api/users/{self.config.user_id}/data"
        
        response = await self.client.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        
        data = response.json()
        logs = []
        
        for item in data.get("data", []):
            log = WakapiLog(
                id=item["id"],
                user_id=item["user"],
                project_name=item["project"],
                language=item["language"],
                editor=item["editor"],
                operating_system=item["operatingSystem"],
                machine=item["machine"],
                entity=item["entity"],
                type=item["type"],
                time=datetime.fromisoformat(item["time"]),
                data=item.get("data", {}),
                branch=item.get("branch"),
                is_write=item.get("isWrite", False)
            )
            logs.append(log)
            
        return logs
    
    async def get_stats(
        self,
        time_range: TimeRange = TimeRange.DAILY,
        project_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> WakapiStats:
        params: Dict[str, Any] = {"range": time_range.value}
        
        if project_name:
            params["project"] = project_name
        if start_date:
            params["start"] = start_date.isoformat()
        if end_date:
            params["end"] = end_date.isoformat()
            
        url = f"{self.config.base_url}api/users/{self.config.user_id}/stats"
        
        response = await self.client.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        
        data = response.json()
        
        return WakapiStats(
            total_time=data.get("total", 0),
            total_count=data.get("total_count", 0),
            languages=data.get("languages", {}),
            projects=data.get("projects", {})
        )
    
    async def get_projects(self) -> List[str]:
        url = f"{self.config.base_url}api/users/{self.config.user_id}/projects"
        
        response = await self.client.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        data = response.json()
        return data.get("data", [])
    
    async def get_languages(self) -> List[str]:
        url = f"{self.config.base_url}api/users/{self.config.user_id}/languages"
        
        response = await self.client.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        data = response.json()
        return data.get("data", [])