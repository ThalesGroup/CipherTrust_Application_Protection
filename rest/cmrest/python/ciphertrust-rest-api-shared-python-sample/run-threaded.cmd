@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%src;%PYTHONPATH%"
python -m ciphertrust_rest_api_shared_sample.threaded_demo_main %*
exit /b %ERRORLEVEL%