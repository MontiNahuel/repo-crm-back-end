from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone

# Configuramos bcrypt, que es el algoritmo estándar y más seguro actualmente
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Toma una contraseña en texto plano y devuelve el hash encriptado."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña plana coincide con el hash guardado en la DB."""
    return pwd_context.verify(plain_password, hashed_password)

SECRET_KEY = "tu_super_clave_secreta_indescifrable_crm_2026" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 12000000

def crear_token_acceso(data: dict):
    to_encode = data.copy()
    
    # Definimos en qué momento exacto caduca este token
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Fabricamos el token usando la librería PyJWT
    token_codificado = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token_codificado