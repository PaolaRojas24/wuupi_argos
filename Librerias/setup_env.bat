@echo off
echo ===============================================
echo  Instalando librerías necesarias de Python...
echo ===============================================
echo.

REM Actualizar pip
python -m pip install --upgrade pip

REM Instalar todas las dependencias desde requirements.txt
pip install -r requirements.txt

echo.
echo ===============================================
echo  Instalación completada. Puedes cerrar esta ventana.
echo ===============================================
pause