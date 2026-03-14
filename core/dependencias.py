from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from core.security import SECRET_KEY, ALGORITHM
from database import get_db
from models.usuario import Usuario
from models.enums import RolUsuario

# ⚠️ IMPORTANTE: Esta URL debe ser la ruta exacta de tu endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/login")

def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    excepcion_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Desencriptamos el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id_str: str = payload.get("sub")
        
        if usuario_id_str is None:
            raise excepcion_credenciales
            
        usuario_id = int(usuario_id_str)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise excepcion_credenciales

    # Buscamos al usuario en la DB para confirmar que sigue existiendo y está activo
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if usuario is None or not usuario.es_activo: # Asegúrate de usar 'es_activo' o el nombre que le diste
        raise excepcion_credenciales

    return usuario


def requerir_rol_admin(
    # Fíjate cómo esta función LLAMA a tu guardia anterior automáticamente
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Verifica que el usuario autenticado tenga el rol de ADMIN.
    Si no lo tiene, lanza un error 403 Forbidden.
    """
    # Verificamos si el rol no es el de Administrador
    if usuario_actual.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=403, # 403 significa "Prohibido / Sin Permisos"
            detail="No tienes los privilegios necesarios para realizar esta acción."
        )
    
    # Si es ADMIN, lo dejamos pasar al endpoint
    return usuario_actual