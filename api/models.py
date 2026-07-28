from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class UserCreate(BaseModel):
    user_id: str
    full_name: str
    email: str
    phone_number: str
    bvn: Optional[str] = None
    nin: Optional[str] = None
    date_of_birth: date
    state: str
    signup_date: datetime
    kyc_verified_at: Optional[datetime] = None
    account_status: str