/*
 * NAEVersionedKey.c  
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for NAE Versioned Key.
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "cadp_capi.h"

void usage(void)
{
    fprintf(stderr, "\n  usage: NAEVersionedKey conf_file user passwd OPERATION \n"
            "  conf_file - typically, CADP_CAPI.properties\n"
            "  user - NAE user, user can be in a root domain or in a specific domain. For domain user, specify domain||username\n"
            "  passwd - NAE user's password\n"
            "  OPERATION - CREATE  keyName algo Size [exportable deletable]\n"
            "            - CREATEVERSION  keyName\n"
            "            - PRINT  keyName\n"
            "            - DESTROY  keyName\n"
	    "		 - MODIFYGROUPPERMISSIONS keyName groupname\n"
            "  algo - algorithm name, for example, 'AES'\n"
            "  keyName - name of the key. To create a new versioned key append # to key name. To create a new version of a versioned key don't include #\n"
            "  size - key size in bits\n"
            "  exportable - true/false (optional)\n"
            "  deletable - true/false(optional)\n"
            );
    exit(1);
}

void usage_create(void)
{
    fprintf(stderr, "\n  usage: NAEVersionKey conf_file user passwd CREATE keyName algo size exportable deletable\n"
            "  conf_file - typically, CADP_CAPI.properties\n"
            "  user - NAE user, user can be in a root domain or in a specific domain. For domain user, specify domain||username\n"
            "  passwd - NAE user's password\n"
            "  keyName - name of the versioned key with # appended to it.Example 'abc#'\n"
            "  algo - algorithm name, for example, 'AES'\n"
            "  size - key size in bits\n"
            "  exportable - true/false (optional)\n"
            "  deletable - true/false(optional)\n"

            );
    exit(1);
}

void usage_create_version(void)
{
    fprintf(stderr, "\n  usage: NAEVersionKey conf_file user passwd CREATEVERSION  keyName\n"
            "  conf_file - typically, CADP_CAPI.properties\n"
            "  user - NAE user, user can be in a root domain or in a specific domain. For domain user, specify domain||username\n"
            "  passwd - NAE user's password\n"
            "  keyName - name of the versioned key with no #\n"

            );
    exit(1);
}

void usage_print_versionInfo(void)
{
    fprintf(stderr, "\n  usage: NAEVersionKey conf_file user passwd PRINT  keyName\n"
            "  conf_file - typically, CADP_CAPI.properties\n"
            "  user - NAE user, user can be in a root domain or in a specific domain. For domain user, specify domain||username\n"
            "  passwd - NAE user's password\n"
            "  keyName - name of the versioned key to get the information\n"

            );
    exit(1);
}

void usage_destroy_Key(void)
{
    fprintf(stderr, "\n  usage: NAEVersionKey conf_file user passwd DESTROY keyName\n"
            "  conf_file - typically, CADP_CAPI.properties\n"
            "  user - NAE user, user can be in a root domain or in a specific domain. For domain user, specify domain||username\n"
            "  passwd - NAE user's password\n"
            "  keyName - name of the versioned key ned to delete\n"

            );
    exit(1);
}

void usage_modify(void)
{
    fprintf(stderr, "\n usage: NAEVersionKey conf_file user passwd MODIFYGROUPPERMISSIONS keyName\n"
	    "  conf_file - typically, CADP_CAPI.properties\n"
            "  user - NAE user, user can be in a root domain or in a specific domain. For domain user, specify domain||username\n"
            "  passwd - NAE user's password\n"
            "  keyName - name of the key whose permissions are to be modified\n"
	    "  groupname - group name\n"

	   );
    exit(1);

}

I_T_BOOL str2bool(char *str)
{
    if (str[0] && (str[0] == 'y' || str[0] == 'Y' || str[0] == 't'))
        return I_T_TRUE;
    return I_T_FALSE;
}

void makeupper(char *p)
{
    for (; *p != '\0'; p++)
        *p = toupper(*p);
}

int func_destroy_VersionKey(I_O_Session * handle, char *keyname)
{
    I_T_RETURN rc = I_E_OK;
    rc = I_C_DestroyKey(*handle, keyname);
    if (rc != I_E_OK)
    {
        fprintf(stderr, "rc = %d: %s\n", rc, I_C_GetErrorString(rc));
		fprintf(stderr, "Destroy Failed\n");
    }
	else
		fprintf(stderr, "Destroy Successful\n");
    return rc;
}

int func_printInfo(I_O_Session * handle, char *keyname)
{
    int rc = I_E_OK;

    I_O_AttributeList pSystemAttributeList = NULL, pCustomAttributeList = NULL;
    char *pVersioned;
    char *attributeValue;

    do
    {

        rc = I_C_GetKeyAttributes(*handle,
                keyname,
                &pSystemAttributeList,
                &pCustomAttributeList);
        if (rc != I_E_OK)
        {
            fprintf(stderr, "rc = %d: %s\n", rc, I_C_GetErrorString(rc));
            break;
        }

        rc = I_C_FindInAttributeList(pSystemAttributeList,
                "Versioned", &pVersioned);
        if (rc != I_E_OK)
        {
            fprintf(stderr, "rc = %d: %s\n", rc, I_C_GetErrorString(rc));
            break;
        }

        if (!strncmp(pVersioned, "true", 4))
        {
            fprintf(stderr, "Key(%s) is versioned.\n", keyname);

            rc = I_C_FindInAttributeList(pSystemAttributeList,
                    "KeyVersionNumber", &pVersioned);
            if (rc != I_E_OK)
            {
                fprintf(stderr, "rc = %d: %s\n", rc, I_C_GetErrorString(rc));
                break;
            }

            fprintf(stderr, "Key(%s) version# is %s.\n", keyname, pVersioned);

            rc = I_C_FindInAttributeList(pSystemAttributeList,
                    "NumKeyVersions", &pVersioned);
            if (rc != I_E_OK)
            {
                fprintf(stderr, "rc = %d: %s\n", rc, I_C_GetErrorString(rc));
                break;
            }

            fprintf(stderr, "Key(%s) NumKeyVersions is %s.\n", keyname,
                    pVersioned);

            rc = I_C_FindInAttributeList(pSystemAttributeList,
                    "NumActiveVersions", &pVersioned);
            if (rc != I_E_OK)
            {
                fprintf(stderr, "rc = %d: %s\n", rc, I_C_GetErrorString(rc));
                break;
            }

            fprintf(stderr, "Key(%s) NumActiveVersions is %s.\n", keyname,
                    pVersioned);

            rc = I_C_FindInAttributeList(pSystemAttributeList,
                    "NumRestrictedVersions",
                    &pVersioned);
            if (rc != I_E_OK)
            {
                fprintf(stderr, "rc = %d: %s\n", rc, I_C_GetErrorString(rc));
                break;
            }

            fprintf(stderr, "Key(%s) NumRestrictedVersions is %s.\n", keyname,
                    pVersioned);

            rc = I_C_FindInAttributeList(pSystemAttributeList,
                    "NumRetiredVersions", &pVersioned);
            if (rc != I_E_OK)
            {
                fprintf(stderr, "rc = %d: %s\n", rc, I_C_GetErrorString(rc));
                break;
            }

            fprintf(stderr, "Key(%s) NumRetiredVersions is %s.\n", keyname,
                    pVersioned);

            rc = I_C_FindInAttributeList(pSystemAttributeList,
                    "NumWipedVersions", &pVersioned);
            if (rc != I_E_OK)
            {
                fprintf(stderr, "rc = %d: %s\n", rc, I_C_GetErrorString(rc));
                break;
            }
            if (pVersioned && atoi(pVersioned) >= 0) 
            fprintf(stderr, "Key(%s) NumWipedVersions is %s.\n", keyname,
                    pVersioned);
        }
        else
        {
            fprintf(stderr, "Key(%s) is not versioned.\n", keyname);
        }

        // to find Custom attribute
        /*rc = I_C_FindInAttributeList(pCustomAttributeList,
                "attr_bool", &attributeValue, &attributeType);
        if (rc != I_E_OK)
        {
            fprintf(stderr, "rc = %d: %s\n", rc, I_C_GetErrorString(rc));
            break;
        }
        printf("Custom attribute name = '%s', type = %d.\n", attributeValue, attributeType);
        */
    }    while (0);

    if (pSystemAttributeList != NULL)
        I_C_DeleteAttributeList(pSystemAttributeList);
    if (pCustomAttributeList != NULL)
        I_C_DeleteAttributeList(pCustomAttributeList);

    return 0;
}

