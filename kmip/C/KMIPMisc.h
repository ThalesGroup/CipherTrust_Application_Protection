/*
 * KMIPMisc.h 
 *
 * Sample code is provided for educational purposes
 * No warranty of any kind, either expressed or implied by fact or law
 * Use of this item is not restricted by copyright or license terms
 *
 */

#define KMIP_REQUEST 1
#define KMIP_RESPONSE 0

void printAttrList(I_KO_AttributeList attrList, int request);
void printKeyFormat(I_KT_KeyFormat value);
void printObjectType(I_KT_ObjectType value);
void printOperation(I_KT_Operation value);
void printValue(I_KS_Value *value);
void printElement(I_KS_Element* element);
void printAttributeNameList(I_KS_AttributeNameList *attrNameList);
void printResults(	BatchHandle hBatch,I_T_UINT	opid);
void printObject( I_KS_Object * object_p);
void printQueryResponse(I_KS_QueryResponse		*queryResponse_p);

void addUniqueIdentifier(I_KO_AttributeList attrList, char *uniqueID_p);
void addCustomAttributes(I_KO_AttributeList attrList);
void addObjectGroup(I_KO_AttributeList attrList);
void addName(I_KO_AttributeList attrList, char *name1, char *name2);
void addContactInformation(I_KO_AttributeList attrList);
void addCryptographicLength(I_KO_AttributeList attrList);
void addCryptographicAlgorithm(I_KO_AttributeList attrList);
void addApplicationSpecificInfo(I_KO_AttributeList attrList);
void addLink(I_KO_AttributeList attrList);
void addIV(I_KO_AttributeList attrList, const char *iv, unsigned int ivlen);
void addAlgorithm(I_KO_AttributeList attrList, const char *algo);
void addpadding(I_KO_AttributeList attrList, int value);
void addrandomIV(I_KO_AttributeList attrList, int random);
void addCipherLen(I_KO_AttributeList attrList, int cipher_len);
void addIVLen(I_KO_AttributeList attrList, int iv_len);
void addTagLen(I_KO_AttributeList attrList, int tag_len);

void addAttributeObjectGroup(I_KO_AttributeList attrList);
void modifyContactInformation(I_KO_AttributeList attrList);
void addWrappingMethodType (I_KO_AttributeList attrList,int value);
void addBlockCipherMode (I_KO_AttributeList attrList,int value);
void addEncodingOption(I_KO_AttributeList attrList, int value);

I_KS_Result batch_Create(BatchHandle hBatch, char *keyname1,char *keyname2,I_KT_ObjectType obj_type,I_T_UINT *opid_Create);
I_KS_Result batch_Register(BatchHandle hBatch, char *keyname1,char *keyname2,I_KT_ObjectType obj_type,I_T_UINT *opid_Register);
I_KS_Result batch_Locate(BatchHandle hBatch,char *name,I_T_UINT *opid_Locate);
I_KS_Result batch_Get(BatchHandle hBatch, char *uniqueID_p,I_T_UINT *opid_Get);
I_KS_Result batch_GetAttribute(BatchHandle hBatch,char *uniqueID_p,char **attrName,int number,I_T_UINT *opid_GetAttr);
I_KS_Result batch_GetAttributeList(BatchHandle hBatch, char *uniqueID_p,I_T_UINT *opid_GetAttrList);
I_KS_Result batch_AddAttribute(BatchHandle hBatch, char *uniqueID_p,I_T_UINT *opid_Addattr);
I_KS_Result batch_ModifyAttribute(BatchHandle hBatch, char *uniqueID_p,I_T_UINT *opid_Modifyattr);
I_KS_Result batch_DeleteAttribute(BatchHandle hBatch, char *uniqueID_p,char *attrName,int index,I_T_UINT *opid_DeleteAttr);
I_KS_Result batch_Destroy(BatchHandle hBatch, char *uniqueID_p,I_T_UINT *opid_Destroy);
I_KS_Result batch_Query(BatchHandle hBatch,I_T_UINT *opid_Query);
