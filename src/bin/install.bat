@echo off
cd ..
python HealthCheck-1.0.0/get_pip/get_pip.py || if %ERRORLEVEL% neq 0 goto :error
cd Scripts
easy_install --quiet -Z ../HealthCheck-1.0.0/eggs/colorama-0.3.2.tar.gz || if %ERRORLEVEL% neq 0 goto :error
easy_install --quiet -Z ../HealthCheck-1.0.0/eggs/pycrypto-2.6.1.tar.gz || if %ERRORLEVEL% neq 0 goto :error
easy_install --quiet -Z ../HealthCheck-1.0.0/eggs/ecdsa-0.11.tar.gz || if %ERRORLEVEL% neq 0 goto :error
easy_install --quiet -Z ../HealthCheck-1.0.0/eggs/paramiko-1.15.1.tar.gz || if %ERRORLEVEL% neq 0 goto :error
easy_install --quiet -Z ../HealthCheck-1.0.0/eggs/prettytable-0.7.2.tar.gz || if %ERRORLEVEL% neq 0 goto :error
easy_install --quiet -Z ../HealthCheck-1.0.0/eggs/requests-2.4.3.tar.gz || if %ERRORLEVEL% neq 0 goto :error
easy_install --quiet -Z ../HealthCheck-1.0.0/eggs/six-1.8.0.tar.gz || if %ERRORLEVEL% neq 0 goto :error
easy_install --quiet -Z ../HealthCheck-1.0.0/eggs/pyvmomi-5.5.0.2014.1.1.tar.gz || if %ERRORLEVEL% neq 0 goto :error
easy_install --quiet -Z ../HealthCheck-1.0.0/eggs/Pillow-2.6.1.tar.gz || if %ERRORLEVEL% neq 0 goto :error
easy_install --quiet -Z ../HealthCheck-1.0.0/eggs/reportlab-3.1.8.tar.gz || if %ERRORLEVEL% neq 0 goto :error
easy_install --quiet -Z --install-dir ../ ../HealthCheck-1.0.0/eggs/HealthCheck-1.0.0-py2.7.egg || if %ERRORLEVEL% neq 0 goto :error
cd ../HealthCheck-1.0.0-py2.7.egg/src/bin
setx PATH "%cd%;%Path%;"
goto :end

:error
echo Failed with error #%errorlevel%.
exit /b %errorlevel%

:end
echo Package Installed Successfully...
echo Switching to Installation Directory...
echo Run the application using healthcheck.bat for windows or healthcheck.sh for linux...