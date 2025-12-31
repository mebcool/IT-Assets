
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date

class StaffCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None

class StaffUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class StaffOut(BaseModel):
    staff_id: int
    name: str
    email: Optional[EmailStr]

    class Config:
        from_attributes = True

class ComputerCreate(BaseModel):
    staff_id: int
    comp_name: str
    computer_model: str
    service_tag: str
    warranty_end: Optional[date] = None
    is_manager: bool = False
    ticket_number: Optional[str] = None

class ComputerUpdate(BaseModel):
    staff_id: Optional[int] = None
    comp_name: Optional[str] = None
    computer_model: Optional[str] = None
    service_tag: Optional[str] = None
    warranty_end: Optional[date] = None
    manager_staff_id: Optional[int] = None
    is_manager: Optional[bool] = None
    ticket_number: Optional[str] = None

class ComputerOut(BaseModel):
    computer_id: int
    staff_id: int
    comp_name: str
    computer_model: str
    service_tag: str
    warranty_end: Optional[date]
    manager_staff_id: Optional[int]
    is_manager: bool 
    ticket_number: Optional[str]
    class Config:
        from_attributes = True

class SoftwareCreate(BaseModel):
    computer_id: int
    software_name: str

class SoftwareUpdate(BaseModel):
    computer_id: Optional[int] = None
    software_name: Optional[str] = None

class SoftwareOut(BaseModel):
    software_id: int
    computer_id: int
    software_name: str

    class Config:
        from_attributes = True
