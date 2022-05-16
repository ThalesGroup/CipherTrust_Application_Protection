/*
* KMIPMisc.c	
*
* Sample code is provided for educational purposes
* No warranty of any kind, either expressed or implied by fact or law
* Use of this item is not restricted by copyright or license terms
*
* Miscellaneous code for KMIP Sample Applications.
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

void printDate(time_t value);

void printCipherMode(I_KT_BlockCipherMode value)
{

        switch (value)
        {
        case I_KT_Mode_NISTKeyWrap:
                printf("NIST Key Wrap");
                break;
        default:
                printf("Unrecognized Cipher Mode");
                break;
        }
}

void printWrappingMethod(I_KT_WrappingMethod value)
{
        switch (value)
        {
        case I_KT_WrappingMethod_Encrypt:
                printf("Encrypt");
                break;
        default:
                printf("Unrecognized Wrapping Method");
                break;
        }
}

void printEncodingOption(I_KT_EncodingOption value)
{
        switch (value)
        {
        case I_KT_EncodingOption_No_Encoding:
                printf("No Encoding");
                break;
        case I_KT_EncodingOption_TTLV_Encoding:
                printf("TTLV Encoding");
                break;
        default:
                printf("Unrecognized Encoding Option");
                break;
        }
}

void printElement(I_KS_Element* element)
{
	if(element)
	{
		printf("Element Tag : 0x%x ", element->tag);

		printValue(&element->value_s);
	}
	else
		printf("Element Tag : < null >");

}

void printObjectType(I_KT_ObjectType value)
{
	switch (value)
	{
	case I_KT_ObjectType_SymmetricKey:
		printf("SymmetricKey ");
		break;
	case I_KT_ObjectType_Certificate:
		printf("Certificate ");
		break;
	case I_KT_ObjectType_PublicKey:
		printf("PublicKey ");
		break;
	case I_KT_ObjectType_PrivateKey:
		printf("PrivateKey ");
		break;
	case I_KT_ObjectType_Template:
		printf("Template ");
		break;
	case I_KT_ObjectType_SecretData:
		printf("SecretData ");
		break;
	case I_KT_ObjectType_OpaqueObject:
		printf("OpaqueObject ");
		break;
	case I_KT_ObjectType_SplitKey:
		printf("SplitKey ");
		break;
	}
}

void printOperation(I_KT_Operation value)
{
	switch (value)
	{
	case I_KT_Operation_Register:
		printf("Register ");
		break;
	case I_KT_Operation_Get:
		printf("Get ");
		break;
	case I_KT_Operation_GetAttributes:
		printf("GetAttributes ");
		break;
	case I_KT_Operation_Locate:
		printf("Locate ");
		break;
	case I_KT_Operation_Query:
		printf("Query ");
		break;
	case I_KT_Operation_Destroy:
		printf("Destroy ");
		break;
	case I_KT_Operation_Create:
		printf("Create ");
		break;
	case I_KT_Operation_CreateKeyPair:
		printf("CreateKeyPair ");
		break;
	case I_KT_Operation_ReKey:
		printf("ReKey ");
		break;
	case I_KT_Operation_DeriveKey:
		printf("DeriveKey ");
		break;
	case I_KT_Operation_Certify:
		printf("Certify ");
		break;
	case I_KT_Operation_ReCertify:
		printf("ReCertify ");
		break;
	case I_KT_Operation_Check:
		printf("Check ");
		break;
	case I_KT_Operation_GetAttributesList:
		printf("GetAttributeList ");
		break;
	case I_KT_Operation_AddAttribute:
		printf("AddAttribute ");
		break;
	case I_KT_Operation_ModifyAttribute:
		printf("ModifyAttribute ");
		break;
	case I_KT_Operation_DeleteAttribute:
		printf("DeleteAttribute ");
		break;
	case I_KT_Operation_ObtainLease:
		printf("ObtainLease ");
		break;
	case I_KT_Operation_GetUsageAllocation:
		printf("GetUsageAllocation ");
		break;
	case I_KT_Operation_Activate:
		printf("Activate ");
		break;
	case I_KT_Operation_Revoke:
		printf("Revoke ");
		break;
	case I_KT_Operation_Archive:
		printf("Archive ");
		break;
	case I_KT_Operation_Recover:
		printf("Recover ");
		break;
	case I_KT_Operation_Validate:
		printf("Validate ");
		break;
	case I_KT_Operation_Cancel:
		printf("Cancel ");
		break;
	case I_KT_Operation_Poll:
		printf("Poll ");
		break;
	case I_KT_Operation_Notify:
		printf("Notify ");
		break;
	case I_KT_Operation_Put:
		printf("Put ");
		break;
	case I_KT_Operation_ReKey_KeyPair:
                printf("ReKey_KeyPair ");
                break;
	case I_KT_Operation_DiscoverVersions:
                printf("DiscoverVersions ");
                break;





	}

}

void modifyContactInformation(I_KO_AttributeList attrList)
{
	I_KS_Attribute attribute;
	I_KS_Result ret_s;
	do
	{
		//Contact Information
		attribute.attributeValue.index = 0;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_TextString;
		attribute.attributeValue.value_u.textStringVal_p = "Thales Group. (Modified) ";
		attribute.attributeName = "Contact Information";
		ret_s = I_KC_AddToAttributeList(attrList, &attribute);
		if (ret_s.status != I_KT_ResultStatus_Success)
		{
			printf("Contact Information addition to attribute list failed\n");
			break;
		}
	} while (0);
	return;
}


void addAttributeObjectGroup(I_KO_AttributeList attrList)
{
	I_KS_Attribute attribute;
	I_KS_Result ret_s;
	do
	{
		//Object Group Index : -1
		attribute.attributeValue.index = -1;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_TextString;
		attribute.attributeValue.value_u.textStringVal_p = "MyGroupIndex2";
		attribute.attributeName = "Object Group";
		ret_s = I_KC_AddToAttributeList(attrList, &attribute);
		if (ret_s.status != I_KT_ResultStatus_Success)
		{
			printf("Object Group addition to attribute list failed\n");
			break;
		}
	} while (0);
	return;
}
void printKeyFormat(I_KT_KeyFormat value)
{
	printf("Key Format : ");
	switch (value)
	{
	case I_KT_KeyFormat_Raw:
		printf("KMIP_KEY_FORMAT_RAW");
		break;
	case I_KT_KeyFormat_Opaque:
		printf("KMIP_KEY_FORMAT_OPAQUE");
		break;
	case I_KT_KeyFormat_PKCS1:
		printf("KMIP_KEY_FORMAT_PKCS1");
		break;
	case I_KT_KeyFormat_PKCS8:
		printf("KMIP_KEY_FORMAT_PKCS8");
		break;
	case I_KT_KeyFormat_X509:
		printf("KMIP_KEY_FORMAT_X509");
		break;
	case I_KT_KeyFormat_ECPrivateKey:
		printf("KMIP_KEY_FORMAT_EC_PRIVATE_KEY");
		break;
	case I_KT_KeyFormat_TransparentSymmetricKey:
		printf("KMIP_KEY_FORMAT_TRANSPARENT_SYMMETRIC_KEY");
		break;
	case I_KT_KeyFormat_TransparentDSAPrivateKey:
		printf("KMIP_KEY_FORMAT_TRANSPARENT_DSA_PRIVATE_KEY");
		break;
	case I_KT_KeyFormat_TransparentDSAPublicKey:
		printf("KMIP_KEY_FORMAT_TRANSPARENT_DSA_PUBLIC_KEY");
		break;
	case I_KT_KeyFormat_TransparentRSAPrivateKey:
		printf("KMIP_KEY_FORMAT_TRANSPARENT_RSA_PRIVATE_KEY");
		break;
	case I_KT_KeyFormat_TransparentRSAPublicKey:
		printf("KMIP_KEY_FORMAT_TRANSPARENT_RSA_PUBLIC_KEY");
		break;
	case I_KT_KeyFormat_TransparentDHPrivateKey:
		printf("KMIP_KEY_FORMAT_TRANSPARENT_DH_PRIVATE_KEY");
		break;
	case I_KT_KeyFormat_TransparentDHPublicKey:
		printf("KMIP_KEY_FORMAT_TRANSPARENT_DH_PUBLIC_KEY");
		break;
	case I_KT_KeyFormat_TransparentECDSAPrivateKey:
		printf("KMIP_KEY_FORMAT_TRANSPARENT_ECDSA_PRIVATE_KEY");
		break;
	case I_KT_KeyFormat_TransparentECDSAPublicKey:
		printf("KMIP_KEY_FORMAT_TRANSPARENT_ECDSA_PUBLIC_KEY");
		break;
	case I_KT_KeyFormat_TransparentECDHPrivateKey:
		printf("KMIP_KEY_FORMAT_TRANSPARENT_ECDH_PRIVATE_KEY");
		break;
	case I_KT_KeyFormat_TransparentECDHPublicKey:
		printf("KMIP_KEY_FORMAT_TRANSPARENT_ECDH_PUBLIC_KEY");
		break;
	case I_KT_KeyFormat_TransparentECMQVPrivateKey:
		printf("KMIP_KEY_FORMAT_TRANSPARENT_ECMQV_PRIVATE_KEY");
		break;
	case I_KT_KeyFormat_TransparentECMQVPublicKey:
		printf("KMIP_KEY_FORMAT_TRANSPARENT_ECMQV_PUBLIC_KEY");
		break;
	default:
		printf("UnRecognized Key Format.");
		break;
	}
	printf("\n");
}

void printCryptographicAlgorithm(I_KT_CryptographicAlgorithm value)
{
	switch (value)
	{
	case I_KT_CryptographicAlgorithm_None:
		printf("I_KT_CryptographicAlgorithm_None");
		break;
	case I_KT_CryptographicAlgorithm_DES:
		printf("I_KT_CryptographicAlgorithm_DES");
		break;
	case I_KT_CryptographicAlgorithm_3DES:
		printf("I_KT_CryptographicAlgorithm_3DES");
		break;
	case I_KT_CryptographicAlgorithm_AES:
		printf("I_KT_CryptographicAlgorithm_AES");
		break;
	case I_KT_CryptographicAlgorithm_RSA:
		printf("I_KT_CryptographicAlgorithm_RSA");
		break;
	case I_KT_CryptographicAlgorithm_DSA:
		printf("I_KT_CryptographicAlgorithm_DSA");
		break;
	case I_KT_CryptographicAlgorithm_ECDSA:
		printf("I_KT_CryptographicAlgorithm_ECDSA");
		break;
	case I_KT_CryptographicAlgorithm_HMACSHA1:
		printf("I_KT_CryptographicAlgorithm_HMACSHA1");
		break;
	case I_KT_CryptographicAlgorithm_HMACSHA224:
		printf("I_KT_CryptographicAlgorithm_HMACSHA224");
		break;
	case I_KT_CryptographicAlgorithm_HMACSHA256:
		printf("I_KT_CryptographicAlgorithm_HMACSHA256");
		break;
	case I_KT_CryptographicAlgorithm_HMACSHA384:
		printf("I_KT_CryptographicAlgorithm_HMACSHA384");
		break;
	case I_KT_CryptographicAlgorithm_HMACSHA512:
		printf("I_KT_CryptographicAlgorithm_HMACSHA512");
		break;
	case I_KT_CryptographicAlgorithm_HMACMD5:
		printf("I_KT_CryptographicAlgorithm_HMACMD5");
		break;
	case I_KT_CryptographicAlgorithm_DH:
		printf("I_KT_CryptographicAlgorithm_DH");
		break;
	case I_KT_CryptographicAlgorithm_ECDH:
		printf("I_KT_CryptographicAlgorithm_ECDH");
		break;
	case I_KT_CryptographicAlgorithm_ECMQV:
		printf("I_KT_CryptographicAlgorithm_ECMQV");
		break;
	default:
		printf("Unrecongnized Value");
	}
}

void printHasingAlgo(I_KT_HashingAlgorithm value)
{
	printf("Hasing Algorithm : ");
	switch (value)
	{
	case I_KT_Hash_None:
		printf("I_KT_Hash_None");
		break;
	case I_KT_Hash_MD2:
		printf("I_KT_Hash_MD2");
		break;
	case I_KT_Hash_MD4:
		printf("I_KT_Hash_MD4");
		break;
	case I_KT_Hash_MD5:
		printf("I_KT_Hash_MD5");
		break;
	case I_KT_Hash_SHA1:
		printf("I_KT_Hash_SHA1");
		break;
	case I_KT_Hash_SHA224:
		printf("I_KT_Hash_SHA224");
		break;
	case I_KT_Hash_SHA256:
		printf("I_KT_Hash_SHA256");
		break;
	case I_KT_Hash_SHA384:
		printf("I_KT_Hash_SHA384");
		break;
	case I_KT_Hash_SHA512:
		printf("I_KT_Hash_SHA512");
		break;
	default:
		printf("Unrecongnized Hasing Algorithm");
	}
}
 
void printState (I_KT_State value)
{

        switch (value)
        {
        case I_KT_State_PreActive:
                printf("PreActive");
                break;
        case I_KT_State_Active:
                printf("Active");
                break;
        case I_KT_State_Deactivated:
                printf("Deactivated");
                break;
        case I_KT_State_Compromised:
                printf("Compromised");
                break;
        case I_KT_State_Destroyed:
                printf("Destroyed");
                break;
        case I_KT_State_Destroyed_Compromised:
                printf("Destroyed Compromised");
                break;
        default:
                printf("Unrecognized State");
                break;
        }

}
void printValue(I_KS_Value *value)
{
	unsigned int i = 0;
	switch (value->type)
	{
	case I_KT_Integer:
		printf("%d\n", value->value_u.integerVal);
		break;
	case I_KT_LongInteger:
		printf("%d\n", value->value_u.longIntegerVal);
		break;
	case I_KT_Boolean:
		printf("%d\n", value->value_u.boolVal);
		break;
	case I_KT_Enumeration:
		printf("%d\n", value->value_u.enumVal);
		break;
	case I_KT_DateTime:
		printDate(value->value_u.dateTimeVal);
		printf("\n");
		break;
	case I_KT_Interval:
		printf("%d\n", value->value_u.intervalVal);
		break;
	case I_KT_TextString:
		printf("%s\n", value->value_u.textStringVal_p);
		break;
	case I_KT_ByteString:
		for (i = 0; i < value->value_u.byteString_s.byteStringLen; i++)
		{
			printf("%2.2X ", value->value_u.byteString_s.byteString_p[i]);
		}
		printf("\n");
		break;
	case I_KT_BigInteger:
		for (i = 0; i < value->value_u.bigIntegerVal_s.byteStringLen; i++)
		{
			printf("%2.2X ", value->value_u.bigIntegerVal_s.byteString_p[i]);
		}
		printf("\n");
		break;
	}
}

void printDate(time_t value)
{
	struct tm gmt, *gmt_p;
#ifdef WIN32
	gmt_p = gmtime(&value);
	if (gmt_p == NULL)
		printf("Bad Date/Time\n");
	else
	{
		gmt = *gmt_p;
		printf("%4d-%02d-%02d %02d:%02d:%02d GMT",
			gmt.tm_year + 1900,
			gmt.tm_mon + 1,
			gmt.tm_mday,
			gmt.tm_hour,
			gmt.tm_min,
			gmt.tm_sec);
	}
#else
	if (gmtime_r(&value, &gmt) == NULL)
		printf("Bad Date/Time\n");
	else
		printf("%4d-%02d-%02d %02d:%02d:%02d GMT",
		gmt.tm_year + 1900,
		gmt.tm_mon + 1,
		gmt.tm_mday,
		gmt.tm_hour,
		gmt.tm_min,
		gmt.tm_sec);
#endif //WIN32
}
void printAttributeNameList(I_KS_AttributeNameList *attrNameList)
{
	int iLoop = 0;
	printf("\n Printing Attribute List:");
	for(iLoop =0;iLoop< (int)attrNameList->count;iLoop++)
		printf("\n Attribute Name ::%s",attrNameList->attrlistname_pp[iLoop]);
}
void printAttributeValue(I_KS_Attribute *attribute)
{
	unsigned int j;
	switch (attribute->attributeValue.valueType_t)
	{
	case I_KT_AttributeValueType_Custom_S:
		printValue(&attribute->attributeValue.value_u.custom_s);
		break;
	case I_KT_AttributeValueType_TextString:
		printf("%s\n", attribute->attributeValue.value_u.textStringVal_p);
		break;
	case I_KT_AttributeValueType_DateTime:
		printDate(attribute->attributeValue.value_u.dateTimeVal);
		printf("\n");
		break;
	case I_KT_AttributeValueType_Digest_S:
		printf("\n");
		printf("%67s", "");
		printHasingAlgo(attribute->attributeValue.value_u.digest_s.algo_t);
		printf("\n");
		printf("%67s", "");
		printf("Digest ByteString : ");
		for (j = 0; j < attribute->attributeValue.value_u.digest_s.byteString_s.byteStringLen; j++)
			printf("%2.2X", attribute->attributeValue.value_u.digest_s.byteString_s.byteString_p[j]);
		printf("\n");
		break;
	case I_KT_AttributeValueType_Name_S:
		printf("%s \n", attribute->attributeValue.value_u.name_s.name_p);
		break;
	case I_KT_AttributeValueType_Enum:
		if (strcmp(attribute->attributeName, "Object Type") == 0)
			printObjectType(attribute->attributeValue.value_u.enumVal);
		else if (strcmp(attribute->attributeName, "Cryptographic Algorithm") == 0)
			printCryptographicAlgorithm(attribute->attributeValue.value_u.enumVal);
                else if (strcmp(attribute->attributeName, "State") == 0)
                        printState(attribute->attributeValue.value_u.enumVal);
                else if (strcmp(attribute->attributeName, "Cipher Mode") == 0)
                        printCipherMode(attribute->attributeValue.value_u.enumVal);
                else if (strcmp(attribute->attributeName, "Wrapping Method") == 0)
                        printWrappingMethod(attribute->attributeValue.value_u.enumVal);
                else if (strcmp(attribute->attributeName, "Encoding Option") == 0)
                        printEncodingOption(attribute->attributeValue.value_u.enumVal);
		printf("\n");
		break;
	case I_KT_AttributeValueType_Integer:
		printf("%d \n", attribute->attributeValue.value_u.integerVal);
		break;
	case I_KT_AttributeValueType_ApplicationSpecificInfo_S:
		printf("\nData::%s ", attribute->attributeValue.value_u.asi_s.data_p);
		printf("\nNameSpace::%s ", attribute->attributeValue.value_u.asi_s.namespace_p);
		break;
	case I_KT_AttributeValueType_Link_S:
		printf("\nLinkType::%2.2X ", attribute->attributeValue.value_u.link_s.linktype_t);
		printf("\nUID::%s ", attribute->attributeValue.value_u.link_s.uniqueIdentifiers_p);
		break;
	case I_KT_AttributeValueType_CertificateIdentifier_S:
		printf("\nCertificateIssuer::%s ", attribute->attributeValue.value_u.cert_id_s.issuer_p);
		printf("\nS/N::%s\n", attribute->attributeValue.value_u.cert_id_s.sernum_p);
		break;
	case I_KT_AttributeValueType_CertificateIssuer_S:
		printf("\nDistinctName::%s ", attribute->attributeValue.value_u.cert_iss_s.dist_name_p);
		printf("\nAlternativeName::%s\n", attribute->attributeValue.value_u.cert_iss_s.alt_name_p);
		break;
	case I_KT_AttributeValueType_CertificateSubject_S:
		printf("\nDistinctName::%s ", attribute->attributeValue.value_u.cert_subj_s.dist_name_p);
		printf("\nAlternativeName::%s\n", attribute->attributeValue.value_u.cert_subj_s.alt_name_p);
		break;
	default:
		printf("Unknown value type\n");

	}
}

void printAttrList(I_KO_AttributeList attrList, int request)
{
	I_KS_Value *customAttributeValue_p = NULL;
	unsigned int i;
	I_KS_Result rc;
	I_KS_Attribute **attr_pp;
	I_T_UINT count;

	rc = I_KC_RetrieveFromAttributeList(attrList, NULL, &attr_pp, &count);
	if (rc.status == I_KT_ResultStatus_Success)
	{
		if (request == KMIP_REQUEST)
			printf("----Request Attribute List----\n");
		else
			printf("----Response Attribute List----\n");

		for (i = 0; i < count; i++)
		{
			printf("Attribute Name : %25s | Index : %3d | Value : ", attr_pp[i]->attributeName, attr_pp[i]->attributeValue.index);
			printAttributeValue(attr_pp[i]);
		}
		I_C_Free(attr_pp);
	}
}

void addUniqueIdentifier(I_KO_AttributeList attrList, char *uniqueID_p)
{
	I_KS_Attribute attribute;
	I_KS_Result ret_s;

	do
	{
		if (uniqueID_p != NULL)
		{
			attribute.attributeValue.index = 0;
			attribute.attributeValue.valueType_t = I_KT_AttributeValueType_TextString;
			attribute.attributeValue.value_u.textStringVal_p = uniqueID_p;
			attribute.attributeName = "Unique Identifier";
			ret_s = I_KC_AddToAttributeList(attrList, &attribute);
			if (ret_s.status != I_KT_ResultStatus_Success)
			{
				printf("insertion failed in the attrList\n");
				break;
			}
		}
	}
	while (0);


	return;
}

void addCryptographicLength(I_KO_AttributeList attrList)
{
	I_KS_Attribute attribute;
	I_KS_Result ret_s;
	do
	{
		//Cryptographic Length
		attribute.attributeValue.index = 0;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Integer;
		attribute.attributeValue.value_u.integerVal = 16 * 8;
		attribute.attributeName = "Cryptographic Length";
		ret_s = I_KC_AddToAttributeList(attrList, &attribute);
		if (ret_s.status != I_KT_ResultStatus_Success)
		{
			printf("Cryptographic Length addition to attribute list failed\n");
			break;
		}
	} while (0);

	return;
}

void addRSACryptographicLength(I_KO_AttributeList attrList)
{
        I_KS_Attribute attribute;
        I_KS_Result ret_s;
        do
        {
                //Cryptographic Length
                attribute.attributeValue.index = 0;
                attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Integer;
		attribute.attributeValue.value_u.integerVal = 2048;
                attribute.attributeName = "Cryptographic Length";
                ret_s = I_KC_AddToAttributeList(attrList, &attribute);
                if (ret_s.status != I_KT_ResultStatus_Success)
                {
                        printf("Cryptographic Length addition to attribute list failed\n");
                        break;
                }
        } while (0);

        return;
}

void addCryptographicAlgorithm(I_KO_AttributeList attrList)
{
	I_KS_Attribute attribute;
	I_KS_Result ret_s;
	do
	{
		//Cryptographic Algorithm
		attribute.attributeValue.index = 0;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Enum;
		attribute.attributeValue.value_u.enumVal = I_KT_CryptographicAlgorithm_AES;
		attribute.attributeName = "Cryptographic Algorithm";
		ret_s = I_KC_AddToAttributeList(attrList, &attribute);
		if (ret_s.status != I_KT_ResultStatus_Success)
		{
			printf("Cryptographic Algorithm addition to attribute list failed\n");
			break;
		}
	}        while (0);

	return;
}

void addRSACryptographicAlgorithm(I_KO_AttributeList attrList)
{
        I_KS_Attribute attribute;
        I_KS_Result ret_s;
        do
        {
                //Cryptographic Algorithm
                attribute.attributeValue.index = 0;
                attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Enum;
                attribute.attributeValue.value_u.enumVal = I_KT_CryptographicAlgorithm_RSA;
                attribute.attributeName = "Cryptographic Algorithm";
                ret_s = I_KC_AddToAttributeList(attrList, &attribute);
                if (ret_s.status != I_KT_ResultStatus_Success)
                {
                        printf("Cryptographic Algorithm addition to attribute list failed\n");
                        break;
                }
        }        while (0);

        return;
}


void addContactInformation(I_KO_AttributeList attrList)
{
	I_KS_Attribute attribute;
	I_KS_Result ret_s;
	do
	{
		//Contact Information
		attribute.attributeValue.index = 0;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_TextString;
		attribute.attributeValue.value_u.textStringVal_p = "Thales Group.";
		attribute.attributeName = "Contact Information";
		ret_s = I_KC_AddToAttributeList(attrList, &attribute);
		if (ret_s.status != I_KT_ResultStatus_Success)
		{
			printf("Contact Information addition to attribute list failed\n");
			break;
		}
	} while (0);
	return;
}

void addApplicationSpecificInfo(I_KO_AttributeList attrList)
{
	I_KS_Attribute attribute;
	I_KS_Result ret_s;

	do
	{
		attribute.attributeValue.index = 0;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_ApplicationSpecificInfo_S;
		attribute.attributeValue.value_u.asi_s.data_p = "www.thales.com";

		attribute.attributeValue.value_u.asi_s.namespace_p = "ssl";
		attribute.attributeName = "Application Specific Information";
		ret_s = I_KC_AddToAttributeList(attrList, &attribute);
		if (ret_s.status != I_KT_ResultStatus_Success)
		{
			printf("Name addition to attribute list failed\n");
			break;
		}



	}while(0);
	return;
}


void addName(I_KO_AttributeList attrList, char *name1, char *name2)
{
	I_KS_Attribute attribute;
	I_KS_Result ret_s;

	do
	{
		//KeyName Index : 0
		if (name1 != NULL)
		{
			attribute.attributeValue.index = 0;
			attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Name_S;
			attribute.attributeValue.value_u.name_s.name_p = name1;
			attribute.attributeValue.value_u.name_s.nameType_t = I_KT_NameType_Text;
			attribute.attributeName = "Name";
			ret_s = I_KC_AddToAttributeList(attrList, &attribute);
			if (ret_s.status != I_KT_ResultStatus_Success)
			{
				printf("Name addition to attribute list failed\n");
				break;
			}
		}

		//KeyName Index : 1
		if (name2 != NULL)
		{
			attribute.attributeValue.index = 1;
			attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Name_S;
			attribute.attributeValue.value_u.name_s.name_p = name2;
			attribute.attributeValue.value_u.name_s.nameType_t = I_KT_NameType_Text;
			attribute.attributeName = "Name";
			ret_s = I_KC_AddToAttributeList(attrList, &attribute);
			if (ret_s.status != I_KT_ResultStatus_Success)
			{
				printf("Name addition to attribute list failed\n");
				break;
			}
		}
	}        while (0);

	return;
}

void addIV(I_KO_AttributeList attrList, const char *iv, unsigned int ivlen)
{

	I_KS_Attribute attribute;
	I_KS_Result ret_s;
        do
        {
	  if(iv != NULL)
          {
            attribute.attributeValue.index = 0;
            attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Bytes;
            attribute.attributeValue.value_u.bytes.byteString_p = (char *)iv;
            attribute.attributeValue.value_u.bytes.byteStringLen = ivlen;
	    attribute.attributeName = "IV";
            ret_s = I_KC_AddToAttributeList(attrList, &attribute);
            if (ret_s.status != I_KT_ResultStatus_Success)
            {
                 printf("IV addition to attribute list failed\n");
                 break;
            }
          }
        }while (0);
	
	return;
}

void addrandomIV(I_KO_AttributeList attrList, int random)
{

        I_KS_Attribute attribute;
        I_KS_Result ret_s;
        do
        {
          if(random != 0)
          {
            attribute.attributeValue.index = 0;
            attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Integer;
            attribute.attributeValue.value_u.integerVal = random;
            attribute.attributeName = "Random IV";
            ret_s = I_KC_AddToAttributeList(attrList, &attribute);
            if (ret_s.status != I_KT_ResultStatus_Success)
            {
                        printf("Random IV addition to attribute list failed\n");
                        break;
            }
          }
        }while (0);

        return;
}

void addCipherLen(I_KO_AttributeList attrList, int cipher_len)
{
        I_KS_Attribute attribute;
        I_KS_Result ret_s;
        do
        {
          if(cipher_len != 0)
          {
            attribute.attributeValue.index = 0;
            attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Integer;
            attribute.attributeValue.value_u.integerVal = cipher_len;
            attribute.attributeName = "Cipher Len";
            ret_s = I_KC_AddToAttributeList(attrList, &attribute);
            if (ret_s.status != I_KT_ResultStatus_Success)
            {
                        printf("Cipher Len addition to attribute list failed\n");
                        break;
            }
          }
        }while (0);

        return;
}

void addIVLen(I_KO_AttributeList attrList, int iv_len)
{
        I_KS_Attribute attribute;
        I_KS_Result ret_s;
        do
        {
          if(iv_len != 0)
          {
            attribute.attributeValue.index = 0;
            attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Integer;
            attribute.attributeValue.value_u.integerVal = iv_len;
            attribute.attributeName = "IV Len";
            ret_s = I_KC_AddToAttributeList(attrList, &attribute);
            if (ret_s.status != I_KT_ResultStatus_Success)
            {
                        printf("IV Length addition to attribute list failed\n");
                        break;
            }
          }
        }while (0);

        return;
}


void addTagLen(I_KO_AttributeList attrList, int tag_len)
{
        I_KS_Attribute attribute;
        I_KS_Result ret_s;
        do
        {
          if(tag_len != 0)
          {
            attribute.attributeValue.index = 0;
            attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Integer;
            attribute.attributeValue.value_u.integerVal = tag_len;
            attribute.attributeName = "Tag Len";
            ret_s = I_KC_AddToAttributeList(attrList, &attribute);
            if (ret_s.status != I_KT_ResultStatus_Success)
            {
                        printf("Tag Length addition to attribute list failed\n");
                        break;
            }
          }
        }while (0);

        return;
}


void addAlgorithm(I_KO_AttributeList attrList, const char *algo)
{

        I_KS_Attribute attribute;
        I_KS_Result ret_s;

        do
        {
          if(algo != NULL)
          {
            attribute.attributeValue.index = 0;
            attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Name_S;
            attribute.attributeValue.value_u.name_s.name_p = (char *)algo;
            attribute.attributeValue.value_u.name_s.nameType_t = I_KT_NameType_Text;
            attribute.attributeName = "Algorithm";
            ret_s = I_KC_AddToAttributeList(attrList, &attribute);
            if (ret_s.status != I_KT_ResultStatus_Success)
            {
                 printf("Algorithm addition to attribute list failed\n");
                 break;
            }
          }
        }while (0);

        return;
}

void addLink(I_KO_AttributeList attrList)
{
	I_KS_Attribute attribute;
	I_KS_Result ret_s;
	int type=0;
	I_KT_LinkType linkType;
	char uniqueID_p[200];
	int types[] = {I_KT_Certificate_Link,
		I_KT_PublicKey_Link,
		I_KT_PrivateKey_Link,
		I_KT_DerivationBaseObject_Link,
		I_KT_DerivedKey_Link,
		I_KT_ReplacementObject_Link,
		I_KT_ReplacedObject_Link};

	do
	{

		printf("\n 1)Certificate_Link For Certificate");
		printf("\n 2)PublicKey_Link For PubLic Key");
		printf("\n 3)PrivateKey_Link For Private Key");
		printf("\n 4)DerivationBaseObject_Link For Derivation Base Object");
		printf("\n 5)DerivedKey_Link For Derived Key");
		printf("\n 6)ReplacementObject_Link For Replacement Object");
		printf("\n 7)ReplacedObject_Link For Replaced Object");
		printf("\n 0) None");

		printf("\n Please Enter LinkType ::");
		scanf("%d",&type);
		if (!type) break;
		linkType = types[type-1];

		printf("\n Please Enter Unique Identifier to be Linked ::");
		scanf("%s",&uniqueID_p);
		attribute.attributeValue.index = 0;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Link_S;
		attribute.attributeValue.value_u.link_s.linktype_t = linkType;
		attribute.attributeValue.value_u.link_s.uniqueIdentifiers_p = uniqueID_p;
		attribute.attributeName = "Link";
		ret_s = I_KC_AddToAttributeList(attrList, &attribute);
		if (ret_s.status != I_KT_ResultStatus_Success)
		{
			printf("Link addition to attribute list failed\n");
			break;
		}


	}while(0);
	return;

}
void addObjectGroup(I_KO_AttributeList attrList)
{
	I_KS_Attribute attribute;
	I_KS_Result ret_s;

	do
	{
		//Object Group Index : 0
		attribute.attributeValue.index = 0;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_TextString;
		attribute.attributeValue.value_u.textStringVal_p = "MyGroupIndex0";
		attribute.attributeName = "Object Group";
		ret_s = I_KC_AddToAttributeList(attrList, &attribute);
		if (ret_s.status != I_KT_ResultStatus_Success)
		{
			printf("Object Group addition to attribute list failed\n");
			break;
		}

		//Object Group Index : 1
		attribute.attributeValue.index = 1;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_TextString;
		attribute.attributeValue.value_u.textStringVal_p = "MyGroupIndex1";
		attribute.attributeName = "Object Group";
		ret_s = I_KC_AddToAttributeList(attrList, &attribute);
		if (ret_s.status != I_KT_ResultStatus_Success)
		{
			printf("Object Group addition to attribute list failed\n");
			break;
		}
	}        while (0);

	return;

}

void addCustomAttributes(I_KO_AttributeList attrList)
{
	I_KS_Attribute attribute;
	I_KS_Result rc;
	char buf[5] = {0x01, 0x02, 0x03, 0x04, 0x05};

	do
	{
		//Custom Attribute : Byte String, Index 0
		attribute.attributeValue.index = 0;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Custom_S;
		attribute.attributeValue.value_u.custom_s.type = I_KT_ByteString;
		attribute.attributeValue.value_u.custom_s.value_u.byteString_s.byteString_p = buf;
		attribute.attributeValue.value_u.custom_s.value_u.byteString_s.byteStringLen = 5;
		attribute.attributeName = "x-Custom_ByteString";
		rc = I_KC_AddToAttributeList(attrList, &attribute);
		if (rc.status != I_KT_ResultStatus_Success)
		{
			printf("Custom Attriute addition to attribute list failed\n");
			break;
		}

		//Custom Attribute : Byte String, Index 1
		attribute.attributeValue.index = 1;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Custom_S;
		attribute.attributeValue.value_u.custom_s.type = I_KT_ByteString;
		attribute.attributeValue.value_u.custom_s.value_u.byteString_s.byteString_p = buf;
		attribute.attributeValue.value_u.custom_s.value_u.byteString_s.byteStringLen = 5;
		attribute.attributeName = "x-Custom_ByteString";
		rc = I_KC_AddToAttributeList(attrList, &attribute);
		if (rc.status != I_KT_ResultStatus_Success)
		{
			printf("Custom Attriute addition to attribute list failed\n");
			break;
		}

		//Custom Attribute : Text String, Index : 0
		attribute.attributeValue.index = 0;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Custom_S;
		attribute.attributeValue.value_u.custom_s.type = I_KT_TextString;
		attribute.attributeValue.value_u.custom_s.value_u.textStringVal_p = "TestString";
		attribute.attributeName = "x-Custom_TextString";
		rc = I_KC_AddToAttributeList(attrList, &attribute);
		if (rc.status != I_KT_ResultStatus_Success)
		{
			printf("Custom Attriute addition to attribute list failed\n");
			break;
		}

		//Custom Attribute : Text String, Index : 1
		attribute.attributeValue.index = 1;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Custom_S;
		attribute.attributeValue.value_u.custom_s.type = I_KT_TextString;
		attribute.attributeValue.value_u.custom_s.value_u.textStringVal_p = "TestString";
		attribute.attributeName = "x-Custom_TextString";
		rc = I_KC_AddToAttributeList(attrList, &attribute);
		if (rc.status != I_KT_ResultStatus_Success)
		{
			printf("Custom Attriute addition to attribute list failed\n");
			break;
		}

		//Custom Attribute : Integer, Index : 0
		attribute.attributeValue.index = 0;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Custom_S;
		attribute.attributeValue.value_u.custom_s.type = I_KT_Integer;
		attribute.attributeValue.value_u.custom_s.value_u.integerVal = 100;
		attribute.attributeName = "x-Custom_Integer";
		rc = I_KC_AddToAttributeList(attrList, &attribute);
		if (rc.status != I_KT_ResultStatus_Success)
		{
			printf("Custom Attriute addition to attribute list failed\n");
			break;
		}

		//Custom Attribute : Integer, Index : 1
		attribute.attributeValue.index = 1;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Custom_S;
		attribute.attributeValue.value_u.custom_s.type = I_KT_Integer;
		attribute.attributeValue.value_u.custom_s.value_u.integerVal = 100;
		attribute.attributeName = "x-Custom_Integer";
		rc = I_KC_AddToAttributeList(attrList, &attribute);
		if (rc.status != I_KT_ResultStatus_Success)
		{
			printf("Custom Attriute addition to attribute list failed\n");
			break;
		}

		//Custom Attribute : LongInteger, Index : 0
		attribute.attributeValue.index = 0;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Custom_S;
		attribute.attributeValue.value_u.custom_s.type = I_KT_LongInteger;
		attribute.attributeValue.value_u.custom_s.value_u.longIntegerVal = 10000000;
		attribute.attributeName = "x-Custom_LongInteger";
		rc = I_KC_AddToAttributeList(attrList, &attribute);
		if (rc.status != I_KT_ResultStatus_Success)
		{
			printf("Custom Attriute addition to attribute list failed\n");
			break;
		}

		//Custom Attribute : LongInteger, Index : 1
		attribute.attributeValue.index = 1;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Custom_S;
		attribute.attributeValue.value_u.custom_s.type = I_KT_LongInteger;
		attribute.attributeValue.value_u.custom_s.value_u.longIntegerVal = 10000000;
		attribute.attributeName = "x-Custom_LongInteger";
		rc = I_KC_AddToAttributeList(attrList, &attribute);
		if (rc.status != I_KT_ResultStatus_Success)
		{
			printf("Custom Attriute addition to attribute list failed\n");
			break;
		}


		//Custom Attribute : Enumeration, Index : 0
		attribute.attributeValue.index = 0;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Custom_S;
		attribute.attributeValue.value_u.custom_s.type = I_KT_Enumeration;
		attribute.attributeValue.value_u.custom_s.value_u.enumVal = 0x10;
		attribute.attributeName = "x-Custom_Enumeration";
		rc = I_KC_AddToAttributeList(attrList, &attribute);
		if (rc.status != I_KT_ResultStatus_Success)
		{
			printf("Custom Attriute addition to attribute list failed\n");
			break;
		}

		//Custom Attribute : Enumeration, Index : 1
		attribute.attributeValue.index = 1;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Custom_S;
		attribute.attributeValue.value_u.custom_s.type = I_KT_Enumeration;
		attribute.attributeValue.value_u.custom_s.value_u.enumVal = 0x10;
		attribute.attributeName = "x-Custom_Enumeration";
		rc = I_KC_AddToAttributeList(attrList, &attribute);
		if (rc.status != I_KT_ResultStatus_Success)
		{
			printf("Custom Attriute addition to attribute list failed\n");
			break;
		}

		//Custom Attribute : Boolean, Index 0
		attribute.attributeValue.index = 0;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Custom_S;
		attribute.attributeValue.value_u.custom_s.type = I_KT_Boolean;
		attribute.attributeValue.value_u.custom_s.value_u.boolVal = 0x01;
		attribute.attributeName = "x-Custom_Boolean";
		rc = I_KC_AddToAttributeList(attrList, &attribute);
		if (rc.status != I_KT_ResultStatus_Success)
		{
			printf("Custom Attriute addition to attribute list failed\n");
			break;
		}

		//Custom Attribute : Boolean, Index 1
		attribute.attributeValue.index = 1;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Custom_S;
		attribute.attributeValue.value_u.custom_s.type = I_KT_Boolean;
		attribute.attributeValue.value_u.custom_s.value_u.boolVal = 0x01;
		attribute.attributeName = "x-Custom_Boolean";
		rc = I_KC_AddToAttributeList(attrList, &attribute);
		if (rc.status != I_KT_ResultStatus_Success)
		{
			printf("Custom Attriute addition to attribute list failed\n");
			break;
		}

		//Custom Attribute : DateTime Index : 0
		attribute.attributeValue.index = 0;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Custom_S;
		attribute.attributeValue.value_u.custom_s.type = I_KT_DateTime;
		attribute.attributeValue.value_u.custom_s.value_u.dateTimeVal = time(NULL);
		attribute.attributeName = "x-Custom_date";
		rc = I_KC_AddToAttributeList(attrList, &attribute);
		if (rc.status != I_KT_ResultStatus_Success)
		{
			printf("Custom Attriute addition to attribute list failed\n");
			break;
		}

		//Custom Attribute : DateTime Index : 1
		attribute.attributeValue.index = 1;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Custom_S;
		attribute.attributeValue.value_u.custom_s.type = I_KT_DateTime;
		attribute.attributeValue.value_u.custom_s.value_u.dateTimeVal = time(NULL);
		attribute.attributeName = "x-Custom_date";
		rc = I_KC_AddToAttributeList(attrList, &attribute);
		if (rc.status != I_KT_ResultStatus_Success)
		{
			printf("Custom Attriute addition to attribute list failed\n");
			break;
		}


		//Custom Attribute : Interval Index : 0
		attribute.attributeValue.index = 0;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Custom_S;
		attribute.attributeValue.value_u.custom_s.type = I_KT_Interval;
		attribute.attributeValue.value_u.custom_s.value_u.intervalVal = 5600;
		attribute.attributeName = "x-Custom_interval";
		rc = I_KC_AddToAttributeList(attrList, &attribute);
		if (rc.status != I_KT_ResultStatus_Success)
		{
			printf("Custom Attriute addition to attribute list failed\n");
			break;
		}

		//Custom Attribute : Interval Index : 1
		attribute.attributeValue.index = 1;
		attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Custom_S;
		attribute.attributeValue.value_u.custom_s.type = I_KT_Interval;
		attribute.attributeValue.value_u.custom_s.value_u.intervalVal = 5600;
		attribute.attributeName = "x-Custom_interval";
		rc = I_KC_AddToAttributeList(attrList, &attribute);
		if (rc.status != I_KT_ResultStatus_Success)
		{
			printf("Custom Attriute addition to attribute list failed\n");
			break;
		}
	} while (0);

	return;

}

void addCryptographicUsageMask(I_KO_AttributeList attrList)
{
        I_KS_Attribute attribute;
        I_KS_Result ret_s;
        do
        {
                //Cryptographic Usage Mask
                attribute.attributeValue.index = 0;
                attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Integer;
                attribute.attributeValue.value_u.integerVal = 12; //For encrypt & decrypt
                attribute.attributeName = "Cryptographic Usage Mask";
                ret_s = I_KC_AddToAttributeList(attrList, &attribute);
                if (ret_s.status != I_KT_ResultStatus_Success)
                {
                        printf("Cryptographic Usage Mask addition to attribute list failed\n");
                        break;
                }
        } while (0);

        return;
}



I_KS_Result batch_GetAttributeList(BatchHandle hBatch, char *uniqueID_p,I_T_UINT *opid_GetAttrList)
{
	I_KS_Result result = {0,};
	I_KO_AttributeList attrList;
	OpArgObject GetAttributeListArg[2];
	int GetAttributeArgc = 1;

	result = I_KC_CreateAttributeList(&attrList, NULL);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}

	if (uniqueID_p != NULL)
		addUniqueIdentifier(attrList, uniqueID_p);

	GetAttributeListArg[0].type = I_KT_Agr_AttributeList;
	GetAttributeListArg[0].attributeList = attrList;


	printAttrList(attrList, KMIP_REQUEST);
	result = I_KC_AddOperation(hBatch,I_KT_Operation_Code_GetAttributesList,GetAttributeListArg,1,opid_GetAttrList);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_AddOperation failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}

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


void addCryptographicUsageMask_public(I_KO_AttributeList attrList)
{
        I_KS_Attribute attribute;
        I_KS_Result ret_s;
        do
        {
               // Cryptographic Usage Mask
                attribute.attributeValue.index = 0;
                attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Integer;
                attribute.attributeValue.value_u.integerVal = 2; 
                attribute.attributeName = "Cryptographic Usage Mask";
                ret_s = I_KC_AddToAttributeList(attrList, &attribute);
                if (ret_s.status != I_KT_ResultStatus_Success)
                {
                        printf("Cryptographic Usage Mask addition to attribute list failed\n");
                        break;
                }
        } while (0);

        return;
}


void addCryptographicUsageMask_private(I_KO_AttributeList attrList)
{
        I_KS_Attribute attribute;
        I_KS_Result ret_s;
        do
        {
                //Cryptographic Usage Mask
                attribute.attributeValue.index = 0;
                attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Integer;
                attribute.attributeValue.value_u.integerVal = 1; 
                attribute.attributeName = "Cryptographic Usage Mask";
                ret_s = I_KC_AddToAttributeList(attrList, &attribute);
                if (ret_s.status != I_KT_ResultStatus_Success)
                {
                        printf("Cryptographic Usage Mask addition to attribute list failed\n");
                        break;
                }
        } while (0);

        return;
}










I_KS_Result batch_GetAttribute(BatchHandle hBatch,char *uniqueID_p,char **attrName,int number,I_T_UINT *opid_GetAttr)
{
	I_KS_Result result = {0,};
	I_KO_AttributeList attrList;
	OpArgObject GetAttributeArg[2];
	int GetAttributeArgc = 1;
	I_KS_AsciiString *aNames = (I_KS_AsciiString*)malloc(number*sizeof(I_KS_AsciiString));
	int k =0;


	result = I_KC_CreateAttributeList(&attrList, NULL);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}

	if (uniqueID_p != NULL)
		addUniqueIdentifier(attrList, uniqueID_p);

	GetAttributeArg[0].type = I_KT_Agr_AttributeList;
	GetAttributeArg[0].attributeList = attrList;

	for(k=0;k<number;k++) 
	{ 
		aNames[k].pbStr = attrName[k]; 
		aNames[k].size = (I_T_UINT)(strlen(attrName[k])+1); 
	}


	GetAttributeArg[1].type = I_KT_Agr_AsciiStringList; 
	GetAttributeArg[1].AsciiStringList_p = aNames; 
	GetAttributeArg[1].AsciiStringList_c = number;

	printAttrList(attrList, KMIP_REQUEST);
	result = I_KC_AddOperation(hBatch,I_KT_Operation_Code_GetAttributes,GetAttributeArg,2,opid_GetAttr);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_AddOperation failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}

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

	free(aNames);
		return result;
}

I_KS_Result batch_Locate(BatchHandle hBatch,char *name,I_T_UINT *opid_Locate)
{
	I_KS_Result result = {0,};
	I_KO_AttributeList attrList;
	OpArgObject LocateArg[3];
	int LocateArgC = 3;

	result = I_KC_CreateAttributeList(&attrList, NULL);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}
	addName(attrList, name, NULL);
	LocateArg[0].type = I_KT_Agr_AttributeList;
	LocateArg[0].attributeList = attrList;

	LocateArg[1].type = I_KT_Agr_StorageStatusMask;
	LocateArg[1].storageMask = I_KT_StorageStatus_Online;

	LocateArg[2].type = I_KT_Agr_UnsignedInt;
	LocateArg[2].UInterger = 0;

	result = I_KC_AddOperation(hBatch,I_KT_Operation_Code_Locate,LocateArg,LocateArgC,opid_Locate);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_AddOperation failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}

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

I_KS_Result batch_Query(BatchHandle hBatch,I_T_UINT *opid_Query)
{

	I_KT_QueryFunction queryFunctions[] = {I_KT_QueryFunction_Operations,
		I_KT_QueryFunction_Objects,
		I_KT_QueryFunction_ServerInformation,
		I_KT_QueryFunction_ApplicationNameSpaces};
	I_T_UINT count = 4;
	I_KS_Result result = {0,};
	OpArgObject QArg[2];

	int QArgC	=	1;
	QArg[0].type = I_KT_Agr_QueryFunction;
	QArg[0].queryFunctions_p = queryFunctions;
	QArg[0].queryFunctions_c = count;



	result = I_KC_AddOperation(hBatch,I_KT_Operation_Code_Query,QArg,QArgC,opid_Query);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_AddOperation failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}

	return result;
}


I_KS_Result batch_DeleteAttribute(BatchHandle hBatch, char *uniqueID_p,char *attrName,int index,I_T_UINT *opid_DeleteAttr)
{

	I_KS_Result result = {0,};
	I_KO_AttributeList attrList;
	OpArgObject DeleteAttrbArg[3];
	int DeleteAttrbArgC = 3;

	result = I_KC_CreateAttributeList(&attrList, NULL);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}

	if (uniqueID_p != NULL)
		addUniqueIdentifier(attrList, uniqueID_p);

	DeleteAttrbArg[0].type = I_KT_Agr_AttributeList;
	DeleteAttrbArg[0].attributeList = attrList;


	DeleteAttrbArg[1].type = I_KT_Agr_AsciiString;
	DeleteAttrbArg[1].string.pbStr = attrName;
	DeleteAttrbArg[1].string.size = (I_T_UINT)(strlen(attrName) +1 );


	DeleteAttrbArg[2].type = I_KT_Agr_UnsignedInt;
	DeleteAttrbArg[2].UInterger = index;

	result = I_KC_AddOperation(hBatch,I_KT_Operation_Code_DeleteAttribute,DeleteAttrbArg,DeleteAttrbArgC,opid_DeleteAttr);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_AddOperation failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}

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

I_KS_Result batch_Get(BatchHandle hBatch, char *uniqueID_p,I_T_UINT *opid_Get)
{
	I_KS_Result result = {0,};
	I_KO_AttributeList attrList;
	OpArgObject GetArg[2];
	int GetArgC = 2;
	I_KS_GetRequest getRequest;

	result = I_KC_CreateAttributeList(&attrList, NULL);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}

	if (uniqueID_p != NULL)
		addUniqueIdentifier(attrList, uniqueID_p);

	GetArg[0].type = I_KT_Agr_AttributeList;
	GetArg[0].attributeList = attrList;

	getRequest.keyFormat_t = I_KT_KeyFormat_None;
	GetArg[1].type = I_KT_Agr_GetRequest;
	GetArg[1].getRequest_p = getRequest;

	printAttrList(attrList, KMIP_REQUEST);
	result = I_KC_AddOperation(hBatch,I_KT_Operation_Code_Get,GetArg,GetArgC,opid_Get);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_AddOperation failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}

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

I_KS_Result batch_Destroy(BatchHandle hBatch, char *uniqueID_p,I_T_UINT *opid_Destroy)
{
	I_KS_Result result = {0,};
	I_KO_AttributeList attrList;
	OpArgObject DestroyArg[2];
	int DestroyArgC = 1;

	result = I_KC_CreateAttributeList(&attrList, NULL);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}

	if (uniqueID_p != NULL)
		addUniqueIdentifier(attrList, uniqueID_p);

	DestroyArg[0].type = I_KT_Agr_AttributeList;
	DestroyArg[0].attributeList = attrList;


	printAttrList(attrList, KMIP_REQUEST);
	result = I_KC_AddOperation(hBatch,I_KT_Operation_Code_Destroy,DestroyArg,DestroyArgC,opid_Destroy);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_AddOperation failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}

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

I_KS_Result batch_AddAttribute(BatchHandle hBatch, char *uniqueID_p,I_T_UINT *opid_Addattr)
{
	I_KS_Result result = {0,};
	I_KO_AttributeList attrList;
	OpArgObject AddAttributeArg[2];
	int AddAttributeArgC = 1;

	result = I_KC_CreateAttributeList(&attrList, NULL);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}


	addUniqueIdentifier(attrList, uniqueID_p);
	addAttributeObjectGroup(attrList);

	AddAttributeArg[0].type = I_KT_Agr_AttributeList;
	AddAttributeArg[0].attributeList = attrList;


	printAttrList(attrList, KMIP_REQUEST);
	result = I_KC_AddOperation(hBatch,I_KT_Operation_Code_AddAttribute,AddAttributeArg,AddAttributeArgC,opid_Addattr);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_AddOperation failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}

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

I_KS_Result batch_ModifyAttribute(BatchHandle hBatch, char *uniqueID_p,I_T_UINT *opid_Modifyattr)
{
	I_KS_Result result = {0,};
	I_KO_AttributeList attrList;
	OpArgObject ModifyAttributeArg[2];
	int ModifyAttributeArgC = 1;

	result = I_KC_CreateAttributeList(&attrList, NULL);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}


	addUniqueIdentifier(attrList, uniqueID_p);
	modifyContactInformation(attrList);

	ModifyAttributeArg[0].type = I_KT_Agr_AttributeList;
	ModifyAttributeArg[0].attributeList = attrList;


	printAttrList(attrList, KMIP_REQUEST);
	result = I_KC_AddOperation(hBatch,I_KT_Operation_Code_ModifyAttribute,ModifyAttributeArg,ModifyAttributeArgC,opid_Modifyattr);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_AddOperation failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}

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


I_KS_Result  batch_Create(BatchHandle hBatch, char *keyname1,char *keyname2,I_KT_ObjectType obj_type,I_T_UINT *opid_Create)
{
	I_KS_Result result = {0,};
	I_KO_AttributeList attrList;
	OpArgObject CreateArg[2];
	int CreateArgC = 2;

	result = I_KC_CreateAttributeList(&attrList, NULL);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}


	addName(attrList, keyname1, keyname2);
	addCryptographicAlgorithm(attrList);
	addCryptographicLength(attrList);
	addObjectGroup(attrList);
	addContactInformation(attrList);
	addCustomAttributes(attrList);
        addCryptographicUsageMask(attrList);


	CreateArg[0].type = I_KT_Agr_AttributeList;
	CreateArg[0].attributeList = attrList;

	CreateArg[1].type = I_KT_Agr_ObjectType;
	CreateArg[1].objectType = obj_type;

	printAttrList(attrList, KMIP_REQUEST);
	result = I_KC_AddOperation(hBatch,I_KT_Operation_Code_Create,CreateArg,CreateArgC,opid_Create);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_AddOperation failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}

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


I_KS_Result batch_Register(BatchHandle hBatch, char *keyname1,char *keyname2,I_KT_ObjectType obj_type,I_T_UINT *opid_Register)
{
	I_KS_Result result = {0,};
	I_KO_AttributeList attrList;
	I_KS_Object managedObject;
	I_T_BYTE *byteBlock_p = NULL;
	OpArgObject RegisterArg[2];
	int RegisterArgC = 2;
	int len = 0;

	result = I_KC_CreateAttributeList(&attrList, NULL);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_CreateAttributeList failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}


	addName(attrList, keyname1, keyname2);
	addApplicationSpecificInfo(attrList);
	addObjectGroup(attrList);
	addContactInformation(attrList);
	addCustomAttributes(attrList);
        addCryptographicUsageMask(attrList);

	RegisterArg[0].type = I_KT_Agr_AttributeList;
	RegisterArg[0].attributeList = attrList;



	switch(obj_type)
	{
	case I_KT_ObjectType_SymmetricKey:
		{
			byteBlock_p = malloc(16);
			managedObject.object_u.symmetricKey_s.keyBlock_s.keyAlgo_t = I_KT_CryptographicAlgorithm_AES;
			managedObject.object_u.symmetricKey_s.keyBlock_s.keyCompress_t = -1; //I_KT_KeyCompressionType_None;
			managedObject.object_u.symmetricKey_s.keyBlock_s.keyFormat_t = I_KT_KeyFormat_Raw;
			managedObject.object_u.symmetricKey_s.keyBlock_s.keyLength = 16 * 8; // this should be in bits
			managedObject.object_u.symmetricKey_s.keyBlock_s.keyBytes_s.byteString_p = byteBlock_p;
			managedObject.object_u.symmetricKey_s.keyBlock_s.keyBytes_s.byteStringLen = 16;
			managedObject.objectType_t = I_KT_ObjectType_SymmetricKey;

		}
		break;
	case I_KT_ObjectType_PublicKey:
		{
			BIO *out=NULL;
			unsigned long f4=RSA_F4;
			RSA *rsa = RSA_new();
			BIGNUM *bn = BN_new();
			int num = 1024;
			const EVP_CIPHER *enc=NULL;


			if(!BN_set_word(bn, f4) || !RSA_generate_key_ex(rsa, num, bn, NULL))
			{
				printf("RSA Key Generation failed\n");
				exit(EXIT_FAILURE);
			}

			out = BIO_new(BIO_s_mem());

			if (!i2d_RSAPublicKey_bio(out,rsa))
			{
				printf("RSA Key Conversion failed\n");
				BIO_free_all(out);
				exit(EXIT_FAILURE);
			}

			len = BIO_get_mem_data(out,&byteBlock_p);


			managedObject.objectType_t = I_KT_ObjectType_PublicKey;

			// fill the key Block
			managedObject.object_u.publicKey_s.keyBlock_s.keyAlgo_t = I_KT_CryptographicAlgorithm_RSA;
			managedObject.object_u.publicKey_s.keyBlock_s.keyCompress_t = I_KT_KeyCompressionType_None;
			managedObject.object_u.publicKey_s.keyBlock_s.keyFormat_t = I_KT_KeyFormat_PKCS1;
			managedObject.object_u.publicKey_s.keyBlock_s.keyLength = 1024; // this should be in bits
			managedObject.object_u.publicKey_s.keyBlock_s.keyBytes_s.byteString_p = byteBlock_p;
			managedObject.object_u.publicKey_s.keyBlock_s.keyBytes_s.byteStringLen = len;

		}

		break;
	case I_KT_ObjectType_PrivateKey:
		{
			BIO *out=NULL;
			unsigned long f4=RSA_F4;
			RSA *rsa = RSA_new();
			BIGNUM *bn = BN_new();
			int num = 1024;
			const EVP_CIPHER *enc=NULL;


			if(!BN_set_word(bn, f4) || !RSA_generate_key_ex(rsa, num, bn, NULL))
			{
				printf("RSA Key Generation failed\n");
				exit(EXIT_FAILURE);
			}

			out = BIO_new(BIO_s_mem());

			if (!i2d_RSAPrivateKey_bio(out,rsa))
			{
				printf("RSA Key Conversion failed\n");
				BIO_free_all(out);
				exit(EXIT_FAILURE);
			}

			len = BIO_get_mem_data(out,&byteBlock_p);

			// fill the key Block
			managedObject.object_u.privateKey_s.keyBlock_s.keyAlgo_t = I_KT_CryptographicAlgorithm_RSA;
			managedObject.object_u.privateKey_s.keyBlock_s.keyCompress_t = I_KT_KeyCompressionType_None;
			managedObject.object_u.privateKey_s.keyBlock_s.keyFormat_t = I_KT_KeyFormat_PKCS1;
			managedObject.object_u.privateKey_s.keyBlock_s.keyLength = 1024; // this should be in bits
			managedObject.object_u.privateKey_s.keyBlock_s.keyBytes_s.byteString_p = byteBlock_p;
			managedObject.object_u.privateKey_s.keyBlock_s.keyBytes_s.byteStringLen = len;
			managedObject.objectType_t = I_KT_ObjectType_PrivateKey;

		}
		break;
		case I_KT_ObjectType_Template:
		{
			managedObject.objectType_t = I_KT_ObjectType_Template;
		}
		break;
	case I_KT_ObjectType_SecretData:
		{
			byteBlock_p = malloc(16);
			managedObject.object_u.secretData_s.secretDataType = I_KT_SecretData_Password;
			managedObject.object_u.secretData_s.keyBlock_s.keyAlgo_t = I_KT_CryptographicAlgorithm_AES;
			managedObject.object_u.secretData_s.keyBlock_s.keyCompress_t = -1; //I_KT_KeyCompressionType_None;
			managedObject.object_u.secretData_s.keyBlock_s.keyFormat_t = I_KT_KeyFormat_Opaque;
			managedObject.object_u.secretData_s.keyBlock_s.keyLength = 16 * 8; // this should be in bits
			managedObject.object_u.secretData_s.keyBlock_s.keyBytes_s.byteString_p = byteBlock_p;
			managedObject.object_u.secretData_s.keyBlock_s.keyBytes_s.byteStringLen = 16;
			managedObject.objectType_t = I_KT_ObjectType_SecretData;
		}
		break;

	}
	RegisterArg[1].type = I_KT_Agr_Object;
	RegisterArg[1].object_p = &managedObject;



	printAttrList(attrList, KMIP_REQUEST);
	result = I_KC_AddOperation(hBatch,I_KT_Operation_Code_Register,RegisterArg,RegisterArgC,opid_Register);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_AddOperation failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return result;
	}

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


void printQueryResponse(I_KS_QueryResponse		*queryResponse_p) 
{
	int i =0;
	printf("----Query Response----\n");
	printf("Operations Supported : ");
	for (i = 0; i < (int)queryResponse_p->operationsCount; i++)
	{
		printOperation(queryResponse_p->operation_p[i]);
	}
	printf("\n");


	printf("ObjectType Supported : ");
	for (i = 0; i < (int)queryResponse_p->objectTypeCount; i++)
	{
		printObjectType(queryResponse_p->objectType_p[i]);
	}
	
	printf("\n");



	if (queryResponse_p->serverInformationElements_p != NULL &&
		queryResponse_p->serverInformationElements_p->value_s.type == I_KT_Struct)
	{
		printf("Server Information (tag:0x%x): \n", queryResponse_p->serverInformationElements_p->tag);
		for (i = 0; i < (int)queryResponse_p->serverInformationElements_p->value_s.value_u.structVal->nFields; i++)
		{
			printElement(queryResponse_p->serverInformationElements_p->value_s.value_u.structVal->fields[i]);
		}
	}

	printf("VendorSpecificInformation : %s\n", queryResponse_p->vendorIdentification_p);

	for (i = 0; i < queryResponse_p->applicationNamespaceCount; i++)
    {
        printf("Application NameSpace :  %s\n", queryResponse_p->applicationNamespace_pp[i]);
    }

}

void printObject( I_KS_Object * object_p)
{
	int i = 0;
	{
		switch (object_p->objectType_t)
		{
		case I_KT_ObjectType_SymmetricKey:
			printf("Object Type : SymmetricKey\n");
			printf("Key Material Length : %d\n", object_p->object_u.symmetricKey_s.keyBlock_s.keyBytes_s.byteStringLen);
			printf("Key Material : ");
			for (i = 0; i < (int)object_p->object_u.symmetricKey_s.keyBlock_s.keyBytes_s.byteStringLen; i++)
			{
				printf("%2.2X", object_p->object_u.symmetricKey_s.keyBlock_s.keyBytes_s.byteString_p[i]);
			}
			printf("\n");
			printKeyFormat(object_p->object_u.symmetricKey_s.keyBlock_s.keyFormat_t);
			break;
		case I_KT_ObjectType_SecretData:
			printf("Object Type : Secret Data\n");
			switch (object_p->object_u.secretData_s.secretDataType)
			{
			case I_KT_SecretData_None:
				printf("Secret Data Type: I_KT_SecretData_None\n");
				break;
			case I_KT_SecretData_Password:
				printf("Secret Data Type: I_KT_SecretData_Password\n");
				break;
			case I_KT_SecretData_Seed:
				printf("Secret Data Type: I_KT_SecretData_Seed\n");
				break;
			default:
				printf("Secret Data Type: Invalid or unknown Secret Data Type\n");
			}
			printf("Key Material Length : %d\n", object_p->object_u.secretData_s.keyBlock_s.keyBytes_s.byteStringLen);
			printf("Key Material : ");
			for (i = 0; i < (int)object_p->object_u.secretData_s.keyBlock_s.keyBytes_s.byteStringLen; i++)
			{
				printf("%2.2X", object_p->object_u.secretData_s.keyBlock_s.keyBytes_s.byteString_p[i]);
			}
			printf("\n");
			printKeyFormat(object_p->object_u.secretData_s.keyBlock_s.keyFormat_t);
			break;
		case I_KT_ObjectType_Template:
			{
				printf("Object Type : Template\n");
			}
			break;
		case I_KT_ObjectType_OpaqueObject:
			printf("Object Type : OpaqueObject\n");
			break;
		case I_KT_ObjectType_PublicKey:
			printf("Object Type : PublicKey\n");
			printf("Key Material Length : %d\n", object_p->object_u.publicKey_s.keyBlock_s.keyBytes_s.byteStringLen);
			printf("Key Material : ");
			for (i = 0; i < (int)object_p->object_u.publicKey_s.keyBlock_s.keyBytes_s.byteStringLen; i++)
			{
				printf("%2.2X", object_p->object_u.publicKey_s.keyBlock_s.keyBytes_s.byteString_p[i]);
			}
			printf("\n");
			printKeyFormat(object_p->object_u.publicKey_s.keyBlock_s.keyFormat_t);
			break;
		case I_KT_ObjectType_PrivateKey:
			printf("Object Type : PrivateKey\n");
			printf("Key Material Length : %d\n", object_p->object_u.privateKey_s.keyBlock_s.keyBytes_s.byteStringLen);
			printf("Key Material : ");
			for (i = 0; i < (int)object_p->object_u.privateKey_s.keyBlock_s.keyBytes_s.byteStringLen; i++)
			{
				printf("%2.2X", object_p->object_u.privateKey_s.keyBlock_s.keyBytes_s.byteString_p[i]);
			}
			printf("\n");
			printKeyFormat(object_p->object_u.privateKey_s.keyBlock_s.keyFormat_t);

			break;
		case I_KT_ObjectType_Certificate:
			printf("Object Type : Certificate\n");
			break;
		case I_KT_ObjectType_SplitKey:
			printf("Object Type : SplitKey\n");
			break;
		}
	}
}

void printResults(	BatchHandle hBatch,I_T_UINT	opid)
{
	OpOutResult *result_p = NULL;
	I_T_UINT i = 0;
	I_T_UINT j = 0;
	I_KS_Result result;

	result = I_KC_GetResponse(hBatch,opid, &result_p);
	if (result.status != I_KT_ResultStatus_Success)		
	{
		printf("I_KC_GetResponse failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return;
	}
	if (result_p->opresult.status != I_KT_ResultStatus_Success)
	{
		printf("Failed Status:%s Reason:%s\n",
			I_KC_GetResultStatusString(result_p->opresult), I_KC_GetResultReasonString(result_p->opresult));
		return;
	}

	printf(" result_p->outobjcount = %d \n",result_p->outobjcount);

	for(i = 0;i< result_p->outobjcount; i++)
	{
		switch(result_p->outobj[i].type)
		{

		case  I_KT_Agr_AttributeList    :
			printf("I_KT_Agr_AttributeList\n");
			printAttrList(result_p->outobj[i].attributeList, KMIP_RESPONSE);
			break;
		case  I_KT_Agr_Object    :
			printf("I_KT_Agr_Object\n");
			printf("count = %d\n",result_p->outobj[i].object_c);
			for(j=0;j<result_p->outobj[i].object_c;j++);
			{
				printf("returned Key Object[%d] = \n",j);
				printObject(&result_p->outobj[i].object_p[j]);
			}
			break;
		case  I_KT_Agr_ObjectType    :
			printf("I_KT_Agr_ObjectType\n");
			printObjectType(result_p->outobj[i].objectType);
			break;
		case  I_KT_Agr_GetRequest    :
			printf("I_KT_Agr_GetRequest\n");
			printf("getRequest.keyFormat_t = %0x\n",result_p->outobj[i].getRequest_p.keyFormat_t);
			break;
		case  I_KT_Agr_StorageStatusMask    :
			printf("I_KT_Agr_StorageStatusMask\n");
			printf("StorageStatusMask = %0x\n",result_p->outobj[i].storageMask);
			break;
		case  I_KT_Agr_QueryFunction    :
			printf("I_KT_Agr_QueryFunction\n");
			break;
		case  I_KT_Agr_QueryResponse    :
			printf("I_KT_Agr_QueryResponse\n");
			printQueryResponse(result_p->outobj[i].queryResponse_p);
			break;
		case  I_KT_Agr_UnsignedInt    :
			printf("I_KT_Agr_UnsignedInt\n");
			printf("UnsingedInt = %d\n",result_p->outobj[i].UInterger);
			break;
		case  I_KT_Agr_AsciiString    :
			printf("I_KT_Agr_AsciiString\n");
			printf("str {size %d} = %s\n",result_p->outobj[i].string.size,
				result_p->outobj[i].string.pbStr);
			break;
		case  I_KT_Agr_AsciiStringList    :
			printf("I_KT_Agr_AsciiStringList\n");

			for(j=0;j<result_p->outobj[i].AsciiStringList_c;j++)
			{
				printf("str[%d] {size %d } = %s\n",j,result_p->outobj[i].AsciiStringList_p[j].size,
					result_p->outobj[i].AsciiStringList_p[j].pbStr);
			}
			break;
		default:
			printf("invalid argument\n");
			break;
		}
	}
}

void addWrappingMethodType(I_KO_AttributeList attrList,int value)
{
        I_KS_Attribute attribute;
        I_KS_Result ret_s;
        do
        {
                //Wrapping Method type
                attribute.attributeValue.index = 0;
                attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Enum;
                attribute.attributeValue.value_u.enumVal = value;
                attribute.attributeName = "Wrapping Method";
                ret_s = I_KC_AddToAttributeList(attrList, &attribute);
                if (ret_s.status != I_KT_ResultStatus_Success)
                {
                        printf("wrapping method addition to attribute list failed\n");
                        break;
                }
        } while (0);
        return;
}

void addBlockCipherMode(I_KO_AttributeList attrList, int value)
{
        I_KS_Attribute attribute;
        I_KS_Result ret_s;
        do
        {
                //Contact Information
                attribute.attributeValue.index = 0;
                attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Enum;
                attribute.attributeValue.value_u.enumVal = value;
                attribute.attributeName = "Cipher Mode";
                ret_s = I_KC_AddToAttributeList(attrList, &attribute);
                if (ret_s.status != I_KT_ResultStatus_Success)
                {
                        printf("Cipher Mode addition to attribute list failed\n");
                        break;
                }
        } while (0);
        return;
}

void addpadding(I_KO_AttributeList attrList, int value)
{
   I_KS_Attribute attribute;
   I_KS_Result ret_s;
   do
        {
                //Contact Information
                attribute.attributeValue.index = 0;
                attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Enum;
                attribute.attributeValue.value_u.enumVal = value;
                attribute.attributeName = "Padding Type";
                ret_s = I_KC_AddToAttributeList(attrList, &attribute);
                if (ret_s.status != I_KT_ResultStatus_Success)
                {
                        printf("Padding Type addition to attribute list failed\n");
                        break;
                }
        } while (0);
        return;
}

void addEncodingOption(I_KO_AttributeList attrList, int value)
{
        I_KS_Attribute attribute;
        I_KS_Result ret_s;
        do
        {
                //Contact Information
                attribute.attributeValue.index = 0;
                attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Enum;
                attribute.attributeValue.value_u.enumVal = value;
                attribute.attributeName = "Encoding Option";
                ret_s = I_KC_AddToAttributeList(attrList, &attribute);
                if (ret_s.status != I_KT_ResultStatus_Success)
                {
                        printf("Encoding Option addition to attribute list failed\n");
                        break;
                }
        } while (0);
        return;
}

void addOffset(I_KO_AttributeList attrList, int value)
{
        I_KS_Attribute attribute;
        I_KS_Result ret_s;
        do
        {

                attribute.attributeValue.index = 0;
                attribute.attributeValue.valueType_t = I_KT_AttributeValueType_Integer ;
                attribute.attributeValue.value_u.integerVal = value;
                attribute.attributeName = "Offset";
                ret_s = I_KC_AddToAttributeList(attrList, &attribute);
                if (ret_s.status != I_KT_ResultStatus_Success)
                {
                        printf("Offset addition to attribute list failed\n");
                        break;
                }
        } while (0);
        return;
}

