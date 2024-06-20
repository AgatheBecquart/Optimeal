from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .core import DBCanteenEmployees, NotFoundError
import string
import random

class CanteenEmployee(BaseModel):
    employee_id: str
    employee_unique_id: str
    employee_zip_code_prefix: str
    employee_city: str
    employee_state: str

class CanteenEmployeeCreate(BaseModel):
    employee_unique_id: str
    employee_zip_code_prefix: str
    employee_city: str
    employee_state: str

class CanteenEmployeeUpdate(BaseModel):
    employee_unique_id: str
    employee_zip_code_prefix: str
    employee_city: str
    employee_state: str

def read_db_one_canteen_employee(employee_id: str, session: Session) -> DBCanteenEmployees:
    db_employee = session.query(DBCanteenEmployees).filter(DBCanteenEmployees.employee_id == employee_id).first()
    if db_employee is None:
        raise NotFoundError(f"Employee with id {employee_id} not found.")
    return db_employee

def read_db_canteen_employees(session: Session) -> List[DBCanteenEmployees]:
    db_employees = session.query(DBCanteenEmployees).limit(5).all()
    if not db_employees:
        raise NotFoundError("No employees found in the database.")
    return db_employees

def generate_id():
    """Generate a unique string ID."""
    length = 14
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def create_db_canteen_employee(employee: CanteenEmployeeCreate, session: Session) -> DBCanteenEmployees:
    db_employee = DBCanteenEmployees(**employee.model_dump(exclude_none=True), employee_id=generate_id())
    session.add(db_employee)
    session.commit()
    session.refresh(db_employee)
    return db_employee

def update_db_canteen_employee(employee_id: str, employee: CanteenEmployeeUpdate, session: Session) -> DBCanteenEmployees:
    db_employee = read_db_one_canteen_employee(employee_id, session)
    for key, value in employee.model_dump(exclude_none=True).items():
        setattr(db_employee, key, value)
    session.commit()
    session.refresh(db_employee)
    return db_employee

def delete_db_canteen_employee(employee_id: str, session: Session) -> DBCanteenEmployees:
    db_employee = read_db_one_canteen_employee(employee_id, session)
    session.delete(db_employee)
    session.commit()
    return db_employee
