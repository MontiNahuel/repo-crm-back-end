from fastapi import HTTPException, Depends
from schemas.usuarioSchema import UsuarioCreate
from core.security import get_password_hash, verify_password
from repositories.RepositoryUsuario import UsuarioRepository
from schemas.usuarioSchema import LoginRequest
from models.usuario import Usuario

class UsuarioService:
    def __init__(self, repo_usuario: UsuarioRepository = Depends()):
        self.repo_usuario = repo_usuario

    def crear_usuario(self, usuario_in: UsuarioCreate):
        # 1. Validar que el email no exista ya
        usuario_existente = self.repo_usuario.db.query(Usuario).filter(Usuario.email == usuario_in.email).first()
        if usuario_existente:
            raise HTTPException(status_code=400, detail="El email ya está registrado.")

        # 2. Hashear la contraseña ANTES de guardar
        hash_pass = get_password_hash(usuario_in.password)
        
        # 3. Crear el nuevo usuario reemplazando la contraseña por el hash
        nuevo_usuario = UsuarioCreate(
            email=usuario_in.email,
            password=hash_pass,
            rol=usuario_in.rol,
            nombre=usuario_in.nombre,
            apellido=usuario_in.apellido
        )
        
        return self.repo_usuario.create(nuevo_usuario)
    

    def autenticar_usuario(self, email: str, password: str):
        usuario = self.repo_usuario.db.query(Usuario).filter(Usuario.email == email).first()
        if not usuario:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        if not verify_password(password, usuario.password):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        return usuario


    def autenticar_usuario_final(self, login_data: LoginRequest):
        usuario = self.repo_usuario.db.query(Usuario).filter(Usuario.email == login_data.email).first()
        if not usuario:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        if not verify_password(login_data.password, usuario.password):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        return usuario

    def obtener_directorio_colaboradores(self, busqueda: str = None):
        """
        Retorna la lista de colaboradores activos del CRM.
        """
        return self.repo_usuario.obtener_colaboradores(busqueda=busqueda)