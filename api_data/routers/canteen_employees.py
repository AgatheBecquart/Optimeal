from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import List
from typing import List, Annotated
from database.core import NotFoundError, get_db
from database.authentificate import oauth2_scheme, has_access, User
from database.canteen_employees import CanteenEmployee, CanteenEmployeeCreate, CanteenEmployeeUpdate, read_db_canteen_employees, read_db_one_canteen_employee, \
    create_db_canteen_employee, update_db_canteen_employee, delete_db_canteen_employee


PROTECTED = Annotated[User, Depends(has_access)]

router = APIRouter(
    prefix="/employees",
)

@router.get("/{employee_id}", response_model=CanteenEmployee)
def get_one_employee(request: Request, employee_id: str, db: Session = Depends(get_db)) -> CanteenEmployee:
    try:
        db_employee = read_db_one_canteen_employee(employee_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return CanteenEmployee(**db_employee.__dict__)

@router.get("/", response_model=List[CanteenEmployee])
def get_employees(request: Request, db: Session = Depends(get_db)) -> List[CanteenEmployee]:
    try:
        db_employees = read_db_canteen_employees(db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return [CanteenEmployee(**employee.__dict__) for employee in db_employees]

@router.post("/")
def create_employee(has_access: PROTECTED, request: Request, employee: CanteenEmployeeCreate, db: Session = Depends(get_db)) -> CanteenEmployee:
    db_employee = create_db_canteen_employee(employee, db)
    return CanteenEmployee(**db_employee.__dict__)

@router.put("/{employee_id}")
def update_employee(has_access: PROTECTED, request: Request, employee_id: str, employee: CanteenEmployeeUpdate, db: Session = Depends(get_db)) -> CanteenEmployee:
    try:
        db_employee = update_db_canteen_employee(employee_id, employee, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return CanteenEmployee(**db_employee.__dict__)

@router.delete("/{employee_id}")
def delete_employee(has_access: PROTECTED, request: Request, employee_id: str, db: Session = Depends(get_db)) -> CanteenEmployee:
    try:
        db_employee = delete_db_canteen_employee(employee_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return CanteenEmployee(**db_employee.__dict__)

