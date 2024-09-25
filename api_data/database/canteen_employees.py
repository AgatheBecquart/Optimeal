from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .core import DBCanteenEmployeesUser, NotFoundError
import string
import random


class CanteenEmployeeUser(BaseModel):
    employee_id: str
    employee_unique_id: str
    employee_username: str
    employee_password: str
    employee_email: str
    employee_first_name: str
    employee_last_name: str
    employee_zip_code_prefix: str
    employee_city: str
    employee_state: str


class CanteenEmployeeUserCreate(BaseModel):
    employee_unique_id: str
    employee_username: str
    employee_password: str
    employee_email: str
    employee_first_name: str
    employee_last_name: str
    employee_zip_code_prefix: str
    employee_city: str
    employee_state: str


class CanteenEmployeeUserUpdate(BaseModel):
    employee_unique_id: str
    employee_username: str
    employee_password: str
    employee_email: str
    employee_first_name: str
    employee_last_name: str
    employee_zip_code_prefix: str
    employee_city: str
    employee_state: str


def read_db_one_canteen_employee_user(
    employee_id: str, session: Session
) -> DBCanteenEmployeesUser:
    db_employee = (
        session.query(DBCanteenEmployeesUser)
        .filter(DBCanteenEmployeesUser.employee_id == employee_id)
        .first()
    )
    if db_employee is None:
        raise NotFoundError(f"Employee with id {employee_id} not found.")
    return db_employee


def read_db_canteen_employee_users(session: Session) -> List[DBCanteenEmployeesUser]:
    db_employees = session.query(DBCanteenEmployeesUser).limit(5).all()
    if not db_employees:
        raise NotFoundError("No employees found in the database.")
    return db_employees


def generate_id():
    """Generate a unique string ID."""
    length = 14
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for i in range(length))


def create_db_canteen_employee_user(
    employee: CanteenEmployeeUserCreate, session: Session
) -> DBCanteenEmployeesUser:
    db_employee = DBCanteenEmployeesUser(
        **employee.model_dump(exclude_none=True), employee_id=generate_id()
    )
    session.add(db_employee)
    session.commit()
    session.refresh(db_employee)
    return db_employee


def update_db_canteen_employee_user(
    employee_id: str, employee: CanteenEmployeeUserUpdate, session: Session
) -> DBCanteenEmployeesUser:
    db_employee = read_db_one_canteen_employee_user(employee_id, session)
    for key, value in employee.model_dump(exclude_none=True).items():
        setattr(db_employee, key, value)
    session.commit()
    session.refresh(db_employee)
    return db_employee


def delete_db_canteen_employee_user(
    employee_id: str, session: Session
) -> DBCanteenEmployeesUser:
    db_employee = read_db_one_canteen_employee_user(employee_id, session)
    session.delete(db_employee)
    session.commit()
    return db_employee
