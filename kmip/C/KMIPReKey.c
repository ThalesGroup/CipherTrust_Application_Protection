/*
 * KMIPReKey.c	
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP ReKey Operation.
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"

void usage(void)
{
    fprintf(stderr, "usage: KMIPReKey conf_file UID [Offset]\n");
    exit(1);
}

I_KS_Result ReKey(I_O_Session *handle_p, char *UID, int offset)
{
    I_KO_AttributeList attrList = NULL;
    I_KS_Result result;
    I_KS_Attribute attributeDate;

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

	if (UID != NULL)
            addUniqueIdentifier(attrList, UID);

        if(offset >= 0)
        {   
           addOffset(attrList,offset);
        }   
        else
        {
           //Uncomment these changes to send date attributes as template attributes
           /*
	   attributeDate.attributeName = "Activation Date";
           attributeDate.attributeValue.index = -1;
           attributeDate.attributeValue.valueType_t = I_KT_AttributeValueType_DateTime;
           attributeDate.attributeValue.value_u.dateTimeVal = time(NULL);
 
           result = I_KC_AddToAttributeList(attrList, &attributeDate);
           attributeDate.attributeName = "Protect Stop Date";
           attributeDate.attributeValue.index = -1;
           attributeDate.attributeValue.valueType_t = I_KT_AttributeValueType_DateTime;
           attributeDate.attributeValue.value_u.dateTimeVal = time(NULL);

           result = I_KC_AddToAttributeList(attrList, &attributeDate);
           attributeDate.attributeName = "Process Start Date";
           attributeDate.attributeValue.index = -1;
           attributeDate.attributeValue.valueType_t = I_KT_AttributeValueType_DateTime;
           attributeDate.attributeValue.value_u.dateTimeVal = time(NULL);

           result = I_KC_AddToAttributeList(attrList, &attributeDate);
           if (result.status != I_KT_ResultStatus_Success)
           {
                printf("Date addition to attribute list failed\n");
                return -1;
           }
           */
        }

        printAttrList(attrList, KMIP_REQUEST);

        // Re key
        result = I_KC_ReKey(*handle_p, attrList,I_KT_ObjectType_SymmetricKey);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_ReKey failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }

        printAttrList(attrList, KMIP_RESPONSE);

    }
    while (0);
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
    char *path, *UID = NULL;
    int argp, offset=-1;
    I_T_RETURN rc;
    I_KS_Result result;

    if (argc < 3)
        usage(); // exit

    argp = 1;
    path = argv[argp++];

    if(strncmp(argv[argp],"null",4) != 0)
      UID = argv[argp];
    argp++;
   
    if (argc == 4)
      offset = atoi(argv[argp]);

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

    result = ReKey(&sess,UID,offset);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("ReKey failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else
        printf("ReKey Successful\n");

    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}

