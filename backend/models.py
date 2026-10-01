from enum import Enum
from datetime import datetime
from pydantic import BaseModel

class Status(str, Enum):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    LIMITED = 'LIMITED'
    UNKNOWN = 'UNKNOWN'

class CheckResult(BaseModel):
    status: Status = Status.UNKNOWN
    reason: str
    dine_in: bool | None = None
    takeaway: bool | None = None
    evidence: list[str] = []

class Restaurant(BaseModel):
    id: str
    name: str
    name_en: str
    name_zh: str
    name_zh_origin: str
    location: str
    location_zh: str
    platform: str | None = None
    order_url: str | None = None
    info_url: str
    dine_in: bool | None = None
    takeaway: bool | None = None
    # Stable supported online fulfillment modes, separate from live evidence.
    dine_in_available: bool | None = None
    takeaway_available: bool | None = None
    services_source: str
    services_source_url: str | None = None
    online_payment: bool | None = None
    mobile_only: bool = False
    session_minutes: int | None = None
    ordering_notes_source_url: str | None = None
    status: Status = Status.UNKNOWN
    reason: str = 'Waiting for official ordering evidence.'
    last_checked: datetime | None = None
    check_delayed: bool = False
    category: str
    icon: str
    tone: str
    evidence: list[str] = []
