from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Json


class BaseItem(BaseModel):
    id: int
    vocode_ai_id: str
    client_id: str
    user_id: int
    active: bool
    label: str
    inbound_agent: str
    outbound_only: bool
    number: str
    telephony_provider: str
    telephony_account_connection: str
    created_at: datetime
    updated_at: datetime
