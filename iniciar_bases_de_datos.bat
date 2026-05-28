@echo off
title CRM Databases Orchestrator
color 0B
cls

echo ==========================================================
echo           CRM DATABASES ORCHESTRATOR (DOCKER)
echo ==========================================================
echo.
echo [*] Verificando el estado del servicio de Docker...

:: Verificamos si docker está disponible y corriendo
docker info >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Docker Desktop no esta activo o no esta instalado.
    echo [INFO] Por favor, abre Docker Desktop y vuelve a intentar.
    echo.
    pause
    exit /b
)

echo [OK] Docker se esta ejecutando.
echo.
echo [*] Inicializando MySQL y MongoDB en contenedores de fondo...
echo.

:: Levantamos las bases de datos en segundo plano
docker compose up -d

if %errorlevel% equ 0 (
    color 0A
    echo.
    echo ==========================================================
    echo  [EXITO] bases de datos levantadas correctamente
    echo ==========================================================
    echo   - MySQL:   Port 3306  (db: inventario_db)
    echo   - MongoDB: Port 27017 (db: crm_colaboradores_chat)
    echo.
    echo  Nota: SQLAlchemy y MongoDB crearan las tablas e indices
    echo        automaticamente al iniciar tu servidor FastAPI.
    echo ==========================================================
) else (
    color 0C
    echo.
    echo [ERROR] Hubo un problema al intentar levantar docker-compose.
)
echo.
pause