int func_create_KeyVersion(I_O_Session * handle, char *keyname)
{
    I_T_RETURN rc = I_E_OK;
    I_O_AttributeList pSystemAttributeList = NULL, pCustomAttributeList = NULL;
    char *pVersioned;

    do
    {

        rc = I_C_GetKeyAttributes(*handle,
                keyname,
                &pSystemAttributeList,
                &pCustomAttributeList);
        if (rc != I_E_OK)
        {
            fprintf(stderr, "rc = %d: %s\n", rc, I_C_GetErrorString(rc));
            break;
        }

        rc = I_C_FindInAttributeList(pSystemAttributeList,
                "Versioned", &pVersioned);
        if (rc != I_E_OK)
        {
            fprintf(stderr, "rc = %d: %s\n", rc, I_C_GetErrorString(rc));
            break;
        }

        if (!strncmp(pVersioned, "true", 4))
        {
            rc = I_C_SetKeyParameter(*handle,
                    keyname,
                    I_T_KeyVersion,
                    I_T_KeyParameter_Version_Increment);
            if (rc != I_E_OK)
            {
                I_T_RETURN err;
                I_C_GetLastError(*handle, &err);
                fprintf(stderr, "I_C_SetKeyParameters() returned %d (%s)\n",
                        rc, I_C_GetErrorString(err));
                break;
            }
            fprintf(stderr, "Create Key Version Successful\n");
        }
        else
        {
            fprintf(stderr,
                    "Key is not versioned. can't create a versioned key\n");
        }
        
    } while (0);

    if (pSystemAttributeList != NULL)
        I_C_DeleteAttributeList(pSystemAttributeList);
    if (pCustomAttributeList != NULL)
        I_C_DeleteAttributeList(pCustomAttributeList);

    return rc;
}

