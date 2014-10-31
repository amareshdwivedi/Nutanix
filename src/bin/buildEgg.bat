@echo off
echo Creating Egg...
cd ../../
python setup_egg.py bdist_egg --exclude-source-files || if %ERRORLEVEL% neq 0 goto :error 
echo Removing Temporary Files...
rmdir build /s /q || if %ERRORLEVEL% neq 0 goto :error 
rmdir HealthCheck.egg-info /s /q || if %ERRORLEVEL% neq 0 goto :error 
cd src/bin
goto :end

:error
echo Failed with error #%errorlevel%.
exit /b %errorlevel%

:end
echo Egg Created Successfully...