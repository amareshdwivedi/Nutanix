@echo off
cd ../Scripts
pip uninstall HealthCheck -y || if %ERRORLEVEL% neq 0 goto :error 
pip uninstall reportlab -y || if %ERRORLEVEL% neq 0 goto :error 
pip uninstall Pillow -y || if %ERRORLEVEL% neq 0 goto :error 
pip uninstall pyvmomi -y || if %ERRORLEVEL% neq 0 goto :error 
pip uninstall six -y || if %ERRORLEVEL% neq 0 goto :error 
pip uninstall requests -y || if %ERRORLEVEL% neq 0 goto :error 
pip uninstall prettytable -y || if %ERRORLEVEL% neq 0 goto :error 
pip uninstall paramiko -y || if %ERRORLEVEL% neq 0 goto :error 
pip uninstall ecdsa -y || if %ERRORLEVEL% neq 0 goto :error 
pip uninstall pycrypto -y || if %ERRORLEVEL% neq 0 goto :error 
pip uninstall colorama -y || if %ERRORLEVEL% neq 0 goto :error 
cd ../HealthCheck-1.0.0
goto :end

:error
echo Failed with error #%errorlevel%.
exit /b %errorlevel%

:end
echo Package Un-installed Successfully...