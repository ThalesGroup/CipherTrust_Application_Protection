/*
 * KMIPSetDate.c	
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 * Sample code for KMIP Add or modify date attributes.
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"
#include <openssl/bn.h>
#include <openssl/rsa.h>
#include <openssl/x509.h>

void usage(void)
{
    fprintf(stderr, "usage: KMIPSetDate conf_file uniqueID\n");
    exit(1);
}


int setDate(I_KO_AttributeList attrList,char *uniqueID_p)
{
        I_KS_Attribute attributeDate;
        I_KS_Result ret_s;
        int attribute =0; 

        printf("\n Enter Attribute to be added:");
        printf("\n 1) Activation Date");
        printf("\n 2) Process Start Date");
        printf("\n 3) Protect Stop Date");
        printf("\n 4) Deactivation Date");
        printf("\n Please Enter attribute ::");
        scanf("%d",&attribute);

        addUniqueIdentifier(attrList, uniqueID_p);
        switch(attribute){
             case 1:
               attributeDate.attributeName = "Activation Date";
               break;
             case 2:
               attributeDate.attributeName = "Process Start Date";
               break;
             case 3:
               attributeDate.attributeName = "Protect Stop Date";
               break;
             case 4:
               attributeDate.attributeName = "Deactivation Date";
               break;
             default:
               printf("Invalid date \n");
               return -1;
        }

        attributeDate.attributeValue.index = -1;
        attributeDate.attributeValue.valueType_t = I_KT_AttributeValueType_DateTime;
        attributeDate.attributeValue.value_u.dateTimeVal = time(NULL);
        ret_s = I_KC_AddToAttributeList(attrList, &attributeDate);
        if (ret_s.status != I_KT_ResultStatus_Success)
        {
            printf("Date addition to attribute list failed\n");
            return -1;
        }
       return 0;
}

int main(int argc, char **argv)
{

    I_O_Session sess;
    I_T_RETURN rc;
    I_KS_Result result;
    I_KO_AttributeList attrList = NULL;
    int type=0,argp = 0, rc_func=0;
    char *path = NULL,*uniqueID_p = NULL;

    if (argc < 3)
        usage(); // exit

    argp = 1;
    path = argv[argp++];

    uniqueID_p = argv[argp];

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

        // create the attribute list
        result = I_KC_CreateAttributeList(&attrList, NULL);
        if (result.status != I_KT_ResultStatus_Success)
        {
            printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
            goto error;
        }

    do
    {
        printf("\n Enter type of operation to be performed:");
        printf("\n 1)Add Attribute");
        printf("\n 2)Modify Attribute");
        printf("\n Please Enter type of operation ::");
        scanf("%d",&type);
        if (!type) break; 


    switch(type)
    {
        case 1:
               rc_func = setDate(attrList,uniqueID_p);
               if (rc_func != 0)break;
               printAttrList(attrList, KMIP_REQUEST);
               // Add Attribute.
               result = I_KC_AddAttribute(sess, attrList);
               if (result.status != I_KT_ResultStatus_Success)
               {
                 printf("I_KC_AddAttribute failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
                 break;
               }
               printAttrList(attrList, KMIP_RESPONSE);
            break;

        case 2:
               rc_func =setDate(attrList,uniqueID_p);
               if (rc_func != 0)break;
               printAttrList(attrList, KMIP_REQUEST);
               // Modify Attribute.
               result = I_KC_ModifyAttribute(sess, attrList);
               if (result.status != I_KT_ResultStatus_Success)
               {
                   printf("I_KC_ModifyAttribute failed Status:%s Reason:%s\n",
                    I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
                   break;
               }
               printAttrList(attrList, KMIP_RESPONSE);
            break;

        default:
            printf("Invalid option\n");
            goto error;
    }



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
    }while(0);

    error:
    I_C_CloseSession(sess);
    I_C_Fini();
    return rc;

}

