/*
 * KMIPRegisterTemplate.c	
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP Register Operation with Template
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"

void usage(void)
{
    fprintf(stderr, "usage: KMIPRegisterTemplate conf_file [templatename1] [templatename2]\n");
    exit(1);
}

I_KS_Result RegisterTemplate(I_O_Session *handle_p, char *templatename1, char* templatename2)
{
    I_KO_AttributeList attrList = NULL;
    I_KS_Object managedObject;
    char *uniqueID_p = NULL;
    I_KS_Result result;

    do
    {

        // create the attribute list
        result = I_KC_CreateAttributeList(&attrList, NULL);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }


        addName(attrList, templatename1, templatename2);
        addObjectGroup(attrList);
        addContactInformation(attrList);
        addCustomAttributes(attrList);
        addCryptographicLength(attrList);
        addCryptographicAlgorithm(attrList);
        addCryptographicUsageMask(attrList);

        printAttrList(attrList, KMIP_REQUEST);

        managedObject.objectType_t = I_KT_ObjectType_Template;
        // register the key
        result = I_KC_Register(*handle_p, attrList, &managedObject);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_Register failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }

        printAttrList(attrList, KMIP_RESPONSE);

    } while (0);
    // delete the attribute list
    if (attrList != NULL)
    {
        I_KS_Result result1;
        result1 = I_KC_DeleteAttributeList(attrList);
        if (result1.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_DeleteAttributeList failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result1), I_KC_GetResultReasonString(result1));
        }
    }

    return result;
}

int main(int argc, char **argv)
{

    I_O_Session sess;
    I_T_RETURN rc;
    char *path, *templatename1 = NULL, *templatename2 = NULL;
    int argp;
    I_KS_Result result;

    if (argc < 2)
        usage(); // exit

    argp = 1;
    path = argv[argp++];

    if (argc >= 3)
        templatename1 = argv[argp];
    if (argc == 4)
        templatename2 = argv[++argp];

    rc = I_C_Initialize(I_T_Init_File, path);

    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_Initialize error: %s\n",
                I_C_GetErrorString(rc));
        return rc;
    }

    rc = I_C_OpenSession(&sess, I_T_Auth_NoPassword, NULL, NULL);

    if (rc != I_E_OK)
    {
        fprintf(stderr, "I_C_OpenSession error: %s\n",
                I_C_GetErrorString(rc));
        I_C_Fini();
        return rc;
    }

    result = RegisterTemplate(&sess, templatename1, templatename2);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("RegisterTemplate failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else
        printf("RegisterTemplate Successful\n");
    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}

