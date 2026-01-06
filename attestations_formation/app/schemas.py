from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class ConventionData(BaseModel):
    provider_name: str
    beneficiary_name: str
    date_start: str = Field(description="Format expected: DD/MM/YYYY")
    date_end: str = Field(description="Format expected: DD/MM/YYYY")
    duration: str
    action_title: str
    
    # Optional fields
    company_name: Optional[str] = None
    signatory_name: Optional[str] = None
    location: Optional[str] = None
    
    @field_validator("date_start", "date_end")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%d/%m/%Y")
        except ValueError:
            raise ValueError("Date format must be DD/MM/YYYY")
        return v

class AttestationData(BaseModel):
    signatory_name: str
    provider_name: str
    beneficiary_name: str
    company_name: str
    action_title: str
    checkbox_action_training: str = "X"
    date_start: str
    date_end: str
    duration: str
    location: str
    signature_date: str