int func_create_Key(I_O_Session * handle, char *name, char *algo, char *size, I_T_BOOL exportable, I_T_BOOL deletable)
{
    I_T_RETURN rc = I_E_OK;

    I_O_KeyInfo keyinfo;
    rc = I_C_CreateKeyInfo(algo, atoi(size), exportable, deletable,
            &keyinfo);
    if (rc != I_E_OK)
    {
        fprintf(stderr, "rc = %d: %s\n", rc, I_C_GetErrorString(rc));
        return rc;
    }

    rc = I_C_CreateKey(*handle, name, keyinfo, NULL);
    if (rc != I_E_OK)
    {
        fprintf(stderr, "rc = %d: %s\n", rc, I_C_GetErrorString(rc));\
		fprintf(stderr, "Create Key Failed\n");
    }
	else
		fprintf(stderr, "Create Key Successful\n");

    I_C_DeleteKeyInfo(keyinfo);
    return rc;

}



int func_modify(I_O_Session * handle,const I_T_CHAR *keyname,const I_T_CHAR *groupname)
{


	I_T_RETURN rc = I_E_OK;
	I_O_GroupList grouplist;
  	rc = I_C_CreateGroupListObject (&grouplist);
    	if (rc != I_E_OK)
   	 {
        	fprintf (stderr, "I_C_CreateGroupListObject() rc = %d\n", rc);
   	 }	
   
        rc = I_C_AddGroupToObject (grouplist,groupname,
                                   I_T_Permission_Encrypt|I_T_Permission_Decrypt|I_T_Permission_Export);
        if (rc != I_E_OK)
        {
            fprintf (stderr, "I_C_AddGroupToObject() rc = %d\n", rc);
        }


	rc = I_C_ModifyGroupPermissions(* handle, keyname, grouplist);
	 if (rc != I_E_OK)
   	 {
        	fprintf(stderr, "rc = %d: %s\n", rc, I_C_GetErrorString(rc));
                fprintf(stderr, "Modify group permissions failed\n");
   	 }
        else
                fprintf(stderr, "Modify group permission successful\n");

	 if (grouplist)
         I_C_DeleteGroupListObject (grouplist);
 
	return rc;


}


