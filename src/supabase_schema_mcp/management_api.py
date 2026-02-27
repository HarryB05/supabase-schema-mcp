"""Supabase Management API HTTP client (httpx)."""

import httpx
from pydantic import BaseModel

from supabase_schema_mcp.config import get_settings

MANAGEMENT_API_BASE = "https://api.supabase.com/v1"


class ProjectInfo(BaseModel):
    """Minimal project metadata from Management API."""

    id: str
    name: str
    ref: str
    region: str | None = None


async def get_project_info() -> ProjectInfo | None:
    """
    Fetch project details from the Supabase Management API.
    Returns None if Management API is not configured or the request fails.
    """
    settings = get_settings()
    if not settings.management_api_configured:
        return None
    url = f"{MANAGEMENT_API_BASE}/projects/{settings.supabase_project_ref}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            url,
            headers={"Authorization": f"Bearer {settings.supabase_service_role_key}"},
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        return ProjectInfo(
            id=data.get("id", ""),
            name=data.get("name", ""),
            ref=data.get("ref", settings.supabase_project_ref),
            region=data.get("region"),
        )
