from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import List
from typing import List, Annotated
from api_data.database.core import NotFoundError, get_db
from api_data.database.authentificate import oauth2_scheme, has_access, User
from api_data.database.canteen_employees import (
    CanteenEmployeeUser,
    CanteenEmployeeUserCreate,
    CanteenEmployeeUserUpdate,
    read_db_canteen_employee_users,
    read_db_one_canteen_employee_user,
    create_db_canteen_employee_user,
    update_db_canteen_employee_user,
    delete_db_canteen_employee_user,
)


PROTECTED = Annotated[User, Depends(has_access)]

router = APIRouter(
    prefix="/employees",
)


@router.get("/{employee_id}", response_model=CanteenEmployeeUser)
def get_one_employee(
    request: Request, employee_id: str, db: Session = Depends(get_db)
) -> CanteenEmployeeUser:
    try:
        db_employee = read_db_one_canteen_employee_user(employee_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return CanteenEmployeeUser(**db_employee.__dict__)


@router.get("/", response_model=List[CanteenEmployeeUser])
def get_employees(
    request: Request, db: Session = Depends(get_db)
) -> List[CanteenEmployeeUser]:
    try:
        db_employees = read_db_canteen_employee_users(db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return [CanteenEmployeeUser(**employee.__dict__) for employee in db_employees]


@router.post("/")
def create_employee(
    has_access: PROTECTED,
    request: Request,
    employee: CanteenEmployeeUserCreate,
    db: Session = Depends(get_db),
) -> CanteenEmployeeUser:
    db_employee = create_db_canteen_employee_user(employee, db)
    return CanteenEmployeeUser(**db_employee.__dict__)


@router.put("/{employee_id}")
def update_employee(
    has_access: PROTECTED,
    request: Request,
    employee_id: str,
    employee: CanteenEmployeeUserUpdate,
    db: Session = Depends(get_db),
) -> CanteenEmployeeUser:
    try:
        db_employee = update_db_canteen_employee_user(employee_id, employee, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return CanteenEmployeeUser(**db_employee.__dict__)


@router.delete("/{employee_id}")
def delete_employee(
    has_access: PROTECTED,
    request: Request,
    employee_id: str,
    db: Session = Depends(get_db),
) -> CanteenEmployeeUser:
    try:
        db_employee = delete_db_canteen_employee_user(employee_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return CanteenEmployeeUser(**db_employee.__dict__)
