/*
* KMIPBatching.c	
*
* Sample code is provided for educational purposes
* No warranty of any kind, either expressed or implied by fact or law
* Use of this item is not restricted by copyright or license terms
*
* Sample code for KMIP Batching Operation. 
* 
*/

#include <stdio.h>
#include <stdlib.h>
#ifdef WIN32
#include <conio.h>
#endif
#include <string.h>
#include <ctype.h>
#include "cadp_capi.h"
#include "KMIPMisc.h"

void usage_Batching(void)
{
	fprintf(stderr, "usage: KMIPBatching conf_file\n");
	exit(1);
}
typedef enum  _command 
{
	cmd_exit = 0,
	cmd_add_operation = 1,
	cmd_delete_operation =2,
	cmd_execute_batch = 3,
	cmd_print_result = 4,
	cmd_flush_result = 5,
	cmd_reset_batch = 6
} I_KS_Command;
typedef struct _cmd_prompt
{
	char		strCmd[30];
	I_KS_Command cmd;
}I_KS_Command_Prompt;

struct _KMIP_Operation
{
	char strOp[30];
	I_KT_OperationCode OpCode;
}supported_codes[] = {
	{"Create",I_KT_Operation_Code_Create},
	{"Register",I_KT_Operation_Code_Register},
	{"Locate",I_KT_Operation_Code_Locate},
	{"Get",I_KT_Operation_Code_Get},
	{"GetAttributes",I_KT_Operation_Code_GetAttributes},
	{"GetAttributesList",I_KT_Operation_Code_GetAttributesList},
	{"AddAttribute",I_KT_Operation_Code_AddAttribute},
	{"ModifyAttribute",I_KT_Operation_Code_ModifyAttribute},
	{"DeleteAttribute",I_KT_Operation_Code_DeleteAttribute},
	{"Destroy",I_KT_Operation_Code_Destroy},
	{"Query",I_KT_Operation_Code_Query},
	{"<<== Go BACK||",I_KT_Operation_Code_None}
};

char *const  OpCodeToStr(I_KT_OperationCode OpCode)
{
	int i = 0;
	for(i=0; i< sizeof(supported_codes)/sizeof(supported_codes[0]);i++)
		if(OpCode == supported_codes[i].OpCode) return supported_codes[i].strOp;
	return NULL;
}
I_T_UINT hexstr_to_binary(char *str)
{
	I_T_UINT id  = 0,temp = 0;
	int i = 0 ;
	unsigned char digit = 0;
	char ch = 0;
	if(strlen(str) != 8)
		return id;
	for(i=0;i<8;i++)
	{
		ch = str[i];
		if(	(ch >= '0') && (ch <= '9') )
			id = id *16 + (ch - '0');
		else if((ch >= 'A') && (ch <= 'F'))
			id = id *16 + 10 + (ch - 'A');
		else if((ch >= 'a') && (ch <= 'f'))
			id = id *16 + 10 + (ch - 'a');
		else 
			return 0; 
	}
	id = ((id & 0xFF000000) >> 24 )
		|((id & 0x00FF0000) >> 8 )
		|((id & 0x0000FF00) << 8 )
		|((id & 0x000000FF) << 24 );
		
	return id;
}

I_KT_OperationCode	PromptForOperationCode()
{

	I_KT_OperationCode code = 0;
	int i = 0;
	int flag = 0;
	int c = 0;
	do{
		flag = 0;
		printf("\nEnter the Operation code to add");
		printf("\n%10s %s  \n","Code","Operation");
		for(i=0;i< sizeof(supported_codes)/sizeof(supported_codes[0]);i++)
			printf("%10d %s\n",supported_codes[i].OpCode,supported_codes[i].strOp);
		printf("\n>");
		scanf("%d",&code);
		while ((c = getchar()) != '\n' && c != EOF);
		for(i=0;i< sizeof(supported_codes)/sizeof(supported_codes[0]);i++)
			if(supported_codes[i].OpCode == code)
			{
				flag = 1;
				break;
			}
			if(flag) 
				break;
			else
				printf("\t Wrong Choice!!!\n");
	}while(!flag);
	return code;	 
}

I_KS_Command_Prompt prompt1[]={
	{"Add Operation",cmd_add_operation},
	{"Delete Operation",cmd_delete_operation},
	{"Execute Batch",cmd_execute_batch},
	{"Reset Batch",cmd_reset_batch},
	{"Exit",cmd_exit}
};

