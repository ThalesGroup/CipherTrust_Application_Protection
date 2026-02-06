#!/bin/bash
#
# Script to find out license count for Oracle DB instances with the CAKM library loaded.
# Compatible with RHEL and AIX.
#

# --- Configuration ---
# The script will search for a library file containing this pattern.
CAKM_LIB_PATTERN="libcadp_pkcs11"

# Initialize counter
instance_count=0
os_type=$(uname)

# Find all running pmon processes, which indicate a running Oracle instance.
# The output of `ps` is filtered to get the SID.
# The awk command extracts the last column (ora_pmon_SID) and then substr removes "ora_pmon_".
# pmon_processes=$(ps -ef | grep -o 'ora_pmon_[^ ]*' | sed 's/ora_pmon_//' | sort -u) # not working on AIX
pmon_processes=$(ps -ef | grep ora_pmon_ | grep -v grep | sed -n 's/.*ora_pmon_//p' | sort -u)

if [ -z "$pmon_processes" ]; then
    echo "No running Oracle instances found (pmon process not detected)."
    exit 0
fi

echo "Found running instances. Now checking for CAKM library..."

# Loop through each discovered SID
for sid in $pmon_processes; do
    # Guard against empty SID which can cause a grep error
    # Also skip if SID is "//" or "[^" which can happen with malformed ps output
    if [ -z "$sid" ] || [ "$sid" = "//" ] || [[ "$sid" =~ ^\[\^ ]]; then
        continue
    fi

    # Get all Process IDs (PIDs) for the current SID.
    # The CAKM library might be loaded by any of the instance's background processes.
    pids=$(ps -ef | grep "[o]ra_.*_${sid}$" | awk '{print $2}')

    if [ -z "$pids" ]; then
        continue
    fi

    library_found=0
    # Loop through each process associated with the SID
    for pid in $pids; do
        # Platform-specific check for the loaded library
        if [ "$os_type" = "Linux" ]; then
            # Use lsof on Linux (RHEL)
            if lsof -p "$pid" 2>/dev/null | grep -iq "$CAKM_LIB_PATTERN"; then
                echo "SUCCESS: CAKM library found in PID: ${pid} for instance '${sid}'."
                library_found=1
                break # Found it, no need to check other PIDs for this SID
            fi
        elif [ "$os_type" = "AIX" ]; then
            # Use procldd on AIX. Requires appropriate permissions.
            if procldd "$pid" 2>/dev/null | grep -iq "$CAKM_LIB_PATTERN"; then
                echo "SUCCESS: CAKM library found in PID: ${pid} for instance '${sid}'."
                library_found=1
                break # Found it, no need to check other PIDs for this SID
            fi
        elif [ "$os_type" = "SunOS" ]; then
            # Use pldd on Solaris.
            if pldd "$pid" 2>/dev/null | grep -iq "$CAKM_LIB_PATTERN"; then
                echo "SUCCESS: CAKM library found in PID: ${pid} for instance '${sid}'."
                library_found=1
                break # Found it, no need to check other PIDs for this SID
            fi
        else
            echo "Unsupported OS: ${os_type}. Cannot check for loaded libraries."
            continue 2 # Continue outer loop
        fi
    done

    if [ $library_found -eq 1 ]; then
        instance_count=$((instance_count + 1))
    else
        echo "INFO: CAKM library is NOT loaded for instance '${sid}'."
    fi
done

echo "-------------------------------------"
echo "Total license count required for CAKM for Oracle TDE: ${instance_count}"
echo "-------------------------------------"
exit 0
