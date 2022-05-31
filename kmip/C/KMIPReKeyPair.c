/*
 * KMIPReKeyPair.c	
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP ReKeyPair Operation.
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"

void usage(void)
{
    fprintf(stderr, "usage: KMIPReKeyPair conf_file Private_Key_UID [Offset]\n");
    exit(1);
}

I_KS_Result AddKeyAttributes(I_KO_AttributeList attrList)
{
    
         I_KS_Attribute attributeDate;
         I_KS_Result result;

            attributeDate.attributeName = "Activation Date";
           attributeDate.attributeValue.index = -1;
           attributeDate.attributeValue.valueType_t = I_KT_AttributeValueType_DateTime;
           attributeDate.attributeValue.value_u.dateTimeVal = time(NULL);

           result = I_KC_AddToAttributeList(attrList, &attributeDate);
           if (result.status != I_KT_ResultStatus_Success)
           {
                printf("Date addition to attribute list failed\n");
                return result;
           }

        printAttrList(attrList, KMIP_REQUEST);
        return result;

}

I_KS_Result CreateKeyAttributes(I_O_Session *handle_p,  I_KO_AttributeList* pAttrList)
{
    I_KS_Result result;

    result = I_KC_CreateAttributeList(pAttrList, NULL);
    if (result.status == I_KT_ResultStatus_Success)
    {

        AddKeyAttributes(*pAttrList);
   }
   return result;
}

I_KS_Result ReKeyPair(I_O_Session *handle_p, char *UID, int offset)
{
    I_KO_AttributeList attrListPriv = NULL;
    I_KO_AttributeList attrListPub = NULL;
    I_KO_AttributeList attrListComm = NULL;
    I_KS_Result result;
    I_KS_Attribute attributeDate;

    do
    {

        result = I_KC_CreateAttributeList(&attrListComm, NULL);
        if (result.status != I_KT_ResultStatus_Success)
        {
                printf("ReKeypair failed. Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
                break;
        }

	if (UID != NULL)
            addUniqueIdentifier(attrListComm, UID);

        if(offset >= 0)
        {   
           addOffset(attrListComm,offset);
        }   
        else
        {

        // To send date attributes, uncomment below code
        /*  
        result = AddKeyAttributes(attrListComm);
        if (result.status != I_KT_ResultStatus_Success)
        {
                printf("ReKeypair failed. Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
                break;
        }

        result = CreateKeyAttributes(handle_p, &attrListPriv);
        if (result.status != I_KT_ResultStatus_Success)
        {
                printf("ReKeypair failed for private key. Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
                break;
        }

        result = CreateKeyAttributes(handle_p, &attrListPub);
        if (result.status != I_KT_ResultStatus_Success)
        {
                printf("ReKeypair failed for public key. Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
                break;
        }
        */
        }

        // Re key Pair
        result = I_KC_ReKeyPair(*handle_p,attrListComm, attrListPriv,attrListPub,I_KT_ObjectType_PrivateKey);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_ReKeyPair failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            break;
        }

        printAttrList(attrListComm, KMIP_RESPONSE);

    }
    while (0);
    // delete the attribute list
    if (attrListComm != NULL)
    {
        I_KS_Result result1;
        result1 = I_KC_DeleteAttributeList(attrListComm);
        if (result1.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_DeleteAttributeList failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result1), I_KC_GetResultReasonString(result1));
        }
    }
    if (attrListPriv != NULL)
    {
        I_KS_Result result1;
        result1 = I_KC_DeleteAttributeList(attrListPriv);
        if (result1.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_DeleteAttributeList failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result1), I_KC_GetResultReasonString(result1));
        }
    }
    if (attrListPub != NULL)
    {
        I_KS_Result result1;
        result1 = I_KC_DeleteAttributeList(attrListPub);
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

    result = ReKeyPair(&sess,UID,offset);
    if (result.status != I_KT_ResultStatus_Success)
    {
        printf("ReKeyPair failed Status:%s Reason:%s\n",
                I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
    }
    else
        printf("ReKeyPair Successful\n");

    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}