I_KS_Command_Prompt prompt2[]={
	{"Print Results",cmd_print_result},
	{"Fulsh All Results",cmd_flush_result},
	{"Reset Batch",cmd_reset_batch},
	{"Exit",cmd_exit}
};
I_KS_Command PromptForCommand(I_KS_Command_Prompt *prompt, int size)
{
	I_KS_Command cmd;
	int flag = 0;
	int c=0,i = 0; 
	int ret = 0;
	do
	{

		printf("\nEnter command \n%10s %30s \n","Code","Command");
		for(i=0;i< size;i++)
			printf("%10d %s\n",prompt[i].cmd,prompt[i].strCmd);
		printf("\n> ");
		ret = scanf("%d",&cmd);
		while ((c = getchar()) != '\n' && c != EOF);
		for(i=0;i< size;i++)
			if(prompt[i].cmd == cmd)
			{
				flag = 1;
				break;
			}
			if(flag) 
				break;
			else
				printf("\t Wrong Choice!!!\n");
	}while(!flag);
	return cmd;
}

typedef struct _OperationList
{
	I_KT_OperationCode OpCode;
	I_T_UINT		   OpID;
	struct _OperationList *next;

} OpListNode;

void PrintOperationList(OpListNode *start)
{
	int lc = 0;
	unsigned char *oid=0;

	printf("\nBATCH [");
	while(start)
	{
		if(lc >=3)
		{
			lc = 0;
			printf("\n       ");
		}
		oid = (unsigned char *)&start->OpID;
		printf("%15s(id=%02X%02X%02X%02X)",OpCodeToStr(start->OpCode),oid[0],oid[1],oid[2],oid[3]);
		lc++;
		start = start->next;
	}
	printf(" ]\n");
}
void AddToList(OpListNode **start,I_T_UINT code,I_T_UINT id)
{
	OpListNode *temp = NULL;
	OpListNode *node = NULL;
	
	node = (OpListNode *) malloc(sizeof(OpListNode));
	node->OpCode = code;
	node->OpID = id;
	node->next = NULL;
	while(*start)
		start = &((*start)->next);
	*start = node;
}
void FreeList(OpListNode **start)
{
	OpListNode *temp = *start;
	OpListNode *temp2 = 0;
	while(temp)
	{
		temp2 = temp;
		temp = temp->next;
		free(temp2);
		temp2 = 0;
	}
	*start = NULL;
}
void DeleteOperation(BatchHandle hBatch,OpListNode **start)
{
	I_KS_Result result= {0,};
	char opid[80] = {0,};
	I_T_UINT id = 0;
	OpListNode *temp = NULL;
	OpListNode *node = NULL;

	if(NULL == *start) 
	{
		printf("\n No operation to delete!!!\n");
		return;
	}

	PrintOperationList(*start);
	printf("\n Enter operation id to delete \n>");
	scanf(" %[^\n]s",opid);
	id = hexstr_to_binary(opid);
	if(0 == id)
	{
		printf("InValid ID string !!!\n");
		return;
	}
	result = I_KC_DeleteOperation(hBatch,id);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("\n I_KC_DeleteOperation failed \n Status:%s\n Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		return;
	}
	temp = *start;

	if(temp->OpID == id)
	{
		*start = temp->next;
		free(temp);
	}
	else
	{	node = temp;

		while(node)
		{
			if(node->OpID == id)
				break;
			temp = node;
			node = node->next;
		}

		if(node)
		{
			node = temp->next;
			temp->next =  node->next;
			free(node);
		}
	}
}
OpListNode *next;
void PrintBatchResults(BatchHandle hBatch,OpListNode *start)
{
	I_T_UINT id = 0;
	char opid[80] = {0,};
	OpListNode *temp = NULL;	
	unsigned char *oid=0;
	
	if(NULL == start) 
	{
		printf("\n No operation to Print Results!!!\n");
		return;
	}

	PrintOperationList(start);
	
	printf("\n Enter operation id to Get Results \n Or write [F]irst/[N]ext for iterator \n>");
	scanf(" %[^\n]s",opid);
	if(!strcmp("First",opid) || !strcmp("F",opid))
	{
		next = start;
		id = start->OpID;
	}
	else if(!strcmp("Next",opid) || !strcmp("N",opid))
	{
		if(next)
			next = next->next;
		if(!next)
			next = start;
		id = next->OpID;
	}
	else
	{
		id = hexstr_to_binary(opid);
		if(0 == id)
		{
			printf("InValid ID string !!!\n");
			return;
		}
	}
	oid = (unsigned char *)&id;
	printf("\n id=%02X%02X%02X%02X \n",oid[0],oid[1],oid[2],oid[3]);
		
	printResults(hBatch,id);	

}

