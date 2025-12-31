
from sqlalchemy import (
    Column, Integer, String, Date, ForeignKey, UniqueConstraint, Text
)
from sqlalchemy.orm import relationship
from .database import Base

class Staff(Base):
    __tablename__ = 'staff'

    staff_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    

    
    computers = relationship(
    'Computer',
    back_populates='owner',
    cascade='all, delete-orphan',
    foreign_keys='Computer.staff_id',   # disambiguate: use the owner FK
    )


    __table_args__ = (
        UniqueConstraint('name', name='uq_staff_name'),
    )


class Computer(Base):
    __tablename__ = 'computers'

    computer_id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey('staff.staff_id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    comp_name = Column(String, nullable=False, unique=True)
    computer_model = Column(String, nullable=False)
    service_tag = Column(String, nullable=False, unique=True)
    warranty_end = Column(Date, nullable=True)

    # LEGACY: previously FK to staff; keep column so old rows load, but we won't use it
    manager_staff_id = Column(Integer, ForeignKey('staff.staff_id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)

    # NEW: binary manager flag
    is_manager = Column(Integer, nullable=False, default=0)  # 0/1 boolean
    ticket_number = Column(String, nullable=True)
    owner = relationship('Staff', foreign_keys=[staff_id], back_populates='computers')
    # REMOVE: manager relationship
    # manager = relationship('Staff', foreign_keys=[manager_staff_id])
    software = relationship('SpecialSoftware', back_populates='computer', cascade='all, delete-orphan')

class SpecialSoftware(Base):
    __tablename__ = 'special_software'

    software_id = Column(Integer, primary_key=True, index=True)
    computer_id = Column(Integer, ForeignKey('computers.computer_id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    software_name = Column(String, nullable=False)

    computer = relationship('Computer', back_populates='software')

    __table_args__ = (
        UniqueConstraint('computer_id', 'software_name', name='uq_sw_per_computer'),
    )
