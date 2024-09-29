# main.py script
from fastapi import FastAPI, Depends
import api_model.predict
from fastapi import FastAPI
from fastapi.params import Depends
from api_model.utils import has_access, generate_token
import sys
import uvicorn
from api_model.openapi import custom_openapi

app = FastAPI()
app.openapi = custom_openapi

# routes
PROTECTED = [Depends(has_access)]

app.include_router(api_model.predict.router, prefix="/predict", dependencies=PROTECTED)

if __name__ == "__main__":
    print(generate_token("admin"))
    args = sys.argv
    port = 8000
    if len(args) > 1:
        port_string = args[1]
        port = int(port_string)

    uvicorn.run(app, host="0.0.0.0", port=port)
