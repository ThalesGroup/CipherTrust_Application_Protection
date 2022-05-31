/*
 * NAEKeyManagement.c  
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for NAE Key Management.
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "cadp_capi.h"

void hexprint(const char* label, const I_T_BYTE *in, int len)
{
    int i;
    fprintf(stdout, "%s:", label);
    for(i = 0; i < len && i < len; i++)
    {
        fprintf(stdout,"%2.2x ",(unsigned char)in[i]);
    }
    fprintf(stdout,"\n");
}

void usage(void)
{
    fprintf(stderr, "\n  usage: NAEKeyManagement conf_file user passwd OPERATION \n"
            "  conf_file - typically, CADP_CAPI.properties\n"
            "  user - NAE user, user can be in a root domain or in a specific domain. For domain user, specify domain||username\n"
            "  passwd - NAE user's password\n"
            "  OPERATION - CREATE keyName algo Size CurveID(for ECC keys) [exportable deletable] \n"
            "            - EXPORT keyName keytype [format] \n"
            "  algo - algorithm name, for example, 'AES'\n"
            "  keyName - name of the key. To create a new versioned key append # to key name. To create a new version of a versioned key don't include #\n"
            "  size - key size in bits\n"
	    "  curveID - ID of the elliptic curve (valid only for ECC keys)\n"
            "  exportable - true/false (optional)\n"
            "  deletable - true/false(optional)\n"
            "  keytype - 1 for public/ 2 for private/ 3 for Symmmetric Key\n"
            "  format - 1 for PEM-SEC1/ 2 for PEM-PKCS#8 .This is mandatory parameter for private key type\n"
            );
    exit(1);
}

void usage_create(void)
{
    fprintf(stderr, "\n  usage: NAEKeyManagement conf_file user passwd CREATE keyName algo size curveID(for ECC keys) exportable deletable\n"
            "  conf_file - typically, CADP_CAPI.properties\n"
            "  user - NAE user, user can be in a root domain or in a specific domain. For domain user, specify domain||username\n"
            "  passwd - NAE user's password\n"
            "  keyName - name of the versioned key with # appended to it.Example 'abc#'\n"
            "  algo - algorithm name, for example, 'AES'\n"
            "  size - key size in bits\n"
	    "  curveID - ID of the elliptic curve e.g. secp224k1,brainpoolP256r1(valid only for ECC keys)\n"
            "  exportable - true/false (optional)\n"
            "  deletable - true/false(optional)\n"

            );
    exit(1);
}

void usage_export(void)
{
    fprintf(stderr, "\n  usage: NAEKeyManagement conf_file user passwd EXPORT keyName keytype [format] \n"
            "  conf_file - typically, CADP_CAPI.properties\n"
            "  user - NAE user, user can be in a root domain or in a specific domain. For domain user, specify domain||username\n"
            "  passwd - NAE user's password\n"
            "  keyName - name of the key\n"
            "  keytype - 1 for public key/ 2 for private key/ 3 for Symmmetric Key\n"
            "  format - 1 for PEM-SEC1/ 2 for PEM-PKCS#8 .This is mandatory parameter for private key type\n"
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


int func_create_Key(I_O_Session * handle, char *name, char *algo, char *size, I_T_BOOL exportable, I_T_BOOL deletable, int curveID )
{
    I_T_RETURN rc = I_E_OK;
    I_O_KeyInfo keyinfo = NULL;
    I_T_KeyDetails keyDetails={0} ;
    keyDetails.curve_eq = curveID;

    if( !strncmp(algo ,"EC",2))
    rc = I_C_CreateKeyInfo_KeyDetails(algo, atoi(size), exportable, deletable,               
            &keyinfo, &keyDetails);
    else
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

int func_export_key(I_O_Session * handle, char *keyname, int keytype, int format)
{
    I_T_RETURN rc = I_E_OK;
    char *pVersioned;
    I_T_CHAR *pkeyBytes = NULL;
    I_T_UINT keyBytesLen;

    do
    {
        rc = I_C_ExportKey(*handle,keyname,keytype,format,&pkeyBytes,&keyBytesLen);
        if (rc != I_E_OK)
        {
            fprintf(stderr, "I_C_ExportKey error: %s\n",
                I_C_GetErrorString(rc));
            break;
        }
        hexprint ("keybytes:", pkeyBytes,keyBytesLen);
    } while (0);

    if (pkeyBytes != NULL)
        I_C_Free (pkeyBytes);

    return rc;
}

enum operationType_t
{
    CREATE,
    EXPORT,
    NOTVALID
} operationType;

int main(int argc, char **argv)
{
    I_O_Session sess;
    char *path, *user, *pass, *keyname, *algo=NULL, *size, *operation, *groupname,*curvename = NULL;
    int argp,curveID = -1;
    I_T_RETURN rc = I_E_OK;
    I_T_BOOL exportable, deletable;
    int keytype = 0;
    int format = 0;

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
                usage_create();

	    keyname = argv[argp++];
	    if(strncmp(keyname,"null",4)==0)
	            keyname = NULL;
            algo = argv[argp++];
	    
            if((!strncmp(algo, "EC",2) && (argc <9))|| (strncmp(algo,"EC",2) && (argc < 8)))
            	usage_create(); // exit
            
	    size = argv[argp++];
	    
	    if(!strncmp(algo,"null",4))
	    {
		fprintf(stderr,"Invalid Algorithm\n");
                exit(0);
	    }
	    if (!strncmp(algo,"EC",2))
	    {
		curvename = argv[argp++];	
	    }    
            operationType = CREATE;
        
        if ( (!strncmp(algo,"EC",2)  && argc > 10) || (strncmp(algo,"EC",2)) && argc > 9)
        {
            exportable = str2bool(argv[argp++]);
            deletable = str2bool(argv[argp++]);
        }
        else if ((!strncmp(algo,"EC",2) && argc == 10) ||(strncmp(algo,"EC",2))&& (argc == 9))
        {
            exportable = str2bool(argv[argp++]);
        }

    }
    else if (strcmp(operation, "EXPORT") == 0)
    {
        if (argc < 7)
            usage_export(); // exit
        else
        {
            operationType = EXPORT;
            keyname = argv[argp++];
            keytype = atoi(argv[argp++]);
        }
        if ((keytype == 2) && (argc != 8))
            usage_export(); // exit
            
        if (argc == 8)
        {
            format = atoi(argv[argp++]);
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
	
    	if(!strncmp(algo ,"EC",2))
      	{
	 if (!strncmp(curvename, "secp224k1", 9))
           curveID  = I_T_secp224k1;
        else if (!strncmp(curvename, "secp224r1", 9))
            curveID  = I_T_secp224r1;
        else if (!strncmp(curvename, "secp256k1", 9))
            curveID  = I_T_secp256k1;
        else if (!strncmp(curvename, "secp384r1", 9))
            curveID  = I_T_secp384r1;
        else if (!strncmp(curvename, "secp521r1", 9))
            curveID  = I_T_secp521r1;
        else if (!strncmp(curvename, "prime256v1", 9))
            curveID  = I_T_prime256v1;
        else if (!strncmp(curvename, "brainpoolP224r1", 15))
            curveID = I_T_brainpoolP224r1;
        else if (!strncmp(curvename, "brainpoolP224t1", 15))
            curveID =  I_T_brainpoolP224t1;
        else if (!strncmp(curvename, "brainpoolP256r1", 15))
            curveID  = I_T_brainpoolP256r1;
        else if (!strncmp(curvename, "brainpoolP256t1", 15))
            curveID  = I_T_brainpoolP256t1;
        else if (!strncmp(curvename, "brainpoolP384r1", 15))
            curveID = I_T_brainpoolP384r1;
        else if (!strncmp(curvename, "brainpoolP384t1", 15))
            curveID  = I_T_brainpoolP384t1;
        else if (!strncmp(curvename, "brainpoolP512r1", 15))
            curveID  = I_T_brainpoolP512r1;
        else if (!strncmp(curvename, "brainpoolP512t1", 15))
            curveID  = I_T_brainpoolP512t1;
        else 
	    {
		curveID = invalidID;
		fprintf(stderr,"Invalid curveID\n");
		exit(0);
	    }
   	 }
		
         func_create_Key(&sess, keyname, algo, size, exportable, deletable, curveID);
            break;
        }
        case EXPORT:
        {
            rc = func_export_key(&sess, keyname, keytype, format);
            break;
        }
    }
    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}