enum operationType_t
{
    CREATE,
    CREATEVERSION,
    PRINT,
    DESTROY,
    MODIFYGROUPPERMISSIONS,
    NOTVALID
} operationType;

int main(int argc, char **argv)
{
    I_O_Session sess;
    char *path, *user, *pass, *keyname, *algo, *size, *operation, *groupname;
    int argp;
    I_T_RETURN rc = I_E_OK;
    I_T_BOOL exportable, deletable;
    exportable = deletable = I_T_FALSE;

    operationType = NOTVALID;
    if (argc < 5)
        usage(); // exit

    argp = 1;
    path = argv[argp++];
    user = argv[argp++];
    pass = argv[argp++];
    operation = argv[argp++];
    makeupper(operation);

    if (strcmp(operation, "CREATE") == 0)
    {
        if (argc < 8)
            usage_create(); // exit
        else
        {
            keyname = argv[argp++];
	    if(strncmp(keyname,"null",4)==0)
	    keyname = NULL;
            algo = argv[argp++];
            size = argv[argp++];
            operationType = CREATE;
        }
        if (argc > 9)
        {
            exportable = str2bool(argv[argp++]);
            deletable = str2bool(argv[argp++]);
        }
        else if (argc == 9)
        {
            exportable = str2bool(argv[argp++]);
        }

    }
    else if (strcmp(operation, "CREATEVERSION") == 0)
    {
        if (argc < 6)
            usage_create_version(); // exit
        else
        {
            keyname = argv[argp++];
            operationType = CREATEVERSION;
        }
    }
    else if (strcmp(operation, "PRINT") == 0)
    {
        if (argc < 6)
            usage_print_versionInfo(); // exit
        else
        {
            keyname = argv[argp++];
            operationType = PRINT;
        }
    }
    else if (strcmp(operation, "DESTROY") == 0)
    {
        if (argc < 6)
            usage_destroy_Key(); // exit
        else
        {
            keyname = argv[argp++];
            operationType = DESTROY;
        }
    }
   	 else if (strcmp(operation, "MODIFYGROUPPERMISSIONS") == 0)
    {
        if (argc < 7)
            usage_modify(); // exit
        else
        {
            keyname = argv[argp++];
            groupname = argv[argp++];
            operationType = MODIFYGROUPPERMISSIONS;
        }
    }





	 else
    {
        printf("InValid Operation");
        return 0;
    }

    rc = I_C_Initialize(I_T_Init_File, path);

    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_Initialize error: %s\n",
                I_C_GetErrorString(rc));
        return rc;
    }
    rc = I_C_OpenSession(&sess, I_T_Auth_Password, user, pass);
    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_OpenSession error: %s\n",
                I_C_GetErrorString(rc));
        I_C_Fini();
        return rc;
    }
    switch (operationType)
    {
        case CREATE:
        {
            func_create_Key(&sess, keyname, algo, size, exportable, deletable);
            break;
        }
        case CREATEVERSION:
        {
            func_create_KeyVersion(&sess, keyname);
            break;
        }
        case PRINT:
        {
            func_printInfo(&sess, keyname);
            break;
        }
        case DESTROY:
        {
            func_destroy_VersionKey(&sess, keyname);
            break;
        }
	case MODIFYGROUPPERMISSIONS:
	{
	    func_modify(&sess, keyname, groupname);
	    break;
	}
    }
    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}
