import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "kpi_software_architecture_lab_1_secret_key_2026_secure_ultra_long"
security = HTTPBearer()

def create_token(email: str):
    return jwt.encode({"sub": email}, SECRET_KEY, algorithm="HS256")

def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(auth.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")