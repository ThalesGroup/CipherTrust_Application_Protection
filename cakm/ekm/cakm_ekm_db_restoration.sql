--cakm_ekm_db_restoration.sql script will be used for db restoration from VKM to CAKM and CAKM to CAKM.
--It is committed at github https://github.com/ThalesGroup/CipherTrust_Application_Protection/cakm/ekm

sp_configure 'xp_cmdshell', 1;
GO
RECONFIGURE;
GO

DECLARE @keyname NVARCHAR(128);
DECLARE @provider NVARCHAR(128);
DECLARE @sql NVARCHAR(MAX);
DECLARE @login_cmd NVARCHAR(MAX);
DECLARE @cred_cmd NVARCHAR(MAX);
DECLARE @alter_login NVARCHAR(MAX);
DECLARE @dbname NVARCHAR(100);
DECLARE @backupp VARCHAR(200);
DECLARE @drop_sql NVARCHAR(MAX);
DECLARE @cm_user NVARCHAR(128);
DECLARE @cm_passwd NVARCHAR(128);
DECLARE @login NVARCHAR(128);
DECLARE @cred NVARCHAR(128);
DECLARE @prop_file NVARCHAR(MAX);
DECLARE @prop_file_bkp NVARCHAR(MAX);
DECLARE @prop_path NVARCHAR(MAX);
DECLARE @cakm_prop_change NVARCHAR(MAX);
DECLARE @exec_prop_bkp_cmd NVARCHAR(MAX);
DECLARE @exec_prop_cmd NVARCHAR(MAX);
DECLARE @exec_exec_uuid_cmd NVARCHAR(MAX);
DECLARE @exec_exec_fp_cmd NVARCHAR(MAX);
DECLARE @exec_rm_prop_bkp_cmd NVARCHAR(MAX);

SET @keyname = N'$(keyname)';
SET @provider = N'$(provider)';
SET @dbname = N'$(dbname)';
--SET @backupp = N'$(backupp)';
SET @backupp = N'$(backup)';
SET @cm_user = N'$(cm_user)';
SET @cm_passwd = N'$(cm_passwd)';
SET @login = N'login_' + @keyname;
SET @cred = N'cred_' + @keyname;
SET @prop_path =N'$(prop_path)';
 
IF '$(prop_path)' = ''
BEGIN
    SET @prop_file =N'C:\Program Files\CipherTrust\CAKM For SQLServerEKM\cakm_mssql_ekm.properties';
	SET @prop_file_bkp =N'C:\Program Files\CipherTrust\CAKM For SQLServerEKM\cakm_mssql_ekm.properties_bkp';
	SET @cakm_prop_change =N'C:\Program Files\CipherTrust\CAKM For SQLServerEKM\cakm_ekm_config_change.exe';
	PRINT 'Property file path not provided, So using default path';
END
ELSE
BEGIN
	SET @prop_file = @prop_path + N'\cakm_mssql_ekm.properties';
	SET @prop_file_bkp = @prop_path + N'\cakm_mssql_ekm.properties_bkp';
	SET @cakm_prop_change = @prop_path + N'\cakm_ekm_config_change.exe';
END

SET @exec_prop_bkp_cmd = 'EXEC xp_cmdshell ''copy "' + @prop_file + '" "' + @prop_file_bkp + '"''';
SET @exec_prop_cmd = 'EXEC xp_cmdshell ''copy "' + @prop_file_bkp + '" "' + @prop_file + '"''';
SET @exec_rm_prop_bkp_cmd = 'EXEC xp_cmdshell ''del "' + @prop_file_bkp + '"''';
SET @exec_exec_uuid_cmd = 'EXEC xp_cmdshell ''"' + @cakm_prop_change + '" UUID'';';
SET @exec_exec_fp_cmd = 'EXEC xp_cmdshell ''"' + @cakm_prop_change + '" FP'';';

-- Execute the command
PRINT "Creating the Backup of Property file";
--PRINT @exec_prop_bkp_cmd;
EXEC sp_executesql @exec_prop_bkp_cmd;

PRINT "Setting the VKM_mode to 'yes' in Property file"
--PRINT @exec_exec_uuid_cmd;
EXEC sp_executesql @exec_exec_uuid_cmd;

--PRINT @prop_file;
--PRINT @prop_file_bkp;
--PRINT @cakm_prop_change;

PRINT "Getting Asymmetric Key from Key Manager"

SET @sql = '
CREATE ASYMMETRIC KEY ' + QUOTENAME(@keyname) + '
FROM PROVIDER ' + QUOTENAME(@provider) + '
WITH 
PROVIDER_KEY_NAME = ''' + @keyname + ''',
CREATION_DISPOSITION = OPEN_EXISTING;';

--PRINT @sql;
EXEC sp_executesql @sql;
--SELECT name,thumbprint FROM SYS.ASYMMETRIC_KEYS where name = @keyname;

PRINT "Setting login and cred for the key"

SET @login_cmd = '
CREATE LOGIN ' + QUOTENAME(@login) + '
FROM ASYMMETRIC KEY ' + QUOTENAME(@keyname)+ ';';

--PRINT @login_cmd;
EXEC sp_executesql @login_cmd;

SET @cred_cmd = '
CREATE CREDENTIAL ' + QUOTENAME(@cred) + '
WITH IDENTITY = ''' + @cm_user + ''' ,
SECRET = ''' + @cm_passwd + '''
FOR CRYPTOGRAPHIC PROVIDER ' + QUOTENAME(@provider) + ';';

--PRINT @cred_cmd;
EXEC sp_executesql @cred_cmd;

SET @alter_login = '
ALTER LOGIN' + QUOTENAME(@login) + '
ADD CREDENTIAL' + QUOTENAME(@cred) + ';';

--PRINT @alter_login;
EXEC sp_executesql @alter_login;

SET @drop_sql = '
drop ASYMMETRIC KEY ' + QUOTENAME(@keyname) + ';';

PRINT 'Restoring DB';
	RESTORE DATABASE @dbname FROM DISK = @backupp WITH REPLACE;

IF @@ERROR <> 0
    BEGIN
		PRINT 'Restore Failure';
		PRINT "Dropping Asymmetric Key"
		--PRINT @drop_sql;
		EXEC sp_executesql @drop_sql;
		--SELECT  name,thumbprint FROM SYS.ASYMMETRIC_KEYS where name = @keyname;
		--EXEC xp_cmdshell 'whoami';
		--EXEC xp_cmdshell 'C:\EKM\a.exe';
		
		PRINT "Setting the VKM_mode to 'no' in Property file"
		--PRINT @exec_exec_fp_cmd;
		EXEC sp_executesql @exec_exec_fp_cmd;

		PRINT "Getting Asymmetric Key from Key Manager"
		--PRINT @sql;
		EXEC sp_executesql @sql;
		--SELECT  name,thumbprint FROM SYS.ASYMMETRIC_KEYS where name = @keyname;
		
		PRINT 'Restoring DB';		
		RESTORE DATABASE @dbname FROM DISK = @backupp WITH REPLACE;
		IF @@ERROR <> 0
    		BEGIN
				PRINT 'Restore Failure';
			END
			ELSE
			BEGIN
				PRINT 'Restore successful.';
			END
    END
    ELSE
    BEGIN
        PRINT 'Restore successful.';
    END

PRINT "Restoring the Backup of Property file";
--PRINT @exec_prop_cmd;
EXEC sp_executesql @exec_prop_cmd;

PRINT "Removing the Backup of Property file";
--PRINT @exec_rm_prop_bkp_cmd;
EXEC sp_executesql @exec_rm_prop_bkp_cmd;