I_KS_Result AddOperation(BatchHandle hBatch,I_T_UINT opCode,I_T_UINT  *id)
{
	I_KS_Result result = {0,};

	char *atrribNames[5] = { "Name",
							 "Cryptographic Algorithm",
							 "Cryptographic Length",
							 "Object Type",
							 "Digest"};
	I_T_UINT	attr_Count = 5;

	char keyname1[80] = {0,};
	char keyname2[80] = {0,};
	char uid[80] = {0,};
	char *ptr = NULL;
	I_KT_ObjectType obj_type;
	I_T_UINT  index = 0;
	switch(opCode)
	{
	case I_KT_Operation_Code_Create            :
		printf("\n Please enter keyname1  = \n>");
		scanf(" %[^\n]s",keyname1);
		printf("\n Please enter keyname2  ( enter NULL to leave blank)=  \n>");scanf(" %[^\n]s",keyname2);
		ptr = NULL;
		if(strcmp("NULL",keyname2))
			ptr =  keyname2;
		printf("\nEnter ");
		printf("\n 2 for Symmetric ");
		printf("\n 3 for Public ");
		printf("\n 4 for Private ");
		printf("\n 6 for Template ");
		printf("\n 7 for Secret ");
		printf("\n Please enter object type = \n>");scanf("%d",&obj_type);
		return batch_Create(hBatch,keyname1,ptr,obj_type,id);
		break;
	case I_KT_Operation_Code_Register          :
		printf("\n Please enter keyname1 = \n>");scanf(" %[^\n]s",keyname1);
		printf("\n Please enter keyname2 ( enter NULL to leave blank)= \n>");scanf(" %[^\n]s",keyname2);
		ptr = NULL;
		if(strcmp("NULL",keyname2))
			ptr =  keyname2;
		printf("\nEnter ");
		printf("\n 2 for Symmetric ");
		printf("\n 3 for Public ");
		printf("\n 4 for Private ");
		printf("\n 6 for Template ");
		printf("\n 7 for Secret ");
		printf("\n Please enter object type = \n>");scanf("%d",&obj_type);
		return batch_Register(hBatch,keyname1,ptr,obj_type,id);

		break;
	case I_KT_Operation_Code_Locate            :
		printf("\n Please enter key name = \n>");scanf(" %[^\n]s",keyname1);
		return batch_Locate(hBatch,keyname1,id);
		break;
	case I_KT_Operation_Code_Get               :
		printf("\n Please enter unique ID (NULL to use ID Placeholder) = \n>");scanf(" %[^\n]s",uid);
		ptr = NULL;
		if(strcmp("NULL",uid))
			ptr =  uid;
		return batch_Get(hBatch,ptr,id);
		break;
	case I_KT_Operation_Code_GetAttributes     :
		printf("\n Please enter unique ID (NULL to use ID Placeholder) = \n>");scanf(" %[^\n]s",uid);
		ptr = NULL;
		if(strcmp("NULL",uid))
			ptr =  uid;
		return batch_GetAttribute(hBatch,ptr,atrribNames,attr_Count,id);
		break;
	case I_KT_Operation_Code_GetAttributesList :
		printf("\n Please enter unique ID (NULL to use ID Placeholder) = \n>");scanf(" %[^\n]s",uid);
		ptr = NULL;
		if(strcmp("NULL",uid))
			ptr =  uid;
		return batch_GetAttributeList(hBatch,ptr,id);
		break;
	case I_KT_Operation_Code_AddAttribute      :
		printf("\n Please enter unique ID (NULL to use ID Placeholder) = \n>");scanf(" %[^\n]s",uid);
		ptr = NULL;
		if(strcmp("NULL",uid))
			ptr =  uid;
		return batch_AddAttribute(hBatch,ptr,id);
		break;
	case I_KT_Operation_Code_ModifyAttribute   :
		printf("\n Please enter unique ID (NULL to use ID Placeholder) = \n>");scanf(" %[^\n]s",uid);
		ptr = NULL;
		if(strcmp("NULL",uid))
			ptr =  uid;
		return batch_ModifyAttribute(hBatch,ptr,id);
		break;
	case I_KT_Operation_Code_DeleteAttribute   :
		printf("\n Please enter unique ID (NULL to use ID Placeholder) = \n>");scanf(" %[^\n]s",uid);
		ptr = NULL;
		if(strcmp("NULL",uid))
			ptr =  uid;
		printf("\n Please enter attrib name = \n>");
		scanf(" %[^\n]s",keyname1);
		printf("\n Please enter index = \n>");scanf("%d",&index);
		return batch_DeleteAttribute(hBatch,ptr,keyname1,index,id);
		break;
	case I_KT_Operation_Code_Destroy           :
		printf("\n Please enter unique ID = \n>");scanf(" %[^\n]s",uid);
		return batch_Destroy(hBatch,uid,id);
		break;
	case I_KT_Operation_Code_Query             :
		return batch_Query(hBatch,id);
		break;
	default :
		break;
	}
	return result;
}
I_KS_Result Batching(I_O_Session *handle_p)

