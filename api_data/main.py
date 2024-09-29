from fastapi import FastAPI, APIRouter
from api_data.routers.canteen_employees import router as canteen_employees_router
from api_data.routers.authentificate import router as authentificate_router
from api_data.routers.core import router as core_router

test_router = APIRouter()

app = FastAPI()

from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API Documentation",
        version="1.0.0",
        description="Cette API permet de gérer les employés de cantine et l'authentification des utilisateurs.",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(canteen_employees_router)

app.include_router(authentificate_router)

app.include_router(core_router)


@app.get("/")
def read_root():
    return "Server is running."


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
