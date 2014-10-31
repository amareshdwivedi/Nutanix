@echo off
cd ..
python __main__.pyc %* || if %ERRORLEVEL% neq 0 goto :error
cd bin
goto :end

:error
echo Failed with error #%errorlevel%.
exit /b %errorlevel%

:end