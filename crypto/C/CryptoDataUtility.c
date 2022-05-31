#include "CryptoDataUtility.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char** argv) {
	unsigned char *test = NULL;
	
	I_O_Session sess = NULL; 
	int rc = 0;
	unsigned char buf[1024] = {0};
	int i = 0, j = 0;
        int freeInData = 1;
		unsigned char *in = NULL;

	if(argc < 6) {
		printf("Usage: CryptoDataUtility propertyfile ks_username ks_password keyname data_to_encrypt\n");
		return 0;
	}
	
	rc = I_C_Initialize(I_T_Init_File,argv[1]);
	if(rc) {
              fprintf(stderr, "I_C_Initialize error: %s\n",
            I_C_GetErrorString(rc));
                return rc;
	}
	rc = I_C_OpenSession(&sess,I_T_Auth_Password,argv[2],argv[3]);
	if(rc) {
                  fprintf(stderr, "I_C_OpenSession error: %s\n",
                  I_C_GetErrorString(rc));
                  return rc;
	}
	test = NULL;
	i = Encrypt(argv[4], (unsigned char*)argv[5], strlen(argv[5]), &in , sess);
	printf("Output encrypted size %d\n",i);
	if(i <=0 ){
	I_C_CloseSession(sess);
	I_C_Fini();
	 return -1;
	}
	rc = Decrypt(in,i, &test, sess, freeInData);
	test[rc] = 0;
	printf("Decrypted data %s\n",(char*)test);
	free(test);
        if (freeInData == 0) 
        {
	    if (in) free(in);
        }
	I_C_CloseSession(sess);
	I_C_Fini();
}
