from fastapi import HTTPException, status, Depends
from jose import JWTError, jwt
import os
from pydantic import BaseModel
import pickle
from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import date
from sqlalchemy import create_engine


async def has_access(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    token = credentials.credentials
    load_dotenv()
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ALGORITHM = "HS256"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print(f"Decoded payload: {payload}")
    except JWTError:
        raise credentials_exception
    if username == "admin":
        return True
    else:
        raise credentials_exception


class SinglePredictionInput(BaseModel):
    id_jour: date


class SinglePredictionOutput(BaseModel):
    prediction: float


def predict_single(loaded_model, df_to_predict):
    prediction = loaded_model.predict(df_to_predict)
    return prediction[0]


def get_model(run_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, "api_model", f"{run_name}.pkl")
    with open(model_path, "rb") as file:
        loaded_model = pickle.load(file)
    return loaded_model


def generate_token(to_encode):
    load_dotenv()
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ALGORITHM = "HS256"
    to_encode_dict = {"sub": to_encode}
    print(
        "DEBUG: SECRET_KEY =", repr(SECRET_KEY)
    )  # Affichez la clé secrète à des fins de débogage
    encoded_jwt = jwt.encode(to_encode_dict, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


if __name__ == "__main__":
    print(generate_token("admin"))
