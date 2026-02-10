# CAKM for Oracle TDE & SQL EKM (Traditional) - License Count Tool

## Overview (Objective)

This tool provides a set of scripts to count the number of running database instances that have the Thales CipherTrust Application Key Management (CAKM) library loaded. This is essential for determining the required license count for traditional "CAKM for Oracle TDE" or "CAKM for SQL EKM".

The tool includes scripts for different operating systems:
*   `cakm_license_count_tool.sh`: For Linux (RHEL), and AIX environments running Oracle Database.
*   `cakm_license_count_tool.ps1`: For Windows environments running Oracle Database or Microsoft SQL Server.

The scripts automatically detect running database instances and inspect their processes to see if the CAKM library is loaded.

## Prerequisites

### Linux/AIX (`cakm_license_count_tool.sh`)

*   **Supported OS**: RHEL (or compatible Linux), AIX.
*   **Supported Database**: Oracle Database.
*   **Permissions**: The script must be executed by a user with sufficient privileges to inspect the processes of the running Oracle instances. This is typically the `root` user or the `oracle` software owner. The script needs to execute commands like `ps`, `lsof` (Linux), and `procldd` (AIX).

### Windows (`cakm_license_count_tool.ps1`)

*   **Supported OS**: Windows Server (with PowerShell).
*   **Supported Databases**: Oracle Database, Microsoft SQL Server.
*   **Permissions**: The script requires administrative privileges to inspect process modules. You must run the script from an elevated PowerShell session (using "Run as Administrator").

## How to Run

### Single Node

A single node refers to a standalone database server that is not part of a cluster.

#### Linux/AIX

1.  Transfer the `cakm_license_count_tool.sh` script to the database server.
2.  Open a terminal session on the server.
3.  Grant execute permissions to the script:
    ```sh
    chmod +x cakm_license_count_tool.sh
    ```
4.  Execute the script. It is recommended to run it as `root` or the `oracle` user.
    ```sh
    ./cakm_license_count_tool.sh
    ```

#### Windows

1.  Transfer the `cakm_license_count_tool.ps1` script to the database server.
2.  Right-click the PowerShell icon and select **"Run as Administrator"** to open an elevated session.
3.  Navigate to the directory where you saved the script.
4.  Execute the script.
    *   To check for **Oracle Database** instances (the default):
        ```powershell
        .\cakm_license_count_tool.ps1
        ```
        or
        ```powershell
        .\cakm_license_count_tool.ps1 -DatabaseType Oracle
        ```
    *   To check for **Microsoft SQL Server** instances:
        ```powershell
        .\cakm_license_count_tool.ps1 -DatabaseType MSSQL
        ```

### RAC Cases (Oracle Real Application Clusters)

For Oracle RAC environments, the script must be executed individually on **each node** of the cluster. The total license count is the sum of the counts from all nodes.

**Example**: In a 4-node RAC cluster, you must run the script on all four nodes. If the script reports a count of 1 on each node, the total license count required for the cluster is 4.

The procedure for running the script on each node is the same as described in the "Single Node" section for the respective operating system.

## Output with Snippet (Example)

### Single Node

#### Linux/AIX - Example Output

In this example, two Oracle instances (`ORCL` and `TESTDB`) are running, but only `ORCL` has the CAKM library loaded.

```
Found running instances. Now checking for CAKM library...
SUCCESS: CAKM library found in PID: 12345 for instance 'ORCL'.
INFO: CAKM library is NOT loaded for instance 'TESTDB'.
-------------------------------------
Total license count required for CAKM for Oracle TDE: 1
-------------------------------------
```

#### Windows - Example Output

Here, the script checks for Oracle instances. The instance `ORCL` is found to be using the CAKM library.

```powershell
Found running database services. Now checking for CAKM library...
----------------------------------------
Checking service: OracleServiceORCL
Checking Oracle instance: ORCL
Instance: ORCL, Process Name: oracle.exe, PID: 5678
SUCCESS: CAKM for Oracle TDE is loaded for instance 'ORCL'.
----------------------------------------
Checking service: OracleServiceTESTDB
Checking Oracle instance: TESTDB
Instance: TESTDB, Process Name: oracle.exe, PID: 8765
INFO: CAKM library is NOT loaded for instance 'TESTDB'.
-------------------------------------------
Total license count required for CAKM for Oracle TDE: 1
-------------------------------------------
```

### RAC Cases

When running in a RAC environment, you will get a separate output from each node. You must manually sum the counts from each node's output to get the total for the cluster.

**Example Scenario**: A 2-node Oracle RAC cluster.

#### Output from Node 1:

```
Found running instances. Now checking for CAKM library...
SUCCESS: CAKM library found in PID: 23456 for instance 'RACDB1'.
-------------------------------------
Total license count required for CAKM for Oracle TDE: 1
-------------------------------------
```

#### Output from Node 2:

```
Found running instances. Now checking for CAKM library...
SUCCESS: CAKM library found in PID: 34567 for instance 'RACDB2'.
-------------------------------------
Total license count required for CAKM for Oracle TDE: 1
-------------------------------------
```

**Total Cluster License Count**: 1 (from Node 1) + 1 (from Node 2) = **2**

