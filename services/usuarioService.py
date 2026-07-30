from fastapi import HTTPException, Depends
from schemas.usuarioSchema import UsuarioCreate
from core.security import get_password_hash, verify_password
from repositories.RepositoryUsuario import UsuarioRepository
from schemas.usuarioSchema import LoginRequest
from models.usuario import Usuario
from models.enums import RolUsuario
import logging

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

    def obtener_todos_los_usuarios(self, skip: int = 0, limit: int = 100):
        """
        Retorna la lista de todos los usuarios registrados en el sistema. (Panel de Administración).
        """
        return self.repo_usuario.get_all(skip=skip, limit=limit)

    async def actualizar_usuario_por_admin(self, usuario_id: int, datos: dict, grupo_service) -> Usuario:
        """
        Actualiza parcialmente los atributos de un usuario.
        Si se actualiza el password, se hashea automáticamente.
        Si el usuario es desactivado o su rol cambia a uno no comercial, se le remueve de su grupo de trabajo en caliente.
        """
        # 1. Buscamos el usuario actual en la DB
        usuario = self.repo_usuario.get(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # 2. Hashear la contraseña si se intenta actualizar
        if "password" in datos and datos["password"]:
            datos["password"] = get_password_hash(datos["password"])
        else:
            datos.pop("password", None) # Evitamos sobrescribir con strings vacíos o None

        # 3. Validar si hay desvinculación de grupo por cambio de rol o de estado activo
        es_activo_anterior = usuario.es_activo
        rol_anterior = usuario.rol
        grupo_id_anterior = usuario.grupo_id

        # 4. Actualizamos en base de datos relacional
        usuario_actualizado = self.repo_usuario.update(usuario_id, datos)

        if usuario_actualizado and grupo_id_anterior:
            # Si el usuario fue desactivado, o si su rol cambió y ya no es VENDEDOR o SUPERVISOR
            nuevo_rol_comercial = usuario_actualizado.rol in [RolUsuario.VENDEDOR, RolUsuario.SUPERVISOR]
            desactivado = es_activo_anterior and not usuario_actualizado.es_activo

            if desactivado or not nuevo_rol_comercial:
                # Removemos de su grupo y del chat sincronizado en MongoDB
                try:
                    await grupo_service.remover_miembro_de_grupo(grupo_id_anterior, usuario_id)
                except Exception as e:
                    # Registramos el error de sincronización de chat pero permitimos continuar la edición de DB
                    logging.getLogger("crm").error(
                        f"⚠️ Error sincronizando remoción de grupo al editar usuario {usuario_id}: {e}"
                    )

        return usuario_actualizado