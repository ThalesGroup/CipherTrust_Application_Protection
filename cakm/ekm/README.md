README.md

This SQL script (cakm_ekm_db_restoration.sql) and a C executable (cakm_ekm_config_change.exe) will be used to automatically restore the encrypted VKM/CAKM  databases to CAKM without any customer environment downtime.
This is a sample script and you can update the same as per your requirement.

Perform the following steps to run SQL script (`cakm_ekm_db_restoration.sql`):

1. Copy `cakm_ekm_db_restoration.sql` and `cakm_ekm_config_change.exe` from github.

2. Place these files on the location where CAKM is installed.<br>For example, `C:\Program Files\CipherTrust\CAKM For SQLServerEKM`

3. Open the command prompt and navigate to the path where CAKM is installed.

4. Below is the sample command to restore the encrypted backup file:

	**Sample**

		#!yaml
		sqlcmd -S <Hostname> -d <master> -U <sa> -P <password> -i <cakm_ekm_db_restoration.sql> -v keyname=<"DSM_VKM_Migration_Key_2_2"> provider=<"thales_provider"> dbname=<"VKM_DB"> backup=<"C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\Backup\VKM_Migration_Testing.bak"> cm_user=<"cm_username"> cm_passwd=<"cm_password"> prop_path=""
 
	Where, 
	
	* (-S): SQL Server name
	
	* (-d): Database name 

	* (-U): SQL Login ID 

	* (-P): SQL Login ID password 
	
	* (-i): SQL script
	
	* (-v): provide custom arguments as key="value" pair as specified in above command example:
	
	* keyname: Keyname present on CipherTrust Manager
	
	* provider: Crytographic provider
	
	* backup: DB backup file with complete path
	
	* dbname: database name with which backup will be restored
	
	* cm_user: CipherTrust login user name
	
	* cm_passwd: CipherTrust login password
	
	* prop_path=""
		* If you want to provide a path to this parameter, the path should be the location where the **CAKM for MSSQL EKM** is installed. For example, prop_path=`"C:\Program Files\CipherTrust\CAKM For SQLServerEKM\"`.
		
		* If an empty value is provided in `prop_path`, then script will use the default path to find the property file and executable file(`cakm_ekm_config_change.exe`).<br>Default path: `C:\Program Files\CipherTrust\CAKM For SQLServerEKM\`.
		
	!!! note
		
		In the above sample command, the SQL script (cakm_ekm_db_restoration.sql) is provided with `-i` option as an input to run  `sqlcmd` utility.

At the end of script execution, 

* If the encrypted database backup is successfully restored, a **"Restore successful"** message is displayed.

* If the encrypted database backup restore fails, **"Restore failed. Error:`<Detailed Error Message>`"** is displayed.

Please refer to [Thalesdoc](https://thalesdocs.com/ctp/con/cakm/cakm-mssql-ekm/alpha-8.6.1/admin/cakm_mssql_ekm_advanced_topics/cakm_vkm_db_restore/index.html) for more information.