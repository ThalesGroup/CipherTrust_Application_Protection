@echo off
SET var=""
SET VKMDLL=""
SET VKMDLL32=C:\Program Files (x86)\Vormetric\DataSecurityExpert\agent\pkcs11\bin\vorekm.dll
SET VKMDLL64=C:\Program Files\Vormetric\DataSecurityExpert\agent\pkcs11\bin\vorekm.dll
SET VKMDLL='%VKMDLL32%'
IF not exist "%VKMDLL32%" (
    SET VKMDLL='%VKMDLL64%'
    IF not exist "%VKMDLL64%" (
        ECHO.
        ECHO ErrCode=2, Failed to Load Cryptography Provider !
        @echo on
        EXIT /B
    )
)

IF ["%~1"]==[""] (
    SET INSTNAME=
) ELSE (
    SET INSTNAME=-S %1   
    ECHO SQL Instance: %1 	
)

SET command=sqlcmd %INSTNAME% -Q "CREATE CRYPTOGRAPHIC PROVIDER ga5tEwq52t6EsD#18754 FROM FILE = %VKMDLL%;"
sqlcmd %INSTNAME% -Q "sp_configure 'show advanced options', 1; RECONFIGURE" > NUL 2>&1
sqlcmd %INSTNAME% -Q "sp_configure 'EKM provider enabled', 1; RECONFIGURE" > NUL 2>&1
%command% > pingtemp.txt 2>&1
FOR /F "delims=" %%c in (pingtemp.txt) do set var=%%c
del pingtemp.txt
IF "x"""=="x%var%" (
    TIMEOUT 2 > NUL
    %command% > pingtemp.txt 2>&1
    FOR /F "delims=" %%c in (pingtemp.txt) do set var=%%c
    del pingtemp.txt
)
set STR1=already exists
set STR2=Error: Microsoft ODBC Driver
CALL SET keyRemoved1=%%var:%STR1%=%%
CALL SET keyRemoved2=%%var:%STR2%=%%
IF NOT "x%keyRemoved1%"=="x%var%" (
    ECHO.
    ECHO ErrCode=0, Health Check Success !
    sqlcmd %INSTNAME% -Q "DROP CRYPTOGRAPHIC PROVIDER ga5tEwq52t6EsD#18754"> NUL 2>&1
) ELSE (
    IF NOT "x%keyRemoved2%"=="x%var%" (
        ECHO. 
        ECHO ErrCode=1, SQL Server Connection Failed !
    ) ELSE (
        ECHO.
        ECHO ErrCode=2, Failed to Load Cryptography Provider !
    )
)
@echo on