{
	I_KS_Result result = {0,};
	BatchHandle hBatch = NULL;

	int OpListCount = 0;
	OpListNode   *start = NULL;
	OpListNode   *node = NULL;
	I_T_UINT     opCode = 0;
	I_T_UINT     id = 0;
	I_T_UINT       loop1 = 1;
	int			   mode = 0;

	result = I_KC_CreateBatch(&hBatch,0,1);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_CreateBatch failed \n Status:%s\n Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
		goto FUNC_RET;
	}

	do
	{

		if(mode == 0)
		{
			switch(PromptForCommand(prompt1,5))
			{
			case cmd_add_operation:
				if(!(opCode = PromptForOperationCode()))
					break;
				if ((AddOperation(hBatch,opCode,&id)).status == I_KT_ResultStatus_Success)
				{
					AddToList(&start,opCode,id);
					PrintOperationList(start);
				}
				else
					printf("\n AddOperation failled !!!\n");
				break;
			case cmd_delete_operation:
				DeleteOperation(hBatch,&start);
				break;
			case cmd_execute_batch:
				result = I_KC_ExecuteBatch(*handle_p,hBatch);
				if (result.status != I_KT_ResultStatus_Success)
				{
					printf("I_KC_EexecuteBatch failed \n Status:%s\n Reason:%s\n",
					I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
					break;
				}
				mode = 1;
				break;
			case cmd_reset_batch:
				result = I_KC_ResetBatch(hBatch,I_KT_RESET_ALL_OPERATIONS);
				if (result.status != I_KT_ResultStatus_Success)
					printf("I_KC_ResetBatch failed \n Status:%s\n Reason:%s\n",
					I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
				FreeList(&start);
				break;
			default :
				loop1 = 0;
			}
		}
		else
		{
			switch(PromptForCommand(prompt2,4))
			{
			case cmd_flush_result: 
				result = I_KC_ResetBatch(hBatch,I_KT_RESET_OUTPUT_LIST);
				if (result.status != I_KT_ResultStatus_Success)
					printf("I_KC_ResetBatch failed \n Status:%s\n Reason:%s\n",
					I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
				mode = 0;
				break;
			case cmd_print_result:
				PrintBatchResults(hBatch,start);
				break;
			case cmd_reset_batch:
				result = I_KC_ResetBatch(hBatch,I_KT_RESET_ALL_OPERATIONS);
				if (result.status != I_KT_ResultStatus_Success)
					printf("I_KC_ResetBatch failed \n Status:%s\n Reason:%s\n",
					I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
				FreeList(&start);
				mode = 0;
				break;
			default :
				loop1 = 0;
			}
		}


	}
	while(loop1);
	
	result = I_KC_DestroyBatch(hBatch);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("I_KC_DestroyBatch failed \n Status:%s\n Reason:%s\n",
					I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
	}
FUNC_RET:
	return result;
}
#ifdef WIN32
char mygetch( ) {
return getch();
}
#else

#include <termios.h>
#include <unistd.h>


char mygetch( ) {
  struct termios oldt,
                 newt;
  char            ch;
  tcgetattr( STDIN_FILENO, &oldt );
  newt = oldt;
  newt.c_lflag &= ~( ICANON | ECHO );
  tcsetattr( STDIN_FILENO, TCSANOW, &newt );
  ch = getchar();
  tcsetattr( STDIN_FILENO, TCSANOW, &oldt );
  return ch;
}
#endif

char str[100] = {0,};
char *getstring(void *arg)
{
	char *ptr = str;
	char t = 0;
	char *ar = (char*)arg;
	printf("\nPlease enter password for privatekey [%s] : ",ar);
	while((t = mygetch())!='\n')
	{
		if(t == 13 || t == 10)
			break;
		if(!iscntrl (t))
		{
			putchar('*');
			*ptr++  = t;
		}
	}
			putchar('\n');
	*ptr = 0;
	
	return str;
}
int main(int argc, char **argv)
{

	I_O_Session sess;
	char *path;
	int argp;
	I_T_RETURN rc;
	I_KS_Result result;

	if (argc < 2)
		usage_Batching(); // exit

	argp = 1;
	path = argv[argp++];

	rc = I_C_Initialize(I_T_Init_File, path);

	if (rc != I_E_OK)
	{
		fprintf(stderr, "I_C_Initialize error: %s\n",
			I_C_GetErrorString(rc));
		return rc;
	}
	rc = I_C_SetPassPhraseCallback(getstring);
	if (rc != I_E_OK)
	{
		fprintf(stderr, "I_C_SetPassPhraseCallback error: %s\n",
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

	result = Batching(&sess);
	if (result.status != I_KT_ResultStatus_Success)
	{
		printf("\n Batching failed \n Status:%s\n Reason:%s\n",
			I_KC_GetResultStatusString(result), I_KC_GetResultReasonString(result));
	}
	I_C_CloseSession(sess);
	I_C_Fini();
	return rc;
}
