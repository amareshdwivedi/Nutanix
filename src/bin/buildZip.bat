@echo off
cd ../../
python setup_zip.py bdist_egg --exclude-source-files
echo Build Created...
echo Creating Zip Package...
echo Creating Directories....
mkdir HealthCheck-1.0.0
cd HealthCheck-1.0.0
mkdir eggs
mkdir get_pip
cd ..
echo Copying Required Files.....
copy dist\HealthCheck-1.0.0-py2.7.egg HealthCheck-1.0.0\eggs || if %ERRORLEVEL% neq 0 goto :error 
copy src\libs\*.* HealthCheck-1.0.0\eggs || if %ERRORLEVEL% neq 0 goto :error 
copy get_pip.py HealthCheck-1.0.0\get_pip || if %ERRORLEVEL% neq 0 goto :error 
copy src\bin\install.bat HealthCheck-1.0.0 || if %ERRORLEVEL% neq 0 goto :error 
copy src\bin\uninstall.bat HealthCheck-1.0.0 || if %ERRORLEVEL% neq 0 goto :error 
copy src\bin\README.txt HealthCheck-1.0.0 || if %ERRORLEVEL% neq 0 goto :error 
echo Creating .zip File...
cd src/bin
zip -r ../../HealthCheck-1.0.0.zip ../../HealthCheck-1.0.0 || if %ERRORLEVEL% neq 0 goto :error 
echo Removing Temporary Files.....
cd ../../
rmdir dist /s /q
rmdir build /s /q
rmdir HealthCheck.egg-info /s /q
rmdir HealthCheck-1.0.0 /s /q
cd src/bin
goto :end

:error
echo Failed with error #%errorlevel%.
exit /b %errorlevel%

:end
echo HealthCheck-1.0.0.zip Created Successfully....
