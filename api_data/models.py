from pydantic import BaseModel


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


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
